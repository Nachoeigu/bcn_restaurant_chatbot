import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from fastapi import FastAPI
from langchain.memory import ConversationBufferWindowMemory
#from mangum import Magnum
from langchain_openai.chat_models import ChatOpenAI
from models.chain_pipeline import ChainPipeline
import uvicorn
import json
from models.tts_bot import TextToSpeech
from models.stt_bot import SpeechToText



app = FastAPI()
#model = ChatVertexAI(model="gemini-pro", temperature=0)
#model = ChatGoogleGenerativeAI(model = 'gemini-1.5-pro', temperature = 0)
model = ChatOpenAI(model = 'gpt-4o-mini', temperature = 0)
#model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
memory = ConversationBufferWindowMemory(memory_key='chat_history',return_messages=True,k=3)
tts_bot = TextToSpeech()
stt_bot = SpeechToText(duration_secs=10)

entire_chain = ChainPipeline(model = model, 
                                conversation_in_text=True)

@app.get("/")
def index():
    return {"App": "Running"}

@app.post("/query")
def answering_query(request: str) -> str:
    entire_chain.set_memory(memory)
    result = entire_chain.run(request)
    memory.save_context(
        {'user':request},
        {'bot':result['output']}
    )   
    entire_chain.set_memory(memory)
    return result['output']

@app.post("/model")
def provide_used_model():
    return "You are receiving answers from the model: \n-"+ model._get_ls_params()['ls_model_name']
