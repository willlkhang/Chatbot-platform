from __future__ import annotations

import argparse  # argparse for CLI flags/args (so we can ingest from terminal)
import os  # used for file checks and building paths
import re  # regex used for text cleanup/normalization
import sys  # used for exit codes + stderr printing in CLI mode
from dotenv import load_dotenv  # load .env so local configs work without exporting vars

from langchain_core.documents import Document  # LangChain doc container (content + metadata)
from langchain_community.document_loaders import TextLoader  # loads .txt into Document objects
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splits docs into chunks

from repository import RagRepository  # our sqlite + embeddings repo where chunks are stored

load_dotenv()  # loads environment variables from .env (handy for ollama settings)


_NORMALIZE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\.{4,}"), "..."),  # collapse long dot leaders (e.g. "....") into "..."
    (re.compile(r"-{4,}"), "---"),  # collapse long hyphen separators into a standard marker
    (re.compile(r"_{4,}"), "___"),  # collapse long underscore separators into a standard marker
    (re.compile(r" {2,}"), " "),  # reduce repeated spaces (keeps text consistent for embeddings)
    (re.compile(r"\n{3,}"), "\n\n"),  # reduce huge blank gaps (keeps chunks denser)
    (re.compile(r"\t+"), " "),  # tabs often appear in copy/pasted docs; replace with spaces
]


def _normalize_text(text: str) -> str:
    # normalize repeated punctuation/whitespace so embeddings aren't polluted by formatting noise
    for pattern, replacement in _NORMALIZE_PATTERNS:  # run each cleanup rule in order
        text = pattern.sub(replacement, text)  # substitute occurrences of the pattern
    return text.strip()  # final trim (avoids leading/trailing whitespace-only chunks)


# course -> (source text file, target sqlite DB)
COURSE_PRESETS: dict[str, tuple[str, str]] = {
    "ICT159": ("./knowledge/ICT159_ALL_CONTENT.txt", "./data/ICT159_all.sqlite"),  # C foundations
    "ICT167": ("./knowledge/ICT167_ALL_CONTENT.txt", "./data/ICT167_all.sqlite"),  # Java foundations
    "ICT283": ("./knowledge/ICT283_ALL_CONTENT.txt", "./data/ICT283_all.sqlite"),  # software design/OOP
}


def _build_splitter(chunk_size_tokens: int, chunk_overlap_tokens: int) -> RecursiveCharacterTextSplitter:
    """Token-aware splitter that still respects structural separators.

    ``from_tiktoken_encoder`` keeps the recursive splitting behaviour (try
    paragraphs first, then sentences, then words) but measures chunks in
    tokens instead of characters.
    """
    # note: token-aware splitting is important because Ollama embedding models have context limits
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(  # tokenizer-based split sizing
        encoding_name="cl100k_base",  # common OpenAI-compatible tokenizer; good enough for chunk sizing
        chunk_size=chunk_size_tokens,  # target chunk size measured in tokens (not characters)
        chunk_overlap=chunk_overlap_tokens,  # overlap improves recall across boundary cuts
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],  # try "nice" boundaries first
    )  # if no separator matches, it will fall back down to character splitting


def ingest(
    source_path: str,
    db_path: str,
    *,
    course: str,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
    clear: bool = False,
) -> int:
    # quick sanity check so we fail early (instead of creating an empty DB)
    if not os.path.exists(source_path):  # verify input text exists
        raise FileNotFoundError(f"Source file not found: {source_path}")  # clear error message

    print(f"[ingest] Loading {source_path}")  # CLI feedback so users know what's happening
    document = TextLoader(source_path, encoding="UTF-8").load()  # load the entire text as Document(s)

    for d in document:  # normalize each loaded Document
        d.page_content = _normalize_text(d.page_content)  # strip formatting noise before chunking

    print(
        f"[ingest] Splitting course={course} "
        f"chunk_size={chunk_size}t chunk_overlap={chunk_overlap}t"
    )
    splitter = _build_splitter(chunk_size, chunk_overlap)  # create splitter configured in tokens
    chunks = splitter.split_documents(document)  # split into many smaller Document chunks
    print(f"[ingest] Created {len(chunks)} chunks")  # chunk count is a useful quick health signal

    source_name = os.path.basename(source_path)  # keep just file name for citations (not full path)
    enriched: list[Document] = []  # new list so we can attach consistent metadata per chunk
    for i, chunk in enumerate(chunks):  # walk each chunk and add our metadata fields
        meta = dict(chunk.metadata or {})  # clone metadata to avoid mutating the splitter output
        meta.update(  # standard fields used later for citations + debugging
            {
                "course": course,  # which course this chunk belongs to
                "source": source_name,  # where the content came from (file name)
                "chunk_index": i,  # stable index for that course+source ingestion run
            }
        )
        enriched.append(  # wrap as a new Document with updated metadata
            Document(page_content=chunk.page_content, metadata=meta)
        )

    repo = RagRepository(sqlite_path=db_path, course=course)  # repo instance points at the target DB
    if clear:  # optional "start fresh" mode (useful when you changed chunking settings)
        print(f"[ingest] Clearing existing rows in {db_path}")  # tell user we are deleting rows
        repo.clear()  # wipes both the doc table and vec index (if available)

    print(f"[ingest] Writing {len(enriched)} chunks to {db_path}")  # progress output
    inserted = repo.add_documents(enriched)  # embeds + inserts chunks (plus vec index when enabled)
    print(f"[ingest] Inserted {inserted} chunks into {db_path}")  # final status
    return inserted  # return count for scripting / CI usage


def _parse_args() -> argparse.Namespace:
    # dedicated CLI parser so ingestion can be done without running the web server
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
    args = _parse_args()  # parse CLI args (either presets or custom source+db)

    # custom ingestion mode (for any text file not in COURSE_PRESETS)
    if args.source or args.db:  # if user is trying to use custom paths, validate them
        if not (args.source and args.db and args.course):  # all three are required together
            print("--source, --db and --course must be provided together.", file=sys.stderr)
            return 2  # standard "bad usage" exit code
        ingest(  # run ingestion for a single custom corpus
            args.source,
            args.db,
            course=args.course,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            clear=args.clear,
        )
        return 0  # success

    # preset ingestion mode (use --all or pass 1+ course codes)
    targets: list[str] = list(COURSE_PRESETS) if args.all else list(args.courses)  # build target list
    if not targets:  # user provided nothing, so tell them how to run it
        print("No courses specified. Use --all or pass course codes (e.g. ICT159).", file=sys.stderr)
        print(f"Available presets: {', '.join(COURSE_PRESETS)}", file=sys.stderr)
        return 2  # bad usage

    unknown = [c for c in targets if c not in COURSE_PRESETS]  # validate course codes
    if unknown:  # fail early with a helpful list
        print(f"Unknown course(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"Available presets: {', '.join(COURSE_PRESETS)}", file=sys.stderr)
        return 2  # bad usage

    for course in targets:  # ingest each selected preset course
        source, db = COURSE_PRESETS[course]  # map course -> (source txt, sqlite target)
        print(f"\n=== Ingesting {course} ===")  # visual separator between courses
        ingest(  # run ingestion using shared chunking config
            source,
            db,
            course=course,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            clear=args.clear,
        )

    print("\n[ingest] Done.")  # final CLI message
    return 0  # success


if __name__ == "__main__":
    sys.exit(main())  # exit code is helpful for scripts/CI
