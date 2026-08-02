import tempfile
import unittest

from hhs_backend.runtime.hhs_pass198_operation_calibration_registry_v1 import (
    BUILTIN_PASS197_SPEC,
    Pass198OperationCalibrationRegistry,
    Pass198RegistryError,
)


class Pass198OperationCalibrationRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.registry = Pass198OperationCalibrationRegistry(state_root=self.temp.name)

    def tearDown(self):
        self.registry.close()
        self.temp.cleanup()

    def test_builtin_operation_and_default_tree(self):
        status = self.registry.status()
        self.assertTrue(status["ok"])
        self.assertEqual(status["operation_count"], 1)
        operation = self.registry.get_operation("pass197.reciprocal_matrix_gate")
        self.assertEqual(operation["spec_hash72"], BUILTIN_PASS197_SPEC.spec_hash72)
        tree = self.registry.parameter_tree("pass197.reciprocal_matrix_gate")
        self.assertEqual(tree["state_count"], 405)
        self.assertEqual(tree["eligible_state_count"], 320)
        self.assertEqual(tree["rejected_state_count"], 85)
        self.assertEqual(len(tree["tree_hash72"]), 72)

    def test_run_records_proof_carrying_simplifications(self):
        run = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {
                "x_values": ["-1", "0", "1"],
                "y_values": ["-1", "0", "1"],
                "xy_symbol_values": [0],
            },
            vm81_receipt_hash72="1" * 72,
        )
        self.assertEqual(run["status"], "CLOSED")
        self.assertEqual(run["summary"]["evaluated_parameter_states"], 9)
        self.assertEqual(run["summary"]["admitted_parameter_states"], 4)
        self.assertEqual(run["summary"]["domain_rejected_parameter_states"], 5)
        self.assertEqual(run["summary"]["mismatch_parameter_states"], 0)
        simplifications = self.registry.list_simplifications("pass197.reciprocal_matrix_gate")
        self.assertEqual(len(simplifications), 4)
        for item in simplifications:
            self.assertEqual(item["status"], "ENVELOPE_VERIFIED")
            self.assertEqual(item["verification_run_count"], 1)
            self.assertEqual(item["run_ids"], [run["run_id"]])
            self.assertEqual(item["counterexample_search"]["mismatch_parameter_states"], 0)
            self.assertTrue(item["retained_witnesses"])
            self.assertTrue(item["revocation_conditions"])

    def test_two_distinct_runs_enable_one_stage_promotion(self):
        first = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {"x_values": ["-1", "1"], "y_values": ["-1", "1"], "xy_symbol_values": [0]},
            vm81_receipt_hash72="2" * 72,
        )
        second = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {"x_values": ["-2", "2"], "y_values": ["-1/2", "1/2"], "xy_symbol_values": [1]},
            vm81_receipt_hash72="3" * 72,
        )
        simplification = self.registry.list_simplifications()[0]
        self.assertEqual(simplification["verification_run_count"], 2)
        promoted = self.registry.promote_simplification(
            simplification["simplification_id"],
            "CROSS_WORKLOAD_VERIFIED",
            evidence_run_ids=[first["run_id"], second["run_id"]],
            vm81_receipt_hash72="4" * 72,
        )
        self.assertEqual(promoted["status"], "CROSS_WORKLOAD_VERIFIED")
        with self.assertRaises(Pass198RegistryError):
            self.registry.promote_simplification(
                simplification["simplification_id"],
                "RUNTIME_ADMITTED",
                evidence_run_ids=[first["run_id"], second["run_id"]],
            )

    def test_promotion_rejects_unknown_evidence(self):
        self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {"x_values": [1], "y_values": [1], "xy_symbol_values": [0]},
        )
        simplification = self.registry.list_simplifications()[0]
        with self.assertRaises(Pass198RegistryError):
            self.registry.promote_simplification(
                simplification["simplification_id"],
                "CROSS_WORKLOAD_VERIFIED",
                evidence_run_ids=["f" * 72, "e" * 72],
            )

    def test_revocation_is_persistent_and_fail_closed(self):
        self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {"x_values": [1], "y_values": [1], "xy_symbol_values": [0]},
        )
        simplification = self.registry.list_simplifications()[0]
        revoked = self.registry.revoke_simplification(
            simplification["simplification_id"],
            {"classification": "COUNTEREXAMPLE", "state_hash72": "a" * 72},
            vm81_receipt_hash72="5" * 72,
        )
        self.assertEqual(revoked["status"], "REVOKED")
        self.assertEqual(self.registry.list_simplifications()[0]["status"], "REVOKED")
        self.assertTrue(self.registry.verify_event_chain()["ok"])

    def test_float_parameter_ingress_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.parameter_tree(
                "pass197.reciprocal_matrix_gate",
                {"x_values": [0.5], "y_values": [1], "xy_symbol_values": [0]},
            )

    def test_operation_identity_is_immutable(self):
        payload = BUILTIN_PASS197_SPEC.payload()
        payload["display_name"] = "Mutated identity"
        with self.assertRaises(Pass198RegistryError):
            self.registry.register_operation(payload)

    def test_database_reopen_preserves_chain_and_records(self):
        run = self.registry.run_operation(
            "pass197.reciprocal_matrix_gate",
            {"x_values": [1], "y_values": [1], "xy_symbol_values": [0]},
        )
        self.registry.close()
        self.registry = Pass198OperationCalibrationRegistry(state_root=self.temp.name)
        self.assertEqual(self.registry.list_runs()[0]["run_id"], run["run_id"])
        self.assertEqual(len(self.registry.list_simplifications()), 4)
        self.assertTrue(self.registry.verify_event_chain()["ok"])


if __name__ == "__main__":
    unittest.main()
