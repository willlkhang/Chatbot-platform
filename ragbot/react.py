import os
import logging

from dotenv import load_dotenv
from langchain_community.chat_models import ChatLlamaCpp

from tools.knowledge_tools import ICT283_questions, ICT167_questions, ICT159_questions

load_dotenv()

logger = logging.getLogger("ragbot.react")

LLAMA_MODEL_PATH = (
    os.environ.get("LLAMA_MODEL_PATH")
    or "./models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
)
LLAMA_N_GPU_LAYERS = int(os.environ.get("LLAMA_N_GPU_LAYERS") or "33")
LLAMA_N_CTX = int(os.environ.get("LLAMA_N_CTX") or "8192")
LLAMA_N_BATCH = int(os.environ.get("LLAMA_N_BATCH") or "512")
LLAMA_TEMPERATURE = float(os.environ.get("LLAMA_TEMPERATURE") or "0.1")


class ToolRegistry:
    def __init__(
        self,
        *,
        model_path: str | None = None,
        extra_tools: list | None = None,
    ) -> None:
        self._model_path = model_path or LLAMA_MODEL_PATH
        self._extra_tools = extra_tools or []
        if not os.path.isfile(self._model_path):
            logger.warning(
                "GGUF model not found at '%s'. "
                "Download it to that path before starting the server.",
                self._model_path,
            )

    def build_tools(self):
        return [
            ICT283_questions,
            ICT167_questions,
            ICT159_questions,
            *self._extra_tools,
        ]

    def build_llm(self):
        return ChatLlamaCpp(
            model_path=self._model_path,
            n_gpu_layers=LLAMA_N_GPU_LAYERS,
            n_ctx=LLAMA_N_CTX,
            n_batch=LLAMA_N_BATCH,
            temperature=LLAMA_TEMPERATURE,
            verbose=False,
        )

    def build_llm_with_tools(self):
        tools_local = self.build_tools()
        llm_local = self.build_llm()
        return tools_local, llm_local.bind_tools(tools_local)


_registry = ToolRegistry()
tools, llm_with_tools = _registry.build_llm_with_tools()
