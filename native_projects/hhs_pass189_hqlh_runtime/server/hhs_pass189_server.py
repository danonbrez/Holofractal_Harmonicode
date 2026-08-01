#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import struct
import sys
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass189 import (  # noqa: E402
    CLASSIFICATION,
    CONTEXTUAL_STATES,
    CONTRACT,
    DEFAULT_RUNTIME,
    EquationObject,
    PROJECTED_STATES,
    decode_context,
    exact_ast,
    load_registry,
    node_to_dict,
)

WEB_ROOT = ROOT / "web"


def websocket_frame(payload: str) -> bytes:
    data = payload.encode("utf-8")
    if len(data) < 126:
        return bytes((0x81, len(data))) + data
    if len(data) <= 0xFFFF:
        return bytes((0x81, 126)) + struct.pack("!H", len(data)) + data
    return bytes((0x81, 127)) + struct.pack("!Q", len(data)) + data


class Handler(BaseHTTPRequestHandler):
    server_version = "HHS189/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        if os.environ.get("HHS189_QUIET") != "1":
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
        if length > 2_000_000:
            raise ValueError("request too large")
        return json.loads(self.rfile.read(length) or b"{}")

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
            if path in ("/", "/pass189"):
                self._serve_file(WEB_ROOT / "index.html", "text/html; charset=utf-8")
                return
            if path == "/api/pass189/health":
                self._json({
                    "status": "ok",
                    "contract": CONTRACT,
                    "classification": CLASSIFICATION,
                    "projected_states": PROJECTED_STATES,
                    "contextual_states": CONTEXTUAL_STATES,
                    "deployment_authority": "DIGITALOCEAN_SELF_HOSTED",
                    "vercel_required": False,
                    "runtime": DEFAULT_RUNTIME.snapshot(),
                })
                return
            if path == "/api/pass189/registry":
                self._json(load_registry())
                return
            if path == "/api/pass189/decode":
                query = parse_qs(parsed.query)
                extended = int(query.get("extended", ["0"])[0])
                self._json(asdict(decode_context(extended)))
                return
            if path == "/api/pass189/events":
                payload = json.dumps({"event": "pass189.runtime", "runtime": DEFAULT_RUNTIME.snapshot()}, separators=(",", ":"))
                data = f"event: pass189\ndata: {payload}\n\n".encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if path == "/ws":
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
                self.wfile.write(websocket_frame(json.dumps({"event": "pass189.ready", "runtime": DEFAULT_RUNTIME.snapshot()})))
                return
            self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        try:
            body = self._body()
            if path == "/api/pass189/membranes":
                self._json(exact_ast(str(body.get("source", ""))))
                return
            if path == "/api/pass189/hydrate":
                equation_data = body.get("equation")
                equation = None
                if equation_data:
                    equation = EquationObject.create(
                        str(equation_data.get("source", body.get("source", "x==x"))),
                        units=equation_data.get("units", {}),
                        dimensions=equation_data.get("dimensions", {}),
                        bindings=equation_data.get("bindings", []),
                        calibration=equation_data.get("calibration", []),
                        postulates=equation_data.get("postulates", []),
                    )
                node = DEFAULT_RUNTIME.hydrate(
                    projected=int(body.get("projected", 0)),
                    path=[int(value) for value in body.get("path", [])],
                    source=str(body.get("source", "x==x")),
                    xnor_a=int(body.get("xnor_a", 0)),
                    xnor_b=int(body.get("xnor_b", 0)),
                    postulates=body.get("postulates", []),
                    equation=equation,
                    admit=bool(body.get("admit", True)),
                )
                self._json(node_to_dict(node))
                return
            if path == "/api/pass189/replay":
                self._json({"replay": DEFAULT_RUNTIME.replay(body)})
                return
            if path == "/api/pass189/equation":
                equation = EquationObject.create(
                    str(body.get("source", "x==x")),
                    units=body.get("units", {}),
                    dimensions=body.get("dimensions", {}),
                    bindings=body.get("bindings", []),
                    calibration=body.get("calibration", []),
                    postulates=body.get("postulates", []),
                )
                self._json({**asdict(equation), "projections": equation.projections(DEFAULT_RUNTIME.receipt_index)})
                return
            self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, json.JSONDecodeError, TypeError) as exc:
            self._json({"error": str(exc)}, 400)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("HHS189_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("HHS189_PORT", "8189")))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"HHS Pass 189 listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
