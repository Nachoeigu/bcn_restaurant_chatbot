from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai.chat_models import ChatOpenAI
from utils import analyzing_secure_sql_query

class DataAnalyst:

    def __init__(self, model):
        self.db = SQLDatabase.from_uri("sqlite:///local_database/restaurant_data.db")
        self.model = model
        self.write_query = create_sql_query_chain(model, self.db)
        self.execute_query = QuerySQLDataBaseTool(db=self.db)
        self.__creating_template_sql_to_response()
        self.chain = self.__creating_chain()

    def __creating_template_sql_to_response(self):
        self.sql_to_response_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
        )



    def __creating_chain(self):
        return RunnablePassthrough.assign(query=self.write_query).assign(result=itemgetter('query') 
                                                                    | analyzing_secure_sql_query
                                                                    | self.execute_query
                ) | self.sql_to_response_prompt | self.model | StrOutputParser()

    def analyzing_user_query(self, user_query):
        return self.chain.invoke({'question': user_query})
