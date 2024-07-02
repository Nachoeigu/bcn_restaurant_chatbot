import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from models.tts_bot import TextToSpeech
from models.stt_bot import SpeechToText
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.globals import set_debug
from models.chain_pipeline import ChainPipeline

import logging
import logging_config

logger = logging.getLogger(__name__)

if os.getenv("LANGCHAIN_DEBUG_LOGGING") == 'True':
    set_debug(True)


if __name__ == '__main__':
    #model = ChatVertexAI(model="gemini-pro", temperature=0)
    #model = ChatGoogleGenerativeAI(model = 'gemini-1.5-pro', temperature = 0)
    model = ChatOpenAI(model = 'gpt-4o', temperature = 0)
    #model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
    memory = ConversationBufferWindowMemory(memory_key='chat_history',return_messages=True,k=3)
    tts_bot = TextToSpeech()
    stt_bot = SpeechToText(duration_secs=10)

    entire_chain = ChainPipeline(model = model, 
                                 conversation_in_text=True)
    
    while True:
        entire_chain.set_memory(memory)

        user_query = input("Write your question: \n - ") if entire_chain.conversation_in_text else stt_bot.listen_and_transcribing_audio()
        
        result = entire_chain.run(user_query = user_query)
        

        output = {
            'output': result['output'] if entire_chain.conversation_in_text else tts_bot.generating_audio(result['output'])
        }
        try:
            print("AI Response:\n"+output['output'])
        except:
            pass

        memory.save_context(
            {'user':user_query},
            {'bot':result['output']}
        )   
        entire_chain.set_memory(memory)

