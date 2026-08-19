from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import (
    PASS217_I4_ADDRESS_MAP_SHA256,
    PASS217_I4_CANDIDATE_SHA256,
    PASS217_I4_MANIFOLD_ROOT_SHA256,
    PASS217_I4_MATRIX_ROOT_SHA256,
    PASS217_I4_NUCLEUS_IDENTITY_SHA256,
    PASS217_I4_NUCLEUS_SUPPORT_SHA256,
    PASS217_I4_PROTECTED_RUNTIME_BLOB,
    PASS217_I4_RECORD_ROOT,
    _verify_frozen_pass217_i4_evidence,
)


def test_frozen_i4_evidence_is_authenticated_without_requiring_current_runtime_blob_identity() -> None:
    record = _verify_frozen_pass217_i4_evidence()
    assert record["record_root_sha256"] == PASS217_I4_RECORD_ROOT
    assert record["frozen_inputs"]["logical_genesis_candidate"]["sha256"] == PASS217_I4_CANDIDATE_SHA256
    assert record["frozen_inputs"]["address_map"]["sha256"] == PASS217_I4_ADDRESS_MAP_SHA256
    assert record["frozen_inputs"]["protected_vm81_runtime"]["git_blob"] == PASS217_I4_PROTECTED_RUNTIME_BLOB
    assert record["hash72_manifold"]["matrix_root_sha256"] == PASS217_I4_MATRIX_ROOT_SHA256
    assert record["hash72_manifold"]["manifold_root_sha256"] == PASS217_I4_MANIFOLD_ROOT_SHA256
    assert record["immutable_nucleus"]["identity_root_sha256"] == PASS217_I4_NUCLEUS_IDENTITY_SHA256
    assert record["immutable_nucleus"]["support_root_sha256"] == PASS217_I4_NUCLEUS_SUPPORT_SHA256
    assert len(record["hash72_manifold"]["wrapped_directions"]) == 4
    assert all(row["order"] == 72 for row in record["hash72_manifold"]["wrapped_directions"])
    assert record["claim_boundary"]["hash72_manifold_validated"] is True
    assert record["claim_boundary"]["immutable_nucleus_validated"] is True
    assert record["claim_boundary"]["canonical_authority_promoted"] is False
    assert record["claim_boundary"]["runtime_mutation_performed"] is False
    assert record["claim_boundary"]["logical_genesis_rom_generated"] is False
