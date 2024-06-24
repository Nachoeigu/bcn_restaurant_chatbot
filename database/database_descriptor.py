import os
from dotenv import load_dotenv
import sys
import sqlite3

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

import logging
import logging_config

logger = logging.getLogger(__name__)


class DatabaseDescriber:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def get_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in self.cursor.fetchall()]
        return tables

    def get_columns_info(self, table_name):
        self.cursor.execute(f'PRAGMA table_info({table_name});')
        return self.cursor.fetchall()

    def get_column_descriptions(self, table_name):
        self.cursor.execute('SELECT column_name, description FROM restaurant_metadata WHERE table_name = ?', (table_name,))
        descriptions_info = self.cursor.fetchall()
        return {desc[0]: desc[1] for desc in descriptions_info}

    def get_sample_rows(self, table_name, limit=5):
        self.cursor.execute(f'SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT {limit};')
        return self.cursor.fetchall()

    def describe_table(self, table_name):
        columns_info = self.get_columns_info(table_name)
        column_descriptions = self.get_column_descriptions(table_name)
        sample_rows = self.get_sample_rows(table_name)

        description = f"Table: {table_name}\nColumns:\n"
        for column in columns_info:
            col_name = column[1]
            col_type = column[2]
            col_desc = column_descriptions.get(col_name, 'No description available')
            description += f"  - {col_name} ({col_type}): {col_desc}\n"

        description += "Sample Rows:\n"
        for row in sample_rows:
            description += f"  {row}\n"
        
        description += "\n"
        return description

    def describe_database(self):
        self.connect()
        tables = self.get_tables()
        description = ""
        for table_name in tables:
            if table_name in ['sqlite_sequence','restaurant_metadata']:
                continue
            description += self.describe_table(table_name)
        self.close()


        with open(f'{WORKDIR}/database/database_info.txt','w') as file:
            file.write(description)
