import shutil
import zipfile
from pathlib import Path
from .base import ExtractorBase

"""
claude code
"""

class ZipExtractor(ExtractorBase):
    """
    Extracts a .zip archive into a sibling folder next to the source zip,
    and returns a flat list of every file that came out (recursively).
    """

    def _extract(self, path: str | Path = None) -> list:
        path = Path(path)
        out_dir = path.parent / f"{path.stem}_extracted"

        # Start clean: wipe any previous extraction from a prior run
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(path) as z:
            for member in z.infolist():
                # The ZIP spec requires forward slashes in filenames, but some
                # older Windows tools write backslashes anyway. Python's
                # extraction logic trips on those, so we normalise them here
                # before letting Python do its thing. Both filename fields
                # need to match or Python's internal integrity check fails.
                fixed = member.filename.replace('\\', '/')
                member.filename = fixed
                if hasattr(member, 'orig_filename'):
                    member.orig_filename = fixed

                z.extract(member, out_dir)

        # Walk the extracted tree; return only real files, not directories
        return [p for p in out_dir.rglob('*') if p.is_file()]