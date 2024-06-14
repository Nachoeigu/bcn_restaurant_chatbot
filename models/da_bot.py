from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai.chat_models import ChatOpenAI
from constants import TABLES_INFO, SYSTEM_PROMPT_DA
from langchain.output_parsers import PydanticOutputParser
from validators.langchain_validators import ExpectedOutputBotDA


class DataAnalyst:

    def __init__(self, model):
        self.db = SQLDatabase.from_uri("sqlite:///local_database/restaurant_data.db")
        self.model = model
        self.parser = PydanticOutputParser(pydantic_object=ExpectedOutputBotDA)
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
                "format_instructions": self.parser.get_format_instructions(),
                "system_prompt": SYSTEM_PROMPT_DA},
        )

    def __creating_template_sql_to_response(self):
        self.sql_to_response_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
        Question: {user_query}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
        )

    def __creating_chain(self):
    
        querying_db =  self.question_to_sql_prompt \
                                    | self.model \
                                    | self.parser \
                                    | {'query': lambda parsed_data : parsed_data.query,
                                       'user_query': lambda parsed_data : parsed_data.user_query} \
                                    | RunnablePassthrough.assign(
                                        query=itemgetter("query"),
                                        result=self.execute_query,
                                        user_query=itemgetter("user_query")
                                    )
        translating_sql_to_audience = self.sql_to_response_prompt \
                                        | self.model \
                                        | StrOutputParser()
    
        return querying_db | translating_sql_to_audience

    def analyzing_user_query(self, user_query):
        return self.chain.invoke({'user_query': user_query})
