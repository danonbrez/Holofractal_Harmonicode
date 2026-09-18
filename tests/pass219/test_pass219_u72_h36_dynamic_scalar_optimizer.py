from __future__ import annotations

import os

import pytest

from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    HASH72_DEPTH,
    PHASE_RADIX,
    QUDIT_RADIX,
    GLYPH_RADIX,
    canonical_lo_shu_assembly_fixture,
)
from hhs_runtime.pass219.u72_h36_dynamic_scalar_optimizer import (
    ANCHOR_SLOTS,
    H36_HALF_TURN,
    QUARTER_SLOTS,
    RESONANCE_COORDINATE,
    U72_PERIOD,
    U72H36DynamicScalarOptimizerError,
    build_u72_dynamic_cycle,
    crt_idempotent_basis,
    expected_lane_record_for_slot,
    optimized_replace_coordinate,
    u72_h36_dynamic_scalar_optimizer,
    u72_slot_components,
    validate_dynamic_frame,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    pack_vm81_binding_words,
    raw_le_to_words,
    words_to_raw_le,
)


def test_crt_idempotent_basis_is_exact_at_hash72_depth() -> None:
    basis = crt_idempotent_basis()
    assert basis["depth"] == HASH72_DEPTH
    assert basis["phase_modulus"] == PHASE_RADIX**HASH72_DEPTH
    assert basis["qudit_modulus"] == QUDIT_RADIX**HASH72_DEPTH
    assert basis["combined_modulus"] == GLYPH_RADIX**HASH72_DEPTH
    assert basis["phase_modulus"] * basis["qudit_modulus"] == basis["combined_modulus"]
    assert basis["phase_idempotent"] % basis["phase_modulus"] == 1
    assert basis["phase_idempotent"] % basis["qudit_modulus"] == 0
    assert basis["qudit_idempotent"] % basis["phase_modulus"] == 0
    assert basis["qudit_idempotent"] % basis["qudit_modulus"] == 1
    assert (
        basis["phase_idempotent"] + basis["qudit_idempotent"]
    ) % basis["combined_modulus"] == 1


def test_every_u72_slot_is_same_exact_scalar_and_local_crt_glyph() -> None:
    for slot in range(U72_PERIOD):
        row = u72_slot_components(slot)
        assert row["normalized_slot"] == slot
        assert row["phase_digit"] == slot % PHASE_RADIX
        assert row["qudit_digit"] == slot % QUDIT_RADIX
        assert row["glyph"] == slot

    closure = u72_slot_components(U72_PERIOD)
    assert closure["normalized_slot"] == 0
    assert closure["phase_digit"] == 0
    assert closure["qudit_digit"] == 0
    assert closure["glyph"] == 0


def test_quarter_cycle_and_h36_geometry_are_locked_by_crt() -> None:
    quarter = [u72_slot_components(slot) for slot in QUARTER_SLOTS]
    assert [row["phase_digit"] for row in quarter] == [0, 2, 4, 6]
    assert [row["qudit_digit"] for row in quarter] == [0, 0, 0, 0]

    for slot in range(H36_HALF_TURN):
        left = u72_slot_components(slot)
        right = u72_slot_components(slot + H36_HALF_TURN)
        assert right["qudit_digit"] == left["qudit_digit"]
        assert (right["phase_digit"] - left["phase_digit"]) % PHASE_RADIX == 4
        assert (right["glyph"] - left["glyph"]) % GLYPH_RADIX == H36_HALF_TURN


def test_dynamic_cycle_matches_full_reference_at_every_transition() -> None:
    cycle = build_u72_dynamic_cycle()
    assert len(cycle["states"]) == U72_PERIOD + 1
    assert cycle["full_cycle_closed"] is True
    assert cycle["initial_bigint"] == cycle["final_bigint"]
    assert cycle["optimized_coordinate_updates"] == U72_PERIOD
    assert cycle["reference_coordinate_visits"] == U72_PERIOD * HASH72_DEPTH
    assert cycle["avoided_coordinate_visits"] == U72_PERIOD * (HASH72_DEPTH - 1)
    assert len(cycle["reciprocal_pairs"]) == H36_HALF_TURN
    assert all(row["frame_dependency_exact"] for row in cycle["states"])
    assert [cycle["states"][slot]["glyph"] for slot in QUARTER_SLOTS] == list(QUARTER_SLOTS)


