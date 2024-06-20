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
from models.tts_bot import TextToSpeech
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from utils import loading_retriever


if __name__ == '__main__':
    #model = ChatVertexAI(model="gemini-pro", temperature=0)
    #model = ChatGoogleGenerativeAI(model = 'gemini-1.5-pro', temperature = 0)
    #model = ChatOpenAI(model = 'gpt-4o', temperature = 0)
    model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
    app = PineconeManagment()
    ta_bot = ToolAnalyzer(model = model)
    da_bot = DataAnalyst(model = model)
    retriever = loading_retriever(app = app)
    qa_bot = QAbot(model = model,
                retriever= retriever)
    tts_bot = TextToSpeech()

    while True:
        user_query = input("Make your query: ")
        result_toolanalyzer = ta_bot.analyzing_query(user_query = user_query)
        if result_toolanalyzer.go_database:
            da_result = da_bot.analyzing_user_query(user_query = user_query)
            if (da_result.solved == False)|(da_result.response == ''):
                print("Answer not present in our SQL database...")
                result = qa_bot.query(user_query = user_query)
            else:
                result = da_result.response
        else:
            result = qa_bot.query(user_query = user_query)

        tts_bot.generating_audio(result)
