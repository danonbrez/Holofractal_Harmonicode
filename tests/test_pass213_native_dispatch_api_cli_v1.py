from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.pass213_native_dispatch_routes import (
    configure_pass213_native_dispatch_service,
    router,
)
from hhs_backend.runtime.hhs_pass213_governed_native_dispatch_v1 import (
    DispatchRuntimeState,
    GovernedNativeDispatchAuthority,
    GovernedNativeDispatchService,
    NativeDispatchCapabilityAuthority,
    NativeDispatchKernel,
    NativeDispatchLedger,
    SCOPE_DISPATCH_EXECUTE,
    SCOPE_DISPATCH_READ,
)
from hhs_backend.runtime.hhs_pass213_moving_tensor_v1 import MovingTensorState
from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    protect_compiled_rom_entry,
)
from hhs_runtime.pass213.native_dispatch_cli import main as dispatch_cli_main
from tests.test_pass213_governed_native_dispatch_v1 import (
    ADMISSION_KEY,
    CAPABILITY_KEY,
    LEDGER_KEY,
    MEMORY_KEY,
    TENSOR_KEY,
    baseline_receipt,
    compiled_native_entry,
    h,
)
from tests.test_pass213_moving_tensor_v1 import synthetic_anchor

ROOT = Path(__file__).resolve().parents[1]
SECURE_SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
DISPATCH_SOURCE = ROOT / "native/pass213/hhs_pass213_native_dispatch.c"


def strip_runtime_contract(value: dict[str, object]) -> dict[str, object]:
    result = dict(value)
    result.pop("runtime_contract", None)
    return result


