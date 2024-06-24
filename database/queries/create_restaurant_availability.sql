CREATE TABLE IF NOT EXISTS restaurant_availability (
    table_id INT,
    date TEXT,
    time_slot VARCHAR(50),
    is_available BOOLEAN,
    PRIMARY KEY (table_id, date, time_slot),
    FOREIGN KEY (table_id) REFERENCES tables_info (table_id)
);