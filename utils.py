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
    
import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_table_info(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def get_sample_rows(cursor, table_name, limit=3):
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT {limit}")
    return cursor.fetchall()

def get_column_statistics(cursor, table_name, column_name):
    cursor.execute(f"SELECT COUNT(DISTINCT {column_name}) FROM {table_name}")
    distinct_count = cursor.fetchone()[0]
    
    if distinct_count <= 15:
        cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name}")
        values = [row[0] for row in cursor.fetchall()]
        return f"contains these values: {values}"
    else:
        cursor.execute(f"SELECT MIN({column_name}), MAX({column_name}) FROM {table_name}")
        min_val, max_val = cursor.fetchone()
        return f"contains more than 15 unique values. The range of values goes from {min_val} to {max_val}"


def get_info_from_database():
    connection = sqlite3.connect(f'{WORKDIR}/database/restaurant_data.db')
    cursor = connection.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    result = ""
    
    for table in tables:
        table_name = table[0]
        if table_name == 'sqlite_sequence':
            continue        
        # Get table info
        columns = get_table_info(cursor, table_name)
        
        # Generate CREATE TABLE statement
        create_statement = f"CREATE TABLE {table_name} (\n"
        for col in columns:
            col_name, col_type, notnull, dflt_value, pk = col[1], col[2], col[3], col[4], col[5]
            col_constraints = []
            if notnull:
                col_constraints.append("NOT NULL")
            if dflt_value is not None:
                col_constraints.append(f"DEFAULT {dflt_value}")
            if pk:
                col_constraints.append("PRIMARY KEY")
            create_statement += f"\t{col_name} {col_type} {' '.join(col_constraints)},\n"
        create_statement = create_statement.rstrip(",\n") + "\n);\n"
        
        # Get sample rows
        sample_rows = get_sample_rows(cursor, table_name)
        sample_rows_str = f"\n/*\n3 rows from {table_name} table:\n"
        sample_rows_str += ",".join([col[1] for col in columns]) + "\n"
        for row in sample_rows:
            sample_rows_str += ",".join([repr(item) for item in row]) + "\n"
        sample_rows_str += "*/\n"
        
        # Get column statistics
        column_stats = f"\n/*\nStatistic info of the table {table_name}\n"
        for col in columns:
            col_name = col[1]
            stat_info = get_column_statistics(cursor, table_name, col_name)
            column_stats += f"{col_name}: {stat_info}\n"
        column_stats += "*/\n"
        
        result += create_statement + sample_rows_str + column_stats + "\n"
    
    connection.close()
    
    with open(f"{WORKDIR}/database/database_info.txt",'w') as file:
        file.write(result)

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
