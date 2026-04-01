from dotenv import load_dotenv
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph, END

from react import tools, llm_with_tools

load_dotenv()

SYSTEM_MSG = SystemMessage(content="You are a helpful assistant. " \
"Use search_assignment_docs for homework and Tavily for general web info.")


def run_agent_reasoning(state: MessagesState):
    response = llm_with_tools.invoke([SYSTEM_MSG] + state["messages"])
    return {"messages": [response]}

def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END
    return "tools"

tool_node = ToolNode(tools)