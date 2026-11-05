from __future__ import annotations

from copy import deepcopy
from hashlib import sha1
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import (
    lean_identity_receipt,
)
from hhs_runtime.hhs_pass220_i063_canonical_stem_physics_law_objects_v1 import (
    CLASS_HHS_ADMISSIBILITY,
    CLASS_HHS_PHYSICAL_HYPOTHESIS,
    CLASS_STANDARD_PHYSICS,
    PASS178_BLOB_SHA,
    PASS178_SOURCE,
    CalibrationEvidence,
    DimensionSignature,
    DimensionalEquality,
    EmpiricalPolicy,
    ExactRational,
    I063_BASE_MAIN,
    I061_MERGE,
    I062_MERGE,
    I063PhysicsLawError,
    SourceIdentity,
    VariableSpec,
    bind_law_to_i061_candidate,
    build_physics_law_object,
    canonical_stem_physics_law_self_test,
    hhs_p4_ab_admissibility_law,
    relativistic_energy_momentum_law,
    validate_law_to_i061_envelope,
    validate_physics_law_object,
)

ROOT = Path(__file__).resolve().parents[2]


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    framed = f"blob {len(payload)}\0".encode("ascii") + payload
    return sha1(framed).hexdigest()


def h72(label: str) -> str:
    return hash72_digest({"test": "I063", "label": label}, label)


def parent216() -> str:
    return h72("minus") + h72("center") + h72("plus")


def calibration(domain: str) -> CalibrationEvidence:
    return CalibrationEvidence(
        evidence_id="i063-fixture",
        source="TEST_FIXTURE_ONLY",
        declared_domain=domain,
        unit="J^2",
        dimension="M^2 L^4 T^-4",
        measured_value=ExactRational(1001, 1000),
        predicted_value=ExactRational(1, 1),
        residual=ExactRational(1, 1000),
        error_bound=ExactRational(1, 500),
        replay_receipt_hash72=h72("empirical-replay"),
    )


def test_i063_exact_lineage_contains_frozen_i061_and_merged_i062() -> None:
    assert I063_BASE_MAIN == "7f34d20819ddbbb8f470f6b87e92621e47b99de4"
    assert I061_MERGE == "8db145707a71f60015904577e2a0786e438a4c65"
    assert I062_MERGE == "d6560ba13382282d8cc41fafeece1d862a2b752e"


def test_i063_pass178_source_identity_is_repository_exact() -> None:
    source = ROOT / PASS178_SOURCE
    assert source.exists()
    assert git_blob_sha(source) == PASS178_BLOB_SHA


def test_i063_relativistic_energy_momentum_dimensions_close_exactly() -> None:
    law = relativistic_energy_momentum_law()
    result = validate_physics_law_object(law)

    assert result["ok"] is True
    assert law["classification"] == CLASS_STANDARD_PHYSICS
    assert law["source"]["verbatim_expression"] == "E^2-p^2c^2=m^2c^4"
    assert law["dimension_receipts"] == [
        {
            "label": "energy_momentum_mass_shell",
            "dimension": {
                "M": 2,
                "L": 4,
                "T": -4,
                "I": 0,
                "Theta": 0,
                "N": 0,
                "J": 0,
            },
            "term_count": 3,
            "closed": True,
        }
    ]
    assert law["empirical_policy"]["measured_behavior_permitted"] is True
    assert law["empirical_policy"]["calibration_required_when_measured"] is True


def test_i063_hhs_membrane_is_not_promoted_to_measured_physics() -> None:
    law = hhs_p4_ab_admissibility_law()
    result = validate_physics_law_object(law)

    assert result["ok"] is True
    assert law["classification"] == CLASS_HHS_ADMISSIBILITY
    assert law["source"]["verbatim_expression"] == r"\boxed{P^4=AB}"
    assert law["empirical_policy"]["measured_behavior_permitted"] is False

    with pytest.raises(
        I063PhysicsLawError,
        match="does not permit measured-behavior claim",
    ):
        bind_law_to_i061_candidate(
            law,
            tick=1,
            body_count=1,
            collider_count=1,
            constraint_count=0,
            delta_time=ExactRational(1, 60),
            parent_hash216=parent216(),
            claims_measured_physical_behavior=True,
            declared_domain="anything",
            calibration_evidence=[calibration("anything")],
        )


