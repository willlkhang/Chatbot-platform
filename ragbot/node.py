from dotenv import load_dotenv
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph, END

from react import tools, llm_with_tools

load_dotenv()

SYSTEM_MSG = SystemMessage(content="You are a helpful assistant. " \
"Use search_assignment_docs for homework and Tavily for general web info.")

class AgentNodes:
    def __init__(self, *, system_message: SystemMessage | None = None, llm_with_tools_instance=None, tools_list=None) -> None:
        self.system_message = system_message or SYSTEM_MSG
        self.llm_with_tools = llm_with_tools_instance or llm_with_tools
        self.tools = tools_list or tools
        self.tool_node = ToolNode(self.tools)

    def run_agent_reasoning(self, state: MessagesState):
        response = self.llm_with_tools.invoke([self.system_message] + state["messages"])
        return {"messages": [response]}

    def should_continue(self, state: MessagesState):
        last_message = state["messages"][-1]
        if not last_message.tool_calls:
            return END
        return "tools"

def run_agent_reasoning(state: MessagesState):
    return _nodes.run_agent_reasoning(state)

def should_continue(state: MessagesState):
    return _nodes.should_continue(state)

_nodes = AgentNodes()

tool_node = _nodes.tool_node