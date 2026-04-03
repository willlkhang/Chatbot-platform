import os, sqlite3
from operator import itemgetter
from dotenv import load_dotenv

import asyncio

#LangChain / LangGraph imports
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from graph import workflow

load_dotenv()


conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)

memory = SqliteSaver(conn)

app = workflow.compile(checkpointer=memory)

async def run_request(query):
    config = {"configurable": {"thread_id": "convo_1"}}

    res = app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    raw = res['messages'][-1].content
    print(f"\nAgent: {raw}")

    if isinstance(raw, list):
        text = ""
        for block in raw:
            if isinstance(block, dict) and block.get('type') == 'text':
                text += block.get('text', '')
    else:
        text = raw

    return text

if __name__ == "__main__":
    query = "What is my name?"
    asyncio.run(run_request(query))