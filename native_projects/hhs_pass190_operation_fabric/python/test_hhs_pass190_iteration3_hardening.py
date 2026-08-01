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
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190_capability import CapabilityTokenError, issue_capability_token, verify_capability_token  # noqa: E402
from hhs_pass190_iteration2 import PersistentAuthorityContext, PersistentStoreError  # noqa: E402
from hhs_pass190_iteration3_hardening import HardenedAuthorityContext  # noqa: E402
from hhs_pass190_iteration3_server import build_server  # noqa: E402

SECRET = "pass190-hardening-test-secret-" + ("z" * 48)


class BufferedSocketReader:
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.buffer = bytearray()

    def _fill(self, size: int) -> None:
        while len(self.buffer) < size:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise AssertionError("unexpected socket closure")
            self.buffer.extend(chunk)

    def read_exact(self, size: int) -> bytes:
        self._fill(size)
        value = bytes(self.buffer[:size])
        del self.buffer[:size]
        return value

    def read_headers(self) -> bytes:
        marker = b"\r\n\r\n"
        while marker not in self.buffer:
            self.buffer.extend(self.sock.recv(4096))
        index = self.buffer.index(marker) + len(marker)
        value = bytes(self.buffer[:index])
        del self.buffer[:index]
        return value

    def read_frame(self) -> dict:
        header = self.read_exact(2)
        length = header[1] & 0x7F
        if length == 126:
            length = struct.unpack("!H", self.read_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self.read_exact(8))[0]
        return json.loads(self.read_exact(length))


def post_json(url: str, payload: dict, headers: dict[str, str] | None = None):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except HTTPError as exc:
        return exc.code, json.loads(exc.read())


