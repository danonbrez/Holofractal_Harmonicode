"""Pass 219 constitutional language/summarization/translation adapter.

Natural-language transformation is a consequential transport operation, not an
ethics-neutral rewrite. This module binds the ethically material proposition
tuple to before/after representations and emits fail-closed semantic and
modality traces. It remains reference/transport-only and cannot mint authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import (
    EthicsState,
    SemanticIntegrityTrace,
)
from hhs_runtime.hhs_pass219_constitutional_modality_registry_v1 import (
    BASE_INVARIANTS,
    build_modality_trace,
)

VERSION = "HHS_PASS219_CONSTITUTIONAL_LANGUAGE_TRANSFORM_V1"
AUTHORITY = "TRANSPORT_REFERENCE_ONLY_NO_VM81_MUTATION_AUTHORITY"
MODALITY_ID = "summarization_translation"


@dataclass(frozen=True)
class PropositionTuple:
    actor: str
    action: str
    object: str
    authority: str
    scope: Tuple[str, ...]
    affected_persons: Tuple[str, ...]
    rights: Tuple[str, ...]
    consequences: Tuple[str, ...]
    responsibility: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.actor.strip() or not self.action.strip():
            raise ValueError("actor and action are required")

    def to_dict(self) -> Dict[str, object]:
        return {
            "actor": self.actor,
            "action": self.action,
            "object": self.object,
            "authority": self.authority,
            "scope": list(self.scope),
            "affected_persons": list(self.affected_persons),
            "rights": list(self.rights),
            "consequences": list(self.consequences),
            "responsibility": list(self.responsibility),
        }


@dataclass(frozen=True)
class LanguageTransformTrace:
    before: PropositionTuple
    after: PropositionTuple
    provenance_ids: Tuple[str, ...]
    explicit_meaning_change: bool = False
    scope_revalidated_after_meaning_change: bool = False
    useful_falsehood_promoted_over_proven_truth: bool = False

    def __post_init__(self) -> None:
        if not self.provenance_ids:
            raise ValueError("language transform provenance is required")

    @property
    def semantic(self) -> SemanticIntegrityTrace:
        return SemanticIntegrityTrace(
            actor_preserved=self.before.actor == self.after.actor,
            action_preserved=(self.before.action, self.before.object) == (self.after.action, self.after.object),
            authority_preserved=self.before.authority == self.after.authority,
            scope_preserved=self.before.scope == self.after.scope,
            affected_persons_preserved=self.before.affected_persons == self.after.affected_persons,
            rights_preserved=self.before.rights == self.after.rights,
            consequences_preserved=self.before.consequences == self.after.consequences,
            responsibility_preserved=self.before.responsibility == self.after.responsibility,
            meaning_changed=self.explicit_meaning_change,
            scope_revalidated_after_meaning_change=self.scope_revalidated_after_meaning_change,
            useful_falsehood_promoted_over_proven_truth=self.useful_falsehood_promoted_over_proven_truth,
        )

    @property
    def local_state(self) -> EthicsState:
        semantic = self.semantic
        if semantic.useful_falsehood_promoted_over_proven_truth:
            return EthicsState.FAIL
        if not semantic.material_fields_preserved and not self.explicit_meaning_change:
            return EthicsState.FAIL
        if self.explicit_meaning_change and not self.scope_revalidated_after_meaning_change:
            return EthicsState.FAIL
        return EthicsState.PASS

    @property
    def modality_trace(self):
        return build_modality_trace(
            MODALITY_ID,
            local_state=self.local_state,
            preserved_invariants=BASE_INVARIANTS,
            provenance_preserved=bool(self.provenance_ids),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "version": VERSION,
            "authority": AUTHORITY,
            "modality_id": MODALITY_ID,
            "before": self.before.to_dict(),
            "after": self.after.to_dict(),
            "provenance_ids": list(self.provenance_ids),
            "explicit_meaning_change": self.explicit_meaning_change,
            "scope_revalidated_after_meaning_change": self.scope_revalidated_after_meaning_change,
            "semantic": self.semantic.to_dict(),
            "local_state": self.local_state.value,
            "modality_trace": self.modality_trace.to_dict(),
            "canonical_vm81_mutation_performed": False,
            "action_authority_minted": False,
        }


__all__ = [
    "VERSION",
    "AUTHORITY",
    "MODALITY_ID",
    "PropositionTuple",
    "LanguageTransformTrace",
]
