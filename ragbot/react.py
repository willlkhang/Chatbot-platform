import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_ollama import ChatOllama

from repository import retriever_ICT283, retriever_SOF

load_dotenv()

@tool
def ICT283_questions(query: str) -> str:
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
    docs = retriever_ICT283.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

@tool
def Stack_overflow_questions(query: str) -> str:
    """Search assignments questions.
        Look for keywords:
        - Tree
        - Graph
        - DSA
        - Programming language
        - Interface, Abstract Classes
        - C, C++, Java, Python, C#, JavaScript, TypeScript
    """
    docs = retriever_SOF.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

class ToolRegistry:
    def __init__(
        self,
        *,
        retriever_instance=None,
        model: str | None = None,
        tavily_max_results: int = 1,
    ) -> None:
        self._retriever = retriever_instance or retriever
        self._model = model or os.environ.get("OLLAMA_MODEL") or "qwen2.5:7b"
        self._tavily_max_results = tavily_max_results

    def build_tools(self):
        # search_assignment_docs uses module-level retriever by default; allow override.
        if self._retriever is not retriever:
            def _search(query: str) -> str:
                docs = self._retriever.invoke(query)
                return "\n\n".join(doc.page_content for doc in docs)

            override_search_assignment_docs = tool(_search)
            override_search_assignment_docs.name = "ICT283_questions"
            override_search_assignment_docs.description = ICT283_questions.description
            assignment_tool = override_search_assignment_docs
        else:
            assignment_tool = ICT283_questions

        return [TavilySearch(max_results=self._tavily_max_results), assignment_tool]

    def build_llm(self):
        return ChatOllama(model=self._model)

    def build_llm_with_tools(self):
        tools_local = self.build_tools()
        llm_local = self.build_llm()
        return tools_local, llm_local.bind_tools(tools_local)


_registry = ToolRegistry()
tools, llm_with_tools = _registry.build_llm_with_tools()