def test_optimized_coordinate_update_rejects_stale_dependency_metadata() -> None:
    fixture = canonical_lo_shu_assembly_fixture()
    bigint = int(fixture["bigint"])
    with pytest.raises(
        U72H36DynamicScalarOptimizerError,
        match="OLD_COORDINATE_MISMATCH",
    ):
        optimized_replace_coordinate(
            bigint,
            RESONANCE_COORDINATE,
            old_phase=1,
            old_qudit=0,
            new_phase=2,
            new_qudit=2,
        )


def test_dynamic_frame_rejects_metadata_not_entailed_by_scalar_slot() -> None:
    cycle = build_u72_dynamic_cycle()
    state = cycle["states"][18]
    words = list(raw_le_to_words(state["raw_bytes"]))

    # Replace the deterministic slot-18 lane binding with the slot-19 binding.
    wrong_lane = expected_lane_record_for_slot(19)
    rebuilt = pack_vm81_binding_words(
        state["bigint"],
        [row for row in raw_le_to_words(state["raw_bytes"])[8:80]],
        wrong_lane,
    )
    words = list(rebuilt)

    with pytest.raises(
        U72H36DynamicScalarOptimizerError,
        match="U72_METADATA_DEPENDENCY_MISMATCH",
    ):
        validate_dynamic_frame(words)


def test_optimizer_report_locks_exact_dynamic_and_h36_closure() -> None:
    report = u72_h36_dynamic_scalar_optimizer()
    geometry = report["exact_geometry"]
    dynamic = report["dynamic_cycle"]
    optimization = report["optimization"]
    authority = report["authority"]

    assert geometry["local_factorization_exact"] is True
    assert geometry["vm5184_factorization_exact"] is True
    assert geometry["h36_scale_exact"] is True
    assert dynamic["full_u72_cycle_closed"] is True
    assert dynamic["every_slot_scalar_equals_local_glyph"] is True
    assert dynamic["quarter_phase_digits"] == [0, 2, 4, 6]
    assert dynamic["quarter_qudit_digits"] == [0, 0, 0, 0]
    assert dynamic["h36_reciprocal_pair_count"] == 36
    assert dynamic["all_h36_pairs_preserve_nonary_and_flip_phase"] is True
    assert optimization["reference_coordinate_visits"] == 5184
    assert optimization["optimized_coordinate_updates"] == 72
    assert optimization["avoided_coordinate_visits"] == 5112
    assert optimization["exact_reference_equality_every_transition"] is True
    assert optimization["new_primitive_algebra_required"] is False
    assert authority["new_canonical_vm81_mutation_authority"] is False
    assert authority["new_canonical_receipt_authority"] is False
    assert authority["floating_point_authority"] is False


def test_candidate_cpp_rna_anchors_when_native_probe_is_available() -> None:
    native_probe = os.environ.get("HHS_PASS219_BIGINT_RNA_NATIVE_PROBE")
    if not native_probe:
        pytest.skip("candidate native probe not supplied")
    report = u72_h36_dynamic_scalar_optimizer(candidate_native_probe=native_probe)
    native = report["candidate_rna_anchors"]
    assert native["anchor_slots"] == list(ANCHOR_SLOTS)
    assert native["all_candidate_routes_green"] is True
    assert len(native["rows"]) == len(ANCHOR_SLOTS)


def test_signed_environmental_anchor_commits_when_native_probe_is_available() -> None:
    native_probe = os.environ.get("HHS_PASS219_BIGINT_ENVIRONMENT_NATIVE_PROBE")
    if not native_probe:
        pytest.skip("signed environmental native probe not supplied")
    report = u72_h36_dynamic_scalar_optimizer(environment_native_probe=native_probe)
    native = report["signed_environment_anchors"]
    assert native["anchor_slots"] == list(ANCHOR_SLOTS)
    assert native["all_signed_environmental_commits_exact"] is True
    assert len(native["rows"]) == len(ANCHOR_SLOTS)
