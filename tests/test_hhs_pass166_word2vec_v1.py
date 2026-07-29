from __future__ import annotations

from dataclasses import asdict, replace
from hashlib import sha256
from io import BytesIO, StringIO
import json
from pathlib import Path
import struct
import zipfile

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_runtime.pass166.cli import main as cli_main
from hhs_runtime.pass166.common import QUANTIZATION_SCALE, Word2VecError, Word2VecPackageManifest
from hhs_runtime.pass166.service import SimulatedInterruption, Word2VecService

ROWS = (
    ("king", (1.0, 1.0, 0.0, 0.0)),
    ("queen", (1.0, 0.9, 0.1, 0.0)),
    ("man", (0.9, 0.0, 0.0, 0.0)),
    ("woman", (0.9, -0.1, 0.1, 0.0)),
)


def text_fixture(rows=ROWS) -> bytes:
    lines = [f"{len(rows)} 4"]
    lines.extend(f"{token} " + " ".join(format(value, ".8g") for value in vector) for token, vector in rows)
    return ("\n".join(lines) + "\n").encode("utf-8")


def binary_fixture(rows=ROWS) -> bytes:
    output = bytearray(f"{len(rows)} 4\n".encode("ascii"))
    for token, vector in rows:
        output.extend(token.encode("utf-8") + b" ")
        output.extend(b"".join(struct.pack("<f", value) for value in vector))
        output.extend(b"\n")
    return bytes(output)


def write_source(directory: Path, name: str, raw: bytes) -> Path:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path.resolve()


def manifest_for(path: Path, *, model_id: str = "toy-text", vector_format: str = "WORD2VEC_TEXT", archive_type: str = "NONE", artifact_path: str | None = None, dimension: int = 4, vocabulary_size: int = 4, digest: str | None = None) -> Word2VecPackageManifest:
    raw = path.read_bytes()
    return Word2VecPackageManifest(
        package_id=model_id,
        display_name=model_id,
        provider="HHS_TEST_FIXTURE",
        source_uri=path.as_uri(),
        source_version="1",
        license_id="TEST-ONLY",
        license_uri="https://example.invalid/test-license",
        expected_byte_length=len(raw),
        expected_sha256=digest or sha256(raw).hexdigest(),
        archive_type=archive_type,
        vector_format=vector_format,
        vector_dimension=dimension,
        vocabulary_size=vocabulary_size,
        normalization_profile="CASE_FOLDED",
        artifact_path=artifact_path,
    )


def install_text(tmp_path: Path, *, model_id: str = "toy-text") -> tuple[Word2VecService, Word2VecPackageManifest, dict]:
    source = write_source(tmp_path, f"{model_id}.txt", text_fixture())
    manifest = manifest_for(source, model_id=model_id)
    service = Word2VecService(tmp_path / f"store-{model_id}")
    service.register_manifest(manifest)
    receipt = service.install(model_id, accept_license=True, activate=True, offline_ready=True)
    return service, manifest, receipt


def test_text_install_lookup_projection_nearest_analogy_and_replay(tmp_path: Path) -> None:
    service, manifest, receipt = install_text(tmp_path)
    assert receipt["classification"] == "P166_ACTIVATION_RECEIPT"
    assert service.status()["active_model_id"] == manifest.package_id
    vector = service.vector("king")
    assert vector["dimension"] == 4
    assert vector["denominator"] == QUANTIZATION_SCALE
    assert len(vector["projection_5184_b64"]) == 864
    assert "=" not in vector["projection_5184_b64"]
    assert len(vector["projection_5184_root"]) == 72
    assert service.nearest("king", top_k=2)["results"][0]["token"] == "queen"
    analogy = service.analogy(["king", "woman"], ["man"], top_k=1)
    assert analogy["results"][0]["token"] == "queen"
    similarity = service.similarity("king", "queen")
    assert similarity["cosine_sign"] == 1
    assert "/" in similarity["cosine_squared_exact"]
    assert service.replay(manifest.package_id)["deterministic_replay"] is True
    assert service.verify(manifest.package_id)["verified"] is True


def test_word2vec_binary_import_and_exact_bit_decoding(tmp_path: Path) -> None:
    source = write_source(tmp_path, "toy.bin", binary_fixture())
    manifest = manifest_for(source, model_id="toy-binary", vector_format="WORD2VEC_BINARY")
    service = Word2VecService(tmp_path / "binary-store")
    service.register_manifest(manifest)
    result = service.install("toy-binary", accept_license=True)
    assert result["canonical_model_root"]
    vector = service.vector("queen", model_id="toy-binary")
    assert vector["canonical_values"][0] == QUANTIZATION_SCALE
    assert vector["canonical_values"][2] != 0
    assert service.replay("toy-binary")["records"] == 4


