from dataclasses import replace

import pytest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CompiledROMEntry,
    TimestampBoundary,
)
from hhs_runtime.hhs_pass220_quantum_collapse_admission_bridge_v1 import (
    QUANTUM_NATIVE_DISPATCH_ID,
    Pass220I027CollapseAdmissionError,
    bridge_contract_descriptor,
    collapse_address,
    create_quantum_collapse_admission,
    quantum_canonical_operation,
    quantum_operation_id,
)
from hhs_runtime.hhs_pass220_quantum_measurement_projectors_v1 import (
    basis_state,
    collapse_candidate,
)


VALIDATION_KEY = bytes(range(32))
SOURCE_SHA = "a" * 64
PROVISIONAL_ADMISSION_SHA = "b" * 64


def boundary(parent="1" * 64):
    return TimestampBoundary.create(
        kind="open",
        timestamp_ns=1000,
        serial=1,
        genesis_epoch=0,
        group_sequence=1,
        parent_hash216=parent,
        previous_receipt_hash72="c" * 72,
        kernel_measurement_hash216="2" * 64,
    )


def entry_for(outcome=4, nucleus=2):
    address = collapse_address(outcome, nucleus)
    return CompiledROMEntry.create(
        operation_id=quantum_operation_id(address),
        canonical_operation=quantum_canonical_operation(address),
        constraints={"exact": True},
        vm81_cell_id=address.vm81_cell_id,
        operation_slot=7,
        g243_control_id=11,
        native_dispatch_id=QUANTUM_NATIVE_DISPATCH_ID,
        kernel_policy_hash216="3" * 64,
        creation_group_sequence=1,
        creation_open_boundary_hash216="4" * 64,
        creation_close_boundary_hash216="5" * 64,
        closure_path_root_hash216="6" * 64,
        closure_position=0,
        parent_hash216="7" * 64,
    )


def candidate(outcome=4):
    return collapse_candidate(
        basis_state(0),
        outcome,
        source_state_receipt_sha256=SOURCE_SHA,
        admission_witness_sha256=PROVISIONAL_ADMISSION_SHA,
    )


def test_row_major_lo_shu_and_vm81_address_binding():
    address = collapse_address(4, 2)
    assert address.row == 1
    assert address.column == 1
    assert address.lo_shu_value == 5
    assert address.zero_centered_value == 0
    assert address.trinary_sign == 0
    assert address.vm81_cell_id == 22

    first = collapse_address(0, 0)
    last = collapse_address(8, 8)
    assert first.vm81_cell_id == 0
    assert last.vm81_cell_id == 80


def test_real_pass213_parametric_admission_is_created_and_validated():
    collapse = candidate(4)
    opening = boundary()
    admission, binding = create_quantum_collapse_admission(
        collapse_candidate=collapse,
        nucleus_index=2,
        base_entry=entry_for(4, 2),
        opening_boundary=opening,
        validation_key=VALIDATION_KEY,
    )

    assert admission.vm81_cell_id == 22
    assert admission.parent_hash216 == opening.parent_hash216
    assert len(admission.vm81_admission_root_hash216) == 64
    assert binding["pass213_parametric_admission_validated"] is True
    assert binding["row_major_lo_shu_binding_verified"] is True
    assert binding["pass213_vm81_admission_root_hash216"] == (
        admission.vm81_admission_root_hash216
    )


def test_current_native_dispatch_boundary_fails_closed_not_mutated():
    _, binding = create_quantum_collapse_admission(
        collapse_candidate=candidate(4),
        nucleus_index=2,
        base_entry=entry_for(4, 2),
        opening_boundary=boundary(),
        validation_key=VALIDATION_KEY,
    )
    assert binding["status"] == "ADMISSION_BOUND_DISPATCH_BLOCKED"
    assert binding["native_quantum_dispatch_registered"] is False
    assert binding["governed_dispatch_required"] is True
    assert binding["canonical_runtime_mutated"] is False
    assert binding["canonical_collapse_commit_closed"] is False
    assert binding["new_mutation_authority_created"] is False
    assert binding["hash72_minted"] is False
    assert binding["hash216_persisted"] is False


