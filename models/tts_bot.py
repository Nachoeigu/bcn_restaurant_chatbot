from langchain_core.runnables import chain, RunnableLambda
from langchain_community.tools import ElevenLabsText2SpeechTool
from dotenv import load_dotenv
import logging
import logging_config

logger = logging.getLogger(__name__)

load_dotenv()


class TextToSpeech:

    def __init__(self):
        logger.info("Setting text to speech bot...")
        self.tts = ElevenLabsText2SpeechTool()
        self.__creating_chain()
    
    def __creating_chain(self):
        self.chain = RunnableLambda(self.tts.run) \
                    | RunnableLambda(self.tts.play)

    def generating_audio(self, input_string):
        logger.info("Generating audio...")
        return self.chain.invoke(input_string)
