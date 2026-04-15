export OLLAMA_MODEL="qwen2.5:7b"
export OLLAMA_EMBED_MODEL="nomic-embed-text"
export RAG_MEMORY_DB="./data/rag_memory.sqlite"
uv run ingestion.py
uv run controller.py