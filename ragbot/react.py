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

class ToolRegistry:
    def __init__(
        self,
        *,
        retriever_instance=None,
        model: str = "gemini-3.1-flash-lite-preview",
        tavily_max_results: int = 1,
    ) -> None:
        self._retriever = retriever_instance or retriever
        self._model = model
        self._tavily_max_results = tavily_max_results

    def build_tools(self):
        # search_assignment_docs uses module-level retriever by default; allow override.
        if self._retriever is not retriever:
            def _search(query: str) -> str:
                docs = self._retriever.invoke(query)
                return "\n\n".join(doc.page_content for doc in docs)

            override_search_assignment_docs = tool(_search)
            override_search_assignment_docs.name = "search_assignment_docs"
            override_search_assignment_docs.description = search_assignment_docs.description
            assignment_tool = override_search_assignment_docs
        else:
            assignment_tool = search_assignment_docs

        return [TavilySearch(max_results=self._tavily_max_results), assignment_tool]

    def build_llm(self):
        return ChatGoogleGenerativeAI(model=self._model)

    def build_llm_with_tools(self):
        tools_local = self.build_tools()
        llm_local = self.build_llm()
        return tools_local, llm_local.bind_tools(tools_local)


_registry = ToolRegistry()
tools, llm_with_tools = _registry.build_llm_with_tools()
