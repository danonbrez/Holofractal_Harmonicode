#!/usr/bin/env python3
"""Install and verify production HHS language assets.

The script never chooses an unpinned model source. A Pass 166 Word2Vec manifest
must be supplied through HHS_WORD2VEC_MANIFEST or HHS_WORD2VEC_MANIFEST_JSON.
The manifest binds source URI, byte length, SHA-256, license, format, dimension,
and vocabulary size. Gemma is verified through the configured LiteRT-LM model
registry. The resulting status is written for deployment diagnostics.
"""
from __future__ import annotations

import argparse
import grp
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import urllib.request
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATUS_PATH = ROOT / ".hhs" / "production_language_assets_status.json"


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_production_checkout_readability(root: Path = ROOT) -> dict[str, Any]:
    """Make tracked production source readable by the configured service group.

    The guarded updater runs as root under umask 027 while hhs.service runs as
    User=hhs/Group=hhs. Git promotion and rollback can therefore replace tracked
    files with root-owned modes that the service cannot read. Only tracked files
    and their parent directories are normalized; untracked host state and secrets
    are intentionally untouched.
    """
    if os.geteuid() != 0:
        return {"normalized": False, "reason": "not-root", "tracked_files": 0}
    if not _truthy("HHS_PRODUCTION_NORMALIZE_CHECKOUT_READABILITY", default=True):
        return {"normalized": False, "reason": "disabled", "tracked_files": 0}

    group_name = os.getenv("HHS_PRODUCTION_SERVICE_GROUP", "hhs").strip() or "hhs"
    try:
        gid = grp.getgrnam(group_name).gr_gid
    except KeyError as exc:
        raise RuntimeError(f"production service group does not exist: {group_name}") from exc

    process = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    relative_paths = [
        Path(value.decode("utf-8", errors="strict"))
        for value in process.stdout.split(b"\0")
        if value
    ]
    directories: set[Path] = {root}
    normalized_files = 0

    for relative in relative_paths:
        path = root / relative
        if not path.exists() or path.is_symlink():
            continue
        current = path.stat()
        os.chown(path, -1, gid)
        os.chmod(path, stat.S_IMODE(current.st_mode) | stat.S_IRGRP)
        normalized_files += 1

        parent = path.parent
        while parent != root.parent and root in (parent, *parent.parents):
            directories.add(parent)
            if parent == root:
                break
            parent = parent.parent

    for directory in sorted(directories, key=lambda value: len(value.parts)):
        if not directory.exists() or directory.is_symlink():
            continue
        current = directory.stat()
        os.chown(directory, -1, gid)
        os.chmod(
            directory,
            stat.S_IMODE(current.st_mode) | stat.S_IRGRP | stat.S_IXGRP,
        )

    return {
        "normalized": True,
        "reason": None,
        "service_group": group_name,
        "tracked_files": normalized_files,
    }


def _load_manifest() -> Mapping[str, Any] | None:
    inline = os.getenv("HHS_WORD2VEC_MANIFEST_JSON", "").strip()
    path_value = os.getenv("HHS_WORD2VEC_MANIFEST", "").strip()
    if inline and path_value:
        raise RuntimeError(
            "set only one of HHS_WORD2VEC_MANIFEST_JSON or HHS_WORD2VEC_MANIFEST"
        )
    if inline:
        value = json.loads(inline)
        if not isinstance(value, Mapping):
            raise RuntimeError("HHS_WORD2VEC_MANIFEST_JSON must contain a JSON object")
        return dict(value)
    if path_value:
        path = Path(path_value)
        if not path.is_absolute():
            path = ROOT / path
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, Mapping):
            raise RuntimeError("HHS_WORD2VEC_MANIFEST must contain a JSON object")
        return dict(value)
    return None


