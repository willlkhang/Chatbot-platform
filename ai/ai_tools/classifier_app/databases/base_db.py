"""Abstract database API used by the classifier application.

Concrete database implementations should provide `get_resources` and
`add_resources` methods. The base class documents the minimal API used
by route handlers.
"""

from abc import abstractmethod


class BaseDB:

    @abstractmethod
    def get_resources(self, topic: str) -> list:
        """Return a list of resource strings matched by `topic`."""
        ...

    @abstractmethod
    def add_resources(self, topic: str, resource: str):
        """Persist a `resource` under `topic` in the backing store."""
        ...