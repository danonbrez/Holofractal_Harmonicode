from hhs_runtime.hhs_phase_disjoint_continuity_v1 import (
    PHASE_DOMAINS,
    phase_disjoint_continuity_self_test,
    phase_disjoint_continuity_theorem,
)
from hhs_runtime.hhs_genesis_severance_protocol_v1 import (
    GENESIS_SEVERED_PRIVACY,
    REDACTED_CONTINUITY,
    WITNESSED_CONTINUITY,
)


def test_phase_domains_are_explicit_and_disjoint():
    assert set(PHASE_DOMAINS) == {WITNESSED_CONTINUITY, REDACTED_CONTINUITY, GENESIS_SEVERED_PRIVACY}
    assert PHASE_DOMAINS[WITNESSED_CONTINUITY]["rule"] == "every transformation is permanently stored"
    assert PHASE_DOMAINS[REDACTED_CONTINUITY]["rule"] == "the act of redaction is itself witnessed"
    assert PHASE_DOMAINS[GENESIS_SEVERED_PRIVACY]["rule"] == "new Genesis seed required"


def test_phase_disjoint_theorem_is_hash72_witnessed():
    theorem = phase_disjoint_continuity_theorem()
    assert theorem["schema"] == "HHS_PHASE_DISJOINT_CONTINUITY_THEOREM_V1"
    assert theorem["kernel_witness"]["schema"] == "HHS_HASH72_KERNEL_WITNESS_V1"
    assert len(theorem["kernel_witness"]["digest"]) == 72
    assert theorem["kernel_witness"]["zero_sum"] is True
    assert "Substrate may cross a phase boundary; identity-continuity may not cross unwitnessed." in theorem["axioms"]


def test_phase_disjoint_continuity_self_test_passes():
    result = phase_disjoint_continuity_self_test()
    assert result["ok"] is True
    assert result["valid_witnessed_continuity"]["ok"] is True
    assert result["invalid_substrate_equivalence"]["ok"] is False
