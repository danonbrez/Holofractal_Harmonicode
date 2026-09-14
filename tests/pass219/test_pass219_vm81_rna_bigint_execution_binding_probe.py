from __future__ import annotations

import os

import pytest

from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    GLYPH_WORD_START,
    METADATA_WORD_INDEX,
    VM81RNABigIntExecutionBindingProbeError,
    build_execution_cases,
    pack_vm81_binding_words,
    raw_le_to_words,
    unpack_vm81_binding_words,
    vm81_rna_bigint_execution_binding_probe,
    words_to_raw_le,
)


def test_all_twelve_directional_views_preserve_one_bigint_and_typed_metadata() -> None:
    cases = build_execution_cases()
    assert len(cases) == 12
    assert [row["opcode"] for row in cases] == list(range(12))
    assert len({row["bigint"] for row in cases}) == 1
    assert len({row["raw_sha256"] for row in cases}) == 12
    for row in cases:
        restored = row["restored"]
        assert restored["bigint"] == row["bigint"]
        assert restored["metadata"] == {
            "opcode": row["opcode"],
            "lane": row["lane"],
            "direction": row["direction"],
            "source": row["source"],
            "target": row["target"],
        }
        assert len(restored["glyph_stream"]) == 72
        assert len(restored["phase_digits"]) == 72
        assert len(restored["qudit_digits"]) == 72
        assert len(row["raw_bytes"]) == 648
        assert words_to_raw_le(raw_le_to_words(row["raw_bytes"])) == row["raw_bytes"]


def test_glyph_tamper_is_rejected_against_embedded_bigint_identity() -> None:
    case = build_execution_cases()[0]
    words = list(raw_le_to_words(case["raw_bytes"]))
    words[GLYPH_WORD_START] = (words[GLYPH_WORD_START] + 1) % 72
    with pytest.raises(
        VM81RNABigIntExecutionBindingProbeError,
        match="VM81_BIGINT_GLYPH_CROSSCHECK_FAILED",
    ):
        unpack_vm81_binding_words(words)


def test_bigint_limb_tamper_is_rejected_against_glyph_stream() -> None:
    case = build_execution_cases()[0]
    words = list(raw_le_to_words(case["raw_bytes"]))
    words[0] ^= 1
    with pytest.raises(
        VM81RNABigIntExecutionBindingProbeError,
        match="VM81_BIGINT_GLYPH_CROSSCHECK_FAILED",
    ):
        unpack_vm81_binding_words(words)


def test_metadata_reserved_bits_and_opcode_lane_mismatch_are_rejected() -> None:
    case = build_execution_cases()[0]
    words = list(raw_le_to_words(case["raw_bytes"]))
    words[METADATA_WORD_INDEX] |= 1 << 48
    with pytest.raises(
        VM81RNABigIntExecutionBindingProbeError,
        match="METADATA_RESERVED_BITS_NONZERO",
    ):
        unpack_vm81_binding_words(words)

    bad_row = {
        "opcode": 0,
        "lane": 1,
        "direction": "pq",
        "source": "S00",
        "target": "S10",
    }
    with pytest.raises(
        VM81RNABigIntExecutionBindingProbeError,
        match="OPCODE_LANE_MISMATCH",
    ):
        pack_vm81_binding_words(
            case["bigint"],
            case["restored"]["glyph_stream"],
            bad_row,
        )


def test_native_cpp_rna_route_preserves_binding_and_authority_when_available() -> None:
    native_probe = os.environ.get("HHS_PASS219_BIGINT_RNA_NATIVE_PROBE")
    if not native_probe:
        pytest.skip("focused native probe executable not supplied")
    report = vm81_rna_bigint_execution_binding_probe(native_probe)
    assert report["assembly_identity"]["all_typed_frames_round_trip"] is True
    assert report["assembly_identity"]["all_typed_frames_have_distinct_raw_identity"] is True
    assert report["assembly_identity"]["same_bigint_preserved_across_twelve_directional_views"] is True
    assert report["native_execution"]["case_count"] == 12
    assert report["native_execution"]["all_native_candidate_routes_green"] is True
    assert report["binding_result"] == {
        "decode_to_vm5184_exact": True,
        "native_rna_candidate_execution_exact": True,
        "reencode_preserves_bigint_identity": True,
        "typed_six_lane_pq_qp_identity_preserved": True,
        "hash216_receipt_ancestry_preserved": True,
        "existing_cpp_rna_route_reused": True,
        "new_mutation_primitive_required": False,
        "new_receipt_primitive_required": False,
        "canonical_execution_promotion_claimed": False,
    }
    for row in report["native_execution"]["rows"]:
        assert row["deterministic_repeat_exact"] is True
        assert row["raw_unchanged"] is True
        assert row["import_export_exact"] is True
        assert row["hash216_reference_verified"] is True
        assert row["transition_identity_preserved"] is True
        assert row["authority_closed"] is True
        assert row["word_visits"] == 81
        assert row["graph_edge_visits"] == 1620
        assert 0 <= row["selected_lane"] < 4
