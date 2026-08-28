from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

from fastapi.testclient import TestClient

from hhs_backend.public_api_server import create_app
from hhs_runtime.pass190 import Pass190CompletionContext
from hhs_runtime.pass190.completion import PASS190_NATIVE_PYTHON
from hhs_runtime.pass190.python_compat import (
    COVERAGE_MODULES,
    build_python_compatibility_registry,
    compatibility_summary,
)
from hhs_runtime.pass190.shell import ShellUnsupported, lower_shell_command

if str(PASS190_NATIVE_PYTHON) not in sys.path:
    sys.path.insert(0, str(PASS190_NATIVE_PYTHON))
from hhs_pass190_capability import issue_capability_token  # type: ignore


SECRET = "pass190-i136-test-secret-" + ("x" * 40)


class Pass190I136CompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compat = build_python_compatibility_registry()
        cls.summary = compatibility_summary(cls.compat)

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "authority.sqlite3"
        self.context = Pass190CompletionContext(
            database_path=self.database,
            repository_root=Path(__file__).resolve().parents[1],
            hydration_state_root=Path(self.temp.name) / "hydration",
            capability_secret=SECRET,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def token(self, *scopes: str) -> str:
        return issue_capability_token(
            SECRET,
            principal="i136-test",
            scopes=scopes,
            ttl_seconds=900,
            nonce="i136-fixed-nonce",
        )

    def test_python_census_is_complete_classified_and_pinned(self) -> None:
        self.assertEqual(self.compat["python_version"], "3.12")
        self.assertEqual(len(self.compat["coverage_modules"]), len(COVERAGE_MODULES))
        self.assertGreater(self.summary["public_callable_record_count"], 500)
        self.assertEqual(self.summary["unclassified_public_callables"], 0)
        self.assertEqual(self.summary["supported_nucleus_count"], 6)
        records = {
            item["qualified_python_identity"]: item
            for item in self.compat["records"]
        }
        self.assertEqual(records["builtins.len"]["operation_id"], "python.len")
        self.assertEqual(records["math.gcd"]["operation_id"], "math.gcd")
        self.assertEqual(
            records["builtins.eval"]["implementation_class"],
            "SECURITY_RESTRICTED",
        )
        self.assertIsNone(records["builtins.eval"]["operation_id"])
        self.assertEqual(len(self.compat["registry_hash216"]), 216)

    def test_existing_iteration7_is_single_execution_authority(self) -> None:
        status = self.context.status()
        self.assertEqual(status["governed_operation_count"], 42)
        self.assertEqual(status["runtime_mode"], "FULL_CANONICAL_RUNTIME")
        self.assertFalse(status["new_vm81_authority"])
        self.assertFalse(status["new_receipt_clock"])

    def test_python_constructor_shell_and_direct_parity(self) -> None:
        direct = self.context.invoke(
            "python.len",
            {"value": [1, 2, 3]},
            surface="direct",
        )
        python = self.context.invoke_python(
            "builtins.len",
            [[1, 2, 3]],
        )
        constructor = self.context.invoke_constructor(
            "Len(value=[1,2,3])"
        )
        shell = lower_shell_command(
            self.context,
            "hhs invoke python.len '{\"value\":[1,2,3]}'",
        )
        for result in (direct, python, constructor, shell):
            self.assertEqual(result["operation_id"], "python.len")
            self.assertEqual(result["result"], 3)

    def test_mutation_requires_authenticated_capability(self) -> None:
        read_only = Pass190CompletionContext(
            database_path=Path(self.temp.name) / "read-only.sqlite3",
            repository_root=Path(__file__).resolve().parents[1],
            hydration_state_root=Path(self.temp.name) / "hydration-ro",
            capability_secret=None,
        )
        with self.assertRaises(Exception):
            read_only.invoke(
                "state.counter.advance",
                {"delta": 1},
                surface="test",
            )

        token = self.token("runtime.mutate")
        result = self.context.invoke(
            "state.counter.advance",
            {"delta": 2},
            surface="test",
            authorization_token=token,
        )
        self.assertEqual(result["result"]["after"], 2)
        replay = self.context.replay(result["receipt"]["hash72"])
        self.assertTrue(replay["replay_verified"])

    def test_actual_repository_hydration_is_reused_not_reimplemented(self) -> None:
        hydration = self.context.hydration_preview()
        self.assertEqual(hydration["passes_linked"], 191)
        self.assertEqual(hydration["blocker_count"], 0)
        self.assertTrue(hydration["symmetry_valid"])
        self.assertEqual(
            hydration["dqpl_inheritance"]["theorem_status"],
            "OBSTRUCTED",
        )

    def test_shell_is_honest_about_remaining_acceptance_commands(self) -> None:
        doctor = lower_shell_command(self.context, "hhs doctor")
        self.assertTrue(doctor["ok"])
        self.assertEqual(doctor["governed_operation_count"], 42)
        with self.assertRaises(ShellUnsupported) as captured:
            lower_shell_command(self.context, "hhs build")
        self.assertIn("ACCEPTANCE_COMMAND_NOT_YET_BOUND:build", str(captured.exception))

    def test_full_runtime_fastapi_gateway_uses_same_context(self) -> None:
        client = TestClient(create_app(self.context))
        status = client.get("/v1/system/status")
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.json()["runtime_mode"], "FULL_CANONICAL_RUNTIME")
        self.assertEqual(status.json()["governed_operation_count"], 42)

        pure = client.post(
            "/v1/operations/python.len",
            json={"arguments": {"value": [1, 2, 3]}},
        )
        self.assertEqual(pure.status_code, 200)
        self.assertEqual(pure.json()["operation_id"], "python.len")
        self.assertEqual(pure.json()["result"], 3)

        denied = client.post(
            "/v1/operations/state.counter.advance",
            json={"arguments": {"delta": 1}},
        )
        self.assertEqual(denied.status_code, 401)

        token = self.token("runtime.mutate")
        admitted = client.post(
            "/v1/operations/state.counter.advance",
            headers={"Authorization": "HHS-Capability " + token},
            json={"arguments": {"delta": 1}},
        )
        self.assertEqual(admitted.status_code, 200)
        self.assertEqual(admitted.json()["result"]["after"], 1)

        float_rejected = client.post(
            "/v1/operations/python.abs",
            json={"arguments": {"value": 1.25}},
        )
        self.assertEqual(float_rejected.status_code, 400)
        self.assertIn("FLOAT_CANONICAL_TRANSPORT_REJECTED", float_rejected.json()["detail"])

        document = client.get("/v1/registry/openapi")
        self.assertEqual(document.status_code, 200)
        self.assertEqual(document.json()["x-hhs-operation-count"], 42)
        self.assertEqual(
            document.json()["x-hhs-runtime-mode"],
            "FULL_CANONICAL_RUNTIME",
        )

    def test_websocket_is_receipt_projection_not_authority(self) -> None:
        client = TestClient(create_app(self.context))
        self.context.invoke("python.abs", {"value": -3}, surface="test")
        with client.websocket_connect("/v1/receipts/ws") as socket:
            snapshot = socket.receive_json()
        self.assertEqual(snapshot["schema"], "HHS_PASS_190_RECEIPT_STREAM_SNAPSHOT_V1")
        self.assertGreaterEqual(len(snapshot["receipts"]), 1)
        self.assertFalse(snapshot["canonical_state_fabricated"])


if __name__ == "__main__":
    unittest.main()
