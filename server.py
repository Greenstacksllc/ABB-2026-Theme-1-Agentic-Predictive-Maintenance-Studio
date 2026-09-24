"""Dependency-free local demonstration dashboard. Run: python3 server.py"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from studio import MaintenanceStudio, demo_rows

ROOT = Path(__file__).resolve().parent
studio = MaintenanceStudio()
samples = demo_rows()
cursor = 0


class Handler(BaseHTTPRequestHandler):
    def respond(self, status: int, data: object) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/":
            payload = (ROOT / "dashboard.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif self.path == "/api/state":
            self.respond(200, {**studio.snapshot(), "demo_remaining": len(samples) - cursor})
        else:
            self.respond(404, {"error": "Not found"})

    def do_POST(self) -> None:
        global cursor, studio
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 65536 or length < 0:
                raise ValueError("request exceeds 64 KB")
            body = json.loads(self.rfile.read(length)) if length else {}
            if not isinstance(body, dict):
                raise ValueError("JSON object required")
            if self.path == "/api/next":
                if cursor >= len(samples):
                    raise ValueError("demo stream complete; reset to replay")
                result = studio.ingest(samples[cursor])
                cursor += 1
            elif self.path == "/api/ingest":
                result = studio.ingest(body)
            elif self.path == "/api/review":
                result = studio.review(str(body.get("order_id", "")),
                                       str(body.get("decision", "")),
                                       str(body.get("reviewer", "")))
            elif self.path == "/api/reset":
                studio = MaintenanceStudio()
                cursor = 0
                result = {"reset": True}
            else:
                self.respond(404, {"error": "Not found"})
                return
            self.respond(200, result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.respond(400, {"error": str(exc)})


if __name__ == "__main__":
    hosted = bool(os.environ.get("REPL_ID") or os.environ.get("REPLIT_DEPLOYMENT"))
    host = "0.0.0.0" if hosted else "127.0.0.1"
    port = int(os.environ.get("PORT", "3000" if hosted else "8765"))
    print(f"Serving maintenance demo on {host}:{port}", flush=True)
    HTTPServer((host, port), Handler).serve_forever()
