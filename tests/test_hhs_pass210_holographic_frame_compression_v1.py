from __future__ import annotations

import ast
import inspect
import json
import random

import pytest

from hhs_backend.runtime import hhs_pass210_holographic_frame_compression_v1 as hfc


def corpus() -> dict[str, bytes]:
    rng = random.Random(210)
    return {
        "zeros": bytes([0]) * hfc.REGISTER_LEN,
        "ones": bytes([1]) * hfc.REGISTER_LEN,
        "alternating": bytes(index & 1 for index in range(hfc.REGISTER_LEN)),
        "prng_210": bytes(rng.randrange(2) for _ in range(hfc.REGISTER_LEN)),
    }


def test_constants_and_invariants() -> None:
    assert hfc.REGISTER_LEN == 72**2 == 81 * 64 == 36 * 144
    assert hfc.SNAPSHOT_COUNT * hfc.SNAPSHOT_WIDTH == 2 * hfc.REGISTER_LEN
    assert hfc.SECTION_PHI_HI + hfc.SECTION_PHI_LO == hfc.SNAPSHOT_STRIDE
    assert all(hfc.audit_invariants().values())
    assert set((hfc.SNAPSHOT_STRIDE * index) % hfc.LINE_BYTES for index in range(36)) == {0, 16, 32, 48}


def test_round_trip_adversarial_corpus_and_alignment() -> None:
    for raw in corpus().values():
        runtime = hfc.HolographicFrameCompressionRuntime()
        frame = runtime.frame_encode(raw)
        assert frame.register.address % hfc.LINE_BYTES == 0
        assert runtime.frame_decode(frame) == raw
        assert frame.register.to_bytes() == raw


def test_snapshot_coverage_and_lazy_single_storage() -> None:
    raw = corpus()["alternating"]
    runtime = hfc.HolographicFrameCompressionRuntime()
    frame = runtime.frame_encode(raw)
    assert all(count == 2 for count in hfc.coverage_counts())
    for cell in range(hfc.REGISTER_LEN):
        locations = hfc.containing_snapshots(cell)
        assert len(locations) == 2
        assert all(frame.snapshot_view(index)[offset] == raw[cell] for index, offset in locations)
    assert all(frame.snapshot_view(index).register is frame.register for index in range(hfc.SNAPSHOT_COUNT))


def test_golden_sections_and_matrix() -> None:
    raw = corpus()["prng_210"]
    runtime = hfc.HolographicFrameCompressionRuntime()
    frame = runtime.frame_encode(raw)
    for index in range(hfc.SNAPSHOT_COUNT):
        sections = hfc.hfc_section(frame.snapshot_view(index))
        assert tuple(map(len, sections)) == (89, 55, 89, 55)
        assert b"".join(sections) == runtime.snapshot(frame, index)
    matrix = hfc.hfc_matrix(raw[: hfc.SNAPSHOT_STRIDE])
    assert len(matrix) == 12
    assert all(len(row) == 12 for row in matrix)
    assert bytes(value for row in matrix for value in row) == raw[:144]


def test_affine_view_admission_and_inverse() -> None:
    runtime = hfc.HolographicFrameCompressionRuntime()
    view_id = runtime.view_admit(5, 1, 361)
    view = runtime.view(view_id)
    assert view.inverse_k == 289
    assert all(view.decode(view.encode(value)) == value for value in range(361))
    before = len(runtime._views)
    with pytest.raises(hfc.HFCNonBijectiveViewRejected, match=hfc.NON_BIJECTIVE_VIEW):
        runtime.view_admit(6, 1, 12)
    assert len(runtime._views) == before


def test_all_single_snapshot_erasures_recover_exactly() -> None:
    raw = corpus()["prng_210"]
    runtime = hfc.HolographicFrameCompressionRuntime()
    frame = runtime.frame_encode(raw)
    for lost_index in range(hfc.SNAPSHOT_COUNT):
        assert runtime.recover(frame, lost_index) == raw
        degraded = frame.without_snapshot(lost_index)
        assert runtime.frame_decode(degraded) == raw


