"""Pass220 I089 dependency-scoped original RML4/RML11/VM81/Hash216 tests."""
from __future__ import annotations

import pytest

from hhs_runtime import hhs_pass220_i089_rml4_rml11_vm81_hash216_candidate_binding_v1 as mod
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
)
from hhs_runtime.hhs_pass220_i070_i_tensor_lane5_vm81_bridge_v1 import (
    build_lane5_vm81_candidate, validate_lane5_vm81_candidate,
)
from hhs_runtime.pass219.phase_clifford_intertwiner import (
    _channel_action_matrices,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import PRODUCT_RELATIONS


def test_original_rml4_state_has_admissible_exact_signed_72_phase_geometry():
    state=mod._state()
    assert state["admissible_product_geometry"] is True
    assert tuple(state["phases"])==mod.PHASE8
    assert state["quarter_turn_signs"]==mod.ORIGINAL_SIGNED_PAIRS
    for name in ("xy","yx","zw","wz"):
        generator=PRODUCT_RELATIONS[name]["generator"]
        assert state["phases"][name] == (
            state["phases"][generator]+18*mod.ORIGINAL_SIGNED_PAIRS[name]
        )%72
    assert state["canonical_vm81_mutation_authority"] is False


def test_original_rml11_all_eight_quarter_actions_are_exact_and_typed():
    _,rows=mod._eight_original_quarter_channel_bindings(mod._state())
    assert len(rows)==8
    assert tuple(row["channel"] for row in rows)==mod.PHASE8
    actions=_channel_action_matrices()
    for row in rows:
        assert row["actual_original_clifford_matrix_sha256"] is not None
        assert len(row["original_phase_transport_sha256"])==64
        assert row["exact_quarter_turn_complete"] is True
        assert row["reverse_original_order_inverse_verified"] is True
        assert row["phase_residual"]==0
        assert row["quarter_turn_phase_steps"]==18
        assert row["native_full_u72_lift_proven"] is False
    assert actions["xy"]!=actions["yx"]
    assert actions["zw"]!=actions["wz"]


def test_actual_original_i070_and_i065_receipt_composition():
    r=mod.bind_i089_original_phase_vm81_candidate(0,phase_channel=0)
    assert r["schema"]==mod.SCHEMA
    assert r["i086_literal_source"]==mod.MATRIX_SOURCE
    assert len(r["i088_exact_word_quotient_sha256"])==64
    assert r["i088_52term_original_clifford_quotient_replayed"] is True
    assert r["rml11_exact_u18_channel_action_fidelity_all8_proven"] is True
    assert r["original_i071_exact_phase_slots"]==72
    assert r["original_i071_nucleus"]==0
    assert r["original_i071_phase_slot_for_center"]==4
    assert r["original_i065_three_plane_hydration_roundtrip"] is True
    assert r["original_i065_hydration_plane_count"]==3
    assert r["source_bound_candidate_hash216"] == (
        r["source_bound_previous_hash72"]
        + r["source_bound_change_hash72"]
        + r["source_bound_receipt_hash72"]
    )
    assert len(r["source_bound_candidate_hash216"])==216
    for key in (
        "source_bound_previous_hash72",
        "source_bound_change_hash72",
        "source_bound_receipt_hash72",
    ):
        assert len(r[key])==72
    original=build_lane5_vm81_candidate(0)
    assert validate_lane5_vm81_candidate(original) is True
    assert r["original_i070_vm81_candidate_binding_hash72"] == original["binding_hash72"]
    assert r["original_i070_candidate_hash216"] == original["candidate_hash216"]
    assert hydrate_hash216_geometry(
        r["source_bound_candidate_hash216"]
    )["roundtrip_exact"] is True


def test_positive_u18_and_unresolved_u19_residual_keep_distinct_receipts():
    full=mod.bind_i089_original_phase_vm81_candidate(
        2,phase_channel=5,residual_probe_steps=18
    )
    partial=mod.bind_i089_original_phase_vm81_candidate(
        2,phase_channel=5,residual_probe_steps=19
    )
    a=full["rml11_residual_probe"]
    b=partial["rml11_residual_probe"]
    assert a["channel"]==b["channel"]=="yx"
    assert a["quarter_units"]==b["quarter_units"]==1
    assert a["residual_steps"]==0
    assert b["residual_steps"]==1
    assert a["complete_clifford_lift"] is True
    assert b["complete_clifford_lift"] is False
    assert a["remaining_native_u72_phase_preserved"] is False
    assert b["remaining_native_u72_phase_preserved"] is True
    assert full["source_bound_change_hash72"] != partial["source_bound_change_hash72"]
    assert full["source_bound_candidate_hash216"] != partial["source_bound_candidate_hash216"]


def test_real_nucleus_and_phase_position_are_source_bound():
    for nucleus,channel in ((0,0),(4,6),(8,7)):
        r=mod.bind_i089_original_phase_vm81_candidate(
            nucleus,phase_channel=channel,residual_probe_steps=18
        )
        assert r["original_i071_nucleus"]==nucleus
        assert r["original_i071_phase_slot_for_center"]==9*channel+4
        assert r["source_bound_candidate_hash216"]!=r["original_i070_candidate_hash216"]


@pytest.mark.parametrize("nucleus,channel,steps",[
    (-1,0,18),(9,0,18),(False,0,18),(0,-1,18),
    (0,8,18),(0,True,18),(0,0,0),(0,0,17),
    (0,0,20),(0,0,18.0),
])
def test_bad_cell_phase_or_nonquarter_probe_fails_closed(nucleus,channel,steps):
    with pytest.raises(mod.I089CandidateBindingError):
        mod.bind_i089_original_phase_vm81_candidate(
            nucleus,phase_channel=channel,residual_probe_steps=steps
        )


def test_no_candidate_is_promoted_to_native_signed_mutation():
    r=mod.bind_i089_original_phase_vm81_candidate(8,phase_channel=2)
    for field in (
        "complete_vm81_to_clifford_algebra_faithfulness_proven",
        "complete_u72_root_transport_proven",
        "native_wx_vm81_operator_registered",
        "native_full_matrix_division_admitted",
        "canonical_hash72_minted",
        "canonical_hash216_transition_committed",
        "signed_vm81_mutation",
        "floating_point_authority",
    ):
        assert r[field] is False
    assert r["candidate_only"] is True
    assert len(r["native_obligations_still_held"])==7


def test_repeatable_actual_hash216_ancestry_for_same_source_and_phase():
    first=mod.bind_i089_original_phase_vm81_candidate(1,phase_channel=3)
    second=mod.bind_i089_original_phase_vm81_candidate(1,phase_channel=3)
    assert first == second
