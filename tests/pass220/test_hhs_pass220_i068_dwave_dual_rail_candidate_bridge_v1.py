from __future__ import annotations

import unittest

from hhs_runtime.hhs_pass220_i068_dwave_dual_rail_candidate_bridge_v1 import (
    AUTHORITY_BOUNDARY,
    MCEDSignal,
    OUTCOME_SYMBOLS,
    OrderedGateWitness,
    Pass220I068DWaveBridgeError,
    compare_with_vm81_histogram,
    hash72,
    i027_outcome_for_symbols,
    self_test,
    transcribe_dwave_counts,
    transcribe_leap_result,
)


class FakeResult:
    def __init__(self) -> None:
        self.post_select_args = []

    def get_counts(self, *, post_select=False):
        self.post_select_args.append(post_select)
        return [{"00": 3, "0*": 1, "*1": 1}]

    def get_measurements_register(self):
        return ["q0", "q1"]


def program_hash() -> str:
    return hash72({"program": "i068-test"})


def build_candidate(*, gate=None, register_order=("q0", "q1")):
    return transcribe_dwave_counts(
        counts={"00": 3, "0*": 1, "*1": 1},
        register_order=register_order,
        gate=gate or OrderedGateWitness("CZ", "q0", "q1"),
        qpu="DRsim_21qubits",
        noise_model=True,
        shots_requested=5,
        program_hash72=program_hash(),
        mced_events=(MCEDSignal(0, 3, "q1", 1),),
    )


class I068DWaveBridgeTests(unittest.TestCase):
    def test_ordered_pair_maps_bijectively_to_existing_i027_nine_state_surface(self):
        values = {
            i027_outcome_for_symbols(control, target)
            for control in OUTCOME_SYMBOLS
            for target in OUTCOME_SYMBOLS
        }
        self.assertEqual(values, set(range(9)))
        self.assertNotEqual(
            i027_outcome_for_symbols("0", "*"),
            i027_outcome_for_symbols("*", "0"),
        )

    def test_splats_are_preserved_and_yield_is_exact(self):
        candidate = build_candidate()
        round_ = candidate.rounds[0]
        self.assertEqual(round_.shots_observed, 5)
        self.assertEqual(round_.clean_shots, 3)
        self.assertEqual(round_.erased_shots, 2)
        self.assertEqual(
            (
                round_.exact_yield_numerator,
                round_.exact_yield_denominator,
            ),
            (3, 5),
        )
        self.assertIn(("q0", 1), round_.erasure_counts_by_register)
        self.assertIn(("q1", 1), round_.erasure_counts_by_register)
        self.assertEqual(len(candidate.receipt_hash216), 216)
        self.assertEqual(
            candidate.receipt_hash216,
            candidate.config_hash72
            + candidate.result_hash72
            + candidate.authority_hash72,
        )

    def test_register_order_is_explicit_not_assumed(self):
        direct = build_candidate()
        reversed_order = transcribe_dwave_counts(
            counts={"00": 3, "*0": 1, "1*": 1},
            register_order=("q1", "q0"),
            gate=OrderedGateWitness("CZ", "q0", "q1"),
            qpu="DRsim_21qubits",
            noise_model=True,
            shots_requested=5,
            program_hash72=program_hash(),
        )
        self.assertEqual(
            dict(direct.rounds[0].i027_outcome_histogram),
            dict(reversed_order.rounds[0].i027_outcome_histogram),
        )
        self.assertNotEqual(
            direct.config_hash72,
            reversed_order.config_hash72,
        )

    def test_control_target_reversal_changes_ordered_geometry(self):
        direct = build_candidate()
        reversed_gate = build_candidate(
            gate=OrderedGateWitness("CZ", "q1", "q0")
        )
        self.assertNotEqual(
            dict(direct.rounds[0].i027_outcome_histogram),
            dict(reversed_gate.rounds[0].i027_outcome_histogram),
        )
        self.assertNotEqual(
            direct.receipt_hash216,
            reversed_gate.receipt_hash216,
        )

    def test_post_selected_only_input_fails_closed(self):
        with self.assertRaises(Pass220I068DWaveBridgeError):
            transcribe_dwave_counts(
                counts={"00": 5},
                register_order=("q0", "q1"),
                gate=OrderedGateWitness("CZ", "q0", "q1"),
                qpu="DRsim_21qubits",
                noise_model=True,
                shots_requested=5,
                program_hash72=program_hash(),
                post_selected=True,
            )

    def test_ideal_mode_rejects_erasure_splats(self):
        with self.assertRaises(Pass220I068DWaveBridgeError):
            transcribe_dwave_counts(
                counts={"0*": 1},
                register_order=("q0", "q1"),
                gate=OrderedGateWitness("CZ", "q0", "q1"),
                qpu="DRsim_21qubits",
                noise_model=False,
                shots_requested=1,
                program_hash72=program_hash(),
            )

    def test_receipt_is_deterministic(self):
        first = build_candidate()
        second = build_candidate()
        self.assertEqual(
            first.receipt_hash216,
            second.receipt_hash216,
        )

    def test_leap_result_transcription_explicitly_disables_post_selection(self):
        result = FakeResult()
        candidate = transcribe_leap_result(
            result,
            gate=OrderedGateWitness("CZ", "q0", "q1"),
            qpu="DRsim_21qubits",
            noise_model=True,
            shots_requested=5,
            program_hash=program_hash(),
        )
        self.assertEqual(result.post_select_args, [False])
        self.assertEqual(candidate.rounds[0].erased_shots, 2)

    def test_authority_boundary_is_candidate_only(self):
        candidate = build_candidate()
        self.assertEqual(
            dict(candidate.authority),
            AUTHORITY_BOUNDARY,
        )
        self.assertTrue(candidate.authority["candidate_only"])
        self.assertFalse(
            candidate.authority[
                "canonical_vm81_mutation_authority"
            ]
        )
        self.assertFalse(
            candidate.authority[
                "canonical_hash72_commit_authority"
            ]
        )
        self.assertFalse(
            candidate.authority[
                "canonical_hash216_commit_authority"
            ]
        )
        self.assertFalse(
            candidate.authority[
                "canonical_persistence_authority"
            ]
        )

    def test_vm81_comparison_is_exact_and_non_authoritative(self):
        candidate = build_candidate()
        canonical = dict(
            candidate.rounds[0].i027_outcome_histogram
        )
        canonical_receipt = (
            hash72("vm81-prev")
            + hash72("vm81-state")
            + hash72("vm81-receipt")
        )
        witness = compare_with_vm81_histogram(
            candidate,
            canonical_histogram=canonical,
            canonical_vm81_receipt_hash216=canonical_receipt,
        )
        self.assertTrue(witness.sample_count_equal)
        self.assertTrue(witness.exact_histogram_equal)
        self.assertFalse(
            witness.canonical_mutation_authority
        )
        self.assertFalse(
            witness.hash72_commit_authority
        )
        self.assertFalse(
            witness.hash216_commit_authority
        )

    def test_float_metadata_is_rejected(self):
        with self.assertRaises(Pass220I068DWaveBridgeError):
            hash72({"run_time": 0.1})

    def test_self_test_closes(self):
        report = self_test()
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(report["checks"].values()))


if __name__ == "__main__":
    unittest.main()
