from dotenv import load_dotenv
from langgraph.graph import MessagesState, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage

from react import tools, llm_with_tools
from prompts.system_prompts import system_prompt

load_dotenv()

SYSTEM_MSG = SystemMessage(content=system_prompt)


class AgentNodes:
    def __init__(
        self,
        *,
        system_message: SystemMessage | None = None,
        llm_with_tools_instance=None,
        tools_list=None,
    ) -> None:
        self.system_message = system_message or SYSTEM_MSG
        self.llm_with_tools = llm_with_tools_instance or llm_with_tools
        self.tools = tools_list or tools
        self.tool_node = ToolNode(self.tools)

    def run_agent_reasoning(self, state: MessagesState):
        response = self.llm_with_tools.invoke([self.system_message] + state["messages"])
        return {"messages": [response]}

    def should_continue(self, state: MessagesState) -> str:
        if not state["messages"][-1].tool_calls:
            return END
        return "tools"


_nodes = AgentNodes()
tool_node = _nodes.tool_node


def run_agent_reasoning(state: MessagesState):
    return _nodes.run_agent_reasoning(state)


def should_continue(state: MessagesState):
    return _nodes.should_continue(state)
