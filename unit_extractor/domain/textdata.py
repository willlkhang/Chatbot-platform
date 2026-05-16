"""Small data container holding extracted text and basic metadata.

`TextData` stores the original file name, parent folder name, the text
content and a `metadata` dictionary that currently includes file
extension and full path. Only documentation/comments added; behavior
unchanged.
"""

from pathlib import Path


class TextData:

    def __init__(self,
                 path: str | Path,
                 text: str = None):

        path = Path(path)

        # filename without directories
        self.filename = path.name
        # immediate parent folder name
        self.file_folder = path.parent.name
        # extracted or loaded text content
        self.text = text
        # lightweight metadata dictionary; keep minimal for privacy
        self.metadata = {
            "extension": path.suffix.lstrip('.').lower(),
            "full_path": path.as_posix()  # comment out for privacy purposes
        }