def _litert_cli_status() -> dict[str, Any]:
    executable = shutil.which(os.getenv("HHS_LITERT_LM_BIN", "litert-lm"))
    if not executable:
        return {
            "installed": False,
            "executable": None,
            "version": None,
            "error": "litert-lm executable not found",
        }
    try:
        process = subprocess.run(
            [executable, "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
        version = (process.stdout or process.stderr).strip()
        return {
            "installed": True,
            "executable": executable,
            "version": version,
            "error": None,
        }
    except Exception as exc:
        return {
            "installed": False,
            "executable": executable,
            "version": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _gemma_registry_status() -> dict[str, Any]:
    base_url = os.getenv("HHS_LITERT_LM_BASE_URL", "http://127.0.0.1:9379/v1").rstrip("/")
    model_id = os.getenv("HHS_LITERT_LM_MODEL", "gemma4-12b")
    try:
        with urllib.request.urlopen(f"{base_url}/models", timeout=3.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
        model_ids = sorted({
            str(item.get("id"))
            for item in (payload.get("data") or [])
            if isinstance(item, Mapping) and item.get("id")
        })
        ready = model_id in model_ids
        return {
            "ready": ready,
            "base_url": base_url,
            "configured_model_id": model_id,
            "registered_model_ids": model_ids,
            "error": None if ready else "configured Gemma model alias is not registered",
        }
    except Exception as exc:
        return {
            "ready": False,
            "base_url": base_url,
            "configured_model_id": model_id,
            "registered_model_ids": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


def _word2vec_install(*, install_if_configured: bool) -> dict[str, Any]:
    from hhs_runtime.pass166.service import DEFAULT_WORD2VEC_SERVICE

    service = DEFAULT_WORD2VEC_SERVICE
    before = dict(service.status())
    manifest = _load_manifest()
    operation: dict[str, Any] | None = None

    if manifest is not None and install_if_configured:
        if not _truthy("HHS_WORD2VEC_ACCEPT_LICENSE"):
            raise RuntimeError(
                "HHS_WORD2VEC_ACCEPT_LICENSE=1 is required for the configured manifest"
            )
        registration = service.register_manifest(manifest)
        model_id = str(
            os.getenv("HHS_WORD2VEC_MODEL_ID")
            or manifest.get("package_id")
            or ""
        )
        if not model_id:
            raise RuntimeError("configured Word2Vec manifest has no package_id")
        current = service.status()
        if current.get("active_model_id") == model_id and current.get("offline_ready"):
            operation = {
                "classification": "P166_EXISTING_ACTIVE_MODEL_REUSED",
                "registration": registration,
                "verification": service.verify(model_id),
                "replay": service.replay(model_id),
            }
        else:
            operation = service.install(
                model_id,
                accept_license=True,
                activate=True,
                offline_ready=True,
                replace_existing=_truthy("HHS_WORD2VEC_REPLACE_EXISTING"),
                expected_pass165_frontier=os.getenv("HHS_WORD2VEC_EXPECTED_PASS165_FRONTIER") or None,
            )

    after = dict(service.status())
    ready = bool(after.get("active_model_id") and after.get("offline_ready"))
    return {
        "ready": ready,
        "manifest_configured": manifest is not None,
        "install_attempted": bool(manifest is not None and install_if_configured),
        "before": before,
        "after": after,
        "operation": operation,
        "required_configuration": (
            None
            if ready
            else [
                "HHS_WORD2VEC_MANIFEST or HHS_WORD2VEC_MANIFEST_JSON",
                "HHS_WORD2VEC_ACCEPT_LICENSE=1",
            ]
        ),
    }


def execute(*, install_if_configured: bool, require_assistant: bool) -> dict[str, Any]:
    word2vec = _word2vec_install(install_if_configured=install_if_configured)
    litert_cli = _litert_cli_status()
    gemma = _gemma_registry_status()

    from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
        HHSNativeLiteRTLMTransport,
    )

    native = HHSNativeLiteRTLMTransport().installation_status()
    assistant_ready = bool(gemma.get("ready") or native.get("ready"))
    report: dict[str, Any] = {
        "schema": "HHS_PRODUCTION_LANGUAGE_ASSET_INSTALLATION_STATUS_V1",
        "assistant_ready": assistant_ready,
        "selected_provider": (
            "provider:hhs.litert_lm.gemma4"
            if gemma.get("ready")
            else "provider:hhs.local.text"
            if native.get("ready")
            else None
        ),
        "gemma": gemma,
        "litert_lm_cli": litert_cli,
        "word2vec": word2vec,
        "native_hhs": native,
        "require_assistant": require_assistant,
        "fixture_substitution_allowed": False,
    }
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    if require_assistant and not assistant_ready:
        raise RuntimeError(
            "production assistant installation is incomplete: configure a reachable "
            "LiteRT-LM Gemma model or install an authoritative Pass 166 Word2Vec manifest"
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-if-configured", action="store_true")
    parser.add_argument("--require-assistant", action="store_true")
    args = parser.parse_args()
    require = bool(
        args.require_assistant
        or _truthy("HHS_PRODUCTION_REQUIRE_ASSISTANT", default=False)
    )
    try:
        _normalize_production_checkout_readability()
        report = execute(
            install_if_configured=args.install_if_configured,
            require_assistant=require,
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema": "HHS_PRODUCTION_LANGUAGE_ASSET_INSTALLATION_ERROR_V1",
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
