from langchain_community.document_loaders import JSONLoader
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import time
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import Dict
from validators import IndexNameStructure, ExpectedNewData


load_dotenv()

class PineconeManagment:

    def __init__(self):
        pass

    def __extract_metadata(self, record: dict, metadata: dict) -> dict:

        metadata["question"] = record['question']
        print("Metadata extracted!")
        return metadata

    def reading_datasource(self):
        loader = JSONLoader(
            file_path='./datasource/faq.json',
            jq_schema='.[]',
            text_content=False,
            metadata_func=self.__extract_metadata)

        return loader.load()
    
    def creating_index(self, index_name: str, docs: Document, dimension=1536, metric="cosine", embedding = OpenAIEmbeddings(model="text-embedding-ada-002")):
        print(f"Creating index {index_name}...")
        IndexNameStructure(index_name=index_name)
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if index_name in existing_indexes:
            raise Exception("The index already exists...")
        pc.create_index(
            name=index_name.lower(),
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

        print(f"Index '{index_name}' created...")
        
        PineconeVectorStore.from_documents(documents = docs, embedding = embedding, index_name = index_name)

        print(f"Index '{index_name}' populated with data...")
        
    def loading_vdb(self, index_name: str, embedding=OpenAIEmbeddings(model="text-embedding-ada-002")):
        print("Loading vector database from Pinecone...")
        self.vdb =  PineconeVectorStore(index_name=index_name, embedding=embedding)
        print("Vector database loaded...")
    

    def adding_documents(self, new_info: Dict[str,str]):
        ExpectedNewData(new_info = new_info)
        print("Adding data in the vector database...")
        self.vdb.add_documents([Document(page_content="question: " + new_info['question'] + '\n answer: ' + new_info['answer'], metadata={"question": new_info['question']})])
        print("More info added in the vector database...")

    def finding_similar_docs(self, user_query):
        docs = self.vdb.similarity_search(
                    query = user_query,
                    k = 3
                )
        
        return docs