"""Lightweight SQLite-backed resource store used by the classifier app.

This class implements a minimal `BaseDB` using a bundled SQLite
database file located in the package `data/resources.db`. Only small
explanatory comments and docstrings were added; no runtime behavior was
changed.
"""

import sqlite3
from pathlib import Path
from .base_db import BaseDB


class SQLiteDB(BaseDB):

    def __init__(self):
        # path to the packaged resources database file
        self.db_path = data_path = Path(__file__).parent / 'data' / 'resources.db'

        # Ensure the table exists by connecting and creating it if needed
        connection = sqlite3.connect(data_path)
        cursor = connection.cursor()

        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS resources (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                topic TEXT NOT NULL,
                                resource TEXT NOT NULL UNIQUE
                                )
                        """)

        connection.commit()

    def add_resources(self, topic: str, resource: str):
        """Insert a resource URL/text under the given topic.

        Args:
            topic: topic name used as the lookup key.
            resource: resource string (e.g., URL) to store.
        """

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("""
                        INSERT INTO resources (topic, resource)
                        VALUES(?, ?)
                        """, (topic, resource))

        connection.commit()
        connection.close()

    def get_resources(self, topic: str):
        """Return a list of resource strings that match `topic`.

        Returns only the `resource` field values.
        """

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
                        SELECT * FROM resources WHERE topic = ?
                        """, (topic,))

        rows = cursor.fetchall()

        # rows are (id, topic, resource) tuples; return the resource element
        return [resources[2] for resources in rows]