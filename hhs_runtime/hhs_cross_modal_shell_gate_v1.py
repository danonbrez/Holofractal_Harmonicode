"""
HHS Cross-Modal Shell Gate v1
=============================

Web/security shell rule:

    No state change is allowed unless mandatory high-priority HARMONICODE
    witnesses agree in both canonical next-state hash and phase commitment.

Mandatory high-priority witnesses:

    AUDIO
    HARMONICODE
    XYZW
    HASH72

Lower-priority witnesses such as TEXT, LANGUAGE, CODE, FILE, API, SENSOR,
IMAGE, VIDEO, DATABASE, and INTERNAL may support the transition, but they cannot
commit state without the mandatory harmonic witnesses.

Pipeline:

    external modality input
    -> modality projection
    -> kernel-normalized proposed_next_state
    -> QGU temporal admissibility witness
    -> Hash72 next_state commitment
    -> harmonic phase commitment
    -> mandatory witness presence check
    -> weighted quorum check
    -> cross-modal next-state equality check
    -> phase equality check
    -> state commit OR quarantine

The shell never mutates state directly. It only calls HHSStateLayerV1 after the
modality floor, mandatory witness set, weighted quorum, temporal admissibility,
canonical next-state consensus, and phase consensus all pass.
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
MODALITY_WEIGHTS = {
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
REQUIRED_WEIGHTED_QUORUM = sum(MODALITY_WEIGHTS[m] for m in MANDATORY_HIGH_PRIORITY_WITNESSES)


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
class ModalityProjection:
    modality: ModalityKind
    source_id: str
    proposed_patch: Dict[str, Any]
    normalized_next_state: Dict[str, Any]
    next_state_hash72: str
    phase_hash72: str
    temporal_status: str
    temporal_receipt_hash72: str
    weight: int
    projection_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["modality"] = self.modality.value
        return data


@dataclass(frozen=True)
class CrossModalConsensusReceipt:
    projections: List[ModalityProjection]
    agreed_next_state_hash72: str | None
    agreed_phase_hash72: str | None
    distinct_modality_count: int
    min_distinct_modalities: int
    modality_floor_ok: bool
    mandatory_witnesses_present: bool
    missing_mandatory_witnesses: List[str]
    weighted_quorum: int
    required_weighted_quorum: int
    weighted_quorum_ok: bool
    temporal_ok: bool
    phase_consensus_ok: bool
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
            "agreed_phase_hash72": self.agreed_phase_hash72,
            "distinct_modality_count": self.distinct_modality_count,
            "min_distinct_modalities": self.min_distinct_modalities,
            "modality_floor_ok": self.modality_floor_ok,
            "mandatory_witnesses_present": self.mandatory_witnesses_present,
            "missing_mandatory_witnesses": self.missing_mandatory_witnesses,
            "weighted_quorum": self.weighted_quorum,
            "required_weighted_quorum": self.required_weighted_quorum,
            "weighted_quorum_ok": self.weighted_quorum_ok,
            "temporal_ok": self.temporal_ok,
            "phase_consensus_ok": self.phase_consensus_ok,
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
    return security_hash72_v44(
        {"next_state_hash72": next_state_hash72, "normalized_next_state": normalized_next_state},
        domain="HHS_SHELL_HARMONICODE_PHASE",
    )


def project_modality_to_next_state(
    *,
    modality: ModalityKind,
    source_id: str,
    proposed_patch: Dict[str, Any],
    current_state: Dict[str, Any],
    phase_hash72: str | None = None,
) -> ModalityProjection:
    normalized_patch = canonicalize_for_hash72(proposed_patch)
    normalized_next_state = apply_patch_to_snapshot(current_state, normalized_patch)
    state_only_hash = security_hash72_v44(normalized_next_state, domain="HHS_SHELL_NEXT_STATE_CANON")
    phase_hash = harmonic_phase_hash(state_only_hash, normalized_next_state, phase_hash72)
    temporal = evaluate_temporal_admissibility(
        {"modality": modality.value, "source_id": source_id, "next_state_hash72": state_only_hash, "phase_hash72": phase_hash}
    )
    projection_hash = security_hash72_v44(
        {
            "modality": modality.value,
            "source_id": source_id,
            "patch_hash72": canonical_patch_hash(normalized_patch),
            "state_only_hash72": state_only_hash,
            "phase_hash72": phase_hash,
            "temporal_receipt_hash72": temporal.receipt_hash72,
            "weight": MODALITY_WEIGHTS.get(modality.value, 1),
        },
        domain="HHS_SHELL_MODALITY_PROJECTION",
    )
    return ModalityProjection(
        modality=modality,
        source_id=source_id,
        proposed_patch=normalized_patch,
        normalized_next_state=normalized_next_state,
        next_state_hash72=state_only_hash,
        phase_hash72=phase_hash,
        temporal_status=temporal.status.value,
        temporal_receipt_hash72=temporal.receipt_hash72,
        weight=MODALITY_WEIGHTS.get(modality.value, 1),
        projection_hash72=projection_hash,
    )


def _consensus_reason(
    *,
    modality_floor_ok: bool,
    mandatory_witnesses_present: bool,
    weighted_quorum_ok: bool,
    temporal_ok: bool,
    state_consensus_ok: bool,
    phase_consensus_ok: bool,
    armor_ok: bool,
) -> str:
    if not modality_floor_ok:
        return "distinct modality floor not satisfied"
    if not mandatory_witnesses_present:
        return "mandatory high-priority HARMONICODE witnesses missing"
    if not weighted_quorum_ok:
        return "weighted modality quorum not satisfied"
    if not temporal_ok:
        return "one or more modality witnesses failed QGU temporal admissibility"
    if not state_consensus_ok:
        return "cross-modal next-state disagreement"
    if not phase_consensus_ok:
        return "HARMONICODE phase disagreement"
    if not armor_ok:
        return "security armor rejected consensus envelope"
    return "mandatory HARMONICODE witnesses agree in state and phase"


def cross_modal_consensus(projections: Sequence[ModalityProjection]) -> CrossModalConsensusReceipt:
    hashes = [p.next_state_hash72 for p in projections]
    unique_hashes = set(hashes)
    agreed = hashes[0] if hashes and len(unique_hashes) == 1 else None
    phase_hashes = [p.phase_hash72 for p in projections]
    unique_phase_hashes = set(phase_hashes)
    agreed_phase = phase_hashes[0] if phase_hashes and len(unique_phase_hashes) == 1 else None

    distinct_modalities = {p.modality.value for p in projections}
    distinct_modality_count = len(distinct_modalities)
    modality_floor_ok = distinct_modality_count >= MIN_DISTINCT_MODALITIES
    missing_mandatory = sorted(MANDATORY_HIGH_PRIORITY_WITNESSES - distinct_modalities)
    mandatory_present = not missing_mandatory
    weighted_quorum = sum(p.weight for p in projections if p.next_state_hash72 == agreed and p.phase_hash72 == agreed_phase)
    weighted_quorum_ok = weighted_quorum >= REQUIRED_WEIGHTED_QUORUM
    temporal_ok = all(p.temporal_status == TemporalGuardStatus.ADMISSIBLE.value for p in projections)
    state_consensus_ok = agreed is not None
    phase_consensus_ok = agreed_phase is not None

    delta_e_zero = len(projections) > 0 and all(p.proposed_patch for p in projections)
    psi_zero = state_consensus_ok and phase_consensus_ok and mandatory_present and weighted_quorum_ok
    theta = theta15_true()
    omega_true = modality_floor_ok and temporal_ok and psi_zero and all(p.normalized_next_state for p in projections)
    armor = armor_guard(
        {
            "projection_hashes": [p.projection_hash72 for p in projections],
            "agreed_next_state_hash72": agreed,
            "agreed_phase_hash72": agreed_phase,
            "distinct_modalities": sorted(distinct_modalities),
            "mandatory_witnesses": sorted(MANDATORY_HIGH_PRIORITY_WITNESSES),
            "missing_mandatory_witnesses": missing_mandatory,
            "weighted_quorum": weighted_quorum,
            "required_weighted_quorum": REQUIRED_WEIGHTED_QUORUM,
        }
    )
    armor_ok = armor.status == ArmorStatus.VALID
    ok = delta_e_zero and psi_zero and theta and omega_true and armor_ok
    status = ShellGateStatus.COMMITTED if ok else ShellGateStatus.QUARANTINED
    reason = _consensus_reason(
        modality_floor_ok=modality_floor_ok,
        mandatory_witnesses_present=mandatory_present,
        weighted_quorum_ok=weighted_quorum_ok,
        temporal_ok=temporal_ok,
        state_consensus_ok=state_consensus_ok,
        phase_consensus_ok=phase_consensus_ok,
        armor_ok=armor_ok,
    )

    quarantine = None if ok else security_hash72_v44(
        {
            "reason": reason,
            "projection_hashes": [p.projection_hash72 for p in projections],
            "next_state_hashes": hashes,
            "phase_hashes": phase_hashes,
            "distinct_modalities": sorted(distinct_modalities),
            "missing_mandatory_witnesses": missing_mandatory,
            "weighted_quorum": weighted_quorum,
            "required_weighted_quorum": REQUIRED_WEIGHTED_QUORUM,
        },
        domain="HHS_SHELL_CROSS_MODAL_QUARANTINE",
    )
    receipt = security_hash72_v44(
        {
            "projection_hashes": [p.projection_hash72 for p in projections],
            "agreed_next_state_hash72": agreed,
            "agreed_phase_hash72": agreed_phase,
            "distinct_modality_count": distinct_modality_count,
            "min_distinct_modalities": MIN_DISTINCT_MODALITIES,
            "modality_floor_ok": modality_floor_ok,
            "mandatory_witnesses_present": mandatory_present,
            "missing_mandatory_witnesses": missing_mandatory,
            "weighted_quorum": weighted_quorum,
            "required_weighted_quorum": REQUIRED_WEIGHTED_QUORUM,
            "weighted_quorum_ok": weighted_quorum_ok,
            "temporal_ok": temporal_ok,
            "phase_consensus_ok": phase_consensus_ok,
            "delta_e_zero": delta_e_zero,
            "psi_zero": psi_zero,
            "theta15_true": theta,
            "omega_true": omega_true,
            "armor_ok": armor_ok,
            "status": status.value,
            "quarantine": quarantine,
        },
        domain="HHS_SHELL_CROSS_MODAL_CONSENSUS",
    )
    return CrossModalConsensusReceipt(
        list(projections),
        agreed,
        agreed_phase,
        distinct_modality_count,
        MIN_DISTINCT_MODALITIES,
        modality_floor_ok,
        mandatory_present,
        missing_mandatory,
        weighted_quorum,
        REQUIRED_WEIGHTED_QUORUM,
        weighted_quorum_ok,
        temporal_ok,
        phase_consensus_ok,
        delta_e_zero,
        psi_zero,
        theta,
        omega_true,
        armor_ok,
        status,
        receipt,
        quarantine,
        reason,
    )


class CrossModalShellGateV1:
    def __init__(self, *, state_layer: HHSStateLayerV1 | None = None, ledger_path: str | Path = "demo_reports/hhs_cross_modal_shell_gate_ledger_v1.json") -> None:
        self.state_layer = state_layer or HHSStateLayerV1()
        self.ledger_path = Path(ledger_path)

    def propose_and_commit(self, modality_patches: Sequence[Dict[str, Any]]) -> ShellCommitReceipt:
        current_state = self.state_layer.snapshot()["state"]
        projections: List[ModalityProjection] = []
        for idx, item in enumerate(modality_patches):
            modality = ModalityKind(str(item.get("modality", ModalityKind.INTERNAL.value)))
            source_id = str(item.get("source_id", f"source_{idx}"))
            patch = dict(item.get("patch", {}))
            projections.append(
                project_modality_to_next_state(
                    modality=modality,
                    source_id=source_id,
                    proposed_patch=patch,
                    current_state=current_state,
                    phase_hash72=item.get("phase_hash72"),
                )
            )

        consensus = cross_modal_consensus(projections)
        state_result = None
        if consensus.status == ShellGateStatus.COMMITTED and projections:
            patch = projections[0].proposed_patch
            state_result = self.state_layer.apply_patch(
                StatePatch(
                    op=str(patch.get("op", "SET")),
                    path=str(patch.get("path", ".")),
                    value=patch.get("value"),
                    metadata={"source": "cross_modal_shell_gate", "consensus_hash72": consensus.receipt_hash72},
                )
            )
            if not state_result.get("ok"):
                consensus = CrossModalConsensusReceipt(
                    consensus.projections,
                    consensus.agreed_next_state_hash72,
                    consensus.agreed_phase_hash72,
                    consensus.distinct_modality_count,
                    consensus.min_distinct_modalities,
                    consensus.modality_floor_ok,
                    consensus.mandatory_witnesses_present,
                    consensus.missing_mandatory_witnesses,
                    consensus.weighted_quorum,
                    consensus.required_weighted_quorum,
                    consensus.weighted_quorum_ok,
                    consensus.temporal_ok,
                    consensus.phase_consensus_ok,
                    consensus.delta_e_zero,
                    False,
                    consensus.theta15_true,
                    consensus.omega_true,
                    consensus.armor_ok,
                    ShellGateStatus.QUARANTINED,
                    consensus.receipt_hash72,
                    consensus.quarantine_hash72 or security_hash72_v44(state_result, domain="HHS_SHELL_STATE_COMMIT_QUARANTINE"),
                    "state layer rejected agreed transition",
                )

        ledger = MemoryLedger(self.ledger_path)
        commit = ledger.append_payloads("cross_modal_shell_commit_v1", [consensus.to_dict(), state_result or {}])
        replay = replay_ledger(self.ledger_path)
        status = consensus.status
        receipt = hash72_digest(("shell_commit_receipt_v1", consensus.receipt_hash72, state_result, commit.receipt_hash72, replay.receipt_hash72, status.value), width=18)
        return ShellCommitReceipt(consensus, state_result, commit.to_dict(), replay.to_dict(), status, receipt)


def demo() -> Dict[str, Any]:
    gate = CrossModalShellGateV1()
    patch = {"op": "SET", "path": "web.intent", "value": {"next": "state"}}
    return gate.propose_and_commit(
        [
            {"modality": "AUDIO", "source_id": "audio_phase", "patch": patch},
            {"modality": "HARMONICODE", "source_id": "harmonicode_kernel", "patch": patch},
            {"modality": "XYZW", "source_id": "xyzw_algebra", "patch": patch},
            {"modality": "HASH72", "source_id": "hash72_commitment", "patch": patch},
            {"modality": "TEXT", "source_id": "text_parser", "patch": patch},
            {"modality": "CODE", "source_id": "code_parser", "patch": patch},
        ]
    ).to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
