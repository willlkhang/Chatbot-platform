import os, sqlite3
from operator import itemgetter
from dotenv import load_dotenv

import asyncio

#LangChain / LangGraph imports
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode

from repository import retriever

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")


@tool
def search_assignment_docs(query: str) -> str:
    """Search assignments questions.
        Look for keywords:
        - Assignment 1
        - Assignment 2
        - Lab, tutorials
        - SOLID
        - ICT283
        - No marks, zero marks
        - Demostrate, demo, demostration
    """
    docs = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

tools = [TavilySearch(max_results=1), search_assignment_docs]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

def run_agent_reasoning(state: MessagesState):
    SYSTEM_MSG = SystemMessage(content="You are a helpful assistant. Use search_assignment_docs for homework and Tavily for general web info.")

    response = llm_with_tools.invoke([SYSTEM_MSG] + state["messages"])
    return {"messages": [response]}

def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END
    return "tools"


conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

workflow = StateGraph(MessagesState)
workflow.add_node("agent", run_agent_reasoning)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue) # Decide: Tools or End?
workflow.add_edge("tools", "agent") # Back to agent after using tool

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