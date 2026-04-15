import os
import json
import sqlite3
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from utils.cosine import _cosine_similarity

load_dotenv()

class RagRepository:
    def __init__(
        self,
        *,
        sqlite_path: str | None = None,
        embedding_model: str | None = None,
        k: int = 3,
    ) -> None:
        self._sqlite_path = sqlite_path or os.environ.get("RAG_MEMORY_DB") or "./data/rag_memory.sqlite"
        self._embedding_model = embedding_model or os.environ.get("OLLAMA_EMBED_MODEL") or "nomic-embed-text"
        self._k = k

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

        self._embeddings = OllamaEmbeddings(model=self._embedding_model)

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

retriever = RagRepository().retriever