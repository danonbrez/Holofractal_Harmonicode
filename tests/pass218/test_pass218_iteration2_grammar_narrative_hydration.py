from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations
from hhs_runtime.pass218 import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    GenesisSeedBuilder,
    NarrativeBeatHydrator,
    build_curriculum_manifest,
    compile_grammar_rules,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GRAMMAR_PATH = REPOSITORY_ROOT / "hhs_runtime" / "Grammar Correction.csv"
NARRATIVE_PATH = REPOSITORY_ROOT / "creative_writing" / "novels" / "THE_SMALLEST_PERMISSION.md"


def _seed():
    relation_db = load_wordnet_relations(
        [REPOSITORY_ROOT / "hhs_runtime" / "WordnetAntonyms.csv"],
        require_all=False,
    )
    return GenesisSeedBuilder(REPOSITORY_ROOT, relation_db=relation_db).compile(
        ["ability", "abnormal", "authority", "permission", "scope"],
        use_repository_wordnet=False,
    )


def test_grammar_corpus_compiles_to_structural_nonverbatim_rules() -> None:
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    record = rule_set.to_record()
    serialized = json.dumps(record, sort_keys=True)
    assert record["source_row_count"] > 0
    assert len(record["rules"]) > 0
    assert record["verbatim_examples_retained"] is False
    assert record["authoritative_float_weights"] is False
    assert "I goes to the store everyday." not in serialized
    assert "I go to the store everyday." not in serialized
    assert all(rule["support_count"] > 0 for rule in record["rules"])
    assert all(rule["verbatim_examples_retained"] is False for rule in record["rules"])
    assert validate_hash72(record["rule_set_hash72"])
    assert validate_hash72(record["validation_hash72"])


def test_grammar_rule_compilation_is_byte_deterministic() -> None:
    first = compile_grammar_rules(GRAMMAR_PATH)
    second = compile_grammar_rules(GRAMMAR_PATH)
    assert first.to_record() == second.to_record()


def test_grammar_rule_identity_binds_source_asset(tmp_path: Path) -> None:
    first_path = tmp_path / "first.csv"
    second_path = tmp_path / "second.csv"
    header = "Serial Number,Error Type,Ungrammatical Statement,Standard English\n"
    first_path.write_text(header + "1,Agreement,They was ready.,They were ready.\n", encoding="utf-8")
    second_path.write_text(header + "1,Agreement,They is ready.,They are ready.\n", encoding="utf-8")
    first = compile_grammar_rules(first_path)
    second = compile_grammar_rules(second_path)
    assert first.source_asset_sha256 != second.source_asset_sha256
    assert first.rule_set_hash72 != second.rule_set_hash72


def test_grammar_compiler_emits_explicit_edit_rule_objects() -> None:
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    edit_kinds = {rule.edit_kind for rule in rule_set.rules}
    assert edit_kinds
    assert edit_kinds <= {
        "CASE_NORMALIZATION",
        "CONTRACTION_FORM_CHANGE",
        "MORPHOLOGICAL_FORM_CHANGE",
        "LEXICAL_SUBSTITUTION_SHAPE",
        "SPAN_REPLACEMENT",
        "TOKEN_DELETION",
        "TOKEN_INSERTION",
    }
    assert any(rule.source_shapes or rule.target_shapes for rule in rule_set.rules)


def test_narrative_hydration_emits_nonverbatim_hash216_candidate() -> None:
    seed = _seed()
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    source = NARRATIVE_PATH.read_text("utf-8")
    candidate = NarrativeBeatHydrator(paragraphs_per_beat=5).hydrate(
        source,
        source_id="the-smallest-permission",
        source_epistemic_class="FICTIONAL_COUNTERFACTUAL",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
        expected_source_sha256=sha256(source.encode("utf-8")).hexdigest(),
    )
    record = candidate.to_record()
    assert len(record["hash216"]) == 216
    assert record["hash216"] == (
        seed.genesis_seed_hash72 + candidate.hydration_hash72 + candidate.validation_hash72
    )
    assert all(validate_hash72(record["hash216"][start:start + 72]) for start in (0, 72, 144))
    assert record["verbatim_source_retained"] is False
    assert record["source_text_retained"] is False
    assert record["truth_promotion"] is False
    assert record["action_authority_minted"] is False
    assert record["authoritative_vector_store_promotion"] is False
    assert len(record["beats"]) > 0


def test_narrative_candidate_does_not_retain_source_sentence() -> None:
    seed = _seed()
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    source = "Aster lanterns negotiate impossible violet doorways. The witness cannot authorize the gate."
    candidate = NarrativeBeatHydrator(paragraphs_per_beat=2).hydrate(
        source,
        source_id="nonverbatim-fixture",
        source_epistemic_class="FICTIONAL_TEST",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
    )
    serialized = json.dumps(candidate.to_record(), sort_keys=True).casefold()
    for fragment in ("aster", "lanterns", "negotiate", "violet", "doorways", "witness", "gate"):
        assert fragment not in serialized


