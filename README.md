# BCN Restaurant Chatbot

This chatbot is useful for customer question-answering issues. Based on Artificial Intelligence, this software receives the question of an user and, in a completely autonomous way, reply to him with the correspond answer.

Applied AI approach in this project: Vector Databases Managment, Retrieval Augmented Generation (RAG), Q&A with Autonomous Data Analytics (SQL) and developing multiple LLMs working together to solve the issue.

### How to use this script?

1) Set .env variables:
    -PINECONE_API_KEY
    -LANGCHAIN_API_KEY
    -LANGCHAIN_TRACING_V2
    -LANGCHAIN_PROJECT
    -OPENAI_API_KEY
    -GOOGLE_API_KEY
    -REDSHIFT_HOST
    -REDSHIFT_PORT
    -REDSHIFT_DATABASE
    -REDSHIFT_USERNAME
    -REDSHIFT_PASSWORD
    -WORKDIR

1) First run the generate_database.py script so you have the database available.

2) In the main file you have the entry point of the process. 