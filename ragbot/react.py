from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

from repository import retriever

load_dotenv()

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

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")

llm_with_tools = llm.bind_tools(tools)