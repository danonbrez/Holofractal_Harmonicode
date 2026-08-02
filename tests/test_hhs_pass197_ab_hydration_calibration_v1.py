import json
import tempfile
import unittest
from pathlib import Path

from hhs_backend.runtime.pass197_exact_v1 import (
    ADDRESS_COUNT, COLUMN_SUMS, EXPECTED_COLUMN_SUMS, EXPECTED_INVERSE_ROW_SUMS,
    INVERSE_ROW_SUMS, M, M_INVERSE, address, decode_address, matrix_identity,
    matrix_multiply,
)
from hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1 import (
    Pass197ABHydrationCalibration,
    Pass197CalibrationError,
)


class Pass197Tests(unittest.TestCase):
    def test_reciprocal_constants_and_inverse(self):
        self.assertEqual(COLUMN_SUMS, EXPECTED_COLUMN_SUMS)
        self.assertEqual(INVERSE_ROW_SUMS, EXPECTED_INVERSE_ROW_SUMS)
        self.assertEqual(matrix_multiply(M, M_INVERSE), matrix_identity(3))

    def test_address_codec_covers_5184(self):
        seen = set()
        for state in range(ADDRESS_COUNT):
            i, j, k, l, lane = decode_address(state)
            cell = 27 * i + 9 * j + 3 * k + l
            self.assertEqual(address(cell, lane), state)
            seen.add((i, j, k, l, lane))
        self.assertEqual(len(seen), 5184)

    def test_exact_ab_tree_and_lossless_broadcast(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Pass197ABHydrationCalibration(state_root=temp)
            report = runtime.run({
                "x_values": ["-1", "0", "1"],
                "y_values": ["-1", "0", "1"],
                "xy_symbol_values": [-1, 0, 1],
            })
            summary = report["summary"]
            self.assertEqual(summary["evaluated_parameter_states"], 27)
            self.assertEqual(summary["admitted_parameter_states"], 12)
            self.assertEqual(summary["domain_rejected_parameter_states"], 15)
            self.assertEqual(summary["mismatch_parameter_states"], 0)
            self.assertEqual(summary["singular_parameter_states"], 0)
            self.assertEqual(summary["address_comparisons"], 12 * 5184)
            self.assertTrue(summary["lossless_simplifications_admitted"])
            self.assertEqual(summary["saved_fraction"], {"numerator": 63, "denominator": 64})
            self.assertTrue(report["closed"])
            self.assertTrue(report["replay"]["deterministic"])
            self.assertEqual(runtime.report()["report_hash72"], report["report_hash72"])

    def test_resume_is_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Pass197ABHydrationCalibration(state_root=temp)
            payload = {"x_values": ["1/2", "1"], "y_values": ["1/2", "1"], "xy_symbol_values": [0, 1]}
            first = runtime.run(payload)
            second = runtime.run(payload)
            self.assertEqual(first["state_root_hash72"], second["state_root_hash72"])
            self.assertEqual(first["report_hash72"], second["report_hash72"])

    def test_full_default_calibration_envelope(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Pass197ABHydrationCalibration(state_root=temp)
            report = runtime.run()
            summary = report["summary"]
            self.assertEqual(summary["evaluated_parameter_states"], 405)
            self.assertEqual(summary["admitted_parameter_states"], 320)
            self.assertEqual(summary["domain_rejected_parameter_states"], 85)
            self.assertEqual(summary["address_comparisons"], 1_658_880)
            self.assertEqual(summary["mismatch_parameter_states"], 0)
            self.assertEqual(summary["singular_parameter_states"], 0)
            self.assertEqual(report["replay"]["replayed_parameter_states"], 405)
            self.assertTrue(report["analytic_domain_proof"]["all_real_nonzero_rational_states_nonsingular"])
            self.assertTrue(report["closed"])

    def test_float_ingress_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Pass197ABHydrationCalibration(state_root=temp)
            with self.assertRaises(ValueError):
                runtime.run({"x_values": [0.5], "y_values": [1], "xy_symbol_values": [0]})

    def test_checkpoint_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Pass197ABHydrationCalibration(state_root=temp)
            payload = {"x_values": [1], "y_values": [1], "xy_symbol_values": [0]}
            runtime.run(payload)
            checkpoint = Path(temp) / "ab_hydration_checkpoint.json"
            data = json.loads(checkpoint.read_text())
            data["receipt_tip_hash72"] = "f" * 72
            checkpoint.write_text(json.dumps(data))
            with self.assertRaises(Pass197CalibrationError):
                runtime.run(payload)


if __name__ == "__main__":
    unittest.main()
