import pyaudio
import speech_recognition as sr
from langchain_core.runnables import RunnableLambda

class SpeechToText:

    def __init__(self, duration_secs=10):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100        
        self.DURATION_SECS = duration_secs
        self.__creating_chain()

    def catch_audio(self):
        """
        Start listening and process it
        """
        MIC = pyaudio.PyAudio()
        stream = MIC.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK)
        
        print("Catching audio...")
        
        frames = []
        
        for _ in range(0, int(self.RATE / self.CHUNK * self.DURATION_SECS)):
            data = stream.read(self.CHUNK)
            frames.append(data)
            
        print("End of recording...")
        
        stream.stop_stream()
        stream.close()
        MIC.terminate()
        audio = b''.join(frames)
        
        return audio

    def audio_to_text(self, audio_data) -> str:
        """
        Converts audio into text
        """
        recognizer = sr.Recognizer()
        audio_data = sr.AudioData(audio_data, sample_rate=44100, sample_width=2)
        text = recognizer.recognize_google(audio_data=audio_data, language='en')

        return text

    def __creating_chain(self):
        self.chain = RunnableLambda(lambda _: self.catch_audio()) \
                    | RunnableLambda(lambda audio_data: self.audio_to_text(audio_data))
        
    def listen_and_transcribing_audio(self):
        return self.chain.invoke(None)