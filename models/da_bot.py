import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from constants import SYSTEM_PROMPT_DA, SYSTEM_PROMPT_COMMUNICATOR
from validators.langchain_validators import ExpectedSQLOutputBotDA,ExpectedResponseOutputBotDA
from utils import evaluating_sql_output
from langchain.globals import set_debug

set_debug(True)

class DataAnalyst:

    def __init__(self, model):
        self.db = SQLDatabase.from_uri(f"sqlite:///{WORKDIR}/database/restaurant_data.db")
        
        with open(f"{WORKDIR}/database/database_info.txt",'r') as file:
            self.tables_info = file.read()

        self.model_structured_for_sql_development = model.with_structured_output(ExpectedSQLOutputBotDA)
        self.model_structed_for_answering = model.with_structured_output(ExpectedResponseOutputBotDA)
        self.execute_query = QuerySQLDataBaseTool(db=self.db)
        self.__creating_template_question_to_sql()
        self.__creating_template_sql_to_response()
        self.chain = self.__creating_chain()

    def __creating_template_question_to_sql(self):
        self.question_to_sql_prompt = PromptTemplate(
            template="{system_prompt}.\n {tables_info}\n\n{memory}\nThe question you should answer with a SQL query is: {user_query}\n",
            input_variables=["user_query", "memory"],
            partial_variables={
                "tables_info":self.tables_info,
                "system_prompt": SYSTEM_PROMPT_DA},
        )

    def __creating_template_sql_to_response(self):
        self.sql_to_response_prompt = PromptTemplate(
            template="{system_prompt}.\n Now that you understand, answer this.\n User question: {user_query}\n SQL Query: {query} \n SQL Result: {result}.",
            input_variables=["user_query","query","result"],
            partial_variables={
                "system_prompt": SYSTEM_PROMPT_COMMUNICATOR},
        )
        
    def __creating_chain(self):
        querying_db =  self.question_to_sql_prompt \
                        | self.model_structured_for_sql_development \
                        | {'query': lambda parsed_data : parsed_data.query,
                            'user_query': lambda parsed_data : parsed_data.user_query} \
                        | RunnablePassthrough.assign(
                            query=itemgetter("query"),
                            result=self.execute_query | RunnableLambda(evaluating_sql_output),
                            user_query=itemgetter("user_query")
                        ) 
        translating_sql_to_audience = self.sql_to_response_prompt \
                                        | self.model_structed_for_answering
    
        return querying_db \
                | translating_sql_to_audience

    def analyzing_user_query(self, user_query, memory=''):
        return self.chain.invoke({'user_query': user_query,
                                  'memory': memory})
