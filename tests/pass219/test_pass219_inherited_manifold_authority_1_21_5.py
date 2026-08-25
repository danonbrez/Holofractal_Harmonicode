from __future__ import annotations

import copy
import json
from pathlib import Path

from hhs_runtime.core_sandbox.hhs_pass219_inherited_manifold_authority_1_21_5 import (
    DECISION,
    EXPECTED_AUTHORITY_PATH,
    presentation_normalize,
    verify_inherited_manifold_authority,
)
from hhs_runtime.pass219_native_universal_constraint_v1 import (
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_manifold_engine_v2 import (
    verify_integrated_manifold_search,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_manifold_kernel_v1 import (
    MANIFOLD_SOURCE,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "contracts" / "pass219" / "PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode"
PASS191_EVIDENCE = (
    ROOT
    / "native_projects"
    / "hhs_pass191_dyadic_quartic_phase_lattice"
    / "evidence"
    / "PASS_191_INTEGRATED_PROOF_SEARCH.json"
)


def test_i120_source_is_exact_frozen_pass191_source() -> None:
    native = FIXTURE.read_text(encoding="utf-8").rstrip("\n")
    assert native == MANIFOLD_SOURCE
    assert presentation_normalize(native) == CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE.rstrip("\n")


def test_i121_5_binds_inherited_authority_without_claiming_pass169_closure() -> None:
    result = verify_inherited_manifold_authority(ROOT)
    assert result["decision"] == DECISION
    assert result["authority_path"] == EXPECTED_AUTHORITY_PATH
    assert result["pass191_integrated_manifold_verified"] is True
    assert result["pass191_theorem_status"] == "OBSTRUCTED"
    assert result["exact_context_chain_hits"] == 837
    assert result["exact_context_frontier_size"] == 16
    assert result["contextual_states_visited"] == 51_648_192
    assert result["pass189_contextual_fabric_bound"] is True
    assert result["pass186_ordered_noncommutative_abi_bound"] is True
    assert result["pass175_singleton_vm81_authority_bound"] is True
    assert result["hash72_deterministic_replay_bound"] is True
    assert result["pass159_vmir_effect_binding_observed"] is False
    assert result["whole_expression_semantics_resolved"] is False
    assert result["canonical_monolithic_proof"] is False
    assert result["pass169_whole_expression_admission_required"] is True
    assert result["floating_point_authority"] is False
    assert result["vm81_mutation_authority"] is False
    assert result["hash72_commit_authority"] is False
    assert len(result["evidence_hash72"]) == 72


def test_i121_5_evidence_identity_is_deterministic() -> None:
    first = verify_inherited_manifold_authority(ROOT)
    second = verify_inherited_manifold_authority(ROOT)
    assert first == second


def test_inherited_verifier_rejects_tampered_exact_context_certificate() -> None:
    payload = json.loads(PASS191_EVIDENCE.read_text(encoding="utf-8"))
    tampered = copy.deepcopy(payload)
    tampered["unified_manifold_epoch"]["deep_candidate_certificates"][0]["residuals"][
        "cubic_minus_delta"
    ] = 1
    rejected = False
    try:
        verify_integrated_manifold_search(tampered)
    except AssertionError:
        rejected = True
    assert rejected is True


def test_pass191_exact_hits_remain_context_scoped_not_monolithic_proofs() -> None:
    payload = json.loads(PASS191_EVIDENCE.read_text(encoding="utf-8"))
    certificates = payload["unified_manifold_epoch"]["deep_candidate_certificates"]
    assert len(certificates) == 16
    for certificate in certificates:
        assert certificate["chain_decision"]["proposition"] == "t^3-t = Delta = m^2-m"
        assert certificate["chain_decision"]["scope"] == "EXACT_CONTEXT_CANDIDATE"
        assert certificate["chain_decision"]["status"] == "PROVED"
    assert payload["theorem_decision"]["status"] == "OBSTRUCTED"


def run_dependency_free_conformance() -> None:
    test_i120_source_is_exact_frozen_pass191_source()
    test_i121_5_binds_inherited_authority_without_claiming_pass169_closure()
    test_i121_5_evidence_identity_is_deterministic()
    test_inherited_verifier_rejects_tampered_exact_context_certificate()
    test_pass191_exact_hits_remain_context_scoped_not_monolithic_proofs()


if __name__ == "__main__":
    run_dependency_free_conformance()
