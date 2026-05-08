import os
import ollama
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI


from tools.knowledge_tools import ICT283_questions, Stack_overflow_questions

load_dotenv()


class ToolRegistry:
    def __init__(
        self,
        *,
        model: str | None = None,
        tavily_max_results: int = 1,
        enable_web: bool = True,
        extra_tools: list | None = None,
    ) -> None:
        self._model = model or os.environ.get("OLLAMA_MODEL") or "granite4.1:3b"
            
        self._tavily_max_results = tavily_max_results
        self._enable_web = enable_web
        self._extra_tools = extra_tools or []

    def build_tools(self):
        tool_list = []
        if self._enable_web:
            tool_list.append(TavilySearch(max_results=self._tavily_max_results))

        tool_list.extend([ICT283_questions, Stack_overflow_questions])

        tool_list.extend(self._extra_tools)

        return tool_list

    def build_llm(self):
        return ChatOllama(model=self._model)
        #return ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")

    def build_llm_with_tools(self):
        tools_local = self.build_tools()
        llm_local = self.build_llm()
        return tools_local, llm_local.bind_tools(tools_local)


_registry = ToolRegistry()
tools, llm_with_tools = _registry.build_llm_with_tools()
