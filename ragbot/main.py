from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState, StateGraph, END

from node import run_agent_reasoning, tool_node

#graph persistence LLM memory
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

AGENT_REASON="agent_reason"
ACT= "act"
LAST = -1

conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

def should_continue(state: MessagesState) -> str:
    if not state["messages"][LAST].tool_calls:
        return END
    return ACT

flow = StateGraph(MessagesState)

flow.add_node(AGENT_REASON, run_agent_reasoning)
flow.set_entry_point(AGENT_REASON)
flow.add_node(ACT, tool_node)

flow.add_conditional_edges(AGENT_REASON, should_continue, {
    END:END,
    ACT:ACT})

flow.add_edge(ACT, AGENT_REASON)