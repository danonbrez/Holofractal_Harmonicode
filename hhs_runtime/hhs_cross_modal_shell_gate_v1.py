"""
HHS Cross-Modal Shell Gate v1
=============================

Web/security shell rule:

    No state change is allowed unless every active modality passing through the
    kernel agrees on the exact same canonical next-state commitment.

Pipeline:

    external modality input
    -> modality projection
    -> kernel-normalized proposed_next_state
    -> Hash72 next_state commitment
    -> cross-modal equality check
    -> state commit OR quarantine

The shell never mutates state directly. It only calls HHSStateLayerV1 after all
modalities agree on the same next-state hash.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import (
    AuditedRunner,
    canonicalize_for_hash72,
    security_hash72_v44,
)
from hhs_runtime.core_sandbox.hhs_state_layer_v1 import HHSStateLayerV1, StatePatch
from hhs_runtime.core_sandbox.hhs_security_armor_v1 import armor_guard, ArmorStatus
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger


class ModalityKind(str, Enum):
    TEXT = "TEXT"
    FILE = "FILE"
    API = "API"
    SENSOR = "SENSOR"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    DATABASE = "DATABASE"
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
    projection_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["modality"] = self.modality.value
        return data


@dataclass(frozen=True)
class CrossModalConsensusReceipt:
    projections: List[ModalityProjection]
    agreed_next_state_hash72: str | None
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


def project_modality_to_next_state(
    *,
    modality: ModalityKind,
    source_id: str,
    proposed_patch: Dict[str, Any],
    current_state: Dict[str, Any],
) -> ModalityProjection:
    normalized_patch = canonicalize_for_hash72(proposed_patch)
    normalized_next_state = apply_patch_to_snapshot(current_state, normalized_patch)
    next_state_hash = security_hash72_v44(
        {
            "modality": modality.value,
            "source_id": source_id,
            "next_state": normalized_next_state,
        },
        domain="HHS_SHELL_MODALITY_NEXT_STATE",
    )
    # Agreement must be over state alone, not modality label. So also compute a
    # modality-independent state commitment and use it as the consensus target.
    state_only_hash = security_hash72_v44(normalized_next_state, domain="HHS_SHELL_NEXT_STATE_CANON")
    projection_hash = security_hash72_v44(
        {
            "modality": modality.value,
            "source_id": source_id,
            "patch_hash72": canonical_patch_hash(normalized_patch),
            "state_only_hash72": state_only_hash,
            "next_state_hash72": next_state_hash,
        },
        domain="HHS_SHELL_MODALITY_PROJECTION",
    )
    return ModalityProjection(
        modality=modality,
        source_id=source_id,
        proposed_patch=normalized_patch,
        normalized_next_state=normalized_next_state,
        next_state_hash72=state_only_hash,
        projection_hash72=projection_hash,
    )


def cross_modal_consensus(projections: Sequence[ModalityProjection]) -> CrossModalConsensusReceipt:
    hashes = [p.next_state_hash72 for p in projections]
    unique_hashes = set(hashes)
    agreed = hashes[0] if hashes and len(unique_hashes) == 1 else None
    delta_e_zero = len(projections) > 0 and all(p.proposed_patch for p in projections)
    psi_zero = agreed is not None
    theta = theta15_true()
    omega_true = agreed is not None and all(p.normalized_next_state for p in projections)
    armor = armor_guard({"projection_hashes": [p.projection_hash72 for p in projections], "agreed_next_state_hash72": agreed})
    armor_ok = armor.status == ArmorStatus.VALID
    ok = delta_e_zero and psi_zero and theta and omega_true and armor_ok
    status = ShellGateStatus.COMMITTED if ok else ShellGateStatus.QUARANTINED
    reason = "all modalities agree on canonical next state" if ok else "cross-modal next-state disagreement or invariant failure"
    quarantine = None if ok else security_hash72_v44(
        {
            "reason": reason,
            "projection_hashes": [p.projection_hash72 for p in projections],
            "next_state_hashes": hashes,
        },
        domain="HHS_SHELL_CROSS_MODAL_QUARANTINE",
    )
    receipt = security_hash72_v44(
        {
            "projection_hashes": [p.projection_hash72 for p in projections],
            "agreed_next_state_hash72": agreed,
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
        list(projections), agreed, delta_e_zero, psi_zero, theta, omega_true, armor_ok, status, receipt, quarantine, reason
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
                )
            )
        consensus = cross_modal_consensus(projections)
        state_result = None
        if consensus.status == ShellGateStatus.COMMITTED and projections:
            # Since all next states agree, committing the first patch reaches the agreed state.
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
    return gate.propose_and_commit([
        {"modality": "TEXT", "source_id": "text_parser", "patch": patch},
        {"modality": "API", "source_id": "api_schema", "patch": patch},
        {"modality": "FILE", "source_id": "file_tokenizer", "patch": patch},
    ]).to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
