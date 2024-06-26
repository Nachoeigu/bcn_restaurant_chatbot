import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from langchain_core.prompts import PromptTemplate
from constants import SYSTEM_PROMPT_TA
from langchain.output_parsers import PydanticOutputParser
from validators.langchain_validators import ExpectedOutputBotTA
from langchain.globals import set_debug
import logging
import logging_config
from langchain.memory import ConversationBufferMemory

logger = logging.getLogger(__name__)

if os.getenv("LANGCHAIN_DEBUG_LOGGING") == 'True':
    set_debug(True)


class ToolAnalyzer:

    def __init__(self, model):
        logger.info("Setting tool analyzer bot...")
        self.parser = PydanticOutputParser(pydantic_object=ExpectedOutputBotTA)
        self.__creating_prompt()
        self.model = model
    
    def set_memory(self, memory: ConversationBufferMemory):
        self.memory = memory

    def __creating_prompt(self):
        self.prompt = PromptTemplate(
            template="{system_prompt}\n{format_instructions}\n{memory}\n{user_query}\n",
            input_variables=["user_query","memory"],
            partial_variables={"format_instructions": self.parser.get_format_instructions(),
                               "system_prompt": SYSTEM_PROMPT_TA},
        )

    def analyzing_query(self, user_query):
        logger.info("Analyzing if we need to go to Vectorstore or SQL Database...")
        chain = self.prompt | self.model | self.parser

        return chain.invoke({'user_query':user_query,
                             'memory':self.memory})
