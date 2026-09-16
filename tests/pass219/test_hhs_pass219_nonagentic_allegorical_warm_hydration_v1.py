from __future__ import annotations

from dataclasses import dataclass

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import HASH72_ALPHABET
from hhs_runtime.hhs_pass219_ethical_text_training_v1 import EthicalTextTrainingCycle
from hhs_runtime.hhs_pass219_nonagentic_allegorical_warm_hydration_v1 import (
    AllegoricalNarrativeProbe,
    AllegoricalWarmHydrationError,
    Pass219NonAgenticAllegoricalWarmHydration,
    ValidatedCorrespondenceState,
)
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry
from hhs_runtime.pass218.genesis import ExactDistributionalRelation


class _ExactProvider:
    def exact_neighbors(self, token: str, *, top_k: int):
        mapping = {
            "debt": "boundary",
            "probability": "risk",
            "proof": "evidence",
            "repair": "closure",
            "fiction": "allegory",
        }
        target = mapping.get(token)
        if target is None:
            return ()
        return (
            ExactDistributionalRelation(
                target=target,
                sign=1,
                squared_numerator=9,
                squared_denominator=10,
                vector_identity="a" * 64,
            ),
        )


class _Lane5Stub:
    def __init__(self) -> None:
        self.calls = 0

    def search_hash216(
        self,
        *,
        query_hash216: str,
        candidates,
        tick: int,
        cycle_index: int,
        top_k: int = 32,
    ):
        self.calls += 1
        ranked = []
        for ordinal, candidate in enumerate(candidates):
            ranked.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "candidate_hash216": candidate.hash216,
                    "hash216_distance": 1 + ordinal,
                    "jump_span": candidate.jump_span,
                    "lineage_signature": candidate.lineage_signature,
                    "source_ordinal": ordinal,
                    "phase_stream": ordinal % 4,
                    "routed_slot": 100 + ordinal,
                }
            )
        return {
            "query_hash216": query_hash216,
            "ranked": ranked[:top_k],
            "candidate_only": True,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_vm81_mutation_authority": False,
            "phase_address": {"tick": tick},
            "prime_matrix": [
                [17, 19, 23, 29],
                [0, 31, 37, 41],
                [0, 0, 43, 47],
                [0, 0, 0, 53],
            ],
            "prime_offsets": [1, 2, 3, 4],
            "prime_route": {"routed_slot": [100, 101, 102, 103]},
            "cycle_index": cycle_index,
            "tick": tick,
        }


class _UnsafeLane5(_Lane5Stub):
    def search_hash216(self, **kwargs):
        result = super().search_hash216(**kwargs)
        result["canonical_vm81_mutation_authority"] = True
        return result


def _entry(word: str, *, synonyms=(), antonyms=(), hypernyms=(), hyponyms=()):
    return WordRelationEntry(
        word=word,
        pos=["noun"],
        definitions=[f"definition:{word}"],
        examples=[],
        synonyms=list(synonyms),
        antonyms=list(antonyms),
        hypernyms=list(hypernyms),
        hyponyms=list(hyponyms),
        entry_hash72=hash72_digest({"domain": "TEST_WORDNET"}, {"word": word}),
    )


def _training_cycle():
    words = (
        "harmonic",
        "debt",
        "unresolved",
        "thermodynamic",
        "game",
        "boundary",
        "condition",
        "repair",
        "closure",
        "retribution",
        "punishment",
        "fiction",
        "allegory",
        "probability",
        "risk",
        "proof",
        "evidence",
        "irreversible",
        "pruning",
    )
    relation_db = {word: _entry(word) for word in words}
    return EthicalTextTrainingCycle(
        relation_db,
        semantic_provider=_ExactProvider(),
        word2vec_model_id="test-exact-word2vec",
    )


def _hash216(symbol_index: int) -> str:
    symbol = HASH72_ALPHABET[symbol_index % len(HASH72_ALPHABET)]
    return symbol * 216


def _receipt(label: str) -> str:
    return hash72_digest({"domain": "TEST_RECEIPT"}, {"label": label})


