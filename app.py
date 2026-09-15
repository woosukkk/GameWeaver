"""GameWeaver HTTP API and static web server (standard library only)."""

import json
import logging
import os
import secrets
import time
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from gameweaver import create_plan, refine_plan
from gameweaver.config import load_env
from gameweaver.auth import RateLimiter, csrf_token
from gameweaver.observability import event, request_id
from gameweaver.repository import ProjectRepository

ROOT = Path(__file__).parent
load_env(ROOT / ".env")
REPOSITORY = ProjectRepository()
AUTH_LIMITER = RateLimiter()
# ponytail: process-local limiter; move counters to a shared store when multiple workers are deployed.
IP_AUTH_LIMITER = RateLimiter(limit=20)
LOGGER = logging.getLogger("gameweaver")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)


def effort_factors(payload, user_id):
    project = payload["project"]
    return {item["task_name"]: item["effort_factor"] for item in REPOSITORY.calibrations(user_id=user_id) if item["genre"] == project["genre"] and item["engine"] == project["engine"]}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.started_at = time.monotonic()
        self.trace_id = None
        self.user_id = None
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)

    def _trace_id(self):
        if not self.trace_id:
            self.trace_id = request_id(self.headers.get("X-Request-ID"))
        return self.trace_id

    def log_request(self, code="-", size="-"):
        LOGGER.info(event("http_request", request_id=self._trace_id(), method=self.command, path=urlparse(self.path).path, status=code, duration_ms=round((time.monotonic() - self.started_at) * 1000, 1), user_id=self.user_id))

    def log_message(self, format, *args):
        LOGGER.warning(event("server_message", request_id=self._trace_id(), message=format % args))

    def end_headers(self):
        self.send_header("X-Request-ID", self._trace_id())
        super().end_headers()

    def _json(self, status, payload, cookies=None):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for cookie in cookies or []:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def _user(self):
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        token = cookie.get("gameweaver_session")
        user = REPOSITORY.session_user(token.value if token else None)
        self.user_id = user["id"] if user else None
        return user

    def _cookies(self):
        return SimpleCookie(self.headers.get("Cookie", ""))

    def _csrf_valid(self):
        cookie = self._cookies().get("gameweaver_csrf")
        supplied = self.headers.get("X-CSRF-Token", "")
        return bool(cookie and supplied and secrets.compare_digest(cookie.value, supplied))

    def _csrf_cookie(self, token=None, clear=False):
        secure = "; Secure" if os.getenv("APP_ENV") == "production" else ""
        return f"gameweaver_csrf={token or ''}; SameSite=Lax; Path=/; Max-Age={'0' if clear else '2592000'}{secure}"

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
            if not user:
                return self._json(401, {"error": "로그인이 필요합니다."})
            csrf = self._cookies().get("gameweaver_csrf")
            return self._json(200, {"user": user}, [] if csrf else [self._csrf_cookie(csrf_token())])
        if path.startswith("/api/") and not (user := self._require_user()):
            return
        if path == "/api/projects":
            return self._json(200, {"projects": REPOSITORY.list(user_id=user["id"])})
        if path == "/api/calibrations":
            return self._json(200, {"calibrations": REPOSITORY.calibrations(user_id=user["id"])})
        if path.startswith("/api/plans/") and path.endswith("/feedback"):
            try:
                feedback = REPOSITORY.feedback(int(path.split("/")[3]), user["id"])
            except ValueError:
                feedback = None
            return self._json(200, feedback) if feedback is not None else self._json(404, {"error": "계획을 찾을 수 없습니다."})
        if path.startswith("/api/projects/") and path.endswith("/members"):
            members = REPOSITORY.members(path.split("/")[3], user["id"])
            return self._json(200, {"members": members}) if members is not None else self._json(404, {"error": "프로젝트를 찾을 수 없습니다."})
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
                ip = self.client_address[0]
                key = str(payload.get("email", "")).strip().casefold()
                if not IP_AUTH_LIMITER.allow(ip) or not AUTH_LIMITER.allow(key):
                    return self._json(429, {"error": "로그인 시도가 너무 많습니다. 5분 후 다시 시도하세요."})
                token, user = REPOSITORY.register(payload.get("email"), payload.get("password")) if self.path.endswith("register") else REPOSITORY.login(payload.get("email"), payload.get("password"))
                AUTH_LIMITER.reset(key)
                secure = "; Secure" if os.getenv("APP_ENV") == "production" else ""
                cookie = f"gameweaver_session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000{secure}"
                return self._json(200, {"user": user}, [cookie, self._csrf_cookie(csrf_token())])
            user = self._require_user()
            if not user:
                return
            if not self._csrf_valid():
                return self._json(403, {"error": "요청 보안 토큰이 올바르지 않습니다."})
            if self.path == "/api/auth/logout":
                cookie = self._cookies().get("gameweaver_session")
                REPOSITORY.logout(cookie.value if cookie else None)
                expired = "gameweaver_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"
                return self._json(200, {"logged_out": True}, [expired, self._csrf_cookie(clear=True)])
            if self.path == "/api/plan":
                result = create_plan(payload, effort_factors=effort_factors(payload, user["id"]), similar_cases=REPOSITORY.similar_cases(payload["project"], user_id=user["id"]))
                result.update(REPOSITORY.save(payload, result, user_id=user["id"]))
                return self._json(200, result)
            if self.path == "/api/invitations/accept":
                return self._json(200, {"project_key": REPOSITORY.accept_invitation(payload.get("token"), user["id"])})
            if self.path.startswith("/api/projects/") and self.path.endswith("/invitations"):
                project_key = self.path.split("/")[3]
                token = REPOSITORY.invite(project_key, payload.get("email"), payload.get("role", "editor"), user["id"])
                return self._json(200, {"invitation_token": token, "expires_in_days": 7})
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
        except Exception as exc:
            LOGGER.exception(event("unhandled_error", request_id=self._trace_id(), method=self.command, path=urlparse(self.path).path, error_type=type(exc).__name__))
            return self._json(500, {"error": "계획 생성 중 오류가 발생했습니다."})

    def do_DELETE(self):
        path = urlparse(self.path).path
        user = self._require_user()
        if not user:
            return
        if not self._csrf_valid():
            return self._json(403, {"error": "요청 보안 토큰이 올바르지 않습니다."})
        if path.startswith("/api/projects/") and "/" not in path.removeprefix("/api/projects/"):
            deleted = REPOSITORY.delete_project(path.rsplit("/", 1)[1], user["id"])
            return self._json(200, {"deleted_plans": deleted}) if deleted else self._json(404, {"error": "프로젝트를 찾을 수 없습니다."})
        return self._json(404, {"error": "API를 찾을 수 없습니다."})


if __name__ == "__main__":
    port = int(os.getenv("GAMEWEAVER_PORT", "8000"))
    print(f"GameWeaver: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
