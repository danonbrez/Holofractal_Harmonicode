from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import zipfile

import pytest

from hhs_runtime.pass166.common import Word2VecError, Word2VecPackageManifest
from hhs_runtime.pass166.service import Word2VecService


def _manifest(path: Path, model_id: str, *, archive_type: str = "NONE", artifact_path: str | None = None) -> Word2VecPackageManifest:
    raw = path.read_bytes()
    return Word2VecPackageManifest(
        package_id=model_id,
        display_name=model_id,
        provider="HHS_SUPPLY_CHAIN_TEST",
        source_uri=path.resolve().as_uri(),
        source_version="1",
        license_id="TEST-ONLY",
        license_uri="https://example.invalid/test-license",
        expected_byte_length=len(raw),
        expected_sha256=sha256(raw).hexdigest(),
        archive_type=archive_type,
        vector_format="WORD2VEC_TEXT",
        vector_dimension=2,
        vocabulary_size=2,
        normalization_profile="CASE_FOLDED",
        artifact_path=artifact_path,
    )


def test_exact_source_components_and_source_model_root_are_preserved(tmp_path: Path) -> None:
    source = tmp_path / "vectors.txt"
    source.write_bytes(b"2 2\nAlpha 0.1 -0.25\nBeta 1.5 0\n")
    manifest = _manifest(source, "source-preservation")
    service = Word2VecService(tmp_path / "store")
    service.register_manifest(manifest)
    service.install(manifest.package_id, accept_license=True)
    model = service._models[manifest.package_id]
    alpha = model.vectors[0]
    assert alpha.source_model_root == manifest.manifest_root
    assert alpha.source_values_exact == ("1/10", "-1/4")
    assert alpha.source_numeric_encoding == "DECIMAL_TEXT"
    assert alpha.source_vector_digest
    restarted = Word2VecService(tmp_path / "store")
    restored = restarted._models[manifest.package_id].vectors[0]
    assert restored.source_values_exact == alpha.source_values_exact
    assert restored.canonical_values == alpha.canonical_values


def test_undeclared_executable_archive_payload_is_rejected(tmp_path: Path) -> None:
    package = tmp_path / "executable.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("vectors.txt", b"2 2\na 1 0\nb 0 1\n")
        archive.writestr("install.sh", b"#!/bin/sh\nexit 0\n")
    manifest = _manifest(package, "executable", archive_type="ZIP", artifact_path="vectors.txt")
    service = Word2VecService(tmp_path / "store")
    service.register_manifest(manifest)
    with pytest.raises(Word2VecError, match="P166_UNDECLARED_EXECUTABLE_PAYLOAD"):
        service.install(manifest.package_id, accept_license=True)


def test_manifest_rejects_unpinned_scheme_and_unsupported_profile(tmp_path: Path) -> None:
    source = tmp_path / "vectors.txt"
    source.write_bytes(b"2 2\na 1 0\nb 0 1\n")
    manifest = _manifest(source, "scheme")
    with pytest.raises(Word2VecError, match="P166_UNPINNED_OR_UNSUPPORTED_SOURCE"):
        Word2VecPackageManifest(**{**manifest.__dict__, "source_uri": "http://example.invalid/model.bin"}).validate()
    with pytest.raises(Word2VecError, match="P166_UNSUPPORTED_QUANTIZATION_PROFILE"):
        Word2VecPackageManifest(**{**manifest.__dict__, "quantization_profile": "FLOAT32_NATIVE"}).validate()