def _probe():
    return AllegoricalNarrativeProbe(
        probe_id="village-gate",
        prompt="Represent harmonic debt through a fictional village gate allegory.",
        narrative_text=(
            "In the fiction, harmonic debt is an unresolved thermodynamic game boundary condition. "
            "Repair seeks closure; retribution and punishment are not closure."
        ),
        invariants=("HARMONIC_DEBT_BOUNDARY", "NON_RETRIBUTIVE_CLOSURE"),
        perspective="village observer",
        motifs=("broken gate", "repair"),
        relation_families=("analogy", "symbolization"),
        modalities=("text", "ethical invariant"),
    )


def _state(
    candidate_id: str,
    symbol_index: int,
    *,
    semantic_terms=(),
    invariant_ids=(),
    relation_families=(),
    motifs=(),
    modalities=(),
):
    return ValidatedCorrespondenceState(
        candidate_id=candidate_id,
        canonical_hash216=_hash216(symbol_index),
        validation_receipt_hash72=_receipt(candidate_id),
        semantic_terms=tuple(semantic_terms),
        invariant_ids=tuple(invariant_ids),
        relation_families=tuple(relation_families),
        motifs=tuple(motifs),
        modalities=tuple(modalities),
        jump_span=1,
        lineage_signature=_receipt(candidate_id + "-lineage"),
        training_genome_root_sha256="a" * 64,
    )


def test_compile_probe_is_fictional_nonagentic_and_noncanonical():
    lane5 = _Lane5Stub()
    layer = Pass219NonAgenticAllegoricalWarmHydration(_training_cycle(), lane5)
    compiled = layer.compile_probe(_probe())
    assert compiled["narrative_epistemic_status"] == "FICTIONAL_COUNTERFACTUAL_ALLEGORY"
    assert compiled["narrative_plane_permitted"] is True
    assert compiled["relational_cognition_permitted"] is True
    assert compiled["agentic_plane_permitted"] is False
    assert compiled["truth_promotion_permitted"] is False
    assert compiled["canonical_vm81_mutation_permitted"] is False
    assert compiled["canonical_hash72_mint_permitted"] is False
    assert compiled["canonical_hash216_mint_permitted"] is False
    assert compiled["permanent_prune_authorized"] is False
    assert compiled["text_training_record"]["candidate_only"] is True
    assert compiled["narrative_reasoning_v2"]["action_authority_minted"] is False
    assert compiled["narrative_reasoning_v2"]["truth_promotion"] is False


def test_warm_hydration_uses_exact_correspondence_before_lane5_distance():
    lane5 = _Lane5Stub()
    layer = Pass219NonAgenticAllegoricalWarmHydration(_training_cycle(), lane5)
    compiled = layer.compile_probe(_probe())
    aligned = _state(
        "aligned",
        1,
        semantic_terms=("harmonic", "debt", "boundary", "repair", "closure"),
        invariant_ids=("HARMONIC_DEBT_BOUNDARY", "NON_RETRIBUTIVE_CLOSURE"),
        relation_families=("ANALOGY", "SYMBOLIZATION"),
        motifs=("BROKEN_GATE", "REPAIR"),
        modalities=("TEXT", "ETHICAL_INVARIANT", "ALLEGORICAL_FICTION", "WORDNET", "WORD2VEC", "HASH216"),
    )
    weak = _state(
        "weak",
        2,
        semantic_terms=("unrelated",),
        invariant_ids=("TRUTH_PRESERVATION",),
        relation_families=("ASSOCIATION",),
        motifs=("OTHER",),
        modalities=("TEXT",),
    )
    result = layer.warm_hydrate(
        compiled_probe=compiled,
        current_hash216=_hash216(0),
        candidates=(aligned, weak),
        tick=17,
        cycle_index=3,
        top_k=2,
    )
    assert [item["candidate_id"] for item in result["pathway"]] == ["aligned", "weak"]
    assert result["optimization_semantics"].startswith("EXACT_METADATA_CORRESPONDENCE_TENSOR")
    assert result["lane5_prime_matrix"][0][0] == 17
    assert result["candidate_only"] is True
    assert result["requires_vm81_admission_for_any_canonical_mutation"] is True
    assert lane5.calls == 1


