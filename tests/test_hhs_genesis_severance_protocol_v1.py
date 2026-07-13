import copy
import pytest

from hhs_runtime.hhs_genesis_severance_protocol_v1 import (
    CANONICAL_BOUNDARY_FIELD_ORDER,
    GENESIS_SEVERED_PRIVACY,
    WITNESSED_CONTINUITY,
    REJECT_BOUNDARY_FIELD_FLOAT_VALUE,
    REJECT_CHILD_PUBLIC_POINTER_IN_OPAQUE_SEVERANCE,
    REJECT_HIDDEN_PARENT_POINTER_IN_PHASE_INVERTED_RECORD,
    REJECT_OPAQUE_TRANSFORM_EMBEDDED_IN_IMMUTABLE_TRACE,
    REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM,
    REJECT_REVERSIBLE_PARENT_MAPPING_IN_PHASE_INVERTED_RECORD,
    canonical_boundary_fields,
    commit_value,
    genesis_severance_protocol_self_test,
    make_phase_inversion_severance_witness,
    validate_boundary_fields,
    validate_phase_inversion_severance_witness,
)


def _sample_witness():
    parent = {"schema": "PARENT", "phase": WITNESSED_CONTINUITY, "commitment": "parent"}
    seed = {"schema": "SEED", "seed_material_commitment": "seed"}
    return make_phase_inversion_severance_witness(parent_record=parent, new_genesis_seed=seed)


def test_canonical_boundary_fields_are_complete_and_ordered():
    fields = canonical_boundary_fields(
        parent_record_commitment="PARENT72",
        new_genesis_seed_commitment="SEED72",
    )
    assert tuple(fields.keys()) == CANONICAL_BOUNDARY_FIELD_ORDER
    assert len(fields) == len(CANONICAL_BOUNDARY_FIELD_ORDER)
    assert fields["parent_phase"] == WITNESSED_CONTINUITY
    assert fields["child_phase"] == GENESIS_SEVERED_PRIVACY
    assert fields["parent_trace_continued"] is False
    assert fields["opaque_transform_embedded"] is False
    assert fields["child_public_pointer"] is None
    assert fields["resonator_constant_q"] == "179971179971/1000000"
    assert fields["closure_constant_q"] == "1001/1000"


def test_boundary_witness_hash_is_deterministic():
    first = _sample_witness()
    second = _sample_witness()
    assert first["boundary_witness_hash72"] == second["boundary_witness_hash72"]
    assert len(first["boundary_witness_hash72"]) == 72
    assert validate_phase_inversion_severance_witness(first)["ok"] is True


def test_boundary_witness_rejects_float_fields():
    fields = canonical_boundary_fields(
        parent_record_commitment="PARENT72",
        new_genesis_seed_commitment="SEED72",
    )
    fields["loshu_anchor"] = 5.0
    result = validate_boundary_fields(fields)
    assert result["status"] == REJECT_BOUNDARY_FIELD_FLOAT_VALUE


def test_commit_value_rejects_float_source_material():
    with pytest.raises(ValueError):
        commit_value({"bad_float": 1.001})


def test_parent_manifold_allows_only_minimal_severance_witness():
    witness = _sample_witness()
    assert witness["parent_trace_continued"] is False
    assert witness["opaque_transform_embedded"] is False
    assert witness["reversible_mapping_stored"] is False
    assert witness["hidden_parent_pointer_stored"] is False
    assert witness["child_public_pointer"] is None
    assert "opaque_transform" not in witness
    assert "reversible_mapping" not in witness
    assert "hidden_parent_pointer" not in witness


def test_rejects_parent_trace_continuity_inside_privacy_boundary():
    witness = _sample_witness()
    fields = copy.deepcopy(witness["canonical_boundary_fields"])
    fields["parent_trace_continued"] = True
    result = validate_boundary_fields(fields)
    assert result["status"] == REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM


def test_rejects_embedded_opaque_transform_inside_parent_manifold():
    witness = _sample_witness()
    bad = dict(witness)
    bad["opaque_transform"] = {"recipe": "forbidden"}
    result = validate_phase_inversion_severance_witness(bad)
    assert result["status"] == REJECT_OPAQUE_TRANSFORM_EMBEDDED_IN_IMMUTABLE_TRACE


def test_rejects_child_public_pointer_reversible_mapping_and_hidden_parent_pointer():
    fields = canonical_boundary_fields(
        parent_record_commitment="PARENT72",
        new_genesis_seed_commitment="SEED72",
    )
    with_child = copy.deepcopy(fields)
    with_child["child_public_pointer"] = "child://public"
    assert validate_boundary_fields(with_child)["status"] == REJECT_CHILD_PUBLIC_POINTER_IN_OPAQUE_SEVERANCE

    with_mapping = copy.deepcopy(fields)
    with_mapping["reversible_mapping_stored"] = True
    assert validate_boundary_fields(with_mapping)["status"] == REJECT_REVERSIBLE_PARENT_MAPPING_IN_PHASE_INVERTED_RECORD

    with_hidden_parent = copy.deepcopy(fields)
    with_hidden_parent["hidden_parent_pointer_stored"] = True
    assert validate_boundary_fields(with_hidden_parent)["status"] == REJECT_HIDDEN_PARENT_POINTER_IN_PHASE_INVERTED_RECORD


def test_hash_mismatch_is_rejected():
    witness = _sample_witness()
    tampered = copy.deepcopy(witness)
    tampered["boundary_witness_hash72"] = "X" * 72
    result = validate_phase_inversion_severance_witness(tampered)
    assert result["status"] == "REJECT_BOUNDARY_WITNESS_HASH_MISMATCH"


def test_genesis_severance_protocol_self_test_passes():
    result = genesis_severance_protocol_self_test()
    assert result["ok"] is True
    assert result["canonical_boundary_field_count"] == len(CANONICAL_BOUNDARY_FIELD_ORDER)
