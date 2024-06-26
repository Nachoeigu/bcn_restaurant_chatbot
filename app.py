import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from fastapi import FastAPI
#from mangum import Magnum
from langchain_openai.chat_models import ChatOpenAI
from models.chain_pipeline import ChainPipeline
import uvicorn
import json


app = FastAPI()
#handler = Magnum(app)

model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
chain = ChainPipeline(model = model,
                    conversation_in_text= True).chain

@app.get("/")
def index():
    return {"Hello": "World"}

@app.post("/query")
def answering_query(request: str) -> str:
    return chain.run(user_query=request)

@app.post("/model")
def provide_used_model():
    return "You are receiving answers from the model: \n-"+ model._get_ls_params()['ls_model_name']