def test_i063_hhs_physical_hypothesis_can_require_empirical_axis_without_becoming_admissibility_rule() -> None:
    dimensionless = DimensionSignature()
    law = build_physics_law_object(
        law_id="TEST_HHS_PHYSICAL_HYPOTHESIS",
        name="Test-only HHS physical hypothesis",
        classification=CLASS_HHS_PHYSICAL_HYPOTHESIS,
        source=SourceIdentity(
            path=PASS178_SOURCE,
            git_blob_sha=PASS178_BLOB_SHA,
            source_kind="TEST_FIXTURE_ONLY",
            verbatim_expression="X=Y",
        ),
        variables=(
            VariableSpec("X", "test_x", dimensionless, "1", "Exact", "TEST"),
            VariableSpec("Y", "test_y", dimensionless, "1", "Exact", "TEST"),
        ),
        dimensional_equalities=(
            DimensionalEquality.make("test_xy", ({"X": 1}, {"Y": 1})),
        ),
        assumptions=("TEST FIXTURE ONLY",),
        boundary_conditions=("TEST FIXTURE ONLY",),
        law_domain="TEST",
        knowledge_coordinate5184=100,
        empirical_policy=EmpiricalPolicy(
            measured_behavior_permitted=True,
            calibration_required_when_measured=True,
            allowed_declared_domains=("TEST_DOMAIN",),
        ),
    )

    with pytest.raises(I063PhysicsLawError, match="requires I061 calibration"):
        bind_law_to_i061_candidate(
            law,
            tick=2,
            body_count=1,
            collider_count=1,
            constraint_count=0,
            delta_time=ExactRational(1, 60),
            parent_hash216=parent216(),
            claims_measured_physical_behavior=True,
            declared_domain="TEST_DOMAIN",
        )

    envelope = bind_law_to_i061_candidate(
        law,
        tick=2,
        body_count=1,
        collider_count=1,
        constraint_count=0,
        delta_time=ExactRational(1, 60),
        parent_hash216=parent216(),
        claims_measured_physical_behavior=True,
        declared_domain="TEST_DOMAIN",
        calibration_evidence=[calibration("TEST_DOMAIN")],
    )
    result = validate_law_to_i061_envelope(law, envelope)
    assert result["ok"] is True
    assert result["i061_validation"]["empirical_required"] is True
    assert result["i061_validation"]["empirical_valid"] is True


def test_i063_dimension_mismatch_fails_before_law_identity_exists() -> None:
    force = DimensionSignature(M=1, L=1, T=-2)
    mass = DimensionSignature(M=1)
    velocity = DimensionSignature(L=1, T=-1)

    with pytest.raises(I063PhysicsLawError, match="dimension mismatch"):
        build_physics_law_object(
            law_id="BAD_F_EQUALS_MV",
            name="Dimensionally invalid fixture",
            classification=CLASS_STANDARD_PHYSICS,
            source=SourceIdentity(
                path=PASS178_SOURCE,
                git_blob_sha=PASS178_BLOB_SHA,
                source_kind="TEST_FIXTURE_ONLY",
                verbatim_expression="F=mv",
            ),
            variables=(
                VariableSpec("F", "force", force, "N", "Exact", "REAL"),
                VariableSpec("m", "mass", mass, "kg", "Exact", "REAL"),
                VariableSpec("v", "velocity", velocity, "m/s", "Exact", "REAL"),
            ),
            dimensional_equalities=(
                DimensionalEquality.make("bad_force", ({"F": 1}, {"m": 1, "v": 1})),
            ),
            assumptions=("TEST",),
            boundary_conditions=("TEST",),
            law_domain="TEST",
            knowledge_coordinate5184=101,
            empirical_policy=EmpiricalPolicy(
                measured_behavior_permitted=True,
                calibration_required_when_measured=True,
            ),
        )


