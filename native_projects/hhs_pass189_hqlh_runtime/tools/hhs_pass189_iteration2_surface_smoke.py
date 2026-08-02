#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server" / "hhs_pass189_iteration2_server.py"


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def json_request(port: int, method: str, path: str, payload=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    body = None if payload is None else json.dumps(payload)
    headers = {} if payload is None else {"Content-Type": "application/json"}
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    data = response.read()
    connection.close()
    parsed = json.loads(data) if data else {}
    if response.status >= 400:
        raise AssertionError(f"{method} {path} failed: {response.status} {parsed}")
    return response.status, parsed


def main() -> int:
    port = free_port()
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / "iteration2.sqlite3"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "python")
        env["HHS189_I2_QUIET"] = "1"
        process = subprocess.Popen(
            [sys.executable, str(SERVER), "--host", "127.0.0.1", "--port", str(port), "--db", str(db)],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    _, status = json_request(port, "GET", "/api/pass189/i2/status")
                    break
                except Exception:
                    if process.poll() is not None:
                        out, err = process.communicate(timeout=1)
                        raise AssertionError(f"server exited\n{out}\n{err}")
                    time.sleep(0.05)
            else:
                raise AssertionError("iteration 2 server did not become ready")
            assert status["status"] == "ok"
            assert status["deployment_authority"] == "DIGITALOCEAN_SELF_HOSTED"
            assert status["vercel_required"] is False

            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            connection.request("GET", "/pass189/i2/")
            response = connection.getresponse()
            document = response.read().decode("utf-8")
            connection.close()
            assert response.status == 200 and "Pass 189 · Iteration 2" in document

            profile_payload = {
                "device_id": "adc-smoke", "variable": "V", "unit": "volt", "dimension": "electric_potential",
                "scale": {"numerator": 1, "denominator": 1000}, "offset": 0, "raw_min": 0, "raw_max": 5000,
                "canonical_min": 0, "canonical_max": 5, "resolution": {"numerator": 1, "denominator": 1000},
                "tolerance": {"numerator": 1, "denominator": 100}, "required_samples": 3,
                "evidence_class": "SYNTHETIC", "calibration_source": "smoke-fixture", "device_attested": False,
                "operator_arm_hash72": "0" * 72, "created_ns": 1,
            }
            code, profile = json_request(port, "POST", "/api/pass189/i2/calibration/profile", profile_payload)
            assert code == 201 and len(profile["profile_id"]) == 72
            for index, raw in enumerate((1000, 2000, 3000), start=1):
                code, sample = json_request(port, "POST", "/api/pass189/i2/calibration/sample", {
                    "profile_id": profile["profile_id"], "measurement_id": f"smoke-{index}",
                    "measurement_ns": index, "source": "smoke-fixture", "raw": raw,
                    "expected": {"numerator": raw, "denominator": 1000},
                })
                assert code == 201
            assert sample["profile_status"] == "VALIDATED"

            _, simulation = json_request(port, "POST", "/api/pass189/i2/calibration/admit", {
                "profile_id": profile["profile_id"], "requested": 2, "mode": "SIMULATION"
            })
            _, physical = json_request(port, "POST", "/api/pass189/i2/calibration/admit", {
                "profile_id": profile["profile_id"], "requested": 2, "mode": "PHYSICAL", "operator_arm_token": "none"
            })
            assert simulation["authorized"] is True
            assert physical["authorized"] is False

            _, before = json_request(port, "GET", "/api/pass189/i2/status")
            _, worldline = json_request(port, "POST", "/api/pass189/i2/worldline/resolve", {
                "causal_rate": 1,
                "collision_policy": "REJECT",
                "candidates": [
                    {"object_id": "a", "input_receipt_index": before["events"], "position4": [0, 0, 0, 0], "delta4": [2, 1, 0, 0]},
                    {"object_id": "b", "input_receipt_index": before["events"], "position4": [0, 4, 0, 0], "delta4": [2, -1, 0, 0]},
                ],
            })
            assert worldline["joint_admission"] is True
            assert len({item["receipt_index"] for item in worldline["objects"]}) == 1

            code, checkpoint = json_request(port, "POST", "/api/pass189/i2/checkpoint", {"label": "smoke"})
            assert code == 201 and len(checkpoint["checkpoint_id"]) == 72
            _, verified = json_request(port, "POST", "/api/pass189/i2/checkpoint/verify", {"checkpoint_id": checkpoint["checkpoint_id"]})
            assert verified["verified"] is True

            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            connection.request("GET", "/api/pass189/i2/events")
            response = connection.getresponse()
            sse = response.read().decode("utf-8")
            connection.close()
            assert response.status == 200 and "pass189-iteration2" in sse

            key = base64.b64encode(b"pass189-iteration2-smoke").decode("ascii")
            expected_accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()).decode("ascii")
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            connection.request("GET", "/ws/pass189/i2", headers={
                "Upgrade": "websocket", "Connection": "Upgrade", "Sec-WebSocket-Key": key, "Sec-WebSocket-Version": "13"
            })
            response = connection.getresponse()
            response.read()
            assert response.status == 101 and response.getheader("Sec-WebSocket-Accept") == expected_accept
            connection.close()

            print("HHS_PASS_189_ITERATION_2_SURFACE_SMOKE_PASS")
            return 0
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)


if __name__ == "__main__":
    raise SystemExit(main())
