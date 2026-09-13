from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = ROOT / "tools/pass219/verify_generation_integrity_v1.py"
MANIFEST_PATH = ROOT / "contracts/pass219/PASS_219_GENERATION_INTEGRITY_MANIFEST_V1.json"

spec = importlib.util.spec_from_file_location("pass219_generation_integrity_v1", VERIFIER_PATH)
assert spec is not None and spec.loader is not None
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_generation_integrity_manifest_policy_is_fail_closed() -> None:
    manifest = _manifest()
    policy = manifest["policy"]
    assert manifest["schema"] == "HHS_PASS219_GENERATION_INTEGRITY_MANIFEST_V1"
    assert policy["generation_is_untrusted_until_verified"] is True
    assert policy["halt_on_structural_drift"] is True
    assert policy["halt_on_artifact_identity_drift"] is True
    assert policy["halt_on_abi_drift"] is True
    assert policy["halt_on_authority_drift"] is True
    assert policy["creates_canonical_mutation_authority"] is False
    assert policy["provider_scratch_is_canonical_state"] is False


def test_generation_integrity_manifest_is_fully_sealed() -> None:
    manifest = _manifest()
    for record in manifest["protected_artifacts"]:
        assert record["git_blob_sha1"]
        assert record["sha256"]
        assert isinstance(record["byte_length"], int)
        assert record["byte_length"] > 0


def test_generation_integrity_rejects_protected_byte_mutation(tmp_path: Path) -> None:
    source = ROOT / "hhs_runtime/include/hhs_runtime_exact_abi_v1_1_base.h"
    relative = "protected/exact.h"
    target = tmp_path / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    target.write_bytes(data)

    record = {
        "path": relative,
        "byte_length": len(data),
        "git_blob_sha1": verifier._git_blob_sha1(data),
        "sha256": verifier.hashlib.sha256(data).hexdigest(),
    }
    manifest = {"protected_artifacts": [record]}
    verifier._verify_artifacts(tmp_path, manifest, require_sealed=True)

    target.write_bytes(data + b"\n/* injected drift */\n")
    with pytest.raises(RuntimeError, match="protected artifact"):
        verifier._verify_artifacts(tmp_path, manifest, require_sealed=True)


def test_generation_integrity_rejects_vm81_geometry_drift(tmp_path: Path) -> None:
    source = ROOT / "hhs_runtime/include/hhs_runtime_exact_abi_v1_1_base.h"
    relative = "include/exact.h"
    target = tmp_path / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8").replace(
        "#define HHS_EXACT_VM81_FRAME_BYTES 648U",
        "#define HHS_EXACT_VM81_FRAME_BYTES 649U",
    )
    target.write_text(text, encoding="utf-8")

    manifest = deepcopy(_manifest())
    manifest["structural_constants"]["path"] = relative
    with pytest.raises(RuntimeError, match="structural constant drift"):
        verifier._verify_structural_constants(tmp_path, manifest)


def test_generation_integrity_rejects_authority_export_leak(tmp_path: Path) -> None:
    source = ROOT / "hhs_runtime/c/hhs_pass219_vm81_authority_exports.map"
    relative = "authority.map"
    target = tmp_path / relative
    target.write_text(
        source.read_text(encoding="utf-8").replace(
            "        hhs_exact_pass219_vm81_pqc_admit_signed;\n",
            "",
        ),
        encoding="utf-8",
    )
    manifest = deepcopy(_manifest())
    manifest["authority_map"]["path"] = relative
    with pytest.raises(RuntimeError, match="no longer explicitly local"):
        verifier._verify_local_authority_map(tmp_path, manifest)


def test_generation_integrity_rejects_provider_cleanup_drift(tmp_path: Path) -> None:
    source = ROOT / "hhs_runtime/c/hhs_pass219_vm81_pqc_signature_1_31.inc"
    relative = "pqc.inc"
    target = tmp_path / relative
    target.write_text(
        source.read_text(encoding="utf-8").replace(
            "OPENSSL_free(signature);",
            "/* cleanup removed */",
        ),
        encoding="utf-8",
    )
    manifest = deepcopy(_manifest())
    manifest["provider_scratch"]["path"] = relative
    with pytest.raises(RuntimeError, match="provider scratch ownership drift|unexpected OpenSSL free surface"):
        verifier._verify_provider_scratch(tmp_path, manifest)
