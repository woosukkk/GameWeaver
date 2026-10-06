from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WebUITests(unittest.TestCase):
    def test_planning_ui_assets_and_hidden_state_are_present(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "web" / "ui.css").read_text(encoding="utf-8")
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")

        self.assertIn('href="/ui.css"', html)
        self.assertIn('src="/app.js?v=2"', html)
        self.assertIn('class="planning-progress"', html)
        self.assertIn('class="result-heading"', html)
        self.assertIn('id="document-form"', html)
        self.assertIn('id="knowledge-references"', html)
        self.assertIn('class="advanced-fields"', html)
        self.assertIn('추가 설정', html)
        self.assertIn('class="member-extra"', js)
        for field in ("platform", "contentScale", "deadline", "references", "excluded", "completed", "assets", "constraints", "useAi"):
            self.assertIn(f'name="{field}"', html)
        self.assertRegex(css, r"\[hidden\]\s*\{\s*display:\s*none\s*!important;\s*\}")


if __name__ == "__main__":
    unittest.main()
