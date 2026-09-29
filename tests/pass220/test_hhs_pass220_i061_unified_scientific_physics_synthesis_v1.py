from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import (
    lean_identity_receipt,
)
from hhs_runtime.hhs_pass220_i061_unified_scientific_physics_synthesis_v1 import (
    CalibrationEvidence,
    CONSTRUCTION_ORDER,
    ExactRational,
    I061_PARENT_MAIN,
    I061PhysicsSynthesisError,
    SCHEMA,
    VERBATIM_HHS_SOURCE,
    VERBATIM_HHS_SOURCE_SHA256,
    WOLFRAM_FORMALIZATION,
    WOLFRAM_FORMALIZATION_SHA256,
    build_scientific_physics_candidate,
    scientific_physics_synthesis_self_test,
    validate_scientific_physics_candidate,
)

ROOT = Path(__file__).resolve().parents[2]


def h72(label: str) -> str:
    return hash72_digest({"test": "I061", "label": label}, label)


def parent216() -> str:
    return h72("parent-minus") + h72("parent-center") + h72("parent-plus")


def evidence(domain: str = "bench-rigid-body-v1") -> CalibrationEvidence:
    return CalibrationEvidence(
        evidence_id="cal-001",
        source="deterministic-bench-fixture",
        declared_domain=domain,
        unit="m",
        dimension="length",
        measured_value=ExactRational(1001, 1000),
        predicted_value=ExactRational(1, 1),
        residual=ExactRational(1, 1000),
        error_bound=ExactRational(1, 500),
        replay_receipt_hash72=h72("empirical-replay"),
    )


def test_i061_parent_is_verified_i060_merge() -> None:
    assert I061_PARENT_MAIN == "ad697affec1eb87d413f25ddb9aa4ece403506ff"


def test_i061_repository_formal_artifact_identities_are_exact() -> None:
    verbatim = ROOT / VERBATIM_HHS_SOURCE
    wolfram = ROOT / WOLFRAM_FORMALIZATION
    assert sha256(verbatim.read_bytes()).hexdigest() == VERBATIM_HHS_SOURCE_SHA256
    assert sha256(wolfram.read_bytes()).hexdigest() == WOLFRAM_FORMALIZATION_SHA256


def test_i061_formal_only_candidate_binds_i060_before_physics_construction() -> None:
    candidate = build_scientific_physics_candidate(
        tick=7,
        body_count=4,
        collider_count=6,
        constraint_count=3,
        delta_time=ExactRational(1, 120),
        knowledge_coordinate5184=511,
        parent_hash216=parent216(),
    )
    result = validate_scientific_physics_candidate(candidate)
    lean = lean_identity_receipt()

    assert candidate["schema"] == SCHEMA
    assert tuple(candidate["construction_order"]) == CONSTRUCTION_ORDER
    assert result["ok"] is True
    assert result["formal_valid"] is True
    assert result["empirical_required"] is False
    assert result["empirical_valid"] is True
    assert result["intrinsic_lean_binding"] is True

    binding = candidate["intrinsic_proof_binding"]
    physics = candidate["physics_cell_candidate"]
    assert binding["binding_stage"] == "PRE_PHYSICS_CELL_CANDIDATE_CONSTRUCTION"
    assert binding["post_hoc_attachment_permitted"] is False
    assert binding["theorem_identity_hash72"] == lean["theorem_identity_hash72"]
    assert binding["dependency_identity_hash72"] == lean["dependency_identity_hash72"]
    assert physics["theorem_identity_hash72"] == lean["theorem_identity_hash72"]
    assert physics["dependency_identity_hash72"] == lean["dependency_identity_hash72"]
    assert physics["intrinsic_proof_binding_hash72"] == binding["proof_binding_hash72"]
    assert physics["proof_identity_bound_before_construction"] is True
    assert physics["post_hoc_proof_attachment"] is False


def test_i061_hash216_is_ordered_formal_empirical_physics_topology() -> None:
    candidate = build_scientific_physics_candidate(
        tick=8,
        body_count=1,
        collider_count=1,
        constraint_count=0,
        delta_time=ExactRational(1, 60),
        knowledge_coordinate5184=5183,
        parent_hash216=parent216(),
    )
    graph = candidate["lane5_knowledge_graph_binding"]
    formal = candidate["formal_validity_axis"]["formal_axis_hash72"]
    empirical = candidate["empirical_correspondence_axis"]["empirical_axis_hash72"]
    physics = graph["physics_candidate_hash72"]

    assert validate_hash72(formal)
    assert validate_hash72(empirical)
    assert validate_hash72(physics)
    assert graph["candidate_hash216"] == formal + empirical + physics
    assert len(graph["candidate_hash216"]) == 216
    assert graph["knowledge_graph_projection_only"] is True
    assert graph["execution_authority"] is False
    assert graph["mutation_authority"] is False
    assert graph["canonical_hash72_commit_authority"] is False
    assert graph["canonical_hash216_persistence_authority"] is False


