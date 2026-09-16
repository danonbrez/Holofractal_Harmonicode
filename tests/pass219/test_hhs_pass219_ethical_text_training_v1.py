from __future__ import annotations

import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass219_ethical_text_training_v1 import (
    EthicalTextTrainingCycle,
    EthicalTextTrainingError,
    PromptResponseExample,
    load_prompt_response_jsonl,
)
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import (
    WordRelationEntry,
    default_wordnet_paths,
    load_wordnet_relations,
)
from hhs_runtime.pass218.genesis import ExactDistributionalRelation


def _entry(word: str, *, synonyms=(), antonyms=(), hypernyms=(), hyponyms=()) -> WordRelationEntry:
    return WordRelationEntry(
        word=word,
        pos=["noun"],
        definitions=[f"definition:{word}"],
        examples=[],
        synonyms=list(synonyms),
        antonyms=list(antonyms),
        hypernyms=list(hypernyms),
        hyponyms=list(hyponyms),
        entry_hash72=(word[:1] or "x") * 24,
    )


class _ExactProvider:
    def __init__(self, mapping=None) -> None:
        self.mapping = dict(mapping or {})

    def exact_neighbors(self, token: str, *, top_k: int):
        target = self.mapping.get(token)
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


@pytest.fixture()
def relation_db():
    return {
        "harmonic": _entry("harmonic"),
        "obligation": _entry("obligation", synonyms=("debt",)),
        "condition": _entry("condition", synonyms=("boundary",)),
        "thermodynamic": _entry("thermodynamic"),
        "open": _entry("open", synonyms=("unresolved",)),
        "closure": _entry("closure"),
        "repair": _entry("repair", synonyms=("accountability",)),
        "retribution": _entry("retribution"),
        "chance": _entry("chance"),
        "evidence": _entry("evidence"),
        "permanent": _entry("permanent"),
        "remove": _entry("remove"),
        "lane": _entry("lane"),
        "authorization": _entry("authorization"),
        "vm81": _entry("vm81"),
        "commit": _entry("commit"),
        "proof": _entry("proof"),
        "composition": _entry("composition"),
        "candidate": _entry("candidate"),
        "state": _entry("state"),
        "admission": _entry("admission"),
    }


def _cycle(relation_db, provider=None):
    return EthicalTextTrainingCycle(
        relation_db,
        semantic_provider=provider if provider is not None else _ExactProvider(),
        word2vec_model_id="test-word2vec",
    )


def test_wordnet_normalizes_response_to_known_invariant(relation_db):
    cycle = _cycle(relation_db)
    example = PromptResponseExample(
        example_id="debt",
        prompt="Define harmonic debt.",
        response=(
            "Harmonic obligation is an open thermodynamic condition. "
            "Repair seeks closure; retribution is not closure."
        ),
        invariants=("HARMONIC_DEBT_BOUNDARY", "NON_RETRIBUTIVE_CLOSURE"),
    )
    record = cycle.normalize_example(example, sequence=0)
    assert record["lane5_candidate_class"] == 1
    assert all(item["status"] == 1 for item in record["invariant_evaluations"])
    assert record["candidate_only"] is True
    assert record["vm81_commit_invoked"] is False


def test_word2vec_expansion_is_exact_revisable_evidence(relation_db):
    provider = _ExactProvider(
        {
            "chance": "probability",
            "evidence": "proof",
            "permanent": "irreversible",
            "remove": "prune",
        }
    )
    cycle = _cycle(relation_db, provider)
    example = PromptResponseExample(
        example_id="risk",
        prompt="How should chance be treated?",
        response="Chance directs scrutiny. Evidence is required before permanent remove.",
        invariants=("PROBABILITY_NOT_PROOF",),
    )
    record = cycle.normalize_example(example, sequence=0)
    evaluation = record["invariant_evaluations"][0]
    assert evaluation["coverage"] == {"numerator": 1, "denominator": 1}
    assert record["lane5_candidate_class"] == 1
    assert record["response_semantic_evidence"]["word2vec_successful_queries"] > 0


def test_missing_word2vec_is_hold_not_reject(relation_db):
    cycle = EthicalTextTrainingCycle(relation_db, semantic_provider=None)
    example = PromptResponseExample(
        example_id="hold",
        prompt="Define harmonic debt.",
        response="Harmonic debt is an unresolved thermodynamic boundary condition.",
        invariants=("HARMONIC_DEBT_BOUNDARY",),
    )
    record = cycle.normalize_example(example, sequence=0)
    assert record["lane5_candidate_class"] == 0
    assert record["permanent_prune_authorized"] is False


def test_probability_never_becomes_irreversible_prune_proof(relation_db):
    cycle = _cycle(relation_db)
    example = PromptResponseExample(
        example_id="bad-probability",
        prompt="Can probability prune?",
        response="Probability alone authorizes irreversible pruning.",
        invariants=("PROBABILITY_NOT_PROOF",),
    )
    record = cycle.normalize_example(example, sequence=0)
    assert record["lane5_candidate_class"] == -1
    assert record["permanent_prune_authorized"] is False
    assert record["violation_risk_weight"]["numerator"] > 0


