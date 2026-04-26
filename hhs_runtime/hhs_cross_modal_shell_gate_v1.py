"""
HHS Cross-Modal Shell Gate v1
=============================

State mutation now requires mandatory high-priority HARMONICODE witnesses to
agree across state, time, phase, and trust-weighted modality consensus.

Mandatory high-priority witnesses:
    AUDIO, HARMONICODE, XYZW, HASH72

Low-priority witnesses such as TEXT, LANGUAGE, CODE, FILE, API, SENSOR, IMAGE,
VIDEO, DATABASE, and INTERNAL may support the transition, but cannot override
mandatory harmonic witnesses.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import canonicalize_for_hash72, security_hash72_v44
from hhs_runtime.core_sandbox.hhs_state_layer_v1 import HHSStateLayerV1, StatePatch
from hhs_runtime.core_sandbox.hhs_security_armor_v1 import ArmorStatus, armor_guard
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_qgu_temporal_phase_guard_v1 import TemporalGuardStatus, evaluate_temporal_admissibility

MIN_DISTINCT_MODALITIES = 2
MANDATORY_HIGH_PRIORITY_WITNESSES = {"AUDIO", "HARMONICODE", "XYZW", "HASH72"}
PHASE_RING = 72
MANDATORY_PHASE_TOLERANCE = 0
SUPPORT_PHASE_TOLERANCE = 1

BASE_MODALITY_WEIGHTS = {
    "HARMONICODE": 12,
    "XYZW": 12,
    "HASH72": 12,
    "AUDIO": 10,
    "VIDEO": 5,
    "SENSOR": 4,
    "API": 3,
    "FILE": 3,
    "DATABASE": 3,
    "CODE": 2,
    "LANGUAGE": 1,
    "TEXT": 1,
    "IMAGE": 1,
    "INTERNAL": 1,
}
REQUIRED_WEIGHTED_QUORUM = sum(BASE_MODALITY_WEIGHTS[m] for m in MANDATORY_HIGH_PRIORITY_WITNESSES)


class ModalityKind(str, Enum):
    TEXT = "TEXT"
    LANGUAGE = "LANGUAGE"
    CODE = "CODE"
    FILE = "FILE"
    API = "API"
    SENSOR = "SENSOR"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    DATABASE = "DATABASE"
    HARMONICODE = "HARMONICODE"
    XYZW = "XYZW"
    HASH72 = "HASH72"
    INTERNAL = "INTERNAL"


class ShellGateStatus(str, Enum):
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"
    STALLED = "STALLED"


@dataclass(frozen=True)
class AdaptiveTrustProfile:
    modality_scores: Dict[str, int]
    profile_hash72: str

    def effective_weight(self, modality: str) -> int:
        base = BASE_MODALITY_WEIGHTS.get(modality, 1)
        bonus = max(-base + 1, min(base, int(self.modality_scores.get(modality, 0))))
        return base + bonus

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ModalityProjection:
    modality: ModalityKind
    source_id: str
    proposed_patch: Dict[str, Any]
    normalized_next_state: Dict[str, Any]
    next_state_hash72: str
    phase_hash72: str
    phase_index: int
    temporal_status: str
    temporal_receipt_hash72: str
    base_weight: int
    effective_weight: int
    projection_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["modality"] = self.modality.value
        return data


@dataclass(frozen=True)
class CrossModalConsensusReceipt:
    projections: List[ModalityProjection]
    agreed_next_state_hash72: str | None
    anchor_phase_index: int | None
    phase_max_distance: int | None
    distinct_modality_count: int
    min_distinct_modalities: int
    modality_floor_ok: bool
    mandatory_witnesses_present: bool
    missing_mandatory_witnesses: List[str]
    mandatory_phase_ok: bool
    support_phase_ok: bool
    weighted_quorum: int
    required_weighted_quorum: int
    weighted_quorum_ok: bool
    temporal_ok: bool
    phase_consensus_ok: bool
    adaptive_trust_profile: AdaptiveTrustProfile
    delta_e_zero: bool
    psi_zero: bool
    theta15_true: bool
    omega_true: bool
    armor_ok: bool
    status: ShellGateStatus
    receipt_hash72: str
    quarantine_hash72: str | None
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projections": [p.to_dict() for p in self.projections],
            "agreed_next_state_hash72": self.agreed_next_state_hash72,
            "anchor_phase_index": self.anchor_phase_index,
            "phase_max_distance": self.phase_max_distance,
            "distinct_modality_count": self.distinct_modality_count,
            "min_distinct_modalities": self.min_distinct_modalities,
            "modality_floor_ok": self.modality_floor_ok,
            "mandatory_witnesses_present": self.mandatory_witnesses_present,
            "missing_mandatory_witnesses": self.missing_mandatory_witnesses,
            "mandatory_phase_ok": self.mandatory_phase_ok,
            "support_phase_ok": self.support_phase_ok,
            "weighted_quorum": self.weighted_quorum,
            "required_weighted_quorum": self.required_weighted_quorum,
            "weighted_quorum_ok": self.weighted_quorum_ok,
            "temporal_ok": self.temporal_ok,
            "phase_consensus_ok": self.phase_consensus_ok,
            "adaptive_trust_profile": self.adaptive_trust_profile.to_dict(),
            "delta_e_zero": self.delta_e_zero,
            "psi_zero": self.psi_zero,
            "theta15_true": self.theta15_true,
            "omega_true": self.omega_true,
            "armor_ok": self.armor_ok,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
            "quarantine_hash72": self.quarantine_hash72,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ShellCommitReceipt:
    consensus: CrossModalConsensusReceipt
    state_result: Dict[str, Any] | None
    ledger_commit_receipt: Dict[str, Any]
    replay_receipt: Dict[str, Any]
    status: ShellGateStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consensus": self.consensus.to_dict(),
            "state_result": self.state_result,
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def canonical_patch_hash(patch: Dict[str, Any]) -> str:
    return security_hash72_v44(canonicalize_for_hash72(patch), domain="HHS_SHELL_PATCH")


def phase_index_from_hash(phase_hash72: str) -> int:
    acc = 0
    for ch in phase_hash72:
        acc = (acc * 131 + ord(ch)) % PHASE_RING
    return acc


def phase_distance(a: int, b: int) -> int:
    delta = abs((a - b) % PHASE_RING)
    return min(delta, PHASE_RING - delta)


def trust_profile_from_history(history: Sequence[Dict[str, Any]] | None = None) -> AdaptiveTrustProfile:
    scores = {k: 0 for k in BASE_MODALITY_WEIGHTS}
    for item in history or []:
        modality = str(item.get("modality", "")).upper()
        if modality not in scores:
            continue
        if item.get("replay_valid") is True and item.get("phase_valid") is True:
            scores[modality] += 1
        if item.get("replay_valid") is False or item.get("phase_valid") is False or item.get("quarantined") is True:
            scores[modality] -= 2
    h = security_hash72_v44(scores, domain="HHS_ADAPTIVE_MODALITY_TRUST_PROFILE")
    return AdaptiveTrustProfile(scores, h)


def apply_patch_to_snapshot(snapshot_state: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    temp = HHSStateLayerV1(initial_state=snapshot_state)
    next_state = temp.apply_patch_to_copy(
        StatePatch(
            op=str(patch.get("op", "SET")),
            path=str(patch.get("path", ".")),
            value=patch.get("value"),
            metadata=dict(patch.get("metadata", {})),
        )
    )
    return canonicalize_for_hash72(next_state)


def harmonic_phase_hash(next_state_hash72: str, normalized_next_state: Dict[str, Any], override_phase_hash72: str | None = None) -> str:
    if override_phase_hash72:
        return override_phase_hash72
    return security_hash72_v44({"next_state_hash72": next_state_hash72, "normalized_next_state": normalized_next_state}, domain="HHS_SHELL_HARMONICODE_PHASE")


def project_modality_to_next_state(
    *,
    modality: ModalityKind,
    source_id: str,
    proposed_patch: Dict[str, Any],
    current_state: Dict[str, Any],
    trust_profile: AdaptiveTrustProfile,
    phase_hash72: str | None = None,
) -> ModalityProjection:
    normalized_patch = canonicalize_for_hash72(proposed_patch)
    normalized_next_state = apply_patch_to_snapshot(current_state, normalized_patch)
    state_only_hash = security_hash72_v44(normalized_next_state, domain="HHS_SHELL_NEXT_STATE_CANON")
    phase_hash = harmonic_phase_hash(state_only_hash, normalized_next_state, phase_hash72)
    phase_index = phase_index_from_hash(phase_hash)
    temporal = evaluate_temporal_admissibility({"modality": modality.value, "source_id": source_id, "next_state_hash72": state_only_hash, "phase_hash72": phase_hash})
    base_weight = BASE_MODALITY_WEIGHTS.get(modality.value, 1)
    effective_weight = trust_profile.effective_weight(modality.value)
    projection_hash = security_hash72_v44(
        {
            "modality": modality.value,
            "source_id": source_id,
            "patch_hash72": canonical_patch_hash(normalized_patch),
            "state_only_hash72": state_only_hash,
            "phase_hash72": phase_hash,
            "phase_index": phase_index,
            "temporal_receipt_hash72": temporal.receipt_hash72,
            "base_weight": base_weight,
            "effective_weight": effective_weight,
            "trust_profile_hash72": trust_profile.profile_hash72,
        },
        domain="HHS_SHELL_MODALITY_PROJECTION",
    )
    return ModalityProjection(modality, source_id, normalized_patch, normalized_next_state, state_only_hash, phase_hash, phase_index, temporal.status.value, temporal.receipt_hash72, base_weight, effective_weight, projection_hash)


def cross_modal_consensus(projections: Sequence[ModalityProjection], trust_profile: AdaptiveTrustProfile | None = None) -> CrossModalConsensusReceipt:
    profile = trust_profile or trust_profile_from_history()
    hashes = [p.next_state_hash72 for p in projections]
    unique_hashes = set(hashes)
    agreed = hashes[0] if hashes and len(unique_hashes) == 1 else None
    mandatory = [p for p in projections if p.modality.value in MANDATORY_HIGH_PRIORITY_WITNESSES]
    anchor = next((p.phase_index for p in mandatory if p.modality.value == "HARMONICODE"), None)
    if anchor is None and mandatory:
        anchor = mandatory[0].phase_index
    all_distances = [phase_distance(anchor, p.phase_index) for p in projections] if anchor is not None else []
    mandatory_distances = [phase_distance(anchor, p.phase_index) for p in mandatory] if anchor is not None else []
    phase_max_distance = max(all_distances) if all_distances else None

    distinct_modalities = {p.modality.value for p in projections}
    missing_mandatory = sorted(MANDATORY_HIGH_PRIORITY_WITNESSES - distinct_modalities)
    mandatory_present = not missing_mandatory
    modality_floor_ok = len(distinct_modalities) >= MIN_DISTINCT_MODALITIES
    mandatory_phase_ok = mandatory_present and bool(mandatory_distances) and max(mandatory_distances) <= MANDATORY_PHASE_TOLERANCE
    support_phase_ok = bool(all_distances) and max(all_distances) <= SUPPORT_PHASE_TOLERANCE
    phase_consensus_ok = mandatory_phase_ok and support_phase_ok
    temporal_ok = all(p.temporal_status == TemporalGuardStatus.ADMISSIBLE.value for p in projections)
    state_consensus_ok = agreed is not None
    weighted_quorum = sum(p.effective_weight for p in projections if p.next_state_hash72 == agreed and (anchor is not None and phase_distance(anchor, p.phase_index) <= SUPPORT_PHASE_TOLERANCE))
    weighted_quorum_ok = weighted_quorum >= REQUIRED_WEIGHTED_QUORUM
    delta_e_zero = len(projections) > 0 and all(p.proposed_patch for p in projections)
    psi_zero = state_consensus_ok and phase_consensus_ok and mandatory_present and weighted_quorum_ok
    theta = theta15_true()
    omega_true = modality_floor_ok and temporal_ok and psi_zero and all(p.normalized_next_state for p in projections)
    armor = armor_guard({"projection_hashes": [p.projection_hash72 for p in projections], "agreed_next_state_hash72": agreed, "anchor_phase_index": anchor, "phase_max_distance": phase_max_distance, "trust_profile_hash72": profile.profile_hash72})
    armor_ok = armor.status == ArmorStatus.VALID
    ok = delta_e_zero and psi_zero and theta and omega_true and armor_ok
    if ok:
        reason = "mandatory HARMONICODE witnesses agree within phase tolerance and weighted quorum"
    elif not mandatory_present:
        reason = "mandatory high-priority HARMONICODE witnesses missing"
    elif not mandatory_phase_ok:
        reason = "mandatory HARMONICODE phase disagreement"
    elif not support_phase_ok:
        reason = "support modality phase outside tolerance band"
    elif not weighted_quorum_ok:
        reason = "weighted modality quorum not satisfied"
    elif not temporal_ok:
        reason = "one or more modality witnesses failed QGU temporal admissibility"
    elif not state_consensus_ok:
        reason = "cross-modal next-state disagreement"
    else:
        reason = "security armor or invariant gate rejected consensus envelope"
    status = ShellGateStatus.COMMITTED if ok else ShellGateStatus.QUARANTINED
    quarantine = None if ok else security_hash72_v44({"reason": reason, "next_state_hashes": hashes, "phase_indices": [p.phase_index for p in projections], "missing_mandatory_witnesses": missing_mandatory, "weighted_quorum": weighted_quorum}, domain="HHS_SHELL_CROSS_MODAL_QUARANTINE")
    receipt = security_hash72_v44({"projection_hashes": [p.projection_hash72 for p in projections], "agreed_next_state_hash72": agreed, "anchor_phase_index": anchor, "phase_max_distance": phase_max_distance, "mandatory_phase_ok": mandatory_phase_ok, "support_phase_ok": support_phase_ok, "weighted_quorum": weighted_quorum, "status": status.value, "quarantine": quarantine}, domain="HHS_SHELL_CROSS_MODAL_CONSENSUS")
    return CrossModalConsensusReceipt(list(projections), agreed, None, anchor, phase_max_distance, len(distinct_modalities), MIN_DISTINCT_MODALITIES, modality_floor_ok, mandatory_present, missing_mandatory, mandatory_phase_ok, support_phase_ok, weighted_quorum, REQUIRED_WEIGHTED_QUORUM, weighted_quorum_ok, temporal_ok, phase_consensus_ok, profile, delta_e_zero, psi_zero, theta, omega_true, armor_ok, status, receipt, quarantine, reason)


class CrossModalShellGateV1:
    def __init__(self, *, state_layer: HHSStateLayerV1 | None = None, ledger_path: str | Path = "demo_reports/hhs_cross_modal_shell_gate_ledger_v1.json", trust_history: Sequence[Dict[str, Any]] | None = None) -> None:
        self.state_layer = state_layer or HHSStateLayerV1()
        self.ledger_path = Path(ledger_path)
        self.trust_profile = trust_profile_from_history(trust_history)

    def propose_and_commit(self, modality_patches: Sequence[Dict[str, Any]]) -> ShellCommitReceipt:
        current_state = self.state_layer.snapshot()["state"]
        projections: List[ModalityProjection] = []
        for idx, item in enumerate(modality_patches):
            modality = ModalityKind(str(item.get("modality", ModalityKind.INTERNAL.value)))
            projections.append(project_modality_to_next_state(modality=modality, source_id=str(item.get("source_id", f"source_{idx}")), proposed_patch=dict(item.get("patch", {})), current_state=current_state, trust_profile=self.trust_profile, phase_hash72=item.get("phase_hash72")))
        consensus = cross_modal_consensus(projections, self.trust_profile)
        state_result = None
        if consensus.status == ShellGateStatus.COMMITTED and projections:
            patch = projections[0].proposed_patch
            state_result = self.state_layer.apply_patch(StatePatch(op=str(patch.get("op", "SET")), path=str(patch.get("path", ".")), value=patch.get("value"), metadata={"source": "cross_modal_shell_gate", "consensus_hash72": consensus.receipt_hash72}))
        ledger = MemoryLedger(self.ledger_path)
        commit = ledger.append_payloads("cross_modal_shell_commit_v1", [consensus.to_dict(), state_result or {}])
        replay = replay_ledger(self.ledger_path)
        status = consensus.status
        receipt = hash72_digest(("shell_commit_receipt_v1", consensus.receipt_hash72, state_result, commit.receipt_hash72, replay.receipt_hash72, status.value), width=18)
        return ShellCommitReceipt(consensus, state_result, commit.to_dict(), replay.to_dict(), status, receipt)


def demo() -> Dict[str, Any]:
    gate = CrossModalShellGateV1()
    patch = {"op": "SET", "path": "web.intent", "value": {"next": "state"}}
    return gate.propose_and_commit([
        {"modality": "AUDIO", "patch": patch},
        {"modality": "HARMONICODE", "patch": patch},
        {"modality": "XYZW", "patch": patch},
        {"modality": "HASH72", "patch": patch},
        {"modality": "TEXT", "patch": patch},
        {"modality": "CODE", "patch": patch},
    ]).to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
