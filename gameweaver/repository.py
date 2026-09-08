"""SQLite persistence for project inputs and generated plans."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class ProjectRepository:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                input_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                revision_request TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")

    def save(self, input_data, result):
        with self._db() as db:
            cursor = db.execute(
                "INSERT INTO plans(project_name,input_json,result_json,revision_request) VALUES(?,?,?,?)",
                (input_data["project"]["name"], _dump(input_data), _dump(result), result.get("revision_request", ""))
            )
            return cursor.lastrowid

    def get(self, plan_id):
        with self._db() as db:
            row = db.execute("SELECT * FROM plans WHERE id=?", (plan_id,)).fetchone()
        return _row(row) if row else None

    def list(self, limit=20):
        with self._db() as db:
            rows = db.execute("SELECT id,project_name,revision_request,created_at FROM plans ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        finally:
            db.close()


def _dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _row(row):
    result = dict(row)
    result["input"] = json.loads(result.pop("input_json"))
    result["result"] = json.loads(result.pop("result_json"))
    return result
