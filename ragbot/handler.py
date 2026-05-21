import os
import sqlite3
import logging
from typing import TypedDict

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from graph import workflow
from repository import _SOURCES_CV

load_dotenv()

logger = logging.getLogger("ragbot.handler")


class InvokeResult(TypedDict):
    answer: str
    sources: list[dict]


def _open_sqlite(path: str) -> sqlite3.Connection:
    """Open a SQLite connection tuned for multi-threaded use.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


class RagbotService:
    """Compiled LangGraph workflow with a SQLite checkpointer.
    """

    def __init__(
        self,
        *,
        sqlite_path: str | None = None,
        default_thread_id: str = "convo_default",
    ) -> None:
        self._sqlite_path = sqlite_path or os.environ.get(
            "RAGBOT_CHECKPOINT_DB", "./data/checkpoints.sqlite"
        )
        self._default_thread_id = default_thread_id

        self._conn = _open_sqlite(self._sqlite_path)
        self._memory = SqliteSaver(self._conn)
        self._app = workflow.compile(checkpointer=self._memory)

        logger.info("RagbotService ready (checkpoint_db=%s)", self._sqlite_path)

    def invoke(self, query: str, *, thread_id: str | None = None) -> InvokeResult:
        """Run the agent and return the answer text plus structured sources."""
        config = {
            "configurable": {"thread_id": thread_id or self._default_thread_id}
        }

        sources: list[dict] = []
        token = _SOURCES_CV.set(sources)
        try:
            res = self._app.invoke(
                {"messages": [HumanMessage(content=query)]},
                config=config,
            )
        finally:
            _SOURCES_CV.reset(token)

        raw = res["messages"][-1].content
        if isinstance(raw, list):
            text = ""
            for block in raw:
                if isinstance(block, dict) and block.get("type") == "text":
                    text += block.get("text", "")
        else:
            text = raw

        return {"answer": text, "sources": _dedupe_sources(sources)}

    def export_graph(self, output_file_path: str = "flow.png") -> None:
        self._app.get_graph().draw_mermaid_png(output_file_path=output_file_path)


def _dedupe_sources(sources: list[dict]) -> list[dict]:
    """Collapse duplicate citations across multiple tool calls."""
    seen: dict[tuple, dict] = {}
    for s in sources:
        key = (s.get("course"), s.get("source"), s.get("chunk_index"))
        existing = seen.get(key)
        if existing is None or (s.get("score") or 0) > (existing.get("score") or 0):
            seen[key] = s
    return list(seen.values())


service = RagbotService()


if __name__ == "__main__":
    service.export_graph()