def test_tampered_entry_cell_is_rejected_before_admission():
    good = entry_for(4, 2)
    bad = replace(good, vm81_cell_id=23)
    with pytest.raises(
        Pass220I027CollapseAdmissionError,
        match="VM81 cell",
    ):
        create_quantum_collapse_admission(
            collapse_candidate=candidate(4),
            nucleus_index=2,
            base_entry=bad,
            opening_boundary=boundary(),
            validation_key=VALIDATION_KEY,
        )


def test_tampered_semantic_domain_is_rejected():
    good = entry_for(4, 2)
    op = dict(good.canonical_operation)
    op["semantic_domain"] = "WRONG"
    bad = replace(good, canonical_operation=op)
    with pytest.raises(
        Pass220I027CollapseAdmissionError,
        match="semantic mismatch",
    ):
        create_quantum_collapse_admission(
            collapse_candidate=candidate(4),
            nucleus_index=2,
            base_entry=bad,
            opening_boundary=boundary(),
            validation_key=VALIDATION_KEY,
        )


def test_wrong_native_dispatch_id_is_rejected():
    good = entry_for(4, 2)
    bad = replace(good, native_dispatch_id="hhs.native.u64.add.v1")
    with pytest.raises(
        Pass220I027CollapseAdmissionError,
        match="quantum-collapse native dispatch",
    ):
        create_quantum_collapse_admission(
            collapse_candidate=candidate(4),
            nucleus_index=2,
            base_entry=bad,
            opening_boundary=boundary(),
            validation_key=VALIDATION_KEY,
        )


def test_collapse_outcome_and_entry_address_must_match():
    with pytest.raises(
        Pass220I027CollapseAdmissionError,
        match="operation id",
    ):
        create_quantum_collapse_admission(
            collapse_candidate=candidate(5),
            nucleus_index=2,
            base_entry=entry_for(4, 2),
            opening_boundary=boundary(),
            validation_key=VALIDATION_KEY,
        )


def test_pass213_wrong_validation_key_is_rejected():
    with pytest.raises(Exception):
        create_quantum_collapse_admission(
            collapse_candidate=candidate(4),
            nucleus_index=2,
            base_entry=entry_for(4, 2),
            opening_boundary=boundary(),
            validation_key=b"x",
        )


def test_boolean_and_out_of_range_addresses_fail_closed():
    with pytest.raises(Pass220I027CollapseAdmissionError):
        collapse_address(True, 0)
    with pytest.raises(Pass220I027CollapseAdmissionError):
        collapse_address(9, 0)
    with pytest.raises(Pass220I027CollapseAdmissionError):
        collapse_address(0, 9)


def test_binding_is_deterministic_for_same_inputs():
    kwargs = dict(
        collapse_candidate=candidate(4),
        nucleus_index=2,
        base_entry=entry_for(4, 2),
        opening_boundary=boundary(),
        validation_key=VALIDATION_KEY,
    )
    a1, b1 = create_quantum_collapse_admission(**kwargs)
    a2, b2 = create_quantum_collapse_admission(**kwargs)
    assert a1.to_mapping() == a2.to_mapping()
    assert b1 == b2
    assert b1["receipt_sha256"] == b2["receipt_sha256"]


def test_contract_records_existing_authority_without_promoting_mutation():
    descriptor = bridge_contract_descriptor()
    assert descriptor["lo_shu_ordering"] == "ROW_MAJOR_3X3"
    assert descriptor["vm81_cell_range"] == [0, 80]
    assert descriptor["pass213_parametric_admission_authority"] is True
    assert descriptor["native_quantum_dispatch_registered"] is False
    assert descriptor["canonical_mutation_authority"] is False
    assert descriptor["hash72_mint_authority"] is False
    assert descriptor["hash216_persistence_authority"] is False
    assert descriptor["governed_dispatch_required"] is True
