from __future__ import annotations

import gzip
import hashlib
import zipfile

import numpy as np
import pytest

import hhs_runtime.pass219.lane5_nine_loop_large_artifact_1_69 as large
from hhs_runtime.pass219.lane5_nine_loop_large_artifact_1_69 import (
    EXPECTED_COMPARISON_ROWS,
    EXPECTED_MATRIX_SHAPE,
    Lane5NineLoopLargeArtifactError,
    build_large_artifact_receipt,
    discover_large_artifact_schema,
    derive_public_logical_equivalence,
    inspect_comparison_gzip,
    inspect_npz,
    inspect_zip_metadata,
    parse_manifest,
)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture_set(tmp_path):
    p1 = tmp_path / "E9_symbol_complete_mod2147483647.npz"
    p2 = tmp_path / "E9_symbol_complete_mod2147483629.npz"
    matrix1 = np.zeros(EXPECTED_MATRIX_SHAPE, dtype=np.int64)
    matrix2 = np.zeros(EXPECTED_MATRIX_SHAPE, dtype=np.int64)
    matrix1[0, 0] = 1
    matrix2[0, 0] = 2
    shared_log = np.array("shared-log")
    shared_pivots = np.zeros((424, 5), dtype=np.int64)
    np.savez_compressed(
        p1,
        E0=matrix1,
        L=np.array(9, dtype=np.int64),
        V=np.zeros((424, 5431, 0), dtype=np.int64),
        fix_note=np.array("p1-note"),
        log=shared_log,
        n=np.array(13, dtype=np.int64),
        p=np.array(2147483647, dtype=np.int64),
        pivots=shared_pivots,
        tau_N3LL=np.array([11], dtype=np.int64),
    )
    np.savez_compressed(
        p2,
        E0=matrix2,
        L=np.array(9, dtype=np.int64),
        V=np.zeros((424, 5431, 0), dtype=np.int64),
        fix_note=np.array("p2-note-is-longer"),
        log=shared_log,
        n=np.array(13, dtype=np.int64),
        p=np.array(2147483629, dtype=np.int64),
        pivots=shared_pivots,
        tau_N3LL=np.array([22], dtype=np.int64),
    )

    comparison = tmp_path / "09_septuple_vs_quintuple_107053_words.txt.gz"
    with gzip.open(comparison, "wt", encoding="utf-8") as handle:
        for i in range(EXPECTED_COMPARISON_ROWS):
            handle.write(f"ah bh {i} {i}\n")

    septuple = tmp_path / "MHV9septuples.zip"
    with zipfile.ZipFile(septuple, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("MHV9septuples.txt", "fixture\n")

    manifest = "\n".join(
        [
            f"{_sha(p1)}  amplitude/{p1.name}",
            f"{_sha(p2)}  amplitude/{p2.name}",
            f"{_sha(comparison)}  validation/records/{comparison.name}",
            f"{_sha(septuple)}  MHV9/{septuple.name}",
        ]
    ) + "\n"
    return manifest, p1, p2, comparison, septuple


def test_schema_discovery_preserves_distinct_prime_containers(tmp_path):
    manifest, p1, p2, comparison, septuple = _fixture_set(tmp_path)
    discovery = discover_large_artifact_schema(
        manifest_text=manifest,
        p1_npz=p1,
        p2_npz=p2,
        comparison_gz=comparison,
        septuple_zip=septuple,
    )
    lane1 = discovery["prime_lanes"]["2147483647"]
    lane2 = discovery["prime_lanes"]["2147483629"]
    assert lane1["expected_matrix_shape_verified"] is True
    assert lane2["expected_matrix_shape_verified"] is True
    assert lane1["structure_sha256"] != lane2["structure_sha256"]
    assert discovery["cross_prime_container_identity_required"] is False
    assert discovery["logical_equivalence_contract_frozen"] is False
    assert discovery["comparison"]["comparison_rows"] == EXPECTED_COMPARISON_ROWS
    assert discovery["comparison"]["mismatch_marker_count"] == 0
    assert discovery["septuple_archive"]["archive_extracted"] is False
    assert discovery["candidate_only"] is True
    assert discovery["full_materialization"] is False
    assert discovery["canonical_vm81_mutation_authority"] is False
    assert discovery["canonical_hash216_authority"] is False


def _patch_public_constants(monkeypatch, discovery):
    p1 = discovery["prime_lanes"]["2147483647"]
    a1 = {record["name"]: record for record in p1["arrays"]}
    monkeypatch.setattr(
        large,
        "FROZEN_SOURCE_SHA256",
        {role: record["sha256"] for role, record in discovery["source"].items()},
    )
    monkeypatch.setattr(
        large,
        "FROZEN_SHARED_MEMBER_SHA256",
        {
            name: a1[name]["content_sha256"]
            for name in ("L", "V", "log", "n", "pivots")
        },
    )
    monkeypatch.setattr(
        large,
        "FROZEN_COMPARISON_NORMALIZED_SHA256",
        discovery["comparison"]["normalized_sha256"],
    )
    monkeypatch.setattr(
        large,
        "FROZEN_SEPTUPLE_STRUCTURE_SHA256",
        discovery["septuple_archive"]["structure_sha256"],
    )
    monkeypatch.setattr(large, "EXPECTED_NONZERO_COORDINATE_UNION", 1)


def test_observed_logical_equivalence_allows_prime_dependent_payloads(
    tmp_path, monkeypatch
):
    manifest, p1, p2, comparison, septuple = _fixture_set(tmp_path)
    discovery = discover_large_artifact_schema(
        manifest_text=manifest,
        p1_npz=p1,
        p2_npz=p2,
        comparison_gz=comparison,
        septuple_zip=septuple,
    )
    _patch_public_constants(monkeypatch, discovery)
    relation = derive_public_logical_equivalence(discovery)
    assert relation["logical_equivalence_contract_frozen"] is True
    assert relation["literal_container_identity_required"] is False
    assert relation["native_hash216_composition_frozen"] is False
    assert relation["prime_dependent_members"] == ["E0", "fix_note", "p", "tau_N3LL"]
    assert relation["nonzero_support_sha256"]


def test_logical_equivalence_rejects_different_e0_support(tmp_path, monkeypatch):
    manifest, p1, p2, comparison, septuple = _fixture_set(tmp_path)
    with np.load(p2, allow_pickle=False) as archive:
        payload = {key: archive[key] for key in archive.files}
    moved = np.zeros(EXPECTED_MATRIX_SHAPE, dtype=np.int64)
    moved[0, 1] = 2
    payload["E0"] = moved
    np.savez_compressed(p2, **payload)

    # refresh manifest after the intentional source change
    manifest = "\n".join(
        [
            f"{_sha(p1)}  amplitude/{p1.name}",
            f"{_sha(p2)}  amplitude/{p2.name}",
            f"{_sha(comparison)}  validation/records/{comparison.name}",
            f"{_sha(septuple)}  MHV9/{septuple.name}",
        ]
    ) + "\n"
    discovery = discover_large_artifact_schema(
        manifest_text=manifest,
        p1_npz=p1,
        p2_npz=p2,
        comparison_gz=comparison,
        septuple_zip=septuple,
    )
    _patch_public_constants(monkeypatch, discovery)
    with pytest.raises(Lane5NineLoopLargeArtifactError, match="support geometry"):
        derive_public_logical_equivalence(discovery)


def test_final_equivalence_receipt_cannot_precede_observed_contract(tmp_path):
    manifest, p1, p2, comparison, septuple = _fixture_set(tmp_path)
    with pytest.raises(Lane5NineLoopLargeArtifactError, match="not frozen"):
        build_large_artifact_receipt(
            manifest_text=manifest,
            p1_npz=p1,
            p2_npz=p2,
            comparison_gz=comparison,
            septuple_zip=septuple,
        )


def test_manifest_tamper_fails_closed(tmp_path):
    manifest, p1, p2, comparison, septuple = _fixture_set(tmp_path)
    manifest = manifest.replace(_sha(p1), "00" * 32, 1)
    with pytest.raises(Lane5NineLoopLargeArtifactError, match="SHA-256 mismatch"):
        discover_large_artifact_schema(
            manifest_text=manifest,
            p1_npz=p1,
            p2_npz=p2,
            comparison_gz=comparison,
            septuple_zip=septuple,
        )


def test_wrong_npz_shape_fails_closed(tmp_path):
    bad = tmp_path / "bad.npz"
    np.savez_compressed(bad, matrix=np.zeros((423, 5431), dtype=np.uint8))
    with pytest.raises(Lane5NineLoopLargeArtifactError, match="expected 424 x 5431"):
        inspect_npz(bad)


def test_short_comparison_fails_closed(tmp_path):
    path = tmp_path / "short.txt.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("ah 1 1\n")
    with pytest.raises(Lane5NineLoopLargeArtifactError, match="row count"):
        inspect_comparison_gzip(path)


def test_explicit_mismatch_marker_fails_closed(tmp_path):
    path = tmp_path / "mismatch.txt.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for i in range(EXPECTED_COMPARISON_ROWS - 1):
            handle.write(f"ah {i} {i}\n")
        handle.write("mismatch detected\n")
    with pytest.raises(Lane5NineLoopLargeArtifactError, match="mismatch"):
        inspect_comparison_gzip(path)


def test_unsafe_zip_member_rejected(tmp_path):
    path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../escape.txt", "no")
    with pytest.raises(Lane5NineLoopLargeArtifactError, match="unsafe ZIP"):
        inspect_zip_metadata(path)


def test_manifest_conflicting_duplicate_rejected():
    text = (
        ("11" * 32) + "  amplitude/a.npz\n"
        + ("22" * 32) + "  amplitude/a.npz\n"
    )
    with pytest.raises(Lane5NineLoopLargeArtifactError, match="conflicting duplicate"):
        parse_manifest(text)
