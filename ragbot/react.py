import os  # env vars for model/base url config
import logging  # logger so we can see model availability/pull status
import ollama  # official Ollama SDK (used for listing/pulling models)
from dotenv import load_dotenv  # load .env so local development is easier
from langchain_ollama import ChatOllama  # LangChain wrapper around Ollama chat endpoint

from tools.knowledge_tools import (  # the tools the agent is allowed to call
    ICT283_questions,
    ICT167_questions,
    ICT159_questions,
)

load_dotenv()  # loads environment variables from .env (recommended for local)

logger = logging.getLogger("ragbot.react")  # per-module logger (shows in controller logging config)

OLLAMA_BASE_URL = (os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip(
    "/"
)  # keep base url stable (no trailing slash surprises)
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL") or "qwen3.5:latest"  # fallback model for dev

_ollama_sdk = ollama.Client(host=OLLAMA_BASE_URL)  # low-level SDK client (model list/pull)


class ToolRegistry:
    def __init__(
        self,
        *,
        model: str | None = None,
        extra_tools: list | None = None,
        auto_pull: bool | None = None,
    ) -> None:
        self._model = model or DEFAULT_OLLAMA_MODEL  # select model (env > default)
        self._extra_tools = extra_tools or []  # optional tools for experiments/extensions
        if auto_pull is None:  # decide whether to auto-download missing model
            auto_pull = os.environ.get("RAGBOT_AUTO_PULL_MODEL", "true").lower() in (
                "1",
                "true",
                "yes",
            )
        if auto_pull:  # helpful for new machines/containers where model isn't pulled yet
            self._ensure_model()  # best effort; failures only warn

    def _ensure_model(self) -> None:
        # this function tries to ensure the configured model exists locally in Ollama
        try:  # model listing/pulling can fail if Ollama isn't running; do not crash the app
            local_models = _ollama_sdk.list()  # ask Ollama for local models
            model_names = [m["model"] for m in local_models["models"]]  # flatten to a list of names

            if (
                self._model not in model_names
                and f"{self._model}:latest" not in model_names
            ):
                logger.info("Model '%s' not found locally. Pulling...", self._model)  # status log
                _ollama_sdk.pull(self._model)  # download model from registry (can take time)
                logger.info("Pull complete: %s", self._model)  # success log
            else:
                logger.info("Ollama model '%s' is available.", self._model)  # already installed
        except Exception as e:  # never block app startup on this
            logger.warning("Could not verify or pull Ollama model: %s", e)  # warn only

    def build_tools(self):
        # base tools are our course retrievers; extra tools can be injected for experiments
        return [  # order doesn't matter much; it's mainly for readability
            ICT283_questions,  # retrieval tool for ICT283 course material
            ICT167_questions,  # retrieval tool for ICT167 course material
            ICT159_questions,  # retrieval tool for ICT159 course material
            *self._extra_tools,  # add any additional tools if configured
        ]

    def build_llm(self):
        # ChatOllama talks to the local/remote Ollama server specified by OLLAMA_BASE_URL
        return ChatOllama(model=self._model, base_url=OLLAMA_BASE_URL)  # configured chat model

    def build_llm_with_tools(self):
        # this returns both the tools list + a tool-bound LLM (LangChain will do tool calling)
        tools_local = self.build_tools()  # build tool list
        llm_local = self.build_llm()  # build base LLM client
        return tools_local, llm_local.bind_tools(tools_local)  # LLM can now emit tool_calls


_registry = ToolRegistry()  # singleton registry used by node.py/graph.py
tools, llm_with_tools = _registry.build_llm_with_tools()  # exported for AgentNodes
