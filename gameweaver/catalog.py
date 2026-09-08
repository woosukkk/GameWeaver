"""Load game-domain knowledge from replaceable JSON files."""

import json
from functools import lru_cache
from pathlib import Path

KNOWLEDGE = Path(__file__).parent.parent / "knowledge"


@lru_cache
def common():
    return _read(KNOWLEDGE / "common" / "planning.json")


@lru_cache
def genre(name):
    path = KNOWLEDGE / "genres" / f"{_slug(name)}.json"
    return _read(path if path.exists() else KNOWLEDGE / "genres" / "default.json")


@lru_cache
def engine(name):
    path = KNOWLEDGE / "engines" / f"{_slug(name)}.json"
    return _read(path) if path.exists() else {"context": f"{name} Development", "skills": []}


def _read(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _slug(value):
    return value.casefold().replace(" ", "-")
