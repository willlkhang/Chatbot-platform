from __future__ import annotations

import os  # env flags/config for reranking
import logging  # logging for model load + fallback behavior
import threading  # lock to make lazy model load safe in multi-threaded server
from typing import TYPE_CHECKING  # avoids runtime import of Document type

if TYPE_CHECKING:
    from langchain_core.documents import Document  # only for type hints (no runtime dependency)

logger = logging.getLogger("ragbot.reranker")  # module logger for rerank feature


def _flag(name: str, default: bool) -> bool:
    # helper to parse boolean-ish env vars (so config is consistent across the project)
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Reranker:
    def __init__(
        self,
        *,
        model_name: str | None = None,
        cache_dir: str | None = None,
        max_length: int = 512,
    ) -> None:
        self._model_name = model_name or os.environ.get(  # select reranker model name
            "RAGBOT_RERANK_MODEL", "ms-marco-MiniLM-L-12-v2"  # good default for small CPU rerank
        )
        self._cache_dir = cache_dir or os.environ.get(  # where Flashrank caches weights
            "RAGBOT_RERANK_CACHE_DIR", "./data/flashrank_cache"
        )
        self._max_length = max_length  # truncate passage length to keep reranker fast/stable
        self._enabled = _flag("RAGBOT_RERANK_ENABLED", True)  # easy kill-switch via env var
        self._ranker = None  # lazy init (so app can start without downloading model yet)
        self._lock = threading.Lock()  # avoid race on lazy load under concurrency

    @property
    def enabled(self) -> bool:
        return self._enabled  # allows other modules to check if reranking is active

    def _ensure_loaded(self):
        # loads the Flashrank model on-demand (first request that needs reranking)
        if self._ranker is not None or not self._enabled:  # already loaded OR feature disabled
            return
        with self._lock:  # only one thread should attempt to initialize the model
            if self._ranker is not None:  # re-check after acquiring lock
                return
            try:
                from flashrank import Ranker  # imported only when needed (keeps base install lighter)

                os.makedirs(self._cache_dir, exist_ok=True)  # ensure cache directory exists
                logger.info(  # helpful startup log (otherwise users think it's hung)
                    "Loading reranker model '%s' (cache=%s)",
                    self._model_name,
                    self._cache_dir,
                )
                self._ranker = Ranker(  # initialize reranker (may download weights)
                    model_name=self._model_name,
                    cache_dir=self._cache_dir,
                    max_length=self._max_length,
                )
            except Exception as e:  # if reranker can't load, we disable and fall back gracefully
                logger.warning("Reranker disabled (init failed): %s", e)
                self._enabled = False  # important: avoid retrying every request

    def rerank(
        self, query: str, docs: list["Document"], *, top_k: int = 3
    ) -> list["Document"]:
        # this function is designed to be safe: if anything fails, we still return something usable
        if not docs:  # nothing retrieved
            return []
        if not self._enabled or len(docs) <= 1:  # fast path: reranking off OR no meaningful ordering
            return docs[:top_k]  # just return the first K from vector store

        self._ensure_loaded()  # load model lazily
        if self._ranker is None:  # if load failed, fall back to vector-store order
            return docs[:top_k]

        try:
            from flashrank import RerankRequest  # request object for ranker.rerank

            passages = [  # Flashrank expects simple dicts containing id + text
                {"id": i, "text": d.page_content, "meta": d.metadata}  # keep meta for debugging
                for i, d in enumerate(docs)
            ]
            results = self._ranker.rerank(  # run cross-encoder ranking
                RerankRequest(query=query, passages=passages)
            )

            reranked: list = []
            for r in results[:top_k]:
                idx = int(r["id"])  # original index in docs list
                doc = docs[idx]  # pick the original Document
                doc.metadata["_rerank_score"] = float(r.get("score", 0.0))  # store score for citations/logs
                reranked.append(doc)  # append in reranked order
            return reranked  # top-K reranked docs
        except Exception as e:
            # Never let reranking failure break a query.
            logger.warning("Reranking failed, returning top-K from vector store: %s", e)  # warn and continue
            return docs[:top_k]  # safe fallback


reranker = Reranker()  # singleton instance imported by tools layer
