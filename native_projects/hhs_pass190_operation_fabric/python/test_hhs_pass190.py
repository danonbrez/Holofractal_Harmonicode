from __future__ import annotations

import json
import sys
import threading
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190 import (  # noqa: E402
    ArgumentValidationError,
    CapabilityDeniedError,
    StateConflictError,
    get_context,
    hash72,
)
from hhs_pass190_server import build_server  # noqa: E402


class Pass190Test(unittest.TestCase):
    def setUp(self) -> None:
        self.context = get_context()
        self.context.reset_for_tests()

    def test_singleton_and_registry_identity(self) -> None:
        self.assertIs(get_context(), get_context())
        self.assertEqual(len(self.context.registry.records), 10)
        self.assertEqual(len(self.context.registry.by_id), 10)
        self.assertTrue(all(len(record.raw["Hash216_identity"]) == 216 for record in self.context.registry.records))

    def test_constructor_shell_python_parity(self) -> None:
        key = "parity-len-1"
        constructor = self.context.invoke_constructor("Len([1,2,3])", idempotency_key=key)
        shell = self.context.invoke_shell("hhs eval 'Len([1,2,3])'", idempotency_key=key)
        python = self.context.invoke_python("builtins.len", {"value": [1, 2, 3]}, idempotency_key=key)
        self.assertEqual(constructor.result, 3)
        self.assertEqual(shell.result, constructor.result)
        self.assertEqual(python.result, constructor.result)
        self.assertEqual(shell.receipt["hash72"], constructor.receipt["hash72"])
        self.assertEqual(python.receipt["hash72"], constructor.receipt["hash72"])

    def test_safe_constructor_rejects_executable_ast(self) -> None:
        with self.assertRaises(ArgumentValidationError):
            self.context.invoke_constructor("Len(__import__('os').listdir('.'))")
        with self.assertRaises(ArgumentValidationError):
            self.context.invoke_constructor("Len([x for x in [1]])")

    def test_exact_pass189_context_decode(self) -> None:
        decoded = self.context.invoke_constructor("DecodePass189Context(51648191)").result
        self.assertEqual(decoded["cell81"], 80)
        self.assertEqual(decoded["operation64"], 63)
        self.assertEqual(decoded["gear243"], 242)
        self.assertEqual(decoded["kappa41"], 40)
        self.assertEqual(decoded["local_k"], 20)

    def test_pure_operations(self) -> None:
        self.assertEqual(self.context.invoke_constructor("Abs(-12)").result, 12)
        self.assertEqual(self.context.invoke_constructor("Sorted([3,1,2], reverse=True)").result, [3, 2, 1])
        self.assertEqual(self.context.invoke_constructor("WithAppended([1,2], 3)").result, [1, 2, 3])
        self.assertEqual(self.context.invoke_constructor("Get({'x':7}, 'x', 0)").result, 7)
        self.assertEqual(self.context.invoke_constructor("Join('-', ['a','b'])").result, "a-b")
        self.assertEqual(self.context.invoke_constructor("GCD(84,30)").result, 6)

    def test_capability_gated_singleton_mutation_and_conflict(self) -> None:
        initial = self.context.state_root
        with self.assertRaises(CapabilityDeniedError):
            self.context.invoke("state.counter.advance", {"delta": 2})
        result = self.context.invoke(
            "state.counter.advance",
            {"delta": 2},
            capabilities={"runtime.mutate"},
            expected_state=initial,
            idempotency_key="counter-2",
        )
        self.assertEqual(result.result["before"], 0)
        self.assertEqual(result.result["after"], 2)
        duplicate = self.context.invoke(
            "state.counter.advance",
            {"delta": 2},
            capabilities={"runtime.mutate"},
            idempotency_key="counter-2",
        )
        self.assertEqual(duplicate.receipt["hash72"], result.receipt["hash72"])
        self.assertEqual(self.context.invoke("system.status", {}).result["receipt_index"], 1)
        with self.assertRaises(StateConflictError):
            self.context.invoke(
                "state.counter.advance",
                {"delta": 1},
                capabilities={"runtime.mutate"},
                expected_state=initial,
            )

    def test_receipt_chain_and_replay(self) -> None:
        first = self.context.invoke_constructor("Abs(-9)")
        second = self.context.invoke_constructor("GCD(18,12)")
        self.assertEqual(second.receipt["predecessor_hash72"], first.receipt["hash72"])
        replay = self.context.replay(first.receipt["hash72"])
        self.assertTrue(replay.replay_verified)
        self.assertEqual(replay.result, 9)
        self.assertEqual(len(first.receipt["hash72"]), 72)
        self.assertEqual(len(first.receipt["hash216"]), 216)

    def test_openapi_generated_from_registry(self) -> None:
        document = self.context.openapi_document()
        self.assertEqual(document["openapi"], "3.1.0")
        operation_ids = {
            operation["operationId"]
            for path in document["paths"].values()
            for operation in path.values()
        }
        self.assertEqual(operation_ids, set(self.context.registry.by_id))

    def test_http_health_invoke_replay_and_openapi(self) -> None:
        server = build_server(port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with urllib.request.urlopen(base + "/api/pass190/health", timeout=5) as response:
                health = json.load(response)
            self.assertEqual(health["result"]["status"], "ok")
            body = json.dumps({"operation_id": "python.abs", "arguments": {"value": -15}}).encode()
            request = urllib.request.Request(
                base + "/api/pass190/invoke",
                data=body,
                headers={"Content-Type": "application/json", "Idempotency-Key": "http-abs"},
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                invoked = json.load(response)
            self.assertEqual(invoked["result"], 15)
            replay_body = json.dumps({"hash72": invoked["receipt"]["hash72"]}).encode()
            replay_request = urllib.request.Request(
                base + "/api/pass190/replay",
                data=replay_body,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(replay_request, timeout=5) as response:
                replay = json.load(response)
            self.assertTrue(replay["replay_verified"])
            with urllib.request.urlopen(base + "/openapi.json", timeout=5) as response:
                openapi = json.load(response)
            self.assertEqual(openapi["x-hhs-contract"], "HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_hash72_payload_sensitivity(self) -> None:
        self.assertNotEqual(hash72("test", {"a": 1}), hash72("test", {"a": 2}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
