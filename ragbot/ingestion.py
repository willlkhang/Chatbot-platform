import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

if __name__ == "__main__":
    print("Woring, Will !!!")
    
    loader = TextLoader("./A1-QandA.txt", encoding='UTF-8')
    document = loader.load()

    print("Splitting...")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(document)

    print(f"Created {len(texts)} chunks")

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001",
                                              google_api_key=os.environ.get("GOOGLE_API_KEY"),
                                              output_dimensionality=1536)
    
    print("ingesting...")
    PineconeVectorStore.from_documents(
        texts, embeddings, index_name=os.environ['INDEX_NAME']
        )
    print("Done, Will")