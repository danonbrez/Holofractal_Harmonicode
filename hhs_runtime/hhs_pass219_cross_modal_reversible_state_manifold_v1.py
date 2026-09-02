"""Pass 219 additive cross-modal reversible state-manifold verifier.

This module is a candidate planning/verification membrane. It never mints a
canonical Hash72/Hash216 receipt and never mutates VM81. Canonical mutation
remains the inherited singleton C VM81 path.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable, Mapping, Sequence

SCHEMA = "HHS_PASS219_CROSS_MODAL_REVERSIBLE_STATE_MANIFOLD_V1"
VERSION = "1.0.0"
VM81_CELLS = 81
OPERATIONS_PER_CELL = 64
VM81_ADDRESSES = 5184
PHASE_BASIS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")


def _stable_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ModalityProjectionWitness:
    modality_id: str
    canonical_root_sha256: str
    projection_sha256: str
    recovered_canonical_root_sha256: str
    reversible: bool = True

    @property
    def roundtrip_verified(self) -> bool:
        return (
            self.reversible
            and self.canonical_root_sha256 == self.recovered_canonical_root_sha256
        )


@dataclass(frozen=True)
class ReversibleOperationWitness:
    forward_state_id: str
    inverse_state_id: str
    recovered_parent_id: str
    expected_parent_id: str
    exact_roundtrip_verified: bool

    @property
    def ok(self) -> bool:
        return (
            self.exact_roundtrip_verified
            and self.recovered_parent_id == self.expected_parent_id
            and bool(self.forward_state_id)
            and bool(self.inverse_state_id)
        )


@dataclass(frozen=True)
class BranchState:
    node_id: str
    parent_id: str
    depth: int
    genesis_id: str
    phase_path: tuple[str, ...]
    canonical_root_sha256: str
    constraint_root: str
    modality_registry_root: str
    hash216_lineage: str
    projections: tuple[ModalityProjectionWitness, ...]

    @property
    def ordered_phase_identity(self) -> str:
        return _stable_sha256({"phase_path": list(self.phase_path)})


def derive_node_id(
    *,
    parent_id: str,
    depth: int,
    genesis_id: str,
    phase_path: Sequence[str],
    canonical_root_sha256: str,
    constraint_root: str,
    modality_registry_root: str,
    hash216_lineage: str,
) -> str:
    return _stable_sha256(
        {
            "parent_id": parent_id,
            "depth": depth,
            "genesis_id": genesis_id,
            "phase_path": list(phase_path),
            "canonical_root_sha256": canonical_root_sha256,
            "constraint_root": constraint_root,
            "modality_registry_root": modality_registry_root,
            "hash216_lineage": hash216_lineage,
        }
    )


def make_branch_state(
    *,
    parent_id: str,
    depth: int,
    genesis_id: str,
    phase_path: Sequence[str],
    canonical_root_sha256: str,
    constraint_root: str,
    modality_registry_root: str,
    hash216_lineage: str,
    projections: Iterable[ModalityProjectionWitness],
) -> BranchState:
    projection_tuple = tuple(projections)
    node_id = derive_node_id(
        parent_id=parent_id,
        depth=depth,
        genesis_id=genesis_id,
        phase_path=phase_path,
        canonical_root_sha256=canonical_root_sha256,
        constraint_root=constraint_root,
        modality_registry_root=modality_registry_root,
        hash216_lineage=hash216_lineage,
    )
    return BranchState(
        node_id=node_id,
        parent_id=parent_id,
        depth=depth,
        genesis_id=genesis_id,
        phase_path=tuple(phase_path),
        canonical_root_sha256=canonical_root_sha256,
        constraint_root=constraint_root,
        modality_registry_root=modality_registry_root,
        hash216_lineage=hash216_lineage,
        projections=projection_tuple,
    )


def validate_branch_state(
    state: BranchState,
    *,
    required_modalities: Sequence[str],
    required_constraint_root: str,
    required_modality_registry_root: str,
) -> Mapping[str, object]:
    failures: list[str] = []
    required = tuple(required_modalities)
    observed_ids = tuple(p.modality_id for p in state.projections)

    if state.depth < 0:
        failures.append("NEGATIVE_DEPTH")
    if state.depth == 0 and state.parent_id:
        failures.append("GENESIS_HAS_PARENT")
    if state.depth > 0 and not state.parent_id:
        failures.append("MISSING_PARENT_LINEAGE")
    if not state.genesis_id:
        failures.append("MISSING_GENESIS")
    if not state.phase_path or any(p not in PHASE_BASIS for p in state.phase_path):
        failures.append("INVALID_ORDERED_PHASE_PATH")
    if not state.constraint_root or state.constraint_root != required_constraint_root:
        failures.append("GLOBAL_CONSTRAINT_ROOT_MISMATCH")
    if (
        not state.modality_registry_root
        or state.modality_registry_root != required_modality_registry_root
    ):
        failures.append("MODALITY_REGISTRY_ROOT_MISMATCH")
    if len(state.hash216_lineage) != 216:
        failures.append("HASH216_LINEAGE_WIDTH_MISMATCH")
    if len(set(observed_ids)) != len(observed_ids):
        failures.append("DUPLICATE_MODALITY_MAPPING")
    if tuple(sorted(observed_ids)) != tuple(sorted(required)):
        failures.append("REQUIRED_MODALITY_COVERAGE_MISMATCH")

    for projection in state.projections:
        if projection.canonical_root_sha256 != state.canonical_root_sha256:
            failures.append(f"CANONICAL_ROOT_MISMATCH:{projection.modality_id}")
        if not projection.roundtrip_verified:
            failures.append(f"ROUNDTRIP_MISMATCH:{projection.modality_id}")

    expected_node_id = derive_node_id(
        parent_id=state.parent_id,
        depth=state.depth,
        genesis_id=state.genesis_id,
        phase_path=state.phase_path,
        canonical_root_sha256=state.canonical_root_sha256,
        constraint_root=state.constraint_root,
        modality_registry_root=state.modality_registry_root,
        hash216_lineage=state.hash216_lineage,
    )
    if state.node_id != expected_node_id:
        failures.append("NODE_ID_REPLAY_MISMATCH")

    return {
        "schema": SCHEMA,
        "ok": not failures,
        "failures": failures,
        "node_id": state.node_id,
        "ordered_phase_identity": state.ordered_phase_identity,
        "mapped_modalities": len(state.projections),
        "required_modalities": len(required),
        "vm81_addresses": VM81_ADDRESSES,
        "candidate_mutation_authority": False,
        "singleton_vm81_authority_required": True,
        "floating_point_authority": False,
    }


def validate_replay(states: Sequence[BranchState]) -> Mapping[str, object]:
    failures: list[str] = []
    if not states:
        return {"schema": SCHEMA, "ok": False, "failures": ["EMPTY_REPLAY"]}
    for index, state in enumerate(states):
        if index == 0:
            continue
        parent = states[index - 1]
        if state.parent_id != parent.node_id:
            failures.append(f"PARENT_LINK_MISMATCH:{index}")
        if state.depth != parent.depth + 1:
            failures.append(f"DEPTH_MISMATCH:{index}")
        if state.genesis_id != parent.genesis_id:
            failures.append(f"GENESIS_DRIFT:{index}")
    return {
        "schema": SCHEMA,
        "ok": not failures,
        "failures": failures,
        "states": len(states),
        "candidate_mutation_authority": False,
    }


def validate_sibling_merge(
    base: BranchState,
    left: BranchState,
    right: BranchState,
) -> Mapping[str, object]:
    conflicts: list[str] = []
    if left.parent_id != base.node_id or right.parent_id != base.node_id:
        conflicts.append("NOT_SIBLING_BRANCHES")
    if left.constraint_root != right.constraint_root:
        conflicts.append("CONSTRAINT_ROOT_CONFLICT")
    if left.modality_registry_root != right.modality_registry_root:
        conflicts.append("MODALITY_REGISTRY_CONFLICT")
    if left.genesis_id != right.genesis_id or left.genesis_id != base.genesis_id:
        conflicts.append("GENESIS_CONFLICT")
    return {
        "schema": SCHEMA,
        "mergeable": not conflicts,
        "conflicts": conflicts,
        "requires_singleton_vm81_admission": True,
        "candidate_merge_authority": False,
    }


def exact_work_plan(
    *,
    depth: int,
    modalities: int,
    constraints_per_state: int,
    cached_prefix_depth: int,
    changed_constraints: int,
    prefix_proof_valid: bool,
    hub_roundtrip_verified: bool,
) -> Mapping[str, int | bool | str]:
    if not (1 <= depth <= 1_000_000):
        raise ValueError("depth out of range")
    if not (2 <= modalities <= 64):
        raise ValueError("modalities out of range")
    if not (1 <= constraints_per_state <= 1_000_000):
        raise ValueError("constraints_per_state out of range")
    if not (0 <= cached_prefix_depth <= depth):
        raise ValueError("cached_prefix_depth out of range")
    if not (0 <= changed_constraints <= constraints_per_state):
        raise ValueError("changed_constraints out of range")

    baseline_constraint_checks = depth * modalities * constraints_per_state
    baseline_translation_checks = depth * modalities * (modalities - 1)
    baseline_authority_checks = depth
    baseline_total = (
        baseline_constraint_checks
        + baseline_translation_checks
        + baseline_authority_checks
    )

    active_depth = depth - cached_prefix_depth
    candidate_constraint_checks = (
        active_depth * modalities * constraints_per_state
        + changed_constraints * modalities
    )
    candidate_translation_checks = (active_depth + 1) * 2 * modalities
    candidate_authority_checks = depth
    candidate_total = (
        candidate_constraint_checks
        + candidate_translation_checks
        + candidate_authority_checks
    )

    selected = (
        prefix_proof_valid
        and hub_roundtrip_verified
        and cached_prefix_depth > 0
        and candidate_total < baseline_total
    )
    selected_total = candidate_total if selected else baseline_total
    saved = baseline_total - selected_total
    return {
        "schema": "HHS_PASS219_CROSS_MODAL_WORK_PLAN_V1",
        "depth": depth,
        "modalities": modalities,
        "constraints_per_state": constraints_per_state,
        "cached_prefix_depth": cached_prefix_depth,
        "changed_constraints": changed_constraints,
        "prefix_proof_valid": prefix_proof_valid,
        "hub_roundtrip_verified": hub_roundtrip_verified,
        "optimization_selected": selected,
        "complete_fallback": not selected,
        "baseline_constraint_checks": baseline_constraint_checks,
        "baseline_translation_checks": baseline_translation_checks,
        "baseline_authority_checks": baseline_authority_checks,
        "baseline_total_work": baseline_total,
        "candidate_constraint_checks": candidate_constraint_checks,
        "candidate_translation_checks": candidate_translation_checks,
        "candidate_authority_checks": candidate_authority_checks,
        "candidate_total_work": candidate_total,
        "selected_total_work": selected_total,
        "exact_work_saved": saved,
        "candidate_mutation_authority": False,
        "singleton_vm81_authority_required": True,
    }


__all__ = [
    "SCHEMA",
    "VERSION",
    "VM81_CELLS",
    "OPERATIONS_PER_CELL",
    "VM81_ADDRESSES",
    "PHASE_BASIS",
    "ModalityProjectionWitness",
    "ReversibleOperationWitness",
    "BranchState",
    "derive_node_id",
    "make_branch_state",
    "validate_branch_state",
    "validate_replay",
    "validate_sibling_merge",
    "exact_work_plan",
]
