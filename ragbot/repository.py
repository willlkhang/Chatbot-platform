from __future__ import annotations

import os  # env vars + filesystem paths for sqlite location
import json  # store/load metadata in sqlite text columns
import sqlite3  # sqlite DB used as our lightweight vector store
import struct  # packs float vectors into bytes for sqlite-vec
import threading  # lock access to sqlite connection across threads
import logging  # log warnings about extensions + embedding issues
import contextvars  # used to track sources per-request (safe under concurrency)
from typing import Any  # typing for kwargs dicts

from dotenv import load_dotenv  # load .env for local settings
from langchain_ollama import OllamaEmbeddings  # embeddings client for Ollama /embed endpoint
from langchain_core.documents import Document  # Document type (content + metadata)

import sqlite_vec  # sqlite-vec extension (fast ANN-ish search inside sqlite)

load_dotenv()  # load env variables (helps local dev + docker)

logger = logging.getLogger("ragbot.repository")  # module logger


# Per-request sink for retrieved chunks; the controller installs a fresh list
# at the start of each request so concurrent users don't see each other's hits.
_SOURCES_CV: contextvars.ContextVar[list[dict] | None] = contextvars.ContextVar(
    "ragbot_sources", default=None
)


def _serialize_vector(vec: list[float]) -> bytes:
    # sqlite-vec expects the embedding as a blob of little-endian float32 values
    return struct.pack(f"{len(vec)}f", *vec)  # packs floats into bytes blob


def record_sources(docs, *, course: str | None = None) -> None:
    """Push the given documents into the current request's citation sink.

    Called by the tools layer *after* reranking, so the API only surfaces the
    chunks the LLM actually saw, not the raw vector-store fan-out.
    """
    sink = _SOURCES_CV.get()  # fetch request-local list (or None if caller didn't set it)
    if sink is None:  # if this isn't called within a request, just do nothing
        return
    for d in docs:  # push one citation per returned chunk
        meta = d.metadata or {}  # defensive: metadata can be None
        sink.append(  # append structured citation dict for API response
            {
                "course": meta.get("course", course),  # prefer per-doc course, fallback to arg
                "source": meta.get("source"),  # usually file name (set during ingestion)
                "section": meta.get("section"),  # optional field if you later add sectioning
                "chunk_index": meta.get("chunk_index"),  # stable chunk id within ingestion run
                # Prefer rerank score (cross-encoder) when present.
                "score": meta.get("_rerank_score") or meta.get("_score"),  # score for debugging/sorting
                "snippet": d.page_content[:240],  # short preview (avoid huge payloads)
            }
        )


