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

if os.getenv("LANGCHAIN_DEBUG_LOGGING") == 'True':
    set_debug(True)

class ChainPipeline:

    def __init__(self, model, conversation_in_text=True):
        app = PineconeManagment()
        self.ta_bot = ToolAnalyzer(model = model)
        self.da_bot = DataAnalyst(model = model)
        retriever = loading_retriever(app = app)
        self.qa_bot = QAbot(model = model,
                    retriever= retriever)
        self.conversation_in_text = conversation_in_text
        self.chain = self.__implementing_chain()

    def __implementing_chain(self):

        return RunnableLambda(self.ta_bot.analyzing_query) \
                | RunnableBranch(
                (
                    #Chain if the tool analyzer consider that the query could be solved with SQL Database
                    lambda tool_analyzer_result: tool_analyzer_result.go_database,
                    #Intermediate output where we obtain the response based on the developed SQL Query
                    ({'intermediate_output': lambda tool_analyzer_result: self.da_bot.analyzing_user_query(user_query = tool_analyzer_result.user_query)}) \
                        #Analyzing if it is needed to go to Vectorstore or if the answer from the Data Analyst is good for it.
                        | RunnableBranch(
                            (
                                #Chain if the Data Analyst bot couldn´t answer succesfully the initial query
                                lambda intermediate_output : (intermediate_output['intermediate_output'].solved == False)|(intermediate_output['intermediate_output'].response == ''),
                                #In this chain, we go to the Vectorstore and retrieve the result from it
                                {'output': lambda tool_analyzer_result: self.qa_bot.query(user_query = tool_analyzer_result.user_query)}
                            ),
                            #Chain if the Data Analyst bot could answer succesfully the initial query
                            {'output': lambda intermediate_output: intermediate_output['intermediate_output'].response}
                            
                        )
                ),
                (
                    #Chain if the tool analyzer consider that the query could be solved with Vector Database
                    lambda tool_analyzer_result: tool_analyzer_result.go_database == False,
                    #Chain, where we retrieve the result from the Vector database
                    ({'output': lambda tool_analyzer_result: self.qa_bot.query(user_query = tool_analyzer_result.user_query)})
                ),
                RunnableLambda(lambda tool_analyzer_result: tool_analyzer_result)
            )