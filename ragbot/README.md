Quick Start: 

uv init

uv sync

uv run controller.py

Local models (recommended):
- **LLM**: set `OLLAMA_MODEL` (default: `qwen2.5:7b`)
- **Embeddings**: set `OLLAMA_EMBED_MODEL` (default: `nomic-embed-text`)
- **Long-term memory DB**: set `RAG_MEMORY_DB` (default: `./data/rag_memory.sqlite`)

ollama pull qwen2.5:7b
ollama pull nomic-embed-text