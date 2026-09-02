from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping

from .exact import ExactPhysicsError, ExactRational, reject_float


@dataclass(frozen=True)
class ConstraintRelation:
    relation_id: str
    left: str
    right: str
    classification: str
    status: str
    witness: str

    def __post_init__(self) -> None:
        if self.classification not in {
            "STANDARD_PHYSICS_EQUATION",
            "HHS_ADMISSIBILITY_CONSTRAINT",
            "DERIVED_SYMBOLIC_IDENTITY",
            "NUMERICAL_OR_INTERVAL_APPROXIMATION",
            "RENDER_ONLY_INTERPRETATION",
            "UNRESOLVED_HYPOTHESIS",
        }:
            raise ExactPhysicsError("P178_CONSTRAINT_CLASSIFICATION")
        if self.status not in {"SATISFIED", "REJECTED", "UNRESOLVED", "SUPERPOSED", "FOLDED"}:
            raise ExactPhysicsError("P178_CONSTRAINT_STATUS")


@dataclass(frozen=True)
class ConstraintGraph:
    source_sha256: str
    relations: tuple[ConstraintRelation, ...]

    def payload(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_178_CONSTRAINT_GRAPH_V1",
            "source_sha256": self.source_sha256,
            "relations": [
                {
                    "relation_id": r.relation_id,
                    "left": r.left,
                    "right": r.right,
                    "classification": r.classification,
                    "status": r.status,
                    "witness": r.witness,
                }
                for r in self.relations
            ],
        }

    def root_sha256(self) -> str:
        return hashlib.sha256(
            json.dumps(self.payload(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def source_identity(source: bytes) -> dict[str, Any]:
    return {
        "schema": "HHS_PASS_178_SOURCE_IDENTITY_V1",
        "bytes": len(source),
        "sha256": hashlib.sha256(source).hexdigest(),
        "byte_preserving": True,
    }


def canonical_membrane(values: Mapping[str, Any]) -> ConstraintGraph:
    reject_float(values)
    required = ("P", "A", "B", "p", "q")
    missing = [name for name in required if name not in values]
    if missing:
        raise ExactPhysicsError("P178_MEMBRANE_MISSING:" + ",".join(missing))
    P = ExactRational.coerce(values["P"])
    A = ExactRational.coerce(values["A"])
    B = ExactRational.coerce(values["B"])
    p = ExactRational.coerce(values["p"])
    q = ExactRational.coerce(values["q"])
    p2 = P ** 2
    p4 = P ** 4
    delta = p2 - p * q

    def rel(name: str, left: str, right: str, ok: bool, witness: str) -> ConstraintRelation:
        return ConstraintRelation(
            name,left,right,"HHS_ADMISSIBILITY_CONSTRAINT",
            "SATISFIED" if ok else "REJECTED",witness
        )

    relations = (
        rel("P4_AB","P^4","A*B",p4 == A * B,f"{p4.as_pair()} == {(A*B).as_pair()}"),
        rel("A_P2","A","P^2",A == p2,f"{A.as_pair()} == {p2.as_pair()}"),
        rel("B_P2","B","P^2",B == p2,f"{B.as_pair()} == {p2.as_pair()}"),
        ConstraintRelation(
            "DELTA_DEFINITION","Delta","P^2-p*q","HHS_ADMISSIBILITY_CONSTRAINT",
            "SATISFIED",str(delta.as_pair())
        ),
        ConstraintRelation(
            "O_NE_PI","O","Pi","HHS_ADMISSIBILITY_CONSTRAINT","SATISFIED",
            "symbol identities remain distinct"
        ),
        ConstraintRelation(
            "U72","u^72","1","HHS_ADMISSIBILITY_CONSTRAINT","UNRESOLVED",
            "requires typed residue/phase state"
        ),
    )
    return ConstraintGraph(
        source_sha256=hashlib.sha256(b"P178_CANONICAL_MEMBRANE_V1").hexdigest(),
        relations=relations,
    )


def membrane_admitted(graph: ConstraintGraph) -> bool:
    return not any(r.status == "REJECTED" for r in graph.relations)