def test_safe_zip_package_import(tmp_path: Path) -> None:
    package = tmp_path / "toy.zip"
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("vectors.txt", text_fixture())
    manifest = manifest_for(package.resolve(), model_id="toy-zip", archive_type="ZIP", artifact_path="vectors.txt")
    service = Word2VecService(tmp_path / "zip-store")
    service.register_manifest(manifest)
    result = service.install("toy-zip", accept_license=True)
    assert result["model_id"] == "toy-zip"
    assert service.vector("queen", model_id="toy-zip")["token"] == "queen"


def test_cross_instance_determinism_and_offline_restart(tmp_path: Path) -> None:
    source = write_source(tmp_path, "deterministic.txt", text_fixture())
    manifest = manifest_for(source, model_id="deterministic")
    first = Word2VecService(tmp_path / "first")
    second = Word2VecService(tmp_path / "second")
    first.register_manifest(manifest); second.register_manifest(manifest)
    first_result = first.install("deterministic", accept_license=True)
    second_result = second.install("deterministic", accept_license=True)
    assert first_result["canonical_model_root"] == second_result["canonical_model_root"]
    assert first_result["index_root"] == second_result["index_root"]
    source.unlink()
    restarted = Word2VecService(tmp_path / "first")
    assert restarted.status()["offline_ready"] is True
    assert restarted.vector("king")["vector_identity"] == first.vector("king")["vector_identity"]
    assert restarted.replay("deterministic")["deterministic_replay"] is True


def test_idempotent_reinstall_and_profile_conflict(tmp_path: Path) -> None:
    service, manifest, first = install_text(tmp_path, model_id="idempotent")
    second = service.install("idempotent", accept_license=True)
    assert second["classification"] == "P166_IDEMPOTENT_INSTALL_REUSED"
    assert second["reused"] is True
    altered = replace(manifest, source_version="2")
    with pytest.raises(Word2VecError, match="P166_MANIFEST_ID_CONFLICT"):
        service.register_manifest(altered)


def test_atomic_rollback_before_vm81_admission(tmp_path: Path) -> None:
    service, _, _ = install_text(tmp_path, model_id="primary")
    incoming = service.status()["vm81_state_hash72"]
    source = write_source(tmp_path, "candidate.txt", text_fixture())
    service.register_manifest(manifest_for(source, model_id="candidate"))
    service._fault_after = "before_vm81_admission"
    with pytest.raises(SimulatedInterruption, match="before_vm81_admission"):
        service.install("candidate", accept_license=True)
    status = service.status()
    assert status["active_model_id"] == "primary"
    assert status["vm81_state_hash72"] == incoming
    assert "candidate" not in {item["model_id"] for item in service.list_models() if item["state"] != "RESOLVED"}
    assert any(record["stage"] == "ROLLBACK" for record in service._receipt_chain)


def test_deactivate_activate_remove_and_historical_receipts(tmp_path: Path) -> None:
    service, _, _ = install_text(tmp_path, model_id="lifecycle")
    assert service.deactivate("lifecycle")["classification"] == "P166_MODEL_DEACTIVATED"
    assert service.status()["active_model_id"] is None
    assert service.activate("lifecycle")["classification"] == "P166_MODEL_ACTIVATED"
    operation_count = len(service._receipt_chain)
    assert service.remove("lifecycle", purge_package=True)["classification"] == "P166_MODEL_REMOVED"
    assert len(service._receipt_chain) == operation_count + 1
    assert service.receipts_path.exists()


def test_repair_rebuilds_inconsistent_index(tmp_path: Path) -> None:
    service, _, _ = install_text(tmp_path, model_id="repairable")
    service._models["repairable"] = replace(service._models["repairable"], index_root="0" * 64)
    service._persist_registry()
    result = service.repair("repairable")
    assert result["classification"] == "P166_MODEL_REPAIRED"
    assert service.verify("repairable")["verified"] is True


def test_cli_documented_alias_and_api_equivalence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = write_source(tmp_path, "surface.txt", text_fixture())
    manifest = manifest_for(source, model_id="surface")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(asdict(manifest)), "utf-8")
    cli_service = Word2VecService(tmp_path / "cli-store")
    out, err = StringIO(), StringIO()
    code = cli_main(["model", "install", "word2vec", "surface", "--manifest", str(manifest_path), "--license-accept", "--output", "json"], service=cli_service, stdout=out, stderr=err)
    assert code == 0 and not err.getvalue()
    cli_result = json.loads(out.getvalue())

    from hhs_backend.api import pass166_word2vec_routes as routes
    api_service = Word2VecService(tmp_path / "api-store")
    monkeypatch.setattr(routes, "SERVICE", api_service)
    app = FastAPI(); app.include_router(routes.router)
    client = TestClient(app)
    assert client.post("/v1/modalities/language/models/word2vec/manifests", json={"manifest": asdict(manifest)}).status_code == 200
    response = client.post("/v1/modalities/language/models/word2vec/install", json={"model_id": "surface", "source_manifest_id": "surface", "expected_sha256": manifest.expected_sha256, "accept_license": True, "activate": True, "offline_ready": True, "replace_existing": False})
    assert response.status_code == 200
    api_result = response.json()
    assert api_result["canonical_model_root"] == cli_result["canonical_model_root"]
    lookup = client.get("/v1/modalities/language/vectors/king")
    assert lookup.status_code == 200 and lookup.json()["token"] == "king"
    nearest = client.post("/v1/modalities/language/nearest", json={"token": "king", "top_k": 2})
    assert nearest.status_code == 200 and nearest.json()["approximate"] is False


