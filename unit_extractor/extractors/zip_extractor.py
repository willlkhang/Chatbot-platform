"""Extractor for ZIP archives.

Extracts archive contents into a sibling directory and returns a flat
list of files found. The extractor normalises ZIP member filenames to
handle archives created by legacy tools that may use backslashes.
"""

import shutil
import zipfile
from pathlib import Path
from .base import ExtractorBase


class ZipExtractor(ExtractorBase):
    """Extract a ZIP archive and return the contained file paths."""

    def _extract(self, path: str | Path = None) -> list:
        path = Path(path)
        out_dir = path.parent / f"{path.stem}_extracted"

        # Start clean: wipe any previous extraction from a prior run
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(path) as z:
            for member in z.infolist():
                # Normalise path separators to forward slashes to avoid
                # platform-specific extraction issues.
                fixed = member.filename.replace('\\', '/')
                member.filename = fixed
                if hasattr(member, 'orig_filename'):
                    member.orig_filename = fixed

                z.extract(member, out_dir)

        # Walk the extracted tree; return only files
        return [p for p in out_dir.rglob('*') if p.is_file()]