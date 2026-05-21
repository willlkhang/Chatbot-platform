import os
import json
import sqlite3
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from utils.cosine import _cosine_similarity

load_dotenv()

def _split_document(doc: Document, *, chunk_size: int, chunk_overlap: int) -> list[Document]:
    text = doc.page_content or ""
    if len(text) <= chunk_size:
        return [doc]

    step = max(1, chunk_size - chunk_overlap)
    chunks: list[Document] = []
    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size]
        if not chunk:
            continue
        meta = dict(doc.metadata or {})
        meta["chunk_start"] = start
        meta["chunk_end"] = start + len(chunk)
        chunks.append(Document(page_content=chunk, metadata=meta))
        if start + chunk_size >= len(text):
            break
    return chunks


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
        # Safety defaults: prevents Ollama "context length exceeded" on embeddings.
        self._embed_chunk_size = int(os.environ.get("EMBED_CHUNK_SIZE") or "1500")
        self._embed_chunk_overlap = int(os.environ.get("EMBED_CHUNK_OVERLAP") or "150")

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

        _embed_kwargs: dict = {"model": self._embedding_model}
        _base = os.environ.get("OLLAMA_BASE_URL")
        if _base:
            _embed_kwargs["base_url"] = _base.rstrip("/")
        self._embeddings = OllamaEmbeddings(**_embed_kwargs)

    @property
    def retriever(self):
        return _SqliteRetriever(self)

    def add_documents(self, docs: list[Document]) -> int:
        if not docs:
            return 0

        # Always enforce a safe chunk size for embeddings.
        expanded: list[Document] = []
        for d in docs:
            expanded.extend(
                _split_document(
                    d,
                    chunk_size=self._embed_chunk_size,
                    chunk_overlap=self._embed_chunk_overlap,
                )
            )

        texts = [d.page_content for d in expanded]

        try:
            vectors = self._embeddings.embed_documents(texts)
        except Exception as e:
            # If Ollama complains about context length, retry with smaller chunks.
            msg = str(e).lower()
            if "exceeds the context length" in msg or "context length" in msg:
                smaller_size = max(200, self._embed_chunk_size // 2)
                expanded2: list[Document] = []
                for d in docs:
                    expanded2.extend(
                        _split_document(d, chunk_size=smaller_size, chunk_overlap=min(self._embed_chunk_overlap, smaller_size // 5))
                    )
                texts2 = [d.page_content for d in expanded2]
                vectors = self._embeddings.embed_documents(texts2)
                expanded = expanded2
            else:
                raise

        rows = []
        for doc, vec in zip(expanded, vectors, strict=True):
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

retriever_ICT283 = RagRepository(sqlite_path="./data/ICT283_all.sqlite").retriever
retriever_ICT167 = RagRepository(sqlite_path="./data/ICT167_all.sqlite").retriever
retriever_ICT159 = RagRepository(sqlite_path="./data/ICT159_all.sqlite").retriever