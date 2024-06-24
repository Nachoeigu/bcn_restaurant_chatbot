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
from models.stt_bot import SpeechToText
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain.memory import ConversationBufferMemory
from utils import loading_retriever


if __name__ == '__main__':
    #model = ChatVertexAI(model="gemini-pro", temperature=0)
    #model = ChatGoogleGenerativeAI(model = 'gemini-1.5-pro', temperature = 0)
    model = ChatOpenAI(model = 'gpt-4o', temperature = 0)
    #model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
    app = PineconeManagment()
    ta_bot = ToolAnalyzer(model = model)
    da_bot = DataAnalyst(model = model)
    retriever = loading_retriever(app = app)
    qa_bot = QAbot(model = model,
                retriever= retriever)
    tts_bot = TextToSpeech()
    stt_bot = SpeechToText(duration_secs=10)
    memory = ConversationBufferMemory(memory_key='chat_history',return_messages=True)
    print("Settings:\n")
    user_input_preference = int(input("Do you want to write or speech? \n 1) Write\n 2) Speech \nAnswer: "))
    user_output_preference = int(input("Do you want to receive text or audio? \n 1) Text\n 2) Audio \nAnswer: "))

    while True:
        if user_input_preference == 1:
            user_query = input("Write your question: \n - ")
        if user_input_preference == 2:
            input("Press Intro to start your question:")
            user_query = stt_bot.listen_and_transcribing_audio()

        result_toolanalyzer = ta_bot.analyzing_query(user_query = user_query,
                                                     memory = str(memory.load_memory_variables({})))
        if result_toolanalyzer.go_database:
            da_result = da_bot.analyzing_user_query(user_query = user_query,
                                                    memory = str(memory.load_memory_variables({})))
            
            if (da_result.solved == False)|(da_result.response == ''):
                print("Answer not present in our SQL database...")
                result = qa_bot.query(user_query = user_query,
                                      memory = str(memory.load_memory_variables({})))
            else:
                result = da_result.response
        else:
            result = qa_bot.query(user_query = user_query,
                                  memory = str(memory.load_memory_variables({})))
        if user_output_preference == 1:
            print(result)
        else:
            tts_bot.generating_audio(result)

        memory.save_context(
            {'user':user_query},
            {'bot':result}
        )
