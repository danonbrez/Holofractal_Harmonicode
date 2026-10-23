from __future__ import annotations

import copy
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i079_harmonicode_trilayer_proof_hydration_v1 import (
    AUTHORITY_BOUNDARY,
    GOOD_CLOSED_FRAGMENT,
    Pass220I079Error,
    REPO_ROOT,
    SOURCE_A_GIT_BLOB_SHA,
    SOURCE_A_PATH,
    SOURCE_B_GIT_BLOB_SHA,
    SOURCE_B_PATH,
    VM81_SYMBOLS,
    _git_blob_sha,
    build_candidate,
    reconstruct_verbatim,
    self_test,
    symbol_address_witness,
    validate_candidate,
    verbatim_layer,
)


def test_verbatim_sources_are_git_blob_bound_and_reconstruct_exactly() -> None:
    layer = verbatim_layer()
    source_a = (REPO_ROOT / SOURCE_A_PATH).read_bytes()
    source_b = (REPO_ROOT / SOURCE_B_PATH).read_bytes()

    assert _git_blob_sha(source_a) == SOURCE_A_GIT_BLOB_SHA
    assert _git_blob_sha(source_b) == SOURCE_B_GIT_BLOB_SHA
    assert layer["sources"]["A"]["text"] == source_a.decode("utf-8")
    assert layer["sources"]["B"]["text"] == source_b.decode("utf-8")
    assert layer["source_replacement_allowed"] is False


def test_tri_layer_hash216_is_verbatim_reduction_proof_in_order() -> None:
    candidate = build_candidate()
    lanes = candidate["hash72_lanes"]

    assert tuple(lanes) == ("verbatim", "reduction", "proof_reconstruction")
    assert all(len(value) == 72 for value in lanes.values())
    assert candidate["candidate_hash216"] == (
        lanes["verbatim"] + lanes["reduction"] + lanes["proof_reconstruction"]
    )
    assert len(candidate["candidate_hash216"]) == 216
    assert candidate["hydration"]["roundtrip_exact"] is True
    assert candidate["hydration"]["full_attached_components"] == 15552


def test_reduction_nodes_are_exact_source_spans_not_replacements() -> None:
    candidate = build_candidate()
    source_a, source_b = reconstruct_verbatim(candidate)
    sources = {"A": source_a, "B": source_b}

    spans = candidate["layers"]["reduction"]["source_span_witnesses"]
    assert len(spans) == 8

    for span in spans:
        source = sources[span["source_key"]]
        extracted = source[
            span["start_character"] : span["end_character_exclusive"]
        ]
        assert extracted == span["marker"]
        assert span["derived_view_only"] is True
        assert span["source_replacement_allowed"] is False

    assert candidate["layers"]["proof"]["same_proof_binds_both_layers"] is True
    assert (
        candidate["layers"]["proof"]["reconstruction"]["source_bytes_retained"]
        is True
    )


def test_scalar_looking_symbols_are_positional_vm81_bigint_objects() -> None:
    addresses = symbol_address_witness()

    assert len(VM81_SYMBOLS) == len(addresses) == 24
    assert tuple(row["cell81"] for row in addresses) == tuple(range(24))
    assert len({row["symbol"] for row in addresses}) == 24

    blocks = []
    for row in addresses:
        assert row["bigint_5184_block_start"] == 64 * row["cell81"]
        assert row["bigint_5184_block_end_exclusive"] == 64 * (
            row["cell81"] + 1
        )
        assert row["bigint_5184_block_width"] == 64
        assert row["within_cell_operation_selector"] == "PRESERVED_BY_CONSTRUCTOR"
        assert row["uniform_scalar_identity"] is False
        assert row["lo_shu_nucleus_reference_required"] is True
        blocks.append(
            (
                row["bigint_5184_block_start"],
                row["bigint_5184_block_end_exclusive"],
            )
        )

    assert len(set(blocks)) == 24
    assert blocks[0] == (0, 64)
    assert blocks[-1] == (1472, 1536)


def test_a2_known_lo_shu_anchor_is_preserved_without_inventing_other_anchors() -> None:
    candidate = build_candidate()
    anchor = candidate["layers"]["reduction"]["lo_shu_nucleus_anchor"]

    assert anchor["symbol"] == "a2"
    assert anchor["scalar_projection"] == 1
    assert anchor["lo_shu_value"] == 1
    assert anchor["lo_shu_position_1based"] == (3, 2)
    assert anchor["lo_shu_local_index_0based"] == 7
    assert anchor["scope"] == "SOURCE_PROVED_POSITIONAL_ANCHOR_ONLY"


def test_hnan_and_good_closed_are_typed_inherited_constraints() -> None:
    candidate = build_candidate()
    proof = candidate["layers"]["proof"]

    assert proof["hnan_inheritance"]["native_hnan_gate"] is True
    assert proof["hnan_inheritance"]["i074_closure_readout"] == "1_H"
    assert proof["ethical_attractor"]["binding"] == GOOD_CLOSED_FRAGMENT
    assert proof["ethical_attractor"]["typed_correspondence_only"] is True
    assert proof["ethical_attractor"]["scalar_orbital_variable"] is False
    assert proof["no_translation_without_computational_proof"] is True


def test_authority_remains_fail_closed_and_candidate_only() -> None:
    candidate = build_candidate()

    assert candidate["authority"] == AUTHORITY_BOUNDARY
    assert candidate["authority"]["candidate_only"] is True
    assert candidate["authority"]["reduction_is_derived_view_only"] is True
    assert candidate["authority"]["canonical_vm81_mutation_authority"] is False
    assert candidate["authority"]["canonical_hash72_commit_authority"] is False
    assert candidate["authority"]["canonical_hash216_commit_authority"] is False
    assert (
        candidate["authority"]["canonical_hash216_persistence_authority"]
        is False
    )
    assert candidate["authority"]["host_float_arithmetic_authority"] is False


def test_tampered_candidate_fails_closed() -> None:
    candidate = build_candidate()
    tampered = copy.deepcopy(candidate)
    tampered["layers"]["reduction"]["address_law"] = "scalarized"

    with pytest.raises(Pass220I079Error):
        validate_candidate(tampered)


def test_self_test_passes() -> None:
    report = self_test()

    assert report["status"] == "PASS"
    assert report["check_count"] == report["pass_count"] == 20
    assert report["failed"] == []
    assert len(report["binding_hash72"]) == 72
    assert len(report["candidate_hash216"]) == 216
