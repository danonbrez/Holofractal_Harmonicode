from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Any, Callable, Dict, Iterable, Optional, Set


class EdgeType(str, Enum):
    VALUE_DEPENDS_ON = "VALUE_DEPENDS_ON"
    CONSTRAINT_DEPENDS_ON = "CONSTRAINT_DEPENDS_ON"
    AUTHORITY_DEPENDS_ON = "AUTHORITY_DEPENDS_ON"
    PROVENANCE_DEPENDS_ON = "PROVENANCE_DEPENDS_ON"
    RECEIPT_DEPENDS_ON = "RECEIPT_DEPENDS_ON"
    RESOURCE_DEPENDS_ON = "RESOURCE_DEPENDS_ON"
    CLOSURE_DEPENDS_ON = "CLOSURE_DEPENDS_ON"


class CandidateState(str, Enum):
    UNSEEN = "UNSEEN"
    BLOCKED = "BLOCKED"
    PARTIAL = "PARTIAL"
    READY = "READY"
    EVALUATING = "EVALUATING"
    PROVISIONAL = "PROVISIONAL"
    VERIFIED = "VERIFIED"
    INVALIDATED = "INVALIDATED"
    CONFLICT = "CONFLICT"
    RESOURCE_BOUNDED = "RESOURCE_BOUNDED"
    COMMITTED = "COMMITTED"


TERMINAL_PREDICTIVE = {
    CandidateState.VERIFIED,
    CandidateState.INVALIDATED,
    CandidateState.CONFLICT,
    CandidateState.RESOURCE_BOUNDED,
}


@dataclass(frozen=True)
class TypedEdge:
    source: str
    target: str
    edge_type: EdgeType


@dataclass
class OperationNode:
    node_id: str
    operation_id: str
    compute: Optional[Callable[[Dict[str, Any]], Any]] = None
    dependencies: Set[str] = field(default_factory=set)
    edge_types: Dict[str, EdgeType] = field(default_factory=dict)
    mandatory: bool = True
    estimated_cost: Fraction = Fraction(1, 1)
    lifecycle: CandidateState = CandidateState.UNSEEN
    value: Any = None
    candidate_root: str = ""
    semantic_version: str = "1.0.0"
    phase_id: str = "0"
    lane_id: str = "default"
    provenance: list[dict[str, Any]] = field(default_factory=list)
    horizon: int = 1
    partial_inputs: Dict[str, Any] = field(default_factory=dict)
    evaluation_count: int = 0
    verification_digest: str = ""
    result_used: bool = False
    layer_id: str = "L1"
    predicted_risk: Fraction = Fraction(0, 1)
    redundancy_cost: Fraction = Fraction(0, 1)

    def ready_partial(self, resolved: Iterable[str]) -> bool:
        resolved = set(resolved)
        return bool(self.dependencies & resolved) or not self.dependencies

    def ready_final(self, resolved: Iterable[str]) -> bool:
        return self.dependencies.issubset(set(resolved))


@dataclass(frozen=True)
class EquivalenceWitness:
    witness_id: str
    source_node: str
    target_node: str
    constraint_root: str
    authority_root: str
    semantic_version: str
    operand_digest: str
    type_identity: str
    scope_identity: str
    canonical_form_source: str
    canonical_form_target: str
    phase_id: str
    source_lane: str
    target_lane: str
    proof_id: str


@dataclass(frozen=True)
class SkipWitness:
    witness_id: str
    node_id: str
    operation_id: str
    input_node: str
    constraint_root: str
    authority_root: str
    semantic_version: str
    proof_id: str
    canonical_hash: str


@dataclass(frozen=True)
class RootEquivalenceWitness:
    witness_id: str
    old_root: str
    new_root: str
    semantic_version: str
    proof_id: str


class Pass152Error(RuntimeError):
    pass


class AuthorityViolation(Pass152Error):
    pass


class ClosureIncomplete(Pass152Error):
    pass


class InvalidWitness(Pass152Error):
    pass


class ResourceBounded(Pass152Error):
    pass


class ReplayMismatch(Pass152Error):
    pass
