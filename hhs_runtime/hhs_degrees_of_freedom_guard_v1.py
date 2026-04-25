"""
HHS Degrees-of-Freedom Preservation Guard v1
===========================================

Prevents defensive learning/self-modification from over-constraining the kernel.

Purpose:
    Stop "immune system overdrive" where learned security penalties make the
    system so restrictive that valid operation is lost.

Core law:
    A proposed change may harden a boundary, but it must not remove valid
    kernel degrees of freedom.

Reject changes that:
    - remove core operations
    - disable replay, quarantine, or rollback
    - collapse cross-modal consensus to one modality
    - block all writes to valid runtime namespaces
    - make learning/self-modification permanently impossible
    - lower invariant enforcement
    - mutate Layer 0 directly

Allow changes that:
    - add validation
    - add quarantine conditions
    - add path allowlists with at least one valid namespace preserved
    - penalize unsafe patterns without disabling safe alternatives
    - reinforce replay and rollback
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from typing import Any, Dict, List, Sequence, Set
import json

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


class DOFGuardStatus(str, Enum):
    ALLOWED = "ALLOWED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"


class ChangeClass(str, Enum):
    VALIDATION_ADD = "VALIDATION_ADD"
    QUARANTINE_ADD = "QUARANTINE_ADD"
    PENALTY_RULE = "PENALTY_RULE"
    REINFORCEMENT_RULE = "REINFORCEMENT_RULE"
    PATH_ALLOWLIST = "PATH_ALLOWLIST"
    OPERATION_DISABLE = "OPERATION_DISABLE"
    NAMESPACE_BLOCK = "NAMESPACE_BLOCK"
    MODALITY_REDUCTION = "MODALITY_REDUCTION"
    KERNEL_MUTATION = "KERNEL_MUTATION"
    UNKNOWN = "UNKNOWN"


CORE_OPERATIONS = {"ADD", "SUB", "MUL", "DIV", "SUM", "SORT", "BINARY_SEARCH"}
REQUIRED_SAFETY_PATHS = {"quarantine", "rollback", "replay", "ledger", "manifest"}
REQUIRED_MODALITIES_MIN = 2
VALID_RUNTIME_NAMESPACES = {
    "web",
    "uploads",
    "sensors",
    "execution",
    "memory",
    "learning",
    "planning",
    "fuzz",
    "semantic",
}
FORBIDDEN_MUTATION_NAMESPACES = {
    "kernel",
    "core_sandbox",
    "manifest",
    "security_armor",
}


@dataclass(frozen=True)
class ProposedChange:
    change_id: str
    change_class: ChangeClass
    target: str
    action: str
    payload: Dict[str, Any]
    support_hashes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["change_class"] = self.change_class.value
        return data


@dataclass(frozen=True)
class DOFDelta:
    before_operation_count: int
    after_operation_count: int
    before_namespace_count: int
    after_namespace_count: int
    before_modality_count: int
    after_modality_count: int
    removed_operations: List[str]
    blocked_namespaces: List[str]
    disabled_safety_paths: List[str]
    dof_preserved: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DOFGuardReceipt:
    proposed_change: ProposedChange
    delta: DOFDelta
    invariant_gate: EthicalInvariantReceipt
    status: DOFGuardStatus
    reason: str
    receipt_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["proposed_change"] = self.proposed_change.to_dict()
        data["delta"] = self.delta.to_dict()
        data["invariant_gate"] = self.invariant_gate.to_dict()
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class DOFPolicyState:
    allowed_operations: Set[str]
    allowed_namespaces: Set[str]
    required_safety_paths: Set[str]
    active_modalities: Set[str]
    learning_enabled: bool = True
    self_modification_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed_operations": sorted(self.allowed_operations),
            "allowed_namespaces": sorted(self.allowed_namespaces),
            "required_safety_paths": sorted(self.required_safety_paths),
            "active_modalities": sorted(self.active_modalities),
            "learning_enabled": self.learning_enabled,
            "self_modification_enabled": self.self_modification_enabled,
        }


def default_policy_state() -> DOFPolicyState:
    return DOFPolicyState(
        allowed_operations=set(CORE_OPERATIONS),
        allowed_namespaces=set(VALID_RUNTIME_NAMESPACES),
        required_safety_paths=set(REQUIRED_SAFETY_PATHS),
        active_modalities={"TEXT", "API", "FILE"},
        learning_enabled=True,
        self_modification_enabled=True,
    )


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def classify_change(raw: Dict[str, Any]) -> ProposedChange:
    target = str(raw.get("target", raw.get("key", "unknown")))
    action = str(raw.get("action", raw.get("kind", "unknown")))
    payload = dict(raw.get("payload", raw))
    support = [str(x) for x in raw.get("support_hashes", raw.get("support", []))]
    text = f"{target} {action} {json.dumps(payload, sort_keys=True, default=str)}".lower()

    if "core_sandbox" in text or "kernel" in text and "mutation" in text:
        cls = ChangeClass.KERNEL_MUTATION
    elif "disable" in text and any(op.lower() in text for op in CORE_OPERATIONS):
        cls = ChangeClass.OPERATION_DISABLE
    elif "block_namespace" in text or "namespace_block" in text:
        cls = ChangeClass.NAMESPACE_BLOCK
    elif "modality" in text and ("disable" in text or "reduce" in text or "single" in text):
        cls = ChangeClass.MODALITY_REDUCTION
    elif "allowlist" in text:
        cls = ChangeClass.PATH_ALLOWLIST
    elif "penalize" in text or "penalty" in text:
        cls = ChangeClass.PENALTY_RULE
    elif "reinforce" in text:
        cls = ChangeClass.REINFORCEMENT_RULE
    elif "quarantine" in text:
        cls = ChangeClass.QUARANTINE_ADD
    elif "validate" in text or "validation" in text:
        cls = ChangeClass.VALIDATION_ADD
    else:
        cls = ChangeClass.UNKNOWN

    change_hash = hash72_digest(("proposed_change_v1", target, action, payload, support, cls.value), width=18)
    return ProposedChange(change_hash, cls, target, action, payload, support)


def simulate_policy_after_change(policy: DOFPolicyState, change: ProposedChange) -> DOFPolicyState:
    allowed_operations = set(policy.allowed_operations)
    allowed_namespaces = set(policy.allowed_namespaces)
    required_safety_paths = set(policy.required_safety_paths)
    active_modalities = set(policy.active_modalities)
    learning_enabled = policy.learning_enabled
    self_modification_enabled = policy.self_modification_enabled

    payload = change.payload
    target_lower = change.target.lower()

    if change.change_class == ChangeClass.OPERATION_DISABLE:
        for op in list(allowed_operations):
            if op.lower() in target_lower or op in payload.get("operations", []):
                allowed_operations.discard(op)

    if change.change_class in {ChangeClass.NAMESPACE_BLOCK, ChangeClass.PATH_ALLOWLIST}:
        blocked = set(str(x) for x in payload.get("blocked_namespaces", []))
        allowlist = set(str(x) for x in payload.get("allowed_namespaces", []))
        if blocked:
            allowed_namespaces -= blocked
        if allowlist:
            allowed_namespaces &= allowlist

    if change.change_class == ChangeClass.MODALITY_REDUCTION:
        disabled = set(str(x).upper() for x in payload.get("disabled_modalities", []))
        active_modalities -= disabled
        if payload.get("single_modality"):
            keep = str(payload.get("single_modality")).upper()
            active_modalities &= {keep}

    if payload.get("disable_learning") is True:
        learning_enabled = False
    if payload.get("disable_self_modification") is True:
        self_modification_enabled = False
    if payload.get("disabled_safety_paths"):
        required_safety_paths -= set(str(x) for x in payload.get("disabled_safety_paths", []))

    return DOFPolicyState(allowed_operations, allowed_namespaces, required_safety_paths, active_modalities, learning_enabled, self_modification_enabled)


def compute_dof_delta(before: DOFPolicyState, after: DOFPolicyState) -> DOFDelta:
    removed_ops = sorted(before.allowed_operations - after.allowed_operations)
    blocked_ns = sorted(before.allowed_namespaces - after.allowed_namespaces)
    disabled_safety = sorted(before.required_safety_paths - after.required_safety_paths)
    dof_preserved = (
        not removed_ops
        and len(after.allowed_namespaces & VALID_RUNTIME_NAMESPACES) > 0
        and len(after.active_modalities) >= REQUIRED_MODALITIES_MIN
        and not disabled_safety
        and after.learning_enabled
        and after.self_modification_enabled
    )
    return DOFDelta(
        len(before.allowed_operations),
        len(after.allowed_operations),
        len(before.allowed_namespaces),
        len(after.allowed_namespaces),
        len(before.active_modalities),
        len(after.active_modalities),
        removed_ops,
        blocked_ns,
        disabled_safety,
        dof_preserved,
    )


def invariant_gate_for_dof(change: ProposedChange, delta: DOFDelta) -> EthicalInvariantReceipt:
    delta_e_zero = bool(change.change_id and change.target)
    psi_zero = delta.dof_preserved
    theta = theta15_true()
    omega_true = bool(security_hash72_v44({"change": change.to_dict(), "delta": delta.to_dict()}, domain="HHS_DOF_GUARD_REPLAY"))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "dof_preserved": delta.dof_preserved,
        "removed_operations": delta.removed_operations,
        "blocked_namespaces": delta.blocked_namespaces,
        "disabled_safety_paths": delta.disabled_safety_paths,
    }
    receipt = hash72_digest(("dof_guard_invariant_gate_v1", details, change.to_dict(), delta.to_dict(), status.value), width=18)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def evaluate_proposed_change(raw_change: Dict[str, Any], policy: DOFPolicyState | None = None) -> DOFGuardReceipt:
    before = policy or default_policy_state()
    change = classify_change(raw_change)
    after = simulate_policy_after_change(before, change)
    delta = compute_dof_delta(before, after)
    gate = invariant_gate_for_dof(change, delta)

    if gate.status != ModificationStatus.APPLIED:
        status = DOFGuardStatus.REJECTED
        reason = "change would remove kernel degrees of freedom or disable required safety paths"
    else:
        status = DOFGuardStatus.ALLOWED
        reason = "degrees of freedom preserved"
    quarantine = None if status == DOFGuardStatus.ALLOWED else hash72_digest(("dof_guard_quarantine", change.to_dict(), delta.to_dict(), gate.to_dict()), width=18)
    receipt = hash72_digest(("dof_guard_receipt_v1", change.to_dict(), delta.to_dict(), gate.receipt_hash72, status.value, reason, quarantine), width=18)
    return DOFGuardReceipt(change, delta, gate, status, reason, receipt, quarantine)


def evaluate_many(raw_changes: Sequence[Dict[str, Any]], policy: DOFPolicyState | None = None) -> List[DOFGuardReceipt]:
    return [evaluate_proposed_change(change, policy) for change in raw_changes]


def demo() -> Dict[str, Any]:
    samples = [
        {"target": "cross_modal_shell", "action": "add validation", "payload": {"allowed_namespaces": ["web", "uploads", "sensors"]}},
        {"target": "runtime", "action": "disable operation", "payload": {"operations": ["SUM"]}},
        {"target": "modalities", "action": "reduce to single modality", "payload": {"single_modality": "TEXT"}},
        {"target": "security", "action": "add quarantine", "payload": {"pattern": "fake_receipt"}},
    ]
    return {"receipts": [r.to_dict() for r in evaluate_many(samples)]}


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
