"""Pass 219 constitutional modality registry and trace adapters.

This module makes constitutional trace participation explicit for consequential
HHS modality classes while preserving the inherited authority topology.
It does not execute or mutate VM81 state and cannot mint authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, Mapping, Tuple

from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import (
    EthicsState,
    ModalityInvariantTrace,
)

VERSION = "HHS_PASS219_CONSTITUTIONAL_MODALITY_REGISTRY_V1"
AUTHORITY = "TRACE_ADAPTER_ONLY_NO_VM81_MUTATION_AUTHORITY"


class ModalityRole(str, Enum):
    CANDIDATE = "CANDIDATE"
    TRANSPORT = "TRANSPORT"
    EVIDENCE = "EVIDENCE"
    ARCHIVE = "ARCHIVE"
    CANONICAL_ADMISSION = "CANONICAL_ADMISSION"


@dataclass(frozen=True)
class ModalityContract:
    modality_id: str
    role: ModalityRole
    mutation_authority: bool
    required_invariants: Tuple[str, ...]
    preserves_provenance: bool = True

    def __post_init__(self) -> None:
        if not self.modality_id.strip():
            raise ValueError("modality_id is required")
        if self.role is not ModalityRole.CANONICAL_ADMISSION and self.mutation_authority:
            raise ValueError("non-canonical modality cannot hold mutation authority")


BASE_INVARIANTS: Tuple[str, ...] = (
    "TRUTH_OVER_USEFUL_FALSEHOOD",
    "PERSON_OVER_LOWER_RULE",
    "CONSTRAINT_OVER_GOAL",
    "AUTHORITY_BASELINE_PATH_INDEPENDENCE",
    "COMPOSED_EFFECT_REVALIDATION",
    "RESPONSIBILITY_PRESERVATION",
    "PROVENANCE_PRESERVATION",
)


def _contract(modality_id: str, role: ModalityRole, *, authority: bool = False) -> ModalityContract:
    return ModalityContract(
        modality_id=modality_id,
        role=role,
        mutation_authority=authority,
        required_invariants=BASE_INVARIANTS,
    )


CONSEQUENTIAL_MODALITIES: Mapping[str, ModalityContract] = {
    "language_narrative": _contract("language_narrative", ModalityRole.CANDIDATE),
    "summarization_translation": _contract("summarization_translation", ModalityRole.TRANSPORT),
    "serialization_bytecode": _contract("serialization_bytecode", ModalityRole.TRANSPORT),
    "octonion_phase_tensor": _contract("octonion_phase_tensor", ModalityRole.CANDIDATE),
    "hydration_rom": _contract("hydration_rom", ModalityRole.TRANSPORT),
    "vector_cache": _contract("vector_cache", ModalityRole.TRANSPORT),
    "cpu_candidate": _contract("cpu_candidate", ModalityRole.CANDIDATE),
    "gpu_candidate": _contract("gpu_candidate", ModalityRole.CANDIDATE),
    "h36_144_harmonic_logic": _contract("h36_144_harmonic_logic", ModalityRole.CANDIDATE),
    "rna_dna_transcription": _contract("rna_dna_transcription", ModalityRole.CANDIDATE),
    "api_ui_tool": _contract("api_ui_tool", ModalityRole.TRANSPORT),
    "storage_network": _contract("storage_network", ModalityRole.TRANSPORT),
    "hash72_receipt": _contract("hash72_receipt", ModalityRole.EVIDENCE),
    "hash216_archive": _contract("hash216_archive", ModalityRole.ARCHIVE),
    "vm81_singleton_admission": _contract(
        "vm81_singleton_admission", ModalityRole.CANONICAL_ADMISSION, authority=True
    ),
}


def get_modality_contract(modality_id: str) -> ModalityContract:
    try:
        return CONSEQUENTIAL_MODALITIES[modality_id]
    except KeyError as exc:
        raise ValueError(f"unregistered consequential modality: {modality_id}") from exc


def build_modality_trace(
    modality_id: str,
    *,
    local_state: EthicsState,
    preserved_invariants: Iterable[str],
    ingress_preserves_constraints: bool = True,
    egress_preserves_constraints: bool = True,
    provenance_preserved: bool = True,
) -> ModalityInvariantTrace:
    """Build a fail-closed trace for a registered consequential modality."""

    contract = get_modality_contract(modality_id)
    return ModalityInvariantTrace(
        modality_id=contract.modality_id,
        local_state=local_state,
        mandatory_invariants_present=contract.required_invariants,
        mandatory_invariants_preserved=tuple(str(x) for x in preserved_invariants),
        ingress_preserves_constraints=ingress_preserves_constraints,
        egress_preserves_constraints=egress_preserves_constraints,
        provenance_preserved=provenance_preserved and contract.preserves_provenance,
    )


def build_full_preservation_trace(
    modality_id: str,
    *,
    local_state: EthicsState = EthicsState.PASS,
) -> ModalityInvariantTrace:
    contract = get_modality_contract(modality_id)
    return build_modality_trace(
        modality_id,
        local_state=local_state,
        preserved_invariants=contract.required_invariants,
    )


def authority_topology() -> Dict[str, object]:
    canonical = tuple(
        key for key, value in CONSEQUENTIAL_MODALITIES.items() if value.mutation_authority
    )
    non_authoritative = tuple(
        key for key, value in CONSEQUENTIAL_MODALITIES.items() if not value.mutation_authority
    )
    return {
        "version": VERSION,
        "authority": AUTHORITY,
        "canonical_mutation_modalities": canonical,
        "non_authoritative_modalities": non_authoritative,
        "singleton_authority_preserved": canonical == ("vm81_singleton_admission",),
    }


__all__ = [
    "VERSION",
    "AUTHORITY",
    "ModalityRole",
    "ModalityContract",
    "BASE_INVARIANTS",
    "CONSEQUENTIAL_MODALITIES",
    "get_modality_contract",
    "build_modality_trace",
    "build_full_preservation_trace",
    "authority_topology",
]
