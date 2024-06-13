from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from constants import SYSTEM_PROMPT_TA
from langchain.output_parsers import PydanticOutputParser
from langchain_validators import ExpectedOutputBotTA

load_dotenv()

class ToolAnalyzer:

    def __init__(self, model):
        self.parser = PydanticOutputParser(pydantic_object=ExpectedOutputBotTA)
        self.__creating_prompt()
        self.model = model

    def __creating_prompt(self):
        self.prompt = PromptTemplate(
            template="{system_prompt}.\n Answer the user query.\n{format_instructions}\n{user_query}\n",
            input_variables=["user_query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions(),
                               "system_prompt": SYSTEM_PROMPT_TA},
        )

    def analyzing_query(self, user_query):
        chain = self.prompt | self.model | self.parser

        return chain.invoke({'user_query':user_query})