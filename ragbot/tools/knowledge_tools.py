from __future__ import annotations

import os
import logging

from langchain_core.tools import tool

from repository import (
    repo_ICT283,
    repo_ICT167,
    repo_ICT159,
    RagRepository,
    record_sources,
)
from reranker import reranker

logger = logging.getLogger("ragbot.tools")


RETRIEVAL_K = int(os.environ.get("RAGBOT_RETRIEVAL_K", "20"))
RERANK_TOP_K = int(os.environ.get("RAGBOT_RERANK_TOP_K", "3"))


def _retrieve(repo: RagRepository, query: str) -> str:
    """Run the retrieve -> rerank -> format pipeline for one course."""
    raw = repo.similarity_search(query, k=RETRIEVAL_K)
    if not raw:
        return "No relevant course material was found for that query."

    top = reranker.rerank(query, raw, top_k=RERANK_TOP_K)

    # Only the post-rerank top-K is surfaced as citations to the API caller.
    record_sources(top, course=getattr(repo, "_course", None))

    parts: list[str] = []
    for i, doc in enumerate(top, start=1):
        meta = doc.metadata or {}
        course = meta.get("course", "?")
        source = meta.get("source") or "unknown"
        score = meta.get("_rerank_score") or meta.get("_score") or 0.0
        header = f"[{i}] course={course} source={source} score={score:.3f}"
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


@tool
def ICT283_questions(query: str) -> str:
    """Retrieve relevant ICT283 course material.

    USE THIS TOOL whenever the user's question mentions any of:
      - ICT283
      - Software Design / Object-Oriented Design
      - SOLID principles (SRP, OCP, LSP, ISP, DIP)
      - Design patterns (Singleton, Factory, Observer, Strategy, etc.)
      - Inheritance, polymorphism, encapsulation, abstraction in C++/Java
      - Assignment 1, Assignment 2, Lab, tutorial (in ICT283 context)
      - Demonstration / demo of a program
      - "No marks" / "zero marks" policies

    The ``query`` should be a rewritten, self-contained search question.
    """
    return _retrieve(repo_ICT283, query)


@tool
def ICT167_questions(query: str) -> str:
    """Retrieve relevant ICT167 course material.

    USE THIS TOOL whenever the user's question mentions any of:
      - ICT167
      - Java fundamentals (classes, objects, methods)
      - Control flow, loops, conditionals (in ICT167 context)
      - Arrays, ArrayList, basic collections
      - Introductory OOP concepts
      - File I/O in Java
      - ICT167 lab, tutorial, assignment

    The ``query`` should be a rewritten, self-contained search question.
    """
    return _retrieve(repo_ICT167, query)


@tool
def ICT159_questions(query: str) -> str:
    """Retrieve relevant ICT159 course material.

    USE THIS TOOL whenever the user's question mentions any of:
      - ICT159
      - Foundations of Programming / introductory C
      - Modularity, functions, parameters, scope
      - Variables, data types, operators, expressions
      - Selection (if/else), iteration (for/while)
      - Arrays, structs, file I/O in C
      - ICT159 lab, tutorial, assignment

    The ``query`` should be a rewritten, self-contained search question.
    """
    return _retrieve(repo_ICT159, query)
