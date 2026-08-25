import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from hhs_backend.api.pass197_calibration_routes import ABHydrationCalibrationRequest
from hhs_backend.runtime import pass197_exact_v1
from hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1 import (
    Pass197ABHydrationCalibration,
    Pass197CalibrationError,
    REPAIR_SCHEMA,
)
from hhs_backend.runtime.pass197_exact_v1 import exact_fraction
from hhs_backend.runtime.pass197_state_v1 import CalibrationConfig, MAX_SYNCHRONOUS_PARAMETER_STATES


class Pass197I129RepairTests(unittest.TestCase):
    def test_01_rational_object_components_are_strict_integers(self):
        self.assertEqual(exact_fraction({"numerator": 1, "denominator": 2}, field="q").numerator, 1)
        for payload in (
            {"numerator": 1.9, "denominator": 2},
            {"numerator": 1, "denominator": 2.1},
            {"numerator": True, "denominator": 2},
            {"numerator": "1", "denominator": 2},
        ):
            with self.assertRaises(ValueError):
                exact_fraction(payload, field="q")

    def test_02_exact_exponents_do_not_coerce(self):
        for value in (1.0, True, "1"):
            with self.assertRaises(ValueError):
                CalibrationConfig.from_payload({"x_values": [1], "y_values": [1], "xy_symbol_values": [value]})

    def test_03_api_exponents_and_controls_are_strict(self):
        for value in (1.0, True):
            with self.assertRaises(ValidationError):
                ABHydrationCalibrationRequest(xy_symbol_values=[value])
        with self.assertRaises(ValidationError):
            ABHydrationCalibrationRequest(full_replay="true")

    def test_04_duplicate_exact_coordinates_are_rejected(self):
        with self.assertRaises(ValueError):
            CalibrationConfig.from_payload({"x_values": ["1", "1/1"], "y_values": [1], "xy_symbol_values": [0]})
        with self.assertRaises(ValueError):
            CalibrationConfig.from_payload({"x_values": [1], "y_values": [1], "xy_symbol_values": [0, 0]})

    def test_05_synchronous_workload_is_bounded_to_historical_envelope(self):
        self.assertEqual(MAX_SYNCHRONOUS_PARAMETER_STATES, 405)
        with self.assertRaises(ValueError):
            CalibrationConfig.from_payload({
                "x_values": list(range(1, 30)),
                "y_values": list(range(1, 30)),
                "xy_symbol_values": [0],
            })

    def test_06_full_replay_is_required_for_closure(self):
        with tempfile.TemporaryDirectory() as root:
            report = Pass197ABHydrationCalibration(state_root=root).run(
                {"x_values": [1], "y_values": [1], "xy_symbol_values": [0], "full_replay": False},
                vm81_receipt_hash72="1" * 72,
            )
            self.assertFalse(report["closed"])
            self.assertFalse(report["replay"]["deterministic"])
            self.assertEqual(report["replay"]["replayed_parameter_states"], 0)

    def test_07_every_persisted_branch_has_kernel_audit_evidence(self):
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass197ABHydrationCalibration(state_root=root)
            report = runtime.run(
                {"x_values": [0, 1], "y_values": [1], "xy_symbol_values": [0]},
                vm81_receipt_hash72="2" * 72,
            )
            self.assertEqual(report["repair_schema"], REPAIR_SCHEMA)
            self.assertEqual(report["summary"]["kernel_audited_parameter_states"], 2)
            checkpoint = json.loads((Path(root) / "ab_hydration_checkpoint.json").read_text())
            self.assertTrue(checkpoint["completed"])
            for state in checkpoint["completed"].values():
                self.assertTrue(state["kernel_audit_receipt_hash72"])
                self.assertTrue(state["kernel_state_hash72"])

    def test_08_legacy_unaudited_checkpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass197ABHydrationCalibration(state_root=root)
            payload = {"x_values": [1], "y_values": [1], "xy_symbol_values": [0]}
            runtime.run(payload, vm81_receipt_hash72="3" * 72)
            path = Path(root) / "ab_hydration_checkpoint.json"
            checkpoint = json.loads(path.read_text())
            first = next(iter(checkpoint["completed"].values()))
            first.pop("kernel_audit_receipt_hash72")
            body = {k: v for k, v in checkpoint.items() if k != "checkpoint_hash72"}
            checkpoint["checkpoint_hash72"] = pass197_exact_v1.hash72("pass197.checkpoint", body)
            path.write_text(pass197_exact_v1.canonical_json(checkpoint) + "\n")
            with self.assertRaises(Pass197CalibrationError):
                Pass197ABHydrationCalibration(state_root=root).run(payload, vm81_receipt_hash72="4" * 72)

    def test_09_status_quarantines_tampered_report(self):
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass197ABHydrationCalibration(state_root=root)
            runtime.run({"x_values": [1], "y_values": [1], "xy_symbol_values": [0]}, vm81_receipt_hash72="5" * 72)
            path = Path(root) / "ab_hydration_report.json"
            report = json.loads(path.read_text())
            report["closed"] = False
            path.write_text(json.dumps(report))
            restarted = Pass197ABHydrationCalibration(state_root=root)
            status = restarted.status()
            self.assertFalse(status["closed"])
            self.assertTrue(status["quarantined"])
            self.assertEqual(status["reason"], "REPORT_INTEGRITY_VERIFICATION_FAILED")

    def test_10_same_state_root_uses_one_serialization_lock(self):
        with tempfile.TemporaryDirectory() as root:
            left = Pass197ABHydrationCalibration(state_root=root)
            right = Pass197ABHydrationCalibration(state_root=root)
            self.assertIs(left._run_lock, right._run_lock)

    def test_11_hash72_has_no_standalone_fallback(self):
        original = pass197_exact_v1._kernel_hash72
        original_error = pass197_exact_v1._HASH_AUTHORITY_ERROR
        try:
            pass197_exact_v1._kernel_hash72 = None
            pass197_exact_v1._HASH_AUTHORITY_ERROR = RuntimeError("test authority unavailable")
            with self.assertRaises(RuntimeError):
                pass197_exact_v1.hash72("test", {"x": 1})
            self.assertNotIn("FALLBACK", pass197_exact_v1.HASH_AUTHORITY)
        finally:
            pass197_exact_v1._kernel_hash72 = original
            pass197_exact_v1._HASH_AUTHORITY_ERROR = original_error

    def test_12_frontend_registers_only_verified_closed_projection(self):
        source = (Path(__file__).parents[1] / "applications/holofractal_harmonizer/src/pass197-calibration.mjs").read_text()
        self.assertIn("if (!value?.closed || !value?.report_hash72) return;", source)
        self.assertIn("lifecycle_state: 'ACTIVE'", source)
        self.assertNotIn("lifecycle_state: value.closed ? 'ACTIVE'", source)


if __name__ == "__main__":
    unittest.main()
