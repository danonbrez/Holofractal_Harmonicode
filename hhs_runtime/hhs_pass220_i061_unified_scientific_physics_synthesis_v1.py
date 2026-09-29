"""Pass 220 I061 unified scientific physics synthesis.

I061 begins only from the verified I060 merge.  It binds the I060 Lean theorem
and dependency Hash72 identities *before* constructing a PhysicsCellWall
candidate.  Formal validity and empirical correspondence are independent
evidence axes; neither substitutes for the other.

This module creates candidate-only scientific-physics envelopes and a
72+72+72 Hash216 knowledge-topology witness.  It does not mint canonical
VM81/Hash72/Hash216 state.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
from typing import Any, Mapping, Sequence
import json

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import (
    SCHEMA as I060_SCHEMA,
    lean_identity_receipt,
)

SCHEMA = "HHS_PASS_220_I061_UNIFIED_SCIENTIFIC_PHYSICS_SYNTHESIS_V1"
VERSION = "1.0.0"
I061_PARENT_MAIN = "ad697affec1eb87d413f25ddb9aa4ece403506ff"
I059_PHYSICS_CELL = "hhs::game::PhysicsCellWall"

VERBATIM_HHS_SOURCE = (
    "contracts/pass219/"
    "PASS_219_ORDERED_CONSTRAINT_WOLFRAM_FORMALIZATION_1_0.harmonicode"
)
VERBATIM_HHS_SOURCE_SHA256 = (
    "d6d7da60e3e9520c0ec802fa8ec63121ffbee9313263012d021907e210bc652c"
)
WOLFRAM_FORMALIZATION = (
    "formal/wolfram/pass219_ordered_constraint_formalization_1_0.wl"
)
WOLFRAM_FORMALIZATION_SHA256 = (
    "7e4203b0eb578cd10303971fb715576d7fd3af5c8921bd46d5a522d61a950a98"
)

WHITEPAPER_PROOF_SOURCES = (
    "whitepapers/HOLOFRACTAL_HARMONICODE.md",
    "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
    "docs/whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md",
    "docs/whitepapers/HARMONICODE_Q144_H36_HOLOFRACTAL_RELATIVISTIC_GAME_ENGINE_THEOREM.md",
    "HHS_PASS_189_HARMONICODE_QUANTUM_LOGIC_HYDRATION_UNIFIED_PHYSICS_AUTHORITY_ADDITION.md",
)

CONSTRUCTION_ORDER = (
    "I060_LEAN_IDENTITY_RECEIPT",
    "FORMAL_VALIDITY_AXIS",
    "EMPIRICAL_CORRESPONDENCE_AXIS",
    "PROOF_BINDING_HASH72",
    "PHYSICS_CELL_CANDIDATE",
    "KNOWLEDGE_GRAPH_HASH216_CANDIDATE",
    "PHYSICS_CELL_WALL_ADMISSION",
)


class I061PhysicsSynthesisError(ValueError):
    pass


@dataclass(frozen=True)
class ExactRational:
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if isinstance(self.numerator, bool) or not isinstance(self.numerator, int):
            raise I061PhysicsSynthesisError("numerator must be an exact integer")
        if (
            isinstance(self.denominator, bool)
            or not isinstance(self.denominator, int)
            or self.denominator <= 0
        ):
            raise I061PhysicsSynthesisError(
                "denominator must be a positive exact integer"
            )

    def fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def canonical(self) -> dict[str, int]:
        q = self.fraction()
        return {"numerator": q.numerator, "denominator": q.denominator}


@dataclass(frozen=True)
class CalibrationEvidence:
    evidence_id: str
    source: str
    declared_domain: str
    unit: str
    dimension: str
    measured_value: ExactRational
    predicted_value: ExactRational
    residual: ExactRational
    error_bound: ExactRational
    replay_receipt_hash72: str

    def validate(self) -> None:
        for name, value in (
            ("evidence_id", self.evidence_id),
            ("source", self.source),
            ("declared_domain", self.declared_domain),
            ("unit", self.unit),
            ("dimension", self.dimension),
        ):
            if not isinstance(value, str) or not value.strip():
                raise I061PhysicsSynthesisError(f"{name} must be declared")
        if self.error_bound.numerator < 0:
            raise I061PhysicsSynthesisError("error bound cannot be negative")
        if abs(self.residual.fraction()) > self.error_bound.fraction():
            raise I061PhysicsSynthesisError(
                "residual exceeds declared exact error bound"
            )
        if not validate_hash72(self.replay_receipt_hash72):
            raise I061PhysicsSynthesisError(
                "empirical replay receipt must be canonical Hash72"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "evidence_id": self.evidence_id,
            "source": self.source,
            "declared_domain": self.declared_domain,
            "unit": self.unit,
            "dimension": self.dimension,
            "measured_value": self.measured_value.canonical(),
            "predicted_value": self.predicted_value.canonical(),
            "residual": self.residual.canonical(),
            "error_bound": self.error_bound.canonical(),
            "replay_receipt_hash72": self.replay_receipt_hash72,
        }


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _hash72(label: str, value: Any) -> str:
    return hash72_digest(
        {"domain": SCHEMA, "version": VERSION, "label": label},
        _canonical(value),
    )


def _valid_hash216_word(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 216
        and all(validate_hash72(value[i : i + 72]) for i in (0, 72, 144))
    )


def _exact_count(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise I061PhysicsSynthesisError(f"{name} must be a nonnegative integer")
    return value


def _formal_axis() -> dict[str, Any]:
    lean = lean_identity_receipt()
    if lean["schema"] != I060_SCHEMA:
        raise I061PhysicsSynthesisError("I060 receipt schema mismatch")
    if not lean["theorem_identity_valid"] or not lean["dependency_identity_valid"]:
        raise I061PhysicsSynthesisError("I060 Lean identity receipt invalid")
    if not lean["intrinsic_successor_binding_required"]:
        raise I061PhysicsSynthesisError("I060 intrinsic successor gate missing")
    if lean["post_hoc_proof_attachment_satisfies_successor"]:
        raise I061PhysicsSynthesisError("I060 post-hoc proof gate weakened")
    if lean["intended_successor"] != (
        "PASS_220_I061_UNIFIED_SCIENTIFIC_PHYSICS_SYNTHESIS"
    ):
        raise I061PhysicsSynthesisError("I060 intended successor mismatch")

    axis = {
        "axis": "FORMAL_VALIDITY",
        "hhs_verbatim_source": VERBATIM_HHS_SOURCE,
        "hhs_verbatim_source_sha256": VERBATIM_HHS_SOURCE_SHA256,
        "whitepaper_proof_sources": list(WHITEPAPER_PROOF_SOURCES),
        "wolfram": {
            "path": WOLFRAM_FORMALIZATION,
            "sha256": WOLFRAM_FORMALIZATION_SHA256,
            "proof_mode": (
                "LEXICAL_AND_STRUCTURAL_VERIFICATIONTEST_WITH_OPAQUE_SOURCE"
            ),
            "tests_succeeded": 13,
            "tests_failed": 0,
            "all_succeeded": True,
            "canonical_mutation_authority": False,
        },
        "lean4": {
            "schema": lean["schema"],
            "module": lean["module"],
            "theorem_identity_hash72": lean["theorem_identity_hash72"],
            "dependency_identity_hash72": lean["dependency_identity_hash72"],
            "kernel_validation_scope": lean["kernel_validation_scope"],
            "runtime_claims_live_kernel_execution": False,
            "vm81_mutation_authority": lean["vm81_mutation_authority"],
            "hash72_commit_authority": lean["hash72_commit_authority"],
            "hash216_persistence_authority": lean[
                "hash216_persistence_authority"
            ],
        },
        "formal_valid": True,
        "formal_validity_does_not_establish_empirical_correspondence": True,
    }
    axis["formal_axis_hash72"] = _hash72("formal-validity-axis", axis)
    return axis


def _empirical_axis(
    *,
    claims_measured_physical_behavior: bool,
    declared_domain: str | None,
    calibration_evidence: Sequence[CalibrationEvidence],
) -> dict[str, Any]:
    claim = bool(claims_measured_physical_behavior)
    records = [item.to_dict() for item in calibration_evidence]
    domain = "" if declared_domain is None else str(declared_domain).strip()

    if claim:
        if not domain:
            raise I061PhysicsSynthesisError(
                "measured physical behavior requires a declared domain"
            )
        if not records:
            raise I061PhysicsSynthesisError(
                "measured physical behavior requires calibration/experimental evidence"
            )
        if any(row["declared_domain"] != domain for row in records):
            raise I061PhysicsSynthesisError(
                "empirical evidence domain must match candidate declared domain"
            )

    axis = {
        "axis": "EMPIRICAL_CORRESPONDENCE",
        "claims_measured_physical_behavior": claim,
        "empirical_evidence_required": claim,
        "declared_domain": domain or None,
        "evidence": records,
        "empirical_correspondence_valid": bool(records) if claim else True,
        "formal_validity_cannot_substitute": True,
        "empirical_correspondence_cannot_substitute_for_formal_validity": True,
    }
    axis["empirical_axis_hash72"] = _hash72("empirical-correspondence-axis", axis)
    return axis


def _fraction_from_record(value: Any, *, name: str) -> Fraction:
    if not isinstance(value, Mapping):
        raise I061PhysicsSynthesisError(f"{name} must be an exact rational record")
    numerator = value.get("numerator")
    denominator = value.get("denominator")
    if (
        isinstance(numerator, bool)
        or not isinstance(numerator, int)
        or isinstance(denominator, bool)
        or not isinstance(denominator, int)
        or denominator <= 0
    ):
        raise I061PhysicsSynthesisError(f"{name} exact rational record invalid")
    return Fraction(numerator, denominator)


def _validate_empirical_axis_payload(empirical: Mapping[str, Any]) -> bool:
    claimed_hash = empirical.get("empirical_axis_hash72")
    if not validate_hash72(claimed_hash):
        raise I061PhysicsSynthesisError("empirical axis Hash72 invalid")
    body = dict(empirical)
    body.pop("empirical_axis_hash72", None)
    if claimed_hash != _hash72("empirical-correspondence-axis", body):
        raise I061PhysicsSynthesisError("empirical axis Hash72 mismatch")

    claim = empirical.get("claims_measured_physical_behavior") is True
    required = empirical.get("empirical_evidence_required") is True
    if claim != required:
        raise I061PhysicsSynthesisError("empirical requirement flag drift")
    if empirical.get("formal_validity_cannot_substitute") is not True:
        raise I061PhysicsSynthesisError("formal-to-empirical substitution enabled")
    if empirical.get(
        "empirical_correspondence_cannot_substitute_for_formal_validity"
    ) is not True:
        raise I061PhysicsSynthesisError("empirical-to-formal substitution enabled")

    domain = empirical.get("declared_domain")
    rows = empirical.get("evidence")
    if not isinstance(rows, list):
        raise I061PhysicsSynthesisError("empirical evidence must be a list")

    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise I061PhysicsSynthesisError(
                f"empirical evidence row {index} must be a mapping"
            )
        for field in ("evidence_id", "source", "declared_domain", "unit", "dimension"):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                raise I061PhysicsSynthesisError(
                    f"empirical evidence row {index} missing {field}"
                )
        measured = _fraction_from_record(
            row.get("measured_value"), name=f"evidence[{index}].measured_value"
        )
        predicted = _fraction_from_record(
            row.get("predicted_value"), name=f"evidence[{index}].predicted_value"
        )
        residual = _fraction_from_record(
            row.get("residual"), name=f"evidence[{index}].residual"
        )
        error_bound = _fraction_from_record(
            row.get("error_bound"), name=f"evidence[{index}].error_bound"
        )
        if error_bound < 0:
            raise I061PhysicsSynthesisError("empirical error bound cannot be negative")
        if abs(residual) > error_bound:
            raise I061PhysicsSynthesisError(
                "empirical residual exceeds declared exact error bound"
            )
        if measured - predicted != residual:
            raise I061PhysicsSynthesisError(
                "empirical residual must equal measured minus predicted"
            )
        if not validate_hash72(row.get("replay_receipt_hash72")):
            raise I061PhysicsSynthesisError(
                "empirical replay receipt must be canonical Hash72"
            )
        if domain is not None and row.get("declared_domain") != domain:
            raise I061PhysicsSynthesisError(
                "empirical evidence domain mismatch"
            )

    if claim:
        if not isinstance(domain, str) or not domain.strip():
            raise I061PhysicsSynthesisError(
                "measured physical behavior requires declared domain"
            )
        if not rows:
            raise I061PhysicsSynthesisError(
                "measured physical behavior requires empirical evidence"
            )
        if empirical.get("empirical_correspondence_valid") is not True:
            raise I061PhysicsSynthesisError(
                "measured physical behavior empirical axis invalid"
            )
    elif empirical.get("empirical_correspondence_valid") is not True:
        raise I061PhysicsSynthesisError("formal-only empirical axis must be neutral-valid")

    return True


def build_scientific_physics_candidate(
    *,
    tick: int,
    body_count: int,
    collider_count: int,
    constraint_count: int,
    delta_time: ExactRational,
    knowledge_coordinate5184: int,
    parent_hash216: str,
    claims_measured_physical_behavior: bool = False,
    declared_domain: str | None = None,
    calibration_evidence: Sequence[CalibrationEvidence] = (),
) -> dict[str, Any]:
    """Construct an I061 candidate with proof identities bound intrinsically.

    Construction order is intentional: I060 proof identities and both evidence
    axes are materialized and hashed before the PhysicsCellWall candidate
    payload exists.
    """
    tick_i = _exact_count(tick, "tick")
    bodies = _exact_count(body_count, "body_count")
    colliders = _exact_count(collider_count, "collider_count")
    constraints = _exact_count(constraint_count, "constraint_count")
    if delta_time.numerator <= 0:
        raise I061PhysicsSynthesisError("delta_time must be positive")
    if (
        isinstance(knowledge_coordinate5184, bool)
        or not isinstance(knowledge_coordinate5184, int)
        or not 0 <= knowledge_coordinate5184 < 5184
    ):
        raise I061PhysicsSynthesisError(
            "knowledge_coordinate5184 must be in [0, 5183]"
        )
    if not _valid_hash216_word(parent_hash216):
        raise I061PhysicsSynthesisError(
            "parent_hash216 must be three canonical ordered Hash72 words"
        )

    # These are constructed BEFORE the physics candidate by contract.
    formal = _formal_axis()
    empirical = _empirical_axis(
        claims_measured_physical_behavior=claims_measured_physical_behavior,
        declared_domain=declared_domain,
        calibration_evidence=calibration_evidence,
    )
    intrinsic_proof_material = {
        "i061_parent_main": I061_PARENT_MAIN,
        "theorem_identity_hash72": formal["lean4"]["theorem_identity_hash72"],
        "dependency_identity_hash72": formal["lean4"][
            "dependency_identity_hash72"
        ],
        "formal_axis_hash72": formal["formal_axis_hash72"],
        "empirical_axis_hash72": empirical["empirical_axis_hash72"],
        "binding_stage": "PRE_PHYSICS_CELL_CANDIDATE_CONSTRUCTION",
        "post_hoc_attachment_permitted": False,
    }
    proof_binding_hash72 = _hash72(
        "intrinsic-proof-binding", intrinsic_proof_material
    )

    physics = {
        "cell": I059_PHYSICS_CELL,
        "tick": tick_i,
        "body_count": bodies,
        "collider_count": colliders,
        "constraint_count": constraints,
        "delta_time": delta_time.canonical(),
        "exact_state_required": True,
        "host_float_authority_requested": False,
        "renderer_mutation_authority_requested": False,
        "intrinsic_proof_binding_hash72": proof_binding_hash72,
        "theorem_identity_hash72": formal["lean4"]["theorem_identity_hash72"],
        "dependency_identity_hash72": formal["lean4"][
            "dependency_identity_hash72"
        ],
        "proof_identity_bound_before_construction": True,
        "post_hoc_proof_attachment": False,
    }
    physics_hash72 = _hash72("physics-cell-candidate", physics)

    graph = {
        "schema": "HHS_PASS_220_I061_LANE5_5184_HASH216_KNOWLEDGE_BINDING_V1",
        "linear5184": knowledge_coordinate5184,
        "relation": "INSTANCE_OF",
        "formal_axis_hash72": formal["formal_axis_hash72"],
        "empirical_axis_hash72": empirical["empirical_axis_hash72"],
        "physics_candidate_hash72": physics_hash72,
        "candidate_hash216": (
            formal["formal_axis_hash72"]
            + empirical["empirical_axis_hash72"]
            + physics_hash72
        ),
        "parent_hash216": parent_hash216,
        "knowledge_graph_projection_only": True,
        "execution_authority": False,
        "mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
    }

    candidate = {
        "schema": SCHEMA,
        "version": VERSION,
        "i061_parent_main": I061_PARENT_MAIN,
        "construction_order": list(CONSTRUCTION_ORDER),
        "formal_validity_axis": formal,
        "empirical_correspondence_axis": empirical,
        "intrinsic_proof_binding": {
            **intrinsic_proof_material,
            "proof_binding_hash72": proof_binding_hash72,
        },
        "physics_cell_candidate": physics,
        "lane5_knowledge_graph_binding": graph,
        "admission": {
            "formal_axis_required": True,
            "empirical_axis_required_if_measured_behavior_claimed": True,
            "formal_substitutes_for_empirical": False,
            "empirical_substitutes_for_formal": False,
            "physics_cell_wall_required": True,
            "vm81_admission_required_for_canonical_successor": True,
        },
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    candidate["candidate_receipt_hash72"] = _hash72(
        "unified-scientific-physics-candidate", candidate
    )
    return candidate


def validate_scientific_physics_candidate(
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    if candidate.get("schema") != SCHEMA:
        raise I061PhysicsSynthesisError("I061 schema mismatch")
    if candidate.get("i061_parent_main") != I061_PARENT_MAIN:
        raise I061PhysicsSynthesisError("I061 parent lineage mismatch")
    if tuple(candidate.get("construction_order", ())) != CONSTRUCTION_ORDER:
        raise I061PhysicsSynthesisError("I061 construction order mismatch")

    expected_formal = _formal_axis()
    formal = candidate.get("formal_validity_axis")
    if formal != expected_formal:
        raise I061PhysicsSynthesisError("formal validity axis identity drift")
    if formal.get("formal_valid") is not True:
        raise I061PhysicsSynthesisError("formal validity required")

    empirical = candidate.get("empirical_correspondence_axis")
    if not isinstance(empirical, Mapping):
        raise I061PhysicsSynthesisError("empirical axis missing")
    _validate_empirical_axis_payload(empirical)
    measured_claim = empirical.get("claims_measured_physical_behavior") is True

    binding = candidate.get("intrinsic_proof_binding")
    physics = candidate.get("physics_cell_candidate")
    graph = candidate.get("lane5_knowledge_graph_binding")
    if not all(isinstance(x, Mapping) for x in (binding, physics, graph)):
        raise I061PhysicsSynthesisError("I061 binding/candidate/graph missing")

    theorem_hash = expected_formal["lean4"]["theorem_identity_hash72"]
    dependency_hash = expected_formal["lean4"]["dependency_identity_hash72"]
    if binding.get("theorem_identity_hash72") != theorem_hash:
        raise I061PhysicsSynthesisError("theorem identity not intrinsically bound")
    if binding.get("dependency_identity_hash72") != dependency_hash:
        raise I061PhysicsSynthesisError(
            "dependency identity not intrinsically bound"
        )
    if binding.get("binding_stage") != (
        "PRE_PHYSICS_CELL_CANDIDATE_CONSTRUCTION"
    ):
        raise I061PhysicsSynthesisError("proof binding stage is not intrinsic")
    if binding.get("post_hoc_attachment_permitted") is not False:
        raise I061PhysicsSynthesisError("post-hoc proof attachment enabled")

    expected_binding = {
        "i061_parent_main": I061_PARENT_MAIN,
        "theorem_identity_hash72": theorem_hash,
        "dependency_identity_hash72": dependency_hash,
        "formal_axis_hash72": expected_formal["formal_axis_hash72"],
        "empirical_axis_hash72": empirical["empirical_axis_hash72"],
        "binding_stage": "PRE_PHYSICS_CELL_CANDIDATE_CONSTRUCTION",
        "post_hoc_attachment_permitted": False,
    }
    expected_binding_hash = _hash72(
        "intrinsic-proof-binding", expected_binding
    )
    if binding.get("proof_binding_hash72") != expected_binding_hash:
        raise I061PhysicsSynthesisError("intrinsic proof binding hash mismatch")

    if physics.get("intrinsic_proof_binding_hash72") != expected_binding_hash:
        raise I061PhysicsSynthesisError(
            "PhysicsCellWall candidate was not constructed from proof binding"
        )
    if physics.get("theorem_identity_hash72") != theorem_hash:
        raise I061PhysicsSynthesisError(
            "PhysicsCellWall candidate theorem identity drift"
        )
    if physics.get("dependency_identity_hash72") != dependency_hash:
        raise I061PhysicsSynthesisError(
            "PhysicsCellWall candidate dependency identity drift"
        )
    if physics.get("proof_identity_bound_before_construction") is not True:
        raise I061PhysicsSynthesisError("preconstruction proof binding absent")
    if physics.get("post_hoc_proof_attachment") is not False:
        raise I061PhysicsSynthesisError("post-hoc proof attachment detected")
    if physics.get("exact_state_required") is not True:
        raise I061PhysicsSynthesisError("exact physics state required")
    if physics.get("host_float_authority_requested") is not False:
        raise I061PhysicsSynthesisError("host float authority escalation")
    if physics.get("renderer_mutation_authority_requested") is not False:
        raise I061PhysicsSynthesisError("renderer mutation authority escalation")

    coordinate = graph.get("linear5184")
    if (
        isinstance(coordinate, bool)
        or not isinstance(coordinate, int)
        or not 0 <= coordinate < 5184
    ):
        raise I061PhysicsSynthesisError("knowledge graph coordinate invalid")

    physics_material = dict(physics)
    expected_physics_hash = _hash72("physics-cell-candidate", physics_material)
    expected_hash216 = (
        expected_formal["formal_axis_hash72"]
        + empirical["empirical_axis_hash72"]
        + expected_physics_hash
    )
    if graph.get("candidate_hash216") != expected_hash216:
        raise I061PhysicsSynthesisError("knowledge graph Hash216 binding drift")
    if not _valid_hash216_word(graph["candidate_hash216"]):
        raise I061PhysicsSynthesisError("candidate Hash216 shape invalid")

    for key in (
        "execution_authority",
        "mutation_authority",
        "canonical_hash72_commit_authority",
        "canonical_hash216_persistence_authority",
        "floating_point_authority",
    ):
        if graph.get(key) is not False:
            raise I061PhysicsSynthesisError(f"knowledge graph authority escalation: {key}")

    receipt = candidate.get("candidate_receipt_hash72")
    body = dict(candidate)
    body.pop("candidate_receipt_hash72", None)
    expected_receipt = _hash72("unified-scientific-physics-candidate", body)
    if receipt != expected_receipt or not validate_hash72(receipt):
        raise I061PhysicsSynthesisError("candidate receipt mismatch")

    return {
        "ok": True,
        "schema": SCHEMA,
        "formal_valid": True,
        "empirical_required": measured_claim,
        "empirical_valid": empirical["empirical_correspondence_valid"],
        "intrinsic_lean_binding": True,
        "knowledge_coordinate5184": coordinate,
        "candidate_hash216": graph["candidate_hash216"],
        "physics_cell_wall_required": True,
        "vm81_admission_required": True,
        "canonical_authority_escalation": False,
    }



def scientific_physics_synthesis_self_test() -> dict[str, Any]:
    parent = (
        _hash72("self-test-parent-minus", "minus")
        + _hash72("self-test-parent-center", "center")
        + _hash72("self-test-parent-plus", "plus")
    )
    candidate = build_scientific_physics_candidate(
        tick=61,
        body_count=3,
        collider_count=4,
        constraint_count=2,
        delta_time=ExactRational(1, 120),
        knowledge_coordinate5184=61,
        parent_hash216=parent,
    )
    validation = validate_scientific_physics_candidate(candidate)
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "ok": validation["ok"],
        "validation": validation,
        "candidate_receipt_hash72": candidate["candidate_receipt_hash72"],
        "candidate_hash216": candidate[
            "lane5_knowledge_graph_binding"
        ]["candidate_hash216"],
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }


__all__ = [
    "CalibrationEvidence",
    "CONSTRUCTION_ORDER",
    "ExactRational",
    "I061_PARENT_MAIN",
    "I061PhysicsSynthesisError",
    "SCHEMA",
    "VERBATIM_HHS_SOURCE",
    "VERBATIM_HHS_SOURCE_SHA256",
    "VERSION",
    "WHITEPAPER_PROOF_SOURCES",
    "WOLFRAM_FORMALIZATION",
    "WOLFRAM_FORMALIZATION_SHA256",
    "build_scientific_physics_candidate",
    "scientific_physics_synthesis_self_test",
    "validate_scientific_physics_candidate",
]
