uv init

uv sync

export OLLAMA_MODEL="qwen2.5:7b"
export OLLAMA_EMBED_MODEL="nomic-embed-text"

ollama pull qwen2.5:7b
ollama pull nomic-embed-text

uv run ingestion.py

uv run controller.py