"""Pass 220 I063 canonical STEM / physics law objects.

I063 sits above the frozen I061 scientific-admission membrane.  It gives every
physics law/mechanic a typed, hash-addressed identity carrying exact source,
variables, units/dimensions, assumptions, boundary conditions, proof lineage,
empirical policy, and one Lane 5 5,184 coordinate.

The law object is not a solver and does not gain VM81/Hash authority.  A law is
bound to an I061 candidate before later solver-specific state is admitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence
import json
import re

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import (
    lean_identity_receipt,
)
from hhs_runtime.hhs_pass220_i061_unified_scientific_physics_synthesis_v1 import (
    CalibrationEvidence,
    ExactRational,
    I061PhysicsSynthesisError,
    build_scientific_physics_candidate,
    validate_scientific_physics_candidate,
)

SCHEMA = "HHS_PASS_220_I063_CANONICAL_STEM_PHYSICS_LAW_OBJECTS_V1"
VERSION = "1.0.0"
I063_BASE_MAIN = "7f34d20819ddbbb8f470f6b87e92621e47b99de4"
I061_MERGE = "8db145707a71f60015904577e2a0786e438a4c65"
I062_MERGE = "d6560ba13382282d8cc41fafeece1d862a2b752e"

CLASS_STANDARD_PHYSICS = "STANDARD_PHYSICS_EQUATION"
CLASS_HHS_ADMISSIBILITY = "HHS_ADMISSIBILITY_CONSTRAINT"
CLASS_HHS_PHYSICAL_HYPOTHESIS = "HHS_PHYSICAL_HYPOTHESIS"
CLASS_PROJECTION_ONLY = "PROJECTION_ONLY_RELATION"

LAW_CLASSES = (
    CLASS_STANDARD_PHYSICS,
    CLASS_HHS_ADMISSIBILITY,
    CLASS_HHS_PHYSICAL_HYPOTHESIS,
    CLASS_PROJECTION_ONLY,
)

SI_BASE_AXES = ("M", "L", "T", "I", "Theta", "N", "J")

PASS178_SOURCE = (
    "HHS_PASS_178_NATIVE_EXACT_HARMONICODE_RELATIVISTIC_QUANTUM_"
    "THREEJS_PHYSICS_SIMULATION_RUNTIME.md"
)
PASS178_BLOB_SHA = "56d5599011d489f3273d4280b8e4ba0e1cfd8165"


class I063PhysicsLawError(ValueError):
    pass


@dataclass(frozen=True)
class DimensionSignature:
    M: int = 0
    L: int = 0
    T: int = 0
    I: int = 0
    Theta: int = 0
    N: int = 0
    J: int = 0

    @classmethod
    def from_mapping(cls, value: Mapping[str, int] | None = None) -> "DimensionSignature":
        source = dict(value or {})
        unknown = sorted(set(source) - set(SI_BASE_AXES))
        if unknown:
            raise I063PhysicsLawError(
                f"unknown SI base-dimension axes: {','.join(unknown)}"
            )
        normalized: dict[str, int] = {}
        for axis in SI_BASE_AXES:
            raw = source.get(axis, 0)
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise I063PhysicsLawError(
                    f"dimension exponent {axis} must be an integer"
                )
            normalized[axis] = raw
        return cls(**normalized)

    def multiply(self, other: "DimensionSignature") -> "DimensionSignature":
        return DimensionSignature(
            **{
                axis: getattr(self, axis) + getattr(other, axis)
                for axis in SI_BASE_AXES
            }
        )

    def power(self, exponent: int) -> "DimensionSignature":
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise I063PhysicsLawError("dimension power must be an integer")
        return DimensionSignature(
            **{axis: getattr(self, axis) * exponent for axis in SI_BASE_AXES}
        )

    def canonical(self) -> dict[str, int]:
        return {axis: getattr(self, axis) for axis in SI_BASE_AXES}

    @property
    def dimensionless(self) -> bool:
        return all(getattr(self, axis) == 0 for axis in SI_BASE_AXES)


@dataclass(frozen=True)
class SourceIdentity:
    path: str
    git_blob_sha: str
    source_kind: str
    verbatim_expression: str

    def canonical(self) -> dict[str, str]:
        if not isinstance(self.path, str) or not self.path.strip():
            raise I063PhysicsLawError("source path required")
        if not re.fullmatch(r"[0-9a-f]{40}", self.git_blob_sha):
            raise I063PhysicsLawError("source git blob SHA must be 40 lowercase hex")
        if not isinstance(self.source_kind, str) or not self.source_kind.strip():
            raise I063PhysicsLawError("source kind required")
        if not isinstance(self.verbatim_expression, str) or not self.verbatim_expression:
            raise I063PhysicsLawError("verbatim source expression required")
        return {
            "path": self.path,
            "git_blob_sha": self.git_blob_sha,
            "source_kind": self.source_kind,
            "verbatim_expression": self.verbatim_expression,
        }


@dataclass(frozen=True)
class VariableSpec:
    symbol: str
    role: str
    dimension: DimensionSignature
    unit_symbol: str
    exact_type: str
    domain: str

    def canonical(self) -> dict[str, Any]:
        for name, value in (
            ("symbol", self.symbol),
            ("role", self.role),
            ("unit_symbol", self.unit_symbol),
            ("exact_type", self.exact_type),
            ("domain", self.domain),
        ):
            if not isinstance(value, str) or not value.strip():
                raise I063PhysicsLawError(f"variable {name} required")
        return {
            "symbol": self.symbol,
            "role": self.role,
            "dimension": self.dimension.canonical(),
            "unit_symbol": self.unit_symbol,
            "exact_type": self.exact_type,
            "domain": self.domain,
        }


@dataclass(frozen=True)
class DimensionalEquality:
    """All multiplicative terms in one additive/equality family must match."""

    label: str
    terms: tuple[tuple[tuple[str, int], ...], ...]

    @classmethod
    def make(
        cls,
        label: str,
        terms: Sequence[Mapping[str, int]],
    ) -> "DimensionalEquality":
        normalized: list[tuple[tuple[str, int], ...]] = []
        for term in terms:
            row: list[tuple[str, int]] = []
            for symbol, power in term.items():
                if isinstance(power, bool) or not isinstance(power, int):
                    raise I063PhysicsLawError(
                        f"dimension witness power for {symbol} must be integer"
                    )
                if power != 0:
                    row.append((str(symbol), power))
            normalized.append(tuple(row))
        if len(normalized) < 2:
            raise I063PhysicsLawError(
                "dimensional equality needs at least two comparable terms"
            )
        return cls(str(label), tuple(normalized))

    def canonical(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "terms": [
                [{"symbol": symbol, "power": power} for symbol, power in term]
                for term in self.terms
            ],
        }


@dataclass(frozen=True)
class EmpiricalPolicy:
    measured_behavior_permitted: bool
    calibration_required_when_measured: bool
    allowed_declared_domains: tuple[str, ...] = ()

    def canonical(self) -> dict[str, Any]:
        domains = tuple(str(x).strip() for x in self.allowed_declared_domains)
        if any(not x for x in domains):
            raise I063PhysicsLawError("empirical declared domains cannot be empty")
        return {
            "measured_behavior_permitted": bool(self.measured_behavior_permitted),
            "calibration_required_when_measured": bool(
                self.calibration_required_when_measured
            ),
            "allowed_declared_domains": list(domains),
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


def _dimension_of_term(
    term: Sequence[tuple[str, int]],
    variables: Mapping[str, VariableSpec],
) -> DimensionSignature:
    result = DimensionSignature()
    for symbol, power in term:
        if symbol not in variables:
            raise I063PhysicsLawError(
                f"dimension witness references undeclared variable {symbol}"
            )
        result = result.multiply(variables[symbol].dimension.power(power))
    return result


def _validate_dimension_equalities(
    witnesses: Sequence[DimensionalEquality],
    variables: Mapping[str, VariableSpec],
) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for witness in witnesses:
        dimensions = [
            _dimension_of_term(term, variables)
            for term in witness.terms
        ]
        reference = dimensions[0]
        if any(value != reference for value in dimensions[1:]):
            raise I063PhysicsLawError(
                f"dimension mismatch in {witness.label}: "
                + " != ".join(str(x.canonical()) for x in dimensions)
            )
        receipts.append(
            {
                "label": witness.label,
                "dimension": reference.canonical(),
                "term_count": len(dimensions),
                "closed": True,
            }
        )
    return receipts


def build_physics_law_object(
    *,
    law_id: str,
    name: str,
    classification: str,
    source: SourceIdentity,
    variables: Sequence[VariableSpec],
    dimensional_equalities: Sequence[DimensionalEquality],
    assumptions: Sequence[str],
    boundary_conditions: Sequence[str],
    law_domain: str,
    knowledge_coordinate5184: int,
    empirical_policy: EmpiricalPolicy,
) -> dict[str, Any]:
    if not isinstance(law_id, str) or not law_id.strip():
        raise I063PhysicsLawError("law_id required")
    if not isinstance(name, str) or not name.strip():
        raise I063PhysicsLawError("law name required")
    if classification not in LAW_CLASSES:
        raise I063PhysicsLawError(f"unsupported law classification {classification}")
    if (
        isinstance(knowledge_coordinate5184, bool)
        or not isinstance(knowledge_coordinate5184, int)
        or not 0 <= knowledge_coordinate5184 < 5184
    ):
        raise I063PhysicsLawError(
            "knowledge_coordinate5184 must be in [0, 5183]"
        )
    if not isinstance(law_domain, str) or not law_domain.strip():
        raise I063PhysicsLawError("law domain required")

    variable_rows = [item.canonical() for item in variables]
    symbols = [row["symbol"] for row in variable_rows]
    if len(symbols) != len(set(symbols)):
        raise I063PhysicsLawError("law variables must have unique symbols")
    variable_map = {item.symbol: item for item in variables}

    if not dimensional_equalities:
        raise I063PhysicsLawError("at least one dimensional witness required")
    dimension_receipts = _validate_dimension_equalities(
        dimensional_equalities,
        variable_map,
    )

    assumption_rows = [str(x).strip() for x in assumptions]
    boundary_rows = [str(x).strip() for x in boundary_conditions]
    if any(not x for x in assumption_rows):
        raise I063PhysicsLawError("assumptions cannot contain empty entries")
    if any(not x for x in boundary_rows):
        raise I063PhysicsLawError("boundary conditions cannot contain empty entries")

    policy = empirical_policy.canonical()
    if classification in (CLASS_HHS_ADMISSIBILITY, CLASS_PROJECTION_ONLY):
        if policy["measured_behavior_permitted"]:
            raise I063PhysicsLawError(
                f"{classification} cannot by itself claim measured physical behavior"
            )
    if (
        classification in (CLASS_STANDARD_PHYSICS, CLASS_HHS_PHYSICAL_HYPOTHESIS)
        and policy["measured_behavior_permitted"]
        and not policy["calibration_required_when_measured"]
    ):
        raise I063PhysicsLawError(
            "measured behavior must require I061 empirical calibration/experiment"
        )

    lean = lean_identity_receipt()
    if not lean["theorem_identity_valid"] or not lean["dependency_identity_valid"]:
        raise I063PhysicsLawError("I060 Lean identity receipt invalid")

    source_row = source.canonical()
    formal_material = {
        "source": source_row,
        "law_id": law_id,
        "classification": classification,
        "variables": variable_rows,
        "dimensional_equalities": [
            witness.canonical() for witness in dimensional_equalities
        ],
        "dimension_receipts": dimension_receipts,
        "assumptions": assumption_rows,
        "boundary_conditions": boundary_rows,
        "law_domain": law_domain,
        "i060_theorem_identity_hash72": lean["theorem_identity_hash72"],
        "i060_dependency_identity_hash72": lean["dependency_identity_hash72"],
    }
    law_formal_identity_hash72 = _hash72("law-formal-identity", formal_material)

    body = {
        "schema": SCHEMA,
        "version": VERSION,
        "i063_base_main": I063_BASE_MAIN,
        "inherited_i061_merge": I061_MERGE,
        "inherited_i062_merge": I062_MERGE,
        "law_id": law_id,
        "name": name,
        "classification": classification,
        "source": source_row,
        "variables": variable_rows,
        "dimensional_equalities": [
            witness.canonical() for witness in dimensional_equalities
        ],
        "dimension_receipts": dimension_receipts,
        "assumptions": assumption_rows,
        "boundary_conditions": boundary_rows,
        "law_domain": law_domain,
        "knowledge_coordinate5184": knowledge_coordinate5184,
        "empirical_policy": policy,
        "proof_identity": {
            "i060_theorem_identity_hash72": lean["theorem_identity_hash72"],
            "i060_dependency_identity_hash72": lean["dependency_identity_hash72"],
            "law_formal_identity_hash72": law_formal_identity_hash72,
            "bound_during_law_construction": True,
            "post_hoc_proof_attachment": False,
        },
        "exact_source_required": True,
        "dimensions_required": True,
        "assumptions_boundary_conditions_part_of_identity": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
    }
    body["law_object_hash72"] = _hash72("canonical-physics-law-object", body)
    return body


def validate_physics_law_object(law: Mapping[str, Any]) -> dict[str, Any]:
    if law.get("schema") != SCHEMA:
        raise I063PhysicsLawError("law schema mismatch")
    if law.get("i063_base_main") != I063_BASE_MAIN:
        raise I063PhysicsLawError("I063 base lineage mismatch")
    if law.get("inherited_i061_merge") != I061_MERGE:
        raise I063PhysicsLawError("I061 lineage missing")
    if law.get("inherited_i062_merge") != I062_MERGE:
        raise I063PhysicsLawError("I062 lineage missing")
    if law.get("classification") not in LAW_CLASSES:
        raise I063PhysicsLawError("law classification invalid")

    source = law.get("source")
    if not isinstance(source, Mapping):
        raise I063PhysicsLawError("law source identity missing")
    SourceIdentity(
        path=str(source.get("path", "")),
        git_blob_sha=str(source.get("git_blob_sha", "")),
        source_kind=str(source.get("source_kind", "")),
        verbatim_expression=str(source.get("verbatim_expression", "")),
    ).canonical()

    variable_rows = law.get("variables")
    if not isinstance(variable_rows, list) or not variable_rows:
        raise I063PhysicsLawError("law variables missing")
    variables: dict[str, VariableSpec] = {}
    for row in variable_rows:
        if not isinstance(row, Mapping):
            raise I063PhysicsLawError("variable row invalid")
        symbol = str(row.get("symbol", ""))
        spec = VariableSpec(
            symbol=symbol,
            role=str(row.get("role", "")),
            dimension=DimensionSignature.from_mapping(row.get("dimension")),
            unit_symbol=str(row.get("unit_symbol", "")),
            exact_type=str(row.get("exact_type", "")),
            domain=str(row.get("domain", "")),
        )
        spec.canonical()
        if symbol in variables:
            raise I063PhysicsLawError("duplicate variable symbol")
        variables[symbol] = spec

    witness_rows = law.get("dimensional_equalities")
    if not isinstance(witness_rows, list) or not witness_rows:
        raise I063PhysicsLawError("dimension witnesses missing")
    witnesses: list[DimensionalEquality] = []
    for row in witness_rows:
        if not isinstance(row, Mapping):
            raise I063PhysicsLawError("dimension witness row invalid")
        terms = []
        for term in row.get("terms", []):
            if not isinstance(term, list):
                raise I063PhysicsLawError("dimension witness term invalid")
            terms.append(
                {
                    str(part["symbol"]): int(part["power"])
                    for part in term
                }
            )
        witnesses.append(DimensionalEquality.make(str(row.get("label", "")), terms))

    recomputed_dimension_receipts = _validate_dimension_equalities(
        witnesses, variables
    )
    if law.get("dimension_receipts") != recomputed_dimension_receipts:
        raise I063PhysicsLawError("dimension receipt drift")

    policy_row = law.get("empirical_policy")
    if not isinstance(policy_row, Mapping):
        raise I063PhysicsLawError("empirical policy missing")
    policy = EmpiricalPolicy(
        measured_behavior_permitted=bool(
            policy_row.get("measured_behavior_permitted")
        ),
        calibration_required_when_measured=bool(
            policy_row.get("calibration_required_when_measured")
        ),
        allowed_declared_domains=tuple(
            policy_row.get("allowed_declared_domains", ())
        ),
    )
    policy.canonical()
    if law["classification"] in (CLASS_HHS_ADMISSIBILITY, CLASS_PROJECTION_ONLY):
        if policy.measured_behavior_permitted:
            raise I063PhysicsLawError(
                "nonphysical/admission law cannot claim measured behavior"
            )

    lean = lean_identity_receipt()
    proof = law.get("proof_identity")
    if not isinstance(proof, Mapping):
        raise I063PhysicsLawError("law proof identity missing")
    if proof.get("i060_theorem_identity_hash72") != lean["theorem_identity_hash72"]:
        raise I063PhysicsLawError("I060 theorem identity drift")
    if proof.get("i060_dependency_identity_hash72") != lean["dependency_identity_hash72"]:
        raise I063PhysicsLawError("I060 dependency identity drift")
    if proof.get("bound_during_law_construction") is not True:
        raise I063PhysicsLawError("law proof identity was not intrinsic")
    if proof.get("post_hoc_proof_attachment") is not False:
        raise I063PhysicsLawError("post-hoc proof attachment detected")

    formal_material = {
        "source": dict(source),
        "law_id": law["law_id"],
        "classification": law["classification"],
        "variables": variable_rows,
        "dimensional_equalities": witness_rows,
        "dimension_receipts": recomputed_dimension_receipts,
        "assumptions": law.get("assumptions", []),
        "boundary_conditions": law.get("boundary_conditions", []),
        "law_domain": law.get("law_domain"),
        "i060_theorem_identity_hash72": lean["theorem_identity_hash72"],
        "i060_dependency_identity_hash72": lean["dependency_identity_hash72"],
    }
    expected_formal_hash = _hash72("law-formal-identity", formal_material)
    if proof.get("law_formal_identity_hash72") != expected_formal_hash:
        raise I063PhysicsLawError("law formal identity Hash72 drift")

    for key in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_commit_authority",
        "canonical_hash216_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if law.get(key) is not False:
            raise I063PhysicsLawError(f"law authority escalation: {key}")

    body = dict(law)
    claimed = body.pop("law_object_hash72", None)
    expected = _hash72("canonical-physics-law-object", body)
    if claimed != expected or not validate_hash72(claimed):
        raise I063PhysicsLawError("law object Hash72 mismatch")

    coordinate = law.get("knowledge_coordinate5184")
    if (
        isinstance(coordinate, bool)
        or not isinstance(coordinate, int)
        or not 0 <= coordinate < 5184
    ):
        raise I063PhysicsLawError("law 5184 coordinate invalid")

    return {
        "ok": True,
        "schema": SCHEMA,
        "law_id": law["law_id"],
        "classification": law["classification"],
        "law_object_hash72": claimed,
        "law_formal_identity_hash72": expected_formal_hash,
        "knowledge_coordinate5184": coordinate,
        "dimension_witness_count": len(witnesses),
        "canonical_authority_escalation": False,
    }


def bind_law_to_i061_candidate(
    law: Mapping[str, Any],
    *,
    tick: int,
    body_count: int,
    collider_count: int,
    constraint_count: int,
    delta_time: ExactRational,
    parent_hash216: str,
    claims_measured_physical_behavior: bool = False,
    declared_domain: str | None = None,
    calibration_evidence: Sequence[CalibrationEvidence] = (),
) -> dict[str, Any]:
    law_validation = validate_physics_law_object(law)
    policy = law["empirical_policy"]

    if claims_measured_physical_behavior:
        if not policy["measured_behavior_permitted"]:
            raise I063PhysicsLawError(
                "law classification/policy does not permit measured-behavior claim"
            )
        if policy["calibration_required_when_measured"] and not calibration_evidence:
            raise I063PhysicsLawError(
                "measured law mechanic requires I061 calibration/experimental evidence"
            )
        allowed = tuple(policy.get("allowed_declared_domains", ()))
        if allowed and declared_domain not in allowed:
            raise I063PhysicsLawError(
                "declared domain is outside this law object's admitted domains"
            )

    try:
        i061 = build_scientific_physics_candidate(
            tick=tick,
            body_count=body_count,
            collider_count=collider_count,
            constraint_count=constraint_count,
            delta_time=delta_time,
            knowledge_coordinate5184=law["knowledge_coordinate5184"],
            parent_hash216=parent_hash216,
            claims_measured_physical_behavior=claims_measured_physical_behavior,
            declared_domain=declared_domain,
            calibration_evidence=calibration_evidence,
        )
        i061_validation = validate_scientific_physics_candidate(i061)
    except I061PhysicsSynthesisError as exc:
        raise I063PhysicsLawError(f"I061 admission envelope rejected: {exc}") from exc

    binding_material = {
        "law_object_hash72": law["law_object_hash72"],
        "law_formal_identity_hash72": law["proof_identity"][
            "law_formal_identity_hash72"
        ],
        "i061_candidate_receipt_hash72": i061["candidate_receipt_hash72"],
        "i061_physics_candidate_hash72": i061["lane5_knowledge_graph_binding"][
            "physics_candidate_hash72"
        ],
        "i061_candidate_hash216": i061["lane5_knowledge_graph_binding"][
            "candidate_hash216"
        ],
        "knowledge_coordinate5184": law["knowledge_coordinate5184"],
        "binding_stage": "PRE_SOLVER_STATE_CONSTRUCTION",
    }
    law_to_i061_binding_hash72 = _hash72(
        "law-to-i061-admission-binding", binding_material
    )

    envelope = {
        "schema": "HHS_PASS_220_I063_LAW_TO_I061_ADMISSION_ENVELOPE_V1",
        "law_id": law["law_id"],
        "law_object_hash72": law["law_object_hash72"],
        "law_validation": law_validation,
        "i061_candidate": i061,
        "i061_validation": i061_validation,
        "law_to_i061_binding": {
            **binding_material,
            "law_to_i061_binding_hash72": law_to_i061_binding_hash72,
        },
        "solver_state_constructed": False,
        "post_hoc_law_attachment": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    envelope["envelope_hash72"] = _hash72("law-i061-envelope", envelope)
    return envelope


def validate_law_to_i061_envelope(
    law: Mapping[str, Any],
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    law_result = validate_physics_law_object(law)
    if envelope.get("schema") != (
        "HHS_PASS_220_I063_LAW_TO_I061_ADMISSION_ENVELOPE_V1"
    ):
        raise I063PhysicsLawError("law/I061 envelope schema mismatch")
    if envelope.get("law_id") != law["law_id"]:
        raise I063PhysicsLawError("law/I061 envelope law id mismatch")
    if envelope.get("law_object_hash72") != law["law_object_hash72"]:
        raise I063PhysicsLawError("law/I061 envelope law identity mismatch")
    if envelope.get("solver_state_constructed") is not False:
        raise I063PhysicsLawError(
            "I063 law binding must exist before solver-state construction"
        )
    if envelope.get("post_hoc_law_attachment") is not False:
        raise I063PhysicsLawError("post-hoc law attachment detected")

    i061 = envelope.get("i061_candidate")
    if not isinstance(i061, Mapping):
        raise I063PhysicsLawError("I061 candidate missing from law envelope")
    i061_result = validate_scientific_physics_candidate(i061)

    binding = envelope.get("law_to_i061_binding")
    if not isinstance(binding, Mapping):
        raise I063PhysicsLawError("law/I061 binding missing")
    expected_material = {
        "law_object_hash72": law["law_object_hash72"],
        "law_formal_identity_hash72": law["proof_identity"][
            "law_formal_identity_hash72"
        ],
        "i061_candidate_receipt_hash72": i061["candidate_receipt_hash72"],
        "i061_physics_candidate_hash72": i061["lane5_knowledge_graph_binding"][
            "physics_candidate_hash72"
        ],
        "i061_candidate_hash216": i061["lane5_knowledge_graph_binding"][
            "candidate_hash216"
        ],
        "knowledge_coordinate5184": law["knowledge_coordinate5184"],
        "binding_stage": "PRE_SOLVER_STATE_CONSTRUCTION",
    }
    expected_binding_hash = _hash72(
        "law-to-i061-admission-binding", expected_material
    )
    if binding != {
        **expected_material,
        "law_to_i061_binding_hash72": expected_binding_hash,
    }:
        raise I063PhysicsLawError("law/I061 intrinsic binding drift")

    for key in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_commit_authority",
        "canonical_hash216_persistence_authority",
    ):
        if envelope.get(key) is not False:
            raise I063PhysicsLawError(f"law/I061 envelope authority escalation: {key}")

    body = dict(envelope)
    claimed = body.pop("envelope_hash72", None)
    expected = _hash72("law-i061-envelope", body)
    if claimed != expected or not validate_hash72(claimed):
        raise I063PhysicsLawError("law/I061 envelope Hash72 mismatch")

    return {
        "ok": True,
        "law_validation": law_result,
        "i061_validation": i061_result,
        "law_to_i061_binding_hash72": expected_binding_hash,
        "envelope_hash72": claimed,
        "pre_solver_binding": True,
        "canonical_authority_escalation": False,
    }


def relativistic_energy_momentum_law() -> dict[str, Any]:
    energy = DimensionSignature(M=1, L=2, T=-2)
    momentum = DimensionSignature(M=1, L=1, T=-1)
    velocity = DimensionSignature(L=1, T=-1)
    mass = DimensionSignature(M=1)

    return build_physics_law_object(
        law_id="STANDARD_RELATIVISTIC_ENERGY_MOMENTUM_V1",
        name="Relativistic energy-momentum relation",
        classification=CLASS_STANDARD_PHYSICS,
        source=SourceIdentity(
            path=PASS178_SOURCE,
            git_blob_sha=PASS178_BLOB_SHA,
            source_kind="PASS178_STANDARD_PHYSICS_EQUATION",
            verbatim_expression=r"E^2-p^2c^2=m^2c^4",
        ),
        variables=(
            VariableSpec(
                "E", "total_energy", energy, "J", "ExactOrSymbolic", "REAL_NONNEGATIVE"
            ),
            VariableSpec(
                "p", "momentum_magnitude", momentum, "kg*m/s", "ExactOrSymbolic", "REAL_NONNEGATIVE"
            ),
            VariableSpec(
                "c", "invariant_speed", velocity, "m/s", "ExactOrSymbolic", "REAL_POSITIVE"
            ),
            VariableSpec(
                "m", "rest_mass", mass, "kg", "ExactOrSymbolic", "REAL_NONNEGATIVE"
            ),
        ),
        dimensional_equalities=(
            DimensionalEquality.make(
                "energy_momentum_mass_shell",
                (
                    {"E": 2},
                    {"p": 2, "c": 2},
                    {"m": 2, "c": 4},
                ),
            ),
        ),
        assumptions=(
            "Minkowski metric selection is explicit and typed.",
            "Square roots remain algebraic-root nodes or certified intervals.",
            "Renderer-derived velocity has no solver authority.",
        ),
        boundary_conditions=(
            "Massive-particle admission requires v^2<c^2.",
            "Proper and coordinate time remain distinct typed quantities.",
        ),
        law_domain="RELATIVISTIC_MECHANICS",
        knowledge_coordinate5184=13,
        empirical_policy=EmpiricalPolicy(
            measured_behavior_permitted=True,
            calibration_required_when_measured=True,
            allowed_declared_domains=(
                "RELATIVISTIC_PARTICLE_LAB",
                "DECLARED_RELATIVISTIC_BENCH",
            ),
        ),
    )


def hhs_p4_ab_admissibility_law() -> dict[str, Any]:
    dimensionless = DimensionSignature()
    return build_physics_law_object(
        law_id="HHS_MEMBRANE_P4_AB_V1",
        name="HHS canonical membrane P^4=AB",
        classification=CLASS_HHS_ADMISSIBILITY,
        source=SourceIdentity(
            path=PASS178_SOURCE,
            git_blob_sha=PASS178_BLOB_SHA,
            source_kind="PASS178_HHS_ADMISSIBILITY_CONSTRAINT",
            verbatim_expression=r"\boxed{P^4=AB}",
        ),
        variables=(
            VariableSpec(
                "P", "ordered_hhs_carrier", dimensionless, "1", "HHSExact", "HHS_TYPED"
            ),
            VariableSpec(
                "A", "ordered_hhs_left_carrier", dimensionless, "1", "HHSExact", "HHS_TYPED"
            ),
            VariableSpec(
                "B", "ordered_hhs_right_carrier", dimensionless, "1", "HHSExact", "HHS_TYPED"
            ),
        ),
        dimensional_equalities=(
            DimensionalEquality.make(
                "p4_ab_dimensionless_projection",
                (
                    {"P": 4},
                    {"A": 1, "B": 1},
                ),
            ),
        ),
        assumptions=(
            "Operators retain HHS typed ordered semantics.",
            "No commutation, cancellation, or scalar substitution is implied.",
        ),
        boundary_conditions=(
            "Branch and domain witnesses remain required where derived roots occur.",
        ),
        law_domain="HHS_ADMISSION_MEMBRANE",
        knowledge_coordinate5184=10,
        empirical_policy=EmpiricalPolicy(
            measured_behavior_permitted=False,
            calibration_required_when_measured=False,
        ),
    )


def canonical_stem_physics_law_self_test() -> dict[str, Any]:
    standard = relativistic_energy_momentum_law()
    hhs = hhs_p4_ab_admissibility_law()
    standard_result = validate_physics_law_object(standard)
    hhs_result = validate_physics_law_object(hhs)

    parent = (
        _hash72("self-test-parent-minus", "minus")
        + _hash72("self-test-parent-center", "center")
        + _hash72("self-test-parent-plus", "plus")
    )
    envelope = bind_law_to_i061_candidate(
        hhs,
        tick=63,
        body_count=1,
        collider_count=1,
        constraint_count=0,
        delta_time=ExactRational(1, 120),
        parent_hash216=parent,
    )
    envelope_result = validate_law_to_i061_envelope(hhs, envelope)

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "ok": (
            standard_result["ok"]
            and hhs_result["ok"]
            and envelope_result["ok"]
        ),
        "standard_physics_law_hash72": standard["law_object_hash72"],
        "hhs_admissibility_law_hash72": hhs["law_object_hash72"],
        "law_to_i061_binding_hash72": envelope_result[
            "law_to_i061_binding_hash72"
        ],
        "standard_and_hhs_classes_distinct": (
            standard["classification"] != hhs["classification"]
        ),
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }


__all__ = [
    "CLASS_HHS_ADMISSIBILITY",
    "CLASS_HHS_PHYSICAL_HYPOTHESIS",
    "CLASS_PROJECTION_ONLY",
    "CLASS_STANDARD_PHYSICS",
    "CalibrationEvidence",
    "DimensionSignature",
    "DimensionalEquality",
    "EmpiricalPolicy",
    "ExactRational",
    "I063PhysicsLawError",
    "SCHEMA",
    "SourceIdentity",
    "VariableSpec",
    "bind_law_to_i061_candidate",
    "build_physics_law_object",
    "canonical_stem_physics_law_self_test",
    "hhs_p4_ab_admissibility_law",
    "relativistic_energy_momentum_law",
    "validate_law_to_i061_envelope",
    "validate_physics_law_object",
]
