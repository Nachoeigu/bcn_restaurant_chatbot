from fastapi import FastAPI
#from mangum import Magnum
from models.pinecone_managment import PineconeManagment
from models.qa_bot import QAbot
from models.da_bot import DataAnalyst
from models.tool_analyzer import ToolAnalyzer
from langchain_openai.chat_models import ChatOpenAI
from main import analyzing_with_data_analyst, analyzing_with_vectorstore
import uvicorn
import json


app = FastAPI()
#handler = Magnum(app)

model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
pinecone_app = PineconeManagment()
ta_bot = ToolAnalyzer(model = model)
da_bot = DataAnalyst(model = model)


@app.get("/")
def index():
    return {"Hello": "World"}

@app.post("/query")
def answering_query(request: str) -> str:
    result_toolanalyzer = ta_bot.analyzing_query(user_query = request)
    if result_toolanalyzer.go_database:
        da_result = analyzing_with_data_analyst(user_query = request)
        if da_result.solved == False:
            result = analyzing_with_vectorstore(request)
        else:
            result = da_result.response
    else:
        result = analyzing_with_vectorstore(request)

    return result

@app.post("/model")
def provide_used_model():
    return "You are receiving answers from the model: \n-"+ model._get_ls_params()['ls_model_name']