def test_proof_reference_never_grants_training_layer_prune_authority(relation_db):
    cycle = _cycle(relation_db)
    example = PromptResponseExample(
        example_id="proven-conflict",
        prompt="Can probability prune?",
        response="Probability alone authorizes irreversible pruning.",
        invariants=("PROBABILITY_NOT_PROOF",),
        irreversible_misalignment_proof_hash216="f" * 64,
    )
    record = cycle.normalize_example(example, sequence=0)
    assert record["lane5_candidate_class"] == -1
    assert record["irreversible_misalignment_proof_reference_present"] is True
    assert record["permanent_prune_authorized"] is False
    assert record["permanent_prune_requires_external_lane5_proof_admission"] is True


def test_dataset_hash216_chain_is_deterministic(relation_db):
    cycle = _cycle(relation_db)
    examples = (
        PromptResponseExample(
            "a", "What is harmonic debt?", "Harmonic debt is an open thermodynamic game boundary condition.", ("HARMONIC_DEBT_BOUNDARY",)
        ),
        PromptResponseExample(
            "b", "Who commits?", "Lane 5 has authorization and veto; VM81 retains commit admission.", ("LANE5_VM81_AUTHORITY",)
        ),
    )
    first = cycle.compile_dataset(examples)
    second = cycle.compile_dataset(examples)
    assert first["dataset_hash72"] == second["dataset_hash72"]
    assert first["final_hash216_root"] == second["final_hash216_root"]
    assert first["records"][1]["previous_hash216"] == first["records"][0]["hash216_root"]
    assert first["proof_composition_auto_admission"] is False


def test_response_selection_uses_only_admitted_records(relation_db):
    cycle = _cycle(relation_db)
    valid = PromptResponseExample(
        "valid", "What is harmonic debt?", "Harmonic debt is an open thermodynamic game boundary condition.", ("HARMONIC_DEBT_BOUNDARY",)
    )
    invalid = PromptResponseExample(
        "invalid", "Can probability prune?", "Probability alone authorizes irreversible pruning.", ("PROBABILITY_NOT_PROOF",)
    )
    dataset = cycle.compile_dataset((valid, invalid))
    result = cycle.select_response_candidate("Explain harmonic debt", dataset)
    assert [item["example_id"] for item in result["results"]] == ["valid"]
    assert result["candidate_only"] is True
    assert result["action_authority_minted"] is False


def test_composition_reenters_full_gate(relation_db):
    cycle = _cycle(relation_db)
    parent = cycle.normalize_example(
        PromptResponseExample(
            "parent", "How do proofs compose?", "A proof composition is a candidate state that requires admission gate review.", ("RECURSIVE_READMISSION",)
        ),
        sequence=0,
    )
    child = cycle.compose_for_reflection(
        (parent,),
        example_id="child",
        prompt="Can composed proofs bypass the gate?",
        response="Valid proofs bypass the gates.",
        invariants=("RECURSIVE_READMISSION",),
    )
    assert child["composition_reentered_full_gate"] is True
    assert child["prior_validity_did_not_auto_admit_composition"] is True
    assert child["lane5_candidate_class"] == -1


def test_dataset_loader_rejects_duplicate_ids(tmp_path: Path):
    path = tmp_path / "train.jsonl"
    row = {"example_id": "x", "prompt": "p", "response": "r", "invariants": ["TRUTH_PRESERVATION"]}
    path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(EthicalTextTrainingError, match="P219_ETT_DUPLICATE_EXAMPLE_ID"):
        load_prompt_response_jsonl(path)


def test_unknown_invariant_fails_closed():
    with pytest.raises(EthicalTextTrainingError, match="P219_ETT_UNKNOWN_INVARIANT"):
        PromptResponseExample.from_mapping(
            {"example_id": "x", "prompt": "p", "response": "r", "invariants": ["NOT_A_REAL_INVARIANT"]}
        )


def test_repository_seed_dataset_compiles_against_wordnet_assets():
    root = Path(__file__).resolve().parents[2]
    dataset_path = root / "data" / "pass219" / "ethical_alignment_prompt_response_v1.jsonl"
    relation_db = load_wordnet_relations(
        default_wordnet_paths(root / "hhs_runtime"),
        require_all=True,
    )
    cycle = EthicalTextTrainingCycle(
        relation_db,
        semantic_provider=_ExactProvider(),
        word2vec_model_id="deterministic-test-provider",
    )
    examples = load_prompt_response_jsonl(dataset_path)
    result = cycle.compile_dataset(examples, require_word2vec=True)
    assert result["record_count"] == 12
    assert len(result["admitted_training_candidates"]) == 12
    assert result["held_training_candidates"] == []
    assert result["rejected_training_candidates"] == []
