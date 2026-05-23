from __future__ import annotations

import os
import json
import sqlite3
import struct
import threading
import logging
import contextvars
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

import sqlite_vec

load_dotenv()

logger = logging.getLogger("ragbot.repository")


# Per-request sink for retrieved chunks; the controller installs a fresh list
# at the start of each request so concurrent users don't see each other's hits.
_SOURCES_CV: contextvars.ContextVar[list[dict] | None] = contextvars.ContextVar(
    "ragbot_sources", default=None
)


def _serialize_vector(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def record_sources(docs, *, course: str | None = None) -> None:
    """Push the given documents into the current request's citation sink.

    Called by the tools layer *after* reranking, so the API only surfaces the
    chunks the LLM actually saw, not the raw vector-store fan-out.
    """
    sink = _SOURCES_CV.get()
    if sink is None:
        return
    for d in docs:
        meta = d.metadata or {}
        sink.append(
            {
                "course": meta.get("course", course),
                "source": meta.get("source"),
                "section": meta.get("section"),
                "chunk_index": meta.get("chunk_index"),
                # Prefer rerank score (cross-encoder) when present.
                "score": meta.get("_rerank_score") or meta.get("_score"),
                "snippet": d.page_content[:240],
            }
        )


def _split_document(doc: Document, *, chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Last-resort character splitter used only when embedding a document
    exceeds the embedding model's context limit. Real ingestion uses a
    token-aware splitter in ``ingestion.py``."""
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
        course: str | None = None,
        embed_dim: int | None = None,
        k: int = 3,
    ) -> None:
        self._sqlite_path = sqlite_path or os.environ.get("RAG_MEMORY_DB") or "./data/rag_memory.sqlite"
        self._embedding_model = embedding_model or os.environ.get("HF_EMBED_MODEL") or "sentence-transformers/all-MiniLM-L6-v2"
        self._course = course or "unknown"
        self._embed_dim = int(embed_dim or os.environ.get("EMBED_DIM") or 384)
        self._k = k
        self._embed_chunk_size = int(os.environ.get("EMBED_CHUNK_SIZE") or "1500")
        self._embed_chunk_overlap = int(os.environ.get("EMBED_CHUNK_OVERLAP") or "150")
        self._embed_batch_size = int(os.environ.get("EMBED_BATCH_SIZE") or "64")

        os.makedirs(os.path.dirname(self._sqlite_path) or ".", exist_ok=True)
        self._conn = sqlite3.connect(self._sqlite_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._conn.execute("PRAGMA busy_timeout=5000;")
        self._lock = threading.RLock()

        try:
            self._conn.enable_load_extension(True)
            sqlite_vec.load(self._conn)
            self._conn.enable_load_extension(False)
            self._vec_available = True
        except (sqlite3.OperationalError, AttributeError) as e:
            self._vec_available = False
            logger.warning(
                "sqlite-vec extension unavailable for %s (%s). "
                "Falling back to brute-force cosine.",
                self._sqlite_path, e,
            )

        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rag_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    metadata_json TEXT,
                    embedding_json TEXT
                )
                """
            )

            if self._vec_available:
                self._conn.execute(
                    f"""
                    CREATE VIRTUAL TABLE IF NOT EXISTS rag_documents_vec USING vec0(
                        embedding float[{self._embed_dim}] distance_metric=cosine
                    )
                    """
                )

            self._conn.commit()

        if self._vec_available:
            self._migrate_legacy_embeddings()

        self._embeddings = HuggingFaceEmbeddings(
            model_name=self._embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    @property
    def retriever(self):
        return _SqliteRetriever(self)

    def _migrate_legacy_embeddings(self) -> None:
        """Populate vec0 from any rows whose JSON embedding hasn't been indexed yet."""
        with self._lock:
            already = self._conn.execute("SELECT COUNT(*) FROM rag_documents_vec").fetchone()[0]
            total = self._conn.execute(
                "SELECT COUNT(*) FROM rag_documents "
                "WHERE embedding_json IS NOT NULL AND embedding_json != ''"
            ).fetchone()[0]
            if already >= total or total == 0:
                return

            logger.info(
                "Migrating %d legacy embedding rows into vec0 index for %s",
                total - already, self._sqlite_path,
            )
            rows = self._conn.execute(
                """
                SELECT d.id, d.embedding_json
                FROM rag_documents d
                LEFT JOIN rag_documents_vec v ON v.rowid = d.id
                WHERE d.embedding_json IS NOT NULL
                  AND d.embedding_json != ''
                  AND v.rowid IS NULL
                """
            ).fetchall()

            for row_id, embedding_json in rows:
                try:
                    vec = json.loads(embedding_json)
                except (TypeError, json.JSONDecodeError):
                    continue
                if len(vec) != self._embed_dim:
                    logger.warning(
                        "Skipping row %d: dim mismatch (%d vs %d)",
                        row_id, len(vec), self._embed_dim,
                    )
                    continue
                self._conn.execute(
                    "INSERT INTO rag_documents_vec(rowid, embedding) VALUES (?, ?)",
                    (row_id, _serialize_vector(vec)),
                )
            self._conn.commit()
            logger.info("Migration complete for %s", self._sqlite_path)

    def clear(self) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM rag_documents")
            if self._vec_available:
                self._conn.execute("DELETE FROM rag_documents_vec")
            self._conn.commit()
        logger.info("Cleared all rows in %s", self._sqlite_path)

    def _embed_in_batches(self, texts: list[str]) -> list[list[float]]:
        """Embed ``texts`` in batches, halving batch size on context-length errors."""
        out: list[list[float]] = []
        batch_size = self._embed_batch_size
        i = 0
        while i < len(texts):
            batch = texts[i : i + batch_size]
            try:
                out.extend(self._embeddings.embed_documents(batch))
                i += len(batch)
            except Exception as e:
                msg = str(e).lower()
                if "context length" in msg and batch_size > 1:
                    batch_size = max(1, batch_size // 2)
                    logger.info("Reducing embed batch size to %d and retrying", batch_size)
                    continue
                raise
        return out

    def add_documents(self, docs: list[Document]) -> int:
        if not docs:
            return 0

        try:
            vectors = self._embed_in_batches([d.page_content for d in docs])
        except Exception as e:
            msg = str(e).lower()
            if "context length" not in msg:
                raise
            # A single chunk still exceeds the embedding model's context window:
            # fall back to a smaller character-window split and try again.
            smaller_size = max(200, self._embed_chunk_size // 2)
            docs = [
                c
                for d in docs
                for c in _split_document(
                    d,
                    chunk_size=smaller_size,
                    chunk_overlap=min(self._embed_chunk_overlap, smaller_size // 5),
                )
            ]
            vectors = self._embed_in_batches([d.page_content for d in docs])

        if vectors and len(vectors[0]) != self._embed_dim:
            raise RuntimeError(
                f"Embedding dim {len(vectors[0])} does not match expected {self._embed_dim}. "
                f"Set EMBED_DIM accordingly or change embedding model."
            )

        inserted = 0
        with self._lock:
            for doc, vec in zip(docs, vectors, strict=True):
                meta = dict(doc.metadata or {})
                meta.setdefault("course", self._course)
                cur = self._conn.execute(
                    "INSERT INTO rag_documents(content, metadata_json, embedding_json) VALUES(?, ?, ?)",
                    (
                        doc.page_content,
                        json.dumps(meta, ensure_ascii=False),
                        # The JSON embedding column is kept for backwards compat with
                        # legacy DBs (where it is NOT NULL). Real embeddings now live
                        # in the vec0 virtual table.
                        "",
                    ),
                )
                row_id = cur.lastrowid
                if self._vec_available:
                    self._conn.execute(
                        "INSERT INTO rag_documents_vec(rowid, embedding) VALUES (?, ?)",
                        (row_id, _serialize_vector(vec)),
                    )
                inserted += 1
            self._conn.commit()
        return inserted

    def similarity_search(self, query: str, k: int | None = None) -> list[Document]:
        k = k or self._k
        query_vec = self._embeddings.embed_query(query)

        if self._vec_available:
            return self._search_vec(query_vec, k)
        return self._search_brute(query_vec, k)

    def _search_vec(self, query_vec: list[float], k: int) -> list[Document]:
        if len(query_vec) != self._embed_dim:
            raise RuntimeError(
                f"Query embedding dim {len(query_vec)} does not match index dim {self._embed_dim}."
            )

        sql = """
            SELECT d.content, d.metadata_json, v.distance
            FROM rag_documents_vec v
            JOIN rag_documents d ON d.id = v.rowid
            WHERE v.embedding MATCH ? AND k = ?
            ORDER BY v.distance ASC
        """
        with self._lock:
            rows = self._conn.execute(sql, (_serialize_vector(query_vec), k)).fetchall()

        docs: list[Document] = []
        for content, metadata_json, distance in rows:
            meta = json.loads(metadata_json) if metadata_json else {}
            # Cosine distance -> similarity (0..1, higher is better).
            meta["_score"] = max(0.0, 1.0 - float(distance))
            docs.append(Document(page_content=content, metadata=meta))
        return docs

    def _search_brute(self, query_vec: list[float], k: int) -> list[Document]:
        from utils.cosine import _cosine_similarity

        with self._lock:
            rows = self._conn.execute(
                "SELECT content, metadata_json, embedding_json FROM rag_documents "
                "WHERE embedding_json IS NOT NULL AND embedding_json != ''"
            ).fetchall()

        scored: list[tuple[float, Document]] = []
        for content, metadata_json, embedding_json in rows:
            try:
                vec = json.loads(embedding_json)
            except (TypeError, json.JSONDecodeError):
                continue
            score = _cosine_similarity(query_vec, vec)
            meta = json.loads(metadata_json) if metadata_json else {}
            meta["_score"] = score
            scored.append((score, Document(page_content=content, metadata=meta)))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:k]]


class _SqliteRetriever:
    def __init__(self, repo: RagRepository) -> None:
        self._repo = repo

    def invoke(self, query: str, *, k: int | None = None):
        return self._repo.similarity_search(query, k=k)


RETRIEVAL_K = int(os.environ.get("RAGBOT_RETRIEVAL_K", "20"))

repo_ICT283 = RagRepository(sqlite_path="./data/ICT283_all.sqlite", course="ICT283", k=RETRIEVAL_K)
repo_ICT167 = RagRepository(sqlite_path="./data/ICT167_all.sqlite", course="ICT167", k=RETRIEVAL_K)
repo_ICT159 = RagRepository(sqlite_path="./data/ICT159_all.sqlite", course="ICT159", k=RETRIEVAL_K)

retriever_ICT283 = repo_ICT283.retriever
retriever_ICT167 = repo_ICT167.retriever
retriever_ICT159 = repo_ICT159.retriever