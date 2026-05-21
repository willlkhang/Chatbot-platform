Quick Start: 

uv init

uv sync

uv run controller.py

Local models (recommended):
- **LLM**: set `OLLAMA_MODEL` (default: `qwen2.5:7b`)
- **Embeddings**: set `OLLAMA_EMBED_MODEL` (default: `nomic-embed-text`)
- **Ollama API**: set `OLLAMA_BASE_URL` (local default `http://127.0.0.1:11434`; Docker Compose uses `http://host.docker.internal:11434` so the container reaches Ollama on your machine)
- **Long-term memory DB**: set `RAG_MEMORY_DB` (default: `./data/rag_memory.sqlite`)

ollama pull qwen3.5:7b
ollama pull nomic-embed-text

### Docker (project root)

After starting Ollama on the host, from the repo root: `docker compose --env-file .env.dev up --build`. Ragbot data lives in the `ragbot_data` volume under `/app/data` in the container.