import asyncio
import json
import os
from dataclasses import dataclass

from handler import RagbotService
from repository import RagRepository


@dataclass
class Case:
    id: str
    query: str
    requires_docs: bool
    expected_tool: str | None
    retrieval_must_include: list[str]
    answer_must_include: list[str]
    answer_must_not_include: list[str]


def _load_cases(path: str) -> list[Case]:
    cases: list[Case] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            cases.append(
                Case(
                    id=obj["id"],
                    query=obj["query"],
                    requires_docs=bool(obj.get("requires_docs", False)),
                    expected_tool=obj.get("expected_tool"),
                    retrieval_must_include=list(obj.get("retrieval_must_include", [])),
                    answer_must_include=list(obj.get("answer_must_include", [])),
                    answer_must_not_include=list(obj.get("answer_must_not_include", [])),
                )
            )
    return cases


def _contains_all(text: str, phrases: list[str]) -> bool:
    t = text.lower()
    return all(p.lower() in t for p in phrases)


def _contains_any(text: str, phrases: list[str]) -> bool:
    t = text.lower()
    return any(p.lower() in t for p in phrases)


def score_retrieval(repo: RagRepository, case: Case, *, k: int = 3) -> dict:
    if not case.retrieval_must_include:
        return {"retrieval_pass": None, "retrieved_preview": ""}

    docs = repo.similarity_search(case.query, k=k)
    context = "\n\n".join(d.page_content for d in docs)
    return {
        "retrieval_pass": _contains_all(context, case.retrieval_must_include),
        "retrieved_preview": context[:800],
    }


def score_answer(answer: str, case: Case) -> dict:
    must_ok = _contains_all(answer, case.answer_must_include) if case.answer_must_include else True
    must_not_ok = not _contains_any(answer, case.answer_must_not_include) if case.answer_must_not_include else True
    return {
        "answer_pass": bool(must_ok and must_not_ok),
        "must_include_ok": bool(must_ok),
        "must_not_include_ok": bool(must_not_ok),
    }


def score_behavior(messages, case: Case) -> dict:
    tool_names: list[str] = []
    for m in messages:
        tc = getattr(m, "tool_calls", None)
        if not tc:
            continue
        for call in tc:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
            if name:
                tool_names.append(name)

    expected = case.expected_tool
    used_expected = expected in tool_names if expected else (len(tool_names) == 0)
    behavior_pass = used_expected if case.requires_docs else (expected is None and len(tool_names) == 0)


    if case.requires_docs and expected:
        behavior_pass = expected in tool_names

    return {
        "behavior_pass": bool(behavior_pass),
        "tools_called": tool_names,
    }


async def run():
    cases_path = os.path.join(os.path.dirname(__file__), "cases.jsonl")
    cases = _load_cases(cases_path)

    # Separate DBs:
    # - checkpoints: conversation state (handler uses ./data/checkpoints.sqlite)
    # - rag memory: long-term memory (repository uses rag_memory.sqlite by default)
    repo = RagRepository(sqlite_path=os.environ.get("RAG_MEMORY_DB") or "rag_memory.sqlite")
    service = RagbotService(sqlite_path=os.environ.get("CHECKPOINTS_DB") or "./data/checkpoints.sqlite", thread_id="eval_thread")

    results = []
    for case in cases:
        retrieval = score_retrieval(repo, case, k=3)
        raw_state = service.invoke_raw(case.query)
        messages = raw_state.get("messages", [])
        answer = service.invoke(case.query)

        behavior = score_behavior(messages, case)
        ans_score = score_answer(answer, case)

        results.append(
            {
                "id": case.id,
                "query": case.query,
                "retrieval": retrieval,
                "behavior": behavior,
                "answer": {"text_preview": answer[:800], **ans_score},
            }
        )

    out_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    def _rate(key: str) -> str:
        vals = [r[key] for r in (x["answer"] for x in results)]
        return ""

    answer_pass = sum(1 for r in results if r["answer"]["answer_pass"])
    behavior_pass = sum(1 for r in results if r["behavior"]["behavior_pass"])
    retrieval_scored = [r for r in results if r["retrieval"]["retrieval_pass"] is not None]
    retrieval_pass = sum(1 for r in retrieval_scored if r["retrieval"]["retrieval_pass"])

    print(f"cases={len(results)}")
    print(f"answer_pass_rate={answer_pass/len(results):.2%}")
    print(f"behavior_pass_rate={behavior_pass/len(results):.2%}")
    if retrieval_scored:
        print(f"retrieval_pass_rate={retrieval_pass/len(retrieval_scored):.2%} (scored={len(retrieval_scored)})")
    print(f"wrote={out_path}")


if __name__ == "__main__":
    asyncio.run(run())

