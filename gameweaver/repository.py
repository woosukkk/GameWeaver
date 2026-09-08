"""MySQL persistence for project inputs and generated plans."""

import json
import os
from contextlib import contextmanager
from uuid import uuid4


class ProjectRepository:
    def __init__(self, config=None, connector=None):
        if connector is None:
            try:
                import mysql.connector as connector
            except ImportError as exc:
                raise RuntimeError("mysql-connector-python을 설치해 주세요.") from exc
        self.connector = connector
        self.config = config or mysql_config()
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("""CREATE TABLE IF NOT EXISTS plans (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                project_key CHAR(36) NOT NULL,
                project_name VARCHAR(255) NOT NULL,
                version INT UNSIGNED NOT NULL DEFAULT 1,
                parent_plan_id BIGINT UNSIGNED NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'draft',
                input_json JSON NOT NULL,
                result_json JSON NOT NULL,
                revision_request VARCHAR(500) NOT NULL DEFAULT '',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_plans_created_at (created_at)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""")
            columns = {
                "project_key": "ALTER TABLE plans ADD COLUMN project_key CHAR(36) NULL AFTER id",
                "version": "ALTER TABLE plans ADD COLUMN version INT UNSIGNED NOT NULL DEFAULT 1 AFTER project_name",
                "parent_plan_id": "ALTER TABLE plans ADD COLUMN parent_plan_id BIGINT UNSIGNED NULL AFTER version",
                "status": "ALTER TABLE plans ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'draft' AFTER parent_plan_id"
            }
            for name, statement in columns.items():
                cursor.execute("SELECT COUNT(*) AS count FROM information_schema.columns WHERE table_schema=%s AND table_name='plans' AND column_name=%s", (self.config["database"], name))
                if cursor.fetchone()["count"] == 0:
                    cursor.execute(statement)

    def save(self, input_data, result, parent_plan_id=None):
        project_key = input_data["project"].get("id") or str(uuid4())
        input_data["project"]["id"] = project_key
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("SELECT COALESCE(MAX(version),0)+1 AS version FROM plans WHERE project_key=%s", (project_key,))
            version = cursor.fetchone()["version"]
            cursor.execute(
                "INSERT INTO plans(project_key,project_name,version,parent_plan_id,input_json,result_json,revision_request) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (project_key, input_data["project"]["name"], version, parent_plan_id, _dump(input_data), _dump(result), result.get("revision_request", ""))
            )
            return {"plan_id": cursor.lastrowid, "project_key": project_key, "version": version, "status": "draft"}

    def get(self, plan_id):
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("SELECT * FROM plans WHERE id=%s", (plan_id,))
            row = cursor.fetchone()
        return _row(row) if row else None

    def list(self, limit=20):
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("SELECT id,project_key,project_name,version,parent_plan_id,status,revision_request,created_at FROM plans ORDER BY id DESC LIMIT %s", (limit,))
            rows = cursor.fetchall()
        return [_serialize_dates(row) for row in rows]

    def versions(self, project_key):
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("SELECT id,project_key,project_name,version,parent_plan_id,status,revision_request,created_at FROM plans WHERE project_key=%s ORDER BY version", (project_key,))
            rows = cursor.fetchall()
        return [_serialize_dates(row) for row in rows]

    def confirm(self, plan_id):
        with self._db() as (_, cursor):
            cursor.execute("UPDATE plans SET status='confirmed' WHERE id=%s", (plan_id,))
            return cursor.rowcount > 0

    def delete_project(self, project_key):
        with self._db() as (_, cursor):
            cursor.execute("DELETE FROM plans WHERE project_key=%s", (project_key,))
            return cursor.rowcount

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
