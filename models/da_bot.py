from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai.chat_models import ChatOpenAI
from constants import TABLES_INFO, SYSTEM_PROMPT_DA
from langchain.output_parsers import PydanticOutputParser
from validators.langchain_validators import ExpectedSQLOutputBotDA,ExpectedResponseOutputBotDA
from utils import evaluating_sql_output

class DataAnalyst:

    def __init__(self, model):
        self.db = SQLDatabase.from_uri("sqlite:///local_database/restaurant_data.db")
        self.model = model
        self.sqlquery_parser = PydanticOutputParser(pydantic_object=ExpectedSQLOutputBotDA)
        self.response_parser = PydanticOutputParser(pydantic_object=ExpectedResponseOutputBotDA)
        self.execute_query = QuerySQLDataBaseTool(db=self.db)
        self.__creating_template_question_to_sql()
        self.__creating_template_sql_to_response()
        self.chain = self.__creating_chain()

    def __creating_template_question_to_sql(self):
        self.question_to_sql_prompt = PromptTemplate(
            template="{system_prompt}.\n {tables_info}\n{format_instructions}\n\n The question you should answer with a SQL query is: {user_query}\n",
            input_variables=["user_query"],
            partial_variables={
                "tables_info":TABLES_INFO,
                "format_instructions": self.sqlquery_parser.get_format_instructions(),
                "system_prompt": SYSTEM_PROMPT_DA},
        )

    def __creating_template_sql_to_response(self):
        self.sql_to_response_prompt = PromptTemplate(
            template="{system_prompt}.\n User question: {user_query}\n SQL Query: {query} \n SQL Result: {result}.\n{format_instructions}",
            input_variables=["user_query","query","result"],
            partial_variables={
                "tables_info":TABLES_INFO,
                "format_instructions": self.response_parser.get_format_instructions(),
                "system_prompt": "Given the following user question, its corresponding SQL query, and the output of that SQL query, answer the user question providing all the details needed."},
        )
        
    def __creating_chain(self):
        querying_db =  self.question_to_sql_prompt \
                        | self.model \
                        | self.sqlquery_parser \
                        | {'query': lambda parsed_data : parsed_data.query,
                            'user_query': lambda parsed_data : parsed_data.user_query} \
                        | RunnablePassthrough.assign(
                            query=itemgetter("query"),
                            result=self.execute_query,
                            user_query=itemgetter("user_query")
                        ) \
                        | {'query': itemgetter("query"),
                           'result': lambda executed_result: evaluating_sql_output(executed_result['result']),
                           'user_query': itemgetter("user_query")}
        translating_sql_to_audience = self.sql_to_response_prompt \
                                        | self.model \
                                        | self.response_parser
    
        return querying_db | translating_sql_to_audience

    def analyzing_user_query(self, user_query):
        return self.chain.invoke({'user_query': user_query})