def test_license_digest_truncation_and_stale_frontier_rejected(tmp_path: Path) -> None:
    source = write_source(tmp_path, "negative.txt", text_fixture())
    manifest = manifest_for(source, model_id="negative")
    service = Word2VecService(tmp_path / "negative-store")
    service.register_manifest(manifest)
    with pytest.raises(Word2VecError, match="P166_LICENSE_ACCEPTANCE_REQUIRED"):
        service.install("negative", accept_license=False)
    with pytest.raises(Word2VecError, match="P166_STALE_PASS165_FRONTIER"):
        service.install("negative", accept_license=True, expected_pass165_frontier="stale")
    mismatch = manifest_for(source, model_id="mismatch", digest="0" * 64)
    service.register_manifest(mismatch)
    with pytest.raises(Word2VecError, match="P166_DIGEST_MISMATCH"):
        service.install("mismatch", accept_license=True)
    truncated_source = write_source(tmp_path, "truncated.txt", text_fixture()[:-4])
    truncated = replace(manifest_for(truncated_source, model_id="truncated"), expected_byte_length=len(text_fixture()))
    service.register_manifest(truncated)
    with pytest.raises(Word2VecError, match="P166_BYTE_LENGTH_MISMATCH"):
        service.install("truncated", accept_license=True)


@pytest.mark.parametrize(
    ("raw", "classification"),
    [
        (b"not-a-header\n", "P166_MALFORMED_WORD2VEC_HEADER"),
        (b"2 2\na 1\nb 0 1\n", "P166_MIXED_VECTOR_DIMENSIONS"),
        (b"2 2\na 1 0\na 0 1\n", "P166_DUPLICATE_TOKEN_CONFLICT"),
        (b"1 2\na NaN 0\n", "P166_NONFINITE_VALUE"),
        (b"1 2\na Infinity 0\n", "P166_NONFINITE_VALUE"),
    ],
)
def test_malformed_text_vectors_rejected(tmp_path: Path, raw: bytes, classification: str) -> None:
    source = write_source(tmp_path, f"{classification}.txt", raw)
    fields = raw.splitlines()[0].split()
    vocabulary = int(fields[0]) if len(fields) == 2 and fields[0].isdigit() else 1
    dimension = int(fields[1]) if len(fields) == 2 and fields[1].isdigit() else 2
    service = Word2VecService(tmp_path / classification)
    service.register_manifest(manifest_for(source, model_id=classification, dimension=dimension, vocabulary_size=vocabulary))
    with pytest.raises(Word2VecError, match=classification):
        service.install(classification, accept_license=True)


def test_archive_traversal_rejected(tmp_path: Path) -> None:
    package = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("../escape.txt", text_fixture())
    service = Word2VecService(tmp_path / "unsafe-store")
    service.register_manifest(manifest_for(package.resolve(), model_id="unsafe", archive_type="ZIP"))
    with pytest.raises(Word2VecError, match="P166_ARCHIVE_TRAVERSAL"):
        service.install("unsafe", accept_license=True)
    assert not (tmp_path / "escape.txt").exists()


def test_receipt_tamper_and_offline_dependency_omission_rejected(tmp_path: Path) -> None:
    service, manifest, _ = install_text(tmp_path, model_id="tamper")
    lines = service.receipts_path.read_bytes().splitlines()
    envelope = json.loads(lines[0])
    envelope["receipt"]["stage"] = "ALTERED"
    lines[0] = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8")
    service.receipts_path.write_bytes(b"\n".join(lines) + b"\n")
    with pytest.raises(Word2VecError, match="P166_RECEIPT_CHAIN_TAMPER"):
        Word2VecService(service.root)

    clean, clean_manifest, _ = install_text(tmp_path, model_id="offline-missing")
    package = clean.packages_dir / clean_manifest.package_id / clean_manifest.expected_sha256 / "source.package"
    package.unlink()
    with pytest.raises(Word2VecError, match="P166_OFFLINE_DEPENDENCY_OMISSION"):
        clean.replay(clean_manifest.package_id)
