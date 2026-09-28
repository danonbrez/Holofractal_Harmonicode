from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_priority_offset_information_translation_v1 import (
    HNAN_ZERO_EMPTYSET_CENTER_SOURCE,
    HHSInformationTranslationError,
    PRIORITY_DEFAULT,
    REFERENCE_FALLBACK,
    build_cross_layer_information_witness,
    channel_information_translation_witness,
    hnan_information_gate_witness,
    performance_support_witness,
    priority_default_decision,
)

EVIDENCE = Path(
    "evidence/pass220/PASS_220_NUMPY1_FOUR_PHASE_AB_MEASURED_RESULT_20260928.json"
)


@pytest.fixture(scope="module")
def information():
    return build_cross_layer_information_witness()


def test_cross_layer_translation_preserves_complete_information(information):
    assert information["information_preservation_closed"] is True
    assert information["priority_default_eligible"] is True
    assert information["information_preservation_is_primary_gate"] is True
    assert information["speed_is_supporting_evidence_only"] is True
    assert information["fallback_required_on_any_information_failure"] is True


@pytest.mark.parametrize("channel", ("xy", "yx", "zw", "wz"))
def test_each_ordered_channel_preserves_payload_phase_rotation_and_provenance(
    channel,
):
    witness = channel_information_translation_witness(channel)
    checks = witness["checks"]
    assert witness["information_preserved"] is True
    assert checks["complete_tagged_state_equal"] is True
    assert checks["payload_values_equal"] is True
    assert checks["phase_history_equal"] is True
    assert checks["rotation_history_equal"] is True
    assert checks["source_provenance_equal"] is True
    assert checks["inverse_recovers_complete_tagged_source"] is True
    assert checks["inverse_provenance_exact"] is True
    assert checks["zero_provenance_inverse_exact"] is True


@pytest.mark.parametrize("channel", ("xy", "yx", "zw", "wz"))
def test_each_channel_preserves_5184_rna_and_qudit_identity(channel):
    witness = channel_information_translation_witness(channel)
    checks = witness["checks"]
    assert checks["serialized_5184_equal"] is True
    assert checks["serialized_5184_width_exact"] is True
    assert checks["serialized_5184_inverse_exact"] is True
    assert checks["serialized_deserialize_exact"] is True
    assert checks["rna_phase_locked_both"] is True
    assert checks["rna_state_identity_equal"] is True
    assert checks["rna_ordered_phase_binding_equal"] is True
    assert checks["rna_ordered_products_not_collapsed"] is True
    assert checks["rna_xy_yx_zw_wz_exact"] is True
    assert checks["qudit_serialization_identity_equal"] is True
    assert checks["qudit_source_manifold_identity_equal"] is True
    assert checks["qudit_position_bijection_equal"] is True
    assert checks["qudit_topology_equal"] is True
    assert checks["qudit_reconstruction_exact"] is True


def test_hnan_is_mandatory_information_gate():
    witness = hnan_information_gate_witness()
    assert witness["status"] == "PASS"
    assert (
        HNAN_ZERO_EMPTYSET_CENTER_SOURCE
        == "0=∅=HNAN=x+y-z-w+xy+yx-zw-wz"
    )
    assert (
        witness["explicit_zero_emptyset_hnan_center_source"]
        == "0=∅=HNAN=x+y-z-w+xy+yx-zw-wz"
    )
    assert (
        witness["inherited_ab_over_p4_zero_closure_source"]
        == "0=∅=AB/P⁴∅=HNAN"
    )
    assert witness["center_expression"] == "x+y-z-w+xy+yx-zw-wz"
    assert witness["terminal_source"] == "xy+epsilon"
    assert witness["bare_xy_terminal_authorized"] is False
    assert witness["epsilon_elision_authorized"] is False
    assert witness["ordered_product_commutation_authorized"] is False
    assert witness["checks"]["center_expression_bound"] is True
    assert (
        witness["checks"]["explicit_zero_emptyset_hnan_center_identity"]
        is True
    )
    assert (
        witness["checks"]["explicit_hnan_center_matches_receipt_center"]
        is True
    )
    assert (
        witness["checks"]["inherited_ab_over_p4_zero_closure_preserved"]
        is True
    )


def test_cross_layer_witness_requires_supplied_u9_circuit_tensor(information):
    checks = information["checks"]
    assert checks["supplied_u9_circuit_tensor_pass"] is True
    assert checks["u9_power_9_identity"] is True
    assert checks["u9_payload_verbatim"] is True
    assert checks["u9_slot_provenance_preserved"] is True


def test_measured_speed_supports_but_does_not_replace_information_gate():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    performance = performance_support_witness(evidence)
    assert performance["supports_priority_default"] is True
    assert performance["all_four_channels_compact_faster_on_median"] is True
    assert performance["timing_is_canonical"] is False

    information = build_cross_layer_information_witness()
    decision = priority_default_decision(information, performance)
    assert decision["status"] == "PROMOTE_PRIORITY_DEFAULT"
    assert decision["selected_representation"] == PRIORITY_DEFAULT
    assert decision["information_preservation_pass"] is True
    assert decision["performance_support_pass"] is True
    assert decision["speed_alone_can_promote"] is False


def test_information_preservation_without_speed_is_not_full_promotion(information):
    decision = priority_default_decision(information)
    assert (
        decision["status"]
        == "INFORMATION_PRESERVED_PERFORMANCE_PENDING"
    )
    assert decision["selected_representation"] == REFERENCE_FALLBACK


def test_hnan_information_loss_forces_dense_fallback(information):
    tampered = deepcopy(information)
    tampered["information_preservation_closed"] = False
    tampered["priority_default_eligible"] = False
    performance = performance_support_witness(
        json.loads(EVIDENCE.read_text(encoding="utf-8"))
    )
    decision = priority_default_decision(tampered, performance)
    assert decision["status"] == "FALL_BACK_TO_DENSE_REFERENCE"
    assert decision["selected_representation"] == REFERENCE_FALLBACK
    assert decision["fallback_on_information_loss"] is True


def test_bad_performance_evidence_cannot_override_information_gate():
    bad = {
        "schema": "WRONG",
    }
    with pytest.raises(
        HHSInformationTranslationError,
        match="evidence schema mismatch",
    ):
        performance_support_witness(bad)


def test_no_authority_expansion(information):
    assert information["canonical_vm81_mutation_authority"] is False
    assert information["canonical_hash72_authority"] is False
    assert information["canonical_hash216_authority"] is False
    for witness in information["channels"].values():
        assert witness["canonical_vm81_mutation_authority"] is False
        assert witness["canonical_hash72_authority"] is False
        assert witness["canonical_hash216_authority"] is False



def test_cross_layer_promotion_requires_explicit_hnan_zero_center_identity(information):
    assert (
        information["checks"]["hnan_explicit_zero_emptyset_center_identity"]
        is True
    )
    assert (
        information["checks"]["hnan_inherited_ab_over_p4_zero_closure"]
        is True
    )
