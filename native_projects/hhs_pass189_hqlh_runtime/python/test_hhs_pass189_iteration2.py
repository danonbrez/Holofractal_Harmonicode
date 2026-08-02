import tempfile
import threading
import unittest
from fractions import Fraction
from pathlib import Path

from hhs_pass189_iteration2 import (
    CalibrationLedger,
    CalibrationProfile,
    ZERO_HASH72,
    hash72,
    rational_json,
    verify_projection_lock,
)


def profile_payload(*, evidence="SYNTHETIC", attested=False, token="arm"):
    return {
        "device_id": "adc-01",
        "variable": "V",
        "unit": "volt",
        "dimension": "electric_potential",
        "scale": {"numerator": 1, "denominator": 1000},
        "offset": 0,
        "raw_min": 0,
        "raw_max": 5000,
        "canonical_min": 0,
        "canonical_max": 5,
        "resolution": {"numerator": 1, "denominator": 1000},
        "tolerance": {"numerator": 1, "denominator": 100},
        "required_samples": 3,
        "evidence_class": evidence,
        "calibration_source": "fixture" if evidence == "SYNTHETIC" else "bench-meter-01",
        "device_attested": attested,
        "operator_arm_hash72": hash72({"operator_arm_token": token}),
        "created_ns": 100,
    }


