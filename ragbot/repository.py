import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

class RagRepository:
    def __init__(
        self,
        *,
        index_name: str | None = None,
        google_api_key: str | None = None,
        embedding_model: str = "gemini-embedding-001",
        embedding_dimensions: int = 1536,
        k: int = 3,
    ) -> None:
        self._index_name = index_name or os.environ.get("INDEX_NAME")
        self._google_api_key = google_api_key or os.environ.get("GOOGLE_API_KEY")
        self._embedding_model = embedding_model
        self._embedding_dimensions = embedding_dimensions
        self._k = k

        if not self._index_name:
            raise ValueError("Missing INDEX_NAME for Pinecone index.")
        if not self._google_api_key:
            raise ValueError("Missing GOOGLE_API_KEY for embeddings.")

        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=self._embedding_model,
            google_api_key=self._google_api_key,
            output_dimensionality=self._embedding_dimensions,
        )
        self._vectorstore = PineconeVectorStore(
            index_name=self._index_name,
            embedding=self._embeddings,
        )

    @property
    def retriever(self):
        return self._vectorstore.as_retriever(search_kwargs={"k": self._k})


# Backwards-compatible module-level retriever.
retriever = RagRepository().retriever