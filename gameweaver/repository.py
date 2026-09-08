"""MySQL persistence for project inputs and generated plans."""

import json
import os
from contextlib import contextmanager


class ProjectRepository:
    def __init__(self, config=None, connector=None):
        if connector is None:
            try:
                import mysql.connector as connector
            except ImportError as exc:
                raise RuntimeError("mysql-connector-python을 설치해 주세요.") from exc
        self.connector = connector
        self.config = config or mysql_config()
        with self._db() as (_, cursor):
            cursor.execute("""CREATE TABLE IF NOT EXISTS plans (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                project_name VARCHAR(255) NOT NULL,
                input_json JSON NOT NULL,
                result_json JSON NOT NULL,
                revision_request VARCHAR(500) NOT NULL DEFAULT '',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_plans_created_at (created_at)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""")

    def save(self, input_data, result):
        with self._db() as (_, cursor):
            cursor.execute(
                "INSERT INTO plans(project_name,input_json,result_json,revision_request) VALUES(%s,%s,%s,%s)",
                (input_data["project"]["name"], _dump(input_data), _dump(result), result.get("revision_request", ""))
            )
            return cursor.lastrowid

    def get(self, plan_id):
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("SELECT * FROM plans WHERE id=%s", (plan_id,))
            row = cursor.fetchone()
        return _row(row) if row else None

    def list(self, limit=20):
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("SELECT id,project_name,revision_request,created_at FROM plans ORDER BY id DESC LIMIT %s", (limit,))
            rows = cursor.fetchall()
        return [_serialize_dates(row) for row in rows]

    @contextmanager
    def _db(self, dictionary=False):
        connection = self.connector.connect(**self.config)
        cursor = connection.cursor(dictionary=dictionary)
        try:
            yield connection, cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()


def mysql_config():
    required = {"user": os.getenv("MYSQL_USER"), "password": os.getenv("MYSQL_PASSWORD"), "database": os.getenv("MYSQL_DATABASE")}
    missing = [f"MYSQL_{key.upper()}" for key, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"MySQL 설정이 필요합니다: {', '.join(missing)}")
    return {"host": os.getenv("MYSQL_HOST", "127.0.0.1"), "port": int(os.getenv("MYSQL_PORT", "3306")), "charset": "utf8mb4", **required}


def _dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _row(row):
    result = _serialize_dates(dict(row))
    result["input"] = json.loads(result.pop("input_json"))
    result["result"] = json.loads(result.pop("result_json"))
    return result


def _serialize_dates(row):
    result = dict(row)
    if hasattr(result.get("created_at"), "isoformat"):
        result["created_at"] = result["created_at"].isoformat()
    return result
