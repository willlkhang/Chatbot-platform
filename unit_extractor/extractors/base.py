"""Base extractor abstraction for the unit extractor pipeline.

`ExtractorBase` provides a small framework for extractors that yield
either `TextData` instances or file-like objects. It supports optional
`cleaners` (callables) that post-process `TextData` items.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from domain import TextData


class ExtractorBase(ABC):

    def __init__(self, *cleaners, **kwargs):
        # store optional keyword args and any cleaner callables
        self.kwargs = kwargs
        self.cleaners = cleaners

    def extract(self, path=None) -> list:
        """Run the concrete extractor and apply cleaners to TextData results.

        The concrete `_extract` implementation may yield or return a list
        containing `TextData` instances or other items; cleaners are only
        applied to `TextData` objects.
        """

        results = self._extract(path)

        items = []
        for item in results:
            if isinstance(item, TextData):
                items.append(self._apply_cleaners(item))
            else:
                items.append(item)

        return items

    @abstractmethod
    def _extract(self, path=None) -> list:
        """Implement in subclasses: extract text units from `path`."""
        ...

    def _apply_cleaners(self, text_data: TextData):
        # apply cleaner pipeline in order
        cleaned_text_data = text_data
        for cleaner in self.cleaners:
            cleaned_text_data = cleaner(cleaned_text_data)
        return cleaned_text_data


if __name__ == "__main__":
    print('testing')


