#!/usr/bin/env python3
"""Provision the pinned production-native causal language egress model.

The model is non-authoritative natural-language egress only.  This provisioner
does not grant VM81, Hash72, Hash216, filesystem, repository, or deployment
mutation authority to model output.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import grp
import stat
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

MODEL_REPOSITORY = "HuggingFaceTB/SmolLM2-360M-Instruct"
MODEL_REVISION = "a10cc1512eabd3dde888204e902eca88bddb4951"
MODEL_WEIGHT_SHA256 = "e6bffe7435d7ddc10fd3b9a9efd429dafbacb1cb17015fb5562664e7532bf86e"
MODEL_ID = "smollm2-360m-instruct-a10cc1512ea"
DEFAULT_MODEL_ROOT = Path("/var/lib/hhs/models/native-causal")
DEFAULT_STATUS_PATH = Path(
    "/var/lib/hhs/runtime-bootstrap/native_causal_model_status.json"
)
REQUIREMENTS_PATH = ROOT / "requirements-native-causal-lm.txt"

EXPECTED_RUNTIME_VERSIONS = {
    "transformers": "4.57.6",
    "torch": "2.14.1+cpu",
}
TORCH_CPU_INDEX_URL = "https://download.pytorch.org/whl/cpu"

ALLOWED_MODEL_FILES = (
    "config.json",
    "generation_config.json",
    "model.safetensors",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "merges.txt",
    "vocab.json",
)

REQUIRED_MODEL_FILES = (
    "config.json",
    "model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _model_root() -> Path:
    raw = os.getenv("HHS_NATIVE_CAUSAL_LM_ROOT", "").strip()
    return Path(raw) if raw else DEFAULT_MODEL_ROOT


def model_path() -> Path:
    return _model_root() / MODEL_ID


def _status_path() -> Path:
    raw = os.getenv("HHS_NATIVE_CAUSAL_LM_STATUS_PATH", "").strip()
    return Path(raw) if raw else DEFAULT_STATUS_PATH


def _installed_versions() -> dict[str, str | None]:
    values: dict[str, str | None] = {}
    for package in EXPECTED_RUNTIME_VERSIONS:
        try:
            values[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            values[package] = None
    return values


def _run_pip(arguments: list[str], *, timeout: int = 1800) -> None:
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            *arguments,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if process.returncode != 0:
        detail = (process.stderr or process.stdout or "").strip()
        if len(detail) > 12000:
            detail = detail[-12000:]
        raise RuntimeError(
            f"pip install failed with exit {process.returncode}: {detail}"
        )


def _torch_cpu_runtime() -> dict[str, Any]:
    try:
        import torch
    except Exception as exc:
        return {
            "ready": False,
            "version": _installed_versions().get("torch"),
            "cuda_version": None,
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {
        "ready": bool(
            str(getattr(torch, "__version__", "")) == EXPECTED_RUNTIME_VERSIONS["torch"]
            and getattr(getattr(torch, "version", None), "cuda", None) is None
        ),
        "version": str(getattr(torch, "__version__", "")),
        "cuda_version": getattr(getattr(torch, "version", None), "cuda", None),
        "error": None,
    }


def _runtime_ready() -> bool:
    versions = _installed_versions()
    if versions.get("transformers") != EXPECTED_RUNTIME_VERSIONS["transformers"]:
        return False
    if versions.get("torch") != EXPECTED_RUNTIME_VERSIONS["torch"]:
        return False
    return bool(_torch_cpu_runtime().get("ready"))


def _install_runtime() -> dict[str, Any]:
    before = _installed_versions()
    if not REQUIREMENTS_PATH.is_file():
        raise RuntimeError(
            f"native causal requirements file missing: {REQUIREMENTS_PATH}"
        )

    if before.get("torch") != EXPECTED_RUNTIME_VERSIONS["torch"] or not _torch_cpu_runtime().get("ready"):
        _run_pip([
            f"torch=={EXPECTED_RUNTIME_VERSIONS['torch']}",
            "--index-url",
            TORCH_CPU_INDEX_URL,
        ])

    current = _installed_versions()
    if current.get("transformers") != EXPECTED_RUNTIME_VERSIONS["transformers"]:
        _run_pip(["--requirement", str(REQUIREMENTS_PATH)])

    after = _installed_versions()
    torch_cpu = _torch_cpu_runtime()
    mismatches = {
        package: {
            "expected": expected,
            "actual": after.get(package),
        }
        for package, expected in EXPECTED_RUNTIME_VERSIONS.items()
        if after.get(package) != expected
    }
    if mismatches or not torch_cpu.get("ready"):
        raise RuntimeError(
            f"native causal runtime verification failed: versions={mismatches} "
            f"torch_cpu={torch_cpu}"
        )
    return {
        "before": before,
        "after": after,
        "requirements_path": str(REQUIREMENTS_PATH),
        "torch_cpu_index_url": TORCH_CPU_INDEX_URL,
        "torch_cpu": torch_cpu,
        "exact_versions_verified": True,
    }


def _ensure_model() -> dict[str, Any]:
    target = model_path()
    target.mkdir(parents=True, exist_ok=True)

    weight = target / "model.safetensors"
    existing_valid = (
        all((target / name).is_file() for name in REQUIRED_MODEL_FILES)
        and weight.is_file()
        and _sha256_file(weight) == MODEL_WEIGHT_SHA256
    )

    if not existing_valid:
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        from huggingface_hub import snapshot_download

        snapshot_download(
            repo_id=MODEL_REPOSITORY,
            revision=MODEL_REVISION,
            local_dir=str(target),
            allow_patterns=list(ALLOWED_MODEL_FILES),
        )

    missing = [
        name for name in REQUIRED_MODEL_FILES if not (target / name).is_file()
    ]
    if missing:
        raise RuntimeError(
            f"pinned native causal model is incomplete; missing={missing}"
        )

    actual_weight_sha256 = _sha256_file(weight)
    if actual_weight_sha256 != MODEL_WEIGHT_SHA256:
        raise RuntimeError(
            "pinned native causal model weight identity mismatch: "
            f"{actual_weight_sha256} != {MODEL_WEIGHT_SHA256}"
        )

    files: dict[str, dict[str, Any]] = {}
    for path in sorted(target.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        files[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }

    return {
        "repository": MODEL_REPOSITORY,
        "revision": MODEL_REVISION,
        "model_id": MODEL_ID,
        "model_path": str(target),
        "model_weight_sha256": actual_weight_sha256,
        "required_files": list(REQUIRED_MODEL_FILES),
        "files": files,
        "network_download_required_after_provisioning": False,
    }


def _normalize_permissions(path: Path) -> dict[str, Any]:
    if os.geteuid() != 0:
        return {"normalized": False, "reason": "not-root"}

    group_name = os.getenv("HHS_PRODUCTION_SERVICE_GROUP", "hhs").strip() or "hhs"
    try:
        gid = grp.getgrnam(group_name).gr_gid
    except KeyError as exc:
        raise RuntimeError(
            f"production service group does not exist: {group_name}"
        ) from exc

    roots = [
        _model_root(),
        model_path(),
    ]
    for root in roots:
        if not root.exists():
            continue
        os.chown(root, -1, gid)
        current = root.stat()
        os.chmod(
            root,
            stat.S_IMODE(current.st_mode)
            | stat.S_IRGRP
            | stat.S_IXGRP,
        )

    for path in model_path().rglob("*"):
        if path.is_symlink():
            continue
        os.chown(path, -1, gid)
        current = path.stat()
        mode = stat.S_IMODE(current.st_mode)
        if path.is_dir():
            os.chmod(path, mode | stat.S_IRGRP | stat.S_IXGRP)
        else:
            os.chmod(path, mode | stat.S_IRGRP)

    return {
        "normalized": True,
        "service_group": group_name,
    }


def _verify_transformers_load() -> dict[str, Any]:
    os.environ["HHS_NATIVE_CAUSAL_LM_MODEL"] = str(model_path())
    os.environ["HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY"] = "1"

    from transformers import AutoConfig, AutoTokenizer

    config = AutoConfig.from_pretrained(
        str(model_path()),
        local_files_only=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        str(model_path()),
        local_files_only=True,
    )
    return {
        "config_model_type": str(getattr(config, "model_type", "")),
        "tokenizer_class": type(tokenizer).__name__,
        "vocabulary_size": int(getattr(tokenizer, "vocab_size", 0) or 0),
        "local_files_only": True,
    }


def provision(*, install: bool) -> dict[str, Any]:
    runtime = _install_runtime() if install else {
        "before": _installed_versions(),
        "after": _installed_versions(),
        "requirements_path": str(REQUIREMENTS_PATH),
        "exact_versions_verified": _runtime_ready(),
    }
    if not runtime["exact_versions_verified"]:
        raise RuntimeError(
            "native causal runtime is not installed at the pinned versions"
        )

    model = _ensure_model() if install else _verify_existing_model()
    permissions = _normalize_permissions(model_path())
    load_probe = _verify_transformers_load()

    report = {
        "schema": "HHS_PRODUCTION_NATIVE_CAUSAL_MODEL_STATUS_V1",
        "ok": True,
        "natural_language_egress_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mutation_authority": False,
        "canonical_hash216_mutation_authority": False,
        "runtime": runtime,
        "model": model,
        "permissions": permissions,
        "load_probe": load_probe,
    }

    status_path = _status_path()
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    if os.geteuid() == 0:
        try:
            gid = grp.getgrnam(
                os.getenv("HHS_PRODUCTION_SERVICE_GROUP", "hhs").strip() or "hhs"
            ).gr_gid
            os.chown(status_path, -1, gid)
            os.chmod(status_path, 0o640)
        except KeyError:
            pass

    return report


def _verify_existing_model() -> dict[str, Any]:
    target = model_path()
    missing = [
        name for name in REQUIRED_MODEL_FILES if not (target / name).is_file()
    ]
    if missing:
        raise RuntimeError(
            f"pinned native causal model is not provisioned; missing={missing}"
        )
    weight = target / "model.safetensors"
    actual = _sha256_file(weight)
    if actual != MODEL_WEIGHT_SHA256:
        raise RuntimeError(
            f"pinned native causal model weight identity mismatch: {actual}"
        )
    files = {
        path.name: {
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in sorted(target.iterdir())
        if path.is_file() and not path.name.startswith(".")
    }
    return {
        "repository": MODEL_REPOSITORY,
        "revision": MODEL_REVISION,
        "model_id": MODEL_ID,
        "model_path": str(target),
        "model_weight_sha256": actual,
        "required_files": list(REQUIRED_MODEL_FILES),
        "files": files,
        "network_download_required_after_provisioning": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--print-model-path", action="store_true")
    args = parser.parse_args()

    if args.print_model_path:
        print(model_path())
        return 0

    try:
        report = provision(install=args.install)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema": "HHS_PRODUCTION_NATIVE_CAUSAL_MODEL_ERROR_V1",
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1

    print(json.dumps(report, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
