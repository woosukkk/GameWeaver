import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gameweaver.migrations import migrate


class Cursor:
    def __init__(self, connector):
        self.connector = connector

    def execute(self, query, params=None):
        self.query = query
        if query.startswith("INSERT INTO schema_migrations"):
            self.connector.applied.add(params[0])
        self.connector.queries.append(query)

    def fetchall(self):
        return [(value,) for value in self.connector.applied]

    def close(self):
        pass


class Connection:
    def __init__(self, connector):
        self.connector = connector

    def cursor(self):
        return Cursor(self.connector)

    def commit(self):
        self.connector.commits += 1

    def rollback(self):
        pass

    def close(self):
        pass


class Connector:
    def __init__(self):
        self.applied, self.queries, self.commits = set(), [], 0

    def connect(self, **_):
        return Connection(self)


class MigrationTests(unittest.TestCase):
    def test_applies_each_sql_file_once(self):
        connector = Connector()
        with tempfile.TemporaryDirectory() as directory, patch("gameweaver.migrations.mysql_config", return_value={}):
            Path(directory, "001_first.sql").write_text("CREATE TABLE example(id INT);", encoding="utf-8")
            self.assertEqual(["001_first"], migrate(directory, connector))
            self.assertEqual([], migrate(directory, connector))
        self.assertEqual(1, sum(query.startswith("CREATE TABLE example") for query in connector.queries))


if __name__ == "__main__":
    unittest.main()
