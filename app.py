"""GameWeaver HTTP API and static web server (standard library only)."""

import json
import os
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from gameweaver import create_plan, refine_plan
from gameweaver.config import load_env
from gameweaver.repository import ProjectRepository

ROOT = Path(__file__).parent
load_env(ROOT / ".env")
REPOSITORY = ProjectRepository()


def effort_factors(payload, user_id):
    project = payload["project"]
    return {item["task_name"]: item["effort_factor"] for item in REPOSITORY.calibrations(user_id=user_id) if item["genre"] == project["genre"] and item["engine"] == project["engine"]}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)

    def _json(self, status, payload, cookie=None):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def _user(self):
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        token = cookie.get("gameweaver_session")
        return REPOSITORY.session_user(token.value if token else None)

    def _require_user(self):
        user = self._user()
        if not user:
            self._json(401, {"error": "로그인이 필요합니다."})
        return user

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json(200, {"status": "ok", "ai_configured": bool(os.getenv("OPENAI_API_KEY"))})
        if path == "/api/auth/me":
            user = self._user()
            return self._json(200, {"user": user}) if user else self._json(401, {"error": "로그인이 필요합니다."})
        if path.startswith("/api/") and not (user := self._require_user()):
            return
        if path == "/api/projects":
            return self._json(200, {"projects": REPOSITORY.list(user_id=user["id"])})
        if path == "/api/calibrations":
            return self._json(200, {"calibrations": REPOSITORY.calibrations(user_id=user["id"])})
        if path.startswith("/api/plans/"):
            try:
                plan = REPOSITORY.get(int(path.rsplit("/", 1)[1]), user["id"])
            except ValueError:
                plan = None
            return self._json(200, plan) if plan else self._json(404, {"error": "저장된 계획을 찾을 수 없습니다."})
        if path.startswith("/api/projects/") and path.endswith("/plans"):
            project_key = path.split("/")[3]
            return self._json(200, {"plans": REPOSITORY.versions(project_key, user["id"])})
        if path.startswith("/api/projects/"):
            try:
                plan = REPOSITORY.get(int(path.rsplit("/", 1)[1]), user["id"])
            except ValueError:
                plan = None
            return self._json(200, plan) if plan else self._json(404, {"error": "저장된 계획을 찾을 수 없습니다."})
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 1_000_000:
                return self._json(413, {"error": "요청이 너무 큽니다."})
            payload = json.loads(self.rfile.read(length))
            if self.path in ("/api/auth/register", "/api/auth/login"):
                token, user = REPOSITORY.register(payload.get("email"), payload.get("password")) if self.path.endswith("register") else REPOSITORY.login(payload.get("email"), payload.get("password"))
                secure = "; Secure" if os.getenv("APP_ENV") == "production" else ""
                cookie = f"gameweaver_session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000{secure}"
                return self._json(200, {"user": user}, cookie)
            if self.path == "/api/auth/logout":
                cookie = SimpleCookie(self.headers.get("Cookie", "")).get("gameweaver_session")
                REPOSITORY.logout(cookie.value if cookie else None)
                return self._json(200, {"logged_out": True}, "gameweaver_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0")
            user = self._require_user()
            if not user:
                return
            if self.path == "/api/plan":
                result = create_plan(payload, effort_factors=effort_factors(payload, user["id"]), similar_cases=REPOSITORY.similar_cases(payload["project"], user_id=user["id"]))
                result.update(REPOSITORY.save(payload, result, user_id=user["id"]))
                return self._json(200, result)
            if self.path == "/api/refine":
                result = refine_plan(payload, effort_factors=effort_factors(payload["input"], user["id"]), similar_cases=REPOSITORY.similar_cases(payload["input"]["project"], user_id=user["id"]))
                result.update(REPOSITORY.save(payload["input"], result, payload.get("parent_plan_id"), user["id"]))
                return self._json(200, result)
            if self.path.startswith("/api/plans/") and self.path.endswith("/confirm"):
                try:
                    plan_id = int(self.path.split("/")[3])
                except ValueError:
                    return self._json(400, {"error": "계획 ID가 올바르지 않습니다."})
                return self._json(200, {"confirmed": True}) if REPOSITORY.confirm(plan_id, user["id"]) else self._json(404, {"error": "계획을 찾을 수 없습니다."})
            if self.path.startswith("/api/plans/") and self.path.endswith("/outcomes"):
                try:
                    plan_id = int(self.path.split("/")[3])
                except ValueError:
                    return self._json(400, {"error": "계획 ID가 올바르지 않습니다."})
                outcomes = payload.get("outcomes")
                if not isinstance(outcomes, list) or not outcomes:
                    return self._json(400, {"error": "작업 결과가 필요합니다."})
                return self._json(200, {"saved": REPOSITORY.save_outcomes(plan_id, outcomes, user["id"])})
            if self.path.startswith("/api/plans/") and self.path.endswith("/retrospective"):
                try:
                    plan_id = int(self.path.split("/")[3])
                except ValueError:
                    return self._json(400, {"error": "계획 ID가 올바르지 않습니다."})
                REPOSITORY.save_retrospective(plan_id, payload, user["id"])
                return self._json(200, {"completed": True})
            return self._json(404, {"error": "API를 찾을 수 없습니다."})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception:
            return self._json(500, {"error": "계획 생성 중 오류가 발생했습니다."})

    def do_DELETE(self):
        path = urlparse(self.path).path
        user = self._require_user()
        if not user:
            return
        if path.startswith("/api/projects/") and "/" not in path.removeprefix("/api/projects/"):
            deleted = REPOSITORY.delete_project(path.rsplit("/", 1)[1], user["id"])
            return self._json(200, {"deleted_plans": deleted}) if deleted else self._json(404, {"error": "프로젝트를 찾을 수 없습니다."})
        return self._json(404, {"error": "API를 찾을 수 없습니다."})


if __name__ == "__main__":
    port = int(os.getenv("GAMEWEAVER_PORT", "8000"))
    print(f"GameWeaver: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
