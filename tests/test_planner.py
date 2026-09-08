import unittest

from gameweaver import create_plan, refine_plan
from gameweaver.planner import _validate


SAMPLE = {
    "project": {"name": "Dungeon Loop", "genre": "Roguelike", "engine": "Unity", "dimension": "2D", "duration_weeks": 4, "goal": "MVP", "mandatory_features": ["Boss Battle"], "description": "짧은 전투 중심 로그라이크"},
    "members": [
        {"id": "member_01", "name": "민수", "skills": {"Unity": 4, "Programming": 4, "AI": 2}, "preferred_roles": ["Gameplay Programmer"], "avoid_roles": ["UI"], "available_hours_per_week": 12, "learning_interests": ["Enemy AI"]},
        {"id": "member_02", "name": "지수", "skills": {"Unity": 3, "UI": 5, "Game Design": 4}, "preferred_roles": ["UI Designer"], "avoid_roles": [], "available_hours_per_week": 10, "learning_interests": ["Progression"]},
    ],
}


class PlannerTests(unittest.TestCase):
    def test_plan_builds_dynamic_harness_and_assigns_every_task(self):
        plan = create_plan(SAMPLE)
        self.assertIn("Roguelike Context", plan["harness"]["contexts"])
        self.assertEqual(len(plan["tasks"]), len(plan["assignments"]))
        self.assertTrue(plan["validation"]["valid"])
        self.assertIn("Boss Battle", {task["name"] for task in plan["tasks"]})

    def test_refinement_can_avoid_named_assignment(self):
        result = refine_plan({"input": SAMPLE, "request": "민수는 Enemy AI를 맡지 않게 해줘"})
        task = next(task for task in result["tasks"] if task["name"] == "Enemy AI")
        assignment = next(item for item in result["assignments"] if item["task_id"] == task["id"])
        self.assertNotEqual("member_01", assignment["member_id"])

    def test_rejects_team_outside_mvp_size(self):
        payload = {**SAMPLE, "members": [SAMPLE["members"][0]]}
        with self.assertRaisesRegex(ValueError, "2~6"):
            create_plan(payload)

    def test_extended_context_and_completed_feature_are_applied(self):
        payload = {**SAMPLE, "project": {**SAMPLE["project"], "platform": "Mobile", "content_scale": "소규모", "completed_features": ["Player Controller"], "constraints": ["무료 에셋만 사용"]}}
        plan = create_plan(payload)
        self.assertIn("Mobile Platform", plan["harness"]["contexts"])
        self.assertIn("무료 에셋만 사용", plan["harness"]["rules"])
        self.assertNotIn("Player Controller", {task["name"] for task in plan["tasks"]})

    def test_planning_does_not_mutate_input(self):
        payload = {"project": {**SAMPLE["project"]}, "members": [{**member} for member in SAMPLE["members"]]}
        create_plan(payload)
        self.assertNotIn("platform", payload["project"])

    def test_dependency_cycle_is_rejected(self):
        tasks = [
            {"id": "a", "name": "A", "mandatory": True, "dependencies": ["b"]},
            {"id": "b", "name": "B", "mandatory": True, "dependencies": ["a"]},
        ]
        assignments = [{"task_id": "a", "member_id": "member_01"}, {"task_id": "b", "member_id": "member_02"}]
        workload = [{"member_id": "member_01", "assigned_hours": 5, "available_hours": 10}, {"member_id": "member_02", "assigned_hours": 5, "available_hours": 10}]
        result = _validate(tasks, assignments, workload, SAMPLE["members"])
        self.assertFalse(result["valid"])
        self.assertIn("태스크 의존성이 순환합니다.", result["errors"])


if __name__ == "__main__":
    unittest.main()
