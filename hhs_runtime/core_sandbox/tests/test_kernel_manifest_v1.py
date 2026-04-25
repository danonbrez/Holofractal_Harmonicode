from pathlib import Path
import json

from hhs_runtime.core_sandbox.hhs_kernel_manifest_v1 import (
    generate_kernel_manifest,
    write_kernel_manifest,
    verify_kernel_manifest,
    startup_integrity_guard,
    ManifestStatus,
)


def test_generate_and_write_manifest(tmp_path):
    manifest_path = tmp_path / "kernel_manifest_v1.json"
    m = write_kernel_manifest(manifest_path)
    assert m.manifest_hash72
    assert len(m.files) > 0
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["manifest_hash72"] == m.manifest_hash72


def test_verify_manifest_ok(tmp_path):
    manifest_path = tmp_path / "kernel_manifest_v1.json"
    write_kernel_manifest(manifest_path)
    receipt = verify_kernel_manifest(manifest_path)
    assert receipt.status == ManifestStatus.VERIFIED
    assert not receipt.mismatches
    assert not receipt.missing_files
    assert not receipt.unexpected_files


def test_startup_guard_raises_on_tamper(tmp_path, monkeypatch):
    manifest_path = tmp_path / "kernel_manifest_v1.json"
    write_kernel_manifest(manifest_path)

    # Tamper with a kernel file copy: simulate by pointing repo_root to a temp copy and modifying one file.
    # For simplicity, we just modify the manifest file itself to force mismatch.
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["files"][0]["hash72"] = "H72N-FAKE"
    manifest_path.write_text(json.dumps(data), encoding="utf-8")

    receipt = verify_kernel_manifest(manifest_path)
    assert receipt.status == ManifestStatus.QUARANTINED

    raised = False
    try:
        startup_integrity_guard(manifest_path, raise_on_fail=True)
    except RuntimeError:
        raised = True
    assert raised is True
