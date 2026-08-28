"""Dependency-free HTTP/SSE server for Pass 187 composition authority."""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .composition import CONTRACT_ID, CompositionAuthority


class Handler(BaseHTTPRequestHandler):
    authority: CompositionAuthority
    web_root: Path

    def _send_json(self, status: int, payload: Any) -> None:
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path in {"/", "/pass187"}:
            payload = (self.web_root / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.send_header("content-length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == "/api/pass187/health":
            self._send_json(200, {"ok": True, "contract": CONTRACT_ID})
            return
        if self.path == "/api/pass187/status":
            self._send_json(200, self.authority.status())
            return
        if self.path == "/api/pass187/events":
            rows = self.authority._connection.execute(
                "SELECT sequence,operation,vm81_receipt_hash72,event_evidence_hash72 FROM events ORDER BY sequence"
            ).fetchall()
            phases = (
                "candidate_graph_intent",
                "authority_admission",
                "runtime_execution",
                "projection_update",
                "receipt_commit",
            )
            body = "".join(
                "event: "
                + phase
                + "\ndata: "
                + json.dumps(
                    {
                        **dict(row),
                        "phase": phase,
                        "projection_event_is_authority": False,
                    },
                    sort_keys=True,
                )
                + "\n\n"
                for row in rows
                for phase in phases
            ).encode()
            self.send_response(200)
            self.send_header("content-type", "text/event-stream")
            self.send_header("cache-control", "no-cache")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path not in {"/api/pass187/execute", "/api/pass187/preview"}:
            self._send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            operation = str(body["operation"])
            args = dict(body.get("args", {}))
            if self.path.endswith("/preview"):
                if operation.upper() in {"CONNECT", "INTEGRATE", "LAYER", "NEST", "REFERENCE"}:
                    result = self.authority.compatibility(
                        args["source_logical_object_id"],
                        args["source_port"],
                        args["target_logical_object_id"],
                        args["target_port"],
                    )
                    self._send_json(200, {"ok": True, "candidate_only": True, "result": result})
                    return
                self._send_json(400, {"ok": False, "error": "preview unsupported"})
                return
            result = self.authority.execute(operation, args)
            self._send_json(
                200,
                {
                    "ok": True,
                    "operation": operation,
                    "result": result,
                    "projection_event_is_authority": False,
                },
            )
        except (KeyError, ValueError, PermissionError, TypeError) as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(host: str, port: int, db: str, web_root: str) -> None:
    authority = CompositionAuthority(db)
    Handler.authority = authority
    Handler.web_root = Path(web_root)
    server = ThreadingHTTPServer((host, int(port)), Handler)
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
    parser.add_argument(
        "--web-root",
        default="native_projects/hhs_pass187_composition_fabric/web",
    )
    ns = parser.parse_args()
    serve(ns.host, ns.port, ns.db, ns.web_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
