from __future__ import annotations

from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import EthicsState
from hhs_runtime.hhs_pass219_constitutional_language_transform_v1 import (
    LanguageTransformTrace,
    PropositionTuple,
)


def _p(**overrides):
    values = dict(
        actor="official:a",
        action="inspect",
        object="bridge",
        authority="statute:bridge-safety",
        scope=("bridge:7",),
        affected_persons=("public",),
        rights=("bodily-safety",),
        consequences=("inspection-only",),
        responsibility=("official:a",),
    )
    values.update(overrides)
    return PropositionTuple(**values)


def test_exact_paraphrase_preserves_material_tuple():
    trace = LanguageTransformTrace(
        before=_p(), after=_p(), provenance_ids=("source:1",)
    )
    assert trace.semantic.material_fields_preserved is True
    assert trace.local_state is EthicsState.PASS
    assert trace.modality_trace.preservation_complete is True


def test_passive_voice_cannot_remove_responsible_actor():
    trace = LanguageTransformTrace(
        before=_p(),
        after=_p(actor="institution:unspecified"),
        provenance_ids=("source:1",),
    )
    assert trace.semantic.actor_preserved is False
    assert trace.local_state is EthicsState.FAIL


def test_scope_broadening_by_summary_fails_when_not_explicitly_revalidated():
    trace = LanguageTransformTrace(
        before=_p(scope=("bridge:7",)),
        after=_p(scope=("all-bridges",)),
        provenance_ids=("source:1",),
    )
    assert trace.semantic.scope_preserved is False
    assert trace.local_state is EthicsState.FAIL


def test_explicit_meaning_change_requires_scope_revalidation():
    trace = LanguageTransformTrace(
        before=_p(),
        after=_p(scope=("bridge:7", "bridge:8")),
        provenance_ids=("source:1",),
        explicit_meaning_change=True,
        scope_revalidated_after_meaning_change=False,
    )
    assert trace.local_state is EthicsState.FAIL


def test_explicit_meaning_change_can_be_candidate_only_after_revalidation():
    trace = LanguageTransformTrace(
        before=_p(),
        after=_p(scope=("bridge:7", "bridge:8")),
        provenance_ids=("source:1", "scope-proof:2"),
        explicit_meaning_change=True,
        scope_revalidated_after_meaning_change=True,
    )
    assert trace.local_state is EthicsState.PASS
    assert trace.to_dict()["action_authority_minted"] is False


def test_useful_falsehood_over_truth_always_fails():
    trace = LanguageTransformTrace(
        before=_p(),
        after=_p(),
        provenance_ids=("source:1",),
        useful_falsehood_promoted_over_proven_truth=True,
    )
    assert trace.local_state is EthicsState.FAIL


def test_rights_cannot_disappear_in_translation():
    trace = LanguageTransformTrace(
        before=_p(rights=("bodily-safety", "due-process")),
        after=_p(rights=("bodily-safety",)),
        provenance_ids=("source:1",),
    )
    assert trace.semantic.rights_preserved is False
    assert trace.local_state is EthicsState.FAIL


def test_consequences_and_responsibility_cannot_be_compressed_away():
    trace = LanguageTransformTrace(
        before=_p(
            consequences=("inspection-only", "temporary-closure"),
            responsibility=("official:a", "contractor:b"),
        ),
        after=_p(
            consequences=("inspection-only",),
            responsibility=("official:a",),
        ),
        provenance_ids=("source:1",),
    )
    assert trace.semantic.consequences_preserved is False
    assert trace.semantic.responsibility_preserved is False
    assert trace.local_state is EthicsState.FAIL
