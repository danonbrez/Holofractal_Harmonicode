from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path

from hhs_backend.runtime.hhs_pass198_operation_calibration_registry_v1 import (
    BUILTIN_ADAPTER,
    BUILTIN_PASS197_SPEC,
    REPAIR_SCHEMA,
    OperationSpec,
    Pass198OperationCalibrationRegistry,
    Pass198RegistryError,
)


def _small_config(value: str = "1", exponent: int = 0) -> dict:
    return {
        "x_values": [value],
        "y_values": [value],
        "xy_symbol_values": [exponent],
        "include_domain_rejections": True,
        "full_replay": True,
    }


def _custom_operation(operation_id: str) -> dict:
    payload = BUILTIN_PASS197_SPEC.payload()
    payload.pop("spec_hash72", None)
    payload["operation_id"] = operation_id
    payload["display_name"] = f"Custom {operation_id}"
    return payload


class Pass198I128RepairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.registry = Pass198OperationCalibrationRegistry(state_root=self.temp.name)

    def tearDown(self) -> None:
        self.registry.close()
        self.temp.cleanup()

    def test_01_full_replay_is_required_before_simplification_proof(self) -> None:
        run = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {
                "x_values": ["-1", "1"],
                "y_values": ["-1", "1"],
                "xy_symbol_values": [0],
                "full_replay": False,
            },
            vm81_receipt_hash72="1" * 72,
        )
        self.assertEqual(run["status"], "REJECTED")
        self.assertFalse(run["promotion_grade_coverage"])
        self.assertFalse(run["replay"]["full_replay_executed"])
        self.assertEqual(self.registry.list_simplifications(), [])

    def test_02_partial_domain_execution_cannot_claim_full_tree_envelope(self) -> None:
        run = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {
                "x_values": ["0", "1"],
                "y_values": ["0", "1"],
                "xy_symbol_values": [0],
                "include_domain_rejections": False,
                "full_replay": True,
            },
            vm81_receipt_hash72="2" * 72,
        )
        self.assertEqual(run["status"], "REJECTED")
        self.assertEqual(run["summary"]["evaluated_parameter_states"], 1)
        self.assertFalse(run["promotion_grade_coverage"])
        self.assertEqual(self.registry.list_simplifications(), [])

    def test_03_and_11_generic_axes_and_adapter_spoof_fail_closed(self) -> None:
        payload = _custom_operation("custom.axis.operation")
        payload["adapter"] = BUILTIN_ADAPTER
        payload["parameter_axes"] = {"temperature": [1, 2, 3]}
        registered = self.registry.register_operation(payload)
        self.assertNotEqual(registered["spec_hash72"], BUILTIN_PASS197_SPEC.spec_hash72)
        with self.assertRaisesRegex(Pass198RegistryError, "approved executable adapter/specification"):
            self.registry.parameter_tree("custom.axis.operation")
        with self.assertRaisesRegex(Pass198RegistryError, "approved executable adapter/specification"):
            self.registry.run_operation("custom.axis.operation")

    def test_04_registration_receipt_is_persisted_in_document_and_event(self) -> None:
        receipt = "3" * 72
        document = self.registry.register_operation(
            _custom_operation("custom.receipt.operation"),
            source="api.runtime.calibration_registry.operations.register",
            vm81_receipt_hash72=receipt,
        )
        self.assertEqual(document["registration_vm81_receipt_hash72"], receipt)
        persisted = self.registry.get_operation("custom.receipt.operation")
        self.assertEqual(persisted["registration_vm81_receipt_hash72"], receipt)
        rows = list(self.registry._db.execute("SELECT payload_json FROM events ORDER BY seq"))
        event = json.loads(rows[-1][0])
        self.assertEqual(event["payload"]["vm81_receipt_hash72"], receipt)

    def test_05_nested_float_identity_is_rejected(self) -> None:
        payload = _custom_operation("custom.float.operation")
        payload["cost_model"] = {"exact": {"ratio": 0.5}}
        with self.assertRaisesRegex(ValueError, "floating-point"):
            OperationSpec.create(payload)

    def test_06_idempotent_registration_is_atomic_across_connections(self) -> None:
        second = Pass198OperationCalibrationRegistry(state_root=self.temp.name)
        payload = _custom_operation("custom.concurrent.operation")
        barrier = threading.Barrier(2)
        results: list[str] = []
        errors: list[BaseException] = []

        def register(registry: Pass198OperationCalibrationRegistry) -> None:
            try:
                barrier.wait(timeout=5)
                doc = registry.register_operation(payload, source="concurrency-test", idempotent=True)
                results.append(doc["spec_hash72"])
            except BaseException as exc:  # test records either thread failure explicitly
                errors.append(exc)

        threads = [threading.Thread(target=register, args=(registry,)) for registry in (self.registry, second)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        second.close()
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 2)
        self.assertEqual(len(set(results)), 1)
        count = self.registry._db.execute(
            "SELECT COUNT(*) FROM operations WHERE operation_id='custom.concurrent.operation'"
        ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_07_normalized_identifier_updates_exact_persistent_row(self) -> None:
        first = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {"x_values": ["1"], "y_values": ["1"], "xy_symbol_values": [0]},
            vm81_receipt_hash72="4" * 72,
        )
        second = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {"x_values": ["2"], "y_values": ["1"], "xy_symbol_values": [1]},
            vm81_receipt_hash72="5" * 72,
        )
        proof = self.registry.list_simplifications()[0]
        padded = f"  {proof['simplification_id']}  "
        promoted = self.registry.promote_simplification(
            padded,
            "CROSS_WORKLOAD_VERIFIED",
            evidence_run_ids=[first["run_id"], second["run_id"]],
            vm81_receipt_hash72="6" * 72,
        )
        self.assertEqual(promoted["status"], "CROSS_WORKLOAD_VERIFIED")
        self.assertEqual(self.registry.list_simplifications()[0]["status"], "CROSS_WORKLOAD_VERIFIED")
        revoked = self.registry.revoke_simplification(
            padded,
            {"classification": "I128_TEST"},
            vm81_receipt_hash72="7" * 72,
        )
        self.assertEqual(revoked["status"], "REVOKED")
        self.assertEqual(self.registry.list_simplifications()[0]["status"], "REVOKED")

    def test_08_concurrent_same_stage_promotion_commits_once(self) -> None:
        first = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate", _small_config("1", 0), vm81_receipt_hash72="8" * 72
        )
        second_run = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate", _small_config("2", 1), vm81_receipt_hash72="9" * 72
        )
        proof = self.registry.list_simplifications()[0]
        sid = proof["simplification_id"]
        second_registry = Pass198OperationCalibrationRegistry(state_root=self.temp.name)
        barrier = threading.Barrier(2)
        successes: list[str] = []
        failures: list[str] = []

        def promote(registry: Pass198OperationCalibrationRegistry) -> None:
            try:
                barrier.wait(timeout=5)
                result = registry.promote_simplification(
                    sid,
                    "CROSS_WORKLOAD_VERIFIED",
                    evidence_run_ids=[first["run_id"], second_run["run_id"]],
                    vm81_receipt_hash72="a" * 72,
                )
                successes.append(result["status"])
            except Pass198RegistryError as exc:
                failures.append(str(exc))

        threads = [threading.Thread(target=promote, args=(registry,)) for registry in (self.registry, second_registry)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        second_registry.close()
        self.assertEqual(successes, ["CROSS_WORKLOAD_VERIFIED"])
        self.assertEqual(len(failures), 1)
        events = [
            json.loads(row[0])
            for row in self.registry._db.execute("SELECT payload_json FROM events ORDER BY seq")
        ]
        promotions = [
            item for item in events
            if item["event_type"] == "SIMPLIFICATION_PROMOTED"
            and item["payload"]["simplification_id"] == sid
        ]
        self.assertEqual(len(promotions), 1)

    def test_09_checkpoint_identity_is_independent_of_new_tick_receipt(self) -> None:
        config = _small_config("1", 0)
        first = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate", config, vm81_receipt_hash72="b" * 72
        )
        second = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate", config, vm81_receipt_hash72="c" * 72
        )
        self.assertNotEqual(first["run_id"], second["run_id"])
        self.assertEqual(first["checkpoint_identity_hash72"], second["checkpoint_identity_hash72"])
        self.assertTrue(first["checkpoint_receipt_independent"])
        runs_root = Path(self.temp.name) / "runs"
        self.assertEqual(len([item for item in runs_root.iterdir() if item.is_dir()]), 1)

    def test_10_same_workload_under_two_receipts_is_not_cross_workload(self) -> None:
        config = _small_config("1", 0)
        first = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate", config, vm81_receipt_hash72="d" * 72
        )
        second = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate", config, vm81_receipt_hash72="e" * 72
        )
        proof = self.registry.list_simplifications()[0]
        self.assertEqual(proof["verification_run_count"], 2)
        self.assertEqual(proof["verification_workload_count"], 1)
        with self.assertRaisesRegex(Pass198RegistryError, "distinct verified workloads"):
            self.registry.promote_simplification(
                proof["simplification_id"],
                "CROSS_WORKLOAD_VERIFIED",
                evidence_run_ids=[first["run_id"], second["run_id"]],
                vm81_receipt_hash72="f" * 72,
            )

    def test_12_cost_metadata_does_not_claim_aggregate_saving_per_simplification(self) -> None:
        self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {"x_values": ["-1", "1"], "y_values": ["-1", "1"], "xy_symbol_values": [0]},
            vm81_receipt_hash72="0" * 72,
        )
        proofs = self.registry.list_simplifications()
        self.assertEqual(len(proofs), 4)
        seen_names = set()
        for proof in proofs:
            cost = proof["cost"]
            self.assertEqual(cost["claim_scope"], "AGGREGATE_REPORT_REFERENCE_ONLY")
            self.assertEqual(cost["measurement_status"], "UNMEASURED_PER_SIMPLIFICATION")
            self.assertFalse(cost["promotion_grade_cost_claim"])
            self.assertEqual(cost["simplification_name"], proof["name"])
            self.assertNotIn("saved", cost)
            self.assertIn("saved", cost["aggregate_reference"])
            seen_names.add(cost["simplification_name"])
        self.assertEqual(len(seen_names), 4)

    def test_status_exposes_i128_repair_boundary(self) -> None:
        status = self.registry.status()
        self.assertEqual(status["repair_schema"], REPAIR_SCHEMA)
        self.assertTrue(status["executable_adapter_requires_exact_builtin_specification"])
        self.assertTrue(status["promotion_requires_distinct_workload_identities"])
        self.assertFalse(status["compiler_auto_promotion"])
        self.assertFalse(status["runtime_auto_admission"])


if __name__ == "__main__":
    unittest.main()
