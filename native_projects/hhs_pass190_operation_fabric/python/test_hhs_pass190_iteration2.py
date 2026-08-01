from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import sqlite3
import struct
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "tools"))

from hhs_pass190_iteration2 import PersistentAuthorityContext, PersistentStoreError
from hhs_pass190_iteration2_server import build_server
from generate_sdks import generate_python, generate_ts


def read_frame(sock: socket.socket):
    header = sock.recv(2)
    if len(header) != 2:
        raise AssertionError("short frame")
    length = header[1] & 0x7F
    if length == 126:
        length = struct.unpack("!H", sock.recv(2))[0]
    elif length == 127:
        length = struct.unpack("!Q", sock.recv(8))[0]
    body = b""
    while len(body) < length:
        body += sock.recv(length - len(body))
    return json.loads(body)


class Iteration2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "authority.sqlite3"
        self.context = PersistentAuthorityContext(self.db)

    def tearDown(self) -> None:
        try:
            self.context.close()
        except sqlite3.ProgrammingError:
            pass
        self.temp.cleanup()

    def test_persistence_and_idempotency_across_restart(self) -> None:
        root = self.context.state_root
        first = self.context.invoke(
            "state.counter.advance",
            {"delta": 3},
            capabilities=["runtime.mutate"],
            expected_state=root,
            idempotency_key="same",
        )
        first_hash = first.receipt["hash72"]
        self.context.close()
        second = PersistentAuthorityContext(self.db)
        self.assertEqual(second.state_root, first.result["state_root"])
        repeated = second.invoke(
            "state.counter.advance",
            {"delta": 3},
            capabilities=["runtime.mutate"],
            idempotency_key="same",
        )
        self.assertEqual(repeated.receipt["hash72"], first_hash)
        next_result = second.invoke(
            "state.counter.advance",
            {"delta": 2},
            capabilities=["runtime.mutate"],
            expected_state=second.state_root,
        )
        self.assertEqual(next_result.result["before"], 3)
        self.assertEqual(next_result.result["after"], 5)
        second.close()
        self.context = PersistentAuthorityContext(self.db)

    def test_chain_integrity_and_receipt_page(self) -> None:
        first = self.context.invoke("system.status", {})
        second = self.context.invoke("system.status", {})
        report = self.context.integrity_report()
        self.assertEqual(report["receipt_count"], 2)
        self.assertEqual(report["chain_head"], second.receipt["hash72"])
        page = self.context.receipts_after(0, 10)
        self.assertEqual([receipt["hash72"] for receipt in page], [first.receipt["hash72"], second.receipt["hash72"]])

    def test_tamper_is_rejected(self) -> None:
        self.context.invoke("system.status", {})
        self.context.close()
        connection = sqlite3.connect(self.db)
        row = connection.execute("SELECT payload_json FROM receipts WHERE receipt_index = 1").fetchone()
        payload = json.loads(row[0])
        payload["result"]["status"] = "tampered"
        connection.execute(
            "UPDATE receipts SET payload_json = ? WHERE receipt_index = 1",
            (json.dumps(payload),),
        )
        connection.commit()
        connection.close()
        with self.assertRaises(PersistentStoreError):
            PersistentAuthorityContext(self.db)
        self.context = PersistentAuthorityContext(Path(self.temp.name) / "replacement.sqlite3")

    def test_events_are_resumable(self) -> None:
        self.context.invoke("system.status", {})
        events = self.context.events_after(0)
        self.assertEqual(events[0]["event_type"], "operation.admitted")
        self.assertEqual(events[0]["sequence"], 1)
        replay = self.context.replay(events[0]["hash72"])
        self.assertTrue(replay.replay_verified)
        more = self.context.events_after(1)
        self.assertEqual(more[0]["event_type"], "operation.replayed")

    def test_sdk_generation(self) -> None:
        operations = json.loads((ROOT / "registry" / "HHS_OPERATION_REGISTRY_V1.json").read_text())["operations"]
        python_sdk = generate_python(operations)
        typescript_sdk = generate_ts(operations)
        self.assertIn("state_counter_advance", python_sdk)
        self.assertIn("websocket(after = 0)", typescript_sdk)

    def test_live_http_and_websocket(self) -> None:
        server = build_server("127.0.0.1", 0, context=self.context)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        try:
            integrity = json.loads(urlopen(f"http://{host}:{port}/api/pass190/integrity").read())
            self.assertEqual(integrity["status"], "ok")

            key = base64.b64encode(os.urandom(16)).decode()
            sock = socket.create_connection((host, port), timeout=5)
            request = (
                f"GET /api/pass190/ws?after=0 HTTP/1.1\r\n"
                f"Host: {host}:{port}\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                "Sec-WebSocket-Version: 13\r\n"
                f"Sec-WebSocket-Key: {key}\r\n\r\n"
            ).encode()
            sock.sendall(request)
            header = b""
            while b"\r\n\r\n" not in header:
                header += sock.recv(4096)
            self.assertIn(b"101 Switching Protocols", header)
            expected = base64.b64encode(
                hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
            )
            self.assertIn(expected, header)
            ready = read_frame(sock)
            self.assertEqual(ready["event_type"], "channel.ready")

            body = json.dumps({"operation_id": "system.status", "arguments": {}}).encode()
            invoke_request = Request(
                f"http://{host}:{port}/api/pass190/invoke",
                data=body,
                headers={"Content-Type": "application/json"},
            )
            invoked = json.loads(urlopen(invoke_request).read())
            self.assertEqual(invoked["operation_id"], "system.status")
            event = read_frame(sock)
            self.assertEqual(event["event_type"], "operation.admitted")
            self.assertEqual(event["hash72"], invoked["receipt"]["hash72"])
            sock.close()

            events = json.loads(urlopen(f"http://{host}:{port}/api/pass190/events?after=0&limit=10").read())
            self.assertTrue(events["events"])
            receipts = json.loads(urlopen(f"http://{host}:{port}/api/pass190/receipts?after=0&limit=10").read())
            self.assertTrue(receipts["receipts"])
            openapi = json.loads(urlopen(f"http://{host}:{port}/openapi.json").read())
            self.assertEqual(openapi["x-hhs-iteration"], 2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.context = PersistentAuthorityContext(self.db)


if __name__ == "__main__":
    unittest.main(verbosity=2)
