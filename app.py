"""GameWeaver HTTP API and static web server (standard library only)."""

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from gameweaver import create_plan, refine_plan
from gameweaver.config import load_env
from gameweaver.repository import ProjectRepository

ROOT = Path(__file__).parent
load_env(ROOT / ".env")
REPOSITORY = ProjectRepository(ROOT / os.getenv("GAMEWEAVER_DB", "data/gameweaver.db"))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json(200, {"status": "ok", "ai_configured": bool(os.getenv("OPENAI_API_KEY"))})
        if path == "/api/projects":
            return self._json(200, {"projects": REPOSITORY.list()})
        if path.startswith("/api/projects/"):
            try:
                plan = REPOSITORY.get(int(path.rsplit("/", 1)[1]))
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
            if self.path == "/api/plan":
                result = create_plan(payload)
                result["project_id"] = REPOSITORY.save(payload, result)
                return self._json(200, result)
            if self.path == "/api/refine":
                result = refine_plan(payload)
                result["project_id"] = REPOSITORY.save(payload["input"], result)
                return self._json(200, result)
            return self._json(404, {"error": "API를 찾을 수 없습니다."})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception:
            return self._json(500, {"error": "계획 생성 중 오류가 발생했습니다."})


if __name__ == "__main__":
    port = int(os.getenv("GAMEWEAVER_PORT", "8000"))
    print(f"GameWeaver: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