def test_cross_modal_agreement_and_corruption_localization() -> None:
    raw = corpus()["prng_210"]
    runtime = hfc.HolographicFrameCompressionRuntime()
    modalities = ("raw", "hash72", "hash216", "phase", "frame")
    clean = [runtime.project(raw, modality) for modality in modalities]
    verdict = runtime.agree(*clean)
    assert verdict["agreement"] is True
    assert verdict["disagreement_cells"] == []
    assert set(verdict["surviving_witnesses"]) == set(modalities)

    for corrupted_index, modality in enumerate(modalities):
        cell = 777 + corrupted_index
        projections = list(clean)
        projections[corrupted_index] = projections[corrupted_index].corrupt_cell(cell)
        verdict = runtime.agree(*projections)
        assert verdict["agreement"] is False
        assert verdict["repair_performed"] is False
        assert cell in verdict["disagreement_cells"]
        result = next(item for item in verdict["projections"] if item["modality"] == modality)
        assert cell in result["disagreement_cells"]


def test_frame_internal_corruption_is_not_self_repaired() -> None:
    raw = corpus()["alternating"]
    runtime = hfc.HolographicFrameCompressionRuntime()
    frame = runtime.frame_encode(raw)
    bad = frame.corrupt_snapshot_cell(10, 37)
    cell = (10 * hfc.SNAPSHOT_STRIDE + 37) % hfc.REGISTER_LEN
    with pytest.raises(hfc.HFCWitnessViolation) as caught:
        runtime.frame_decode(bad)
    assert cell in caught.value.cells


def test_receipt_replay_is_deterministic_and_noncommit_events_do_not_extend() -> None:
    raw = corpus()["alternating"]

    def session() -> list[dict[str, object]]:
        runtime = hfc.HolographicFrameCompressionRuntime()
        frame = runtime.frame_encode(raw)
        runtime.frame_decode(frame)
        runtime.view_admit(5, 1, 361)
        runtime.recover(frame, 17)
        head = runtime.ledger.head
        count = len(runtime.ledger.records())
        assert runtime.ledger.note_without_extension("HALT", {"reason": "test"}) == head
        assert runtime.ledger.note_without_extension("ANNOTATION", {"note": "test"}) == head
        assert len(runtime.ledger.records()) == count
        return runtime.ledger.export()

    assert session() == session()


def test_strict_compression_only_on_declared_admissible_domain() -> None:
    runtime = hfc.HolographicFrameCompressionRuntime()
    raw = hfc.affine_fibonacci_mod2(0, 1)
    package = runtime.strict_compress(raw)
    assert len(json.dumps(package, sort_keys=True, separators=(",", ":")).encode()) < hfc.REGISTER_LEN
    assert package["admissible_domain_witness"]["domain"] == hfc.ADMISSIBLE_DOMAIN
    assert runtime.strict_decompress(package) == raw
    with pytest.raises(hfc.HFCValidationError, match="HFC_STRICT_COMPRESSION_DOMAIN_WITNESS_REQUIRED"):
        runtime.strict_compress(corpus()["prng_210"])


def test_boolean_register_and_stride_realignment_fail_closed() -> None:
    runtime = hfc.HolographicFrameCompressionRuntime()
    with pytest.raises(hfc.HFCValidationError, match="HFC_REGISTER_LENGTH_REQUIRED"):
        runtime.frame_encode(bytes(hfc.REGISTER_LEN - 1))
    invalid = bytearray(hfc.REGISTER_LEN)
    invalid[91] = 2
    with pytest.raises(hfc.HFCValidationError, match="HFC_BOOLEAN_BYTE_REQUIRED:91"):
        runtime.frame_encode(invalid)
    assert hfc.SNAPSHOT_STRIDE % hfc.LINE_BYTES != 0
    assert hfc.SNAPSHOT_STRIDE != 128


def test_no_float_literals_or_float_conversion_in_canonical_runtime() -> None:
    source = inspect.getsource(hfc)
    tree = ast.parse(source)
    assert not any(isinstance(node, ast.Constant) and isinstance(node.value, float) for node in ast.walk(tree))
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float" for node in ast.walk(tree))


def test_frozen_contract_and_committed_evidence() -> None:
    from pathlib import Path
    import subprocess

    root = Path(__file__).resolve().parents[1]
    contract = json.loads((root / "contracts/pass210/PASS_210_CONTRACT.json").read_text())
    assert contract["pass"] == 210
    assert contract["contract_identifier"] == hfc.CONTRACT
    assert contract["constants"]["REGISTER_LEN"] == hfc.REGISTER_LEN
    completed = subprocess.run(
        ["python", "tools/generate_pass210_hfc_evidence.py", "--check"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PASS210_EVIDENCE_CHECK_OK" in completed.stdout
