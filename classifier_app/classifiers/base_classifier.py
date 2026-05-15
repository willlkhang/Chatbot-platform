"""Abstract base for topic classifiers used by the app.

Defines the minimal interface a classifier implementation should
provide. Only documentation/comments are added; no interface changes
were made.
"""

from abc import abstractmethod


class BaseTopicClassifier:
    """Interface for topic classifiers.

    Concrete implementations should implement `classify` and
    `get_topics`. The signatures are intentionally left as-is to match
    downstream usage.
    """

    @abstractmethod
    def classify(text: str) -> str:
        """Classify a single text string and return a topic label.

        Note: keep the signature as present in the codebase to preserve
        compatibility with existing callers.
        """
        ...

    @abstractmethod
    def get_topics() -> list:
        """Return a list of topic labels supported by the classifier."""
        ...