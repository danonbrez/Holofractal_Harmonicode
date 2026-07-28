from __future__ import annotations

from base64 import b64encode
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_runtime.pass165.durability import (
    DurableMultimodalLearningService,
    SimulatedInterruption,
)
from hhs_runtime.pass165.ingestion import IngestionError, MultimodalLearningService, SNAPSHOT_BYTES

_HELPER_PATH = Path(__file__).with_name("pass165_real_fixture_corpus.py")
_SPEC = importlib.util.spec_from_file_location("pass165_real_fixture_corpus", _HELPER_PATH)
assert _SPEC and _SPEC.loader
_FIXTURES = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_FIXTURES)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_repository_derived_real_format_corpus(tmp_path: Path) -> None:
    corpus = _FIXTURES.build_corpus(REPOSITORY_ROOT, tmp_path / "corpus")
    independent_validation = {
        "PDF": _FIXTURES.validate_pdf(corpus["PDF"]),
        "IMAGE": _FIXTURES.validate_png(corpus["IMAGE"]),
        "AUDIO": _FIXTURES.validate_wav(corpus["AUDIO"]),
        "VIDEO": _FIXTURES.validate_mp4(corpus["VIDEO"], tmp_path / "validated"),
    }
    assert set(independent_validation) == {"PDF", "IMAGE", "AUDIO", "VIDEO"}

    first = MultimodalLearningService()
    first_receipts: list[str] = []
    source_hashes: list[str] = []
    for modality in ("PDF", "IMAGE", "AUDIO", "VIDEO"):
        raw = corpus[modality]
        result = first.ingest_source(
            raw,
            declared_media_type=modality,
            provenance=f"repository-derived-terminal-fixture:{modality}",
            authorization_scope="P165_TERMINAL_FIXTURE_INGEST",
        )
        source_hash = sha256(raw).hexdigest()
        source_hashes.append(source_hash)
        first_receipts.append(result["receipt"]["receipt_hash72"])
        assert result["source"]["source_hash"] == source_hash
        assert result["source"]["detected_media_type"] == modality
        assert result["projection_hash72"] and len(result["projection_hash72"]) == 72
        assert result["token_count"] > 0
        stored = first._sources[source_hash]
        analyzed = first._results[source_hash]
        assert stored.source_bytes == raw
        assert len(analyzed.projection_bytes) == SNAPSHOT_BYTES == 648
        assert all(0 <= token.source_span[0] <= token.source_span[1] <= len(raw) for token in analyzed.tokens)
        if modality == "IMAGE":
            assert any(token.spatial_span is not None for token in analyzed.tokens)
        if modality in ("AUDIO", "VIDEO"):
            assert any(token.temporal_span is not None for token in analyzed.tokens)

    replay = first.replay_ingestion()
    assert replay["deterministic_replay"] is True
    assert replay["records"] == 4

    second = MultimodalLearningService()
    second_receipts = [
        second.ingest_source(
            corpus[modality],
            declared_media_type=modality,
            provenance=f"repository-derived-terminal-fixture:{modality}",
            authorization_scope="P165_TERMINAL_FIXTURE_INGEST",
        )["receipt"]["receipt_hash72"]
        for modality in ("PDF", "IMAGE", "AUDIO", "VIDEO")
    ]
    assert second_receipts == first_receipts
    assert second.weight_root == first.weight_root
    assert second._vm81.state_hash72 == first._vm81.state_hash72

    reused = first.ingest_source(
        corpus["PDF"],
        declared_media_type="PDF",
        provenance="repository-derived-terminal-fixture:PDF",
        authorization_scope="P165_TERMINAL_FIXTURE_INGEST",
    )
    assert reused["receipt"]["reused"] is True
    assert len(first._history) == 4
    assert set(source_hashes) == set(first._sources)


def _ingest_text(service: DurableMultimodalLearningService, index: int) -> dict:
    return service.ingest_source(
        f"pass165 durable source {index}\nalpha_{index} = {index}\nalpha alpha".encode("utf-8"),
        declared_media_type="TEXT",
        provenance=f"repository-durable-fixture:{index}",
        authorization_scope="P165_DURABLE_RECOVERY_TEST",
    )


