from __future__ import annotations

import os
import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.documents import Document

logger = logging.getLogger("ragbot.reranker")


def _flag(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Reranker:
    def __init__(
        self,
        *,
        model_name: str | None = None,
        cache_dir: str | None = None,
        max_length: int = 512,
    ) -> None:
        self._model_name = model_name or os.environ.get(
            "RAGBOT_RERANK_MODEL", "ms-marco-MiniLM-L-12-v2"
        )
        self._cache_dir = cache_dir or os.environ.get(
            "RAGBOT_RERANK_CACHE_DIR", "./data/flashrank_cache"
        )
        self._max_length = max_length
        self._enabled = _flag("RAGBOT_RERANK_ENABLED", True)
        self._ranker = None
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _ensure_loaded(self):
        if self._ranker is not None or not self._enabled:
            return
        with self._lock:
            if self._ranker is not None:
                return
            try:
                from flashrank import Ranker
                os.makedirs(self._cache_dir, exist_ok=True)
                logger.info(
                    "Loading reranker model '%s' (cache=%s)",
                    self._model_name, self._cache_dir,
                )
                self._ranker = Ranker(
                    model_name=self._model_name,
                    cache_dir=self._cache_dir,
                    max_length=self._max_length,
                )
            except Exception as e:
                logger.warning("Reranker disabled (init failed): %s", e)
                self._enabled = False

    def rerank(
        self, query: str, docs: list["Document"], *, top_k: int = 3
    ) -> list["Document"]:
        if not docs:
            return []
        if not self._enabled or len(docs) <= 1:
            return docs[:top_k]

        self._ensure_loaded()
        if self._ranker is None:
            return docs[:top_k]

        try:
            from flashrank import RerankRequest

            passages = [
                {"id": i, "text": d.page_content, "meta": d.metadata}
                for i, d in enumerate(docs)
            ]
            results = self._ranker.rerank(RerankRequest(query=query, passages=passages))

            reranked: list = []
            for r in results[:top_k]:
                idx = int(r["id"])
                doc = docs[idx]
                doc.metadata["_rerank_score"] = float(r.get("score", 0.0))
                reranked.append(doc)
            return reranked
        except Exception as e:
            # Never let reranking failure break a query.
            logger.warning("Reranking failed, returning top-K from vector store: %s", e)
            return docs[:top_k]


reranker = Reranker()
