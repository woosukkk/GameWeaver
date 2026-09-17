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
        if "GET_LOCK" in self.query:
            return {"acquired": 1}
        if "SELECT role FROM project_members" in self.query:
            return {"role": "owner"}
        if "SELECT COUNT(*) FROM project_members" in self.query:
            return (1,)
        if "FROM project_invitations" in self.query:
            return {"project_key": "project-1", "role": "editor", "email": "member@example.com"}
        if "FROM project_retrospectives" in self.query:
            return self.connector.retrospective
        return self.connector.detail

    def fetchall(self):
        if "JOIN users u ON u.id=pm.user_id" in self.query:
            return [{"email": "owner@example.com", "role": "owner"}]
        if "FROM project_retrospectives" in self.query:
            return [{"plan_id": 7, "project_name": "이전 게임", "genre": "Roguelike", "engine": "Unity", "satisfaction": 4, "core_loop_achieved": 1, "summary": "전투 범위를 줄여 완성", "went_well": "", "problems": "", "recommendations": "", "text_score": 1.0}]
        if "FROM task_outcomes" in self.query:
            if "WHERE plan_id" in self.query:
                return [{"task_id": "task_01", "actual_hours": 15, "completed": 1, "rework_hours": 2, "blockers": '["asset"]', "playtest_issues": 1}]
            return [
                {"genre": "Roguelike", "engine": "Unity", "task_name": "Combat", "estimated_hours": 10, "actual_hours": 15},
                {"genre": "Roguelike", "engine": "Unity", "task_name": "Combat", "estimated_hours": 10, "actual_hours": 20},
                {"genre": "Roguelike", "engine": "Unity", "task_name": "Combat", "estimated_hours": 10, "actual_hours": 10},
            ]
        if "FROM knowledge_documents" in self.query:
            return [{"id": 9, "document_type": "gdd", "title": "전투 기획", "source_url": "", "excerpt": "보스 전투", "text_score": 1.0}]
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
        self.detail = {"id": 7, "project_key": "project-1", "project_name": "테스트", "version": 1, "status": "draft", "input_json": '{"project":{"name":"테스트"}}', "result_json": '{"tasks":[],"validation":{"valid":true}}', "revision_request": "", "created_at": datetime(2026, 1, 1)}
        self.retrospective = {"satisfaction": 4, "core_loop_achieved": 1, "summary": "완료", "went_well": "", "problems": "", "recommendations": ""}

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
        self.assertTrue(any("JOIN project_members" in query for query, _ in connector.queries))

    def test_confirm_versions_and_delete(self):
        connector = FakeConnector()
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        self.assertTrue(repository.confirm(7))
        self.assertEqual(1, repository.delete_project("project-1"))
        self.assertEqual("테스트", repository.versions("project-1")[0]["project_name"])

    def test_outcomes_produce_median_calibration(self):
        connector = FakeConnector()
        connector.detail["status"] = "confirmed"
        connector.detail["input_json"] = '{"project":{"name":"테스트","genre":"Roguelike","engine":"Unity"}}'
        connector.detail["result_json"] = '{"tasks":[{"id":"task_01","name":"Combat","estimated_hours":10}]}'
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        saved = repository.save_outcomes(7, [{"task_id": "task_01", "actual_hours": 15, "rework_hours": 2, "playtest_issues": 1}])
        calibration = repository.calibrations()[0]
        self.assertEqual(1, saved)
        self.assertEqual(1.5, calibration["effort_factor"])
        self.assertEqual(3, calibration["sample_count"])

    def test_invalid_plan_cannot_be_confirmed(self):
        connector = FakeConnector()
        connector.detail["result_json"] = '{"validation":{"valid":false}}'
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        with self.assertRaisesRegex(ValueError, "검증을 통과"):
            repository.confirm(7)

    def test_feedback_round_trip_is_returned(self):
        connector = FakeConnector()
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        feedback = repository.feedback(7)
        self.assertEqual(15.0, feedback["outcomes"][0]["actual_hours"])
        self.assertEqual(["asset"], feedback["outcomes"][0]["blockers"])
        self.assertEqual("완료", feedback["retrospective"]["summary"])

    def test_owner_can_invite_and_member_can_accept(self):
        connector = FakeConnector()
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        token = repository.invite("project-1", "member@example.com", "editor", 1)
        project_key = repository.accept_invitation(token, 2)
        self.assertEqual("project-1", project_key)
        self.assertTrue(any("INSERT INTO project_invitations" in query for query, _ in connector.queries))
        self.assertTrue(any("INSERT INTO project_members" in query for query, _ in connector.queries))

    def test_project_members_are_listed(self):
        connector = FakeConnector()
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        self.assertEqual("owner", repository.members("project-1", 1)[0]["role"])

    def test_completed_retrospective_is_searchable(self):
        connector = FakeConnector()
        connector.detail["status"] = "confirmed"
        connector.detail["input_json"] = '{"project":{"name":"테스트","genre":"Roguelike","engine":"Unity"}}'
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        repository.save_retrospective(7, {"satisfaction": 4, "core_loop_achieved": True, "summary": "핵심 전투 완성"})
        cases = repository.similar_cases({"name": "새 게임", "genre": "Roguelike", "engine": "Unity", "mandatory_features": ["Combat"]})
        self.assertEqual("이전 게임", cases[0]["project_name"])
        self.assertTrue(any("MATCH(summary" in query for query, _ in connector.queries))

    def test_project_documents_are_saved_and_searchable(self):
        connector = FakeConnector()
        repository = ProjectRepository({"database": "gameweaver"}, connector)
        document_id = repository.save_document({"project_key": "project-1", "document_type": "gdd", "title": "전투 기획", "content": "보스 전투 단계"}, 1)
        documents = repository.search_documents({"id": "project-1", "name": "테스트", "genre": "Roguelike", "engine": "Unity"}, user_id=1)
        self.assertEqual(7, document_id)
        self.assertEqual("document-9", documents[0]["source_id"])
        self.assertTrue(any("INSERT INTO knowledge_documents" in query for query, _ in connector.queries))
        self.assertEqual(9, repository.list_documents("project-1", 1)[0]["id"])
        self.assertTrue(repository.delete_document(9, 1))

    def test_mysql_config_requires_credentials(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaisesRegex(RuntimeError, "MYSQL_USER"):
            mysql_config()


if __name__ == "__main__":
    unittest.main()
