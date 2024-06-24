import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

import sqlite3
from utils import read_query, get_info_from_database

def setup_database():
    connection = sqlite3.Connection(f'{WORKDIR}/database/restaurant_data.db')
    cursor = connection.cursor()
    cursor.execute(read_query("create_restaurant_catalog"))
    cursor.executescript(read_query("populate_restaurant_catalog"))
    cursor.execute(read_query("create_restaurant_availability"))
    cursor.executescript(read_query("populate_restaurant_availability", current_date = True))
    cursor.execute(read_query("create_restaurant_tables_info"))
    cursor.executescript(read_query("populate_restaurant_tables_info"))
    cursor.execute(read_query("create_restaurant_metadata"))
    cursor.executescript(read_query("populate_restaurant_metadata"))
    
    connection.commit()
    connection.close()

    get_info_from_database()


if __name__ == "__main__":
    setup_database()



