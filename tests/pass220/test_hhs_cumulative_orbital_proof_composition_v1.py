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
    ordered_shared_suffix_witnesses,
    ordered_affine_orbit_witness,
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
        for lane in report["all_provided_odd_prime_lanes"]:
            affine = lane["exact_ordered_affine_orbit"]
            self.assertTrue(affine["exact_ordered_endpoint_identity"])
            self.assertEqual(affine["operator_prime"], "3")
            self.assertEqual(
                len(affine["prefixes"]), len(affine["ordered_operation_word"]),
            )
            self.assertFalse(affine["native_vm81_admission"])
        pairs = report["ordered_shared_suffix_witnesses"]
        self.assertEqual(report["shared_suffix_pair_count"], len(pairs))
        self.assertGreater(len(pairs), 0)
        for pair in pairs:
            self.assertTrue(pair["equal_future_scalar_successors_by_induction"])
            self.assertFalse(pair["full_native_state_equivalence_proved"])
            self.assertTrue(pair["distinct_ancestry_preserved"])
            self.assertEqual(len(pair["left_intersection_root_hash72"]), 72)
            self.assertEqual(len(pair["right_intersection_root_hash72"]), 72)

        self.assertEqual(
            [lane["prime_seed"] for lane in report["all_provided_odd_prime_lanes"]],
            [src["prime"] for src in self.workload["prime_sources"]],
        )

    def test_exact_ordered_affine_construction_for_full_native_word(self):
        # 3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1 -> 4.
        states = [3, 10, 5, 16, 8, 4, 2, 1, 4]
        result = ordered_affine_orbit_witness(
            seed=3, ordered_states=states, operation_word="OEOEEEEO",
        )
        self.assertEqual(result["terminal_integer_state"], "4")
        self.assertEqual(len(result["prefixes"]), 8)
        self.assertEqual(
            int(result["A"]) * 3 + int(result["B"]),
            int(result["D"]) * 4,
        )
        self.assertTrue(result["exact_ordered_endpoint_identity"])

    def test_exact_affine_generalized_prime_operator_not_scalar_reordered(self):
        # Pass 092 p=5 generalized Collatz operator; odd 3 -> 16 -> 8.
        witness = ordered_affine_orbit_witness(
            seed=3, ordered_states=[3, 16, 8],
            operation_word="OE", odd_multiplier=5,
        )
        self.assertEqual(witness["A"], "5")
        self.assertEqual(witness["B"], "1")
        self.assertEqual(witness["D"], "2")
        self.assertEqual(witness["terminal_integer_state"], "8")

    def test_affine_rejects_reordered_or_counterfeit_integer_history(self):
        with self.assertRaisesRegex(
            CumulativeOrbitalProofError,
            "ORDERED_AFFINE_PARITY_OR_SUCCESSOR_MISMATCH",
        ):
            ordered_affine_orbit_witness(
                seed=3, ordered_states=[3, 10, 5], operation_word="EO",
            )
        with self.assertRaisesRegex(
            CumulativeOrbitalProofError,
            "ORDERED_AFFINE_PARITY_OR_SUCCESSOR_MISMATCH",
        ):
            ordered_affine_orbit_witness(
                seed=3, ordered_states=[3, 10, 6], operation_word="OE",
            )

    def test_shared_suffix_does_not_alias_distinct_ancestry(self):
        a = {
            "lane_id": "left", "ordered_states": [3, 10, 5, 16, 8, 4, 2, 1],
            "independent_prefix_root_hash72": "l" * 72,
            "state_nodes": [{"state_root_hash72": f"a{i}"} for i in range(8)],
        }
        b = {
            "lane_id": "right", "ordered_states": [5, 16, 8, 4, 2, 1],
            "independent_prefix_root_hash72": "r" * 72,
            "state_nodes": [{"state_root_hash72": f"b{i}"} for i in range(6)],
        }
        receipts = ordered_shared_suffix_witnesses([a, b])
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["intersection_value"], 5)
        self.assertEqual(receipts[0]["left_depth"], 2)
        self.assertEqual(receipts[0]["right_depth"], 0)
        self.assertEqual(receipts[0]["exact_observed_successor_count"], 5)
        self.assertNotEqual(
            receipts[0]["left_intersection_root_hash72"],
            receipts[0]["right_intersection_root_hash72"],
        )

    def test_shared_suffix_rejects_counterfeit_successor(self):
        a = {
            "lane_id": "left", "ordered_states": [5, 999],
            "independent_prefix_root_hash72": "a" * 72,
            "state_nodes": [{"state_root_hash72": "a"}] * 2,
        }
        b = {
            "lane_id": "right", "ordered_states": [5, 999],
            "independent_prefix_root_hash72": "b" * 72,
            "state_nodes": [{"state_root_hash72": "b"}] * 2,
        }
        with self.assertRaisesRegex(
            CumulativeOrbitalProofError, "SHARED_SUFFIX_NATIVE_SUCCESSOR_MISMATCH"
        ):
            ordered_shared_suffix_witnesses([a, b])

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
