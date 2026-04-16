import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

from repository import RagRepository

load_dotenv()

if __name__ == "__main__":
    print("Woring, Will !!!")
    
    loader = TextLoader("./knowledge/ICT283_cleaned_raws.txt", encoding='UTF-8')
    document = loader.load()

    print("Splitting...")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(document)

    print(f"Created {len(texts)} chunks")

    print("ingesting into sqlite long-term memory...")
    repo = RagRepository(sqlite_path=os.environ.get("RAG_MEMORY_DB") or "./data/ICT283_rag_memory.sqlite")
    inserted = repo.add_documents(texts)
    print(f"Inserted {inserted} chunks")
    print("Done, Will, This is new data ingestion")