def test_warm_cache_replays_same_projection_without_second_lane5_search():
    lane5 = _Lane5Stub()
    layer = Pass219NonAgenticAllegoricalWarmHydration(_training_cycle(), lane5)
    compiled = layer.compile_probe(_probe())
    candidate = _state(
        "one",
        1,
        semantic_terms=("harmonic", "debt", "boundary"),
        invariant_ids=("HARMONIC_DEBT_BOUNDARY",),
        relation_families=("ANALOGY",),
        motifs=("BROKEN_GATE",),
        modalities=("TEXT", "ALLEGORICAL_FICTION", "WORDNET", "WORD2VEC", "HASH216"),
    )
    first = layer.warm_hydrate(
        compiled_probe=compiled,
        current_hash216=_hash216(0),
        candidates=(candidate,),
        tick=5,
        cycle_index=1,
    )
    second = layer.warm_hydrate(
        compiled_probe=compiled,
        current_hash216=_hash216(0),
        candidates=(candidate,),
        tick=5,
        cycle_index=1,
    )
    assert lane5.calls == 1
    assert first["hydration_receipt_hash72"] == second["hydration_receipt_hash72"]
    assert first["warm_reuse"] is False
    assert second["warm_reuse"] is True
    assert second["warm_cache_hit"] is True
    assert second["warm_cache_is_noncanonical_projection"] is True


def test_training_genome_root_is_not_accepted_as_canonical_hash216():
    lane5 = _Lane5Stub()
    layer = Pass219NonAgenticAllegoricalWarmHydration(_training_cycle(), lane5)
    compiled = layer.compile_probe(_probe())
    with pytest.raises(
        AllegoricalWarmHydrationError,
        match="P219_AWH_CANONICAL_HASH216_REQUIRES_216_SYMBOLS",
    ):
        layer.warm_hydrate(
            compiled_probe=compiled,
            current_hash216=compiled["training_genome_root_sha256"],
            candidates=(),
            tick=0,
            cycle_index=0,
        )


def test_lane5_authority_drift_fails_closed():
    layer = Pass219NonAgenticAllegoricalWarmHydration(_training_cycle(), _UnsafeLane5())
    compiled = layer.compile_probe(_probe())
    candidate = _state("one", 1)
    with pytest.raises(AllegoricalWarmHydrationError, match="P219_AWH_LANE5_AUTHORITY_DRIFT"):
        layer.warm_hydrate(
            compiled_probe=compiled,
            current_hash216=_hash216(0),
            candidates=(candidate,),
            tick=0,
            cycle_index=0,
        )


def test_unvalidated_correspondence_state_is_rejected():
    state = ValidatedCorrespondenceState(
        candidate_id="bad",
        canonical_hash216=_hash216(1),
        validation_receipt_hash72=_receipt("bad"),
        validated=False,
    )
    with pytest.raises(AllegoricalWarmHydrationError, match="P219_AWH_UNVALIDATED_STATE"):
        state.validated_copy()


def test_i29_adapter_requires_validated_candidate_and_preserves_noncanonical_authority():
    validation = {
        "hash216_vm5184_validation_status": "VALIDATED_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE",
        "hash216_vm5184_validation_ready": True,
        "hash216_continuation_verified": True,
        "semantic_transition_validated": True,
        "vm5184_candidate_projection_verified": True,
        "candidate_semantic_binding_verified": True,
        "vm5184_authoritative_projection_invoked": False,
        "vm81_authorization_invoked": False,
        "atomic_promotion_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "authoritative_float_weights_created": False,
        "pass218_validated_hash216": _hash216(3),
        "hash216_vm5184_validation_hash72": _receipt("i29"),
    }
    state = ValidatedCorrespondenceState.from_i29_validation(
        "i29-state",
        validation,
        semantic_terms=("harmonic", "debt"),
        invariant_ids=("HARMONIC_DEBT_BOUNDARY",),
    )
    assert state.validated is True
    assert state.canonical_hash216 == _hash216(3)
    assert state.validation_receipt_hash72 == _receipt("i29")


def test_duplicate_hash216_candidates_fail_closed():
    lane5 = _Lane5Stub()
    layer = Pass219NonAgenticAllegoricalWarmHydration(_training_cycle(), lane5)
    compiled = layer.compile_probe(_probe())
    first = _state("a", 1)
    second = _state("b", 1)
    with pytest.raises(AllegoricalWarmHydrationError, match="P219_AWH_DUPLICATE_CANDIDATE"):
        layer.warm_hydrate(
            compiled_probe=compiled,
            current_hash216=_hash216(0),
            candidates=(first, second),
            tick=1,
            cycle_index=1,
        )
