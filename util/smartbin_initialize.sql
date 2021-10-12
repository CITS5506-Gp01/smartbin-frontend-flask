DROP TABLE IF EXISTS distances, devices;

/* Creating the tables */

CREATE TABLE devices(
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_name VARCHAR(128) NOT NULL DEFAULT 'my_iot_device',
    created_datetime TIMESTAMP DEFAULT NOW(),
    max_distance DECIMAL(6,3) DEFAULT 0,
    latitude DECIMAL(7,5),
    longitude DECIMAL(8,5)
);

CREATE TABLE distances(
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id INT,
    logged_datetime TIMESTAMP DEFAULT NOW(),
    distance DECIMAL(6,3) NOT NULL,
    temperature INT, -- Are you sure you want an integer for temperature? How does the device store temperature data?
    battery DECIMAL(5,4),
    lat DECIMAL(7,5),
    lng DECIMAL(8,5),

    FOREIGN KEY (device_id) REFERENCES devices(id)
);

/* Creating Triggers */

-- When a new distance row is inserted, check whether the value is greater than
-- the current max_distance value for that device in the devices table.
DROP TRIGGER IF EXISTS check_max_distance;
delimiter //
CREATE TRIGGER check_max_distance AFTER INSERT ON distances FOR EACH ROW
BEGIN
    -- Get the current max distance
    SELECT max_distance INTO @current_max_distance FROM devices WHERE id = NEW.device_id;
    -- Check if the current distance is 
    IF NEW.distance > @current_max_distance THEN
        UPDATE devices SET max_distance = NEW.distance WHERE id = NEW.device_id;
    END IF;
END;//
delimiter ;

-- When a new distance row is inserted, check if the lat / lng entries are NOT NULL.
-- If neither entry is NULL, update the devices table with these values.
DROP TRIGGER IF EXISTS update_device_position;
delimiter //
CREATE TRIGGER update_device_position AFTER INSERT ON distances FOR EACH ROW
BEGIN
    IF NEW.lat IS NOT NULL THEN
        IF NEW.lng IS NOT NULL THEN
            UPDATE devices SET latitude = NEW.lat WHERE id = NEW.device_id;
            UPDATE devices SET longitude = NEW.lng WHERE id = NEW.device_id;
        END IF;
    END IF;
END;//
delimiter ;