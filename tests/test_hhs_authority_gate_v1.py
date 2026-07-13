import pytest

from hhs_runtime.hhs_authority_gate_v1 import (
    HASH72_LEN,
    HHSAuthorityViolation,
    assert_runtime_authorized,
    audit_runtime_authority,
)


GOOD_HASH72 = "H" * HASH72_LEN


def test_authority_gate_accepts_committed_zero_drift_transition():
    audit = assert_runtime_authorized(
        {
            "step": 1,
            "transport_flux": 0,
            "orientation_flux": 0,
            "constraint_flux": 0,
            "state_hash72": GOOD_HASH72,
            "receipt_hash72": GOOD_HASH72,
        },
        source="test",
    )

    assert audit.ok is True
    assert audit.delta_e == 0
    assert audit.psi == 0
    assert audit.theta15 is True
    assert audit.omega is True
    assert audit.algebraic_closure is True


def test_authority_gate_rejects_missing_hash72_receipt():
    with pytest.raises(HHSAuthorityViolation):
        assert_runtime_authorized(
            {
                "step": 1,
                "transport_flux": 0,
                "orientation_flux": 0,
                "constraint_flux": 0,
                "state_hash72": GOOD_HASH72,
                "receipt_hash72": "",
            },
            source="test_missing_receipt",
        )


def test_authority_gate_rejects_invariant_drift():
    audit = audit_runtime_authority(
        {
            "step": 1,
            "transport_flux": 1,
            "orientation_flux": 0,
            "constraint_flux": 0,
            "state_hash72": GOOD_HASH72,
            "receipt_hash72": GOOD_HASH72,
        },
        source="test_drift",
    )

    assert audit.ok is False
    assert any("Δe" in reason for reason in audit.reasons)
