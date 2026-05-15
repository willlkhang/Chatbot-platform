"""Abstract preprocessor interface for text normalization."""

from abc import abstractmethod


class BasePreprocessor:

    @abstractmethod
    def preprocess(text: str) -> str:
        """Return a normalized/cleaned version of `text`."""
        ...