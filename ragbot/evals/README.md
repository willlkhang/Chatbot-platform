## Evaluating this LangGraph agent

This eval harness scores three aspects:

- **Retrieval quality**: does the local retriever return relevant chunks in top-\(k\)?
- **Answer quality**: does the final answer match expectations and avoid hallucinations?
- **Agent behavior**: does the agent call tools when it should, and avoid tools when it shouldn't?

### Files

- `cases.jsonl`: evaluation dataset (you create/extend this)
- `run_eval.py`: runs the dataset and writes `results.json`

### Run

From repo root:

```bash
uv run ragbot/evals/run_eval.py
```

### Case schema (`cases.jsonl`)

Each line is a JSON object:

- `id` (string): unique id
- `query` (string): user question
- `requires_docs` (bool): whether the agent should use assignment docs
- `expected_tool` (string|null): usually `"search_assignment_docs"` when `requires_docs=true`
- `retrieval_must_include` (array[string]): keywords expected to appear in retrieved context (retrieval quality)
- `answer_must_include` (array[string]): keywords expected in final answer (answer quality)
- `answer_must_not_include` (array[string]): phrases that must not appear

