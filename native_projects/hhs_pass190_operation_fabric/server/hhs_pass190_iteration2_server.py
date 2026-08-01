#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import socket
import struct
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass190 import (  # noqa: E402
    ArgumentValidationError,
    CapabilityDeniedError,
    HHSOperationError,
    StateConflictError,
    canonical_json,
)
from hhs_pass190_iteration2 import (  # noqa: E402
    PersistentAuthorityContext,
    PersistentStoreError,
)

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def websocket_text_frame(payload: Any) -> bytes:
    body = canonical_json(payload).encode("utf-8")
    first = 0x81
    length = len(body)
    if length < 126:
        return bytes((first, length)) + body
    if length < 65_536:
        return bytes((first, 126)) + struct.pack("!H", length) + body
    return bytes((first, 127)) + struct.pack("!Q", length) + body


class Pass190Iteration2Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], context: PersistentAuthorityContext):
        self.context = context
        super().__init__(address, Handler)

    def server_close(self) -> None:
        super().server_close()
        self.context.close()


class Handler(BaseHTTPRequestHandler):
    server_version = "HHS-P190-I2/2.0"

    @property
    def context(self) -> PersistentAuthorityContext:
        return self.server.context  # type: ignore[attr-defined]

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

    @staticmethod
    def _range(query: dict[str, list[str]]) -> tuple[int, int]:
        after = int(query.get("after", ["0"])[0])
        limit = int(query.get("limit", ["100"])[0])
        return after, limit

    def _websocket(self, query: dict[str, list[str]]) -> None:
        if self.headers.get("Upgrade", "").lower() != "websocket":
            self._write(426, {"error": "websocket_upgrade_required"})
            return
        key = self.headers.get("Sec-WebSocket-Key")
        if not key:
            self._write(400, {"error": "missing_websocket_key"})
            return
        accept = base64.b64encode(hashlib.sha1((key + WS_GUID).encode("ascii")).digest()).decode("ascii")
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        sequence = int(query.get("after", ["0"])[0])
        self.connection.settimeout(35)
        try:
            self.connection.sendall(websocket_text_frame({
                "schema": "HHS_PASS_190_EVENT_V1",
                "event_type": "channel.ready",
                "after": sequence,
                "integrity": self.context.integrity_report(),
            }))
            while True:
                events = self.context.wait_for_events(sequence, timeout=15)
                if not events:
                    self.connection.sendall(websocket_text_frame({
                        "schema": "HHS_PASS_190_EVENT_V1",
                        "event_type": "channel.heartbeat",
                        "after": sequence,
                    }))
                    continue
                for event in events:
                    sequence = max(sequence, int(event["sequence"]))
                    self.connection.sendall(websocket_text_frame(event))
        except (BrokenPipeError, ConnectionResetError, socket.timeout, OSError):
            return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/pass190/health":
                self._write(200, self.context.invoke("system.status", {}, surface="http").to_dict())
                return
            if parsed.path == "/api/pass190/operations":
                self._write(200, {"operations": [record.raw for record in self.context.registry.records]})
                return
            if parsed.path == "/api/pass190/integrity":
                self._write(200, self.context.integrity_report())
                return
            if parsed.path == "/api/pass190/events":
                after, limit = self._range(query)
                self._write(200, {"events": self.context.events_after(after, limit)})
                return
            if parsed.path == "/api/pass190/receipts":
                after, limit = self._range(query)
                self._write(200, {"receipts": self.context.receipts_after(after, limit)})
                return
            if parsed.path == "/api/pass190/ws":
                self._websocket(query)
                return
            if parsed.path == "/openapi.json":
                document = self.context.openapi_document()
                document["info"]["version"] = "2.0.0"
                document["x-hhs-iteration"] = 2
                document["x-hhs-websocket"] = "/api/pass190/ws"
                self._write(200, document)
                return
            self._write(404, {"error": "not_found"})
        except (ValueError, PersistentStoreError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        try:
            payload = self._body()
            if parsed.path == "/api/pass190/invoke":
                capabilities = [item.strip() for item in self.headers.get("X-HHS-Capability", "").split(",") if item.strip()]
                result = self.context.invoke(
                    payload["operation_id"],
                    payload.get("arguments", {}),
                    surface="http",
                    capabilities=capabilities,
                    idempotency_key=self.headers.get("Idempotency-Key"),
                    expected_state=self.headers.get("X-HHS-Expected-State"),
                )
                self._write(200, result.to_dict())
                return
            if parsed.path == "/api/pass190/replay":
                self._write(200, self.context.replay(payload["hash72"]).to_dict())
                return
            self._write(404, {"error": "not_found"})
        except CapabilityDeniedError as exc:
            self._write(403, {"error": type(exc).__name__, "message": str(exc)})
        except StateConflictError as exc:
            self._write(409, {"error": type(exc).__name__, "message": str(exc)})
        except (KeyError, ValueError, json.JSONDecodeError, PersistentStoreError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})

    def log_message(self, _format: str, *_args: object) -> None:
        return


def build_server(
    host: str = "127.0.0.1",
    port: int = 8190,
    *,
    database: Path | str = "pass190-authority.sqlite3",
    context: PersistentAuthorityContext | None = None,
) -> Pass190Iteration2Server:
    return Pass190Iteration2Server((host, port), context or PersistentAuthorityContext(database))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8190)
    parser.add_argument("--database", default="pass190-authority.sqlite3")
    args = parser.parse_args()
    server = build_server(args.host, args.port, database=args.database)
    print(f"HHS Pass 190 iteration 2 listening on http://{args.host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
