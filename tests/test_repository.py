import unittest
from datetime import datetime
from unittest.mock import patch

from gameweaver.repository import ProjectRepository, mysql_config


class FakeCursor:
    lastrowid = 7
    rowcount = 1

    def __init__(self, connector):
        self.connector = connector

    def execute(self, query, params=None):
        self.query = query
        self.connector.queries.append((query, params))

    def fetchone(self):
        if "information_schema.columns" in self.query:
            return {"count": 0}
        if "MAX(version)" in self.query:
            return {"version": 1}
        return self.connector.detail

    def fetchall(self):
        return [{"id": 7, "project_name": "테스트", "revision_request": "균등하게", "created_at": datetime(2026, 1, 1)}]

    def close(self):
        pass


class FakeConnection:
    def __init__(self, connector):
        self.connector = connector

    def cursor(self, dictionary=False):
        return FakeCursor(self.connector)

    def commit(self):
        self.connector.commits += 1

    def rollback(self):
        self.connector.rollbacks += 1

    def close(self):
        pass


class FakeConnector:
    def __init__(self):
        self.queries, self.commits, self.rollbacks = [], 0, 0
        self.detail = {"id": 7, "project_key": "project-1", "project_name": "테스트", "version": 1, "status": "draft", "input_json": '{"project":{"name":"테스트"}}', "result_json": '{"tasks":[]}', "revision_request": "", "created_at": datetime(2026, 1, 1)}

    def connect(self, **config):
        self.config = config
        return FakeConnection(self)


class RepositoryTests(unittest.TestCase):
    def test_plan_round_trip_queries(self):
        connector = FakeConnector()
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        metadata = repository.save({"project": {"name": "테스트", "id": "project-1"}}, {"tasks": [], "revision_request": "균등하게"})
        saved = repository.get(metadata["plan_id"])
        listed = repository.list()
        self.assertEqual(7, metadata["plan_id"])
        self.assertEqual(1, metadata["version"])
        self.assertEqual("테스트", saved["input"]["project"]["name"])
        self.assertEqual("2026-01-01T00:00:00", listed[0]["created_at"])
        self.assertTrue(any("INSERT INTO plans" in query for query, _ in connector.queries))
        self.assertEqual(4, connector.commits)

    def test_confirm_versions_and_delete(self):
        connector = FakeConnector()
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        self.assertTrue(repository.confirm(7))
        self.assertEqual(1, repository.delete_project("project-1"))
        self.assertEqual("테스트", repository.versions("project-1")[0]["project_name"])

    def test_mysql_config_requires_credentials(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaisesRegex(RuntimeError, "MYSQL_USER"):
            mysql_config()


if __name__ == "__main__":
    unittest.main()