class Pass189Iteration2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "authority.sqlite3"
        self.ledger = CalibrationLedger(self.db, busy_timeout_ms=100, retries=3)

    def tearDown(self):
        self.ledger.close()
        self.temp.cleanup()

    def test_rejects_float_canonical_profile(self):
        payload = profile_payload()
        payload["scale"] = 0.001
        with self.assertRaises(ValueError):
            CalibrationProfile.create(payload)

    def test_profile_registration_is_idempotent(self):
        first = self.ledger.register_profile(profile_payload())
        second = self.ledger.register_profile(profile_payload())
        self.assertFalse(first["idempotent"])
        self.assertTrue(second["idempotent"])
        self.assertEqual(first["profile_id"], second["profile_id"])
        self.assertEqual(self.ledger.receipt_index, 1)

    def test_exact_samples_validate_profile(self):
        profile = self.ledger.register_profile(profile_payload())
        for index, raw in enumerate((1000, 2500, 5000), start=1):
            sample = self.ledger.append_sample(profile["profile_id"], {
                "measurement_id": f"m{index}",
                "measurement_ns": index,
                "source": "fixture",
                "raw": raw,
                "expected": rational_json(Fraction(raw, 1000)),
            })
        self.assertEqual(sample["profile_status"], "VALIDATED")
        self.assertEqual(sample["accepted_samples"], 3)
        self.assertEqual(self.ledger.get_profile(profile["profile_id"])["status"], "VALIDATED")

    def test_rejected_sample_does_not_validate(self):
        profile = self.ledger.register_profile(profile_payload())
        self.ledger.append_sample(profile["profile_id"], {
            "measurement_id": "bad", "measurement_ns": 1, "source": "fixture", "raw": 1000, "expected": 2,
        })
        self.assertEqual(self.ledger.get_profile(profile["profile_id"])["status"], "CALIBRATION_IN_PROGRESS")

    def test_simulation_authorized_physical_blocked_without_measured_evidence(self):
        profile = self.ledger.register_profile(profile_payload())
        simulation = self.ledger.admit_output(profile["profile_id"], 1, mode="SIMULATION")
        physical = self.ledger.admit_output(profile["profile_id"], 1, mode="PHYSICAL", operator_arm_token="arm")
        self.assertTrue(simulation["authorized"])
        self.assertFalse(physical["authorized"])
        self.assertIn("MEASURED_HARDWARE_EVIDENCE_REQUIRED", physical["reasons"])

    def test_measured_fixture_exercises_bounded_physical_gate(self):
        profile = self.ledger.register_profile(profile_payload(evidence="MEASURED_HARDWARE", attested=True, token="secret"))
        for index, raw in enumerate((1000, 2000, 3000), start=1):
            self.ledger.append_sample(profile["profile_id"], {
                "measurement_id": f"hw{index}", "measurement_ns": index, "source": "bench-meter-01",
                "raw": raw, "expected": {"numerator": raw, "denominator": 1000},
            })
        rejected = self.ledger.admit_output(profile["profile_id"], 2, mode="PHYSICAL", operator_arm_token="wrong")
        admitted = self.ledger.admit_output(profile["profile_id"], 2, mode="PHYSICAL", operator_arm_token="secret")
        self.assertFalse(rejected["authorized"])
        self.assertTrue(admitted["authorized"])
        self.assertEqual(admitted["dispatch_scope"], "CANDIDATE_ONLY_NO_DEVICE_DRIVER")

    def test_worldline_batch_is_joint_and_receipt_locked(self):
        before = self.ledger.receipt_index
        result = self.ledger.resolve_worldlines([
            {"object_id": "a", "input_receipt_index": before, "position4": [0, 0, 0, 0], "delta4": [2, 1, 0, 0]},
            {"object_id": "b", "input_receipt_index": before, "position4": [0, 4, 0, 0], "delta4": [2, -1, 0, 0]},
        ])
        self.assertTrue(result["joint_admission"])
        self.assertEqual({item["receipt_index"] for item in result["objects"]}, {result["global_receipt_index"]})
        self.assertEqual(len(result["global_hash72"]), 72)

    def test_worldline_causal_and_collision_rejection_is_atomic(self):
        before = self.ledger.receipt_index
        with self.assertRaises(ValueError):
            self.ledger.resolve_worldlines([{"object_id": "fast", "position4": [0, 0, 0, 0], "delta4": [1, 2, 0, 0]}])
        self.assertEqual(self.ledger.receipt_index, before)
        with self.assertRaises(ValueError):
            self.ledger.resolve_worldlines([
                {"object_id": "a", "position4": [0, 0, 0, 0], "delta4": [1, 1, 0, 0]},
                {"object_id": "b", "position4": [0, 2, 0, 0], "delta4": [1, -1, 0, 0]},
            ])
        self.assertEqual(self.ledger.receipt_index, before)

    def test_checkpoint_recovery_preserves_captured_root(self):
        profile = self.ledger.register_profile(profile_payload())
        self.ledger.append_sample(profile["profile_id"], {
            "measurement_id": "m1", "measurement_ns": 1, "source": "fixture", "raw": 1000, "expected": 1,
        })
        checkpoint = self.ledger.create_checkpoint("after-first-sample")
        self.assertTrue(self.ledger.verify_checkpoint(checkpoint["checkpoint_id"])["verified"])
        target = Path(self.temp.name) / "recovered.sqlite3"
        recovered = self.ledger.recover_checkpoint(checkpoint["checkpoint_id"], target)
        self.assertTrue(recovered["recovered"])
        self.assertEqual(recovered["root_hash72"], checkpoint["captured_root_hash72"])
        probe = CalibrationLedger(target)
        try:
            self.assertEqual(probe.root_hash72, checkpoint["captured_root_hash72"])
            self.assertEqual(probe.receipt_index, checkpoint["captured_receipt_index"])
        finally:
            probe.close()

    def test_projection_lock(self):
        equation_hash = hash72({"equation": "V==I*R"})
        result = verify_projection_lock({
            "vm81": {"equation_hash72": equation_hash, "receipt_index": 7},
            "circuit": {"equation_hash72": equation_hash, "receipt_index": 7},
            "worldline": {"equation_hash72": equation_hash, "receipt_index": 7},
        })
        self.assertTrue(result["locked"])
        with self.assertRaises(ValueError):
            verify_projection_lock({
                "a": {"equation_hash72": equation_hash, "receipt_index": 7},
                "b": {"equation_hash72": ZERO_HASH72, "receipt_index": 8},
            })

    def test_bounded_concurrent_receipts(self):
        profile = self.ledger.register_profile(profile_payload())
        errors = []

        def worker(index):
            try:
                self.ledger.admit_output(profile["profile_id"], index % 5, mode="SIMULATION")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(self.ledger.receipt_index, 9)
        self.assertEqual(len(self.ledger.root_hash72), 72)


if __name__ == "__main__":
    unittest.main()
