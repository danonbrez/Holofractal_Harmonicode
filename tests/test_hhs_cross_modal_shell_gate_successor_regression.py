from __future__ import annotations

from dataclasses import fields

from hhs_runtime.hhs_cross_modal_shell_gate_v1 import (
    CrossModalConsensusReceipt,
    ShellGateStatus,
    cross_modal_consensus,
)


def test_cross_modal_consensus_receipt_schema_matches_successor_constructor():
    names = [field.name for field in fields(CrossModalConsensusReceipt)]
    assert names == [
        "projections",
        "agreed_next_state_hash72",
        "anchor_phase_index",
        "phase_max_distance",
        "distinct_modality_count",
        "min_distinct_modalities",
        "modality_floor_ok",
        "mandatory_witnesses_present",
        "missing_mandatory_witnesses",
        "mandatory_phase_ok",
        "support_phase_ok",
        "weighted_quorum",
        "required_weighted_quorum",
        "weighted_quorum_ok",
        "temporal_ok",
        "phase_consensus_ok",
        "adaptive_trust_profile",
        "delta_e_zero",
        "psi_zero",
        "theta15_true",
        "omega_true",
        "armor_ok",
        "status",
        "receipt_hash72",
        "quarantine_hash72",
        "reason",
    ]


def test_empty_consensus_fails_closed_without_constructor_arity_drift():
    receipt = cross_modal_consensus([])
    assert receipt.status == ShellGateStatus.QUARANTINED
    assert receipt.agreed_next_state_hash72 is None
    assert receipt.anchor_phase_index is None
    assert receipt.phase_max_distance is None
    assert receipt.mandatory_witnesses_present is False
    assert receipt.reason == "mandatory high-priority HARMONICODE witnesses missing"
