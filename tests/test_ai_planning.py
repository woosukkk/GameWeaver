import unittest
from unittest.mock import patch

from gameweaver import create_plan
from tests.test_planner import SAMPLE


class FakeAgent:
    model = "test-model"

    def __init__(self):
        self.calls = []

    def plan(self, project, members, harness, revision_request="", validation_errors=None):
        self.calls.append(validation_errors)
        if len(self.calls) == 1:
            return {"summary": "첫 시도", "core_loop": ["전투"], "tasks": [{"name": "Prototype", "category": "Gameplay", "required_skills": {"Unity": 3}, "estimated_hours": 8, "dependencies": [], "mandatory": True}]}
        return {"summary": "검증을 반영한 계획", "core_loop": ["전투", "성장"], "tasks": [
            {"name": "Core Combat", "category": "Gameplay", "required_skills": {"Programming": 3}, "estimated_hours": 8, "dependencies": [], "mandatory": True},
            {"name": "Boss Battle", "category": "UI", "required_skills": {"UI": 3}, "estimated_hours": 8, "dependencies": ["Core Combat"], "mandatory": True}
        ]}


class AIPlanningTests(unittest.TestCase):
    def test_agent_retries_with_validator_errors(self):
        agent = FakeAgent()
        payload = {**SAMPLE, "project": {**SAMPLE["project"], "use_ai": True}}
        result = create_plan(payload, agent=agent)
        self.assertEqual(2, len(agent.calls))
        self.assertIn("필수 기능이 누락", agent.calls[1][0])
        self.assertTrue(result["validation"]["valid"])
        self.assertTrue(result["ai"]["used"])
        self.assertEqual("검증을 반영한 계획", result["project_analysis"]["summary"])

    def test_missing_key_uses_rule_engine(self):
        payload = {**SAMPLE, "project": {**SAMPLE["project"], "use_ai": True}}
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
            result = create_plan(payload)
        self.assertFalse(result["ai"]["used"])
        self.assertIn("OPENAI_API_KEY", result["ai"]["fallback_reason"])


if __name__ == "__main__":
    unittest.main()
