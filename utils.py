import sqlite3
from models.pinecone_managment import PineconeManagment
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

def generate_sql_description(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    
    conn.close()
    
    return result

def get_info_from_database(db_path = './local_database/restaurant_data.db'):
    return generate_sql_description(db_path)

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
