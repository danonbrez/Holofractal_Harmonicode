"""Pass219 I182 exact HARMONIC geometry circuit constraint kernel.

This first iteration is an exact, fail-closed computational-geometry verifier.
It does not mint VM81 authority, Hash72 receipts, or Hash216 persistence.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any

SCHEMA = "HHS_PASS219_I182_HARMONIC_GEOMETRY_CIRCUIT_V1"
ITERATION = "PASS219-I182"
Q_H = 5184
FULL_CYCLE = 360
PENTAGON_SIDES = 5
PENTAGON_HALF_SECTOR = 36
PENTAGON_EXTERNAL = 72
PENTAGON_INTERIOR = 108
PENTAGON_SUPPLEMENTARY = 144

PLATONIC_PAIRS = frozenset({(3, 3), (4, 3), (3, 4), (5, 3), (3, 5)})


class HarmonicGeometryConstraintError(ValueError):
    """Fail-closed rejection of a non-admissible canonical geometry candidate."""


@dataclass(frozen=True)
class FactorWitness:
    left: int
    right: int
    product: int

    def verify(self) -> None:
        if self.product != Q_H or self.left * self.right != Q_H:
            raise HarmonicGeometryConstraintError("HHS_GEOMETRY_5184_FACTOR_WITNESS_INVALID")


@dataclass(frozen=True)
class PlatonicClosure:
    p: int
    q: int
    vertices: int
    edges: int
    faces: int
    euler: int

    def verify(self) -> None:
        _require_ints(self.p, self.q, self.vertices, self.edges, self.faces, self.euler)
        if (self.p, self.q) not in PLATONIC_PAIRS:
            raise HarmonicGeometryConstraintError("HHS_GEOMETRY_PLATONIC_PAIR_NOT_ADMISSIBLE")
        if self.p * self.faces != 2 * self.edges:
            raise HarmonicGeometryConstraintError("HHS_GEOMETRY_FACE_EDGE_INCIDENCE_INVALID")
        if self.q * self.vertices != 2 * self.edges:
            raise HarmonicGeometryConstraintError("HHS_GEOMETRY_VERTEX_EDGE_INCIDENCE_INVALID")
        if self.vertices - self.edges + self.faces != 2 or self.euler != 2:
            raise HarmonicGeometryConstraintError("HHS_GEOMETRY_EULER_CLOSURE_INVALID")


def _require_ints(*values: int) -> None:
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise HarmonicGeometryConstraintError("HHS_GEOMETRY_NONINTEGER_CANONICAL_INPUT")


def _exact_div(numerator: int, denominator: int, classification: str) -> int:
    _require_ints(numerator, denominator)
    if denominator == 0 or numerator % denominator != 0:
        raise HarmonicGeometryConstraintError(classification)
    return numerator // denominator


def factor_witness(left: int, right: int) -> FactorWitness:
    _require_ints(left, right)
    witness = FactorWitness(left=left, right=right, product=left * right)
    witness.verify()
    return witness


def hydration_factorization_witnesses() -> tuple[FactorWitness, ...]:
    witnesses = (
        factor_witness(72, 72),
        factor_witness(64, 81),
        factor_witness(36, 144),
        factor_witness(48, 108),
    )
    if any(item.product != Q_H for item in witnesses):
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_5184_CONSERVATION_FAILURE")
    return witnesses


def pentagonal_quantization_witness() -> dict[str, Any]:
    hydration_factorization_witnesses()

    if PENTAGON_SIDES * PENTAGON_EXTERNAL != FULL_CYCLE:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_PENTAGON_CYCLE_INVALID")
    if 3 * PENTAGON_HALF_SECTOR != PENTAGON_INTERIOR:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_PENTAGON_HALF_SECTOR_INVALID")
    if 180 - PENTAGON_EXTERNAL != PENTAGON_INTERIOR:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_PENTAGON_INTERIOR_INVALID")
    if 180 - PENTAGON_HALF_SECTOR != PENTAGON_SUPPLEMENTARY:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_PENTAGON_SUPPLEMENTARY_INVALID")

    return {
        "hydration_quantum": Q_H,
        "sides": PENTAGON_SIDES,
        "half_sector": PENTAGON_HALF_SECTOR,
        "external": PENTAGON_EXTERNAL,
        "interior": PENTAGON_INTERIOR,
        "supplementary": PENTAGON_SUPPLEMENTARY,
        "cycle": FULL_CYCLE,
        "zero_phase_closure": (PENTAGON_SIDES * PENTAGON_EXTERNAL) % FULL_CYCLE,
        "factor_witnesses": [asdict(item) for item in hydration_factorization_witnesses()],
    }


def derive_platonic_closure(p: int, q: int) -> PlatonicClosure:
    """Derive V/E/F from {p,q} and Euler closure without final mesh tables."""
    _require_ints(p, q)
    if (p, q) not in PLATONIC_PAIRS:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_PLATONIC_PAIR_NOT_ADMISSIBLE")

    denominator = 2 * p + 2 * q - p * q
    if denominator <= 0:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_NONCLOSING_PLATONIC_DENOMINATOR")

    edges = _exact_div(2 * p * q, denominator, "HHS_GEOMETRY_EDGE_COUNT_NOT_INTEGRAL")
    vertices = _exact_div(2 * edges, q, "HHS_GEOMETRY_VERTEX_COUNT_NOT_INTEGRAL")
    faces = _exact_div(2 * edges, p, "HHS_GEOMETRY_FACE_COUNT_NOT_INTEGRAL")
    closure = PlatonicClosure(
        p=p,
        q=q,
        vertices=vertices,
        edges=edges,
        faces=faces,
        euler=vertices - edges + faces,
    )
    closure.verify()
    return closure


def validate_platonic_candidate(*, p: int, q: int, vertices: int, edges: int, faces: int) -> PlatonicClosure:
    _require_ints(p, q, vertices, edges, faces)
    expected = derive_platonic_closure(p, q)
    candidate = PlatonicClosure(
        p=p,
        q=q,
        vertices=vertices,
        edges=edges,
        faces=faces,
        euler=vertices - edges + faces,
    )
    candidate.verify()
    if candidate != expected:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_PLATONIC_DERIVATION_MISMATCH")
    return candidate


def derive_dodecahedral_closure() -> PlatonicClosure:
    closure = derive_platonic_closure(5, 3)
    if (closure.vertices, closure.edges, closure.faces) != (20, 30, 12):
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_DODECAHEDRAL_CLOSURE_INVALID")
    if closure.faces * PENTAGON_SIDES != 2 * closure.edges:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_DODECAHEDRAL_FACE_INCIDENCE_INVALID")
    if closure.q * closure.vertices != 2 * closure.edges:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_DODECAHEDRAL_VERTEX_INCIDENCE_INVALID")
    return closure


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def build_geometry_constraint_receipt() -> dict[str, Any]:
    """Build deterministic non-authoritative witness receipt for I182 validation."""
    pentagon = pentagonal_quantization_witness()
    dodecahedron = asdict(derive_dodecahedral_closure())
    platonic = [asdict(derive_platonic_closure(p, q)) for p, q in sorted(PLATONIC_PAIRS)]

    body = {
        "schema": SCHEMA,
        "iteration": ITERATION,
        "classification": "HHS_HARMONIC_GEOMETRY_CONSTRAINT_WITNESS_VALID",
        "canonical_arithmetic": "EXACT_INTEGER_NO_FLOAT_AUTHORITY",
        "hydration_quantum": Q_H,
        "pentagon": pentagon,
        "dodecahedron": dodecahedron,
        "platonic_closures": platonic,
        "authoritative_vertex_table_used": False,
        "vm81_authority_minted": False,
        "hash72_authority_minted": False,
        "hash216_persistence_authority": False,
        "rendering_authority": False,
    }
    body["witness_sha256"] = sha256(_canonical_json(body).encode("ascii")).hexdigest()
    return body


def verify_geometry_constraint_receipt(receipt: dict[str, Any]) -> bool:
    if not isinstance(receipt, dict):
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_RECEIPT_ROOT_INVALID")
    candidate = dict(receipt)
    supplied = candidate.pop("witness_sha256", None)
    if not isinstance(supplied, str) or len(supplied) != 64:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_RECEIPT_DIGEST_INVALID")
    expected = sha256(_canonical_json(candidate).encode("ascii")).hexdigest()
    if supplied != expected:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_RECEIPT_MISMATCH")
    if candidate.get("schema") != SCHEMA or candidate.get("hydration_quantum") != Q_H:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_RECEIPT_METADATA_INVALID")
    if candidate.get("vm81_authority_minted") is not False:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_VM81_AUTHORITY_ESCALATION")
    if candidate.get("hash72_authority_minted") is not False:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_HASH72_AUTHORITY_ESCALATION")
    if candidate.get("hash216_persistence_authority") is not False:
        raise HarmonicGeometryConstraintError("HHS_GEOMETRY_HASH216_AUTHORITY_ESCALATION")
    derive_dodecahedral_closure().verify()
    return True


__all__ = [
    "FULL_CYCLE",
    "HarmonicGeometryConstraintError",
    "ITERATION",
    "PENTAGON_EXTERNAL",
    "PENTAGON_HALF_SECTOR",
    "PENTAGON_INTERIOR",
    "PENTAGON_SUPPLEMENTARY",
    "PLATONIC_PAIRS",
    "PlatonicClosure",
    "Q_H",
    "SCHEMA",
    "build_geometry_constraint_receipt",
    "derive_dodecahedral_closure",
    "derive_platonic_closure",
    "factor_witness",
    "hydration_factorization_witnesses",
    "pentagonal_quantization_witness",
    "validate_platonic_candidate",
    "verify_geometry_constraint_receipt",
]