def recursively_contains_key(value: object, forbidden: set[str]) -> bool:
    if isinstance(value, dict):
        return any(
            str(key).lower() in forbidden
            or recursively_contains_key(item, forbidden)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(recursively_contains_key(item, forbidden) for item in value)
    return False


class Pass213Iteration10NativeDispatchAPIAndCLIParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._native_temp = tempfile.TemporaryDirectory(prefix="pass213-iter10-api-native-")
        cls.secure_library = Path(cls._native_temp.name) / "libhhs_pass213_secure_arena.so"
        cls.dispatch_library = Path(cls._native_temp.name) / "libhhs_pass213_native_dispatch.so"
        for source, output in (
            (SECURE_SOURCE, cls.secure_library),
            (DISPATCH_SOURCE, cls.dispatch_library),
        ):
            subprocess.run(
                [
                    "cc", "-std=c11", "-shared", "-fPIC", "-O2",
                    "-Wall", "-Wextra", "-Werror", str(source),
                    "-o", str(output),
                ],
                check=True,
                cwd=ROOT,
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._native_temp.cleanup()

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="pass213-iter10-api-")
        root = Path(self._temp.name)
        self.store = NativeProtectedCompiledROMStore(
            library_path=self.secure_library,
            admission_key=ADMISSION_KEY,
            memory_root_key=MEMORY_KEY,
            owner_id="PASS213_ITER10_API_CLI_TEST",
        )
        self.entry = compiled_native_entry("ITER10_API_CLI_ADD")
        self.store.inspect_correct_protect_and_admit(
            protect_compiled_rom_entry(self.entry, ADMISSION_KEY)
        )
        self.tensor = MovingTensorState.derive(
            root_key=TENSOR_KEY,
            trusted_anchor=synthetic_anchor(1, 12_000_001),
            tensor_sequence=1,
            genesis_epoch=10,
        )
        initial_root = h("api-cli-initial-state")
        initial_receipt = baseline_receipt(initial_root)
        self.state = DispatchRuntimeState(
            next_sequence=1,
            current_state_root_hash216=initial_root,
            previous_receipt_hash72=initial_receipt,
            kernel_policy_hash216=self.entry.kernel_policy_hash216,
            kernel_measurement_hash216=h("api-cli-kernel-measurement"),
            lineage_root_hash216=self.tensor.anchor.hash216_lineage_root,
            tensor_state=self.tensor,
            last_timestamp_ns=self.tensor.anchor.requested_timestamp_ns,
        )
        self.api_ledger = NativeDispatchLedger(
            database_path=root / "api.sqlite3",
            root_key=LEDGER_KEY,
            anchor_state_root_hash216=initial_root,
            anchor_receipt_hash72=initial_receipt,
        )
        self.cli_ledger = NativeDispatchLedger(
            database_path=root / "cli.sqlite3",
            root_key=LEDGER_KEY,
            anchor_state_root_hash216=initial_root,
            anchor_receipt_hash72=initial_receipt,
        )
        kernel = NativeDispatchKernel(library_path=self.dispatch_library)
        issued = time.time_ns()
        self.api_capabilities = NativeDispatchCapabilityAuthority(
            root_key=CAPABILITY_KEY,
            epoch=10,
        )
        self.cli_capabilities = NativeDispatchCapabilityAuthority(
            root_key=CAPABILITY_KEY,
            epoch=10,
        )
        self.execute_token = self.api_capabilities.issue(
            subject="api-cli-operator",
            scopes=(SCOPE_DISPATCH_EXECUTE,),
            ttl_seconds=900,
            issued_timestamp_ns=issued,
            nonce="api-cli-execute",
        )
        self.read_token = self.api_capabilities.issue(
            subject="api-cli-auditor",
            scopes=(SCOPE_DISPATCH_READ,),
            ttl_seconds=900,
            issued_timestamp_ns=issued,
            nonce="api-cli-read",
        )
        self.api_service = GovernedNativeDispatchService(
            authority=GovernedNativeDispatchAuthority(
                protected_store=self.store,
                native_kernel=kernel,
                ledger=self.api_ledger,
                runtime_state=self.state,
            ),
            capabilities=self.api_capabilities,
        )
        self.cli_service = GovernedNativeDispatchService(
            authority=GovernedNativeDispatchAuthority(
                protected_store=self.store,
                native_kernel=kernel,
                ledger=self.cli_ledger,
                runtime_state=self.state,
            ),
            capabilities=self.cli_capabilities,
        )
        configure_pass213_native_dispatch_service(self.api_service)
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
        self.request = {
            "entry_hash216": self.entry.entry_hash216,
            "operation_id": self.entry.operation_id,
            "expected_parent_hash216": initial_root,
            "expected_tensor_root_hash216": self.tensor.tensor_root_hash216,
            "timestamp_ns": self.tensor.anchor.requested_timestamp_ns + 1,
            "hydration_lane": 4,
            "operands": [21, 34],
            "read_set": ["register.a", "register.b"],
            "write_set": ["register.result"],
        }

    def tearDown(self) -> None:
        configure_pass213_native_dispatch_service(None)
        self.api_ledger.close()
        self.cli_ledger.close()
        self.api_capabilities.close()
        self.cli_capabilities.close()
        self.store.close()
        self._temp.cleanup()

    def test_status_is_public_and_transport_safe(self) -> None:
        response = self.client.get("/api/runtime/native-dispatch/status")
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["result"]["physical_mapping_exposed"])
        self.assertIn("runtime_contract", payload)
        output = StringIO()
        exit_code = dispatch_cli_main(
            ["status"],
            service=self.cli_service,
            output=output,
        )
        self.assertEqual(exit_code, 0, output.getvalue())
        self.assertEqual(
            strip_runtime_contract(payload),
            json.loads(output.getvalue()),
        )

    def test_api_and_cli_execute_same_native_request_bit_exactly(self) -> None:
        api = self.client.post(
            "/api/runtime/native-dispatch/execute",
            json=self.request,
            headers={"Authorization": f"Bearer {self.execute_token}"},
        )
        self.assertEqual(api.status_code, 200, api.text)
        output = StringIO()
        args = [
            "--capability", self.execute_token,
            "execute",
            "--entry-hash216", self.request["entry_hash216"],
            "--operation-id", self.request["operation_id"],
            "--expected-parent-hash216", self.request["expected_parent_hash216"],
            "--expected-tensor-root-hash216", self.request["expected_tensor_root_hash216"],
            "--timestamp-ns", str(self.request["timestamp_ns"]),
            "--hydration-lane", str(self.request["hydration_lane"]),
            "--operand", "21",
            "--operand", "34",
            "--read", "register.a",
            "--read", "register.b",
            "--write", "register.result",
        ]
        exit_code = dispatch_cli_main(
            args,
            service=self.cli_service,
            output=output,
        )
        self.assertEqual(exit_code, 0, output.getvalue())
        cli = json.loads(output.getvalue())
        self.assertEqual(strip_runtime_contract(api.json()), cli)
        self.assertEqual(api.json()["result"]["result_values"], [55])

    def test_exact_dispatch_capability_is_required(self) -> None:
        missing = self.client.post(
            "/api/runtime/native-dispatch/execute",
            json=self.request,
        )
        self.assertEqual(missing.status_code, 403, missing.text)
        wrong_scope = self.client.post(
            "/api/runtime/native-dispatch/execute",
            json=self.request,
            headers={"Authorization": f"Bearer {self.read_token}"},
        )
        self.assertEqual(wrong_scope.status_code, 403, wrong_scope.text)
        self.assertIn("SCOPE_DENIED", wrong_scope.text)

    def test_receipt_read_parity_after_execution(self) -> None:
        execute = self.client.post(
            "/api/runtime/native-dispatch/execute",
            json=self.request,
            headers={"X-HHS-Dispatch-Capability": self.execute_token},
        )
        self.assertEqual(execute.status_code, 200, execute.text)
        api = self.client.get(
            "/api/runtime/native-dispatch/receipts/1",
            headers={"Authorization": f"Bearer {self.read_token}"},
        )
        self.assertEqual(api.status_code, 200, api.text)
        self.cli_service.invoke(
            "native-dispatch.execute",
            self.request,
            capability=self.execute_token,
        )
        output = StringIO()
        exit_code = dispatch_cli_main(
            ["--capability", self.read_token, "receipt", "1"],
            service=self.cli_service,
            output=output,
        )
        self.assertEqual(exit_code, 0, output.getvalue())
        self.assertEqual(
            strip_runtime_contract(api.json()),
            json.loads(output.getvalue()),
        )

    def test_local_capability_issuance_has_no_network_route(self) -> None:
        output = StringIO()
        exit_code = dispatch_cli_main(
            [
                "capability", "issue",
                "--subject", "local-operator",
                "--scope", SCOPE_DISPATCH_EXECUTE,
                "--ttl-seconds", "60",
            ],
            service=self.cli_service,
            output=output,
        )
        self.assertEqual(exit_code, 0, output.getvalue())
        payload = json.loads(output.getvalue())
        self.assertFalse(payload["network_exposed"])
        self.assertTrue(payload["capability"].startswith("hhs213d1."))
        response = self.client.post(
            "/api/runtime/native-dispatch/capability/issue"
        )
        self.assertEqual(response.status_code, 404)

    def test_openapi_exposes_execute_but_not_unsafe_mutation_surfaces(self) -> None:
        paths = set(self.app.openapi()["paths"])
        self.assertTrue({
            "/api/runtime/native-dispatch/status",
            "/api/runtime/native-dispatch/execute",
            "/api/runtime/native-dispatch/receipts/{sequence}",
        }.issubset(paths))
        forbidden_segments = {
            "compile", "repair", "delete", "physical-map",
            "protected-memory", "carrier", "der", "capability",
        }
        for path in paths:
            segments = set(path.strip("/").split("/"))
            self.assertTrue(segments.isdisjoint(forbidden_segments), path)

    def test_api_result_does_not_expose_protected_or_physical_fields(self) -> None:
        response = self.client.post(
            "/api/runtime/native-dispatch/execute",
            json=self.request,
            headers={"Authorization": f"Bearer {self.execute_token}"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        forbidden = {
            "secret_key", "private_key", "owner_token", "authentication_tag",
            "carrier_json", "state_json", "payload_bytes", "exact_bytes",
            "physical_route", "physical_address", "tensor_seed", "arena_id",
            "native_pointer", "request_der_b64", "response_der_b64",
        }
        self.assertFalse(
            recursively_contains_key(response.json(), forbidden),
            response.json(),
        )

    def test_conflicting_capability_headers_fail_closed(self) -> None:
        response = self.client.post(
            "/api/runtime/native-dispatch/execute",
            json=self.request,
            headers={
                "Authorization": f"Bearer {self.execute_token}",
                "X-HHS-Dispatch-Capability": self.read_token,
            },
        )
        self.assertEqual(response.status_code, 401, response.text)
        self.assertIn("HEADERS_CONFLICT", response.text)


if __name__ == "__main__":
    unittest.main()
