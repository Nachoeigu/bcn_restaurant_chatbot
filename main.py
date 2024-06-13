from models.pinecone_managment import PineconeManagment
from models.qa_bot import QAbot
from models.tool_analyzer import ToolAnalyzer
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

if __name__ == '__main__':
    #model = ChatGoogleGenerativeAI(model = 'gemini-1.5-pro', temperature = 0)
    model = ChatOpenAI(model = 'gpt-3.5-turbo', temperature = 0)
    app = PineconeManagment()
    app.loading_vdb(index_name = 'bcnrestaurant')
    retriever = app.vdb.as_retriever(search_type="similarity", 
                                     search_kwargs={"k": 2})
    ta_bot = ToolAnalyzer(model = model)
    qa_bot = QAbot(model = model,
                   retriever= retriever)
    user_query = input("Make your query: ")
    result_toolanalyzer = ta_bot.analyzing_query(user_query = user_query)
    if result_toolanalyzer.go_database:
        print("Calling another LLM to make the specific SQL query in our database")
        result = 'We don´t have the agent ready yet'
    else:
        print("Going to vector database to find result...")
        result = qa_bot.query(user_query) 
    
    print(result)