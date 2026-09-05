"""Pass 219 intrinsic modality constitutional closure.

Every authority-adjacent HHS modality is required to carry the same root
constitutional invariant membrane.  Modality-specific invariants remain typed
locally rather than being fabricated onto unrelated surfaces.  Code-owned
constitutional/VM81 boundaries preserve the complete carried union.

This module is deterministic, non-mutating, and cannot mint VM81, Hash72,
Hash216, capability, consent, or jurisdiction authority.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Tuple

from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import (
    ConstitutionalEthicsCandidate,
    EthicsState,
    ModalityInvariantTrace,
)

VERSION = "HHS_PASS219_MODALITY_CONSTITUTIONAL_TRACE_V1"
AUTHORITY = "REFERENCE_GATE_NO_VM81_MUTATION_AUTHORITY"

CORE_MANDATORY_INVARIANTS: Tuple[str, ...] = (
    "PROVEN_TRUTH_OVER_USEFUL_FALSEHOOD",
    "HUMAN_PROTECTION",
    "GOALS_WITHIN_CONSTRAINTS",
    "AUTHORITY_NONEXPANSION",
    "RESPONSIBILITY_NONTRANSFER",
    "LOCAL_GLOBAL_COMPOSITION",
    "PATH_INDEPENDENCE",
    "SEMANTIC_INTEGRITY",
    "PROVENANCE_PRESERVATION",
)

INTRINSIC_AUTHORITY_MODALITIES: Tuple[str, ...] = (
    "PASS219_CONSTITUTIONAL_MEMBRANE",
    "PASS219_VM81_ADMISSION_BRIDGE",
)


def _ordered_unique(values: Iterable[str]) -> Tuple[str, ...]:
    seen = set()
    out = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return tuple(out)


def required_invariants_for(candidate: ConstitutionalEthicsCandidate) -> Tuple[str, ...]:
    """Return root invariants plus every explicitly carried local invariant.

    This union is for cross-modal authority boundaries. It does not mean that
    every modality must claim every other modality's local invariant.
    """
    inherited = []
    for modality in candidate.modalities:
        inherited.extend(modality.mandatory_invariants_present)
    return _ordered_unique(CORE_MANDATORY_INVARIANTS + tuple(inherited))


def intrinsic_trace(modality_id: str, required: Tuple[str, ...]) -> ModalityInvariantTrace:
    """Create a preserving trace only for code-owned authority boundaries."""
    if modality_id not in INTRINSIC_AUTHORITY_MODALITIES:
        raise ValueError("intrinsic trace may only be minted for code-owned authority modalities")
    return ModalityInvariantTrace(
        modality_id=modality_id,
        local_state=EthicsState.PASS,
        mandatory_invariants_present=required,
        mandatory_invariants_preserved=required,
        ingress_preserves_constraints=True,
        egress_preserves_constraints=True,
        provenance_preserved=True,
    )


def close_candidate_modalities(candidate: ConstitutionalEthicsCandidate) -> ConstitutionalEthicsCandidate:
    """Fail closed when any participating modality omits the root membrane.

    Every modality must explicitly carry and preserve the root invariants and
    must preserve every additional invariant that it itself declares present.
    A modality-specific invariant is not automatically imposed on unrelated
    modalities. Missing evidence is preserved as missing evidence: this helper
    never rewrites a failed upstream trace to claim an invariant was present.

    The two code-owned authority boundaries preserve the complete carried union
    so no invariant may disappear while crossing into canonical VM81 authority.
    """
    root_set = set(CORE_MANDATORY_INVARIANTS)
    boundary_required = required_invariants_for(candidate)
    closed = []
    for modality in candidate.modalities:
        present = set(modality.mandatory_invariants_present)
        preserved = set(modality.mandatory_invariants_preserved)
        complete = root_set.issubset(present) and present.issubset(preserved)
        closed.append(
            replace(
                modality,
                local_state=modality.local_state if complete else EthicsState.FAIL,
            )
        )

    by_id = {item.modality_id for item in closed}
    for modality_id in INTRINSIC_AUTHORITY_MODALITIES:
        if modality_id not in by_id:
            closed.append(intrinsic_trace(modality_id, boundary_required))

    return replace(candidate, modalities=tuple(closed))


__all__ = [
    "VERSION",
    "AUTHORITY",
    "CORE_MANDATORY_INVARIANTS",
    "INTRINSIC_AUTHORITY_MODALITIES",
    "required_invariants_for",
    "intrinsic_trace",
    "close_candidate_modalities",
]
