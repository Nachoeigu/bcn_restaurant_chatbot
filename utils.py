import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

import sqlite3
from models.pinecone_managment import PineconeManagment
from langchain.tools import  tool
from database.database_descriptor import DatabaseDescriber

load_dotenv()

def read_query(query_name):
    with open(WORKDIR + f'/database/queries/{query_name}.sql', 'r') as file:
        sql_query = file.read()

    return sql_query

@tool
def evaluating_sql_output(result):
    """Evaluating if the result of the SQL execution retrieves something or not"""
    if result == '':
        return 'The query didn´t provide any row'
    else:
        return result


def get_info_from_database():
    describer = DatabaseDescriber(f'{WORKDIR}/database/restaurant_data.db')
    describer.describe_database()

def run_query(query):
    db_path = f'{WORKDIR}/database/restaurant_data.db'
    connection = sqlite3.connect(db_path)
    c = connection.cursor()
    try:
        c.execute(query)
        result = c.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()
        return result
