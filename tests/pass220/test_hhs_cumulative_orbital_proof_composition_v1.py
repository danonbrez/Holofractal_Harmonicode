"""Native-service composition against original Pass 089/091 source receipts.

This tests interface preservation; finite orbital runs are not the universal
theorem and do not replace the full original mathematical corpus.
"""
from __future__ import annotations

from pathlib import Path
import copy
import unittest

from native_projects.hhs_bifurcation_calibration.hhs_pass091_collatz_prime_tensor_decay_entanglement_v1 import (
    default_workload,
)
from hhs_runtime.pass220.hhs_cumulative_orbital_proof_composition_v1 import (
    CumulativeOrbitalProofError,
    compose_inherited_orbital_proof,
)

ROOT = Path(__file__).resolve().parents[2]


class TestCumulativeNativeOrbitalComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_workload = default_workload(
            ROOT, workload_id="PASS220_CUMULATIVE_ORBITAL_NATIVE_COMPOSITION",
            prime_count=11,
        )
        # The theorem target explicitly identifies odd-prime seeds: prime 2
        # remains a separately typed dyadic primitive, not an odd-prime seed.
        source_workload["prime_sources"] = [
            source for source in source_workload["prime_sources"]
            if source["prime"] % 2 == 1
        ]
        source_workload["prime_count_admitted"] = len(
            source_workload["prime_sources"]
        )
        cls.workload = source_workload

    def test_preserve_all_admitted_odd_prime_lanes_and_native_witnesses(self):
        report = compose_inherited_orbital_proof(ROOT, self.workload)
        self.assertEqual(
            report["lane_count"], len(self.workload["prime_sources"])
        )
        self.assertTrue(report["native_deterministic_replay"])
        self.assertEqual(report["full_recursive_constraint_bundle"]["pass"], True)
        self.assertEqual(
            report["parent_pass091_result_root_hash72"].__len__(), 72,
        )
        self.assertEqual(
            len(report["inherited_i072_theory_constructor"]["theory_hash216"]),
            216,
        )
        self.assertTrue(report["inherited_i072_hydration_validation"])
        self.assertIsNone(report["native_hnan_all_branch_trace"])
        self.assertIsNone(report["actual_runtime_authority_audit"])
        self.assertFalse(report["global_theorem_completed"])
        self.assertFalse(report["canonical_vm81_admission"])
        self.assertTrue(report["candidate_only"])
        self.assertEqual(
            [lane["prime_seed"] for lane in report["all_provided_odd_prime_lanes"]],
            [src["prime"] for src in self.workload["prime_sources"]],
        )

    def test_reject_unproven_universal_claim(self):
        workload = copy.deepcopy(self.workload)
        workload["claims_collatz_theorem"] = True
        with self.assertRaisesRegex(
            CumulativeOrbitalProofError, "BOUNDED_TRACE_IS_NOT_UNIVERSAL_PROOF"
        ):
            compose_inherited_orbital_proof(ROOT, workload)

    def test_require_actual_native_claims_and_built_library_together(self):
        with self.assertRaisesRegex(
            CumulativeOrbitalProofError,
            "NATIVE_LIBRARY_AND_ACTUAL_CLAIMS_REQUIRED_TOGETHER",
        ):
            compose_inherited_orbital_proof(ROOT, self.workload,
                                            native_library="/missing/lib.so")

    def test_reject_fabricated_runtime_receipt_without_state(self):
        with self.assertRaisesRegex(
            CumulativeOrbitalProofError, "ACTUAL_AUTHORITY_STATE_REQUIRED"
        ):
            compose_inherited_orbital_proof(
                ROOT, self.workload,
                runtime_authority_receipt={"receipt_hash72": "x" * 72},
            )


if __name__ == "__main__":
    unittest.main()
