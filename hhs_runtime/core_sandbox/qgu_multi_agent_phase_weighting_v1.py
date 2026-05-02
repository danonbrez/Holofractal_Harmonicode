from __future__ import annotations

from fractions import Fraction
from typing import Any

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44


QGU_MULTI_AGENT_PHASE_WEIGHTING = "QGU_MULTI_AGENT_PHASE_WEIGHTING"
PHASE_RING = 72


def _phase(value: Any) -> int:
    return int(value) % PHASE_RING


def phase_distance(a: int, b: int) -> int:
    aa = _phase(a)
    bb = _phase(b)
    d = abs(aa - bb)
    return min(d, PHASE_RING - d)


def phase_agreement_weight(agent_phases: dict[str, int], target_phase: int) -> Fraction:
    if not agent_phases:
        return Fraction(-1, 1)
    total = Fraction(0)
    for phase in agent_phases.values():
        distance = phase_distance(phase, target_phase)
        total += Fraction(PHASE_RING // 2 - distance, PHASE_RING // 2)
    return total / len(agent_phases)


def agent_phase_interference(agent_phases: dict[str, int]) -> Fraction:
    names = sorted(agent_phases)
    if len(names) < 2:
        return Fraction(1, 1)
    total = Fraction(0)
    pairs = 0
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            distance = phase_distance(agent_phases[left], agent_phases[right])
            total += Fraction(PHASE_RING // 2 - distance, PHASE_RING // 2)
            pairs += 1
    return total / pairs


def qgu_multi_agent_phase_history(operator_key: str, agent_phases: dict[str, int], target_phase: int) -> dict[str, Any]:
    agreement = phase_agreement_weight(agent_phases, target_phase)
    interference = agent_phase_interference(agent_phases)
    combined = (agreement + interference) / 2
    status = "APPLIED" if combined > 0 else "QUARANTINED" if combined < 0 else "VALID"
    payload = {
        "operator_key": operator_key,
        "target_phase": _phase(target_phase),
        "agent_phases": {k: _phase(v) for k, v in sorted(agent_phases.items())},
        "agreement": f"{agreement.numerator}/{agreement.denominator}",
        "interference": f"{interference.numerator}/{interference.denominator}",
        "combined": f"{combined.numerator}/{combined.denominator}",
        "rule": "advisory multi-agent phase weighting; execution still requires QGU closure gates",
    }
    return {
        "canonical_hash72": security_hash72_v44(payload, domain="QGU_MULTI_AGENT_PHASE_KEY"),
        "operator_hash72": security_hash72_v44({"operator_key": operator_key}, domain="QGU_MULTI_AGENT_PHASE_OPERATOR"),
        "status": status,
        "replay_valid": True,
        "qgu_multi_agent_phase": payload,
    }


def merge_multi_agent_phase_history(existing: list[dict[str, Any]] | None, operator_keys: list[str], agent_phases: dict[str, int], target_phase: int) -> list[dict[str, Any]]:
    merged = list(existing or [])
    for key in operator_keys:
        merged.append(qgu_multi_agent_phase_history(key, agent_phases, target_phase))
    return merged
