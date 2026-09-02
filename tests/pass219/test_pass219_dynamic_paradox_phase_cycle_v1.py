from __future__ import annotations

from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass219_dynamic_paradox_phase_cycle_v1 import (
    MANIFOLD_CARDINALITY,
    analyze_paradox,
    boolean_negation_cycle,
    canonical_random_guess_paradox,
    exact_work_model,
    fixed_point_valid_option_indices,
    h36_identity_witness,
    probability_map,
)


OPTIONS = (Fraction(1, 4), Fraction(0), Fraction(1, 2), Fraction(1, 4))


def test_object_level_has_no_fixed_point_option() -> None:
    assert fixed_point_valid_option_indices(OPTIONS) == ()
    assert probability_map(OPTIONS, Fraction(0)) == Fraction(1, 4)
    assert probability_map(OPTIONS, Fraction(1, 4)) == Fraction(1, 2)
    assert probability_map(OPTIONS, Fraction(1, 2)) == Fraction(1, 4)


def test_b_zero_is_transient_not_object_level_correct_answer() -> None:
    witness = canonical_random_guess_paradox()
    assert witness.object_has_fixed_point is False
    assert witness.seed_option_object_correct is False
    assert witness.trajectory == (
        Fraction(0),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(1, 4),
    )
    assert witness.preperiod == 1
    assert witness.period == 2


def test_meta_zero_is_typed_empty_set_closure_only() -> None:
    witness = canonical_random_guess_paradox()
    assert witness.meta_empty_valid_set is True
    assert witness.meta_probability == Fraction(0)
    assert witness.seed_candidate_trinary == -1
    assert witness.cycle_motion_trinary == 1
    assert witness.meta_closure_trinary == 0
    assert witness.typed_level_separation_preserved is True
    assert witness.canonical_mutation_authority is False
    assert witness.canonical_hash72_authority is False
    assert witness.canonical_persistence_authority is False
    assert witness.floating_point_authority is False


def test_meta_zero_cannot_be_promoted_back_to_object_truth() -> None:
    with pytest.raises(ValueError, match="TYPE_LEVEL_CONFLATION"):
        analyze_paradox(
            OPTIONS,
            seed_index=1,
            promote_meta_zero_to_object_correct=True,
        )


def test_boolean_negation_is_period_two_when_given_temporal_semantics() -> None:
    assert boolean_negation_cycle(0) == (0, 1, 0)
    assert boolean_negation_cycle(1) == (1, 0, 1)


def test_h36_identity_is_exact_and_finite() -> None:
    witness = h36_identity_witness()
    assert witness["lhs_numerator"] == 72
    assert witness["lhs_denominator"] == 2
    assert witness["lhs_value"] == 36
    assert witness["rhs_value"] == 36
    assert witness["h36_value"] == 36
    assert witness["identity_equal"] is True
    assert witness["manifold_cardinality"] == 722_204_136_308_736
    assert witness["manifold_cardinality"] == MANIFOLD_CARDINALITY
    assert witness["manifold_cardinality_equal"] is True
    assert witness["canonical_mutation_authority"] is False
    assert witness["floating_point_authority"] is False


def test_exact_work_model_closes_before_full_recursive_bound() -> None:
    work = exact_work_model(evaluation_count=1)
    assert work["finite_visit_bound"] == 6
    assert work["actual_transitions"] == 3
    assert work["baseline_per_evaluation"] == 120
    assert work["optimized_per_evaluation"] == 33
    assert work["exact_work_saved"] == 87
    assert work["reduction_permille_floor"] == 725
    assert work["timing_is_canonical"] is False
    assert work["canonical_authority_changed"] is False
