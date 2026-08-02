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

from hhs_pass189_iteration2 import CalibrationLedger, CLASSIFICATION  # noqa: E402

WEB_ROOT = ROOT / "web"
LEDGER: CalibrationLedger | None = None


def websocket_frame(payload: str) -> bytes:
    data = payload.encode("utf-8")
    if len(data) < 126:
        return bytes((0x81, len(data))) + data
    if len(data) <= 0xFFFF:
        return bytes((0x81, 126)) + struct.pack("!H", len(data)) + data
    return bytes((0x81, 127)) + struct.pack("!Q", len(data)) + data


def authority() -> CalibrationLedger:
    if LEDGER is None:
        raise RuntimeError("iteration 2 authority not initialized")
    return LEDGER


class Handler(BaseHTTPRequestHandler):
    server_version = "HHS189-I2/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        if os.environ.get("HHS189_I2_QUIET") != "1":
            super().log_message(fmt, *args)

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
        if length > 1_000_000:
            raise ValueError("request too large")
        body = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(body, dict):
            raise ValueError("request body must be an object")
        return body

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
            if path in ("/", "/pass189/i2"):
                self._serve_file(WEB_ROOT / "iteration2.html", "text/html; charset=utf-8")
                return
            if path == "/api/pass189/i2/status":
                self._json({"status": "ok", **authority().snapshot()})
                return
            if path == "/api/pass189/i2/profile":
                profile_id = parse_qs(parsed.query).get("profile_id", [""])[0]
                self._json(authority().get_profile(profile_id))
                return
            if path == "/api/pass189/i2/events":
                payload = json.dumps({"event": "pass189.iteration2", "authority": authority().snapshot()}, separators=(",", ":"))
                data = f"event: pass189-iteration2\ndata: {payload}\n\n".encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if path == "/ws/pass189/i2":
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
                self.wfile.write(websocket_frame(json.dumps({"event": "pass189.iteration2.ready", "authority": authority().snapshot()})))
                return
            self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, RuntimeError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        try:
            body = self._body()
            if path == "/api/pass189/i2/calibration/profile":
                self._json(authority().register_profile(body), 201)
                return
            if path == "/api/pass189/i2/calibration/sample":
                profile_id = str(body.pop("profile_id", ""))
                self._json(authority().append_sample(profile_id, body), 201)
                return
            if path == "/api/pass189/i2/calibration/admit":
                self._json(authority().admit_output(
                    str(body.get("profile_id", "")),
                    body.get("requested"),
                    mode=str(body.get("mode", "SIMULATION")),
                    operator_arm_token=str(body.get("operator_arm_token", "")),
                ))
                return
            if path == "/api/pass189/i2/worldline/resolve":
                self._json(authority().resolve_worldlines(
                    body.get("candidates", []),
                    causal_rate=body.get("causal_rate", 1),
                    collision_policy=str(body.get("collision_policy", "REJECT")),
                ))
                return
            if path == "/api/pass189/i2/checkpoint":
                self._json(authority().create_checkpoint(str(body.get("label", ""))), 201)
                return
            if path == "/api/pass189/i2/checkpoint/verify":
                self._json(authority().verify_checkpoint(str(body.get("checkpoint_id", ""))))
                return
            self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, RuntimeError, TypeError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, 400)


def main() -> int:
    global LEDGER
    parser = argparse.ArgumentParser(description="HHS Pass 189 Iteration 2 authority")
    parser.add_argument("--host", default=os.environ.get("HHS189_I2_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("HHS189_I2_PORT", "8190")))
    parser.add_argument("--db", default=os.environ.get("HHS189_I2_DB", "/var/lib/hhs-pass189/iteration2.sqlite3"))
    args = parser.parse_args()
    LEDGER = CalibrationLedger(args.db)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"HHS Pass 189 Iteration 2 listening on http://{args.host}:{args.port} classification={CLASSIFICATION}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        LEDGER.close()
        LEDGER = None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
