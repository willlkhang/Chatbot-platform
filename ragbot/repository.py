import os
import json
import math
import sqlite3
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

class RagRepository:
    def __init__(
        self,
        *,
        sqlite_path: str | None = None,
        google_api_key: str | None = None,
        embedding_model: str = "gemini-embedding-001",
        embedding_dimensions: int = 1536,
        k: int = 3,
    ) -> None:
        self._sqlite_path = sqlite_path or os.environ.get("RAG_MEMORY_DB") or "rag_memory.sqlite"
        self._google_api_key = google_api_key or os.environ.get("GOOGLE_API_KEY")
        self._embedding_model = embedding_model
        self._embedding_dimensions = embedding_dimensions
        self._k = k

        if not self._google_api_key:
            raise ValueError("Missing GOOGLE_API_KEY for embeddings.")

        self._conn = sqlite3.connect(self._sqlite_path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                metadata_json TEXT,
                embedding_json TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_rag_documents_id ON rag_documents(id)"
        )
        self._conn.commit()

        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=self._embedding_model,
            google_api_key=self._google_api_key,
            output_dimensionality=self._embedding_dimensions,
        )

    @property
    def retriever(self):
        return _SqliteRetriever(self)

    def add_documents(self, docs: list[Document]) -> int:
        if not docs:
            return 0

        texts = [d.page_content for d in docs]
        vectors = self._embeddings.embed_documents(texts)
        rows = []
        for doc, vec in zip(docs, vectors, strict=True):
            rows.append(
                (
                    doc.page_content,
                    json.dumps(doc.metadata or {}, ensure_ascii=False),
                    json.dumps(vec),
                )
            )

        self._conn.executemany(
            "INSERT INTO rag_documents(content, metadata_json, embedding_json) VALUES(?, ?, ?)",
            rows,
        )
        self._conn.commit()
        return len(rows)

    def similarity_search(self, query: str, k: int | None = None) -> list[Document]:
        k = k or self._k
        query_vec = self._embeddings.embed_query(query)

        cur = self._conn.execute(
            "SELECT content, metadata_json, embedding_json FROM rag_documents"
        )
        scored: list[tuple[float, Document]] = []
        for content, metadata_json, embedding_json in cur.fetchall():
            vec = json.loads(embedding_json)
            score = _cosine_similarity(query_vec, vec)
            metadata = json.loads(metadata_json) if metadata_json else {}
            scored.append((score, Document(page_content=content, metadata=metadata)))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:k]]


class _SqliteRetriever:
    def __init__(self, repo: RagRepository) -> None:
        self._repo = repo

    def invoke(self, query: str):
        return self._repo.similarity_search(query)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    # If dimensions mismatch, compare on overlap.
    n = min(len(a), len(b))
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(n):
        ai = float(a[i])
        bi = float(b[i])
        dot += ai * bi
        na += ai * ai
        nb += bi * bi
    denom = math.sqrt(na) * math.sqrt(nb)
    return dot / denom if denom else 0.0


# Backwards-compatible module-level retriever.
retriever = RagRepository().retriever