import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from constants import SYSTEM_PROMPT_QA
from langchain_core.output_parsers.string import StrOutputParser
from langchain.globals import set_debug
from models.tts_bot import TextToSpeech
import logging
import logging_config

logger = logging.getLogger(__name__)

load_dotenv()
if os.getenv("LANGCHAIN_DEBUG_LOGGING") == True:
    set_debug(True)


class QAbot:

    def __init__(self, model, retriever):
        logger.info("Setting questioning answering bot...")
        self.model = model
        self.retriever = retriever
        self.__creating_prompt_template()
        self.__creating_chain()

    def __creating_prompt_template(self):
        self.prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT_QA),
                ("human", "Based on this context: \n <context> {context} <end_context> \n\n Answer this: \n {question}")
                ]
            )
    def __format_retrieved_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def __creating_chain(self):
        self.chain = {"context": self.retriever | self.__format_retrieved_docs, "question": RunnablePassthrough()} \
                        | self.prompt_template \
                        | self.model \
                        | StrOutputParser()


    def query(self, user_query, memory = ''):
        return self.chain.invoke(user_query+'\n'+memory)