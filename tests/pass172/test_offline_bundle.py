from __future__ import annotations

from pathlib import Path
import hashlib
import json
import zipfile

import pytest

from hhs_installer.offline import OfflineBundleError, OfflineBundleVerifier


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _bundle(tmp_path: Path, *, network_fallback: bool = False) -> Path:
    payload = b"wheel-bytes"
    descriptor = {
        "schema": "HHS_PASS_172_OFFLINE_BUNDLE_V1",
        "network_fallback_permitted": network_fallback,
        "file_manifest": "file-manifest.json",
        "supported_profiles": ["core"],
        "supported_platforms": ["Linux"],
        "supported_architectures": ["x86_64"],
        "required_host_dependencies": ["python>=3.11", "c11-compiler"],
    }
    manifest = {
        "files": [
            {
                "path": "offline-bundle.json",
                "size": len(json.dumps(descriptor, sort_keys=True).encode("utf-8")),
                "sha256": _sha_bytes(json.dumps(descriptor, sort_keys=True).encode("utf-8")),
                "artifact_class": "BUNDLE_DESCRIPTOR",
            },
            {
                "path": "wheels/core.whl",
                "size": len(payload),
                "sha256": _sha_bytes(payload),
                "artifact_class": "PYTHON_WHEEL",
            },
        ]
    }
    archive = tmp_path / "offline.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("offline-bundle.json", json.dumps(descriptor, sort_keys=True))
        output.writestr("file-manifest.json", json.dumps(manifest, sort_keys=True))
        output.writestr("wheels/core.whl", payload)
    return archive


def test_valid_offline_bundle(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    result = OfflineBundleVerifier().verify(bundle, expected_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest())
    assert result.network_fallback_permitted is False
    assert result.verified_files == 2
    assert result.supported_profiles == ("core",)


def test_network_fallback_declaration_rejected(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path, network_fallback=True)
    with pytest.raises(OfflineBundleError) as raised:
        OfflineBundleVerifier().verify(bundle, expected_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest())
    assert raised.value.code == "P172_OFFLINE_NETWORK_FALLBACK_DECLARED"


def test_wrong_bundle_digest_rejected_with_offline_classification(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    with pytest.raises(OfflineBundleError) as raised:
        OfflineBundleVerifier().verify(bundle, expected_sha256="0" * 64)
    assert raised.value.code == "P172_OFFLINE_BUNDLE_DIGEST_MISMATCH"
