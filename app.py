"""GameWeaver HTTP API and static web server (standard library only)."""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from gameweaver import create_plan, refine_plan

ROOT = Path(__file__).parent


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
        if self.path == "/api/health":
            return self._json(200, {"status": "ok"})
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 1_000_000:
                return self._json(413, {"error": "요청이 너무 큽니다."})
            payload = json.loads(self.rfile.read(length))
            if self.path == "/api/plan":
                return self._json(200, create_plan(payload))
            if self.path == "/api/refine":
                return self._json(200, refine_plan(payload))
            return self._json(404, {"error": "API를 찾을 수 없습니다."})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception:
            return self._json(500, {"error": "계획 생성 중 오류가 발생했습니다."})


if __name__ == "__main__":
    print("GameWeaver: http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