def test_i063_law_identity_intrinsically_contains_i060_proof_identities() -> None:
    law = relativistic_energy_momentum_law()
    lean = lean_identity_receipt()
    proof = law["proof_identity"]

    assert proof["i060_theorem_identity_hash72"] == lean["theorem_identity_hash72"]
    assert proof["i060_dependency_identity_hash72"] == lean["dependency_identity_hash72"]
    assert proof["bound_during_law_construction"] is True
    assert proof["post_hoc_proof_attachment"] is False


def test_i063_law_mutation_breaks_hash_and_source_or_dimension_drift_fails() -> None:
    law = relativistic_energy_momentum_law()

    tampered = deepcopy(law)
    tampered["assumptions"].append("late mutation")
    with pytest.raises(I063PhysicsLawError, match="law formal identity Hash72 drift"):
        validate_physics_law_object(tampered)

    tampered = deepcopy(law)
    tampered["source"]["git_blob_sha"] = "0" * 40
    with pytest.raises(I063PhysicsLawError):
        validate_physics_law_object(tampered)

    tampered = deepcopy(law)
    tampered["variables"][0]["dimension"]["L"] = 3
    with pytest.raises(I063PhysicsLawError, match="dimension mismatch"):
        validate_physics_law_object(tampered)


def test_i063_law_is_bound_to_i061_before_solver_state_construction() -> None:
    law = relativistic_energy_momentum_law()
    envelope = bind_law_to_i061_candidate(
        law,
        tick=63,
        body_count=2,
        collider_count=2,
        constraint_count=1,
        delta_time=ExactRational(1, 120),
        parent_hash216=parent216(),
    )
    result = validate_law_to_i061_envelope(law, envelope)

    assert result["ok"] is True
    assert result["pre_solver_binding"] is True
    assert envelope["solver_state_constructed"] is False
    assert envelope["post_hoc_law_attachment"] is False
    assert envelope["law_to_i061_binding"]["binding_stage"] == (
        "PRE_SOLVER_STATE_CONSTRUCTION"
    )
    assert (
        envelope["law_to_i061_binding"]["knowledge_coordinate5184"]
        == law["knowledge_coordinate5184"]
    )

    tampered = deepcopy(envelope)
    tampered["solver_state_constructed"] = True
    with pytest.raises(I063PhysicsLawError, match="before solver-state"):
        validate_law_to_i061_envelope(law, tampered)


def test_i063_standard_measured_claim_requires_allowed_domain_and_i061_evidence() -> None:
    law = relativistic_energy_momentum_law()

    with pytest.raises(I063PhysicsLawError, match="outside this law object's admitted domains"):
        bind_law_to_i061_candidate(
            law,
            tick=64,
            body_count=1,
            collider_count=1,
            constraint_count=0,
            delta_time=ExactRational(1, 60),
            parent_hash216=parent216(),
            claims_measured_physical_behavior=True,
            declared_domain="UNDECLARED_DOMAIN",
            calibration_evidence=[calibration("UNDECLARED_DOMAIN")],
        )

    domain = "DECLARED_RELATIVISTIC_BENCH"
    envelope = bind_law_to_i061_candidate(
        law,
        tick=64,
        body_count=1,
        collider_count=1,
        constraint_count=0,
        delta_time=ExactRational(1, 60),
        parent_hash216=parent216(),
        claims_measured_physical_behavior=True,
        declared_domain=domain,
        calibration_evidence=[calibration(domain)],
    )
    result = validate_law_to_i061_envelope(law, envelope)
    assert result["i061_validation"]["empirical_required"] is True
    assert result["i061_validation"]["empirical_valid"] is True


def test_i063_self_test_closes_without_authority_escalation() -> None:
    result = canonical_stem_physics_law_self_test()
    assert result["ok"] is True
    assert result["standard_and_hhs_classes_distinct"] is True
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_commit_authority"] is False
    assert result["canonical_hash216_persistence_authority"] is False
