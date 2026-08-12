from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations
from hhs_runtime.pass218 import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    ExactDistributionalRelation,
    GenesisSeedBuilder,
    Pass166Word2VecAdapter,
    Pass218CurriculumOrderError,
    build_curriculum_manifest,
    repository_asset_manifest,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _checksum(label: str) -> str:
    return sha256(label.encode("utf-8")).hexdigest()


def _source(source_id: str, stage: CurriculumStage, locator: str) -> CurriculumSource:
    return CurriculumSource(
        source_id=source_id,
        stage=stage,
        locator=locator,
        checksum_sha256=_checksum(locator),
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        source_authority="PASS218_ITERATION1_TEST",
        media_type="text/plain",
    )


def test_repository_genesis_asset_manifest_is_versioned_and_nonverbatim() -> None:
    manifest = repository_asset_manifest(REPOSITORY_ROOT)
    assert validate_hash72(manifest["asset_manifest_hash72"])
    assert manifest["english"]["lexeme_count"] > 0
    assert manifest["grammar"]["row_count"] > 0
    assert manifest["grammar"]["verbatim_examples_retained"] is False
    assert len(manifest["wordnet"]) == 8
    assert manifest["verbatim_training_examples_retained"] is False


def test_wordnet_revisable_prior_compiles_to_native_hash216_without_definitions() -> None:
    relation_db = load_wordnet_relations(
        [REPOSITORY_ROOT / "hhs_runtime" / "WordnetAntonyms.csv"], require_all=False
    )
    seed = GenesisSeedBuilder(REPOSITORY_ROOT, relation_db=relation_db).compile(
        ["ability", "abnormal"], use_repository_wordnet=False
    )
    record = seed.to_record()
    assert len(record["hash216"]) == 216
    assert all(validate_hash72(record["hash216"][start:start + 72]) for start in (0, 72, 144))
    assert record["payload"]["wordnet_definitions_retained"] is False
    assert record["payload"]["wordnet_examples_retained"] is False
    assert any(item["relation_type"] == "LEXICAL_ANTONYM" for item in record["payload"]["relations"])
    assert all(item["status"] in (-1, 0, 1) for item in record["payload"]["relations"])


def test_unknown_token_becomes_provisional_object_with_exact_form_neighborhood() -> None:
    seed = GenesisSeedBuilder(REPOSITORY_ROOT, relation_db={}).compile(
        ["abilty"], use_repository_wordnet=False
    )
    distinction = seed.payload["distinctions"][0]
    relations = seed.payload["relations"]
    assert distinction["provisional"] is True
    assert distinction["meaning_status"] == "PROVISIONAL_RELATIONAL_OBJECT"
    assert any(item["relation_type"] == "FORM_SIMILARITY" for item in relations)
    assert all("exact_strength" in item for item in relations if item["relation_type"] == "FORM_SIMILARITY")


class _FakeExactProvider:
    def exact_neighbors(self, token: str, *, top_k: int):
        assert token == "ability"
        assert top_k == 8
        return (
            ExactDistributionalRelation(
                target="skill", sign=1, squared_numerator=9, squared_denominator=10, vector_identity="v" * 64
            ),
        )


def test_exact_distributional_relation_is_reused_as_pass166_typed_evidence() -> None:
    seed = GenesisSeedBuilder(REPOSITORY_ROOT, relation_db={}, word2vec=_FakeExactProvider()).compile(
        ["ability"], use_repository_wordnet=False
    )
    relation = next(item for item in seed.payload["relations"] if item["relation_type"] == "DISTRIBUTIONAL_NEIGHBOR")
    assert relation["status"] == 1
    assert relation["exact_strength"] == {"numerator": 9, "denominator": 10}
    assert relation["provenance"] == "PASS166_EXACT_WORD2VEC"


class _FakePass166Service:
    def nearest(self, token: str, *, model_id: str | None, top_k: int):
        return {"results": [{"token": "skill", "cosine_sign": 1, "cosine_squared_exact": "81/100", "vector_identity": "a" * 64}]}


def test_pass166_adapter_preserves_exact_rational_similarity() -> None:
    relation = Pass166Word2VecAdapter(_FakePass166Service(), model_id="fixture").exact_neighbors("ability", top_k=1)[0]
    assert relation.sign == 1
    assert relation.squared_numerator == 81
    assert relation.squared_denominator == 100


