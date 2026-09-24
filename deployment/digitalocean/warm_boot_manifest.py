#!/usr/bin/env python3
"""Seal and verify the warm-boot identity of the production HHS VM.

Promotion may build the native runtime and Runtime OS once. Service restart may
only verify/adopt those sealed artifacts and durable state roots. This module
never invokes a compiler, package manager, build tool, hydration generator, or
canonical mutation path.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import subprocess
from typing import Any


SCHEMA = "HHS_PASS_220_I046_WARM_HYDRATED_VM_BOOT_V1"

# Mutable databases evolve through canonical admission and are never hashed
# on restart. Previously sealed keys must retain identity across reopens.
PERSISTENT_COMPONENTS: dict[str, tuple[str, ...]] = {
    "pass174": ("hash216_vectors.sqlite3", "hash216_vectors.key"),
    "pass194": (
        "pass194.sqlite3", "pass194_vectors.sqlite3", "pass194_vectors.key",
    ),
    "pass205_db": ("continuation.sqlite3",),
    "pass213_surface": (
        "public-projections.sqlite3", "projection.key", "capability.key",
    ),
    "lane5": (
        "lane5_composition_memory.sqlite3",
        "lane5_composition_vectors.sqlite3",
        "lane5_composition_vectors.key",
    ),
}


class WarmBootError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _head(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or len(value) != 40:
        raise WarmBootError("HHS_WARM_BOOT_REPOSITORY_HEAD_UNAVAILABLE")
    return value


def _runtime_library(repo_root: Path) -> Path:
    system = platform.system().lower()
    if system == "windows":
        name = "hhs_runtime.dll"
    elif system == "darwin":
        name = "libhhs_runtime.dylib"
    else:
        name = "libhhs_runtime.so"
    return repo_root / "hhs_runtime" / "builds" / name


def _state_roots() -> dict[str, str]:
    return {
        "runtime_data": os.environ.get(
            "HHS_DATA_DIR", "/var/lib/hhs/data"
        ),
        "pass174": os.environ.get(
            "HHS_PASS174_STATE_DIR", "/var/lib/hhs/pass174"
        ),
        "pass194": os.environ.get(
            "HHS_PASS194_STATE_ROOT", "/var/lib/hhs/pass194"
        ),
        "pass205_db": os.environ.get(
            "HHS_PASS205_DB", "/var/lib/hhs/pass205/continuation.sqlite3"
        ),
        "pass213_surface": os.environ.get(
            "HHS_PASS213_SURFACE_STATE_DIR", "/var/lib/hhs/pass213/surface"
        ),
        "pass218": os.environ.get(
            "HHS_PASS218_STATE_ROOT", "/var/lib/hhs/pass218"
        ),
        "lane5": os.environ.get(
            "HHS_PASS219_LANE5_STATE_ROOT", "/var/lib/hhs/pass219/lane5"
        ),
        "runtime_bootstrap": os.environ.get(
            "HHS_RUNTIME_BOOTSTRAP_ROOT", "/var/lib/hhs/runtime-bootstrap"
        ),
    }


def _root_directory(name: str, value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if name == "pass205_db":
        return path.parent
    return path


def _persistent_inventory(state: dict[str, str]) -> dict[str, Any]:
    """Inspect existing persistent artifacts without creating a database/key."""
    components: dict[str, dict[str, Any]] = {}
    all_present = True
    for namespace, names in PERSISTENT_COMPONENTS.items():
        root = _root_directory(namespace, state[namespace])
        entries: dict[str, dict[str, Any]] = {}
        for name in names:
            path = root / name
            exists = path.is_file()
            if not exists:
                all_present = False
            size = path.stat().st_size if exists else 0
            if exists and size == 0:
                raise WarmBootError(
                    f"HHS_WARM_BOOT_PERSISTENCE_ARTIFACT_EMPTY:{namespace}:{name}"
                )
            entry: dict[str, Any] = {"present": exists}
            if exists and name.endswith(".key"):
                entry["sha256"] = _sha256(path)
            entries[name] = entry
        components[namespace] = entries
    return {
        "components": components,
        "hydration_classification": (
            "PERSISTENCE_PRESENT" if all_present else "PERSISTENCE_PARTIAL"
        ),
        "all_configured_artifacts_present": all_present,
        # A public projection DB does not prove protected compiled-ROM recovery.
        "protected_compiled_rom_recovery_verified": False,
    }


def _verify_persistence(
    expected: dict[str, Any], current: dict[str, Any]
) -> None:
    if expected.get("components") is None:
        raise WarmBootError("HHS_WARM_BOOT_PERSISTENCE_INVENTORY_MISSING")
    for namespace, entries in expected["components"].items():
        actual_entries = current["components"].get(namespace, {})
        for name, recorded in entries.items():
            actual = actual_entries.get(name, {})
            if recorded.get("present") and not actual.get("present"):
                raise WarmBootError(
                    f"HHS_WARM_BOOT_PERSISTENT_ARTIFACT_LOST:{namespace}:{name}"
                )
            if recorded.get("sha256") and (
                recorded["sha256"] != actual.get("sha256")
            ):
                raise WarmBootError(
                    f"HHS_WARM_BOOT_PERSISTENT_KEY_CHANGED:{namespace}:{name}"
                )


def _artifact_payload(repo_root: Path, runtime_os_root: Path) -> dict[str, Any]:
    native = _runtime_library(repo_root)
    index = runtime_os_root / "index.html"
    assets = runtime_os_root / "assets"
    if not native.is_file():
        raise WarmBootError(f"HHS_WARM_BOOT_NATIVE_RUNTIME_MISSING:{native}")
    if not index.is_file():
        raise WarmBootError(f"HHS_WARM_BOOT_RUNTIME_OS_INDEX_MISSING:{index}")
    if not assets.is_dir():
        raise WarmBootError(f"HHS_WARM_BOOT_RUNTIME_OS_ASSETS_MISSING:{assets}")
    return {
        "native_runtime": {
            "path": str(native.resolve()),
            "sha256": _sha256(native),
        },
        "runtime_os": {
            "root": str(runtime_os_root.resolve()),
            "index": str(index.resolve()),
            "index_sha256": _sha256(index),
            "assets": str(assets.resolve()),
        },
    }


def create_manifest(
    *, repo_root: Path, runtime_os_root: Path, manifest_root: Path
) -> Path:
    head = _head(repo_root)
    state = _state_roots()
    for name, value in state.items():
        root = _root_directory(name, value)
        if not root.is_dir():
            raise WarmBootError(f"HHS_WARM_BOOT_STATE_ROOT_MISSING:{name}:{root}")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "repository_sha": head,
        "repository_root": str(repo_root.resolve()),
        "artifacts": _artifact_payload(repo_root, runtime_os_root),
        "state_roots": state,
        "persistence_inventory": _persistent_inventory(state),
        "boot_policy": {
            "autobuild_forbidden": True,
            "compile_on_restart": False,
            "rehydrate_from_empty_on_restart": False,
            "adopt_persistent_state": True,
            "canonical_state_authority": False,
            "new_vm81_authority": False,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["manifest_sha256"] = sha256(canonical).hexdigest()

    manifest_root.mkdir(parents=True, exist_ok=True)
    destination = manifest_root / f"{head}.json"
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, destination)
    return destination


def verify_manifest(*, repo_root: Path, manifest_root: Path) -> dict[str, Any]:
    if os.environ.get("HHS_DISABLE_C_AUTOBUILD", "").strip().lower() not in {
        "1", "true", "yes", "on"
    }:
        raise WarmBootError("HHS_WARM_BOOT_AUTOBUILD_NOT_DISABLED")

    head = _head(repo_root)
    manifest_path = manifest_root / f"{head}.json"
    if not manifest_path.is_file():
        raise WarmBootError(f"HHS_WARM_BOOT_MANIFEST_MISSING:{manifest_path}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise WarmBootError("HHS_WARM_BOOT_SCHEMA_MISMATCH")
    if payload.get("repository_sha") != head:
        raise WarmBootError("HHS_WARM_BOOT_REPOSITORY_SHA_MISMATCH")

    claimed_digest = payload.pop("manifest_sha256", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    actual_manifest_digest = sha256(canonical).hexdigest()
    payload["manifest_sha256"] = claimed_digest
    if claimed_digest != actual_manifest_digest:
        raise WarmBootError("HHS_WARM_BOOT_MANIFEST_DIGEST_MISMATCH")

    artifacts = payload["artifacts"]
    native = Path(artifacts["native_runtime"]["path"])
    index = Path(artifacts["runtime_os"]["index"])
    runtime_root = Path(artifacts["runtime_os"]["root"])
    assets = Path(artifacts["runtime_os"]["assets"])

    if not native.is_file() or _sha256(native) != artifacts["native_runtime"]["sha256"]:
        raise WarmBootError("HHS_WARM_BOOT_NATIVE_RUNTIME_IDENTITY_MISMATCH")
    if not index.is_file() or _sha256(index) != artifacts["runtime_os"]["index_sha256"]:
        raise WarmBootError("HHS_WARM_BOOT_RUNTIME_OS_IDENTITY_MISMATCH")
    if not runtime_root.is_dir() or not assets.is_dir():
        raise WarmBootError("HHS_WARM_BOOT_RUNTIME_OS_RELEASE_MISSING")

    current_state = _state_roots()
    if current_state != payload["state_roots"]:
        raise WarmBootError("HHS_WARM_BOOT_STATE_ROOT_BINDING_MISMATCH")
    for name, value in current_state.items():
        root = _root_directory(name, value)
        if not root.is_dir():
            raise WarmBootError(f"HHS_WARM_BOOT_STATE_ROOT_MISSING:{name}:{root}")
        if not os.access(root, os.R_OK | os.X_OK):
            raise WarmBootError(f"HHS_WARM_BOOT_STATE_ROOT_UNREADABLE:{name}:{root}")

    observed_persistence = _persistent_inventory(current_state)
    sealed_persistence = payload.get("persistence_inventory", {})
    _verify_persistence(sealed_persistence, observed_persistence)
    fully_sealed = bool(
        sealed_persistence.get("all_configured_artifacts_present")
        and observed_persistence["all_configured_artifacts_present"]
    )

    return {
        "schema": SCHEMA,
        "repository_sha": head,
        "manifest": str(manifest_path),
        "native_runtime_adopted": True,
        "runtime_os_adopted": True,
        "persistent_roots_adopted": True,
        "persistent_state_adopted": fully_sealed,
        "hydration_classification": (
            "PERSISTENCE_SEALED" if fully_sealed else "PERSISTENCE_PARTIAL_OR_UNSEALED"
        ),
        "protected_compiled_rom_recovery_verified": False,
        "compile_on_restart": False,
        "rehydrate_from_empty_on_restart": False,
        "canonical_state_authority": False,
        "new_vm81_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--repo-root", default="/opt/hhs/app")
    create.add_argument("--runtime-os-root", default="/var/lib/hhs/runtime-os/current")
    create.add_argument(
        "--manifest-root", default="/var/lib/hhs/warm-boot/releases"
    )

    verify = sub.add_parser("verify")
    verify.add_argument("--repo-root", default="/opt/hhs/app")
    verify.add_argument(
        "--manifest-root", default="/var/lib/hhs/warm-boot/releases"
    )

    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest_root = Path(args.manifest_root).resolve()

    if args.command == "create":
        path = create_manifest(
            repo_root=repo_root,
            runtime_os_root=Path(args.runtime_os_root).resolve(),
            manifest_root=manifest_root,
        )
        print(f"HHS_WARM_BOOT_MANIFEST_CREATED={path}")
        return 0

    result = verify_manifest(repo_root=repo_root, manifest_root=manifest_root)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
