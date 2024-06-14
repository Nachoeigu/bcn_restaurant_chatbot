from langchain_core.pydantic_v1 import BaseModel, Field, validator
import re

class ExpectedOutputBotTA(BaseModel):
    go_database: bool = Field(..., description = "True if it is question is about food catalog or table availability. Otherwise, False.")

class ExpectedResponseOutputBotDA(BaseModel):
    """Structuring the response of the LLM"""
    response: str = Field(..., description = "The final conclusion based on the provided info. If you don´t know, retrieve empty response.")
    solved: bool = Field(..., description = "If the answer couldn´t be solved False. Otherwise, True")

class ExpectedSQLOutputBotDA(BaseModel):
    """Ensuring that the output of the LLM is a SQL query without more information than the query itself"""
    query: str = Field(..., description = "SQL Query that solves the user question")
    user_query: str = Field(..., description = "The question the user made")
    @validator('query')
    def check_prohibited_statements(cls, value):
        prohibited_keywords =  [
            'delete table', 'truncate table', 'drop table',
            'delete view', 'truncate view', 'drop view',
            'delete from', 'alter column', 'alter table',
            'insert into','copy into'
        ]
        for warning_keyword in prohibited_keywords:
            if warning_keyword in value.lower():
                raise Exception(f"Insecure query: {value}")
        
        return value

    @validator('query')
    def check_if_correct_syntaxis(cls, value):
        sql_keywords = ['SELECT', 'WITH', 'SET', 'EXPLAIN', 'DESCRIBE', 'SHOW']
        sql_pattern = re.compile(r'^\s*(' + '|'.join(sql_keywords) + r')\s', re.IGNORECASE)
        if not sql_pattern.match(value):
            raise ValueError(f"Incorrect SQL syntax: {value}")
        else:
            return value
