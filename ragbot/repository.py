import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001",
                                          google_api_key=os.environ.get("GOOGLE_API_KEY"),
                                          output_dimensionality=1536)

vectorstore = PineconeVectorStore(index_name=os.environ['INDEX_NAME'], embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})