def test_durable_interruption_recovery_and_tamper_rejection(tmp_path: Path) -> None:
    store = tmp_path / "store"
    service = DurableMultimodalLearningService(store)
    first = _ingest_text(service, 1)
    second = _ingest_text(service, 2)
    assert service.status()["durable_records"] == 2

    journal_fault = DurableMultimodalLearningService(store)
    journal_fault._fault_after = "after_journal_fsync"
    with pytest.raises(SimulatedInterruption, match="after_journal_fsync"):
        _ingest_text(journal_fault, 3)
    recovered = DurableMultimodalLearningService(store)
    assert recovered.status()["durable_records"] == 3
    assert recovered.get_ingestion_receipt(first["source"]["source_hash"])["receipt_hash72"] == first["receipt"]["receipt_hash72"]
    assert recovered.get_ingestion_receipt(second["source"]["source_hash"])["receipt_hash72"] == second["receipt"]["receipt_hash72"]

    frontier_fault = DurableMultimodalLearningService(store)
    frontier_fault._fault_after = "after_head_temp_fsync"
    with pytest.raises(SimulatedInterruption, match="after_head_temp_fsync"):
        _ingest_text(frontier_fault, 4)
    recovered = DurableMultimodalLearningService(store)
    assert recovered.status()["durable_records"] == 4
    assert not recovered.head_temp_path.exists()

    prior_root = recovered.weight_root
    prior_vm81 = recovered._vm81.state_hash72
    nondurable_fault = DurableMultimodalLearningService(store)
    nondurable_fault._fault_after = "before_journal_append"
    with pytest.raises(SimulatedInterruption, match="before_journal_append"):
        _ingest_text(nondurable_fault, 5)
    recovered = DurableMultimodalLearningService(store)
    assert recovered.status()["durable_records"] == 4
    assert recovered.weight_root == prior_root
    assert recovered._vm81.state_hash72 == prior_vm81

    with recovered.journal_path.open("ab") as handle:
        handle.write(b'{"schema":"incomplete"')
    recovered = DurableMultimodalLearningService(store)
    assert recovered.status()["durable_records"] == 4
    quarantine = recovered.quarantine_path.read_text("utf-8")
    assert "P165_INCOMPLETE_JOURNAL_TAIL" in quarantine
    assert recovered.replay_ingestion()["deterministic_replay"] is True

    tampered_store = tmp_path / "tampered"
    shutil.copytree(store, tampered_store)
    journal = tampered_store / "ingestion.journal.jsonl"
    lines = journal.read_bytes().splitlines(keepends=True)
    envelope = json.loads(lines[0])
    envelope["record"]["source_hash"] = "0" * 64
    lines[0] = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
    journal.write_bytes(b"".join(lines))
    with pytest.raises(IngestionError, match="P165_DURABLE_JOURNAL_TAMPER"):
        DurableMultimodalLearningService(tampered_store)


def test_public_api_ingests_real_pdf_and_recovers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    corpus = _FIXTURES.build_corpus(REPOSITORY_ROOT, tmp_path / "api-corpus")
    storage = tmp_path / "api-store"
    from hhs_backend.api import pass165_multimodal_ingress_routes as routes

    service = DurableMultimodalLearningService(storage)
    monkeypatch.setattr(routes, "SERVICE", service)
    app = FastAPI()
    app.include_router(routes.router)
    client = TestClient(app)
    response = client.post(
        "/api/runtime/multimodal-ingress/ingest",
        json={
            "source_b64": b64encode(corpus["PDF"]).decode("ascii"),
            "declared_media_type": "PDF",
            "provenance": "repository-derived-api-fixture",
            "authorization_scope": "P165_TERMINAL_FIXTURE_INGEST",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source"]["detected_media_type"] == "PDF"
    assert client.get("/api/runtime/multimodal-ingress/status").json()["durable"] is True
    assert client.post("/api/runtime/multimodal-ingress/replay").json()["deterministic_replay"] is True
    recovery = client.post("/api/runtime/multimodal-ingress/recover")
    assert recovery.status_code == 200
    assert recovery.json()["deterministic_recovery"] is True
