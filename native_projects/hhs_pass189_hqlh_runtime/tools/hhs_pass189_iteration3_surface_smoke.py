#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server" / "hhs_pass189_iteration3_server.py"


def request(url: str, body: dict | None = None) -> tuple[int, bytes, dict]:
    data = None if body is None else json.dumps(body).encode()
    headers = {} if body is None else {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        port = 18191
        env = os.environ.copy()
        env["HHS189_I3_QUIET"] = "1"
        process = subprocess.Popen([
            sys.executable, str(SERVER), "--host", "127.0.0.1", "--port", str(port),
            "--database", str(root / "authority.sqlite3"), "--state-directory", str(root / "state")
        ], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        base = f"http://127.0.0.1:{port}"
        try:
            for _ in range(50):
                try:
                    status, _, _ = request(base + "/api/pass189/i3/status")
                    if status == 200:
                        break
                except OSError:
                    pass
                time.sleep(0.05)
            else:
                raise AssertionError("server did not start")
            status, payload, _ = request(base + "/api/pass189/i3/status")
            health = json.loads(payload)
            assert status == 200 and health["status"] == "ok"
            assert health["vercel_required"] is False and health["actual_physical_dispatch"] is False
            status, html, _ = request(base + "/pass189/i3/")
            assert status == 200 and b"Iteration 3" in html and b"LOOPBACK" in html
            adapter = {
                "adapter_id": "smoke-loop", "device_id": "smoke-device", "driver_kind": "LOOPBACK", "unit": "volt",
                "minimum": 0, "maximum": 5, "allowed_operations": ["SET"], "watchdog_timeout_ms": 100,
                "max_commands_per_lease": 2, "software_attested": True, "created_ns": 1000,
            }
            status, payload, _ = request(base + "/api/pass189/i3/adapter/register", adapter)
            assert status == 201 and len(json.loads(payload)["adapter_hash72"]) == 72
            lease = {
                "lease_id": "smoke-lease", "adapter_id": "smoke-loop", "issued_ns": 2000, "expires_ns": 10_000_000_000,
                "max_commands": 2, "allowed_operations": ["SET"], "arm_token_hash72": "a" * 72,
            }
            status, payload, _ = request(base + "/api/pass189/i3/lease/issue", lease)
            assert status == 201
            command = {
                "command_id": "smoke-command", "lease_id": "smoke-lease", "sequence": 1, "operation": "SET",
                "value": {"numerator": 5, "denominator": 2}, "unit": "volt", "issued_ns": 3000,
                "arm_token_hash72": "a" * 72,
                "candidate": {"candidate_hash72": "b" * 72, "profile_id": "measured-profile", "physical_output_authorized": True,
                              "dispatch_class": "CANDIDATE_ONLY_NO_DEVICE_DRIVER", "candidate_receipt_index": 7},
            }
            status, payload, _ = request(base + "/api/pass189/i3/command/prepare", command)
            assert status == 201 and json.loads(payload)["status"] == "PREPARED"
            status, payload, _ = request(base + "/api/pass189/i3/command/execute", {"command_id": "smoke-command", "execution_ns": 4000})
            trace = json.loads(payload)
            assert status == 200 and trace["dispatch_status"] == "SOFTWARE_TEST_DRIVER_ONLY"
            assert trace["hardware_measurement"] is False and trace["residual"] == {"numerator": 0, "denominator": 1}
            status, payload, _ = request(base + "/api/pass189/i3/chain/verify", {})
            assert status == 200 and json.loads(payload)["valid"] is True
            status, payload, headers = request(base + "/api/pass189/i3/events")
            assert status == 200 and headers["Content-Type"].startswith("text/event-stream") and b"pass189-i3" in payload
            key = base64.b64encode(b"pass189-iteration3-smoke-key").decode()
            with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
                handshake = (
                    "GET /ws/pass189/i3 HTTP/1.1\r\nHost: 127.0.0.1\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                    f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
                ).encode()
                sock.sendall(handshake)
                data = sock.recv(4096)
                assert b"101 Switching Protocols" in data
            print("HHS_PASS_189_ITERATION_3_HTTP_SSE_WEBSOCKET_VISUAL_PASS")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            if process.returncode not in (0, -15):
                out, err = process.communicate()
                raise AssertionError(f"server failed: {out!r} {err!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
