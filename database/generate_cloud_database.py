import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

import psycopg2
from utils import read_query

# Establish a connection to Redshift
conn = psycopg2.connect(
    dbname=os.getenv("REDSHIFT_DATABASE"),
    user=os.getenv("REDSHIFT_USERNAME"),
    password=os.getenv("REDSHIFT_PASSWORD"),
    host=os.getenv("REDSHIFT_HOST"),
    port=os.getenv("REDSHIFT_PORT")
)

# Create a cursor object
cur = conn.cursor()
cur.execute(read_query("create_restaurant_catalog"))
cur.execute(read_query("populate_restaurant_catalog"))
cur.execute(read_query("create_restaurant_availability"))
cur.execute(read_query("populate_restaurant_availability"))
cur.execute(read_query("create_restaurant_tables_info"))
cur.execute(read_query("populate_restaurant_tables_info"))
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
