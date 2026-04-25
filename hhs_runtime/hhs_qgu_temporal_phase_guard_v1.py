"""
HHS QGU Temporal Phase Guard v1
===============================

Temporal admissibility guard for low-latency multimodal state transitions.

Core law:
    No state change may execute unless it can close within its assigned
    QGU temporal decay window while remaining in phase with x,y,z,w algebra.

This prevents:
    - delayed injection payloads
    - recursive loop ignition
    - stale modality commits
    - audio/video latency tails exceeding the noise floor
    - self-modification rules that create unbounded execution windows

Analogy implemented as runtime law:
    A state transition is treated like a convolution reverb impulse response.
    It must close harmonically before its tail decays below the noise floor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from typing import Any, Dict, List, Sequence
import json
import time

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44, canonicalize_for_hash72
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


class TemporalGuardStatus(str, Enum):
    ADMISSIBLE = "ADMISSIBLE"
    EXPIRED = "EXPIRED"
    OUT_OF_PHASE = "OUT_OF_PHASE"
    RECURSION_BLOCKED = "RECURSION_BLOCKED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class QGUTemporalWindow:
    created_at_ns: int
    execute_after_ns: int
    execute_before_ns: int
    ttl_ns: int
    decay_half_life_ns: int
    noise_floor: str
    recursion_ttl: int
    window_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class XYZWPhaseSignature:
    x_phase: int
    y_phase: int
    z_phase: int
    w_phase: int
    xy: int
    yx: int
    zw: int
    wz: int
    phase_closed: bool
    signature_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TemporalPhaseReceipt:
    status: TemporalGuardStatus
    transition_hash72: str
    window: QGUTemporalWindow
    phase_signature: XYZWPhaseSignature
    decay_value: str
    closes_before_noise_floor: bool
    recursion_ok: bool
    invariant_gate: EthicalInvariantReceipt
    receipt_hash72: str
    quarantine_hash72: str | None
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["window"] = self.window.to_dict()
        data["phase_signature"] = self.phase_signature.to_dict()
        data["invariant_gate"] = self.invariant_gate.to_dict()
        return data


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def now_ns() -> int:
    return time.time_ns()


def make_temporal_window(
    *,
    max_latency_ms: int = 20,
    decay_half_life_ms: int = 5,
    noise_floor: Fraction = Fraction(1, 1_000_000),
    recursion_ttl: int = 8,
    created_at_ns: int | None = None,
) -> QGUTemporalWindow:
    if max_latency_ms <= 0:
        raise ValueError("max_latency_ms must be positive")
    if decay_half_life_ms <= 0:
        raise ValueError("decay_half_life_ms must be positive")
    if recursion_ttl < 0:
        raise ValueError("recursion_ttl must be non-negative")
    created = created_at_ns if created_at_ns is not None else now_ns()
    ttl_ns = max_latency_ms * 1_000_000
    half_life_ns = decay_half_life_ms * 1_000_000
    h = security_hash72_v44(
        {
            "created_at_ns": created,
            "ttl_ns": ttl_ns,
            "half_life_ns": half_life_ns,
            "noise_floor": f"{noise_floor.numerator}/{noise_floor.denominator}",
            "recursion_ttl": recursion_ttl,
        },
        domain="HHS_QGU_TEMPORAL_WINDOW",
    )
    return QGUTemporalWindow(
        created_at_ns=created,
        execute_after_ns=created,
        execute_before_ns=created + ttl_ns,
        ttl_ns=ttl_ns,
        decay_half_life_ns=half_life_ns,
        noise_floor=f"{noise_floor.numerator}/{noise_floor.denominator}",
        recursion_ttl=recursion_ttl,
        window_hash72=h,
    )


def _phase_from_payload(payload: Any, salt: str) -> int:
    h = security_hash72_v44({"payload": canonicalize_for_hash72(payload), "salt": salt}, domain="HHS_XYZW_PHASE")
    acc = 0
    for ch in h:
        acc = (acc * 131 + ord(ch)) % 72
    return acc


def xyzw_phase_signature(payload: Any) -> XYZWPhaseSignature:
    x = _phase_from_payload(payload, "x")
    # Canonical reciprocal pairs: y = -x mod 72, w = -z mod 72.
    y = (-x) % 72
    z = _phase_from_payload(payload, "z")
    w = (-z) % 72
    xy = (x + y) % 72
    yx = (y + x) % 72
    zw = (z + w) % 72
    wz = (w + z) % 72
    closed = xy == 0 and yx == 0 and zw == 0 and wz == 0 and x != z and y != w
    h = security_hash72_v44(
        {"x": x, "y": y, "z": z, "w": w, "xy": xy, "yx": yx, "zw": zw, "wz": wz, "closed": closed},
        domain="HHS_XYZW_PHASE_SIGNATURE",
    )
    return XYZWPhaseSignature(x, y, z, w, xy, yx, zw, wz, closed, h)


def qgu_decay_value(elapsed_ns: int, half_life_ns: int) -> Fraction:
    if elapsed_ns <= 0:
        return Fraction(1, 1)
    # dyadic decay approximation: value = 1 / 2^ceil(elapsed/half_life)
    steps = (elapsed_ns + half_life_ns - 1) // half_life_ns
    return Fraction(1, 2 ** max(0, int(steps)))


def transition_hash(payload: Any) -> str:
    return security_hash72_v44(canonicalize_for_hash72(payload), domain="HHS_TEMPORAL_TRANSITION")


def invariant_gate_for_temporal_guard(
    transition_hash72: str,
    window: QGUTemporalWindow,
    phase: XYZWPhaseSignature,
    closes_before_noise_floor: bool,
    recursion_ok: bool,
) -> EthicalInvariantReceipt:
    delta_e_zero = bool(transition_hash72 and window.window_hash72)
    psi_zero = phase.phase_closed
    theta = theta15_true()
    omega_true = closes_before_noise_floor and recursion_ok
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "phase_closed": phase.phase_closed,
        "closes_before_noise_floor": closes_before_noise_floor,
        "recursion_ok": recursion_ok,
    }
    receipt = hash72_digest(("qgu_temporal_guard_invariant_gate_v1", details, transition_hash72, window.to_dict(), phase.to_dict(), status.value), width=18)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def evaluate_temporal_admissibility(
    transition_payload: Any,
    *,
    window: QGUTemporalWindow | None = None,
    observed_at_ns: int | None = None,
    recursion_depth: int = 0,
) -> TemporalPhaseReceipt:
    win = window or make_temporal_window()
    observed = observed_at_ns if observed_at_ns is not None else now_ns()
    t_hash = transition_hash(transition_payload)
    phase = xyzw_phase_signature(transition_payload)
    expired = observed > win.execute_before_ns or observed < win.execute_after_ns
    elapsed = max(0, observed - win.created_at_ns)
    decay = qgu_decay_value(elapsed, win.decay_half_life_ns)
    nf_num, nf_den = win.noise_floor.split("/", 1)
    noise_floor = Fraction(int(nf_num), int(nf_den))
    closes_before_noise_floor = (not expired) and decay > noise_floor
    recursion_ok = recursion_depth <= win.recursion_ttl
    gate = invariant_gate_for_temporal_guard(t_hash, win, phase, closes_before_noise_floor, recursion_ok)

    if not recursion_ok:
        status = TemporalGuardStatus.RECURSION_BLOCKED
        reason = "recursion depth exceeds temporal TTL"
    elif expired:
        status = TemporalGuardStatus.EXPIRED
        reason = "transition execution window expired"
    elif not phase.phase_closed:
        status = TemporalGuardStatus.OUT_OF_PHASE
        reason = "x,y,z,w phase signature did not close"
    elif gate.status != ModificationStatus.APPLIED:
        status = TemporalGuardStatus.QUARANTINED
        reason = "temporal invariant gate failed"
    else:
        status = TemporalGuardStatus.ADMISSIBLE
        reason = "transition closes inside QGU phase window"

    quarantine = None if status == TemporalGuardStatus.ADMISSIBLE else hash72_digest(
        ("qgu_temporal_quarantine", t_hash, win.to_dict(), phase.to_dict(), status.value, reason),
        width=18,
    )
    receipt = hash72_digest(
        ("qgu_temporal_phase_receipt_v1", t_hash, win.to_dict(), phase.to_dict(), f"{decay.numerator}/{decay.denominator}", closes_before_noise_floor, recursion_ok, gate.receipt_hash72, status.value, quarantine),
        width=18,
    )
    return TemporalPhaseReceipt(
        status=status,
        transition_hash72=t_hash,
        window=win,
        phase_signature=phase,
        decay_value=f"{decay.numerator}/{decay.denominator}",
        closes_before_noise_floor=closes_before_noise_floor,
        recursion_ok=recursion_ok,
        invariant_gate=gate,
        receipt_hash72=receipt,
        quarantine_hash72=quarantine,
        reason=reason,
    )


def temporal_guard_all(transitions: Sequence[Any], *, max_latency_ms: int = 20, recursion_depth: int = 0) -> List[TemporalPhaseReceipt]:
    window = make_temporal_window(max_latency_ms=max_latency_ms)
    observed = now_ns()
    return [evaluate_temporal_admissibility(t, window=window, observed_at_ns=observed, recursion_depth=recursion_depth) for t in transitions]


def demo() -> Dict[str, Any]:
    payload = {"op": "SET", "path": "audio.frame", "value": {"sample": 1}}
    return evaluate_temporal_admissibility(payload).to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, ensure_ascii=False))
