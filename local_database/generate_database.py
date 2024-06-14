import sqlite3
import os

def read_query(query_name):
    current_directory = os.path.dirname(__file__)
    with open(current_directory + f'/queries/{query_name}.sql', 'r') as file:
        sql_query = file.read()

    return sql_query


def setup_database():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'restaurant_data.db'))
    c = conn.cursor()
    c.execute(read_query("create_restaurant_catalog"))
    c.executescript(read_query("populate_restaurant_catalog"))
    c.execute(read_query("create_restaurant_availability"))
    c.executescript(read_query("populate_restaurant_availability"))
    c.execute(read_query("create_restaurant_tables_info"))
    c.executescript(read_query("populate_restaurant_tables_info"))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
