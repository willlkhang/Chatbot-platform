import os, sqlite3
from operator import itemgetter
from dotenv import load_dotenv

import asyncio

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from graph import workflow

load_dotenv()


class RagbotService:
    def __init__(self, *, sqlite_path: str = "./data/checkpoints.sqlite", thread_id: str = "convo_5") -> None:
        self._sqlite_path = sqlite_path
        self._thread_id = thread_id

        self._conn = sqlite3.connect(self._sqlite_path, check_same_thread=False)
        self._memory = SqliteSaver(self._conn)
        self._app = workflow.compile(checkpointer=self._memory)

    def invoke(self, query: str, *, thread_id: str | None = None) -> str:
        config = {"configurable": {"thread_id": thread_id or self._thread_id}}
        res = self._app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
        raw = res["messages"][-1].content

        if isinstance(raw, list):
            text = ""
            for block in raw:
                if isinstance(block, dict) and block.get("type") == "text":
                    text += block.get("text", "")
            return text

        return raw
    
    def get_graph(self):
        self._app.get_graph().draw_mermaid_png(output_file_path="flow.png")                                                       


_service = RagbotService()

async def run_request(query: str, *, thread_id: str | None = None):
    return _service.invoke(query, thread_id=thread_id)

if __name__ == "__main__":
    # query = "What is my name?"
    # asyncio.run(run_request(query))
    _service.get_graph()