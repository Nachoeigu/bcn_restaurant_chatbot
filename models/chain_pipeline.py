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
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableLambda
from utils import loading_retriever
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

    def __where_to_go_for_answering(self, ta_answer):
        if ta_answer.go_database:
            return {'intermediate_output': self.da_bot.analyzing_user_query(user_query = self.user_query)}
        else:
            return {'output':self.qa_bot.query(user_query = self.user_query)}

    def __evaluating_developed_answer(self, answer):
        if 'intermediate_output' in answer.keys():
            #This is because we come from SQL database and we need to analyze if the result is correct
            if (answer['intermediate_output'].solved == False)|(answer['intermediate_output'].response == ''):
                return self.qa_bot.query(user_query = self.user_query)
            else:
                return {'output': answer['intermediate_output'].response}
        else:
            return answer

    def __implementing_chain(self):
        chain = RunnableLambda(self.ta_bot.analyzing_query) \
                | RunnableLambda(self.__where_to_go_for_answering) \
                | RunnableLambda(self.__evaluating_developed_answer)

        return chain
    
    def set_memory(self, memory: ConversationBufferMemory):
        self.memory = str(memory.load_memory_variables({}))
        self.ta_bot.memory = str(memory.load_memory_variables({}))
        self.da_bot.memory = str(memory.load_memory_variables({}))
        self.qa_bot.memory = str(memory.load_memory_variables({}))

    def run(self, user_query=''):
        self.user_query = user_query
        return self.chain.invoke({'user_query':user_query})
