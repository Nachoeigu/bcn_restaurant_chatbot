import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

import sqlite3
from langchain.tools import  tool
from database.database_descriptor import DatabaseDescriber
from datetime import datetime, timedelta


load_dotenv()

def loading_retriever(app):
    print("Going to vector database to find result...")
    app.loading_vdb(index_name = 'bcnrestaurant')
    retriever = app.vdb.as_retriever(search_type="similarity", 
                                    search_kwargs={"k": 2})
    
    return retriever

def read_query(query_name,current_date:bool=False):
    with open(WORKDIR + f'/database/queries/{query_name}.sql', 'r') as file:
        sql_query = file.read()

    if current_date == False:
        return sql_query
    else:
        updated_query = sql_query
        for day in range(1, 31): 
            period = f"{day}_days_ahead"
            date = datetime.now().date() + timedelta(days=day)
            date_str = date.strftime('%Y-%m-%d')
            updated_query = updated_query.replace(f"'{period}'", f"'{date_str}'")
        
        return updated_query


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
