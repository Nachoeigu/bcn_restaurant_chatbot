FROM public.ecr.aws/lambda/python:3.11

# Copy requirements.txt
COPY requirements.txt .

# Install the specified packages
RUN pip install -r requirements.txt --upgrade

# For local testing.
EXPOSE 8000

ENV PINECONE_API_KEY=''
ENV LANGCHAIN_API_KEY=''
ENV LANGCHAIN_TRACING_V2=''
ENV LANGCHAIN_PROJECT=''
ENV OPENAI_API_KEY=''
ENV GOOGLE_API_KEY=''

# Copy all files in ./src
COPY . .

ENTRYPOINT ["uvicorn"]
CMD ["app:app", "--host", "0.0.0.0", "--port", "8000"]