from hhs_foundation.hhs_foundational_standards_v1 import (
    HASH72_LEN,
    audit_foundational_conformance,
    assert_foundational_conformance,
    foundational_standards_self_test,
    make_meaning_witness,
    make_proposition_identity,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_foundational_standards_self_test():
    result = foundational_standards_self_test()
    assert result["conformance"]["ok"] is True
    assert len(result["identity"]["identity_hash72"]) == HASH72_LEN
    assert result["meaning_witness"]["meaning_conserved"] is True


def test_foundational_conformance_blocks_missing_identity():
    audit = assert_foundational_conformance(
        {
            "proposition": "A proposition can be upgraded into explicit identity.",
            "operation": "identity projection",
        },
        source="test",
        require_receipt=False,
    )
    assert audit.ok is True


def test_foundational_conformance_detects_drift():
    before = make_proposition_identity("A", source="test")
    after = make_proposition_identity("B", source="test")
    witness = make_meaning_witness(before, after, transformation_rule="unsafe substitution", reversible=False)
    audit = audit_foundational_conformance(
        {"proposition_identity": before, "meaning_witness": witness},
        source="test",
        require_receipt=False,
    )
    assert audit.ok is False
    assert "HHS-M004" in audit.standards and audit.standards["HHS-M004"] is False


def test_service_registry_foundational_self_test_registered():
    registry = make_default_service_registry()
    assert registry.has_service("foundational_standards.self_test")
    interposition = registry.interpose_dispatch("foundational_standards.self_test")
    record = registry.dispatch(
        "foundational_standards.self_test",
        zero_bypass_interposition_token=interposition["interposition_token"],
    )
    assert record["foundational_conformance_pre"]["ok"] is True
    assert record["foundational_conformance_post"]["ok"] is True
    assert record["result"]["conformance"]["ok"] is True
