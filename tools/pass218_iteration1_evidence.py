"""Emit bounded Pass 218 Iteration 1 repository-native evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations
from hhs_runtime.pass218 import CurriculumCursor, CurriculumSource, CurriculumStage, GenesisSeedBuilder, build_curriculum_manifest


def main() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    relation_db = load_wordnet_relations(
        [repository_root / "hhs_runtime" / "WordnetAntonyms.csv"], require_all=False
    )
    seed = GenesisSeedBuilder(repository_root, relation_db=relation_db).compile(
        ["ability", "able", "abnormal"], use_repository_wordnet=False
    )

    def source(source_id: str, stage: CurriculumStage, relative_path: str) -> CurriculumSource:
        raw = (repository_root / relative_path).read_bytes()
        return CurriculumSource(
            source_id=source_id,
            stage=stage,
            locator=relative_path,
            checksum_sha256=sha256(raw).hexdigest(),
            rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
            source_authority="PASS218_ITERATION1_EVIDENCE",
            media_type="text/plain",
        )

    manifest = build_curriculum_manifest(
        seed.genesis_seed_hash72,
        [
            source("reference-english", CurriculumStage.REFERENCE, "hhs_runtime/English_Word_List.txt"),
            source("expository-vm81", CurriculumStage.EXPOSITORY, "hhs_runtime/HARMONICODE_HHS_VM81_PROGRAMMING_GUIDE.md"),
            source("creative-invariant-keeper", CurriculumStage.CREATIVE_SYNTHESIS, "creative_writing/the_invariant_keeper/chapter_01_the_reconciliation_desk.md"),
        ],
    )
    cursor = CurriculumCursor.for_manifest(manifest)
    transition_roots: list[str] = []
    for item in manifest.sources:
        closure = hash72_digest(
            {"domain": "HHS-P218-I1-EVIDENCE-SOURCE-CLOSURE"},
            {"source_id": item["source_id"], "checksum_sha256": item["checksum_sha256"]},
        )
        cursor, receipt = cursor.advance(manifest, source_id=item["source_id"], closure_hash72=closure)
        transition_roots.append(receipt["transition_hash72"])

    print(json.dumps({
        "classification": "HHS_PASS218_ITERATION1_GENESIS_CURRICULUM_EVIDENCE",
        "seed_hash216": seed.hash216,
        "genesis_seed_hash72": seed.genesis_seed_hash72,
        "asset_manifest_hash72": seed.hash216[:72],
        "curriculum_manifest_hash72": manifest.manifest_hash72,
        "curriculum_identity_hash72": manifest.curriculum_identity_hash72,
        "ordered_source_ids": [item["source_id"] for item in manifest.sources],
        "transition_hash72_roots": transition_roots,
        "cursor_complete": cursor.expected_source(manifest) is None,
        "wordnet_antonym_relations": sum(1 for item in seed.payload["relations"] if item["relation_type"] == "LEXICAL_ANTONYM"),
        "authoritative_float_weights": seed.payload["authoritative_float_weights"],
        "grammar_rule_compilation_status": seed.payload["grammar_seed"]["rule_compilation_status"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
