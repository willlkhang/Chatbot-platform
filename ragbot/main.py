import os, sqlite3
from operator import itemgetter
from dotenv import load_dotenv

import asyncio

# LangChain / LangGraph imports
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001",
                                          google_api_key=os.environ.get("GOOGLE_API_KEY"),
                                          output_dimensionality=1536)

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")

vectorstore = PineconeVectorStore(index_name=os.environ['INDEX_NAME'], embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

@tool
def search_assignment_docs(query: str) -> str:
    """Search assignment docs and SOLID principles. Use for assignment questions."""
    docs = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

tools = [TavilySearch(max_results=1), search_assignment_docs]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

def run_agent_reasoning(state: MessagesState):
    SYSTEM_MSG = SystemMessage(content="You are a helpful assistant. Use search_assignment_docs for homework and Tavily for general web info.")
    # Gemini sees the whole history + the system message
    response = llm_with_tools.invoke([SYSTEM_MSG] + state["messages"])
    return {"messages": [response]}

def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END
    return "tools"

# --- 4. BUILD THE GRAPH ---
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

workflow = StateGraph(MessagesState)
workflow.add_node("agent", run_agent_reasoning)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue) # Decide: Tools or End?
workflow.add_edge("tools", "agent") # Back to agent after using tool

app = workflow.compile(checkpointer=memory)

async def run_request():
    config = {"configurable": {"thread_id": "convo_1"}}
    
    # Try asking a question that requires memory
    query = "What happen if I don't use SOLID?"
    res = app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    print(f"\nAgent: {res['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(run_request())