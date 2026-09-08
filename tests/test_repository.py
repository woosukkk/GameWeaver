import tempfile
import unittest
from pathlib import Path

from gameweaver.repository import ProjectRepository


class RepositoryTests(unittest.TestCase):
    def test_plan_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = ProjectRepository(Path(directory) / "plans.db")
            input_data = {"project": {"name": "테스트"}, "members": []}
            result = {"tasks": [], "revision_request": "균등하게"}
            plan_id = repository.save(input_data, result)
            saved = repository.get(plan_id)
            self.assertEqual(input_data, saved["input"])
            self.assertEqual(result, saved["result"])
            self.assertEqual("테스트", repository.list()[0]["project_name"])


if __name__ == "__main__":
    unittest.main()
