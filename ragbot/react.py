from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

load_dotenv()

@tool
def triple(num: float) -> float:
    """x3"""
    return float(num)*3

tools = [TavilySearch(max_results=1), triple]
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview").bind_tools(tools)