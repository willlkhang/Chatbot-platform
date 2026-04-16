from langgraph.graph import START, MessagesState, StateGraph, END

from node import tool_node, should_continue, run_agent_reasoning
from dotenv import load_dotenv

load_dotenv()

class WorkflowFactory:
    def __init__(self, *, state_type=MessagesState) -> None:
        self._state_type = state_type

    def build(self):
        workflow = StateGraph(self._state_type)
        workflow.add_node("agent", run_agent_reasoning)
        workflow.add_node("tools", tool_node)

        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", should_continue, {
            END:END,
            "tools":"tools"
        })
        workflow.add_edge("tools", "agent")
        return workflow


workflow = WorkflowFactory().build()