CREATE DATABASE IF NOT EXISTS event_scheduler;
USE event_scheduler;

CREATE TABLE IF NOT EXISTS event (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS resource (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_name VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS event_resource_allocation (
    allocation_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    resource_id INT,
    FOREIGN KEY (event_id) REFERENCES event(event_id),
    FOREIGN KEY (resource_id) REFERENCES resource(resource_id)
);
