import sqlite3
from models.pinecone_managment import PineconeManagment
from dotenv import load_dotenv

load_dotenv()

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
