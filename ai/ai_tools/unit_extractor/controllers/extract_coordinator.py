"""Coordinator that traverses paths and dispatches to extractors.

`UnitExtractor` performs a depth-first traversal of the provided path
and uses the `extractors` mapping to handle known file extensions.
Extractors are expected to yield `TextData` items which are collected
and returned as a list.
"""

from pathlib import Path
from extractors import ExtractorBase
from domain import TextData


class UnitExtractor:

    def __init__(self, **extractors):
        # mapping of file-extension -> extractor instance
        self.extractors = extractors

    def run(self, path: str | Path = None, skip_list: list = None):
        """Traverse `path` and extract text units using registered extractors.

        Args:
            path: starting filesystem path (file or directory).
            skip_list: optional list of paths/extensions to skip (currently unused).

        Returns:
            A list of `TextData` instances discovered by extractors.
        """

        root = Path(path)
        stack = []
        text_data_list = []

        # seed traversal stack with the top-level entries
        for p in root.iterdir():
            stack.append(p)

        # depth-first traversal
        while stack:
            current = stack.pop()

            # extracted items are passed back onto the stack as TextData
            if isinstance(current, TextData):
                text_data_list.append(current)
                continue

            cur_as_path = Path(current)

            if cur_as_path.is_dir():
                for p in cur_as_path.iterdir():
                    stack.append(p)
            else:
                ext = cur_as_path.suffix.lower()
                extractor: ExtractorBase = self.extractors.get(ext, None)

                if extractor:
                    # simple console feedback preserved from original code
                    print(cur_as_path)
                    print(f"processing {ext}...")
                    # extractor.extract yields TextData objects which we push
                    # onto the stack for collection
                    for txt_data in extractor.extract(cur_as_path):
                        stack.append(txt_data)

        return text_data_list