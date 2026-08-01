#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass190 import (  # noqa: E402
    ArgumentValidationError,
    CapabilityDeniedError,
    HHSOperationError,
    StateConflictError,
    canonical_json,
    get_context,
)


class Handler(BaseHTTPRequestHandler):
    server_version = "HHS-P190/1.0"

    def _write(self, status: int, payload: Any) -> None:
        body = canonical_json(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(payload, dict):
            raise ArgumentValidationError("request body must be an object")
        return payload

    def do_GET(self) -> None:  # noqa: N802
        context = get_context()
        if self.path == "/api/pass190/health":
            self._write(200, context.invoke("system.status", {}, surface="http").to_dict())
            return
        if self.path == "/api/pass190/operations":
            self._write(200, {"operations": [record.raw for record in context.registry.records]})
            return
        if self.path == "/openapi.json":
            self._write(200, context.openapi_document())
            return
        self._write(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        context = get_context()
        try:
            payload = self._body()
            if self.path == "/api/pass190/invoke":
                capabilities = [item.strip() for item in self.headers.get("X-HHS-Capability", "").split(",") if item.strip()]
                result = context.invoke(
                    payload["operation_id"],
                    payload.get("arguments", {}),
                    surface="http",
                    capabilities=capabilities,
                    idempotency_key=self.headers.get("Idempotency-Key"),
                    expected_state=self.headers.get("X-HHS-Expected-State"),
                )
                self._write(200, result.to_dict())
                return
            if self.path == "/api/pass190/replay":
                self._write(200, context.replay(payload["hash72"]).to_dict())
                return
            self._write(404, {"error": "not_found"})
        except CapabilityDeniedError as exc:
            self._write(403, {"error": type(exc).__name__, "message": str(exc)})
        except StateConflictError as exc:
            self._write(409, {"error": type(exc).__name__, "message": str(exc)})
        except (KeyError, ValueError, json.JSONDecodeError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})

    def log_message(self, _format: str, *_args: object) -> None:
        return


def build_server(host: str = "127.0.0.1", port: int = 8190) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8190)
    args = parser.parse_args()
    server = build_server(args.host, args.port)
    print(f"HHS Pass 190 listening on http://{args.host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
