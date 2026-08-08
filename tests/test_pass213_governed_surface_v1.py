from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    FULL_HYDRATION_DOMAIN,
    ZERO_HASH216,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_governed_surface_v2 import (
    CapabilityAuthority,
    GovernedProjectionStore,
    KIND_MOVING_TENSOR,
    Pass213GovernedSurface,
    Pass213SurfaceAuthorizationError,
    Pass213SurfaceIntegrityError,
    Pass213SurfaceValidationError,
    SCOPE_COMPILED_READ,
    SCOPE_INTEGRITY_VERIFY,
    SCOPE_INVENTORY_VERIFY,
    SCOPE_RECEIPT_READ,
    SCOPE_TENSOR_READ,
    SCOPE_TENSOR_VERIFY,
    SCOPE_TIMESTAMP_READ,
    assert_public_projection_safe,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest

STORE_KEY = bytes((index * 7 + 3) % 256 for index in range(32))
CAPABILITY_KEY = bytes((index * 11 + 5) % 256 for index in range(32))


def h(label: str) -> str:
    return hash216("pass213-iteration9-test", label.encode("utf-8"))


def source_receipt(label: str, root: str) -> str:
    return hash72_digest(
        {"domain": "HHS-P213-ITER9-TEST-SOURCE", "label": label},
        bytes.fromhex(root),
    )


def contains_forbidden_key(value: object) -> bool:
    forbidden = {
        "root_key", "inventory_key", "deletion_key", "admission_key",
        "memory_root_key", "secret_key", "private_key", "owner_token",
        "authentication_tag", "carrier_json", "state_json",
        "trusted_anchor_json", "request_der_b64", "response_der_b64",
        "exact_bytes", "payload_bytes", "tensor_seed", "raw_address",
        "physical_address", "arena_id", "native_pointer",
    }
    if isinstance(value, dict):
        return any(
            str(key).lower() in forbidden
            or contains_forbidden_key(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(contains_forbidden_key(item) for item in value)
    return False


class Pass213Iteration9GovernedSurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="pass213-surface-")
        self.database = Path(self._temp.name) / "surface.sqlite3"
        self.store = GovernedProjectionStore(
            database_path=self.database,
            root_key=STORE_KEY,
        )
        self.surface = Pass213GovernedSurface(
            projection_store=self.store,
            capability_authority=CapabilityAuthority(
                root_key=CAPABILITY_KEY,
                epoch=9,
            ),
        )
        self.compiled = {
            "entry_hash216": h("compiled-entry"),
            "operation_id": "HHS_TEST_PREVALIDATED_ADD",
            "vm81_cell_id": 5,
            "operation_slot": 17,
            "g243_control_id": 81,
            "closure_path_root_hash216": h("compiled-closure"),
            "native_dispatch_id": "native-test-add-v1",
            "kernel_policy_hash216": h("kernel-policy"),
            "parent_hash216": h("parent"),
            "creation_group_sequence": 4,
        }
        self.inventory = {
            "valid": True,
            "persistent_chain_valid": True,
            "expected_live_count": 1,
            "expected_tombstone_count": 0,
            "actual_protected_count": 1,
            "missing_live_entry_hashes": (),
            "unexpected_protected_entry_hashes": (),
            "inventory_root_hash216": h("inventory"),
        }
        tensor_root = h("tensor")
        self.tensor_source_receipt = source_receipt("tensor", tensor_root)
        self.tensor = {
            "tensor_sequence": 1,
            "genesis_epoch": 9,
            "prior_tensor_root_hash216": ZERO_HASH216,
            "domain_size": FULL_HYDRATION_DOMAIN,
            "anchor": {
                "anchor_root_hash216": h("timestamp-anchor"),
                "anchor_sequence": 1,
            },
            "lo_shu_root_hash216": h("lo-shu"),
            "closure_proof": {"closure_root_hash216": h("closure")},
            "tensor_root_hash216": tensor_root,
            "receipt_hash72": self.tensor_source_receipt,
        }
        self.timestamp = {
            "intent": {
                "anchor_sequence": 1,
                "signed_checkpoint_root_hash216": h("signed-checkpoint"),
                "verifier_bundle_root_hash216": h("verifier-bundle"),
                "hash216_lineage_root": h("lineage"),
                "authority_id": "HHS_TEST_TSA",
            },
            "evidence": {
                "tsa_policy_oid": "1.2.3.4.1",
                "gen_time_utc": "2026-08-05T23:00:00.000000Z",
                "tsa_subject": "CN=HHS Test TSA",
                "trust_bundle_sha256": h("trust-bundle"),
                "request_der_b64": "MUST_NOT_BE_PROJECTED",
                "response_der_b64": "MUST_NOT_BE_PROJECTED",
                "nonce_hex": "0x1234",
            },
            "anchor_root_hash216": h("timestamp-anchor"),
        }

    def tearDown(self) -> None:
        try:
            self.surface.close()
        except Exception:
            pass
        self._temp.cleanup()

    def _all_token(self, *, issued: int | None = None, ttl: int = 900) -> str:
        return self.surface.capabilities.issue(
            subject="iteration9-test",
            scopes=(
                SCOPE_COMPILED_READ,
                SCOPE_INVENTORY_VERIFY,
                SCOPE_TENSOR_READ,
                SCOPE_TENSOR_VERIFY,
                SCOPE_TIMESTAMP_READ,
                SCOPE_INTEGRITY_VERIFY,
                SCOPE_RECEIPT_READ,
            ),
            ttl_seconds=ttl,
            issued_timestamp_ns=issued,
            nonce="iteration9-fixed-nonce" if issued is not None else None,
        )

    def _publish_all(self) -> None:
        self.surface.publish_compiled_rom(self.compiled, published_timestamp_ns=1)
        self.surface.publish_inventory(self.inventory, published_timestamp_ns=2)
        self.surface.publish_timestamp_anchor(self.timestamp, published_timestamp_ns=3)
        self.surface.publish_moving_tensor(self.tensor, published_timestamp_ns=4)
        receipt_root = h("standalone-receipt")
        self.surface.publish_receipt(
            object_id="iteration9-receipt-1",
            source_root_hash216=receipt_root,
            receipt_hash72=source_receipt("receipt", receipt_root),
            classification="HHS_TEST_RECEIPT",
            published_timestamp_ns=5,
        )

    def test_capability_scope_authentication_and_expiry(self) -> None:
        issued = 5_000_000_000
        token = self.surface.capabilities.issue(
            subject="scope-test",
            scopes=(SCOPE_COMPILED_READ,),
            ttl_seconds=10,
            issued_timestamp_ns=issued,
            nonce="scope-test-nonce",
        )
        claims = self.surface.capabilities.validate(
            token,
            required_scope=SCOPE_COMPILED_READ,
            now_timestamp_ns=issued + 1,
        )
        self.assertEqual(claims.subject, "scope-test")
        self.assertEqual(claims.scopes, (SCOPE_COMPILED_READ,))
        with self.assertRaisesRegex(Pass213SurfaceAuthorizationError, "SCOPE_DENIED"):
            self.surface.capabilities.validate(
                token,
                required_scope=SCOPE_TENSOR_READ,
                now_timestamp_ns=issued + 1,
            )
        with self.assertRaisesRegex(Pass213SurfaceAuthorizationError, "EXPIRED"):
            self.surface.capabilities.validate(
                token,
                required_scope=SCOPE_COMPILED_READ,
                now_timestamp_ns=issued + 10_000_000_000,
            )
        altered = token[:-1] + ("0" if token[-1] != "0" else "1")
        with self.assertRaisesRegex(Pass213SurfaceAuthorizationError, "AUTHENTICATION"):
            self.surface.capabilities.validate(
                altered,
                required_scope=SCOPE_COMPILED_READ,
                now_timestamp_ns=issued + 1,
            )

    def test_public_projection_rejects_protected_bytes_float_and_keys(self) -> None:
        for value in (
            {"secret_key": "not-allowed"},
            {"nested": {"request_der_b64": "not-allowed"}},
            {"bytes": b"not-allowed"},
            {"floating": 0.5},
        ):
            with self.subTest(value=value):
                with self.assertRaises(Pass213SurfaceValidationError):
                    assert_public_projection_safe(value)

    def test_publish_lookup_and_public_non_exposure(self) -> None:
        self._publish_all()
        token = self._all_token()
        compiled = self.surface.invoke(
            "compiled.lookup",
            {"object_id": self.compiled["entry_hash216"]},
            capability=token,
        )
        tensor = self.surface.invoke(
            "tensor.lookup",
            {"object_id": self.tensor["tensor_root_hash216"]},
            capability=token,
        )
        timestamp = self.surface.invoke(
            "timestamp.lookup",
            {"object_id": self.timestamp["anchor_root_hash216"]},
            capability=token,
        )
        for response in (compiled, tensor, timestamp):
            self.assertTrue(response["ok"])
            self.assertFalse(contains_forbidden_key(response), response)
        tensor_public = tensor["result"]["public_data"]
        self.assertFalse(tensor_public["physical_mapping_exposed"])
        self.assertFalse(tensor_public["permutation_parameters_exposed"])
        self.assertNotIn("coordinate_map", tensor_public)
        self.assertNotIn("fibonacci_phase", tensor_public)
        self.assertNotIn("lo_shu_grid", tensor_public)
        self.assertNotIn("sudoku", tensor_public)
        timestamp_public = timestamp["result"]["public_data"]
        self.assertFalse(timestamp_public["der_material_exposed"])
        self.assertFalse(timestamp_public["nonce_exposed"])

    def test_source_receipts_are_separate_from_projection_receipts(self) -> None:
        record = self.surface.publish_moving_tensor(self.tensor, published_timestamp_ns=4)
        self.assertNotEqual(record.receipt_hash72, self.tensor_source_receipt)
        self.assertEqual(record.public_data["receipt_hash72"], self.tensor_source_receipt)
        self.assertTrue(self.store.verify_chain())

    def test_public_status_and_catalog_do_not_require_capability(self) -> None:
        status = self.surface.invoke("surface.status")
        catalog = self.surface.invoke("surface.catalog")
        self.assertEqual(status["authorized_scope"], "PUBLIC")
        self.assertTrue(status["result"]["projection_only"])
        self.assertFalse(status["result"]["mutation_authority"])
        exposed = {item["operation"] for item in catalog["result"]["operations"]}
        self.assertNotIn("compiled.execute", exposed)
        self.assertNotIn("compiled.compile", exposed)
        self.assertIn("compiled.execute", catalog["result"]["not_exposed"])
        self.assertIn("tensor.physical-map", catalog["result"]["not_exposed"])

    def test_protected_operation_requires_exact_scope(self) -> None:
        self.surface.publish_compiled_rom(self.compiled)
        with self.assertRaisesRegex(Pass213SurfaceAuthorizationError, "MISSING"):
            self.surface.invoke(
                "compiled.lookup", {"object_id": self.compiled["entry_hash216"]}
            )
        tensor_only = self.surface.capabilities.issue(
            subject="tensor-only",
            scopes=(SCOPE_TENSOR_READ,),
            ttl_seconds=60,
        )
        with self.assertRaisesRegex(Pass213SurfaceAuthorizationError, "SCOPE_DENIED"):
            self.surface.invoke(
                "compiled.lookup",
                {"object_id": self.compiled["entry_hash216"]},
                capability=tensor_only,
            )

    def test_append_only_chain_reopens_with_same_key(self) -> None:
        self._publish_all()
        expected_head = self.store.current_head()
        self.store.close()
        self.surface.capabilities.close()
        reopened_store = GovernedProjectionStore(
            database_path=self.database,
            root_key=STORE_KEY,
        )
        reopened = Pass213GovernedSurface(
            projection_store=reopened_store,
            capability_authority=CapabilityAuthority(root_key=CAPABILITY_KEY, epoch=9),
        )
        self.surface = reopened
        self.store = reopened_store
        self.assertTrue(reopened_store.verify_chain())
        self.assertEqual(reopened_store.current_head(), expected_head)
        self.assertEqual(reopened_store.count(), 5)

    def test_conflicting_projection_is_rejected(self) -> None:
        self.surface.publish_compiled_rom(self.compiled)
        changed = dict(self.compiled)
        changed["operation_id"] = "HHS_CONFLICTING_OPERATION"
        with self.assertRaisesRegex(Pass213SurfaceIntegrityError, "CONFLICT"):
            self.surface.publish_compiled_rom(changed)

    def test_integrity_scan_detects_database_tamper(self) -> None:
        self.surface.publish_inventory(self.inventory)
        token = self._all_token()
        self.assertTrue(
            self.surface.invoke("integrity.scan", capability=token)["result"]["valid"]
        )
        connection = sqlite3.connect(self.database)
        try:
            with connection:
                connection.execute(
                    "UPDATE projection_events SET public_json=? WHERE sequence=1",
                    (json.dumps({"valid": False}, sort_keys=True),),
                )
        finally:
            connection.close()
        with self.assertRaises(Pass213SurfaceIntegrityError):
            self.surface.invoke("integrity.scan", capability=token)

    def test_argument_shape_and_unexposed_mutations_fail_closed(self) -> None:
        with self.assertRaisesRegex(Pass213SurfaceValidationError, "ARGUMENT_SET"):
            self.surface.invoke("surface.status", {"extra": True})
        with self.assertRaisesRegex(Pass213SurfaceValidationError, "NOT_EXPOSED"):
            self.surface.invoke("compiled.execute", {})


if __name__ == "__main__":
    unittest.main()