def _split_document(doc: Document, *, chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Last-resort character splitter used only when embedding the document
    raises a context-length error from Ollama. Real ingestion uses a token-
    aware splitter in ``ingestion.py``."""
    text = doc.page_content or ""  # grab original content (safe default empty)
    if len(text) <= chunk_size:  # already small enough for embed call
        return [doc]  # keep as-is

    step = max(1, chunk_size - chunk_overlap)  # slide window forward with overlap
    chunks: list[Document] = []  # collect child documents
    for start in range(0, len(text), step):  # generate sliding windows
        chunk = text[start : start + chunk_size]  # char window
        if not chunk:  # should never happen, but keep safe
            continue
        meta = dict(doc.metadata or {})  # clone original metadata
        meta["chunk_start"] = start  # track which slice this came from (debugging)
        meta["chunk_end"] = start + len(chunk)  # track end (debugging)
        chunks.append(Document(page_content=chunk, metadata=meta))  # new smaller Document
        if start + chunk_size >= len(text):  # stop once we reached the end
            break
    return chunks  # return split docs


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
        self._sqlite_path = sqlite_path or os.environ.get("RAG_MEMORY_DB") or "./data/rag_memory.sqlite"  # db path
        self._embedding_model = embedding_model or os.environ.get("OLLAMA_EMBED_MODEL") or "nomic-embed-text"  # embed model
        self._course = course or "unknown"  # stored as default metadata on insert
        self._embed_dim = int(embed_dim or os.environ.get("EMBED_DIM") or 768)  # index dimension must match model output
        self._k = k  # default top-k for similarity_search
        self._embed_chunk_size = int(os.environ.get("EMBED_CHUNK_SIZE") or "1500")  # fallback chunk size (chars) if embed fails
        self._embed_chunk_overlap = int(os.environ.get("EMBED_CHUNK_OVERLAP") or "150")  # overlap for fallback splitter
        # Ollama enforces a combined context budget per /embed call, so send
        # documents in small batches rather than one giant request.
        self._embed_batch_size = int(os.environ.get("EMBED_BATCH_SIZE") or "16")  # batch size for embed_documents

        os.makedirs(os.path.dirname(self._sqlite_path) or ".", exist_ok=True)  # ensure db directory exists
        self._conn = sqlite3.connect(self._sqlite_path, check_same_thread=False)  # allow use across threads
        self._conn.execute("PRAGMA journal_mode=WAL;")  # better concurrent read/write
        self._conn.execute("PRAGMA synchronous=NORMAL;")  # performance vs durability trade-off
        self._conn.execute("PRAGMA busy_timeout=5000;")  # wait if DB is locked rather than failing instantly
        self._lock = threading.RLock()  # re-entrant lock so nested calls are safe

        try:
            self._conn.enable_load_extension(True)  # needed for sqlite-vec to load
            sqlite_vec.load(self._conn)  # loads vec0 virtual table module
            self._conn.enable_load_extension(False)  # reduce attack surface afterwards
            self._vec_available = True  # fast vector search available
        except (sqlite3.OperationalError, AttributeError) as e:
            self._vec_available = False  # fallback mode (slower)
            logger.warning(
                "sqlite-vec extension unavailable for %s (%s). "
                "Falling back to brute-force cosine.",
                self._sqlite_path, e,
            )

        with self._lock:
            self._conn.execute(  # main doc table (content + metadata + legacy embedding json)
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
                self._conn.execute(  # vec0 virtual table stores embeddings in a fast index
                    f"""
                    CREATE VIRTUAL TABLE IF NOT EXISTS rag_documents_vec USING vec0(
                        embedding float[{self._embed_dim}] distance_metric=cosine
                    )
                    """
                )

            self._conn.commit()  # persist schema changes

        if self._vec_available:
            self._migrate_legacy_embeddings()  # populate vec0 index from any older DB rows

        _embed_kwargs: dict[str, Any] = {"model": self._embedding_model}  # args for OllamaEmbeddings
        _base = os.environ.get("OLLAMA_BASE_URL")  # optionally point embeddings at custom Ollama host
        if _base:
            _embed_kwargs["base_url"] = _base.rstrip("/")  # normalize base url
        self._embeddings = OllamaEmbeddings(**_embed_kwargs)  # embeddings client used for insert + query

    @property
    def retriever(self):
        return _SqliteRetriever(self)  # LangGraph/LC "retriever-like" wrapper

    def _migrate_legacy_embeddings(self) -> None:
        """Populate vec0 from any rows whose JSON embedding hasn't been indexed yet."""
        with self._lock:
            already = self._conn.execute("SELECT COUNT(*) FROM rag_documents_vec").fetchone()[0]  # rows already in vec0
            total = self._conn.execute(
                "SELECT COUNT(*) FROM rag_documents "
                "WHERE embedding_json IS NOT NULL AND embedding_json != ''"
            ).fetchone()[0]
            if already >= total or total == 0:  # nothing to do (or already migrated)
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
                try:  # parse JSON embedding blob from legacy DBs
                    vec = json.loads(embedding_json)
                except (TypeError, json.JSONDecodeError):  # skip broken rows
                    continue
                if len(vec) != self._embed_dim:  # vec0 needs consistent dimension
                    logger.warning(
                        "Skipping row %d: dim mismatch (%d vs %d)",
                        row_id, len(vec), self._embed_dim,
                    )
                    continue
                self._conn.execute(
                    "INSERT INTO rag_documents_vec(rowid, embedding) VALUES (?, ?)",
                    (row_id, _serialize_vector(vec)),
                )
            self._conn.commit()  # commit index inserts
            logger.info("Migration complete for %s", self._sqlite_path)  # final status log

    def clear(self) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM rag_documents")  # delete documents
            if self._vec_available:  # keep vec0 in sync
                self._conn.execute("DELETE FROM rag_documents_vec")  # delete embeddings index
            self._conn.commit()  # persist deletes
        logger.info("Cleared all rows in %s", self._sqlite_path)  # log so user knows it happened

    def _embed_in_batches(self, texts: list[str]) -> list[list[float]]:
        """Embed ``texts`` in batches, halving batch size on context-length errors."""
        out: list[list[float]] = []  # output vectors in the same order as input texts
        batch_size = self._embed_batch_size  # starting batch size
        i = 0  # current offset into texts list
        while i < len(texts):
            batch = texts[i : i + batch_size]  # slice current batch
            try:
                out.extend(self._embeddings.embed_documents(batch))  # embed batch (may raise)
                i += len(batch)  # advance by number of embedded docs
            except Exception as e:
                msg = str(e).lower()  # check error message for context-length type issues
                if "context length" in msg and batch_size > 1:  # if too big for model, reduce batch size
                    batch_size = max(1, batch_size // 2)  # halve and retry
                    logger.info("Reducing embed batch size to %d and retrying", batch_size)  # info log
                    continue  # retry same i with smaller batch
                raise  # unknown error, bubble up
        return out  # list of vectors

    def add_documents(self, docs: list[Document]) -> int:
        if not docs:  # nothing to insert
            return 0

        try:
            vectors = self._embed_in_batches([d.page_content for d in docs])  # embed all docs (batched)
        except Exception as e:
            msg = str(e).lower()  # normalize message
            if "context length" not in msg:  # only handle the known "too big" class of errors
                raise  # bubble up unexpected failures
            # A single chunk still exceeds the embedding model's context window:
            # fall back to a smaller character-window split and try again.
            smaller_size = max(200, self._embed_chunk_size // 2)  # reduce chunk size, but keep reasonable minimum
            docs = [
                c
                for d in docs
                for c in _split_document(
                    d,
                    chunk_size=smaller_size,
                    chunk_overlap=min(self._embed_chunk_overlap, smaller_size // 5),
                )
            ]
            vectors = self._embed_in_batches([d.page_content for d in docs])  # retry with smaller docs

        if vectors and len(vectors[0]) != self._embed_dim:
            raise RuntimeError(  # mismatched dimension means wrong EMBED_DIM or wrong embedding model
                f"Embedding dim {len(vectors[0])} does not match expected {self._embed_dim}. "
                f"Set EMBED_DIM accordingly or change embedding model."
            )

        inserted = 0  # track inserted docs
        with self._lock:
            for doc, vec in zip(docs, vectors, strict=True):
                meta = dict(doc.metadata or {})  # clone metadata so we can update safely
                meta.setdefault("course", self._course)  # default course label used by tools/citations
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
                row_id = cur.lastrowid  # primary key used as vec0 rowid
                if self._vec_available:
                    self._conn.execute(
                        "INSERT INTO rag_documents_vec(rowid, embedding) VALUES (?, ?)",
                        (row_id, _serialize_vector(vec)),
                    )
                inserted += 1  # increment inserted count
            self._conn.commit()  # commit inserts
        return inserted  # how many rows inserted

    def similarity_search(self, query: str, k: int | None = None) -> list[Document]:
        k = k or self._k  # default to repo-level k
        query_vec = self._embeddings.embed_query(query)  # embed query into vector

        if self._vec_available:
            return self._search_vec(query_vec, k)  # fast vec0 search
        return self._search_brute(query_vec, k)  # slow fallback (legacy json embedding mode)

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
            rows = self._conn.execute(sql, (_serialize_vector(query_vec), k)).fetchall()  # run vec0 query

        docs: list[Document] = []  # build Document list in rank order
        for content, metadata_json, distance in rows:
            meta = json.loads(metadata_json) if metadata_json else {}  # decode metadata
            # Cosine distance -> similarity (0..1, higher is better).
            meta["_score"] = max(0.0, 1.0 - float(distance))  # convert distance to similarity
            docs.append(Document(page_content=content, metadata=meta))  # create Document
        return docs  # ranked docs

    def _search_brute(self, query_vec: list[float], k: int) -> list[Document]:
        from utils.cosine import _cosine_similarity  # local import to avoid overhead if vec0 is available

        with self._lock:
            rows = self._conn.execute(
                "SELECT content, metadata_json, embedding_json FROM rag_documents "
                "WHERE embedding_json IS NOT NULL AND embedding_json != ''"
            ).fetchall()

        scored: list[tuple[float, Document]] = []  # (score, doc) pairs
        for content, metadata_json, embedding_json in rows:
            try:
                vec = json.loads(embedding_json)  # parse stored embedding vector
            except (TypeError, json.JSONDecodeError):
                continue  # skip invalid/broken rows
            score = _cosine_similarity(query_vec, vec)  # compute cosine similarity
            meta = json.loads(metadata_json) if metadata_json else {}  # decode metadata
            meta["_score"] = score  # attach score for downstream reranker/debugging
            scored.append((score, Document(page_content=content, metadata=meta)))  # store pair

        scored.sort(key=lambda x: x[0], reverse=True)  # highest score first
        return [d for _, d in scored[:k]]  # return top-k docs


class _SqliteRetriever:
    def __init__(self, repo: RagRepository) -> None:
        self._repo = repo  # wrap the repository instance

    def invoke(self, query: str, *, k: int | None = None):
        return self._repo.similarity_search(query, k=k)  # retriever interface used by tools/agent


RETRIEVAL_K = int(os.environ.get("RAGBOT_RETRIEVAL_K", "20"))  # default fan-out k for course repos

repo_ICT283 = RagRepository(sqlite_path="./data/ICT283_all.sqlite", course="ICT283", k=RETRIEVAL_K)  # ICT283 store
repo_ICT167 = RagRepository(sqlite_path="./data/ICT167_all.sqlite", course="ICT167", k=RETRIEVAL_K)  # ICT167 store
repo_ICT159 = RagRepository(sqlite_path="./data/ICT159_all.sqlite", course="ICT159", k=RETRIEVAL_K)  # ICT159 store

retriever_ICT283 = repo_ICT283.retriever  # exported retriever for tools layer
retriever_ICT167 = repo_ICT167.retriever  # exported retriever for tools layer
retriever_ICT159 = repo_ICT159.retriever  # exported retriever for tools layer