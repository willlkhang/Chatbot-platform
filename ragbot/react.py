import os
import ollama
from dotenv import load_dotenv
# from langchain_tavily import TavilySearch
from langchain_ollama import ChatOllama
# from langchain_google_genai import ChatGoogleGenerativeAI


from tools.knowledge_tools import ICT283_questions#, Stack_overflow_questions

load_dotenv()

# LangChain and the Ollama Python client share this host (default: local Ollama).
OLLAMA_BASE_URL = (os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
_ollama_sdk = ollama.Client(host=OLLAMA_BASE_URL)


class ToolRegistry:
    def __init__(
        self,
        *,
        model: str | None = None,
        # tavily_max_results: int = 1,
        enable_web: bool = True,
        extra_tools: list | None = None,
    ) -> None:
        self._model = model or os.environ.get("OLLAMA_MODEL") or "qwen3.5:3b-instruct" #"granite4.1:8b-q3_k_m" #"granite4.1:3b"
            
        # self._tavily_max_results = tavily_max_results
        # self._enable_web = enable_web

        self._extra_tools = extra_tools or []

        #check if the mode exists, otherwise, pull
        self._model_exists()

    def _model_exists(self):
        #this method is used for chekcing if a LM exists, otherwise pull
        try:
            local_models = _ollama_sdk.list()
            model_names = [m["model"] for m in local_models["models"]]

            if self._model not in model_names and f"{self._model}:latest" not in model_names:
                print(f"Model '{self._model}' not found. Pulling now...")
                _ollama_sdk.pull(self._model)
                print("Pull complete!")
            else:
                print(f"Model '{self._model}' is already available.")
        except Exception as e:
            print(f"Could not verify or pull model: {e}")

    def build_tools(self):
        tool_list = []
        # if self._enable_web:
        #     tool_list.append(TavilySearch(max_results=self._tavily_max_results))

        tool_list.extend([ICT283_questions])

        tool_list.extend(self._extra_tools)

        return tool_list

    def build_llm(self):
        return ChatOllama(model=self._model, base_url=OLLAMA_BASE_URL)
        #return ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")

    def build_llm_with_tools(self):
        tools_local = self.build_tools()
        llm_local = self.build_llm()
        return tools_local, llm_local.bind_tools(tools_local)


_registry = ToolRegistry()
tools, llm_with_tools = _registry.build_llm_with_tools()
