from langgraph.graph import START, MessagesState, StateGraph, END # this are node or state for node for langggraph

# tools for nodes for langgraph
from node import tool_node, should_continue, run_agent_reasoning
#this is basically just to load .env
#this is strongly important in the early state, especially for using langsmith
#to use langgraph, I need to provide API for langsmit to see if the system use the correct tool call.
from dotenv import load_dotenv

load_dotenv() #this basically load env file

#defines a class blueprin pieces the graph together
class WorkflowFactory:
    def __init__(self, *, state_type=MessagesState) -> None:
        self._state_type = state_type #saves the passed state types into a class instance variables.

    def build(self): #defines the method that actually pieces the graph together
        workflow = StateGraph(self._state_type) #this is where it starts
        workflow.add_node("agent", run_agent_reasoning) # add agent node
        workflow.add_node("tools", tool_node) #add tools node

        workflow.add_edge(START, "agent") #creates a mandatory pathway from the built-in START node directly to our "agent" node
        workflow.add_conditional_edges("agent", should_continue, { #creates a branching pathway leaving the "agent" node, decided by the 'should_continue' function
            END:END, # If 'should_continue' returns END, route to the built-in END node (stopping the graph)
            "tools":"tools" # If 'should_continue' returns "tools", route to the "tools" node
        })
        workflow.add_edge("tools", "agent") #creates a mandatory pathway from the "tools" node back to the "agent" node, forming a loop
        return workflow #returns the fully constructed, uncompiled graph object


workflow = WorkflowFactory().build() #build graph