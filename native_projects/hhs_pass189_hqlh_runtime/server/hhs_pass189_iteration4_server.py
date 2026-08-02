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

from hhs_pass189_iteration4 import DriverProvenanceAuthority, sign_manifest  # noqa: E402

WEB_ROOT = ROOT / "web"
DATABASE = Path(os.environ.get("HHS189_I4_DB", "/var/lib/hhs-pass189/iteration4.sqlite3"))
QUARANTINE = Path(os.environ.get("HHS189_I4_QUARANTINE", "/var/lib/hhs-pass189/iteration4-quarantine"))
AUTHORITY = DriverProvenanceAuthority(DATABASE, quarantine_directory=QUARANTINE)


def websocket_frame(payload: str) -> bytes:
    data = payload.encode("utf-8")
    if len(data) < 126:
        return bytes((0x81, len(data))) + data
    if len(data) <= 0xFFFF:
        return bytes((0x81, 126)) + struct.pack("!H", len(data)) + data
    return bytes((0x81, 127)) + struct.pack("!Q", len(data)) + data


class Handler(BaseHTTPRequestHandler):
    server_version = "HHS189-I4/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        if os.environ.get("HHS189_I4_QUIET") != "1":
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
        if length > 4_000_000:
            raise ValueError("request too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def _serve_html(self) -> None:
        data = (WEB_ROOT / "iteration4.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        try:
            if path in ("/", "/pass189/i4"):
                self._serve_html()
                return
            if path == "/api/pass189/i4/status":
                self._json(AUTHORITY.status())
                return
            if path == "/api/pass189/i4/package":
                package_id = parse_qs(parsed.query).get("package_id", [""])[0]
                self._json(AUTHORITY.get_package(package_id))
                return
            if path == "/api/pass189/i4/events":
                payload = json.dumps({"event": "pass189.i4", "runtime": AUTHORITY.status()}, separators=(",", ":"))
                data = f"event: pass189-i4\ndata: {payload}\n\n".encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if path == "/ws/pass189/i4":
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
                self.wfile.write(websocket_frame(json.dumps({"event": "pass189.i4.ready", "runtime": AUTHORITY.status()})))
                return
            self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        try:
            body = self._body()
            if path == "/api/pass189/i4/trust/register":
                key = base64.b64decode(str(body.get("key_base64", "")), validate=True)
                self._json(AUTHORITY.register_trust_root(str(body.get("signer_id", "")), key, created_ns=body.get("created_ns")))
                return
            if path == "/api/pass189/i4/trust/revoke":
                self._json(AUTHORITY.revoke_trust_root(str(body.get("signer_id", "")), created_ns=body.get("created_ns")))
                return
            if path == "/api/pass189/i4/package/sign":
                key = base64.b64decode(str(body.get("key_base64", "")), validate=True)
                self._json({"signature_hex": sign_manifest(body.get("manifest", {}), key)})
                return
            if path == "/api/pass189/i4/package/ingest":
                payload = base64.b64decode(str(body.get("payload_base64", "")), validate=True)
                key = base64.b64decode(str(body.get("verification_key_base64", "")), validate=True)
                self._json(AUTHORITY.ingest_package(
                    str(body.get("package_id", "")), body.get("manifest", {}), payload,
                    str(body.get("signature_hex", "")), key,
                ))
                return
            if path == "/api/pass189/i4/conformance":
                self._json(AUTHORITY.record_conformance(body))
                return
            if path == "/api/pass189/i4/promote":
                self._json(AUTHORITY.promote(body))
                return
            if path == "/api/pass189/i4/promotion/revoke":
                self._json(AUTHORITY.revoke_promotion(str(body.get("promotion_id", "")), created_ns=body.get("created_ns")))
                return
            if path == "/api/pass189/i4/rollback":
                self._json(AUTHORITY.rollback(str(body.get("promotion_id", "")), created_ns=body.get("created_ns")))
                return
            if path == "/api/pass189/i4/chain/verify":
                self._json(AUTHORITY.verify_chain())
                return
            if path == "/api/pass189/i4/checkpoint":
                self._json(AUTHORITY.checkpoint(str(body.get("path", "")), str(body.get("checkpoint_id", "")), created_ns=body.get("created_ns")))
                return
            if path == "/api/pass189/i4/checkpoint/verify":
                self._json(AUTHORITY.verify_checkpoint(
                    str(body.get("path", "")), str(body.get("digest_sha256", "")),
                    int(body.get("captured_sequence", 0)), str(body.get("captured_root_hash72", "")),
                ))
                return
            self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, base64.binascii.Error) as exc:
            self._json({"error": str(exc)}, 400)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("HHS189_I4_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("HHS189_I4_PORT", "8192")))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"HHS Pass 189 Iteration 4 listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        AUTHORITY.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
