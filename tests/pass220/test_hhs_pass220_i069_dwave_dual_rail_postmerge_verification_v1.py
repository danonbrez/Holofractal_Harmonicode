from __future__ import annotations

from itertools import product
import unittest

from hhs_runtime.hhs_pass220_i068_dwave_dual_rail_candidate_bridge_v1 import (
    AUTHORITY_BOUNDARY,
    DOCUMENTED_BETA_QPUS,
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
from hhs_runtime.hhs_pass220_quantum_collapse_admission_bridge_v1 import (
    collapse_address,
)


PAIR_KEYS = tuple(
    a + b
    for a in OUTCOME_SYMBOLS
    for b in OUTCOME_SYMBOLS
)


def program_hash(tag: str = "i069") -> str:
    return hash72({"program": tag})


def gate() -> OrderedGateWitness:
    return OrderedGateWitness("CZ", "q0", "q1")


def candidate_from_counts(
    counts,
    *,
    qpu: str = "DRsim_21qubits",
    noise_model: bool = True,
    shots_requested: int | None = None,
    repeat_until_shots_requested: bool = False,
    program_tag: str = "i069",
    gate_witness: OrderedGateWitness | None = None,
    register_order=("q0", "q1"),
    mced_events=(),
):
    if shots_requested is None:
        if isinstance(counts, dict):
            shots_requested = sum(counts.values())
        else:
            shots_requested = sum(next(iter(counts)).values())
    return transcribe_dwave_counts(
        counts=counts,
        register_order=register_order,
        gate=gate_witness or gate(),
        qpu=qpu,
        noise_model=noise_model,
        shots_requested=shots_requested,
        program_hash72=program_hash(program_tag),
        repeat_until_shots_requested=repeat_until_shots_requested,
        mced_events=mced_events,
    )


def weak_compositions(total: int, bins: int):
    if bins == 1:
        yield (total,)
        return
    for head in range(total + 1):
        for tail in weak_compositions(total - head, bins - 1):
            yield (head,) + tail


class FakeResult:
    def __init__(self, counts, register):
        self._counts = counts
        self._register = register
        self.post_select_args = []

    def get_counts(self, *, post_select=False):
        self.post_select_args.append(post_select)
        return self._counts

    def get_measurements_register(self):
        return self._register


class Pass220I069PostMergeVerificationTests(unittest.TestCase):
    def test_i068_self_test_remains_closed_after_merge(self):
        report = self_test()
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(report["checks"].values()))

    def test_all_nine_ordered_dual_rail_states_are_bijective(self):
        observed = {}
        for control, target in product(OUTCOME_SYMBOLS, repeat=2):
            outcome = i027_outcome_for_symbols(control, target)
            self.assertNotIn(outcome, observed)
            observed[outcome] = (control, target)
        self.assertEqual(sorted(observed), list(range(9)))

    def test_erasure_partition_is_exactly_five_vs_four(self):
        pairs = tuple(product(OUTCOME_SYMBOLS, repeat=2))
        erasure = [p for p in pairs if "*" in p]
        clean = [p for p in pairs if "*" not in p]
        self.assertEqual(len(erasure), 5)
        self.assertEqual(len(clean), 4)
        self.assertEqual(len(erasure) + len(clean), 9)

    def test_order_reversal_changes_every_unequal_pair(self):
        for left, right in product(OUTCOME_SYMBOLS, repeat=2):
            direct = i027_outcome_for_symbols(left, right)
            reverse = i027_outcome_for_symbols(right, left)
            if left == right:
                self.assertEqual(direct, reverse)
            else:
                self.assertNotEqual(direct, reverse)

    def test_i027_nucleus_product_covers_all_81_vm81_cells_once(self):
        cells = []
        for nucleus in range(9):
            for outcome in range(9):
                address = collapse_address(outcome, nucleus)
                self.assertEqual(
                    address.vm81_cell_id,
                    9 * nucleus + outcome,
                )
                cells.append(address.vm81_cell_id)
        self.assertEqual(sorted(cells), list(range(81)))
        self.assertEqual(len(set(cells)), 81)

    def test_each_single_shot_pair_hits_exactly_one_expected_bin(self):
        for key in PAIR_KEYS:
            candidate = candidate_from_counts({key: 1})
            histogram = dict(
                candidate.rounds[0].i027_outcome_histogram
            )
            expected = i027_outcome_for_symbols(key[0], key[1])
            self.assertEqual(sum(histogram.values()), 1)
            self.assertEqual(histogram[expected], 1)
            self.assertTrue(
                all(
                    count == (1 if index == expected else 0)
                    for index, count in histogram.items()
                )
            )

    def test_all_small_exact_count_distributions_preserve_histogram(self):
        checked = 0
        for shots in range(1, 5):
            for composition in weak_compositions(shots, 9):
                counts = {
                    key: count
                    for key, count in zip(PAIR_KEYS, composition)
                    if count
                }
                candidate = candidate_from_counts(
                    counts,
                    shots_requested=shots,
                )
                histogram = dict(
                    candidate.rounds[0].i027_outcome_histogram
                )
                self.assertEqual(
                    [histogram[index] for index in range(9)],
                    list(composition),
                )
                round_ = candidate.rounds[0]
                self.assertEqual(round_.shots_observed, shots)
                self.assertEqual(
                    round_.clean_shots + round_.erased_shots,
                    shots,
                )
                checked += 1
        self.assertEqual(checked, 714)

    def test_register_reordering_does_not_silently_commute_gate_geometry(self):
        direct = candidate_from_counts(
            {"00": 3, "0*": 2, "*1": 1},
        )
        reordered = candidate_from_counts(
            {"00": 3, "*0": 2, "1*": 1},
            register_order=("q1", "q0"),
        )
        self.assertEqual(
            dict(direct.rounds[0].i027_outcome_histogram),
            dict(reordered.rounds[0].i027_outcome_histogram),
        )
        self.assertNotEqual(
            direct.config_hash72,
            reordered.config_hash72,
        )

    def test_reversing_control_target_changes_histogram_and_receipt(self):
        direct = candidate_from_counts(
            {"0*": 2, "*1": 1, "10": 3},
        )
        reversed_gate = candidate_from_counts(
            {"0*": 2, "*1": 1, "10": 3},
            gate_witness=OrderedGateWitness("CZ", "q1", "q0"),
        )
        self.assertNotEqual(
            dict(direct.rounds[0].i027_outcome_histogram),
            dict(reversed_gate.rounds[0].i027_outcome_histogram),
        )
        self.assertNotEqual(
            direct.receipt_hash216,
            reversed_gate.receipt_hash216,
        )

    def test_repeat_until_allows_extra_executions_but_never_too_few(self):
        accepted = candidate_from_counts(
            {"00": 5, "0*": 2},
            shots_requested=5,
            repeat_until_shots_requested=True,
        )
        self.assertEqual(accepted.rounds[0].shots_observed, 7)
        with self.assertRaises(Pass220I068DWaveBridgeError):
            candidate_from_counts(
                {"00": 4},
                shots_requested=5,
                repeat_until_shots_requested=True,
            )
        with self.assertRaises(Pass220I068DWaveBridgeError):
            candidate_from_counts(
                {"00": 6},
                shots_requested=5,
                repeat_until_shots_requested=False,
            )

    def test_multi_round_measurements_require_common_shot_count(self):
        accepted = candidate_from_counts(
            [
                {"00": 2, "0*": 1},
                {"11": 1, "**": 2},
            ],
            shots_requested=3,
        )
        self.assertEqual(len(accepted.rounds), 2)
        self.assertTrue(
            all(r.shots_observed == 3 for r in accepted.rounds)
        )
        with self.assertRaises(Pass220I068DWaveBridgeError):
            candidate_from_counts(
                [
                    {"00": 2},
                    {"11": 3},
                ],
                shots_requested=2,
            )

    def test_ideal_mode_accepts_clean_counts_and_rejects_erasure(self):
        clean = candidate_from_counts(
            {"00": 2, "11": 1},
            noise_model=False,
        )
        self.assertEqual(clean.rounds[0].erased_shots, 0)
        with self.assertRaises(Pass220I068DWaveBridgeError):
            candidate_from_counts(
                {"00": 2, "0*": 1},
                noise_model=False,
            )

    def test_post_selected_only_transcript_fails_closed(self):
        with self.assertRaises(Pass220I068DWaveBridgeError):
            transcribe_dwave_counts(
                counts={"00": 3},
                register_order=("q0", "q1"),
                gate=gate(),
                qpu="DRsim_21qubits",
                noise_model=True,
                shots_requested=3,
                program_hash72=program_hash(),
                post_selected=True,
            )

    def test_leap_result_surface_explicitly_requests_unfiltered_counts(self):
        result = FakeResult(
            [{"00": 2, "0*": 1}],
            ["q0", "q1"],
        )
        candidate = transcribe_leap_result(
            result,
            gate=gate(),
            qpu="DRsim_21qubits",
            noise_model=True,
            shots_requested=3,
            program_hash=program_hash(),
        )
        self.assertEqual(result.post_select_args, [False])
        self.assertEqual(candidate.rounds[0].erased_shots, 1)

    def test_mced_events_are_typed_and_receipt_bound(self):
        first = candidate_from_counts(
            {"00": 2, "0*": 1},
            mced_events=(MCEDSignal(0, 2, "q1", 1),),
        )
        second = candidate_from_counts(
            {"00": 2, "0*": 1},
            mced_events=(MCEDSignal(0, 1, "q1", 1),),
        )
        self.assertNotEqual(first.result_hash72, second.result_hash72)
        self.assertNotEqual(
            first.receipt_hash216,
            second.receipt_hash216,
        )
        with self.assertRaises(Pass220I068DWaveBridgeError):
            MCEDSignal(0, 0, "q0", 2)
        with self.assertRaises(Pass220I068DWaveBridgeError):
            MCEDSignal(-1, 0, "q0", 1)

    def test_configuration_fields_are_receipt_sensitive(self):
        base = candidate_from_counts({"00": 2})
        qpu = candidate_from_counts(
            {"00": 2},
            qpu="DRsim_17qubits",
        )
        program = candidate_from_counts(
            {"00": 2},
            program_tag="other-program",
        )
        self.assertNotEqual(base.config_hash72, qpu.config_hash72)
        self.assertNotEqual(base.config_hash72, program.config_hash72)
        self.assertNotEqual(
            base.receipt_hash216,
            qpu.receipt_hash216,
        )
        self.assertNotEqual(
            base.receipt_hash216,
            program.receipt_hash216,
        )

    def test_result_counts_are_receipt_sensitive(self):
        first = candidate_from_counts({"00": 2, "11": 1})
        second = candidate_from_counts({"00": 1, "11": 2})
        self.assertEqual(first.config_hash72, second.config_hash72)
        self.assertNotEqual(first.result_hash72, second.result_hash72)
        self.assertNotEqual(
            first.receipt_hash216,
            second.receipt_hash216,
        )

    def test_receipt_is_deterministic_under_exact_replay(self):
        first = candidate_from_counts(
            {"00": 4, "0*": 2, "*1": 1},
            mced_events=(MCEDSignal(0, 4, "q1", 1),),
        )
        second = candidate_from_counts(
            {"*1": 1, "0*": 2, "00": 4},
            mced_events=(MCEDSignal(0, 4, "q1", 1),),
        )
        self.assertEqual(
            first.receipt_hash216,
            second.receipt_hash216,
        )

    def test_unknown_qpu_is_visible_but_not_promoted(self):
        candidate = candidate_from_counts(
            {"00": 1},
            qpu="external-candidate-qpu",
        )
        self.assertFalse(candidate.documented_beta_qpu)
        self.assertNotIn(
            candidate.qpu,
            DOCUMENTED_BETA_QPUS,
        )
        self.assertTrue(candidate.authority["candidate_only"])

    def test_documented_beta_qpus_are_classified_without_authority_change(self):
        for qpu in DOCUMENTED_BETA_QPUS:
            candidate = candidate_from_counts(
                {"00": 1},
                qpu=qpu,
            )
            self.assertTrue(candidate.documented_beta_qpu)
            self.assertEqual(
                dict(candidate.authority),
                AUTHORITY_BOUNDARY,
            )

    def test_vm81_exact_comparison_positive_path(self):
        candidate = candidate_from_counts(
            {"00": 2, "0*": 1, "*1": 2},
        )
        receipt = (
            hash72("prev")
            + hash72("state")
            + hash72("receipt")
        )
        witness = compare_with_vm81_histogram(
            candidate,
            canonical_histogram=dict(
                candidate.rounds[0].i027_outcome_histogram
            ),
            canonical_vm81_receipt_hash216=receipt,
        )
        self.assertTrue(witness.sample_count_equal)
        self.assertTrue(witness.exact_histogram_equal)
        self.assertTrue(
            all(
                delta == 0
                for _, delta in witness.delta_histogram
            )
        )
        self.assertFalse(witness.canonical_mutation_authority)
        self.assertFalse(witness.hash72_commit_authority)
        self.assertFalse(witness.hash216_commit_authority)

    def test_vm81_exact_comparison_detects_same_count_distribution_mismatch(self):
        candidate = candidate_from_counts(
            {"00": 2, "11": 1},
        )
        receipt = (
            hash72("prev")
            + hash72("state")
            + hash72("receipt")
        )
        canonical = dict(
            candidate.rounds[0].i027_outcome_histogram
        )
        canonical[0] -= 1
        canonical[4] += 1
        witness = compare_with_vm81_histogram(
            candidate,
            canonical_histogram=canonical,
            canonical_vm81_receipt_hash216=receipt,
        )
        self.assertTrue(witness.sample_count_equal)
        self.assertFalse(witness.exact_histogram_equal)
        self.assertTrue(
            any(
                delta != 0
                for _, delta in witness.delta_histogram
            )
        )

    def test_vm81_exact_comparison_detects_sample_count_mismatch(self):
        candidate = candidate_from_counts({"00": 2})
        receipt = (
            hash72("prev")
            + hash72("state")
            + hash72("receipt")
        )
        witness = compare_with_vm81_histogram(
            candidate,
            canonical_histogram={0: 1},
            canonical_vm81_receipt_hash216=receipt,
        )
        self.assertFalse(witness.sample_count_equal)
        self.assertFalse(witness.exact_histogram_equal)

    def test_vm81_comparison_rejects_invalid_inputs(self):
        candidate = candidate_from_counts({"00": 1})
        valid_receipt = (
            hash72("prev")
            + hash72("state")
            + hash72("receipt")
        )
        with self.assertRaises(Pass220I068DWaveBridgeError):
            compare_with_vm81_histogram(
                candidate,
                canonical_histogram={9: 1},
                canonical_vm81_receipt_hash216=valid_receipt,
            )
        with self.assertRaises(Pass220I068DWaveBridgeError):
            compare_with_vm81_histogram(
                candidate,
                canonical_histogram={0: 1},
                canonical_vm81_receipt_hash216="short",
            )

    def test_float_values_are_rejected_recursively(self):
        with self.assertRaises(Pass220I068DWaveBridgeError):
            hash72(
                {
                    "outer": {
                        "inner": [
                            1,
                            {"runtime_seconds": 0.5},
                        ]
                    }
                }
            )

    def test_malformed_measurement_surfaces_fail_closed(self):
        malformed_cases = (
            dict(
                counts={"000": 1},
                register_order=("q0", "q1"),
            ),
            dict(
                counts={"0x": 1},
                register_order=("q0", "q1"),
            ),
            dict(
                counts={"00": 1},
                register_order=("q0", "q0"),
            ),
        )
        for case in malformed_cases:
            with self.assertRaises(Pass220I068DWaveBridgeError):
                transcribe_dwave_counts(
                    counts=case["counts"],
                    register_order=case["register_order"],
                    gate=gate(),
                    qpu="DRsim_21qubits",
                    noise_model=True,
                    shots_requested=1,
                    program_hash72=program_hash(),
                )

    def test_missing_gate_register_fails_closed(self):
        with self.assertRaises(Pass220I068DWaveBridgeError):
            transcribe_dwave_counts(
                counts={"00": 1},
                register_order=("q0", "q2"),
                gate=gate(),
                qpu="DRsim_21qubits",
                noise_model=True,
                shots_requested=1,
                program_hash72=program_hash(),
            )

    def test_invalid_program_hash_fails_closed(self):
        for invalid in ("A" * 71, "~" * 72):
            with self.assertRaises(Pass220I068DWaveBridgeError):
                transcribe_dwave_counts(
                    counts={"00": 1},
                    register_order=("q0", "q1"),
                    gate=gate(),
                    qpu="DRsim_21qubits",
                    noise_model=True,
                    shots_requested=1,
                    program_hash72=invalid,
                )

    def test_authority_boundary_is_stable_across_all_pair_classes(self):
        for key in PAIR_KEYS:
            candidate = candidate_from_counts({key: 1})
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


if __name__ == "__main__":
    unittest.main()