class Iteration3HardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "authority.sqlite3"
        self.context = HardenedAuthorityContext(self.db)

    def tearDown(self) -> None:
        try:
            self.context.close()
        except sqlite3.ProgrammingError:
            pass
        self.temp.cleanup()

    def test_signed_capability_signature_scope_and_expiry(self) -> None:
        token = issue_capability_token(
            SECRET,
            principal="operator",
            scopes=["runtime.mutate"],
            ttl_seconds=60,
            now=1_000_000,
            nonce="fixed",
        )
        principal = verify_capability_token(token, SECRET, required_scope="runtime.mutate", now=1_000_010)
        self.assertEqual(principal.principal, "operator")
        self.assertEqual(len(principal.token_hash72), 72)
        with self.assertRaises(CapabilityTokenError):
            verify_capability_token(token + "x", SECRET, now=1_000_010)
        with self.assertRaises(CapabilityTokenError):
            verify_capability_token(token, SECRET, required_scope="runtime.admin", now=1_000_010)
        with self.assertRaises(CapabilityTokenError):
            verify_capability_token(token, SECRET, now=1_000_060)

    def test_incomplete_metadata_is_rejected(self) -> None:
        self.context.invoke("system.status", {})
        self.context.close()
        connection = sqlite3.connect(self.db)
        connection.execute("DELETE FROM authority_meta WHERE key='state_root'")
        connection.commit()
        connection.close()
        with self.assertRaises(PersistentStoreError):
            HardenedAuthorityContext(self.db)
        self.context = HardenedAuthorityContext(Path(self.temp.name) / "replacement.sqlite3")

    def test_event_tamper_is_rejected(self) -> None:
        admitted = self.context.invoke("system.status", {})
        event = self.context.events_after(0)[0]
        self.assertEqual(event["hash72"], admitted.receipt["hash72"])
        self.assertEqual(len(event["event_hash72"]), 72)
        self.context.close()
        connection = sqlite3.connect(self.db)
        payload = json.loads(connection.execute("SELECT payload_json FROM events WHERE sequence=1").fetchone()[0])
        payload["operation_id"] = "tampered.operation"
        connection.execute("UPDATE events SET payload_json=? WHERE sequence=1", (json.dumps(payload),))
        connection.commit()
        connection.close()
        with self.assertRaises(PersistentStoreError):
            HardenedAuthorityContext(self.db)
        self.context = HardenedAuthorityContext(Path(self.temp.name) / "replacement.sqlite3")

    def test_iteration2_database_migrates(self) -> None:
        legacy_path = Path(self.temp.name) / "legacy.sqlite3"
        legacy = PersistentAuthorityContext(legacy_path)
        legacy.invoke("system.status", {})
        legacy.close()
        upgraded = HardenedAuthorityContext(legacy_path)
        report = upgraded.integrity_report()
        self.assertEqual(report["receipt_count"], 1)
        self.assertTrue(report["events_verified"])
        self.assertEqual(len(upgraded.events_after(0)[0]["event_hash72"]), 72)
        upgraded.close()

    def test_http_rejects_unsigned_and_admits_signed_mutation(self) -> None:
        server = build_server(port=0, context=self.context, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        mutation = {"operation_id": "state.counter.advance", "arguments": {"delta": 2}}
        try:
            status, _ = post_json(base + "/api/pass190/invoke", mutation, {"X-HHS-Capability": "runtime.mutate"})
            self.assertEqual(status, 401)
            forged = issue_capability_token("wrong-secret-" + ("q" * 48), principal="attacker", scopes=["runtime.mutate"])
            status, _ = post_json(base + "/api/pass190/invoke", mutation, {"Authorization": "HHS-Capability " + forged})
            self.assertEqual(status, 401)
            token = issue_capability_token(SECRET, principal="operator", scopes=["runtime.mutate"])
            status, payload = post_json(
                base + "/api/pass190/invoke",
                mutation,
                {"Authorization": "HHS-Capability " + token, "X-HHS-Expected-State": self.context.state_root},
            )
            self.assertEqual(status, 200)
            self.assertEqual(payload["result"]["after"], 2)
            openapi = json.loads(urlopen(base + "/openapi.json", timeout=5).read())
            for path in ("/api/pass190/integrity", "/api/pass190/events", "/api/pass190/receipts", "/api/pass190/invoke", "/api/pass190/replay", "/api/pass190/compile-execute"):
                self.assertIn(path, openapi["paths"])
            self.assertIn("HhsCapabilityToken", openapi["components"]["securitySchemes"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.context = HardenedAuthorityContext(self.db)

    def test_websocket_cursor_is_rejected_before_upgrade(self) -> None:
        server = build_server(port=0, context=self.context, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        try:
            sock = socket.create_connection((host, port), timeout=5)
            key = base64.b64encode(os.urandom(16)).decode()
            sock.sendall((
                f"GET /api/pass190/ws?after=-1 HTTP/1.1\r\nHost: {host}:{port}\r\n"
                "Upgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Version: 13\r\n"
                f"Sec-WebSocket-Key: {key}\r\n\r\n"
            ).encode())
            header = BufferedSocketReader(sock).read_headers()
            self.assertIn(b"400", header)
            self.assertNotIn(b"101 Switching Protocols", header)
            sock.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.context = HardenedAuthorityContext(self.db)

    def test_websocket_buffer_preserves_ready_frame(self) -> None:
        server = build_server(port=0, context=self.context, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        try:
            sock = socket.create_connection((host, port), timeout=5)
            key = base64.b64encode(os.urandom(16)).decode()
            sock.sendall((
                f"GET /api/pass190/ws?after=0 HTTP/1.1\r\nHost: {host}:{port}\r\n"
                "Upgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Version: 13\r\n"
                f"Sec-WebSocket-Key: {key}\r\n\r\n"
            ).encode())
            reader = BufferedSocketReader(sock)
            header = reader.read_headers()
            self.assertIn(b"101 Switching Protocols", header)
            expected = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest())
            self.assertIn(expected, header)
            self.assertEqual(reader.read_frame()["event_type"], "channel.ready")
            status, invoked = post_json(base := f"http://{host}:{port}/api/pass190/invoke", {"operation_id": "system.status", "arguments": {}})
            self.assertEqual(status, 200)
            event = reader.read_frame()
            self.assertEqual(event["hash72"], invoked["receipt"]["hash72"])
            self.assertEqual(len(event["event_hash72"]), 72)
            sock.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.context = HardenedAuthorityContext(self.db)

    def test_persistence_failure_returns_503(self) -> None:
        class FailingContext(HardenedAuthorityContext):
            def invoke(self, *args, **kwargs):
                raise sqlite3.OperationalError("simulated storage failure")

        failing = FailingContext(Path(self.temp.name) / "failing.sqlite3")
        server = build_server(port=0, context=failing, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, payload = post_json(
                f"http://127.0.0.1:{server.server_address[1]}/api/pass190/invoke",
                {"operation_id": "system.status", "arguments": {}},
            )
            self.assertEqual(status, 503)
            self.assertEqual(payload["error"], "persistent_authority_unavailable")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
