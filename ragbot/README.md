Quick Start: 

uv init

uv sync

uv run controller.py

Local models (recommended):
- **LLM**: set `OLLAMA_MODEL` (default: `qwen2.5:7b`)
- **Embeddings**: set `OLLAMA_EMBED_MODEL` (default: `nomic-embed-text`)
- **Long-term memory DB**: set `RAG_MEMORY_DB` (default: `./data/rag_memory.sqlite`)

Example:

```bash
export OLLAMA_MODEL="qwen2.5:7b"
export OLLAMA_EMBED_MODEL="nomic-embed-text"
export RAG_MEMORY_DB="./data/rag_memory.sqlite"
uv run ingestion.py
uv run controller.py
```