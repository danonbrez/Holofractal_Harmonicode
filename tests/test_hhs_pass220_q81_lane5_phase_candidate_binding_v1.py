"""Candidate-only Q81 Lane5 binding tests: no synthetic VM81 admission."""
from __future__ import annotations

from hashlib import sha256
from unittest import TestCase, mock

from hhs_runtime.hhs_pass220_q81_lane5_phase_candidate_binding_v1 import (
    Q81Lane5BindingError,
    bind_candidate,
)
from hhs_runtime.hhs_pass220_q81_binary_phase_hnan_projection_v1 import (
    verify_receipt,
)


RAW = "01" * 2592
PAIRS = tuple(tuple(
    ((0, 1), (1, 0), (-1, 1), (1, -1))[(i * 9 + j) % 4]
    for j in range(9)
) for i in range(9))


def inherited_receipt(raw):
    return {
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
        "raw_roundtrip_exact": True,
        "hnan_gate_inherited": True,
        "raw5184_sha256": sha256(raw.encode("ascii")).hexdigest(),
        "i074_candidate_root_sha256": "root-from-inherited-candidate",
        "i074_hash216": "z" * 216,
        "ordered_phase_difference_witness_sha256": "phase-root",
        "hnan_center_source": "x+y-z-w+xy+yx-zw-wz",
        "hnan_terminal_source": "xy+epsilon",
    }


class TestQ81Lane5CandidateBinding(TestCase):
    def test_source_and_orientation_derived_from_pairs(self):
        with mock.patch(
            "hhs_runtime.hhs_pass220_q81_lane5_phase_candidate_binding_v1.bind_inherited_lane5",
            return_value=inherited_receipt(RAW),
        ) as bridge:
            record = bind_candidate(RAW, PAIRS, inherited_i074_candidate={"existing": True})
        bridge.assert_called_once_with(RAW, candidate={"existing": True})
        self.assertTrue(verify_receipt(record["binary_phase_receipt"]))
        receipt = record["binary_phase_receipt"]
        self.assertEqual(receipt["context"]["source_identity"], sha256(RAW.encode("ascii")).hexdigest())
        self.assertEqual(receipt["binary"][0][:4], (0, 0, 1, 1))
        self.assertEqual(receipt["context"]["orientation"][0][:4], (0, 1, 0, 1))
        self.assertFalse(record["source_phase_native_certified"])
        self.assertFalse(record["pass219_cpp_wall_executed"])
        self.assertFalse(record["vm81_admission_invoked"])

    def test_bad_pair_rejected_before_lane5(self):
        wrong = [list(row) for row in PAIRS]
        wrong[0][0] = (2, 2)
        with mock.patch(
            "hhs_runtime.hhs_pass220_q81_lane5_phase_candidate_binding_v1.bind_inherited_lane5"
        ) as bridge:
            with self.assertRaisesRegex(Q81Lane5BindingError, "PHASE_PAIR_DOMAIN"):
                bind_candidate(RAW, wrong, inherited_i074_candidate={})
            bridge.assert_not_called()

    def test_corrupt_inherited_source_rejected(self):
        forged = inherited_receipt(RAW)
        forged["raw5184_sha256"] = "0" * 64
        with mock.patch(
            "hhs_runtime.hhs_pass220_q81_lane5_phase_candidate_binding_v1.bind_inherited_lane5",
            return_value=forged,
        ):
            with self.assertRaisesRegex(Q81Lane5BindingError, "INHERITED_LANE5_NOT_VERIFIED"):
                bind_candidate(RAW, PAIRS, inherited_i074_candidate={})

    def test_unauthorized_inherited_mutation_rejected(self):
        forged = inherited_receipt(RAW)
        forged["canonical_vm81_mutation_authority"] = True
        with mock.patch(
            "hhs_runtime.hhs_pass220_q81_lane5_phase_candidate_binding_v1.bind_inherited_lane5",
            return_value=forged,
        ):
            with self.assertRaisesRegex(Q81Lane5BindingError, "INHERITED_LANE5_NOT_VERIFIED"):
                bind_candidate(RAW, PAIRS, inherited_i074_candidate={})

    def test_raw_shape_rejected(self):
        with self.assertRaisesRegex(Q81Lane5BindingError, "RAW5184_FORMAT"):
            bind_candidate(RAW[:-1], PAIRS, inherited_i074_candidate={})


if __name__ == "__main__":
    import unittest
    unittest.main()
