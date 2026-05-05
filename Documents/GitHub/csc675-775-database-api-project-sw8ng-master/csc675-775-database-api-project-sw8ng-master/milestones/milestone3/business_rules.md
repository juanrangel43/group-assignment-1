1. Delay propagation (Sean Wang)
   - Purpose: Automatically calculate how a delay at one stop affects all later stops on the same trip.
   - Description: When an incident causes a delay at a specific stop, the system must insert a Delay_Propagation record for every subsequent stop on that trip, with the cumulative delay minutes
   - Challenges: The number of stops varies per trip; we must handle multiple incidents affecting the same trip.
   - Assumptions: Each trip’s stops are ordered by sequence_number. Delay is additive.
   - Planned Approach: Uses Recursive CTE to insert propagation records

2. Trip status change when delay exceeds threshold (Sean Wang)
   - Purpose: Inform passengers when a trip becomes significantly more delayed
   - Description: If Delay_Propagation for a trip has delay_minutes greater than a certain threshold, set the trip's trip_status to delayed
   - Challenges: The database must compare delay values with the threshold each time delays change.
   - Assumptions: The threshold is predefined
   - Planned Approach: Use a trigger that updates trip status when delay records are inserted or updated.

3. Public reports stay anonymous (Sean Wang)
   - Purpose: Protect user privacy in public reports
   - Description: Public reports must not show user_id or any identifiable personal information
   - Challenges: Need to ensure all public access uses the anonymized view, not the base table
   - Assumptions: Admins have access to full data; public users do not
   - Planned Approach: Create a database VIEW named Public_Incident_Report that excludes user_id and joins only non‑sensitive columns.

4. Incident status must follow the right order (Sean Wang)
   - Purpose: Make sure incident progress is tracked properly
   - Description: The only allowed status path is Reported -> In-Progress -> Resolved/Cancelled
   - Challenge: Need to know the previous status and the allowed next statuses
   - Assumptions: Status names are fixed and stored in the Incident_Status look-up table
   - Planned Approach: Use a trigger or function to validate status changes

5. Intelligent Incident Reporting to reduce redundancy and provide incident escalation (Tia Parker)
   - Purpose: Maintain a clean incident database by preventing duplicate reports and actively reflecting the issue's urgency
   - Description: The database must prevent the creation of duplicate incident reports for the same location, type, and time window. Instead, child reports must be linked to the existing active incident. As unique users contribute to linked reports, the incident severity will update incrementally to reflect the impact.
   - Challenges: Defining the “similarity” threshold for location and time. Making sure that the same user cannot inflate the severity indefinitely and cause the system to move slowly.
   - Assumptions: Severity levels will follow a fixed scale (Low < Medium < High)
   - Planned Approach: Use a BEFORE INSERT trigger to intercept new reports, perform a check on existing records to see if they are in the same proximity of a new report, and update the existing incident’s count instead of creating a new row

6. Integrated maintenance and incident lifecycle (Tia Parker)
   - Purpose: Ensure that the infrastructure repairs are actionable and the incident statuses reflect the state of the system
   - Description: For infrastructure-related incidents (equipment or track issues), the database must automatically generate a linked maintenance ticket. An incident cannot be marked as “Resolved” until all associated maintenance tickets are marked “Completed” without at least one documented work update record.
   - Challenges: Managing the one-to-many relationships between an incident and multiple possible maintenance tasks.
   - Assumptions: Maintenance updates are stored in a child table linked to the Ticket ID
   - Planned Approach: Use AFTER INSERT triggers on the incident table that will spawn tickets and BEFORE UPDATE triggers on both Incident and Ticket tables to enforce cross-table status validation.

7. Real-time system status with integrity (Tia Parker)
   - Purpose: Provide passengers with an accurate, data-driven overview of transit conditions.
   - Description: Route and Line statuses have to reflect active incidents dynamically. If a route has a high-severity incident, the status needs to be automatically updated to “On-Time” if active Delay_Propagation records for that trip will still show a general delay > 0.
   - Challenges: Recalculating route status in real-time without causing the performance during high volumes of incident reporting to lag.
   - Assumptions: Delay propagation data is the “ground truth” for trip timing
   - Planned Approach: Use AFTER UPDATE triggers on Incidents to recalculate the parent route status and BEFORE UPDATE triggers on the Trip table to block invalid status changes.

