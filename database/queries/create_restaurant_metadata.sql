CREATE TABLE restaurant_metadata (
    table_name TEXT,
    column_name TEXT,
    description TEXT,
    PRIMARY KEY (table_name, column_name)
);