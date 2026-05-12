"""Plain-text serializer for `TextData` instances.

Writes a simple line-per-item representation to `save_path`. This
serializer is intentionally minimal and primarily useful for quick
inspection of extracted content.
"""

from domain import TextData
from pathlib import Path


def txt_serializer(data: list[TextData], save_path: str | Path = Path().cwd() / 'content.txt'):
    """Serialize `data` to a human-readable text file.

    Each line contains a compact representation of a `TextData` item.
    The function preserves the original simple behavior; only comments
    and a docstring were added.
    """

    # Build simple display lines. Note: `TextData` may not have `id` in
    # all implementations; fallback to `filename` to avoid attribute errors.
    lines = [f"{getattr(td, 'id', td.filename)} : {td.text}" for td in data]

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    ...