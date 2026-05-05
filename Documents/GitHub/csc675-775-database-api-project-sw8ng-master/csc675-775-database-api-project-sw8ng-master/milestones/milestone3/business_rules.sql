-- ==================================================================================
-- 1. Delay Propagation (Sean Wang)
-- ==================================================================================

CREATE PROCEDURE Delay_Propagation(
    IN incident_id INT,
    IN trip_id INT,
    IN start_stop_id INT,
    IN delay_minutes INT
)
BEGIN
    WITH RECURSIVE Later_Stop_Delays AS (
        SELECT
            Stop.stop_id,
            Stop.trip_id,
            Stop.sequence_number,
            delay_minutes AS total_delay
        FROM Stop
        WHERE Stop.stop_id = start_stop_id
          AND Stop.trip_id = trip_id

        UNION ALL

        SELECT
            Stop.stop_id,
            Stop.trip_id,
            Stop.sequence_number,
            Later_Stop_Delays.total_delay + delay_minutes
        FROM Stop
        JOIN Later_Stop_Delays
            ON Stop.trip_id = Later_Stop_Delays.trip_id
           AND Stop.sequence_number = Later_Stop_Delays.sequence_number + 1
    )
    INSERT INTO Delay_Propagation (
        incident_id,
        trip_id,
        stop_id,
        delay_minutes,
        calculated_timestamp,
        impact_scope
    )
    SELECT
        incident_id,
        trip_id,
        Later_Stop_Delays.stop_id,
        Later_Stop_Delays.total_delay,
        NOW(),
        'Later Stops'
    FROM Later_Stop_Delays
    WHERE Later_Stop_Delays.stop_id != start_stop_id;
END

-- ==================================================================================
-- 2. Trip Status Change When Delay Exceeds Threshold (Sean Wang)
-- ==================================================================================
  
CREATE TRIGGER Update_Trip_Status
AFTER INSERT ON Delay_Propagation
FOR EACH ROW
BEGIN
    DECLARE Max_Delay INT;

    SELECT MAX(delay_minutes)
    INTO Max_Delay
    FROM Delay_Propagation
    WHERE trip_id = NEW.trip_id;

    IF Max_Delay >= 15 THEN
        UPDATE Trip
        SET trip_status = 'Delayed'
        WHERE trip_id = NEW.trip_id
          AND trip_status != 'Delayed';
    END IF;
END

-- ==================================================================================
-- 3. Public Reports Stay Anonymous (Sean Wang)
-- ==================================================================================

CREATE VIEW Public_Incident_Report AS
SELECT
    incident_id,
    description,
    reported_timestamp,
    incident_source,

    (SELECT name
     FROM Incident_Status
     WHERE status_id = Incident_Report.status_id) AS Status_Name,

    (SELECT name
     FROM Report_Category
     WHERE category_id = Incident_Report.category_id) AS Category_Name

FROM Incident_Report;

-- ==================================================================================
-- 4. Incident Status Must Follow the Right Order (Sean Wang)
-- ==================================================================================

CREATE TRIGGER Check_Incident_Status
BEFORE UPDATE ON Incident_Report
FOR EACH ROW
BEGIN
    DECLARE Reported INT;
    DECLARE In_Progress INT;
    DECLARE Resolved INT;
    DECLARE Cancelled INT;
    
    SELECT status_id INTO Reported
    FROM Incident_Status
    WHERE name = 'Reported';

    SELECT status_id INTO In_Progress
    FROM Incident_Status
    WHERE name = 'In-Progress';

    SELECT status_id INTO Resolved
    FROM Incident_Status
    WHERE name = 'Resolved';

    SELECT status_id INTO Cancelled
    FROM Incident_Status
    WHERE name = 'Cancelled';
    
    IF OLD.status_id != NEW.status_id THEN
        IF NOT (
            (OLD.status_id = Reported AND NEW.status_id = In_Progress) OR
            (OLD.status_id = In_Progress AND NEW.status_id = Resolved) OR
            (OLD.status_id = In_Progress AND NEW.status_id = Cancelled)
        ) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid status order';
        END IF;
    END IF;