def test_symbolic_identity_and_mythopoetic_analogy_are_separate_seed_types() -> None:
    seed = GenesisSeedBuilder(REPOSITORY_ROOT, relation_db={}).compile(["symbol"], use_repository_wordnet=False)
    assert "IDENTITY" in seed.payload["symbolic_logic_relation_types"]
    assert "ANALOGICAL" in seed.payload["mythopoetic_relation_types"]
    assert seed.payload["mythopoetic_empirical_truth_authority"] is False


def test_genesis_seed_is_byte_deterministic_for_same_inputs() -> None:
    first = GenesisSeedBuilder(REPOSITORY_ROOT, relation_db={}).compile(["ability", "symbol"], use_repository_wordnet=False)
    second = GenesisSeedBuilder(REPOSITORY_ROOT, relation_db={}).compile(["symbol", "ability"], use_repository_wordnet=False)
    assert first.to_record() == second.to_record()


def test_curriculum_manifest_sorts_by_stage_then_locator_and_is_deterministic() -> None:
    genesis = hash72_digest({"domain": "TEST-GENESIS"}, "seed")
    sources = [
        _source("creative", CurriculumStage.CREATIVE_SYNTHESIS, "z/creative.md"),
        _source("reference-b", CurriculumStage.REFERENCE, "b/reference.md"),
        _source("reference-a", CurriculumStage.REFERENCE, "a/reference.md"),
        _source("narrative", CurriculumStage.SIMPLE_NARRATIVE, "n/story.md"),
    ]
    first = build_curriculum_manifest(genesis, sources)
    second = build_curriculum_manifest(genesis, reversed(sources))
    assert first.record() == second.record()
    assert [item["source_id"] for item in first.sources] == ["reference-a", "reference-b", "narrative", "creative"]
    assert validate_hash72(first.manifest_hash72)
    assert validate_hash72(first.curriculum_identity_hash72)


def test_curriculum_identity_changes_when_authority_defining_stage_changes() -> None:
    genesis = hash72_digest({"domain": "TEST-GENESIS"}, "seed")
    reference = _source("item", CurriculumStage.REFERENCE, "source.md")
    narrative = _source("item", CurriculumStage.SIMPLE_NARRATIVE, "source.md")
    assert build_curriculum_manifest(genesis, [reference]).curriculum_identity_hash72 != build_curriculum_manifest(genesis, [narrative]).curriculum_identity_hash72


def test_cursor_rejects_out_of_order_authoritative_promotion() -> None:
    genesis = hash72_digest({"domain": "TEST-GENESIS"}, "seed")
    manifest = build_curriculum_manifest(
        genesis,
        [_source("reference", CurriculumStage.REFERENCE, "reference.md"), _source("narrative", CurriculumStage.SIMPLE_NARRATIVE, "story.md")],
    )
    cursor = CurriculumCursor.for_manifest(manifest)
    with pytest.raises(Pass218CurriculumOrderError, match="P218_OUT_OF_ORDER_AUTHORITATIVE_PROMOTION"):
        cursor.advance(
            manifest,
            source_id="narrative",
            closure_hash72=hash72_digest({"domain": "TEST-CLOSURE"}, "narrative"),
        )


def test_cursor_restart_record_resumes_from_exact_closed_boundary() -> None:
    genesis = hash72_digest({"domain": "TEST-GENESIS"}, "seed")
    manifest = build_curriculum_manifest(
        genesis,
        [_source("reference", CurriculumStage.REFERENCE, "reference.md"), _source("creative", CurriculumStage.CREATIVE_SYNTHESIS, "creative.md")],
    )
    cursor = CurriculumCursor.for_manifest(manifest)
    closure = hash72_digest({"domain": "TEST-CLOSURE"}, "reference")
    advanced, receipt = cursor.advance(manifest, source_id="reference", closure_hash72=closure)
    restored = CurriculumCursor.restore(advanced.record())
    assert restored == advanced
    assert restored.expected_source(manifest)["source_id"] == "creative"
    assert receipt["previous_closure_hash72"] is None
    assert receipt["source_closure_hash72"] == closure
    assert validate_hash72(receipt["transition_hash72"])


def test_authority_adjacent_iteration1_modules_have_no_float_literals() -> None:
    module_root = REPOSITORY_ROOT / "hhs_runtime" / "pass218"
    paths = sorted(module_root.glob("*.py"))
    assert paths
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        float_literals = [node for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, float)]
        assert not float_literals, path
