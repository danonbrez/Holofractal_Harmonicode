"""Dependency-free HTTP surface for Pass 188 license-lineage authority."""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .license_lineage import CONTRACT_ID, LicenseLineageAuthority, execute_operation


class Handler(BaseHTTPRequestHandler):
    authority: LicenseLineageAuthority

    def _send(self, status: int, payload: Any) -> None:
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path == "/api/pass188/license/health":
            self._send(
                200,
                {
                    "ok": True,
                    "contract": CONTRACT_ID,
                    "replay": self.authority.replay(),
                    "external_chain_required": False,
                },
            )
            return
        if self.path == "/api/pass188/license/verify":
            self._send(200, self.authority.verify())
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/api/pass188/license/execute":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            operation = str(body["operation"])
            args = dict(body.get("args", {}))
            result = execute_operation(self.authority, operation, args)
            self._send(200, {"ok": True, "operation": operation, "result": result})
        except (KeyError, ValueError, PermissionError, TypeError) as exc:
            self._send(400, {"ok": False, "error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(host: str, port: int, db: str) -> None:
    authority = LicenseLineageAuthority(db)
    Handler.authority = authority
    server = ThreadingHTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        authority.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8187)
    parser.add_argument("--db", required=True)
    ns = parser.parse_args()
    serve(ns.host, ns.port, ns.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
