import unittest

from gameweaver.rag import _documents, retrieve


class RagEvaluationTests(unittest.TestCase):
    def test_curated_corpus_has_unique_attributed_documents(self):
        documents = _documents()
        ids = [item["source_id"] for item in documents]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item.get("citation") and item.get("excerpt") for item in documents))

    def test_representative_queries_retrieve_expected_evidence(self):
        cases = [
            ({"genre": "Puzzle", "engine": "Godot", "platform": "Web", "description": "undo hint difficulty"}, "genre-puzzle-"),
            ({"genre": "Action", "engine": "Unity", "platform": "Mobile", "description": "touch memory build"}, "platform-android-"),
            ({"genre": "RPG", "engine": "Unreal Engine", "platform": "PC", "description": "save inventory progression"}, "unreal-"),
            ({"genre": "Strategy", "engine": "Custom", "platform": "PC", "description": "campaign progression mission browser"}, "github-openra-"),
        ]
        for project, prefix in cases:
            project.update({"name": "Evaluation", "duration_weeks": 8, "mandatory_features": [], "constraints": []})
            with self.subTest(prefix=prefix):
                self.assertTrue(any(item["source_id"].startswith(prefix) for item in retrieve(project, 8)))


if __name__ == "__main__":
    unittest.main()
