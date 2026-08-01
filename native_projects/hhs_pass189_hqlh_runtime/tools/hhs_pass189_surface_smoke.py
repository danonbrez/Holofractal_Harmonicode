#!/usr/bin/env python3
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
SERVER = ROOT / "server" / "hhs_pass189_server.py"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def request(port: int, method: str, path: str, payload=None, headers=None):
    body = None if payload is None else json.dumps(payload)
    actual_headers = dict(headers or {})
    if body is not None:
        actual_headers["Content-Type"] = "application/json"
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    connection.request(method, path, body=body, headers=actual_headers)
    response = connection.getresponse()
    data = response.read()
    connection.close()
    return response.status, dict(response.getheaders()), data


def wait_ready(port: int) -> None:
    for _ in range(100):
        try:
            status, _, _ = request(port, "GET", "/api/pass189/health")
            if status == 200:
                return
        except OSError:
            pass
        time.sleep(0.05)
    raise RuntimeError("server did not become ready")


def websocket_probe(port: int) -> bytes:
    key = base64.b64encode(b"pass189-websocket-probe").decode("ascii")
    request_bytes = (
        "GET /ws HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    ).encode("ascii")
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(request_bytes)
        return sock.recv(8192)


def main() -> int:
    port = free_port()
    env = os.environ.copy()
    env["HHS189_QUIET"] = "1"
    process = subprocess.Popen(
        [sys.executable, str(SERVER), "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_ready(port)
        status, _, health_data = request(port, "GET", "/api/pass189/health")
        health = json.loads(health_data)
        assert status == 200 and health["deployment_authority"] == "DIGITALOCEAN_SELF_HOSTED"
        assert health["vercel_required"] is False

        status, headers, document = request(port, "GET", "/pass189/")
        assert status == 200 and b"Pass 189 HQLH Runtime" in document
        assert "text/html" in headers["Content-Type"]

        status, _, registry_data = request(port, "GET", "/api/pass189/registry")
        registry = json.loads(registry_data)
        assert status == 200 and registry["implementation_status"] == "EXECUTABLE_VERIFIED"

        source = "List(01,xy)==(yx=01)+(zw*wz)"
        status, _, membrane_data = request(port, "POST", "/api/pass189/membranes", {"source": source})
        membranes = json.loads(membrane_data)
        assert status == 200
        operators = {item["operator"] for item in membranes["membranes"]}
        assert {",", "=", "==", "*"}.issubset(operators)

        status, _, hydrated_data = request(port, "POST", "/api/pass189/hydrate", {
            "projected": 1259711,
            "path": [8, -8, 0, 20],
            "source": source,
            "xnor_a": 1,
            "xnor_b": 1,
            "postulates": [{"name": "bounded-demo", "domain": "projected<1259712", "falsification_test": "coordinate_drift==0"}],
        })
        hydrated = json.loads(hydrated_data)
        assert status == 200 and len(hydrated["v72"]) == 72
        assert len(hydrated["hash72"]) == 72 and len(hydrated["hash216"]) == 216
        assert hydrated["transition_receipt"]["coordinate_drift"] == 0
        assert hydrated["transition_receipt"]["physical_output_authorized"] is False

        status, _, replay_data = request(port, "POST", "/api/pass189/replay", hydrated)
        replay = json.loads(replay_data)
        assert status == 200 and replay["replay"] is True

        status, _, equation_data = request(port, "POST", "/api/pass189/equation", {
            "source": "V==I*R",
            "units": {"V": "volt", "I": "ampere", "R": "ohm"},
            "bindings": [{"variable": "V", "port": "A0"}],
        })
        equation = json.loads(equation_data)
        assert status == 200
        identities = {value["equation_hash72"] for value in equation["projections"].values()}
        assert len(identities) == 1
        assert equation["projections"]["breadboard"]["output_authorized"] is False

        status, headers, event_data = request(port, "GET", "/api/pass189/events")
        assert status == 200 and "text/event-stream" in headers["Content-Type"] and b"event: pass189" in event_data

        websocket = websocket_probe(port)
        assert b"101 Switching Protocols" in websocket
        assert b"Sec-WebSocket-Accept" in websocket

        print("HHS_PASS_189_HQLH_SURFACE_PASS http=1 visual=1 replay=1 sse=1 websocket=1 digitalocean=1")
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        if process.returncode not in (0, -15):
            stdout, stderr = process.communicate()
            print(stdout, file=sys.stderr)
            print(stderr, file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
