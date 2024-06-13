from .models.pinecone_managment import PineconeManagment
from .models.qa_bot import QAbot
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

def vdb_creation(index_name):
    """
    This function is used for creation of the Vector Database. Only one time.
    """
    app = PineconeManagment()
    docs = app.reading_datasource()
    app.creating_index(index_name = index_name, docs = docs)

    return app.loading_vdb(index_name = 'bcnrestaurant')


if __name__ == '__main__':
    #model = ChatGoogleGenerativeAI(model = 'gemini-1.5-pro', temperature = 0)
    model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
    app = PineconeManagment()
    app.loading_vdb(index_name = 'bcnrestaurant')
    retriever = app.vdb.as_retriever(search_type="similarity", 
                                     search_kwargs={"k": 2})
    qa_bot = QAbot(model = model,
                   retriever= retriever)
    result = qa_bot.query("Which hours are you open to the public so I can go and eat?") 
    print(result)