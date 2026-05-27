import os
import sqlite3 #impport splite databae
import logging #import log
from typing import TypedDict #import this to create strict structural types for dictionaries

from dotenv import load_dotenv #load env

#imports LangChain's standard class for a message sent by a human user
from langchain_core.messages import HumanMessage
#imports LangGraph's built-in tool for saving conversation history to SQLite
from langgraph.checkpoint.sqlite import SqliteSaver

#import workflow blueprint from graph.py
from graph import workflow
from repository import _SOURCES_CV #import context variables used to track citations

load_dotenv()

#looging for this file
logger = logging.getLogger("ragbot.handler")

#defines the strict dictionary shape we promise to return to the web server
class InvokeResult(TypedDict):
    answer: str #answer from the AI
    sources: list[dict] #the list of citation dicts

#helper to safely open the memory database.
def _open_sqlite(path: str) -> sqlite3.Connection:
    """Open a SQLite connection tuned for multi-threaded use.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True) #creates the directory for the database if it doesn't exist
    conn = sqlite3.connect(path, check_same_thread=False) #connect to splite
    conn.execute("PRAGMA journal_mode=WAL;") #enable write-ahead logging for bteer concurrent read/write performance
    conn.execute("PRAGMA synchronous=NORMAL;") #optimizinf disks syncing speeds
    conn.execute("PRAGMA busy_timeout=5000;") #tells sqlite the wait up to 5s if the database is temporarily locked
    return conn #return the config connection


class RagbotService:
    """Compiled LangGraph workflow with a SQLite checkpointer.
    """

    def __init__(
        self,
        *, #forces all following arg to be passed as keywords arg
        sqlite_path: str | None = None, #db memory path
        default_thread_id: str = "convo_default", #thread ID arg for chat session in db, and a fallback if user doesn't provide one
    ) -> None:
        self._sqlite_path = sqlite_path or os.environ.get( #set db path from args, env var
            "RAGBOT_CHECKPOINT_DB", "./data/checkpoints.sqlite" #the limitation of this one is if can be massive
        )
        self._default_thread_id = default_thread_id 

        self._conn = _open_sqlite(self._sqlite_path)
        self._memory = SqliteSaver(self._conn)
        self._app = workflow.compile(checkpointer=self._memory)

        logger.info("RagbotService ready (checkpoint_db=%s)", self._sqlite_path)

    def invoke(self, query: str, *, thread_id: str | None = None) -> InvokeResult:
        """Run the agent and return the answer text plus structured sources."""
        config = { #buils the config dict for Langgraph
            "configurable": {"thread_id": thread_id or self._default_thread_id} #tell langgraph which conv thread to load/save
        }

        sources: list[dict] = []
        token = _SOURCES_CV.set(sources)
        try:
            res = self._app.invoke( #run langgraph agent
                {"messages": [HumanMessage(content=query)]},
                config=config, #pass thread id
            )
        finally:
            _SOURCES_CV.reset(token) #removes my list from the global context to prevent memory leaks

        raw = res["messages"][-1].content #grab the raw content of very last message in the conv which is Ai's final answer
        if isinstance(raw, list): #sometimes LLMs return content as a list of blocks
            text = ""
            for block in raw:
                if isinstance(block, dict) and block.get("type") == "text":
                    text += block.get("text", "")
        else:
            text = raw

        return {"answer": text, "sources": _dedupe_sources(sources)} #return defined typed of dict to the controller

    def export_graph(self, output_file_path: str = "flow.png") -> None: #ulitity to draw the graph diagram
        self._app.get_graph().draw_mermaid_png(output_file_path=output_file_path) #optional, this is diagram generate

#this helper function to remove deplicated ciations (if the AI calls the same tool twice)
def _dedupe_sources(sources: list[dict]) -> list[dict]:
    """Collapse duplicate citations across multiple tool calls."""
    seen: dict[tuple, dict] = {} #a dict to keep track of chunk
    for s in sources:
        key = (s.get("course"), s.get("source"), s.get("chunk_index")) # a unique fingerprint for this exact chunk of text
        existing = seen.get(key)
        if existing is None or (s.get("score") or 0) > (existing.get("score") or 0):
            seen[key] = s
    return list(seen.values())


service = RagbotService() #create singletone instance of the service ussed by the web server/


if __name__ == "__main__":
    service.export_graph()
