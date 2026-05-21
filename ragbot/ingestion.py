from __future__ import annotations

import argparse
import os
import re
import sys
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from repository import RagRepository

load_dotenv()


_NORMALIZE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\.{4,}"), "..."),
    (re.compile(r"-{4,}"), "---"),
    (re.compile(r"_{4,}"), "___"),
    (re.compile(r" {2,}"), " "),
    (re.compile(r"\n{3,}"), "\n\n"),
    (re.compile(r"\t+"), " "),
]


def _normalize_text(text: str) -> str:
    for pattern, replacement in _NORMALIZE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text.strip()


# course -> (source text file, target sqlite DB)
COURSE_PRESETS: dict[str, tuple[str, str]] = {
    "ICT159": ("./knowledge/ICT159_ALL_CONTENT.txt", "./data/ICT159_all.sqlite"),
    "ICT167": ("./knowledge/ICT167_ALL_CONTENT.txt", "./data/ICT167_all.sqlite"),
    "ICT283": ("./knowledge/ICT283_ALL_CONTENT.txt", "./data/ICT283_all.sqlite"),
}


def _build_splitter(chunk_size_tokens: int, chunk_overlap_tokens: int) -> RecursiveCharacterTextSplitter:
    """Token-aware splitter that still respects structural separators.

    ``from_tiktoken_encoder`` keeps the recursive splitting behaviour (try
    paragraphs first, then sentences, then words) but measures chunks in
    tokens instead of characters.
    """
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size_tokens,
        chunk_overlap=chunk_overlap_tokens,
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
    )


def ingest(
    source_path: str,
    db_path: str,
    *,
    course: str,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
    clear: bool = False,
) -> int:
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")

    print(f"[ingest] Loading {source_path}")
    document = TextLoader(source_path, encoding="UTF-8").load()

    for d in document:
        d.page_content = _normalize_text(d.page_content)

    print(
        f"[ingest] Splitting course={course} "
        f"chunk_size={chunk_size}t chunk_overlap={chunk_overlap}t"
    )
    splitter = _build_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_documents(document)
    print(f"[ingest] Created {len(chunks)} chunks")

    source_name = os.path.basename(source_path)
    enriched: list[Document] = []
    for i, chunk in enumerate(chunks):
        meta = dict(chunk.metadata or {})
        meta.update(
            {
                "course": course,
                "source": source_name,
                "chunk_index": i,
            }
        )
        enriched.append(Document(page_content=chunk.page_content, metadata=meta))

    repo = RagRepository(sqlite_path=db_path, course=course)
    if clear:
        print(f"[ingest] Clearing existing rows in {db_path}")
        repo.clear()

    print(f"[ingest] Writing {len(enriched)} chunks to {db_path}")
    inserted = repo.add_documents(enriched)
    print(f"[ingest] Inserted {inserted} chunks into {db_path}")
    return inserted


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest course content into SQLite vector stores.")
    parser.add_argument(
        "courses",
        nargs="*",
        help=f"One or more preset course codes. Available: {', '.join(COURSE_PRESETS)}",
    )
    parser.add_argument("--all", action="store_true", help="Ingest every preset course.")
    parser.add_argument("--source", help="Path to a custom source text file (use with --db).")
    parser.add_argument("--db", help="Path to the target SQLite DB (use with --source).")
    parser.add_argument("--course", help="Course label for custom corpora (use with --source).")
    parser.add_argument("--chunk-size", type=int, default=400, help="Chunk size in tokens.")
    parser.add_argument("--chunk-overlap", type=int, default=60, help="Chunk overlap in tokens.")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all existing rows before inserting the new ones.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if args.source or args.db:
        if not (args.source and args.db and args.course):
            print(
                "--source, --db and --course must be provided together.",
                file=sys.stderr,
            )
            return 2
        ingest(
            args.source,
            args.db,
            course=args.course,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            clear=args.clear,
        )
        return 0

    targets: list[str] = list(COURSE_PRESETS) if args.all else list(args.courses)
    if not targets:
        print("No courses specified. Use --all or pass course codes (e.g. ICT159).", file=sys.stderr)
        print(f"Available presets: {', '.join(COURSE_PRESETS)}", file=sys.stderr)
        return 2

    unknown = [c for c in targets if c not in COURSE_PRESETS]
    if unknown:
        print(f"Unknown course(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"Available presets: {', '.join(COURSE_PRESETS)}", file=sys.stderr)
        return 2

    for course in targets:
        source, db = COURSE_PRESETS[course]
        print(f"\n=== Ingesting {course} ===")
        ingest(
            source,
            db,
            course=course,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            clear=args.clear,
        )

    print("\n[ingest] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
