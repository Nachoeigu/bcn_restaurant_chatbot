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
from langchain_core.runnables.branch import RunnableBranch
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from utils import loading_retriever
from validators.extra_validators import QueryUserInput
from operator import itemgetter
from langchain.globals import set_debug

import logging
import logging_config

logger = logging.getLogger(__name__)

if os.getenv("LANGCHAIN_DEBUG_LOGGING") == True:
    set_debug(True)


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
    stt_bot = SpeechToText(duration_secs=10)
    memory = ConversationBufferMemory(memory_key='chat_history',return_messages=True)

    def get_user_inputs():
        return input("Write your question: \n - ")

    chain = RunnableLambda(ta_bot.analyzing_query) \
            | RunnableBranch(
            (
                #Chain if the tool analyzer consider that the query could be solved with SQL Database
                lambda tool_analyzer_result: tool_analyzer_result.go_database,
                #Intermediate output where we obtain the response based on the developed SQL Query
                ({'intermediate_output': lambda tool_analyzer_result: da_bot.analyzing_user_query(user_query = tool_analyzer_result.user_query)}) \
                    #Analyzing if it is needed to go to Vectorstore or if the answer from the Data Analyst is good for it.
                    | RunnableBranch(
                        (
                            #Chain if the Data Analyst bot couldn´t answer succesfully the initial query
                            lambda intermediate_output : (intermediate_output['intermediate_output'].solved == False)|(intermediate_output['intermediate_output'].response == ''),
                            #In this chain, we go to the Vectorstore and retrieve the result from it
                            {'output': lambda tool_analyzer_result: qa_bot.query(user_query = tool_analyzer_result.user_query)}
                        ),
                        #Chain if the Data Analyst bot could answer succesfully the initial query
                        {'output': lambda intermediate_output: intermediate_output['intermediate_output'].response}
                        
                    )
            ),
            (
                #Chain if the tool analyzer consider that the query could be solved with Vector Database
                lambda tool_analyzer_result: tool_analyzer_result.go_database == False,
                #Chain, where we retrieve the result from the Vector database
                ({'output': lambda tool_analyzer_result: qa_bot.query(user_query = tool_analyzer_result.user_query)})
            ),
            RunnableLambda(lambda tool_analyzer_result: tool_analyzer_result)
        )
    
    result = chain.invoke({'user_query': get_user_inputs(),
                            'mode':'text'
                        })    
    print(result['output'])