END


USE mydb;
SHOW TABLES;

DELIMITER $$

-- =========================================================
-- RULE 5 (Tia Parker)
-- I use a small link table so I can connect duplicate-like
-- reports back to one main incident and then raise priority
-- based on how many different users reported it.
-- =========================================================

CREATE TABLE IF NOT EXISTS Incident_Report_Link (
    child_incident_id INT PRIMARY KEY,
    parent_incident_id INT NOT NULL,
    linked_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_incident_id) REFERENCES Incident_Report(incident_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (parent_incident_id) REFERENCES Incident_Report(incident_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) $$

DROP PROCEDURE IF EXISTS sp_update_incident_priority $$
CREATE PROCEDURE sp_update_incident_priority(IN p_parent_incident_id INT)
BEGIN
    DECLARE unique_users INT DEFAULT 0;

    SELECT COUNT(DISTINCT ir.user_id)
    INTO unique_users
    FROM Incident_Report ir
    WHERE ir.incident_id = p_parent_incident_id
       OR ir.incident_id IN (
            SELECT child_incident_id
            FROM Incident_Report_Link
            WHERE parent_incident_id = p_parent_incident_id
       );

    UPDATE Incident_Report
    SET priority_id =
        CASE
            WHEN unique_users >= 5 THEN (SELECT priority_id FROM Priority_Level WHERE name = 'High' LIMIT 1)
            WHEN unique_users >= 3 THEN (SELECT priority_id FROM Priority_Level WHERE name = 'Medium' LIMIT 1)
            ELSE (SELECT priority_id FROM Priority_Level WHERE name = 'Low' LIMIT 1)
        END
    WHERE incident_id = p_parent_incident_id;
END $$

DROP PROCEDURE IF EXISTS sp_link_duplicate_incident $$
CREATE PROCEDURE sp_link_duplicate_incident(IN p_child_incident_id INT)
BEGIN
    DECLARE v_category_id INT;
    DECLARE v_station_id INT;
    DECLARE v_reported_timestamp TIMESTAMP;
    DECLARE v_parent_id INT DEFAULT NULL;

    SELECT category_id, reported_timestamp
    INTO v_category_id, v_reported_timestamp
    FROM Incident_Report
    WHERE incident_id = p_child_incident_id;

    SELECT station_id
    INTO v_station_id
    FROM Incident_Station
    WHERE incident_id = p_child_incident_id
    LIMIT 1;

    SELECT ir.incident_id
    INTO v_parent_id
    FROM Incident_Report ir
    JOIN Incident_Station ist ON ir.incident_id = ist.incident_id
    JOIN Incident_Status s ON ir.status_id = s.status_id
    WHERE ir.incident_id <> p_child_incident_id
      AND ir.category_id = v_category_id
      AND ist.station_id = v_station_id
      AND s.name NOT IN ('Resolved', 'Cancelled')
      AND ABS(TIMESTAMPDIFF(MINUTE, ir.reported_timestamp, v_reported_timestamp)) <= 30
    ORDER BY ir.reported_timestamp DESC
    LIMIT 1;

    IF v_parent_id IS NOT NULL THEN
        INSERT IGNORE INTO Incident_Report_Link (child_incident_id, parent_incident_id)
        VALUES (p_child_incident_id, v_parent_id);

        CALL sp_update_incident_priority(v_parent_id);
    END IF;
END $$


-- =========================================================
-- RULE 6 (Tia Parker)
-- My rule says infrastructure incidents should create
-- maintenance tickets automatically, and incidents should
-- not be resolved until all related tickets are completed
-- and have updates.
-- =========================================================

CREATE TABLE IF NOT EXISTS Maintenance_Ticket (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id INT NOT NULL,
    ticket_status VARCHAR(45) NOT NULL,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES Incident_Report(incident_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) $$

CREATE TABLE IF NOT EXISTS Maintenance_Update (
    update_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    update_note TEXT NOT NULL,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES Maintenance_Ticket(ticket_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) $$

DROP TRIGGER IF EXISTS trg_auto_create_maintenance_ticket $$
CREATE TRIGGER trg_auto_create_maintenance_ticket
AFTER INSERT ON Incident_Report
FOR EACH ROW
BEGIN
    DECLARE cat_name VARCHAR(100);

    SELECT name
    INTO cat_name
    FROM Report_Category
    WHERE category_id = NEW.category_id
    LIMIT 1;

    IF cat_name IN ('Maintenance', 'Infrastructure', 'Track Issue', 'Signal Failure') THEN
        INSERT INTO Maintenance_Ticket (incident_id, ticket_status)
        VALUES (NEW.incident_id, 'Open');
    END IF;
END $$

DROP TRIGGER IF EXISTS trg_block_incident_resolution $$
CREATE TRIGGER trg_block_incident_resolution
BEFORE UPDATE ON Incident_Report
FOR EACH ROW
BEGIN
    DECLARE resolved_id INT;
    DECLARE unfinished_count INT DEFAULT 0;
    DECLARE missing_updates INT DEFAULT 0;

    SELECT status_id
    INTO resolved_id
    FROM Incident_Status
    WHERE name = 'Resolved'
    LIMIT 1;

    IF NEW.status_id = resolved_id AND OLD.status_id <> NEW.status_id THEN
        SELECT COUNT(*)
        INTO unfinished_count
        FROM Maintenance_Ticket
        WHERE incident_id = OLD.incident_id
          AND ticket_status <> 'Completed';

        SELECT COUNT(*)
        INTO missing_updates
        FROM Maintenance_Ticket mt
        WHERE mt.incident_id = OLD.incident_id
          AND NOT EXISTS (
              SELECT 1
              FROM Maintenance_Update mu
              WHERE mu.ticket_id = mt.ticket_id
          );

        IF unfinished_count > 0 OR missing_updates > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Incident cannot be resolved until all tickets are completed and updated';
        END IF;
    END IF;
END $$


-- =========================================================
-- RULE 7 (Tia Parker)
-- I am treating Delay_Propagation as the source of truth.
-- If a trip has delay_minutes > 0, I mark it Delayed.
-- Otherwise I mark it On Time.
-- =========================================================

DROP PROCEDURE IF EXISTS sp_refresh_trip_status $$
CREATE PROCEDURE sp_refresh_trip_status(IN p_trip_id INT)
BEGIN
    DECLARE max_delay INT DEFAULT 0;

    SELECT COALESCE(MAX(delay_minutes), 0)
    INTO max_delay
    FROM Delay_Propagation
    WHERE trip_id = p_trip_id;

    UPDATE Trip
    SET trip_status =
        CASE
            WHEN max_delay > 0 THEN 'Delayed'
            ELSE 'On Time'
        END
    WHERE trip_id = p_trip_id;
END $$

DROP TRIGGER IF EXISTS trg_delay_insert $$
CREATE TRIGGER trg_delay_insert
AFTER INSERT ON Delay_Propagation
FOR EACH ROW
BEGIN
    CALL sp_refresh_trip_status(NEW.trip_id);
END $$

DROP TRIGGER IF EXISTS trg_delay_update $$
CREATE TRIGGER trg_delay_update
AFTER UPDATE ON Delay_Propagation
FOR EACH ROW
BEGIN
    CALL sp_refresh_trip_status(NEW.trip_id);
END $$

DROP TRIGGER IF EXISTS trg_delay_delete $$
CREATE TRIGGER trg_delay_delete
AFTER DELETE ON Delay_Propagation
FOR EACH ROW
BEGIN
    CALL sp_refresh_trip_status(OLD.trip_id);
END $$


-- =========================================================
-- RULE 8 (Tia Parker)
-- I want incidents to auto-resolve when the last dependent
-- maintenance ticket is completed, and I also want a timed
-- escalation for unresolved high-priority incidents.
-- =========================================================

CREATE TABLE IF NOT EXISTS Rule_Config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value INT NOT NULL
) $$

INSERT INTO Rule_Config (config_key, config_value) VALUES
('ESCALATED_HOURS', 2),
('OVERDUE_HOURS', 6)
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value) $$

DROP TRIGGER IF EXISTS trg_auto_resolve_from_ticket $$
CREATE TRIGGER trg_auto_resolve_from_ticket
AFTER UPDATE ON Maintenance_Ticket
FOR EACH ROW
BEGIN
    DECLARE remaining_open INT DEFAULT 0;
    DECLARE missing_updates INT DEFAULT 0;
    DECLARE resolved_id INT;

    IF NEW.ticket_status = 'Completed' AND OLD.ticket_status <> 'Completed' THEN
        SELECT COUNT(*)
        INTO remaining_open
        FROM Maintenance_Ticket
        WHERE incident_id = NEW.incident_id
          AND ticket_status <> 'Completed';

        SELECT COUNT(*)
        INTO missing_updates
        FROM Maintenance_Ticket mt
        WHERE mt.incident_id = NEW.incident_id
          AND NOT EXISTS (
              SELECT 1
              FROM Maintenance_Update mu
              WHERE mu.ticket_id = mt.ticket_id
          );

        IF remaining_open = 0 AND missing_updates = 0 THEN
            SELECT status_id
            INTO resolved_id
            FROM Incident_Status
            WHERE name = 'Resolved'
            LIMIT 1;

            UPDATE Incident_Report
            SET status_id = resolved_id
            WHERE incident_id = NEW.incident_id;
        END IF;
    END IF;
END $$

DROP EVENT IF EXISTS ev_escalate_high_priority_incidents $$
CREATE EVENT ev_escalate_high_priority_incidents
ON SCHEDULE EVERY 15 MINUTE
DO
BEGIN
    DECLARE escalated_hours INT;
    DECLARE overdue_hours INT;
    DECLARE escalated_id INT;
    DECLARE overdue_id INT;

    SELECT config_value INTO escalated_hours
    FROM Rule_Config
    WHERE config_key = 'ESCALATED_HOURS';

    SELECT config_value INTO overdue_hours
    FROM Rule_Config
    WHERE config_key = 'OVERDUE_HOURS';

    SELECT status_id INTO escalated_id
    FROM Incident_Status
    WHERE name = 'Escalated'
    LIMIT 1;

    SELECT status_id INTO overdue_id
    FROM Incident_Status
    WHERE name = 'Overdue'
    LIMIT 1;

    UPDATE Incident_Report ir
    JOIN Priority_Level pl ON ir.priority_id = pl.priority_id
    JOIN Incident_Status s ON ir.status_id = s.status_id
    SET ir.status_id = escalated_id
    WHERE pl.name = 'High'
      AND s.name NOT IN ('Resolved', 'Cancelled', 'Escalated', 'Overdue')
      AND TIMESTAMPDIFF(HOUR, ir.reported_timestamp, NOW()) >= escalated_hours;

    UPDATE Incident_Report ir
    JOIN Priority_Level pl ON ir.priority_id = pl.priority_id
    JOIN Incident_Status s ON ir.status_id = s.status_id
    SET ir.status_id = overdue_id
    WHERE pl.name = 'High'
      AND s.name NOT IN ('Resolved', 'Cancelled', 'Overdue')
      AND TIMESTAMPDIFF(HOUR, ir.reported_timestamp, NOW()) >= overdue_hours;
END $$

DELIMITER ;

-- ==================================================================================
-- 9. Inactive Tracking/User Cleanup (Nate Mugambi)
-- ==================================================================================

CREATE PROCEDURE get_inactive_users(IN days_limit INT)
BEGIN
    SELECT
         SELECT 
        usr.user_id,
        usr.username,
        usr.email,
        MAX(activity_log.activity_time) AS most_recent_activity
    FROM `User` AS usr
    LEFT JOIN (
        SELECT user_id, created_timestamp AS activity_time FROM Notification
        UNION ALL
        SELECT user_id, created_timestamp FROM Incident_Update
        UNION ALL
        SELECT user_id, created_timestamp FROM Upvote
        UNION ALL
        SELECT user_id, created_timestamp FROM Vote
        UNION ALL
        SELECT user_id, created_timestamp FROM Saved_Station
    ) AS activity_log
        ON usr.user_id = activity_log.user_id
    GROUP BY usr.user_id, usr.username, usr.email
    HAVING most_recent_activity IS NULL
       OR most_recent_activity < NOW() - INTERVAL days_limit DAY;
END
-- ==================================================================================
-- 10. Average Rating Auto-Update (Nate Mugambi)
-- ==================================================================================
    
CREATE TRIGGER upvoteInsert
AFTER INSERT ON Upvote
FOR EACH ROW
BEGIN
    UPDATE Incident_Report
    SET total_upvotes = (
        SELECT COUNT(*) FROM Upvote
        WHERE incident_id = NEW.incident_id
    )
    WHERE incident_id = NEW.incident_id;
END


CREATE TRIGGER voteInsert
-- still not sure how to create trigger for this one
END

-- ==================================================================================
-- 11. Real Time Capacity Update (Nate Mugambi)
-- ==================================================================================

CREATE TRIGGER checkCapacityBeforeInsert
BEFORE INSERT ON Live_Feed
FOR EACH ROW
BEGIN
    IF NEW.capacity_percentage < 0 OR NEW.capacity_percentage > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid capacity value (must be 0–100).';
    END IF;
END


CREATE TRIGGER checkCapacityBeforeUpdate
BEFORE UPDATE ON Live_Feed
FOR EACH ROW
BEGIN
    IF NEW.capacity_percentage < 0 OR NEW.capacity_percentage > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid capacity value (must be 0–100).';
    END IF;
END

USE mydb;
SHOW TABLES;

DELIMITER $$


-- ==================================================================================
-- 12. Incident report completeness (Devin Yuan)
-- ==================================================================================
DELIMITER //
CREATE TRIGGER Incident_Report
BEFORE INSERT ON Incident_Report
FOR EACH ROW
BEGIN
    IF NEW.category_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Incident report must include an incident type (category_id)';
    END IF;

    IF NEW.description IS NULL OR LENGTH(TRIM(NEW.description)) < 10 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Incident report must include sufficient description (such as location via Incident_Station)';
    END IF; 

    IF NEW.priority_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Incident report must include priority level';
    END IF; 
END //
DELIMITER ;
-- ==================================================================================
-- 13. Audit logs for all severity and status changes (Devin Yuan)
-- ==================================================================================

CREATE TABLE IF NOT EXISTS Audit_Log
(
    log_id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name        VARCHAR(64)    NOT NULL,
    record_id         INT            NOT NULL,
    field_name        VARCHAR(64)    NOT NULL,
    old_value         TEXT,
    new_value         TEXT,
    changed_by        INT,
    changed_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER //

CREATE TRIGGER Audit_Incident_Changes
AFTER UPDATE ON Incident_Report
FOR EACH ROW
BEGIN

    IF OLD.status_id != NEW.status_id THEN
        INSERT INTO Audit_log (table_name, record_id, field_name, old_value, new_value, changed_by)
        VALUES
        (
            'Incident_Report',
            NEW.incident_id,
            'status_id',
            (SELECT name FROM Incident_Status WHERE status_id = OLD.status_id),
            (SELECT name FROM Incident_Status WHERE status_id = NEW.status_id),
            NEW.user_id
        );
    END IF;

    IF OLD.priority_id != NEW.priority_id THEN
        INSERT INTO Audit_Log (table_name, record_id, field_name, old_value, new_value, changed_by)
        VALUES (
            'Incident_Report',
            NEW.incident_id,
            'priority_id',
            (SELECT name FROM Priority_Level WHERE priority_id = OLD.priority_id),
            (SELECT name FROM Priority_Level WHERE priority_id = NEW.priority_id),
            NEW.user_id
        );
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER Audit_Trip_Status_Change
AFTER UPDATE ON Trip
FOR EACH ROW
BEGIN
    IF OLD.trip_status != NEW.trip_status THEN
        INSERT INTO Audit_Log (table_name, record_id, field_name, old_value, new_value, changed_by)
        VALUES ('Trip', NEW.trip_id, 'trip_status', OLD.trip_status, NEW.trip_status, NULL);
    END IF;
END //
DELIMITER ;
    
-- ==================================================================================
-- 14. Age or account verification (Devin Yuan)
-- ==================================================================================

DELIMITER //

CREATE TRIGGER Audit_Incident_Changes
AFTER UPDATE ON Incident_Report
FOR EACH ROW
BEGIN
   DECLARE account_age_days INT DEFAULT 999;
    DECLARE is_verified TINYINT DEFAULT 0;

    SELECT DATEDIFF(NOW(), created_at), email_verified 
    INTO account_age_days, is_verified
    FROM User 
    WHERE user_id = NEW.user_id;

    -- Block high-priority or escalated reports from new/unverified accounts
    IF (account_age_days < 7 OR is_verified = 0) THEN
        IF NEW.priority_id >= 4   -- adjust number based on your Priority_Level table
           OR (SELECT escalation_flag FROM Report_Category WHERE category_id = NEW.category_id) = 1 THEN
            
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Account must be at least 7 days old and verified to submit high-priority or escalated incidents.';
        END IF;
    END IF;
END //
DELIMITER ;

-- ==================================================================================
-- 15. No overlapping maintenance window for same assets (Devin Yuan)
-- ==================================================================================

CREATE TABLE IF NOT EXISTS Maintenance_Ticket (
    ticket_id       INT AUTO_INCREMENT PRIMARY KEY,
    incident_id     INT,
    asset_type      VARCHAR(50) NOT NULL,        -- e.g. 'station', 'train', 'line'
    asset_id        INT NOT NULL,
    planned_start   DATETIME NOT NULL,
    planned_end     DATETIME NOT NULL,
    ticket_status   VARCHAR(45) DEFAULT 'Open',
    INDEX idx_asset (asset_type, asset_id),
    FOREIGN KEY (incident_id) REFERENCES Incident_Report(incident_id) ON DELETE CASCADE
);

-- Once the table exists, add these two triggers:
DELIMITER //
CREATE TRIGGER Prevent_Overlapping_Maintenance_Insert
BEFORE INSERT ON Maintenance_Ticket
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM Maintenance_Ticket
        WHERE asset_type = NEW.asset_type
          AND asset_id = NEW.asset_id
          AND ticket_status NOT IN ('Completed', 'Cancelled')
          AND (
               (NEW.planned_start BETWEEN planned_start AND planned_end)
            OR (NEW.planned_end   BETWEEN planned_start AND planned_end)
            OR (planned_start     BETWEEN NEW.planned_start AND NEW.planned_end)
          )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Overlapping maintenance window for the same asset is not allowed.';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER Prevent_Overlapping_Maintenance_Update
BEFORE UPDATE ON Maintenance_Ticket
FOR EACH ROW
BEGIN
    IF NEW.planned_start != OLD.planned_start OR NEW.planned_end != OLD.planned_end THEN
        IF EXISTS (
            SELECT 1 FROM Maintenance_Ticket
            WHERE asset_type = NEW.asset_type
              AND asset_id = NEW.asset_id
              AND ticket_id != NEW.ticket_id
              AND ticket_status NOT IN ('Completed', 'Cancelled')
              AND (
                   (NEW.planned_start BETWEEN planned_start AND planned_end)
                OR (NEW.planned_end   BETWEEN planned_start AND planned_end)
                OR (planned_start     BETWEEN NEW.planned_start AND NEW.planned_end)
              )
        ) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Overlapping maintenance window for the same asset is not allowed.';
        END IF;
    END IF;
END //
DELIMITER ;