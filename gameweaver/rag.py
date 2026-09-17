"""Retrieve compact, attributed game-development evidence for the planning agent."""

import csv
import json
import re
from functools import lru_cache
from pathlib import Path


DATASET = Path(__file__).parent.parent / "knowledge" / "datasets" / "game-development-antipatterns" / "problems.tsv"
DOCUMENTS = Path(__file__).parent.parent / "knowledge" / "documents"
SOURCE = "https://doi.org/10.5281/zenodo.5828315"
TOKEN = re.compile(r"[0-9A-Za-z가-힣]+")


def retrieve(project, limit=4):
    query = _tokens(" ".join(_project_terms(project)))
    selectors = {str(project.get(key, "")).casefold() for key in ("genre", "engine", "platform")}
    cases, documents = [], []
    for index, row in enumerate(_rows(), 1):
        topic = row.get("problem_type", "").strip().casefold()
        text = " ".join((row.get("game", ""), topic, row.get("problem_from_postmortem", ""), row.get("antipattern", "")))
        score = len(query & _tokens(text)) + (3 if topic in query else 0)
        if score:
            cases.append((score, index, _evidence(index, row)))
    for index, row in enumerate(_documents(), 1):
        text = " ".join((row["title"], row["topic"], row["excerpt"], row["lesson"], *row.get("tags", [])))
        tags = {tag.casefold() for tag in row.get("tags", [])}
        score = 5 * len(query & _tokens(text)) + 10 * len(selectors & tags)
        if score:
            documents.append((score, index, row))
    cases.sort(key=lambda item: (-item[0], item[1]))
    documents.sort(key=lambda item: (-item[0], item[1]))
    document_limit = max(1, limit // 2)
    selected, topics = [], set()
    for item in documents:
        if item[2]["topic"] not in topics:
            selected.append(item)
            topics.add(item[2]["topic"])
        if len(selected) == document_limit:
            break
    selected += [item for item in documents if item not in selected][: document_limit - len(selected)]
    selected += cases[: limit - len(selected)]
    return [row for _, _, row in selected]


def _project_terms(project):
    values = [project.get(key, "") for key in ("name", "genre", "engine", "platform", "description", "content_scale")]
    values += project.get("mandatory_features", []) + project.get("constraints", [])
    if project.get("duration_weeks", 52) <= 6:
        values += ["planning", "scope", "delays", "cutting-features"]
    if project.get("content_scale") == "대규모":
        values += ["scope", "feature-creep", "crunch-time"]
    values.append("team")
    return [str(value) for value in values]


def _tokens(text):
    return {value.casefold() for value in TOKEN.findall(text) if len(value) > 2 and value.casefold() not in {"game", "게임", "project"}}


@lru_cache
def _rows():
    with DATASET.open(encoding="utf-8-sig", newline="") as file:
        return tuple(row for row in csv.DictReader(file, delimiter="\t") if row.get("problem_from_postmortem"))


@lru_cache
def _documents():
    return tuple(document for path in sorted(DOCUMENTS.glob("*.json")) for document in json.loads(path.read_text(encoding="utf-8")))


def _evidence(index, row):
    excerpt = " ".join(row["problem_from_postmortem"].split())
    return {
        "source_id": f"gas2022-{index}",
        "title": f"{row.get('game') or 'Unknown game'} ({row.get('year') or 'unknown year'})",
        "topic": row.get("problem_type", ""),
        "excerpt": excerpt[:600],
        "lesson": row.get("antipattern", "").strip("()"),
        "citation": SOURCE,
    }
