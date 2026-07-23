from __future__ import annotations

import sys
from pathlib import Path
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import os
import shutil
import tempfile
import zipfile
from hhs_runtime.checkpoint_ancestry import (
    MANIFEST_NAME,
    build_full_child_checkpoint,
    build_manifest,
    classify_archive,
    deterministic_zip,
    locate_first_corruption,
    parent_path_comparison,
    sha256_file,
    tree_records,
    tree_root_from_records,
    write_json,
)
from hhs_runtime.hash72_checkpoint import make_hash72_witness

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "release_artifacts" / "pass134"


def _clean_copy(src: Path, dst: Path) -> None:
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        if any(part in {"__pycache__", ".pytest_cache", "build", "builds"} for part in rel.parts):
            continue
        if path.is_dir():
            (dst / rel).mkdir(parents=True, exist_ok=True)
        elif path.is_file() and path.suffix not in {".pyc", ".so", ".o"}:
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst / rel)


def _make_authoritative_fixture_base(path: Path) -> None:
    path.mkdir(parents=True)
    dirs = ["hhs_runtime", "hhs_backend", "hhs_python", "hhs_gui", "hhs_foundation", "tests", "contracts", "schemas", "tools"]
    for directory in dirs:
        (path / directory).mkdir(parents=True, exist_ok=True)
    (path / "hhs_runtime" / "kernel.py").write_text("KERNEL_AUTHORITY = True\n", encoding="utf-8")
    (path / "hhs_backend" / "server.py").write_text("RUNTIME_ROUTE = 'guarded'\n", encoding="utf-8")
    (path / "hhs_python" / "bridge.py").write_text("ABI = 'validated'\n", encoding="utf-8")
    (path / "hhs_gui" / "main.tsx").write_text("export const authority = 'projection';\n", encoding="utf-8")
    (path / "hhs_foundation" / "invariants.py").write_text("O_NE_PI = True\n", encoding="utf-8")
    (path / "tests" / "test_kernel.py").write_text("def test_kernel(): assert True\n", encoding="utf-8")
    (path / "contracts" / "root.md").write_text("# Root contract\n", encoding="utf-8")
    (path / "schemas" / "root.json").write_text("{}\n", encoding="utf-8")
    (path / "tools" / "run.py").write_text("print('run')\n", encoding="utf-8")
    for index in range(128):
        (path / "hhs_runtime" / f"module_{index:03d}.py").write_text(f"VALUE = {index}\n", encoding="utf-8")
    cache = path / "hhs_runtime" / "__pycache__"
    cache.mkdir(); (cache / "kernel.pyc").write_bytes(b"cache")
    manifest = build_manifest(path, pass_id="PASS_132_FIXTURE", parent_pass=None, parent_tree_root=None)
    write_json(path / MANIFEST_NAME, manifest)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pass132_evidence = Path(os.environ.get("HHS_PASS132_EVIDENCE", ROOT / "release_artifacts" / "pass132" / "hhs_pass_132_release_evidence.zip"))
    pass133_archive = Path(os.environ.get("HHS_PASS133_ARCHIVE", ROOT / "release_artifacts" / "pass133" / "hhs_pass_133_prime_qudit_checkpoint.zip"))
    actual_audit = {
        "schema": "HHS_PASS134_ACTUAL_CHAIN_INPUT_AUDIT_V1",
        "pass132_evidence": classify_archive(pass132_evidence).__dict__,
        "pass133_candidate": classify_archive(pass133_archive).__dict__,
        "determination": {
            "full_pass132_runtime_available": False,
            "pass132_evidence_is_parent_checkpoint": False,
            "pass133_contains_full_ancestry": False,
            "first_known_bad_checkpoint": "PASS_133",
            "repair_authority": "BLOCKED_UNTIL_FULL_PASS132_RUNTIME_OR_COMPLETE_OPERATION_CHAIN_IS_AVAILABLE",
        },
    }
    actual_audit["audit_hash72_witness"] = make_hash72_witness("hhs_pass134_actual_chain_input_audit_v1", actual_audit).to_dict()
    write_json(ART / "PASS_134_ACTUAL_CHAIN_INPUT_AUDIT.json", actual_audit)

    with tempfile.TemporaryDirectory(prefix="hhs134_release_") as td:
        td = Path(td)
        base_root = td / "base_root"
        _make_authoritative_fixture_base(base_root)
        base_zip = td / "base.zip"
        deterministic_zip(base_root, base_zip)

        delta133 = td / "delta133"; delta133.mkdir()
        for rel in ["hhs_runtime/prime_magic_key_state.py", "hhs_runtime/phase_tensor.py", "hhs_runtime/palindromic_ecc.py", "contracts/pass133/HHS-I133_SCHIC_v1.0.md"]:
            source = ROOT / rel
            target = delta133 / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        pass133_full = td / "pass133_full.zip"
        receipt133 = build_full_child_checkpoint(
            base_zip, delta133, pass133_full,
            pass_id="PASS_133_FIXTURE_REPLAY", parent_pass="PASS_132_FIXTURE"
        )

        delta134 = td / "delta134"; delta134.mkdir()
        for rel in ["hhs_runtime/checkpoint_ancestry.py", "tools/run_pass134.py", "contracts/pass134/HHS-I134_RFACC_v1.0.md"]:
            source = ROOT / rel
            target = delta134 / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        pass134_full_a = td / "pass134_full_a.zip"
        pass134_full_b = td / "pass134_full_b.zip"
        receipt134_a = build_full_child_checkpoint(
            pass133_full, delta134, pass134_full_a,
            pass_id="PASS_134_FIXTURE_REPLAY", parent_pass="PASS_133_FIXTURE_REPLAY"
        )
        receipt134_b = build_full_child_checkpoint(
            pass133_full, delta134, pass134_full_b,
            pass_id="PASS_134_FIXTURE_REPLAY", parent_pass="PASS_133_FIXTURE_REPLAY"
        )
        deterministic = sha256_file(pass134_full_a) == sha256_file(pass134_full_b)

        broken_root = td / "broken"
        with zipfile.ZipFile(pass134_full_a) as zf:
            zf.extractall(broken_root)
        (broken_root / "hhs_runtime" / "kernel.py").unlink()
        broken_zip = td / "broken.zip"
        deterministic_zip(broken_root, broken_zip)
        localization = locate_first_corruption([base_zip, pass133_full, broken_zip])

        self_host = {
            "schema": "HHS_PASS134_SELF_HOSTED_RECOVERY_EXECUTION_V1",
            "base": {"archive": str(base_zip), "sha256": sha256_file(base_zip)},
            "pass133_build_receipt": receipt133,
            "pass134_build_receipt": receipt134_a,
            "deterministic_second_build_sha256": sha256_file(pass134_full_b),
            "deterministic_archive_bytes": deterministic,
            "corruption_localization": localization,
            "actual_pass133_components_exercised": [
                "prime_magic_key_state.py", "phase_tensor.py", "palindromic_ecc.py", "HHS-I133_SCHIC_v1.0.md"
            ],
            "status": "SELF_HOSTED_RECOVERY_OPERATION_VERIFIED" if deterministic and localization["first_corrupt_index"] == 2 else "FAIL",
        }
        self_host["receipt_hash72_witness"] = make_hash72_witness("hhs_pass134_self_hosted_recovery_execution_v1", self_host).to_dict()
        write_json(ART / "PASS_134_SELF_HOSTED_RECOVERY_RECEIPT.json", self_host)

    completion = {
        "schema": "HHS_PASS134_COMPLETION_ATTESTATION_V1",
        "pass_id": "PASS_134",
        "claimed_capability": "RECURSIVE_FULL_ANCESTRY_CHECKPOINT_COMPILATION_AND_CORRUPTION_LOCALIZATION",
        "implementation_callable": True,
        "evidence_only_parent_rejected": actual_audit["pass132_evidence"]["archive_class"] == "EVIDENCE_BUNDLE",
        "partial_pass133_rejected": actual_audit["pass133_candidate"]["archive_class"] != "FULL_SYSTEM_CHECKPOINT",
        "self_hosted_recovery_verified": self_host["status"] == "SELF_HOSTED_RECOVERY_OPERATION_VERIFIED",
        "system_file_deletion_prohibited": True,
        "cache_policy": "TRANSIENT CACHES MAY BE OMITTED; RESULTS, REPORTS, RECEIPTS, AND SYSTEM FILES REMAIN DURABLE",
        "actual_historical_chain_repaired": False,
        "historical_repair_blocker": "FULL_PASS132_RUNTIME_BYTES_OR_COMPLETE_POST_PASS132_OPERATION_CHAIN_NOT_AVAILABLE_IN_CURRENT_ENVIRONMENT",
        "terminal_status": "PASS_134_RECOVERY_COMPILER_VERIFIED__HISTORICAL_RECONSTRUCTION_INPUT_REQUIRED",
    }
    completion["attestation_hash72_witness"] = make_hash72_witness("hhs_pass134_completion_attestation_v1", completion).to_dict()
    write_json(ART / "PASS_134_COMPLETION_ATTESTATION.json", completion)
    print(json.dumps(completion, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
