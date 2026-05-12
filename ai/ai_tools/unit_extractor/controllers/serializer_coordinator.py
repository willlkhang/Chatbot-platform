"""Coordinator for running serializers over extracted text data.

This module provides a small `Serializer` coordinator class that accepts
one or more serializer callables and invokes them on a list of
`TextData` items. Changes are limited to adding explanatory comments and
docstrings; behavior is unchanged.
"""

from domain import TextData


class Serializer:
    """Run one or more (callable) serializers over extracted text items.

    Each serializer is expected to be a tuple of `(save_path, func)` where
    `func` is a callable accepting `(data_list, save_path)` and performing
    the actual serialization (writing to disk, formatting, etc.). The
    coordinator only calls these functions and does not modify data.
    """

    def __init__(self, *serializers):
        # store the provided serializer tuples for later execution
        self.serializers = serializers

    def run(self, data: list[TextData]):
        """Execute each serializer over `data`.

        Args:
            data: list of `TextData` domain objects to be serialized.
        """

        for save_path, serialize in self.serializers:
            # Informational log printed to stdout (keeps original behavior)
            print(f'serializing as {save_path}...')
            # Call the serializer callable with the data and target path
            serialize(data, save_path)
