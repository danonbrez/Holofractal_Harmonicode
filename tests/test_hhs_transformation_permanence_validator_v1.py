from hhs_runtime.hhs_genesis_severance_protocol_v1 import (
    GENESIS_SEVERED_PRIVACY,
    REDACTED_CONTINUITY,
    WITNESSED_CONTINUITY,
    make_phase_inversion_severance_witness,
)
from hhs_runtime.hhs_transformation_permanence_validator_v1 import (
    ADMIT_GENESIS_SEVERED_PRIVACY,
    ADMIT_REDACTED_CONTINUITY,
    ADMIT_WITNESSED_CONTINUITY,
    REJECT_DERIVED_HHS_ENTRY_WITHOUT_PERMANENT_TRANSFORMATION_RECORD,
    REJECT_FALSE_CONTINUITY_PROVENANCE_BYPASS,
    REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM,
    REJECT_PRIVACY_RECORD_WITHOUT_VALID_SEVERANCE_WITNESS,
    REJECT_SUBSTRATE_EQUIVALENCE_AS_IDENTITY_CONTINUITY,
    make_transformation_record,
    transformation_permanence_validator_self_test,
    validate_hhs_derivation,
)


def _source():
    return {"schema": "HHS_SOURCE", "is_hhs_encoded": True, "phase": WITNESSED_CONTINUITY, "commitment": "source"}


def _operation(operation_type="transform"):
    return {"schema": "HHS_OPERATION", "operation_type": operation_type, "operation_id": operation_type}


def _trace(operation_type="transform"):
    return make_transformation_record(source_commitment="source", operation_type=operation_type)


def _severance():
    return make_phase_inversion_severance_witness(
        parent_record={"schema": "PARENT", "phase": WITNESSED_CONTINUITY, "commitment": "source"},
        new_genesis_seed={"schema": "SEED", "seed_material_commitment": "private"},
    )


def test_witnessed_continuity_requires_and_accepts_transformation_trace():
    operation = _operation("enhance")
    output = {
        "schema": "HHS_OUTPUT",
        "phase": WITNESSED_CONTINUITY,
        "claims_continuity_with_source": True,
        "transformation_trace": [_trace("enhance")],
    }
    result = validate_hhs_derivation(source=_source(), output=output, operation=operation)
    assert result["status"] == ADMIT_WITNESSED_CONTINUITY
    assert result["transformation_record_present"] is True


def test_missing_trace_rejects_derived_hhs_entry():
    result = validate_hhs_derivation(
        source=_source(),
        output={"schema": "HHS_OUTPUT", "phase": WITNESSED_CONTINUITY, "claims_continuity_with_source": True},
        operation=_operation("summarize"),
    )
    assert result["status"] == REJECT_DERIVED_HHS_ENTRY_WITHOUT_PERMANENT_TRANSFORMATION_RECORD


def test_redacted_continuity_is_trace_preserving_not_unlinkability():
    operation = _operation("redact")
    output = {
        "schema": "HHS_REDACTED_OUTPUT",
        "phase": REDACTED_CONTINUITY,
        "claims_continuity_with_source": True,
        "transformation_trace": [_trace("redact")],
    }
    result = validate_hhs_derivation(source=_source(), output=output, operation=operation)
    assert result["status"] == ADMIT_REDACTED_CONTINUITY


def test_opaque_privacy_requires_valid_genesis_severance_witness():
    operation = _operation("privatize")
    output = {
        "schema": "HHS_PRIVATE_OUTPUT",
        "phase": GENESIS_SEVERED_PRIVACY,
        "claims_opaque_privacy": True,
        "claims_continuity_with_source": False,
    }
    result = validate_hhs_derivation(source=_source(), output=output, operation=operation, severance_witness=_severance())
    assert result["status"] == ADMIT_GENESIS_SEVERED_PRIVACY
    assert result["new_genesis_required"] is True


def test_opaque_privacy_without_severance_witness_is_rejected():
    result = validate_hhs_derivation(
        source=_source(),
        output={"schema": "HHS_PRIVATE_OUTPUT", "phase": GENESIS_SEVERED_PRIVACY, "claims_opaque_privacy": True},
        operation=_operation("privatize"),
    )
    assert result["status"] == REJECT_PRIVACY_RECORD_WITHOUT_VALID_SEVERANCE_WITNESS


def test_privacy_record_cannot_claim_parent_continuity():
    result = validate_hhs_derivation(
        source=_source(),
        output={
            "schema": "HHS_PRIVATE_OUTPUT",
            "phase": GENESIS_SEVERED_PRIVACY,
            "claims_opaque_privacy": True,
            "claims_continuity_with_source": True,
        },
        operation=_operation("privatize"),
        severance_witness=_severance(),
    )
    assert result["status"] == REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM


def test_same_payload_does_not_equal_same_witness_identity():
    result = validate_hhs_derivation(
        source=_source(),
        output={
            "schema": "HHS_OUTPUT",
            "phase": WITNESSED_CONTINUITY,
            "claims_continuity_with_source": True,
            "same_payload_as_source": True,
        },
        operation=_operation("copy"),
    )
    assert result["status"] == REJECT_SUBSTRATE_EQUIVALENCE_AS_IDENTITY_CONTINUITY


def test_derived_hhs_output_must_choose_continuity_or_genesis():
    result = validate_hhs_derivation(
        source=_source(),
        output={"schema": "HHS_OUTPUT", "phase": WITNESSED_CONTINUITY},
        operation=_operation("ambiguous"),
    )
    assert result["status"] == REJECT_FALSE_CONTINUITY_PROVENANCE_BYPASS


def test_transformation_permanence_self_test_passes():
    result = transformation_permanence_validator_self_test()
    assert result["ok"] is True
