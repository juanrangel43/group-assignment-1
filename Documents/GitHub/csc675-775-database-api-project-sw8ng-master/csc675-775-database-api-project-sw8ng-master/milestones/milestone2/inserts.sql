
USE TransitDB; 

SET FOREIGN_KEY_CHECKS = 0;

-- Insert data into the tables -- 
INSERT INTO `USER` (`user_id`, `username`, `password`) VALUES 
(1, 'john_doe', 'password123'),
(2, 'jane_smith', 'password456'),
(3, 'officer_jones', 'password789');

-- Populate Roles --
INSERT INTO `ADMIN` (`admin_id`, `user_id`) VALUES (1, 1);
INSERT INTO `PASSENGER` (`passenger_id`, `user_id`) VALUES (1, 2);
INSERT INTO `OFFICER` (`officer_id`, `user_id`, `badge_number`) VALUES (1, 3, 1001);

-- INSERT INTO other tables as needed --


SET FOREIGN_KEY_CHECKS = 1; 