8. Automate Resolutions and Escalations (Tia Parker)
   - Purpose: Prevent critical issues from crashing the system and ensure that it remains self-correcting
   - Description: Incidents of high severity need to automatically transition to “Escalated” or to “Overdue” status if they are unresolved. There needs to be a predefined time threshold to achieve this. The system must also automatically mark an incident as “Resolved” the moment the last dependent maintenance task is completed and finalized.
   - Challenges: Implementing time-based logic within a database environment that depends on events to trigger actions.
   - Assumptions: Escalation thresholds are defined in a configuration table and follow time-based logic.
   - Planned Approach: Use an AFTER UPDATE trigger on Maintenance Tickets for auto-resolution and a Scheduled Event (database’s job) that will run periodically to flag the overdue high-priority incidents.

9. Inactive User Tracking/ Cleanup (Nate Mugambi)
   - Purpose: Maintain efficiency of the system/data collection purposes.
   - Description: Inactive users for a certain time frame are marked as inactive. The user will benefit from the knowledge of which users are more active than others, and data regarding levels of inactivity based on location/stop may be beneficial. There will need to be a predetermined threshold of time a user is inactive to be marked as such.
   - Challenges: Tracking time spent inactive or determining how long it would take to mark a user as such. Activity on the online system may not be related to how frequently someone uses the transit. The data collected from online activity may not always reflect real life activity.
   - Assumptions: The “last login” data of each user will be stored.
   - Planned Approach: A scheduled and recurring event would occur when data would be collected on inactive users and the cleanup would occur as a result.

10. Average Rating Auto-Update (Nate Mugambi)
    - Purpose: Keeping the overall ratings consistent.
    - Description: The average rating must reflect the aggregate of all the reviews in the system.
    - Challenges: Aggregation may be difficult after a certain amount of reviews are placed. As the review amount gets larger more space may be required to hold each data point.
    - Assumptions: All the rating data will be collected and stored in the system.
    - Planned Approach: Average rating is updated in real time after every review is placed.

11. Real-Time Capacity Adjustment (Nate Mugambi)
    - Purpose: Improving the accuracy of attendance tracking.
    - Description: Event capacity is dynamically adjusted based on actual check-ins vs registrations. Check ins cannot exceed the registrations. The registration number cannot exceed the capacity. Check ins are more like a subset of the registrations.
    - Challenges: Real-time updates may be inconsistent, some users may register but never check in.
    - Assumptions: A system exists to maintain the registrations and subsequent check ins
    - Planned Approach: Trigger will check when the user registers and when the user checks in.

12. Incident Report Completeness (Devin Yuan)
    - Purpose: Prevents an incomplete report from going through and causing confusion to first responders, maintenance teams, or system operators that act immediately and require accurate information
    - Description: Every incident report submitted to the system must include sufficient location information (such as stop/stations or geographical coordinates), and an incident type. Reports missing this critical information shall be rejected so that all incidents can be properly routed, linked to maintenance activities, and responded to effectively
    - Challenges: Handling reports with incomplete GPS data from mobile users while still enforcing minimum location requirements and trying to distinguish between optional rich location data and mandatory core location fields.
    - Assumptions: Location fields are required for both routing and maintenance linking
    - Planned Approach: NOT NULL constraints and CHECK constraints or BEFORE INSERT, which triggers validation of the presence of the key field

13. Audit Logs for All Severity and Status Changes (Devin Yuan)
    - Purpose: Provides traceability for incident handling and compliance
    - Description: Any changes to the incident status, severity, trip status, or maintenance ticket status must create an Audit_log record with user_id, timestamp, old_value, and new_value
    - Challenges: Performance overhead on high-volume tables
    - Assumptions: Logging is mandatory for accountability
    - Planned Approach: AFTER UPDATE triggers on key tables that insert into an Audit_Log_Table

14. Age or Account Verification (Devin Yuan)
    - Purpose: Reduce spam or fraudulent reports in the public incident system
    - Description: Users with accounts younger than X days or without email verification cannot submit high-severity incidents or certain types (e.g., safety threats)
    - Challenges: Balancing accessibility with abuse prevention
    - Assumptions: Account creation timestamp and verification status are stored
    - Planned Approach: BEFORE INSERT trigger on Incident that checks user account age/verification

15. No Overlapping Maintenance Window for Same Assets (Devin Yuan)
    - Purpose: Avoid scheduling conflicts on infrastructure (e.g., elevator or track segment)
    - Description: A new Maintenance_Ticket for a given asset cannot overlap in time with an existing open ticket for the same asset
    - Challenges: Handling different time granularities (hours vs. days)
    - Assumptions: Assets have unique identifiers; tickets store start/end planned times
    - Planned Approach: BEFORE INSERT/UPDATE trigger that queries for overlapping active tickets