def test_narrative_hydration_links_known_lexemes_by_distinction_id_only() -> None:
    seed = _seed()
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    source = "Permission limits authority. Authority narrows scope."
    candidate = NarrativeBeatHydrator().hydrate(
        source,
        source_id="distinction-link-fixture",
        source_epistemic_class="FICTIONAL_TEST",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
    )
    mentions = [
        item
        for beat in candidate.to_record()["beats"]
        for item in beat["distinction_mentions"]
    ]
    assert mentions
    assert all(validate_hash72(item["distinction_id_hash72"]) for item in mentions)
    assert all(set(item) == {"distinction_id_hash72", "count"} for item in mentions)


def test_narrative_structural_beats_preserve_perspective_and_constraint_relations() -> None:
    seed = _seed()
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    source = 'I cannot grant permission now. "You should wait," she said. Then they narrowed the scope.'
    candidate = NarrativeBeatHydrator().hydrate(
        source,
        source_id="perspective-fixture",
        source_epistemic_class="FICTIONAL_TEST",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
    )
    beat = candidate.beats[0]
    assert beat.negation_count > 0
    assert beat.modal_count > 0
    assert beat.authority_count > 0
    assert beat.temporal_count > 0
    assert "AUTHORITY_SCOPE" in beat.relation_types
    assert "MODAL_CONSTRAINT" in beat.relation_types
    assert "NEGATION_PRESSURE" in beat.relation_types
    assert "TEMPORAL_SUCCESSION" in beat.relation_types


def test_narrative_hydration_is_deterministic_for_exact_source() -> None:
    seed = _seed()
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    source = NARRATIVE_PATH.read_text("utf-8")
    hydrator = NarrativeBeatHydrator(paragraphs_per_beat=7)
    first = hydrator.hydrate(
        source,
        source_id="determinism",
        source_epistemic_class="FICTIONAL_COUNTERFACTUAL",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
    )
    second = hydrator.hydrate(
        source,
        source_id="determinism",
        source_epistemic_class="FICTIONAL_COUNTERFACTUAL",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
    )
    assert first.to_record() == second.to_record()


def test_narrative_source_mutation_changes_candidate_transition() -> None:
    seed = _seed()
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    hydrator = NarrativeBeatHydrator()
    first = hydrator.hydrate(
        "Permission is narrow.",
        source_id="mutation",
        source_epistemic_class="FICTIONAL_TEST",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
    )
    second = hydrator.hydrate(
        "Permission is deliberately narrow.",
        source_id="mutation",
        source_epistemic_class="FICTIONAL_TEST",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
    )
    assert first.source_sha256 != second.source_sha256
    assert first.hydration_hash72 != second.hydration_hash72
    assert first.hash216 != second.hash216


def test_narrative_checksum_mismatch_is_rejected() -> None:
    seed = _seed()
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    with pytest.raises(ValueError, match="P218_NARRATIVE_SOURCE_CHECKSUM_MISMATCH"):
        NarrativeBeatHydrator().hydrate(
            "Permission is narrow.",
            source_id="checksum",
            source_epistemic_class="FICTIONAL_TEST",
            genesis_seed=seed,
            grammar_rule_set=rule_set,
            expected_source_sha256="0" * 64,
        )


def test_grammar_then_narrative_close_in_curriculum_order() -> None:
    seed = _seed()
    rule_set = compile_grammar_rules(GRAMMAR_PATH)
    source = "Permission constrains authority."
    source_sha = sha256(source.encode("utf-8")).hexdigest()
    candidate = NarrativeBeatHydrator().hydrate(
        source,
        source_id="narrative",
        source_epistemic_class="FICTIONAL_TEST",
        genesis_seed=seed,
        grammar_rule_set=rule_set,
        expected_source_sha256=source_sha,
    )
    manifest = build_curriculum_manifest(
        seed.genesis_seed_hash72,
        [
            CurriculumSource(
                source_id="grammar-reference",
                stage=CurriculumStage.REFERENCE,
                locator="hhs_runtime/Grammar Correction.csv",
                checksum_sha256=rule_set.source_asset_sha256,
                rights_class="REPOSITORY_NATIVE_REFERENCE",
                source_authority="PASS218_ITERATION2_GRAMMAR",
                media_type="text/csv",
            ),
            CurriculumSource(
                source_id="narrative",
                stage=CurriculumStage.SIMPLE_NARRATIVE,
                locator="fixture://narrative",
                checksum_sha256=source_sha,
                rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
                source_authority="PASS218_ITERATION2_NARRATIVE",
                media_type="text/plain",
            ),
        ],
    )
    cursor = CurriculumCursor.for_manifest(manifest)
    cursor, grammar_receipt = cursor.advance(
        manifest,
        source_id="grammar-reference",
        closure_hash72=rule_set.validation_hash72,
    )
    cursor, narrative_receipt = cursor.advance(
        manifest,
        source_id="narrative",
        closure_hash72=candidate.validation_hash72,
    )
    assert cursor.expected_source(manifest) is None
    assert validate_hash72(grammar_receipt["transition_hash72"])
    assert validate_hash72(narrative_receipt["transition_hash72"])
    assert narrative_receipt["previous_closure_hash72"] == rule_set.validation_hash72


def test_iteration2_authority_adjacent_modules_have_no_float_literals() -> None:
    module_root = REPOSITORY_ROOT / "hhs_runtime" / "pass218"
    for path in sorted(module_root.glob("*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
