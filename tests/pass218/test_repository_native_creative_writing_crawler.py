from __future__ import annotations

import json
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218_native_corpus_crawler import (
    DEFAULT_CREATIVE_WRITING_ROOT,
    CrawlPolicy,
    Pass218PolicyError,
    Pass218ReferenceCrawler,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
NATIVE_CREATIVE_ROOT = REPOSITORY_ROOT / DEFAULT_CREATIVE_WRITING_ROOT
FIRST_CHAPTER = NATIVE_CREATIVE_ROOT / "chapter_01_the_reconciliation_desk.md"


def new_crawler() -> Pass218ReferenceCrawler:
    return Pass218ReferenceCrawler(REPOSITORY_ROOT)


def test_repository_native_creative_writing_folder_exists() -> None:
    assert NATIVE_CREATIVE_ROOT.is_dir()
    assert FIRST_CHAPTER.is_file()


def test_discovery_is_deterministic_sorted_and_allowlisted() -> None:
    crawler = new_crawler()
    first = [crawler._relative_path(path) for path in crawler.discover()]
    second = [crawler._relative_path(path) for path in crawler.discover()]

    assert first == second
    assert first == sorted(first)
    assert len(first) >= 10
    assert (
        "creative_writing/the_invariant_keeper/"
        "chapter_01_the_reconciliation_desk.md"
    ) in first
    assert all(path.startswith(f"{DEFAULT_CREATIVE_WRITING_ROOT}/") for path in first)
    assert all(path.endswith(".md") for path in first)


def test_skip_is_default_outside_allowlist() -> None:
    decision = new_crawler().triage(REPOSITORY_ROOT / "README.md")
    assert decision["route"] == "SKIPPED"
    assert decision["reason"] == "OUTSIDE_ALLOWLIST"


def test_reference_record_uses_native_hash216_and_blocks_promotion() -> None:
    record = new_crawler().crawl_file(FIRST_CHAPTER)

    assert record["status"] == "CLOSED"
    assert record["promotion_eligible"] is False
    assert record["abstraction"]["authoritative_semantic_promotion"] is False
    assert len(record["hash216"]) == 216
    assert validate_hash72(record["hash216"][:72])
    assert validate_hash72(record["hash216"][72:144])
    assert validate_hash72(record["hash216"][144:])
    assert record["hash216"] == (
        record["source_hash72"]
        + record["abstraction_hash72"]
        + record["receipt_hash72"]
    )


def test_style_vector_contains_required_measurable_dimensions() -> None:
    record = new_crawler().crawl_file(FIRST_CHAPTER)
    vector = record["abstraction"]["style_vector"]

    required = {
        "alliteration_adjacent_pair_density",
        "assonance_adjacent_pair_density_proxy",
        "rhythm_phrase_syllable_variance_proxy",
        "median_word_length",
        "median_word_length_per_phrase",
        "vocabulary_type_token_ratio",
        "vocabulary_long_word_ratio",
        "rhyme_scheme_pattern",
        "meter_profile_status",
        "mythology_temperature",
        "poetic_temperature_scalar",
    }
    assert required.issubset(vector)
    assert vector["word_count"] > 0
    assert vector["sentence_count"] > 0
    assert vector["phrase_count"] > 0
    assert 0.0 <= vector["alliteration_adjacent_pair_density"] <= 1.0
    assert 0.0 <= vector["assonance_adjacent_pair_density_proxy"] <= 1.0
    assert 0.0 <= vector["vocabulary_type_token_ratio"] <= 1.0
    assert vector["mythology_temperature"] is None
    assert vector["poetic_temperature_scalar"] is None


def test_retained_record_contains_no_verbatim_fields_or_long_source_span() -> None:
    record = new_crawler().crawl_file(FIRST_CHAPTER)
    serialized = json.dumps(record, sort_keys=True)
    forbidden_keys = {
        '"content"',
        '"raw"',
        '"raw_bytes"',
        '"source_content"',
        '"source_text"',
        '"text"',
        '"tokens"',
        '"verbatim"',
    }
    assert not any(key in serialized for key in forbidden_keys)

    source = FIRST_CHAPTER.read_text(encoding="utf-8")
    long_lines = [
        " ".join(line.split())
        for line in source.splitlines()
        if len(" ".join(line.split())) >= 64
    ]
    assert long_lines
    assert all(line[:64] not in serialized for line in long_lines)


def test_folder_crawl_closes_each_file_before_advancing_and_chains_receipts() -> None:
    records = new_crawler().crawl_folder()
    closed = [record for record in records if record["status"] == "CLOSED"]

    assert closed
    assert all(
        record["status"] in {"CLOSED", "SKIP_DUPLICATE"} for record in records
    )
    assert all(record["state_trace"][-1] == "CLOSED" for record in closed)
    assert all(
        record["state_trace"].index("CANDIDATE_COMMITTED")
        < record["state_trace"].index("VERBATIM_PURGED")
        < record["state_trace"].index("CLOSED")
        for record in closed
    )
    for previous, current in zip(closed, closed[1:]):
        assert current["parent_closure_hash72"] == previous["closure_hash72"]


def test_clean_repeated_crawl_is_byte_deterministic() -> None:
    first = Pass218ReferenceCrawler(REPOSITORY_ROOT).crawl_file(FIRST_CHAPTER)
    second = Pass218ReferenceCrawler(REPOSITORY_ROOT).crawl_file(FIRST_CHAPTER)
    assert first == second


def test_duplicate_checksum_gets_compact_skip_receipt(tmp_path: Path) -> None:
    allowlisted = tmp_path / "creative"
    allowlisted.mkdir()
    first = allowlisted / "one.md"
    second = allowlisted / "two.md"
    first.write_text("Same bounded creative fixture.", encoding="utf-8")
    second.write_text("Same bounded creative fixture.", encoding="utf-8")

    crawler = Pass218ReferenceCrawler(
        tmp_path,
        CrawlPolicy(allowlisted_roots=("creative",)),
    )
    first_record = crawler.crawl_file(first)
    second_record = crawler.crawl_file(second)

    assert first_record["status"] == "CLOSED"
    assert second_record["status"] == "SKIP_DUPLICATE"
    assert "hash216" not in second_record
    assert len(second_record["skip_receipt_sha256"]) == 64


def test_unsupported_extension_is_skipped_before_extraction(tmp_path: Path) -> None:
    allowlisted = tmp_path / "creative"
    allowlisted.mkdir()
    candidate = allowlisted / "payload.bin"
    candidate.write_bytes(b"\x00\x01\x02")

    crawler = Pass218ReferenceCrawler(
        tmp_path,
        CrawlPolicy(allowlisted_roots=("creative",)),
    )
    decision = crawler.triage(candidate)
    record = crawler.crawl_file(candidate)

    assert decision["route"] == "SKIPPED"
    assert decision["reason"] == "UNSUPPORTED_SUFFIX"
    assert record["status"] == "SKIPPED"
    assert "hash216" not in record


def test_oversized_source_is_skipped_before_hydration(tmp_path: Path) -> None:
    allowlisted = tmp_path / "creative"
    allowlisted.mkdir()
    candidate = allowlisted / "large.md"
    candidate.write_text("x" * 32, encoding="utf-8")

    crawler = Pass218ReferenceCrawler(
        tmp_path,
        CrawlPolicy(
            allowlisted_roots=("creative",),
            max_file_bytes=8,
        ),
    )
    decision = crawler.triage(candidate)

    assert decision["route"] == "SKIPPED"
    assert decision["reason"] == "SIZE_LIMIT"


def test_symlink_escape_is_skipped_when_supported(tmp_path: Path) -> None:
    allowlisted = tmp_path / "creative"
    allowlisted.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("Outside source.", encoding="utf-8")
    link = allowlisted / "escape.md"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable in this environment")

    crawler = Pass218ReferenceCrawler(
        tmp_path,
        CrawlPolicy(allowlisted_roots=("creative",)),
    )
    decision = crawler.triage(link)

    assert decision["route"] == "SKIPPED"
    assert decision["reason"] == "SYMLINK_OR_ESCAPE"


def test_missing_allowlisted_root_fails_closed(tmp_path: Path) -> None:
    crawler = Pass218ReferenceCrawler(
        tmp_path,
        CrawlPolicy(allowlisted_roots=("missing",)),
    )
    with pytest.raises(Pass218PolicyError, match="P218_ALLOWLISTED_CRAWL_ROOT_MISSING"):
        crawler.discover("missing")


def test_reference_grounding_inventory_cannot_be_mistaken_for_hydration() -> None:
    record = new_crawler().crawl_file(FIRST_CHAPTER)
    grounding = record["abstraction"]["grounding_inventory"]

    assert grounding["wordnet_csv_inventory_count"] > 0
    assert grounding["wordnet_sense_disambiguation_complete"] is False
    assert grounding["word2vec_distributional_hydration_complete"] is False
    assert grounding["open_weight_contextual_hydration_complete"] is False
    assert grounding["user_perspective_semantic_validation_complete"] is False
    assert grounding["authoritative_semantic_promotion_ready"] is False
    assert record["receipt_payload"]["validators"]["grounding_promotion_ready"] is False
