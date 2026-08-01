#!/usr/bin/env python3
"""Dependency-free Pass 188 HTTP, WebSocket, and visual IDE server."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(PROJECT / "python"))

import hhs_pass188 as runtime  # noqa: E402

INDEX = PROJECT / "web" / "index.html"
_HYDRATION_CACHE: dict[str, object] | None = None


def hydration_summary() -> dict[str, object]:
    global _HYDRATION_CACHE
    if _HYDRATION_CACHE is None:
        _HYDRATION_CACHE = runtime.hydrate()
    return _HYDRATION_CACHE


def websocket_frame(payload: dict[str, object]) -> bytes:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if len(body) < 126:
        return bytes((0x81, len(body))) + body
    if len(body) <= 0xFFFF:
        return bytes((0x81, 126)) + len(body).to_bytes(2, "big") + body
    return bytes((0x81, 127)) + len(body).to_bytes(8, "big") + body


class Handler(BaseHTTPRequestHandler):
    server_version = "HHS-P188/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        if os.environ.get("HHS188_QUIET") != "1":
            super().log_message(fmt, *args)

    def send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict[str, object]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise runtime.Pass188Error("invalid Content-Length") from exc
        if length <= 0 or length > 1_000_000:
            raise runtime.Pass188Error("request body length rejected")
        try:
            value = json.loads(self.rfile.read(length))
        except json.JSONDecodeError as exc:
            raise runtime.Pass188Error("invalid JSON") from exc
        if not isinstance(value, dict):
            raise runtime.Pass188Error("JSON body must be an object")
        return value

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                body = INDEX.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/api/pass188/health":
                self.send_json({
                    "classification": "HHS_PASS_188_RUNTIME_READY",
                    "contract": "HHS-P188-BOTT-RUNTIME-H216-VM81-Q144-G243-X64",
                    "hydrated_states": runtime.HYDRATED_STATES,
                    "floating_point_authority": False,
                    "surfaces": ["C ABI", "x86_64", "Python", "CLI", "HTTP", "WebSocket", "Visual IDE", "Replay"],
                })
                return
            if parsed.path == "/api/pass188/transition":
                query = parse_qs(parsed.query)
                address = int(query.get("address", ["0"])[0])
                self.send_json(runtime.receipt_dict(runtime.transition_projected(address)))
                return
            if parsed.path == "/api/pass188/hydrate":
                self.send_json(hydration_summary())
                return
            if parsed.path == "/api/pass188/events":
                events = [
                    {"event": "runtime-ready", "state": "Ω=true"},
                    {"event": "hydration-complete", **hydration_summary()},
                ]
                body = "".join(f"event: {event['event']}\ndata: {json.dumps(event)}\n\n" for event in events).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/ws":
                self.handle_websocket()
                return
            self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except (ValueError, runtime.Pass188Error, OSError) as exc:
            self.send_json({"classification": "HHS_P188_REJECTED", "error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()
            if parsed.path == "/api/pass188/transition":
                address = int(payload["projected_address"])
                self.send_json(runtime.receipt_dict(runtime.transition_projected(address)))
                return
            if parsed.path == "/api/pass188/replay":
                verified = runtime.replay_receipt(payload)
                self.send_json({
                    "classification": "HHS_P188_REPLAY_VERIFIED" if verified else "HHS_P188_REPLAY_MISMATCH",
                    "verified": verified,
                }, HTTPStatus.OK if verified else HTTPStatus.CONFLICT)
                return
            self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except (KeyError, TypeError, ValueError, runtime.Pass188Error) as exc:
            self.send_json({"classification": "HHS_P188_REJECTED", "error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def handle_websocket(self) -> None:
        if self.headers.get("Upgrade", "").lower() != "websocket":
            self.send_json({"error": "WebSocket upgrade required"}, HTTPStatus.UPGRADE_REQUIRED)
            return
        key = self.headers.get("Sec-WebSocket-Key")
        if not key:
            self.send_json({"error": "Sec-WebSocket-Key required"}, HTTPStatus.BAD_REQUEST)
            return
        accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()).decode("ascii")
        self.send_response(HTTPStatus.SWITCHING_PROTOCOLS)
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        messages = (
            {"event": "runtime-ready", "contract": "HHS-P188-BOTT-RUNTIME-H216-VM81-Q144-G243-X64"},
            {"event": "sample-transition", "receipt": runtime.receipt_dict(runtime.transition_projected(0))},
            {"event": "hydration-complete", "summary": hydration_summary()},
        )
        for message in messages:
            self.wfile.write(websocket_frame(message))
            self.wfile.flush()
        self.wfile.write(b"\x88\x00")
        self.wfile.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8188)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"HHS Pass 188 visual runtime: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
