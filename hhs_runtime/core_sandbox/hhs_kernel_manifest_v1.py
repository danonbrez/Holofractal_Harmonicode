"""
HHS Kernel Manifest V1
======================

Layer 0 integrity sealing and startup verification.

This module generates and verifies Hash72 manifests for the sealed core sandbox.
Any Layer 0 byte mismatch fails closed and returns a quarantine receipt.

Canonical scope:
    hhs_runtime/core_sandbox/*.py

Security law:
    manifest mismatch -> no startup authority -> quarantine
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
import json

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44, canonicalize_for_hash72


MANIFEST_VERSION = "HHS_KERNEL_MANIFEST_V1"
DEFAULT_CORE_SANDBOX_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST_PATH = Path("security/kernel_manifest_v1.json")


class ManifestStatus(str, Enum):
    SEALED = "SEALED"
    VERIFIED = "VERIFIED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class KernelFileSeal:
    path: str
    size_bytes: int
    hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class KernelManifest:
    version: str
    root: str
    files: List[KernelFileSeal]
    manifest_hash72: str
    status: ManifestStatus

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        data["files"] = [f.to_dict() for f in self.files]
        return data


@dataclass(frozen=True)
class ManifestVerificationReceipt:
    version: str
    manifest_path: str
    status: ManifestStatus
    expected_manifest_hash72: str | None
    actual_manifest_hash72: str | None
    mismatches: List[Dict[str, object]]
    missing_files: List[str]
    unexpected_files: List[str]
    receipt_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


def _repo_root_from_core(core_dir: Path = DEFAULT_CORE_SANDBOX_DIR) -> Path:
    # .../repo/hhs_runtime/core_sandbox -> repo
    return core_dir.resolve().parents[1]


def _relative(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def iter_kernel_files(core_dir: Path = DEFAULT_CORE_SANDBOX_DIR) -> List[Path]:
    files = []
    for path in core_dir.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return sorted(files, key=lambda p: str(p))


def hash_file(path: Path) -> str:
    data = path.read_bytes()
    # latin1 preserves raw byte values one-to-one for deterministic hashing.
    payload = {"path": path.name, "size_bytes": len(data), "bytes_latin1": data.decode("latin1")}
    return security_hash72_v44(payload, domain="HHS_KERNEL_FILE")


def seal_file(path: Path, repo_root: Path) -> KernelFileSeal:
    data = path.read_bytes()
    return KernelFileSeal(path=_relative(path, repo_root), size_bytes=len(data), hash72=hash_file(path))


def compute_manifest_hash(root: str, files: Sequence[KernelFileSeal]) -> str:
    payload = {
        "version": MANIFEST_VERSION,
        "root": root,
        "files": [f.to_dict() for f in files],
    }
    return security_hash72_v44(payload, domain="HHS_KERNEL_MANIFEST")


def generate_kernel_manifest(core_dir: Path = DEFAULT_CORE_SANDBOX_DIR) -> KernelManifest:
    core_dir = Path(core_dir)
    repo_root = _repo_root_from_core(core_dir)
    files = [seal_file(path, repo_root) for path in iter_kernel_files(core_dir)]
    root = _relative(core_dir, repo_root)
    manifest_hash = compute_manifest_hash(root, files)
    return KernelManifest(MANIFEST_VERSION, root, files, manifest_hash, ManifestStatus.SEALED)


def write_kernel_manifest(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    core_dir: str | Path = DEFAULT_CORE_SANDBOX_DIR,
) -> KernelManifest:
    manifest = generate_kernel_manifest(Path(core_dir))
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return manifest


def load_kernel_manifest(manifest_path: str | Path = DEFAULT_MANIFEST_PATH) -> KernelManifest:
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    files = [KernelFileSeal(**f) for f in data.get("files", [])]
    return KernelManifest(
        version=data.get("version", MANIFEST_VERSION),
        root=data.get("root", "hhs_runtime/core_sandbox"),
        files=files,
        manifest_hash72=data.get("manifest_hash72", ""),
        status=ManifestStatus(data.get("status", ManifestStatus.SEALED.value)),
    )


def verify_kernel_manifest(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    repo_root: str | Path | None = None,
) -> ManifestVerificationReceipt:
    manifest_path = Path(manifest_path)
    if repo_root is None:
        repo_root = Path.cwd()
    repo_root = Path(repo_root)

    try:
        expected = load_kernel_manifest(manifest_path)
    except Exception as exc:
        quarantine = security_hash72_v44({"manifest_load_error": type(exc).__name__, "message": str(exc)}, domain="HHS_KERNEL_MANIFEST_QUARANTINE")
        receipt = security_hash72_v44({"status": "QUARANTINED", "reason": "manifest_load_error", "quarantine": quarantine}, domain="HHS_KERNEL_MANIFEST_VERIFY")
        return ManifestVerificationReceipt(MANIFEST_VERSION, str(manifest_path), ManifestStatus.QUARANTINED, None, None, [{"error": type(exc).__name__, "message": str(exc)}], [], [], receipt, quarantine)

    expected_by_path = {f.path: f for f in expected.files}
    root_dir = repo_root / expected.root
    actual_files = [seal_file(p, repo_root) for p in iter_kernel_files(root_dir)] if root_dir.exists() else []
    actual_by_path = {f.path: f for f in actual_files}

    mismatches: List[Dict[str, object]] = []
    missing = []
    for path, exp in expected_by_path.items():
        actual = actual_by_path.get(path)
        if actual is None:
            missing.append(path)
            continue
        if actual.hash72 != exp.hash72 or actual.size_bytes != exp.size_bytes:
            mismatches.append({
                "path": path,
                "expected_hash72": exp.hash72,
                "actual_hash72": actual.hash72,
                "expected_size": exp.size_bytes,
                "actual_size": actual.size_bytes,
            })
    unexpected = sorted(set(actual_by_path) - set(expected_by_path))
    actual_manifest_hash = compute_manifest_hash(expected.root, actual_files)
    manifest_hash_ok = actual_manifest_hash == expected.manifest_hash72

    ok = not mismatches and not missing and not unexpected and manifest_hash_ok
    status = ManifestStatus.VERIFIED if ok else ManifestStatus.QUARANTINED
    quarantine = None
    if not ok:
        quarantine = security_hash72_v44({
            "mismatches": mismatches,
            "missing": missing,
            "unexpected": unexpected,
            "expected_manifest_hash72": expected.manifest_hash72,
            "actual_manifest_hash72": actual_manifest_hash,
        }, domain="HHS_KERNEL_MANIFEST_QUARANTINE")
    receipt = security_hash72_v44({
        "version": MANIFEST_VERSION,
        "manifest_path": str(manifest_path),
        "status": status.value,
        "expected_manifest_hash72": expected.manifest_hash72,
        "actual_manifest_hash72": actual_manifest_hash,
        "mismatches": mismatches,
        "missing": missing,
        "unexpected": unexpected,
        "quarantine": quarantine,
    }, domain="HHS_KERNEL_MANIFEST_VERIFY")
    return ManifestVerificationReceipt(MANIFEST_VERSION, str(manifest_path), status, expected.manifest_hash72, actual_manifest_hash, mismatches, missing, unexpected, receipt, quarantine)


def startup_integrity_guard(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    repo_root: str | Path | None = None,
    *,
    raise_on_fail: bool = True,
) -> ManifestVerificationReceipt:
    receipt = verify_kernel_manifest(manifest_path, repo_root)
    if raise_on_fail and receipt.status != ManifestStatus.VERIFIED:
        raise RuntimeError(f"Kernel integrity verification failed: {receipt.to_dict()}")
    return receipt


def demo() -> Dict[str, object]:
    manifest = generate_kernel_manifest()
    return {"manifest_hash72": manifest.manifest_hash72, "file_count": len(manifest.files), "root": manifest.root}


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
