"""Real, unmocked Pass220 I074 -> I065 -> I148 -> HNAN -> Q81 candidate test.

Do not promote source identity or a roundtrip to a VM81 gate certificate.
The complete native course closure and C++ cell-wall mediation remain separate.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    build_candidate as build_i074_candidate,
)
from hhs_runtime.hhs_pass220_q81_lane5_phase_candidate_binding_v1 import (
    bind_candidate,
)
from hhs_runtime.hhs_pass220_q81_binary_phase_hnan_projection_v1 import (
    decode_candidate,
    verify_receipt,
)

RAW = "01" * 2592
PAIRS = tuple(tuple(
    ((0, 1), (1, 0), (-1, 1), (1, -1))[(i * 9 + j) % 4]
    for j in range(9)
) for i in range(9))


class TestQ81RealInheritedPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.i074 = build_i074_candidate()

    def test_actual_inherited_i074_i065_i148_hnan_route(self):
        result = bind_candidate(
            RAW,
            PAIRS,
            inherited_i074_candidate=self.i074,
        )
        receipt = result["binary_phase_receipt"]
        self.assertTrue(verify_receipt(receipt))
        decoded = decode_candidate(receipt["binary"], context=receipt["context"])
        self.assertEqual(decoded["native_ordered_pairs"], PAIRS)
        self.assertEqual(result["i074_hash216"], self.i074["candidate_hash216"])
        self.assertEqual(
            receipt["context"]["provenance"]["i074_hash216"],
            self.i074["candidate_hash216"],
        )
        self.assertTrue(result["native_pair_candidate_equal_to_egress"])
        self.assertFalse(result["source_phase_native_certified"])
        self.assertFalse(result["full_course_closure_certified"])
        self.assertFalse(result["pass219_cpp_wall_executed"])
        self.assertFalse(result["vm81_admission_invoked"])
        self.assertTrue(result["candidate_only"])

    def test_corrupt_native_i074_candidate_rejected(self):
        damaged = deepcopy(self.i074)
        damaged["candidate_hash216"] = "0" * 216
        with self.assertRaises(ValueError):
            bind_candidate(
                RAW,
                PAIRS,
                inherited_i074_candidate=damaged,
            )


if __name__ == "__main__":
    unittest.main()
