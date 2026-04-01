from langgraph.graph import START, MessagesState, StateGraph, END

from node import tool_node, should_continue, run_agent_reasoning
from dotenv import load_dotenv

load_dotenv()

workflow = StateGraph(MessagesState)
workflow.add_node("agent", run_agent_reasoning)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue) # Decide: Tools or End?
workflow.add_edge("tools", "agent") # Back to agent after using tool