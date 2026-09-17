"""Refresh public issue metadata used by RAG without copying issue bodies."""

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


REPOSITORIES = ("OpenRA/OpenRA", "OpenTTD/OpenTTD", "supertuxkart/stk-code")
OUTPUT = Path(__file__).parents[1] / "knowledge" / "documents" / "github-issues-live.json"


def collect(limit=20):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "GameWeaver-knowledge-refresh"}
    if token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    documents = []
    for repository in REPOSITORIES:
        url = f"https://api.github.com/repos/{repository}/issues?state=all&per_page={limit}&sort=updated&direction=desc"
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            issues = json.load(response)
        for issue in issues:
            if "pull_request" in issue:
                continue
            labels = [label["name"] for label in issue.get("labels", [])]
            documents.append({
                "source_id": f"github-{repository.replace('/', '-').casefold()}-{issue['number']}",
                "title": issue["title"],
                "topic": "issue",
                "tags": [repository, issue["state"], *labels],
                "excerpt": f"Public issue metadata from {repository}: {issue['title']}",
                "lesson": f"Classification labels: {', '.join(labels) or 'unlabeled'}",
                "citation": issue["html_url"],
            })
    return documents


if __name__ == "__main__":
    documents = collect()
    OUTPUT.write_text(json.dumps(documents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(documents)} issues to {OUTPUT}")
