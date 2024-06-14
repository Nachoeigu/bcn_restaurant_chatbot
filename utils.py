import sqlite3
from models.pinecone_managment import PineconeManagment
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

@tool
def analyzing_secure_sql_query(query_definition:str) -> str:
    """It analyzes if the query contains delete or alter statements"""
    prohibited_keywords = ['delete table', 'truncate table', 'drop table','delete view', 'truncate view', 'drop view','delete from','alter column','alter table']
    for warning_keyword in prohibited_keywords:
        if warning_keyword in query_definition.lower():
            raise Exception(f"Insecure query: {query_definition}")
    
    return query_definition

def vdb_creation(index_name):
    """
    This function is used for creation of the Vector Database. Only one time.
    """
    app = PineconeManagment()
    docs = app.reading_datasource()
    app.creating_index(index_name = index_name, docs = docs)

    return app.loading_vdb(index_name = 'bcnrestaurant')

def run_query(query):
    db_path = './local_database/restaurant_catalog.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute(query)
        result = c.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        return result