def test_i061_measured_behavior_requires_independent_empirical_axis() -> None:
    with pytest.raises(
        I061PhysicsSynthesisError,
        match="declared domain",
    ):
        build_scientific_physics_candidate(
            tick=9,
            body_count=2,
            collider_count=2,
            constraint_count=1,
            delta_time=ExactRational(1, 60),
            knowledge_coordinate5184=81,
            parent_hash216=parent216(),
            claims_measured_physical_behavior=True,
        )

    with pytest.raises(
        I061PhysicsSynthesisError,
        match="calibration/experimental evidence",
    ):
        build_scientific_physics_candidate(
            tick=9,
            body_count=2,
            collider_count=2,
            constraint_count=1,
            delta_time=ExactRational(1, 60),
            knowledge_coordinate5184=81,
            parent_hash216=parent216(),
            claims_measured_physical_behavior=True,
            declared_domain="bench-rigid-body-v1",
        )

    candidate = build_scientific_physics_candidate(
        tick=9,
        body_count=2,
        collider_count=2,
        constraint_count=1,
        delta_time=ExactRational(1, 60),
        knowledge_coordinate5184=81,
        parent_hash216=parent216(),
        claims_measured_physical_behavior=True,
        declared_domain="bench-rigid-body-v1",
        calibration_evidence=[evidence()],
    )
    result = validate_scientific_physics_candidate(candidate)
    assert result["empirical_required"] is True
    assert result["empirical_valid"] is True
    assert candidate["formal_validity_axis"][
        "formal_validity_does_not_establish_empirical_correspondence"
    ] is True
    assert candidate["empirical_correspondence_axis"][
        "empirical_correspondence_cannot_substitute_for_formal_validity"
    ] is True


def test_i061_empirical_residual_must_fit_declared_exact_error_bound() -> None:
    bad = CalibrationEvidence(
        evidence_id="bad",
        source="fixture",
        declared_domain="bench-rigid-body-v1",
        unit="m",
        dimension="length",
        measured_value=ExactRational(3, 2),
        predicted_value=ExactRational(1, 1),
        residual=ExactRational(1, 2),
        error_bound=ExactRational(1, 10),
        replay_receipt_hash72=h72("bad-residual"),
    )
    with pytest.raises(I061PhysicsSynthesisError, match="residual exceeds"):
        build_scientific_physics_candidate(
            tick=10,
            body_count=1,
            collider_count=1,
            constraint_count=0,
            delta_time=ExactRational(1, 60),
            knowledge_coordinate5184=4,
            parent_hash216=parent216(),
            claims_measured_physical_behavior=True,
            declared_domain="bench-rigid-body-v1",
            calibration_evidence=[bad],
        )


def test_i061_rejects_post_hoc_lean_attachment_or_identity_tampering() -> None:
    candidate = build_scientific_physics_candidate(
        tick=11,
        body_count=1,
        collider_count=1,
        constraint_count=0,
        delta_time=ExactRational(1, 60),
        knowledge_coordinate5184=5,
        parent_hash216=parent216(),
    )

    tampered = deepcopy(candidate)
    tampered["physics_cell_candidate"]["post_hoc_proof_attachment"] = True
    with pytest.raises(I061PhysicsSynthesisError):
        validate_scientific_physics_candidate(tampered)

    tampered = deepcopy(candidate)
    tampered["intrinsic_proof_binding"]["theorem_identity_hash72"] = h72("fake-theorem")
    with pytest.raises(I061PhysicsSynthesisError, match="theorem identity"):
        validate_scientific_physics_candidate(tampered)


def test_i061_rejects_knowledge_graph_topology_drift() -> None:
    candidate = build_scientific_physics_candidate(
        tick=12,
        body_count=1,
        collider_count=1,
        constraint_count=0,
        delta_time=ExactRational(1, 60),
        knowledge_coordinate5184=6,
        parent_hash216=parent216(),
    )
    tampered = deepcopy(candidate)
    tampered["lane5_knowledge_graph_binding"]["candidate_hash216"] = (
        h72("x") + h72("y") + h72("z")
    )
    with pytest.raises(I061PhysicsSynthesisError, match="Hash216 binding drift"):
        validate_scientific_physics_candidate(tampered)


def test_i061_rejects_out_of_range_knowledge_coordinate_and_float_like_time() -> None:
    with pytest.raises(I061PhysicsSynthesisError, match="\[0, 5183\]"):
        build_scientific_physics_candidate(
            tick=1,
            body_count=1,
            collider_count=1,
            constraint_count=0,
            delta_time=ExactRational(1, 60),
            knowledge_coordinate5184=5184,
            parent_hash216=parent216(),
        )

    with pytest.raises(I061PhysicsSynthesisError):
        ExactRational(1, 0)


def test_i061_candidate_receipt_detects_any_postconstruction_mutation() -> None:
    candidate = build_scientific_physics_candidate(
        tick=13,
        body_count=3,
        collider_count=4,
        constraint_count=2,
        delta_time=ExactRational(1, 60),
        knowledge_coordinate5184=72,
        parent_hash216=parent216(),
    )
    tampered = deepcopy(candidate)
    tampered["physics_cell_candidate"]["body_count"] += 1
    with pytest.raises(I061PhysicsSynthesisError, match="candidate receipt mismatch"):
        validate_scientific_physics_candidate(tampered)


def test_i061_self_test_and_service_registry_surface() -> None:
    result = scientific_physics_synthesis_self_test()
    assert result["schema"] == SCHEMA
    assert result["ok"] is True
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_commit_authority"] is False
    assert result["canonical_hash216_persistence_authority"] is False

    registry_source = (
        ROOT / "hhs_runtime" / "hhs_service_registry_v1.py"
    ).read_text(encoding="utf-8")
    assert "pass220.unified_scientific_physics_synthesis.self_test" in registry_source
    assert "hhs_pass220_i061_unified_scientific_physics_synthesis_v1" in registry_source
    assert "REJECT_I061_POST_HOC_PROOF_ATTACHMENT" in registry_source
    assert "REJECT_I061_FORMAL_EMPIRICAL_SUBSTITUTION" in registry_source
