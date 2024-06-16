import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from models.pinecone_managment import PineconeManagment
from models.qa_bot import QAbot
from models.da_bot import DataAnalyst
from models.tool_analyzer import ToolAnalyzer
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

#model = ChatGoogleGenerativeAI(model = 'gemini-1.5-pro', temperature = 0)
model = ChatOpenAI(model = 'gpt-4o', temperature = 0)
#model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
app = PineconeManagment()
ta_bot = ToolAnalyzer(model = model)
def analyzing_with_data_analyst(user_query):
    print("Analyzing on our SQL database")
    da_bot = DataAnalyst(model = model)
    da_result = da_bot.analyzing_user_query(user_query = user_query)

    return da_result
def analyzing_with_vectorstore(user_query):
    print("Going to vector database to find result...")
    app.loading_vdb(index_name = 'bcnrestaurant')
    retriever = app.vdb.as_retriever(search_type="similarity", 
                                    search_kwargs={"k": 2})
    qa_bot = QAbot(model = model,
                retriever= retriever)

    return qa_bot.query(user_query) 

if __name__ == '__main__':
    while True:
        user_query = input("Make your query: ")
        result_toolanalyzer = ta_bot.analyzing_query(user_query = user_query)
        if result_toolanalyzer.go_database:
            da_result = analyzing_with_data_analyst(user_query = user_query)
            if (da_result.solved == False)|(da_result.response == ''):
                print("Answer not present in our SQL database...")
                result = analyzing_with_vectorstore(user_query)
            else:
                result = da_result.response
        else:
            result = analyzing_with_vectorstore(user_query)
        print(f"----------------\nGENERATED ANSWER: \n{result}\n----------------")
