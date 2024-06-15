import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from utils import read_query, connection_redshift

def populating_datasources_in_redshift():
    connection = connection_redshift()
    cursor = connection.cursor()
    cursor.execute(read_query("create_restaurant_catalog"))
    cursor.execute(read_query("populate_restaurant_catalog"))
    cursor.execute(read_query("create_restaurant_availability"))
    cursor.execute(read_query("populate_restaurant_availability"))
    cursor.execute(read_query("create_restaurant_tables_info"))
    cursor.execute(read_query("populate_restaurant_tables_info"))
    connection.commit()
    cursor.close()
    connection.close()


    return True
