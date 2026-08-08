from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.pass213_compiled_rom_routes import (
    configure_pass213_governed_surface,
    router,
)
from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import ZERO_HASH216, hash216
from hhs_backend.runtime.hhs_pass213_governed_surface_v2 import (
    CapabilityAuthority,
    GovernedProjectionStore,
    Pass213GovernedSurface,
    SCOPE_COMPILED_READ,
    SCOPE_INTEGRITY_VERIFY,
    SCOPE_INVENTORY_VERIFY,
    SCOPE_RECEIPT_READ,
    SCOPE_TENSOR_READ,
    SCOPE_TENSOR_VERIFY,
    SCOPE_TIMESTAMP_READ,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass213.cli import main as cli_main

STORE_KEY = bytes((index * 13 + 7) % 256 for index in range(32))
CAPABILITY_KEY = bytes((index * 17 + 9) % 256 for index in range(32))


def h(label: str) -> str:
    return hash216("pass213-api-cli-test", label.encode("utf-8"))


def source_receipt(label: str, root: str) -> str:
    return hash72_digest(
        {"domain": "HHS-P213-ITER9-API-CLI-TEST", "label": label},
        bytes.fromhex(root),
    )


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


class Pass213Iteration9APIAndCLIParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="pass213-api-cli-")
        root = Path(self._temp.name)
        self.surface = Pass213GovernedSurface(
            projection_store=GovernedProjectionStore(
                database_path=root / "surface.sqlite3",
                root_key=STORE_KEY,
            ),
            capability_authority=CapabilityAuthority(
                root_key=CAPABILITY_KEY,
                epoch=9,
            ),
        )
        configure_pass213_governed_surface(self.surface)
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
        self.entry_hash = h("entry")
        self.tensor_root = h("tensor")
        self.anchor_root = h("anchor")
        self.inventory_root = h("inventory")
        self.receipt_object = "pass213-api-cli-receipt"
        self.surface.publish_compiled_rom(
            {
                "entry_hash216": self.entry_hash,
                "operation_id": "HHS_API_CLI_PREVALIDATED_OPERATION",
                "vm81_cell_id": 8,
                "operation_slot": 21,
                "g243_control_id": 144,
                "closure_path_root_hash216": h("compiled-closure"),
                "native_dispatch_id": "native-api-cli-test-v1",
                "kernel_policy_hash216": h("kernel-policy"),
                "parent_hash216": h("parent"),
                "creation_group_sequence": 12,
            },
            published_timestamp_ns=1,
        )
        self.surface.publish_inventory(
            {
                "valid": True,
                "persistent_chain_valid": True,
                "expected_live_count": 1,
                "expected_tombstone_count": 0,
                "actual_protected_count": 1,
                "missing_live_entry_hashes": (),
                "unexpected_protected_entry_hashes": (),
                "inventory_root_hash216": self.inventory_root,
            },
            published_timestamp_ns=2,
        )
        self.surface.publish_timestamp_anchor(
            {
                "intent": {
                    "anchor_sequence": 1,
                    "signed_checkpoint_root_hash216": h("signed-checkpoint"),
                    "verifier_bundle_root_hash216": h("verifier-bundle"),
                    "hash216_lineage_root": h("lineage"),
                    "authority_id": "HHS_API_CLI_TEST_TSA",
                },
                "evidence": {
                    "tsa_policy_oid": "1.2.3.4.1",
                    "gen_time_utc": "2026-08-05T23:30:00.000000Z",
                    "tsa_subject": "CN=HHS API CLI Test TSA",
                    "trust_bundle_sha256": h("trust-bundle"),
                    "request_der_b64": "NOT_PUBLIC",
                    "response_der_b64": "NOT_PUBLIC",
                    "nonce_hex": "0x1234",
                },
                "anchor_root_hash216": self.anchor_root,
            },
            published_timestamp_ns=3,
        )
        tensor_receipt = source_receipt("tensor", self.tensor_root)
        self.surface.publish_moving_tensor(
            {
                "tensor_sequence": 1,
                "genesis_epoch": 9,
                "prior_tensor_root_hash216": ZERO_HASH216,
                "domain_size": 50_388_480,
                "anchor": {
                    "anchor_root_hash216": self.anchor_root,
                    "anchor_sequence": 1,
                },
                "lo_shu_root_hash216": h("lo-shu"),
                "closure_proof": {"closure_root_hash216": h("closure")},
                "tensor_root_hash216": self.tensor_root,
                "receipt_hash72": tensor_receipt,
            },
            published_timestamp_ns=4,
        )
        receipt_root = h("receipt-source")
        self.surface.publish_receipt(
            object_id=self.receipt_object,
            source_root_hash216=receipt_root,
            receipt_hash72=source_receipt("receipt", receipt_root),
            classification="HHS_API_CLI_TEST_RECEIPT",
            published_timestamp_ns=5,
        )
        self.capability = self.surface.capabilities.issue(
            subject="api-cli-test",
            scopes=(
                SCOPE_COMPILED_READ,
                SCOPE_INVENTORY_VERIFY,
                SCOPE_TENSOR_READ,
                SCOPE_TENSOR_VERIFY,
                SCOPE_TIMESTAMP_READ,
                SCOPE_INTEGRITY_VERIFY,
                SCOPE_RECEIPT_READ,
            ),
            ttl_seconds=900,
        )

    def tearDown(self) -> None:
        configure_pass213_governed_surface(None)
        self.surface.close()
        self._temp.cleanup()

    def test_public_status_and_catalog_endpoints(self) -> None:
        for path in (
            "/api/runtime/pass213/status",
            "/api/runtime/pass213/catalog",
            "/api/runtime/compiled-rom/status",
            "/api/runtime/memory-integrity/status",
            "/api/runtime/timestamp-boundary/status",
            "/api/runtime/tensor-lattice/status",
            "/api/runtime/inventory/status",
        ):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, (path, response.text))
            self.assertTrue(response.json()["ok"])
            self.assertIn("runtime_contract", response.json())

    def test_protected_api_routes_require_capability(self) -> None:
        requests = (
            ("POST", "/api/runtime/compiled-rom/lookup", {"object_id": self.entry_hash}),
            ("POST", "/api/runtime/memory-integrity/scan", None),
            ("POST", "/api/runtime/tensor-lattice/verify", None),
            ("POST", "/api/runtime/inventory/verify", None),
        )
        for method, path, payload in requests:
            response = self.client.request(method, path, json=payload)
            self.assertEqual(response.status_code, 403, (path, response.text))
            self.assertFalse(response.json()["detail"]["ok"])

    def test_bearer_and_explicit_capability_headers_are_equivalent(self) -> None:
        bearer = self.client.post(
            "/api/runtime/compiled-rom/lookup",
            json={"object_id": self.entry_hash},
            headers={"Authorization": f"Bearer {self.capability}"},
        )
        explicit = self.client.post(
            "/api/runtime/compiled-rom/lookup",
            json={"object_id": self.entry_hash},
            headers={"X-HHS-Capability": self.capability},
        )
        self.assertEqual(bearer.status_code, 200, bearer.text)
        self.assertEqual(explicit.status_code, 200, explicit.text)
        self.assertEqual(
            strip_runtime_contract(bearer.json()),
            strip_runtime_contract(explicit.json()),
        )

    def test_api_and_cli_return_the_same_governed_payload(self) -> None:
        api = self.client.post(
            "/api/runtime/tensor-lattice/lookup",
            json={"object_id": self.tensor_root},
            headers={"Authorization": f"Bearer {self.capability}"},
        )
        self.assertEqual(api.status_code, 200, api.text)
        output = StringIO()
        exit_code = cli_main(
            [
                "--capability", self.capability,
                "tensor-lattice", "lookup", self.tensor_root,
            ],
            surface=self.surface,
            output=output,
        )
        self.assertEqual(exit_code, 0, output.getvalue())
        cli_payload = json.loads(output.getvalue())
        self.assertEqual(strip_runtime_contract(api.json()), cli_payload)

    def test_cli_rejection_is_structured_and_nonzero(self) -> None:
        output = StringIO()
        exit_code = cli_main(
            ["compiled-rom", "lookup", self.entry_hash],
            surface=self.surface,
            output=output,
        )
        self.assertEqual(exit_code, 2)
        payload = json.loads(output.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(
            payload["schema"],
            "HHS_PASS_213_GOVERNED_CLI_REJECTION_V1",
        )

    def test_local_cli_capability_issuance_is_not_an_api_route(self) -> None:
        output = StringIO()
        exit_code = cli_main(
            [
                "capability", "issue",
                "--subject", "local-operator",
                "--scope", SCOPE_INTEGRITY_VERIFY,
                "--ttl-seconds", "60",
            ],
            surface=self.surface,
            output=output,
        )
        self.assertEqual(exit_code, 0, output.getvalue())
        payload = json.loads(output.getvalue())
        self.assertFalse(payload["network_exposed"])
        self.assertTrue(payload["capability"].startswith("hhs213v1."))
        response = self.client.post("/api/runtime/pass213/capability/issue")
        self.assertEqual(response.status_code, 404)

    def test_openapi_exposes_only_governed_projection_routes(self) -> None:
        paths = set(self.app.openapi()["paths"])
        required = {
            "/api/runtime/pass213/status",
            "/api/runtime/pass213/catalog",
            "/api/runtime/compiled-rom/status",
            "/api/runtime/compiled-rom/lookup",
            "/api/runtime/memory-integrity/status",
            "/api/runtime/memory-integrity/scan",
            "/api/runtime/timestamp-boundary/status",
            "/api/runtime/timestamp-boundary/lookup",
            "/api/runtime/tensor-lattice/status",
            "/api/runtime/tensor-lattice/lookup",
            "/api/runtime/tensor-lattice/verify",
            "/api/runtime/inventory/status",
            "/api/runtime/inventory/verify",
            "/api/runtime/pass213/receipts/{object_id}",
        }
        self.assertTrue(required.issubset(paths), required - paths)
        forbidden_segments = {"execute", "compile", "repair", "delete", "physical-map"}
        for path in paths:
            segments = {segment for segment in path.split("/") if segment}
            self.assertTrue(segments.isdisjoint(forbidden_segments), path)

    def test_api_responses_never_expose_protected_fields(self) -> None:
        forbidden = {
            "secret_key", "private_key", "owner_token", "authentication_tag",
            "carrier_json", "state_json", "trusted_anchor_json",
            "request_der_b64", "response_der_b64", "exact_bytes",
            "payload_bytes", "tensor_seed", "raw_address", "physical_address",
            "arena_id", "native_pointer",
        }
        requests = (
            ("POST", "/api/runtime/compiled-rom/lookup", {"object_id": self.entry_hash}),
            ("POST", "/api/runtime/timestamp-boundary/lookup", {"object_id": self.anchor_root}),
            ("POST", "/api/runtime/tensor-lattice/lookup", {"object_id": self.tensor_root}),
            ("GET", f"/api/runtime/pass213/receipts/{self.receipt_object}", None),
        )
        for method, path, payload in requests:
            response = self.client.request(
                method,
                path,
                json=payload,
                headers={"Authorization": f"Bearer {self.capability}"},
            )
            self.assertEqual(response.status_code, 200, (path, response.text))
            self.assertFalse(recursively_contains_key(response.json(), forbidden), response.json())

    def test_conflicting_capability_headers_fail_closed(self) -> None:
        another = self.surface.capabilities.issue(
            subject="other",
            scopes=(SCOPE_COMPILED_READ,),
            ttl_seconds=60,
        )
        response = self.client.post(
            "/api/runtime/compiled-rom/lookup",
            json={"object_id": self.entry_hash},
            headers={
                "Authorization": f"Bearer {self.capability}",
                "X-HHS-Capability": another,
            },
        )
        self.assertEqual(response.status_code, 401, response.text)
        self.assertEqual(
            response.json()["detail"]["reason"],
            "PASS213_CAPABILITY_HEADERS_CONFLICT",
        )


if __name__ == "__main__":
    unittest.main()
