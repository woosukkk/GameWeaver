"""MySQL persistence for project inputs and generated plans."""

import json
import os
from collections import defaultdict
from contextlib import contextmanager
from statistics import median
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
            cursor.execute("""CREATE TABLE IF NOT EXISTS task_outcomes (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                plan_id BIGINT UNSIGNED NOT NULL,
                task_id VARCHAR(50) NOT NULL,
                task_name VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                engine VARCHAR(100) NOT NULL,
                estimated_hours DECIMAL(8,2) NOT NULL,
                actual_hours DECIMAL(8,2) NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT TRUE,
                rework_hours DECIMAL(8,2) NOT NULL DEFAULT 0,
                blockers JSON NOT NULL,
                playtest_issues INT UNSIGNED NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uq_task_outcome (plan_id, task_id),
                INDEX idx_outcome_context (genre, engine, task_name)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS project_retrospectives (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                plan_id BIGINT UNSIGNED NOT NULL,
                project_key CHAR(36) NOT NULL,
                project_name VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                engine VARCHAR(100) NOT NULL,
                satisfaction TINYINT UNSIGNED NOT NULL,
                core_loop_achieved BOOLEAN NOT NULL,
                summary TEXT NOT NULL,
                went_well TEXT NOT NULL,
                problems TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uq_project_retrospective_plan (plan_id),
                INDEX idx_retrospective_context (genre, engine),
                FULLTEXT KEY ft_retrospective_text (summary, went_well, problems, recommendations)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""")

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
            cursor.execute("DELETE o FROM task_outcomes o JOIN plans p ON p.id=o.plan_id WHERE p.project_key=%s", (project_key,))
            cursor.execute("DELETE FROM project_retrospectives WHERE project_key=%s", (project_key,))
            cursor.execute("DELETE FROM plans WHERE project_key=%s", (project_key,))
            return cursor.rowcount

    def save_outcomes(self, plan_id, outcomes):
        plan = self.get(plan_id)
        if not plan:
            raise ValueError("계획을 찾을 수 없습니다.")
        tasks = {task["id"]: task for task in plan["result"]["tasks"]}
        project = plan["input"]["project"]
        with self._db() as (_, cursor):
            for outcome in outcomes:
                task = tasks.get(outcome.get("task_id"))
                if not task:
                    raise ValueError("계획에 없는 작업 결과가 포함되어 있습니다.")
                actual = outcome.get("actual_hours")
                rework = outcome.get("rework_hours", 0)
                issues = outcome.get("playtest_issues", 0)
                if not isinstance(actual, (int, float)) or actual < 0 or not isinstance(rework, (int, float)) or rework < 0 or not isinstance(issues, int) or issues < 0:
                    raise ValueError("실제 시간, 재작업 시간, 플레이테스트 이슈는 0 이상이어야 합니다.")
                cursor.execute("""INSERT INTO task_outcomes
                    (plan_id,task_id,task_name,genre,engine,estimated_hours,actual_hours,completed,rework_hours,blockers,playtest_issues)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE actual_hours=VALUES(actual_hours),completed=VALUES(completed),rework_hours=VALUES(rework_hours),blockers=VALUES(blockers),playtest_issues=VALUES(playtest_issues)""",
                    (plan_id, task["id"], task["name"], project["genre"], project["engine"], task["estimated_hours"], actual, bool(outcome.get("completed", True)), rework, _dump(outcome.get("blockers", [])), issues))
        return len(outcomes)

    def calibrations(self, min_samples=3):
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("""SELECT o.genre,o.engine,o.task_name,o.estimated_hours,o.actual_hours
                FROM task_outcomes o JOIN plans p ON p.id=o.plan_id
                WHERE o.completed=TRUE AND o.actual_hours>0 AND o.estimated_hours>0 AND p.status='confirmed'""")
            rows = cursor.fetchall()
        groups = defaultdict(list)
        for row in rows:
            groups[(row["genre"], row["engine"], row["task_name"])].append(float(row["actual_hours"]) / float(row["estimated_hours"]))
        return [{"genre": key[0], "engine": key[1], "task_name": key[2], "sample_count": len(values), "effort_factor": round(median(values), 2)} for key, values in groups.items() if len(values) >= min_samples]

    def save_retrospective(self, plan_id, data):
        plan = self.get(plan_id)
        if not plan or plan["status"] not in ("confirmed", "completed"):
            raise ValueError("확정된 계획만 완료할 수 있습니다.")
        satisfaction = data.get("satisfaction")
        if not isinstance(satisfaction, int) or not 1 <= satisfaction <= 5:
            raise ValueError("만족도는 1~5 사이의 정수여야 합니다.")
        project = plan["input"]["project"]
        values = [str(data.get(name, "")).strip() for name in ("summary", "went_well", "problems", "recommendations")]
        if not values[0]:
            raise ValueError("회고 요약이 필요합니다.")
        with self._db() as (_, cursor):
            cursor.execute("""INSERT INTO project_retrospectives
                (plan_id,project_key,project_name,genre,engine,satisfaction,core_loop_achieved,summary,went_well,problems,recommendations)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE satisfaction=VALUES(satisfaction),core_loop_achieved=VALUES(core_loop_achieved),summary=VALUES(summary),went_well=VALUES(went_well),problems=VALUES(problems),recommendations=VALUES(recommendations)""",
                (plan_id, plan["project_key"], plan["project_name"], project["genre"], project["engine"], satisfaction, bool(data.get("core_loop_achieved")), *values))
            cursor.execute("UPDATE plans SET status='completed' WHERE id=%s", (plan_id,))

    def similar_cases(self, project, limit=3):
        terms = " ".join([project.get("name", ""), project.get("genre", ""), project.get("engine", ""), *project.get("mandatory_features", [])]).strip()
        with self._db(dictionary=True) as (_, cursor):
            cursor.execute("""SELECT plan_id,project_name,genre,engine,satisfaction,core_loop_achieved,summary,went_well,problems,recommendations,
                MATCH(summary,went_well,problems,recommendations) AGAINST (%s IN NATURAL LANGUAGE MODE) AS text_score
                FROM project_retrospectives
                WHERE genre=%s OR engine=%s OR MATCH(summary,went_well,problems,recommendations) AGAINST (%s IN NATURAL LANGUAGE MODE)
                ORDER BY (genre=%s)+(engine=%s) DESC,text_score DESC,updated_at DESC LIMIT %s""",
                (terms, project.get("genre"), project.get("engine"), terms, project.get("genre"), project.get("engine"), limit))
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
