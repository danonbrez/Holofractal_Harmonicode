from __future__ import annotations

from hashlib import sha256, shake_256
from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
    AFFINE_SEED_BYTES,
    FULL_HYDRATION_BYTES,
    apply_bit_exceptions,
    generate_affine_hydration,
)
from hhs_backend.runtime.hhs_pass215_iteration1_transformer_ingestion_v1 import (
    FROZEN_PROFILE_GIT_BLOB_SHA1,
    MANIFEST_SCHEMA,
    Pass215Iteration1ValidationError,
    TIER_1,
    TIER_2,
    TIER_3,
    build_incidence_evidence,
    expected_tensor_bytes,
    validate_incidence_evidence,
    validate_manifest,
)


def _manifest(path: str, raw: bytes) -> dict:
    return {
        "schema": MANIFEST_SCHEMA,
        "model_id": "pass215-i1-deterministic-transformer-shaped-fixture",
        "source": {
            "kind": "repository_generated_fixture",
            "real_open_transformer": False,
        },
        "tensors": [
            {
                "name": "layers.0.attention.qkv.weight",
                "dtype": "uint8",
                "shape": [len(raw)],
                "path": path,
                "offset_bytes": 0,
                "length_bytes": len(raw),
                "sha256": sha256(raw).hexdigest(),
            }
        ],
    }


def test_expected_quantized_tensor_bytes() -> None:
    assert expected_tensor_bytes("qint4", [3]) == 2
    assert expected_tensor_bytes("quint4", [16, 2]) == 16
    assert expected_tensor_bytes("int8", [7, 9]) == 63
    assert expected_tensor_bytes("int16", [7, 9]) == 126
    with pytest.raises(Pass215Iteration1ValidationError, match="DTYPE_UNSUPPORTED"):
        expected_tensor_bytes("float16", [8])


def test_float_canonical_input_is_rejected() -> None:
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "model_id": "bad-float",
        "quantization": {"scale": 0.5},
        "tensors": [
            {
                "name": "w",
                "dtype": "int8",
                "shape": [1],
                "path": "w.bin",
                "length_bytes": 1,
            }
        ],
    }
    with pytest.raises(Pass215Iteration1ValidationError, match="FLOAT_FORBIDDEN"):
        validate_manifest(manifest)


def test_three_tier_incidence_and_exact_reconstruction(tmp_path: Path) -> None:
    seeds = bytes(AFFINE_SEED_BYTES)
    tier1 = generate_affine_hydration(seeds)
    tier2 = apply_bit_exceptions(tier1, (0, 5184, 100_000, 900_000))
    tier3 = shake_256(b"pass215-i1-high-entropy-control").digest(FULL_HYDRATION_BYTES)
    raw = tier1 + tier2 + tier3
    tensor_path = tmp_path / "weights.bin"
    tensor_path.write_bytes(raw)

    evidence = build_incidence_evidence(
        _manifest("weights.bin", raw),
        base_directory=tmp_path,
        frozen_profile_blob_sha1=FROZEN_PROFILE_GIT_BLOB_SHA1,
    )
    validate_incidence_evidence(evidence)

    aggregate = evidence["aggregate"]
    assert aggregate["source_bytes"] == FULL_HYDRATION_BYTES * 3
    assert aggregate["tier_1_bytes"] == FULL_HYDRATION_BYTES
    assert aggregate["tier_2_bytes"] == FULL_HYDRATION_BYTES
    assert aggregate["tier_3_bytes"] == FULL_HYDRATION_BYTES
    assert aggregate["admitted_bytes"] == FULL_HYDRATION_BYTES * 2
    assert aggregate["incidence_fraction_exact"] == {"numerator": 2, "denominator": 3}
    assert aggregate["semantic_exactness"] is True
    windows = evidence["tensors"][0]["windows"]
    assert [item["tier"] for item in windows] == [TIER_1, TIER_2, TIER_3]
    assert all(item["semantic_exactness"] is True for item in windows)
    assert evidence["authority"]["benchmark_authority_promoted"] is True
    assert evidence["authority"]["runtime_mutation_authority_promoted"] is False
    assert evidence["authority"]["canonical_mutation_authorized"] is False
    assert evidence["claim_boundary"]["real_open_transformer_measured"] is False
    assert evidence["claim_boundary"]["fifty_billion_desktop_feasibility_claimed"] is False


def test_incomplete_tail_is_conservative_raw_fallback(tmp_path: Path) -> None:
    raw = b"pass215-tail-only"
    (tmp_path / "tail.bin").write_bytes(raw)
    evidence = build_incidence_evidence(
        _manifest("tail.bin", raw),
        base_directory=tmp_path,
        frozen_profile_blob_sha1=FROZEN_PROFILE_GIT_BLOB_SHA1,
    )
    aggregate = evidence["aggregate"]
    assert aggregate["full_hydration_window_count"] == 0
    assert aggregate["tail_fallback_bytes"] == len(raw)
    assert aggregate["tier_1_bytes"] == 0
    assert aggregate["tier_2_bytes"] == 0
    assert aggregate["tier_3_bytes"] == len(raw)
    assert aggregate["incidence_fraction_exact"] == {"numerator": 0, "denominator": 1}
    assert evidence["tensors"][0]["windows"][0]["codec"] == "INCOMPLETE_HYDRATION_TAIL_RAW_FALLBACK"


def test_profile_binding_mismatch_fails_closed(tmp_path: Path) -> None:
    raw = b"x"
    (tmp_path / "x.bin").write_bytes(raw)
    with pytest.raises(Pass215Iteration1ValidationError, match="FROZEN_PROFILE_BLOB_MISMATCH"):
        build_incidence_evidence(
            _manifest("x.bin", raw),
            base_directory=tmp_path,
            frozen_profile_blob_sha1="0" * 40,
        )


def test_path_escape_fails_closed(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-pass215.bin"
    outside.write_bytes(b"x")
    manifest = _manifest("../outside-pass215.bin", b"x")
    with pytest.raises(Pass215Iteration1ValidationError, match="TENSOR_PATH_ESCAPE"):
        build_incidence_evidence(
            manifest,
            base_directory=tmp_path,
            frozen_profile_blob_sha1=FROZEN_PROFILE_GIT_BLOB_SHA1,
        )


def test_evidence_tamper_is_detected(tmp_path: Path) -> None:
    raw = b"exact-tail"
    (tmp_path / "tail.bin").write_bytes(raw)
    evidence = dict(
        build_incidence_evidence(
            _manifest("tail.bin", raw),
            base_directory=tmp_path,
            frozen_profile_blob_sha1=FROZEN_PROFILE_GIT_BLOB_SHA1,
        )
    )
    evidence["evidence_root_hash216"] = "0" * 64
    with pytest.raises(Pass215Iteration1ValidationError, match="EVIDENCE_ROOT_MISMATCH"):
        validate_incidence_evidence(evidence)
