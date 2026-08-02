#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import struct
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass189_iteration3 import CLASSIFICATION, CONTRACT, ITERATION, DeviceAuthority  # noqa: E402

WEB_ROOT = ROOT / "web"
AUTHORITY: DeviceAuthority | None = None


def websocket_frame(payload: str) -> bytes:
    data = payload.encode("utf-8")
    if len(data) < 126:
        return bytes((0x81, len(data))) + data
    if len(data) <= 0xFFFF:
        return bytes((0x81, 126)) + struct.pack("!H", len(data)) + data
    return bytes((0x81, 127)) + struct.pack("!Q", len(data)) + data


class Handler(BaseHTTPRequestHandler):
    server_version = "HHS189-I3/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        if os.environ.get("HHS189_I3_QUIET") != "1":
            super().log_message(fmt, *args)

    @property
    def authority(self) -> DeviceAuthority:
        if AUTHORITY is None:
            raise RuntimeError("authority not initialized")
        return AUTHORITY

    def _json(self, payload: object, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 2_000_000:
            raise ValueError("request too large")
        payload = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _serve_file(self, path: Path, content_type: str) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        try:
            if path in ("/", "/pass189/i3"):
                self._serve_file(WEB_ROOT / "iteration3.html", "text/html; charset=utf-8")
                return
            if path == "/api/pass189/i3/status":
                self._json({"status": "ok", **self.authority.status()})
                return
            if path == "/api/pass189/i3/adapter":
                query = parse_qs(parsed.query)
                self._json(self.authority.get_adapter(query.get("adapter_id", [""])[0]))
                return
            if path == "/api/pass189/i3/command":
                query = parse_qs(parsed.query)
                self._json(self.authority.get_command(query.get("command_id", [""])[0]))
                return
            if path == "/api/pass189/i3/events":
                payload = json.dumps({"event": "pass189.iteration3", "authority": self.authority.status()}, separators=(",", ":"))
                data = f"event: pass189-i3\ndata: {payload}\n\n".encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if path == "/ws/pass189/i3":
                key = self.headers.get("Sec-WebSocket-Key")
                if self.headers.get("Upgrade", "").lower() != "websocket" or not key:
                    self._json({"error": "websocket upgrade required"}, 400)
                    return
                accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()).decode("ascii")
                self.send_response(HTTPStatus.SWITCHING_PROTOCOLS)
                self.send_header("Upgrade", "websocket")
                self.send_header("Connection", "Upgrade")
                self.send_header("Sec-WebSocket-Accept", accept)
                self.end_headers()
                self.wfile.write(websocket_frame(json.dumps({"event": "pass189.i3.ready", "authority": self.authority.status()})))
                return
            self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, json.JSONDecodeError, TypeError) as exc:
            self._json({"error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        try:
            body = self._body()
            if path == "/api/pass189/i3/adapter/register":
                self._json(self.authority.register_adapter(body), 201)
                return
            if path == "/api/pass189/i3/adapter/enable":
                self._json(self.authority.set_adapter_enabled(str(body.get("adapter_id", "")), bool(body.get("enabled", False)), created_ns=body.get("created_ns")))
                return
            if path == "/api/pass189/i3/lease/issue":
                self._json(self.authority.issue_lease(body), 201)
                return
            if path == "/api/pass189/i3/lease/revoke":
                self._json(self.authority.revoke_lease(str(body.get("lease_id", "")), created_ns=body.get("created_ns")))
                return
            if path == "/api/pass189/i3/command/prepare":
                self._json(self.authority.prepare_command(body), 201)
                return
            if path == "/api/pass189/i3/command/execute":
                self._json(self.authority.execute_command(str(body.get("command_id", "")), execution_ns=body.get("execution_ns")))
                return
            if path == "/api/pass189/i3/watchdog/sweep":
                self._json(self.authority.sweep_watchdogs(sweep_ns=body.get("sweep_ns")))
                return
            if path == "/api/pass189/i3/checkpoint":
                self._json(self.authority.checkpoint(str(body.get("path", "")), checkpoint_id=str(body.get("checkpoint_id", "")), created_ns=body.get("created_ns")), 201)
                return
            if path == "/api/pass189/i3/checkpoint/verify":
                self._json(DeviceAuthority.verify_checkpoint(
                    str(body.get("path", "")), str(body.get("digest_sha256", "")), int(body.get("captured_sequence", 0)), str(body.get("captured_root_hash72", ""))
                ))
                return
            if path == "/api/pass189/i3/chain/verify":
                self._json(self.authority.verify_event_chain())
                return
            self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, json.JSONDecodeError, TypeError) as exc:
            self._json({"error": str(exc)}, 400)


def main() -> int:
    global AUTHORITY
    parser = argparse.ArgumentParser(description="HHS Pass 189 Iteration 3 server")
    parser.add_argument("--host", default=os.environ.get("HHS189_I3_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("HHS189_I3_PORT", "8191")))
    parser.add_argument("--database", default=os.environ.get("HHS189_I3_DB", "/var/lib/hhs-pass189/iteration3.sqlite3"))
    parser.add_argument("--state-directory", default=os.environ.get("HHS189_I3_STATE", "/var/lib/hhs-pass189/iteration3"))
    args = parser.parse_args()
    AUTHORITY = DeviceAuthority(args.database, state_directory=args.state_directory)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"HHS Pass 189 Iteration 3 listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        AUTHORITY.close()
        AUTHORITY = None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
