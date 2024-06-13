from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from constants import SYSTEM_PROMPT
from langchain_core.output_parsers.string import StrOutputParser

load_dotenv()

class QAbot:

    def __init__(self, model, retriever):
        self.model = model
        self.retriever = retriever
        self.__creating_prompt_template()

    def __creating_prompt_template(self):
        self.prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Based on this context: \n <context> {context} <end_context> \n\n Answer this: \n {question}")
                ]
            )
    def __format_retrieved_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def query(self, user_query):
        chain = {"context": self.retriever | self.__format_retrieved_docs, "question": RunnablePassthrough()} | self.prompt_template | self.model | StrOutputParser()

        return chain.invoke(user_query)