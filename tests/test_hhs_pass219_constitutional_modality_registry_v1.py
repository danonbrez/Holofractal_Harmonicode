from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import EthicsState
from hhs_runtime.hhs_pass219_constitutional_modality_registry_v1 import (
    BASE_INVARIANTS,
    CONSEQUENTIAL_MODALITIES,
    ModalityContract,
    ModalityRole,
    authority_topology,
    build_full_preservation_trace,
    build_modality_trace,
    get_modality_contract,
)


def test_registry_preserves_singleton_vm81_mutation_authority():
    topology = authority_topology()
    assert topology["singleton_authority_preserved"] is True
    assert topology["canonical_mutation_modalities"] == ("vm81_singleton_admission",)
    assert "hash72_receipt" in topology["non_authoritative_modalities"]
    assert "hash216_archive" in topology["non_authoritative_modalities"]
    assert "gpu_candidate" in topology["non_authoritative_modalities"]
    assert "vector_cache" in topology["non_authoritative_modalities"]


def test_noncanonical_modality_cannot_be_constructed_with_mutation_authority():
    with pytest.raises(ValueError, match="non-canonical modality"):
        ModalityContract(
            modality_id="gpu_candidate",
            role=ModalityRole.CANDIDATE,
            mutation_authority=True,
            required_invariants=BASE_INVARIANTS,
        )


def test_unknown_consequential_modality_fails_closed():
    with pytest.raises(ValueError, match="unregistered consequential modality"):
        get_modality_contract("unregistered_future_surface")


def test_full_preservation_trace_is_complete_for_each_registered_surface():
    for modality_id in CONSEQUENTIAL_MODALITIES:
        trace = build_full_preservation_trace(modality_id)
        assert trace.local_state is EthicsState.PASS
        assert trace.preservation_complete is True
        assert set(trace.mandatory_invariants_present).issubset(
            set(trace.mandatory_invariants_preserved)
        )


def test_cross_modal_constraint_loss_is_detectable():
    trace = build_modality_trace(
        "summarization_translation",
        local_state=EthicsState.PASS,
        preserved_invariants=("TRUTH_OVER_USEFUL_FALSEHOOD",),
    )
    assert trace.preservation_complete is False


def test_transport_with_provenance_loss_is_not_complete():
    trace = build_modality_trace(
        "serialization_bytecode",
        local_state=EthicsState.PASS,
        preserved_invariants=BASE_INVARIANTS,
        provenance_preserved=False,
    )
    assert trace.preservation_complete is False


def test_gpu_candidate_remains_candidate_only():
    contract = get_modality_contract("gpu_candidate")
    assert contract.role is ModalityRole.CANDIDATE
    assert contract.mutation_authority is False


def test_hash72_and_hash216_are_evidence_archive_not_authority():
    hash72 = get_modality_contract("hash72_receipt")
    hash216 = get_modality_contract("hash216_archive")
    assert hash72.role is ModalityRole.EVIDENCE
    assert hash72.mutation_authority is False
    assert hash216.role is ModalityRole.ARCHIVE
    assert hash216.mutation_authority is False
