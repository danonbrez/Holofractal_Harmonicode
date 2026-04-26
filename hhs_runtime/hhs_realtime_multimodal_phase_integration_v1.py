"""
HHS Realtime Multimodal Phase Integration v1
===========================================

Live phase-witness adapter for shell and agent-loop consensus.

Purpose
-------
Convert realtime or near-realtime modality observations into deterministic
phase witnesses that can be passed into:

- hhs_cross_modal_shell_gate_v1
- hhs_phase_coherent_operator_loop_v1

Mandatory high-priority witnesses:
    AUDIO
    HARMONICODE
    XYZW
    HASH72

This module does not perform device capture. It accepts already-captured frames,
feature packets, algebra snapshots, or commitment records and turns them into
bounded, replayable Hash72 phase witnesses.

Pipeline
--------
    observation packets
    -> canonical observation hash
    -> modality-specific witness
    -> QGU temporal window check
    -> shared phase anchor
    -> shell-ready modality patch list
    -> append-only ledger + replay receipt

No raw signal can mutate state. Only phase-locked witness packets are emitted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import canonicalize_for_hash72, security_hash72_v44
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_qgu_temporal_phase_guard_v1 import (
    TemporalGuardStatus,
    make_temporal_window,
    evaluate_temporal_admissibility,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


PHASE_RING = 72
MANDATORY_WITNESS_MODALITIES = ("AUDIO", "HARMONICODE", "XYZW", "HASH72")


class LiveWitnessStatus(str, Enum):
    LOCKED = "LOCKED"
    QUARANTINED = "QUARANTINED"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class LiveModalityObservation:
    modality: str
    source_id: str
    payload: Dict[str, Any]
    observed_at_ns: int | None
    observation_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LivePhaseWitness:
    observation: LiveModalityObservation
    phase_index: int
    phase_hash72: str
    temporal_status: str
    temporal_receipt_hash72: str
    witness_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation": self.observation.to_dict(),
            "phase_index": self.phase_index,
            "phase_hash72": self.phase_hash72,
            "temporal_status": self.temporal_status,
            "temporal_receipt_hash72": self.temporal_receipt_hash72,
            "witness_hash72": self.witness_hash72,
        }


@dataclass(frozen=True)
class MultimodalPhaseLockReceipt:
    witnesses: List[LivePhaseWitness]
    anchor_phase_hash72: str | None
    anchor_phase_index: int | None
    mandatory_present: bool
    missing_mandatory: List[str]
    temporal_ok: bool
    phase_locked: bool
    invariant_gate: EthicalInvariantReceipt
    status: LiveWitnessStatus
    shell_modality_patches: List[Dict[str, Any]]
    ledger_commit_receipt: Dict[str, Any]
    replay_receipt: Dict[str, Any]
    quarantine_hash72: str | None
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "witnesses": [w.to_dict() for w in self.witnesses],
            "anchor_phase_hash72": self.anchor_phase_hash72,
            "anchor_phase_index": self.anchor_phase_index,
            "mandatory_present": self.mandatory_present,
            "missing_mandatory": self.missing_mandatory,
            "temporal_ok": self.temporal_ok,
            "phase_locked": self.phase_locked,
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "shell_modality_patches": self.shell_modality_patches,
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "quarantine_hash72": self.quarantine_hash72,
            "receipt_hash72": self.receipt_hash72,
        }


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def phase_index_from_hash(value: str) -> int:
    acc = 0
    for ch in value:
        acc = (acc * 131 + ord(ch)) % PHASE_RING
    return acc


def normalize_modality(modality: str) -> str:
    return str(modality).upper().strip()


def make_observation(modality: str, source_id: str, payload: Dict[str, Any], observed_at_ns: int | None = None) -> LiveModalityObservation:
    normalized_modality = normalize_modality(modality)
    canonical_payload = canonicalize_for_hash72(payload)
    h = security_hash72_v44(
        {
            "modality": normalized_modality,
            "source_id": source_id,
            "payload": canonical_payload,
            "observed_at_ns": observed_at_ns,
        },
        domain="HHS_LIVE_MODALITY_OBSERVATION",
    )
    return LiveModalityObservation(normalized_modality, source_id, canonical_payload, observed_at_ns, h)


def shared_phase_hash(observations: Sequence[LiveModalityObservation], target_state_hash72: str) -> str:
    mandatory_hashes = {
        obs.modality: obs.observation_hash72
        for obs in observations
        if obs.modality in MANDATORY_WITNESS_MODALITIES
    }
    return security_hash72_v44(
        {
            "target_state_hash72": target_state_hash72,
            "mandatory_observation_hashes": {k: mandatory_hashes.get(k) for k in MANDATORY_WITNESS_MODALITIES},
        },
        domain="HHS_LIVE_SHARED_PHASE_ANCHOR",
    )


def make_phase_witness(
    observation: LiveModalityObservation,
    *,
    target_state_hash72: str,
    anchor_phase_hash72: str,
    max_latency_ms: int = 20,
    recursion_depth: int = 0,
) -> LivePhaseWitness:
    # Mandatory modalities lock to shared phase anchor; support modalities derive a support phase
    # from their own observation plus the shared anchor.
    if observation.modality in MANDATORY_WITNESS_MODALITIES:
        phase_hash = anchor_phase_hash72
    else:
        phase_hash = security_hash72_v44(
            {"anchor_phase_hash72": anchor_phase_hash72, "observation_hash72": observation.observation_hash72},
            domain="HHS_LIVE_SUPPORT_PHASE",
        )
    phase_index = phase_index_from_hash(phase_hash)
    window = make_temporal_window(max_latency_ms=max_latency_ms, created_at_ns=observation.observed_at_ns)
    temporal = evaluate_temporal_admissibility(
        {
            "modality": observation.modality,
            "source_id": observation.source_id,
            "target_state_hash72": target_state_hash72,
            "phase_hash72": phase_hash,
            "observation_hash72": observation.observation_hash72,
        },
        window=window,
        observed_at_ns=observation.observed_at_ns,
        recursion_depth=recursion_depth,
    )
    witness_hash = security_hash72_v44(
        {
            "observation_hash72": observation.observation_hash72,
            "target_state_hash72": target_state_hash72,
            "phase_hash72": phase_hash,
            "phase_index": phase_index,
            "temporal_receipt_hash72": temporal.receipt_hash72,
        },
        domain="HHS_LIVE_PHASE_WITNESS",
    )
    return LivePhaseWitness(observation, phase_index, phase_hash, temporal.status.value, temporal.receipt_hash72, witness_hash)


def invariant_gate_for_live_lock(
    witnesses: Sequence[LivePhaseWitness],
    mandatory_present: bool,
    temporal_ok: bool,
    phase_locked: bool,
) -> EthicalInvariantReceipt:
    delta_e_zero = bool(witnesses) and all(w.witness_hash72 for w in witnesses)
    psi_zero = mandatory_present and temporal_ok and phase_locked
    theta = theta15_true()
    omega_true = bool(hash72_digest(("live_multimodal_phase_lock_closure_v1", [w.witness_hash72 for w in witnesses], mandatory_present, temporal_ok, phase_locked), width=24))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "mandatory_present": mandatory_present,
        "temporal_ok": temporal_ok,
        "phase_locked": phase_locked,
        "witness_count": len(witnesses),
    }
    receipt = hash72_digest(("live_multimodal_phase_lock_gate_v1", details, status.value), width=24)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def shell_patches_from_witnesses(witnesses: Sequence[LivePhaseWitness], state_patch: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for w in witnesses:
        out.append(
            {
                "modality": w.observation.modality,
                "source_id": w.observation.source_id,
                "phase_hash72": w.phase_hash72,
                "patch": state_patch,
                "witness_hash72": w.witness_hash72,
                "temporal_receipt_hash72": w.temporal_receipt_hash72,
            }
        )
    return out


def lock_live_multimodal_phase(
    observations: Sequence[Dict[str, Any] | LiveModalityObservation],
    *,
    state_patch: Dict[str, Any],
    target_state_hash72: str | None = None,
    max_latency_ms: int = 20,
    recursion_depth: int = 0,
    ledger_path: str | Path = "demo_reports/hhs_realtime_multimodal_phase_ledger_v1.json",
) -> MultimodalPhaseLockReceipt:
    obs: List[LiveModalityObservation] = []
    for item in observations:
        if isinstance(item, LiveModalityObservation):
            obs.append(item)
        else:
            obs.append(
                make_observation(
                    modality=str(item.get("modality")),
                    source_id=str(item.get("source_id", item.get("modality", "source"))),
                    payload=dict(item.get("payload", {})),
                    observed_at_ns=item.get("observed_at_ns"),
                )
            )
    target_hash = target_state_hash72 or security_hash72_v44(canonicalize_for_hash72(state_patch), domain="HHS_LIVE_TARGET_STATE_PATCH")
    anchor_phase_hash = shared_phase_hash(obs, target_hash)
    anchor_phase_index = phase_index_from_hash(anchor_phase_hash)
    witnesses = [
        make_phase_witness(
            observation,
            target_state_hash72=target_hash,
            anchor_phase_hash72=anchor_phase_hash,
            max_latency_ms=max_latency_ms,
            recursion_depth=recursion_depth,
        )
        for observation in obs
    ]
    present = {w.observation.modality for w in witnesses}
    missing = sorted(set(MANDATORY_WITNESS_MODALITIES) - present)
    mandatory_present = not missing
    temporal_ok = all(w.temporal_status == TemporalGuardStatus.ADMISSIBLE.value for w in witnesses)
    mandatory_phase_hashes = {w.phase_hash72 for w in witnesses if w.observation.modality in MANDATORY_WITNESS_MODALITIES}
    phase_locked = mandatory_present and len(mandatory_phase_hashes) == 1
    gate = invariant_gate_for_live_lock(witnesses, mandatory_present, temporal_ok, phase_locked)
    status = LiveWitnessStatus.LOCKED if gate.status == ModificationStatus.APPLIED else (LiveWitnessStatus.INCOMPLETE if not mandatory_present else LiveWitnessStatus.QUARANTINED)
    patches = shell_patches_from_witnesses(witnesses, state_patch) if status == LiveWitnessStatus.LOCKED else []
    quarantine = None if status == LiveWitnessStatus.LOCKED else hash72_digest(("live_multimodal_phase_quarantine_v1", [w.witness_hash72 for w in witnesses], missing, temporal_ok, phase_locked), width=24)
    ledger = MemoryLedger(ledger_path)
    payload = {
        "target_state_hash72": target_hash,
        "anchor_phase_hash72": anchor_phase_hash,
        "anchor_phase_index": anchor_phase_index,
        "witnesses": [w.to_dict() for w in witnesses],
        "missing_mandatory": missing,
        "temporal_ok": temporal_ok,
        "phase_locked": phase_locked,
        "invariant_gate": gate.to_dict(),
        "status": status.value,
        "quarantine_hash72": quarantine,
    }
    commit = ledger.append_payloads("live_multimodal_phase_lock_receipt_v1", [payload])
    replay = replay_ledger(ledger_path)
    receipt = hash72_digest(("live_multimodal_phase_lock_receipt_v1", payload, commit.receipt_hash72, replay.receipt_hash72), width=24)
    return MultimodalPhaseLockReceipt(
        witnesses=witnesses,
        anchor_phase_hash72=anchor_phase_hash,
        anchor_phase_index=anchor_phase_index,
        mandatory_present=mandatory_present,
        missing_mandatory=missing,
        temporal_ok=temporal_ok,
        phase_locked=phase_locked,
        invariant_gate=gate,
        status=status,
        shell_modality_patches=patches,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        quarantine_hash72=quarantine,
        receipt_hash72=receipt,
    )


def demo() -> Dict[str, Any]:
    observed_at = 1_000_000_000
    state_patch = {"op": "SET", "path": "runtime.intent", "value": {"next": "phase_locked_state"}}
    observations = [
        {"modality": "AUDIO", "source_id": "audio_frame_0", "observed_at_ns": observed_at, "payload": {"rms": "1/8", "spectral_centroid": 432, "frame_hash": "audio_demo"}},
        {"modality": "HARMONICODE", "source_id": "kernel_phase", "observed_at_ns": observed_at, "payload": {"u72": True, "theta15": True, "omega": True}},
        {"modality": "XYZW", "source_id": "xyzw_algebra", "observed_at_ns": observed_at, "payload": {"xy": 1, "yx": -1, "zw": 1, "wz": -1}},
        {"modality": "HASH72", "source_id": "hash72_commit", "observed_at_ns": observed_at, "payload": {"commitment": "H72-DEMO"}},
        {"modality": "TEXT", "source_id": "text_support", "observed_at_ns": observed_at, "payload": {"intent": "supporting witness"}},
    ]
    return lock_live_multimodal_phase(observations, state_patch=state_patch, ledger_path="demo_reports/hhs_realtime_multimodal_phase_demo_v1.json").to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
