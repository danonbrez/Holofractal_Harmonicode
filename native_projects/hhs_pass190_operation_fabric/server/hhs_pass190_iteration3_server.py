#!/usr/bin/env python3
"""Combined Pass 190 Iteration 3 compiler, native ABI, and hardened remote authority."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import sqlite3
import struct
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterable, Mapping
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
from hhs_pass190_capability import (  # noqa: E402
    AUTHORIZATION_SCHEME,
    CapabilityTokenError,
    parse_authorization_header,
    verify_capability_token,
)
from hhs_pass190_iteration2 import PersistentStoreError  # noqa: E402
from hhs_pass190_iteration3 import (  # noqa: E402
    DEFAULT_NATIVE_MANIFEST,
    HarmonicodeOperationCompiler,
    NativeABIError,
)
from hhs_pass190_iteration3_hardening import (  # noqa: E402
    HARDENING_CLASSIFICATION,
    HardenedAuthorityContext,
)

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
MAX_CURSOR = 9_223_372_036_854_775_807


def websocket_text_frame(payload: Any) -> bytes:
    body = canonical_json(payload).encode("utf-8")
    if len(body) < 126:
        return bytes((0x81, len(body))) + body
    if len(body) < 65_536:
        return bytes((0x81, 126)) + struct.pack("!H", len(body)) + body
    return bytes((0x81, 127)) + struct.pack("!Q", len(body)) + body


def iteration3_openapi_document(context: HardenedAuthorityContext) -> dict[str, Any]:
    document = context.openapi_document()
    document["info"]["version"] = "3.1.0"
    document["x-hhs-iteration"] = 3
    document["x-hhs-native-abi"] = "/api/pass190/native-abi"
    document["x-hhs-authenticated-hardening"] = HARDENING_CLASSIFICATION
    document["x-hhs-websocket"] = {
        "path": "/api/pass190/ws",
        "resume_parameter": "after",
        "event_schema": "HHS_PASS_190_EVENT_V1",
    }
    document.setdefault("components", {}).setdefault("securitySchemes", {})[
        "HhsCapabilityToken"
    ] = {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": f"{AUTHORIZATION_SCHEME} <signed-token>",
    }
    paths = document.setdefault("paths", {})
    for path, operation_id, description in (
        ("/api/pass190/health", "pass190.health", "Runtime status receipt"),
        ("/api/pass190/operations", "pass190.operations", "Canonical operation registry"),
        ("/api/pass190/integrity", "pass190.integrity", "Verified persistent authority"),
        ("/api/pass190/events", "pass190.events", "Verified event page"),
        ("/api/pass190/receipts", "pass190.receipts", "Receipt page"),
        ("/api/pass190/native-abi", "pass190.native.abi", "Native ABI manifest"),
    ):
        paths[path] = {"get": {"operationId": operation_id, "responses": {"200": {"description": description}}}}
    paths["/api/pass190/invoke"] = {
        "post": {
            "operationId": "pass190.invoke",
            "security": [{"HhsCapabilityToken": []}],
            "responses": {
                "200": {"description": "Admitted result and receipt"},
                "401": {"description": "Invalid capability credential"},
                "403": {"description": "Required scope absent"},
                "409": {"description": "Expected-state conflict"},
                "503": {"description": "Persistent authority unavailable"},
            },
        }
    }
    paths["/api/pass190/replay"] = {
        "post": {"operationId": "pass190.replay", "responses": {"200": {"description": "Verified replay result"}}}
    }
    paths["/api/pass190/compile"] = {
        "post": {
            "operationId": "pass190.compile",
            "summary": "Lower exact constructors through CST, AST, HIR, and VMIR",
            "responses": {"200": {"description": "Compiled program"}},
        }
    }
    paths["/api/pass190/compile-execute"] = {
        "post": {
            "operationId": "pass190.compile.execute",
            "security": [{"HhsCapabilityToken": []}],
            "summary": "Compile and execute through persistent VM81 authority",
            "responses": {
                "200": {"description": "Compiled program and admitted results"},
                "401": {"description": "Invalid capability credential"},
                "403": {"description": "Required scope absent"},
                "503": {"description": "Persistent authority unavailable"},
            },
        }
    }
    return document


class Pass190Iteration3Server(ThreadingHTTPServer):
    daemon_threads = False
    block_on_close = True

    def __init__(
        self,
        address: tuple[str, int],
        context: HardenedAuthorityContext,
        compiler: HarmonicodeOperationCompiler,
        capability_secret: str | bytes,
    ):
        self.context = context
        self.compiler = compiler
        self.capability_secret = capability_secret
        self.closing = threading.Event()
        super().__init__(address, Handler)

    def server_close(self) -> None:
        self.closing.set()
        super().server_close()
        self.context.close()


class Handler(BaseHTTPRequestHandler):
    server_version = "HHS-P190-I3/3.1"

    @property
    def context(self) -> HardenedAuthorityContext:
        return self.server.context  # type: ignore[attr-defined]

    @property
    def compiler(self) -> HarmonicodeOperationCompiler:
        return self.server.compiler  # type: ignore[attr-defined]

    @property
    def capability_secret(self) -> str | bytes:
        return self.server.capability_secret  # type: ignore[attr-defined]

    @property
    def closing(self) -> threading.Event:
        return self.server.closing  # type: ignore[attr-defined]

    def _write(self, status: int, payload: Any) -> None:
        body = canonical_json(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ArgumentValidationError("Content-Type must be application/json")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ArgumentValidationError("invalid Content-Length") from exc
        if length < 0 or length > 1_048_576:
            raise ArgumentValidationError("request body outside admitted size")
        payload = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(payload, dict):
            raise ArgumentValidationError("request body must be an object")
        return payload

    @staticmethod
    def _query_integer(query: Mapping[str, list[str]], name: str, default: int, minimum: int, maximum: int) -> int:
        values = query.get(name, [str(default)])
        if len(values) != 1:
            raise ArgumentValidationError(f"duplicate {name} parameter")
        try:
            value = int(values[0], 10)
        except ValueError as exc:
            raise ArgumentValidationError(f"invalid {name} parameter") from exc
        if value < minimum or value > maximum:
            raise ArgumentValidationError(f"{name} parameter outside admitted range")
        return value

    @classmethod
    def _range(cls, query: Mapping[str, list[str]]) -> tuple[int, int]:
        return (
            cls._query_integer(query, "after", 0, 0, MAX_CURSOR),
            cls._query_integer(query, "limit", 100, 1, 1000),
        )

    def _authorized_capabilities(self, operation_ids: Iterable[str]) -> tuple[frozenset[str], str]:
        if self.headers.get("X-HHS-Capability"):
            raise CapabilityTokenError("unsigned X-HHS-Capability claims are forbidden")
        required = {self.context.registry.resolve(operation_id).capability for operation_id in operation_ids} - {"public", "none"}
        authorization = self.headers.get("Authorization")
        if not required and not authorization:
            return frozenset(), "anonymous"
        principal = verify_capability_token(
            parse_authorization_header(authorization),
            self.capability_secret,
        )
        missing = required - principal.scopes
        if missing:
            raise CapabilityDeniedError(f"missing authenticated capabilities: {sorted(missing)}")
        return principal.scopes, principal.principal

    @staticmethod
    def _validated_websocket_key(key: str | None) -> str:
        if not key:
            raise ArgumentValidationError("missing websocket key")
        try:
            decoded = base64.b64decode(key, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ArgumentValidationError("invalid websocket key") from exc
        if len(decoded) != 16:
            raise ArgumentValidationError("invalid websocket key length")
        return key

    def _websocket(self, query: Mapping[str, list[str]]) -> None:
        sequence = self._query_integer(query, "after", 0, 0, MAX_CURSOR)
        if self.headers.get("Upgrade", "").lower() != "websocket":
            self._write(426, {"error": "websocket_upgrade_required"})
            return
        tokens = {value.strip().lower() for value in self.headers.get("Connection", "").split(",") if value.strip()}
        if "upgrade" not in tokens:
            raise ArgumentValidationError("invalid websocket Connection header")
        if self.headers.get("Sec-WebSocket-Version") != "13":
            self._write(426, {"error": "unsupported_websocket_version"})
            return
        key = self._validated_websocket_key(self.headers.get("Sec-WebSocket-Key"))
        accept = base64.b64encode(hashlib.sha1((key + WS_GUID).encode("ascii")).digest()).decode("ascii")
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        self.connection.settimeout(35)
        try:
            self.connection.sendall(websocket_text_frame({
                "schema": "HHS_PASS_190_EVENT_V1",
                "event_type": "channel.ready",
                "after": sequence,
                "integrity": self.context.integrity_report(),
            }))
            while not self.closing.is_set():
                events = self.context.wait_for_events(sequence, timeout=0.25)
                if self.closing.is_set():
                    break
                for event in events:
                    sequence = max(sequence, int(event["sequence"]))
                    self.connection.sendall(websocket_text_frame(event))
        except (BrokenPipeError, ConnectionResetError, socket.timeout, OSError):
            return

    def _manifest(self) -> dict[str, Any]:
        return json.loads(DEFAULT_NATIVE_MANIFEST.read_text(encoding="utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        query = parse_qs(parsed.query, keep_blank_values=True)
        try:
            if parsed.path == "/api/pass190/health":
                self._write(200, self.context.invoke("system.status", {}, surface="http").to_dict())
            elif parsed.path == "/api/pass190/operations":
                self._write(200, {"operations": [record.raw for record in self.context.registry.records]})
            elif parsed.path == "/api/pass190/integrity":
                self._write(200, self.context.integrity_report())
            elif parsed.path == "/api/pass190/events":
                after, limit = self._range(query)
                self._write(200, {"events": self.context.events_after(after, limit)})
            elif parsed.path == "/api/pass190/receipts":
                after, limit = self._range(query)
                self._write(200, {"receipts": self.context.receipts_after(after, limit)})
            elif parsed.path == "/api/pass190/native-abi":
                self._write(200, self._manifest())
            elif parsed.path == "/api/pass190/ws":
                self._websocket(query)
            elif parsed.path == "/openapi.json":
                self._write(200, iteration3_openapi_document(self.context))
            else:
                self._write(404, {"error": "not_found"})
        except (PersistentStoreError, sqlite3.Error, OSError) as exc:
            self._write(503, {"error": "persistent_authority_unavailable", "message": str(exc)})
        except (ValueError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        try:
            payload = self._body()
            if parsed.path == "/api/pass190/invoke":
                operation_id = payload["operation_id"]
                if not isinstance(operation_id, str):
                    raise ArgumentValidationError("operation_id must be a string")
                capabilities, principal = self._authorized_capabilities([operation_id])
                self._write(200, self.context.invoke(
                    operation_id,
                    payload.get("arguments", {}),
                    surface=f"http:{principal}",
                    capabilities=capabilities,
                    idempotency_key=self.headers.get("Idempotency-Key"),
                    expected_state=self.headers.get("X-HHS-Expected-State"),
                ).to_dict())
                return
            if parsed.path == "/api/pass190/replay":
                receipt_hash = payload["hash72"]
                if not isinstance(receipt_hash, str) or len(receipt_hash) != 72:
                    raise ArgumentValidationError("hash72 must contain exactly 72 glyphs")
                self._write(200, self.context.replay(receipt_hash).to_dict())
                return
            if parsed.path in {"/api/pass190/compile", "/api/pass190/compile-execute"}:
                source = payload["source"]
                if not isinstance(source, str):
                    raise ArgumentValidationError("source must be a string")
                program = self.compiler.compile_program(source)
                response: dict[str, Any] = {"program": program}
                if parsed.path.endswith("compile-execute"):
                    operation_ids = [item["operation_id"] for item in program["instructions"]]
                    capabilities, _principal = self._authorized_capabilities(operation_ids)
                    response["results"] = self.compiler.execute(program, self.context, capabilities=capabilities)
                self._write(200, response)
                return
            self._write(404, {"error": "not_found"})
        except CapabilityTokenError as exc:
            self._write(401, {"error": type(exc).__name__, "message": str(exc)})
        except CapabilityDeniedError as exc:
            self._write(403, {"error": type(exc).__name__, "message": str(exc)})
        except StateConflictError as exc:
            self._write(409, {"error": type(exc).__name__, "message": str(exc)})
        except (PersistentStoreError, sqlite3.Error, OSError) as exc:
            self._write(503, {"error": "persistent_authority_unavailable", "message": str(exc)})
        except (KeyError, ValueError, json.JSONDecodeError, NativeABIError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})

    def log_message(self, _format: str, *_args: object) -> None:
        return


def build_server(
    host: str = "127.0.0.1",
    port: int = 8190,
    *,
    database: Path | str = "pass190-authority.sqlite3",
    context: HardenedAuthorityContext | None = None,
    compiler: HarmonicodeOperationCompiler | None = None,
    capability_secret: str | bytes | None = None,
) -> Pass190Iteration3Server:
    secret = capability_secret or os.environ.get("HHS_PASS190_CAPABILITY_SECRET")
    if not secret:
        raise RuntimeError("HHS_PASS190_CAPABILITY_SECRET is required")
    return Pass190Iteration3Server(
        (host, port),
        context or HardenedAuthorityContext(database),
        compiler or HarmonicodeOperationCompiler(),
        secret,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8190)
    parser.add_argument("--database", default="pass190-authority.sqlite3")
    args = parser.parse_args()
    server = build_server(args.host, args.port, database=args.database)
    print(f"HHS Pass 190 iteration 3 listening on http://{args.host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
