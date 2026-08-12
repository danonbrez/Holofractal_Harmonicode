"""Repository-native evidence emitter for Pass 218 full implementation Iteration 2."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

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


def main() -> None:
    grammar_path = REPOSITORY_ROOT / "hhs_runtime" / "Grammar Correction.csv"
    narrative_path = REPOSITORY_ROOT / "creative_writing" / "novels" / "THE_SMALLEST_PERMISSION.md"

    relation_db = load_wordnet_relations(
        [REPOSITORY_ROOT / "hhs_runtime" / "WordnetAntonyms.csv"],
        require_all=False,
    )
    seed = GenesisSeedBuilder(REPOSITORY_ROOT, relation_db=relation_db).compile(
        ["ability", "abnormal", "authority", "permission", "scope"],
        use_repository_wordnet=False,
    )
    grammar = compile_grammar_rules(grammar_path)

    source_text = narrative_path.read_text("utf-8")
    source_sha256 = sha256(source_text.encode("utf-8")).hexdigest()
    hydration = NarrativeBeatHydrator(paragraphs_per_beat=8).hydrate(
        source_text,
        source_id="the-smallest-permission",
        source_epistemic_class="FICTIONAL_COUNTERFACTUAL",
        genesis_seed=seed,
        grammar_rule_set=grammar,
        expected_source_sha256=source_sha256,
    )

    manifest = build_curriculum_manifest(
        seed.genesis_seed_hash72,
        [
            CurriculumSource(
                source_id="grammar-reference",
                stage=CurriculumStage.REFERENCE,
                locator="hhs_runtime/Grammar Correction.csv",
                checksum_sha256=grammar.source_asset_sha256,
                rights_class="REPOSITORY_NATIVE_REFERENCE",
                source_authority="PASS218_ITERATION2_GRAMMAR",
                media_type="text/csv",
            ),
            CurriculumSource(
                source_id="the-smallest-permission",
                stage=CurriculumStage.SIMPLE_NARRATIVE,
                locator="creative_writing/novels/THE_SMALLEST_PERMISSION.md",
                checksum_sha256=source_sha256,
                rights_class="REPOSITORY_NATIVE_CREATIVE_REFERENCE",
                source_authority="PASS218_ITERATION2_NARRATIVE",
                media_type="text/markdown",
            ),
        ],
        compiler_version="HHS-P218-CURRICULUM-I2-V1",
    )
    cursor = CurriculumCursor.for_manifest(manifest)
    cursor, grammar_receipt = cursor.advance(
        manifest,
        source_id="grammar-reference",
        closure_hash72=grammar.validation_hash72,
    )
    cursor, narrative_receipt = cursor.advance(
        manifest,
        source_id="the-smallest-permission",
        closure_hash72=hydration.validation_hash72,
    )

    record = {
        "classification": "HHS_PASS218_ITERATION2_GRAMMAR_NARRATIVE_HYDRATION_EVIDENCE",
        "genesis_seed_hash72": seed.genesis_seed_hash72,
        "grammar_rule_set_hash72": grammar.rule_set_hash72,
        "grammar_validation_hash72": grammar.validation_hash72,
        "grammar_source_rows": grammar.source_row_count,
        "grammar_rule_count": len(grammar.rules),
        "narrative_source_sha256": hydration.source_sha256,
        "narrative_beat_count": len(hydration.beats),
        "narrative_hydration_hash72": hydration.hydration_hash72,
        "narrative_validation_hash72": hydration.validation_hash72,
        "candidate_hash216": hydration.hash216,
        "candidate_hash216_valid": (
            len(hydration.hash216) == 216
            and all(validate_hash72(hydration.hash216[start:start + 72]) for start in (0, 72, 144))
        ),
        "hash216_semantics": [
            "PREVIOUS_GENESIS_STATE",
            "NEXT_HYDRATION_CANDIDATE",
            "VALIDATION_RECEIPT",
        ],
        "curriculum_manifest_hash72": manifest.manifest_hash72,
        "curriculum_identity_hash72": manifest.curriculum_identity_hash72,
        "grammar_transition_hash72": grammar_receipt["transition_hash72"],
        "narrative_transition_hash72": narrative_receipt["transition_hash72"],
        "cursor_complete": cursor.expected_source(manifest) is None,
        "verbatim_source_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "authoritative_vector_store_promotion": False,
        "authoritative_float_weights": False,
    }
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
