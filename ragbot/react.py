import os
import logging
import ollama
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from tools.knowledge_tools import ICT283_questions, ICT167_questions, ICT159_questions

load_dotenv()

logger = logging.getLogger("ragbot.react")

OLLAMA_BASE_URL = (os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL") or "llama3:latest"

_ollama_sdk = ollama.Client(host=OLLAMA_BASE_URL)


class ToolRegistry:
    def __init__(
        self,
        *,
        model: str | None = None,
        extra_tools: list | None = None,
        auto_pull: bool | None = None,
    ) -> None:
        self._model = model or DEFAULT_OLLAMA_MODEL
        self._extra_tools = extra_tools or []
        if auto_pull is None:
            auto_pull = os.environ.get("RAGBOT_AUTO_PULL_MODEL", "true").lower() in (
                "1", "true", "yes",
            )
        if auto_pull:
            self._ensure_model()

    def _ensure_model(self) -> None:
        try:
            local_models = _ollama_sdk.list()
            model_names = [m["model"] for m in local_models["models"]]

            if (
                self._model not in model_names
                and f"{self._model}:latest" not in model_names
            ):
                logger.info("Model '%s' not found locally. Pulling...", self._model)
                _ollama_sdk.pull(self._model)
                logger.info("Pull complete: %s", self._model)
            else:
                logger.info("Ollama model '%s' is available.", self._model)
        except Exception as e:
            logger.warning("Could not verify or pull Ollama model: %s", e)

    def build_tools(self):
        return [
            ICT283_questions,
            ICT167_questions,
            ICT159_questions,
            *self._extra_tools,
        ]

    def build_llm(self):
        return ChatOllama(model=self._model, base_url=OLLAMA_BASE_URL)

    def build_llm_with_tools(self):
        tools_local = self.build_tools()
        llm_local = self.build_llm()
        return tools_local, llm_local.bind_tools(tools_local)


_registry = ToolRegistry()
tools, llm_with_tools = _registry.build_llm_with_tools()
