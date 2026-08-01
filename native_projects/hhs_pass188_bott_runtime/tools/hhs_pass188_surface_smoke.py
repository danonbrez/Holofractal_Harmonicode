#!/usr/bin/env python3
"""Reproducible HTTP, replay, visual-document, SSE, and WebSocket smoke test."""

from __future__ import annotations

import base64
import http.client
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 18_188


def request(method: str, path: str, payload: object | None = None) -> tuple[int, bytes, dict[str, str]]:
    headers: dict[str, str] = {}
    body: bytes | None = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(len(body))
    connection = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    data = response.read()
    normalized = {key.lower(): value for key, value in response.getheaders()}
    connection.close()
    return response.status, data, normalized


def main() -> int:
    environment = os.environ.copy()
    environment["HHS188_QUIET"] = "1"
    process = subprocess.Popen(
        [sys.executable, str(ROOT / "server" / "hhs_pass188_server.py"), "--port", str(PORT)],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        for _ in range(100):
            try:
                status, data, _ = request("GET", "/api/pass188/health")
                if status == 200:
                    break
            except OSError:
                time.sleep(0.02)
        else:
            raise RuntimeError("server did not become ready")

        health = json.loads(data)
        assert health["classification"] == "HHS_PASS_188_RUNTIME_READY"
        assert len(health["surfaces"]) == 8

        status, html, headers = request("GET", "/")
        assert status == 200
        assert headers["content-type"].startswith("text/html")
        assert b"BOTT RUNTIME INSPECTOR" in html
        assert b"Hash72 / Hash216 Receipt" in html

        status, data, _ = request("GET", "/api/pass188/transition?address=0")
        assert status == 200
        receipt = json.loads(data)
        assert receipt["ordered_input_tag"] == "x"
        assert receipt["ordered_output_tag"] == "y"
        assert len(receipt["combined_hash216"]) == 216

        status, data, _ = request("POST", "/api/pass188/replay", receipt)
        assert status == 200
        assert json.loads(data)["verified"] is True

        status, events, headers = request("GET", "/api/pass188/events")
        assert status == 200
        assert headers["content-type"].startswith("text/event-stream")
        assert b"hydration-complete" in events
        assert b"11e3bbf0214751c3" in events

        websocket = socket.create_connection(("127.0.0.1", PORT), timeout=10)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        upgrade = (
            "GET /ws HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{PORT}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        websocket.sendall(upgrade)
        response = websocket.recv(4096)
        websocket.close()
        assert b"101 Switching Protocols" in response
        assert b"Sec-WebSocket-Accept" in response

        print("HHS_PASS_188_HTTP_WEBSOCKET_VISUAL_SURFACES_PASS")
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
