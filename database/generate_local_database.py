import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

import sqlite3
from utils import read_query

def setup_database():
    connection = sqlite3.connectionect(os.path.join(os.path.dirname(__file__), 'restaurant_data.db'))
    cursor = connection.cursor()
    cursor.execute(read_query("create_restaurant_catalog"))
    cursor.executescript(read_query("populate_restaurant_catalog"))
    cursor.execute(read_query("create_restaurant_availability"))
    cursor.executescript(read_query("populate_restaurant_availability"))
    cursor.execute(read_query("create_restaurant_tables_info"))
    cursor.executescript(read_query("populate_restaurant_tables_info"))
    
    connection.commit()
    connection.close()

if __name__ == "__main__":
    setup_database()
