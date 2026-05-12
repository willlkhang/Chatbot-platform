"""Extractor for plain text and common source code files."""

from .base import ExtractorBase
from domain import TextData
from pathlib import Path


class TextExtractor(ExtractorBase):

    def _extract_apply(self, path=None):
        """Read a file with a best-effort encoding fallback.

        Attempt `utf-8` first and fall back to `cp1252` to handle legacy
        Windows-encoded files.
        """
        try:
            return Path(path).read_text(encoding='utf-8')
        except Exception:
            return Path(path).read_text(encoding='cp1252')

    def _extract(self, path: str | Path = None) -> list[TextData]:
        """Return a single `TextData` instance for the file at `path`."""
        path = Path(path)
        content = self._extract_apply(path)

        return [TextData(path=path, text=content)]


if __name__ == "__main__":
    ...