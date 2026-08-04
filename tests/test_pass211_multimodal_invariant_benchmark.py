from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pass211_multimodal_invariant_benchmark.py"
SPEC = importlib.util.spec_from_file_location("pass211_benchmark", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_exact_state_space_constants() -> None:
    report = MODULE.exact_constants()
    assert report["passed"] is True
    assert report["values"] == {
        "vm81_cells": 81,
        "operations_per_cell": 64,
        "permanent_states": 5_184,
        "g243_controls": 243,
        "projected_states": 1_259_712,
        "local_coordinates": 41,
        "contextual_states": 51_648_192,
        "factorial_states": 5_040,
        "outer_envelope": 1_259_713,
    }


def test_context_roundtrip_boundaries_and_samples() -> None:
    addresses = [
        0,
        1,
        40,
        41,
        1_259_712,
        25_824_096,
        51_648_150,
        51_648_191,
    ]
    for address in addresses:
        decoded = MODULE.decode_context(address)
        assert MODULE.encode_context(*decoded) == address

    report = MODULE.benchmark_address_roundtrip(10_000)
    assert report["samples"] == 10_000
    assert report["coordinate_drift"] == 0
    assert len(report["checksum_hex"]) == 16


@pytest.mark.parametrize(
    "args",
    [
        (-1, 0, 0, 0),
        (81, 0, 0, 0),
        (0, 64, 0, 0),
        (0, 0, 243, 0),
        (0, 0, 0, 41),
    ],
)
def test_context_encoder_rejects_out_of_range(args: tuple[int, int, int, int]) -> None:
    with pytest.raises(ValueError):
        MODULE.encode_context(*args)


def test_vector72_is_deterministic_and_path_sensitive() -> None:
    payload = b"same source bytes"
    left = MODULE.vector72("a/model.bin", payload)
    same = MODULE.vector72("a/model.bin", payload)
    right = MODULE.vector72("b/model.bin", payload)
    assert left == same
    assert left != right
    assert len(left) == 72
    assert MODULE.distance72(left, same) == 0
    assert MODULE.distance72(left, right) > 0


def test_retrieval_calibration_exact_and_single_bit_nearest() -> None:
    objects = []
    for index in range(16):
        path = f"object-{index}.md"
        payload = f"payload-{index}".encode()
        objects.append(
            MODULE.RepositoryObject(
                path=path,
                size=len(payload),
                digest_hex=MODULE.hashlib.sha256(payload).hexdigest(),
                vector72=MODULE.vector72(path, payload),
                modalities=("model",),
                invariants=("hash216",),
            )
        )
    report = MODULE.benchmark_retrieval(objects, query_limit=16)
    assert report["exact_hit_rate"] == 1.0
    assert report["single_bit_adaptation_nearest_rate"] == 1.0
    assert report["distance_evaluations"] == 512


def test_repository_scan_detects_modalities_invariants_and_json(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "PASS_210_TEST.md").write_text(
        "Hash72 Hash216 singleton VM81 noncommutative 81 × 64 G243 "
        "1,259,712 51,648,192 5,040 image video animation audio physics game "
        "language model parameter GPU continuation retrieval",
        encoding="utf-8",
    )
    (tmp_path / "valid.json").write_text('{"ok": true}', encoding="utf-8")
    scan, objects = MODULE.scan_repository(tmp_path, max_vector_objects=32)
    assert scan["highest_pass_observed"] == 210
    assert scan["json"]["valid_files"] == 1
    assert scan["json"]["invalid_files"] == 0
    assert scan["invariant_file_counts"]["contextual_51648192"] == 1
    assert scan["modality_file_counts"]["retrieval"] == 1
    assert objects
