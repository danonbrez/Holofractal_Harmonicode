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
from hashlib import sha256
import importlib.metadata
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


def _production_status_path() -> Path:
    configured = os.getenv("HHS_PRODUCTION_LANGUAGE_STATUS_PATH", "").strip()
    if configured:
        return Path(configured)
    return ROOT / ".hhs" / "production_language_assets_status.json"


STATUS_PATH = _production_status_path()

NATIVE_CAUSAL_REQUIREMENTS = ROOT / "requirements-native-causal-lm.txt"
NATIVE_CAUSAL_MODEL_REPO = "HuggingFaceTB/SmolLM2-135M-Instruct"
NATIVE_CAUSAL_MODEL_REVISION = "ee72e5415c002e8fc0566a191a07c0b2b708875a"
NATIVE_CAUSAL_MODEL_FILE_SHA256 = "5af571cbf074e6d21a03528d2330792e532ca608f24ac70a143f6b369968ab8c"
NATIVE_CAUSAL_MODEL_ROOT = Path(
    os.getenv(
        "HHS_NATIVE_CAUSAL_LM_INSTALL_ROOT",
        "/var/lib/hhs/native-language/models/"
        "smollm2-135m-instruct-ee72e5415c002e8fc0566a191a07c0b2b708875a",
    )
)
NATIVE_CAUSAL_PACKAGE_VERSIONS = {
    "torch": "2.5.1+cpu",
    "transformers": "4.46.3",
    "huggingface-hub": "0.26.2",
    "safetensors": "0.4.5",
    "tokenizers": "0.20.3",
}


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


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _native_causal_packages_ready() -> tuple[bool, dict[str, str | None]]:
    observed: dict[str, str | None] = {}
    ready = True
    for package, expected in NATIVE_CAUSAL_PACKAGE_VERSIONS.items():
        try:
            actual = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            actual = None
        observed[package] = actual
        if actual != expected:
            ready = False
    return ready, observed


def _install_native_causal_packages() -> dict[str, Any]:
    ready_before, before = _native_causal_packages_ready()
    if not ready_before:
        if not NATIVE_CAUSAL_REQUIREMENTS.is_file():
            raise RuntimeError(
                f"native causal requirements missing: {NATIVE_CAUSAL_REQUIREMENTS}"
            )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-cache-dir",
                "-r",
                str(NATIVE_CAUSAL_REQUIREMENTS),
            ],
            cwd=ROOT,
            check=True,
            timeout=1800,
        )
    ready_after, after = _native_causal_packages_ready()
    if not ready_after:
        raise RuntimeError(
            f"native causal runtime dependency closure failed: {after}"
        )
    return {
        "ready": True,
        "installed_now": not ready_before,
        "before": before,
        "after": after,
        "requirements": str(NATIVE_CAUSAL_REQUIREMENTS),
    }


def _normalize_model_readability(model_root: Path) -> dict[str, Any]:
    if os.geteuid() != 0:
        return {"normalized": False, "reason": "not-root"}
    group_name = os.getenv("HHS_PRODUCTION_SERVICE_GROUP", "hhs").strip() or "hhs"
    try:
        gid = grp.getgrnam(group_name).gr_gid
    except KeyError as exc:
        raise RuntimeError(
            f"production service group does not exist: {group_name}"
        ) from exc

    changed = 0
    for path in [model_root, *model_root.rglob("*")]:
        if path.is_symlink() or not path.exists():
            continue
        current = path.stat()
        os.chown(path, -1, gid)
        mode = stat.S_IMODE(current.st_mode) | stat.S_IRGRP
        if path.is_dir():
            mode |= stat.S_IXGRP
        os.chmod(path, mode)
        changed += 1
    return {
        "normalized": True,
        "service_group": group_name,
        "paths": changed,
    }


def _install_pinned_native_causal_model() -> dict[str, Any]:
    _install_native_causal_packages()
    from huggingface_hub import snapshot_download

    NATIVE_CAUSAL_MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    model_file = NATIVE_CAUSAL_MODEL_ROOT / "model.safetensors"
    existing_ok = (
        model_file.is_file()
        and _sha256_file(model_file) == NATIVE_CAUSAL_MODEL_FILE_SHA256
    )
    if not existing_ok:
        snapshot_download(
            repo_id=NATIVE_CAUSAL_MODEL_REPO,
            revision=NATIVE_CAUSAL_MODEL_REVISION,
            local_dir=str(NATIVE_CAUSAL_MODEL_ROOT),
            allow_patterns=[
                "config.json",
                "generation_config.json",
                "model.safetensors",
                "tokenizer.json",
                "tokenizer_config.json",
                "special_tokens_map.json",
            ],
        )
    if not model_file.is_file():
        raise RuntimeError(f"pinned native causal model file missing: {model_file}")
    actual_sha256 = _sha256_file(model_file)
    if actual_sha256 != NATIVE_CAUSAL_MODEL_FILE_SHA256:
        raise RuntimeError(
            "pinned native causal model SHA-256 mismatch: "
            f"expected={NATIVE_CAUSAL_MODEL_FILE_SHA256} actual={actual_sha256}"
        )
    permissions = _normalize_model_readability(NATIVE_CAUSAL_MODEL_ROOT)
    return {
        "ready": True,
        "model_root": str(NATIVE_CAUSAL_MODEL_ROOT),
        "repo_id": NATIVE_CAUSAL_MODEL_REPO,
        "revision": NATIVE_CAUSAL_MODEL_REVISION,
        "model_file_sha256": actual_sha256,
        "downloaded_now": not existing_ok,
        "permissions": permissions,
    }


def _native_causal_smoke(model_path: str) -> dict[str, Any]:
    env = dict(os.environ)
    env.update({
        "PYTHONPATH": str(ROOT),
        "HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC": "0",
        "HHS_NATIVE_CAUSAL_LM_MODEL": model_path,
        "HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY": "1",
        "HHS_NATIVE_CAUSAL_LM_CPU_FLOAT32": "1",
        "HHS_NATIVE_CAUSAL_LM_MAX_NEW_TOKENS": "128",
        "HHS_NATIVE_RESPONSE_BLOCK_MAX_NEW_TOKENS": "128",
        "HHS_NATIVE_RESPONSE_MAX_BLOCKS": "2",
        "HHS_NATIVE_LANGUAGE_GENERATION_TIMEOUT_SECONDS": "60",
    })
    process = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "hhs_native_chat_cli.py"),
            "--prompt",
            "Explain in two concise sentences why ice floats on liquid water.",
            "--strict-generation",
            "--json",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if process.returncode != 0:
        raise RuntimeError(
            "native causal CLI smoke failed: "
            + (process.stderr or process.stdout)[-4000:]
        )
    return {
        "ready": True,
        "returncode": process.returncode,
        "stdout_tail": process.stdout[-4000:],
    }


def _native_causal_install(
    *,
    install_if_configured: bool,
    require_assistant: bool,
) -> dict[str, Any]:
    configured = os.getenv("HHS_NATIVE_CAUSAL_LM_MODEL", "").strip()
    auto_install = _truthy(
        "HHS_NATIVE_CAUSAL_LM_AUTO_INSTALL",
        default=require_assistant,
    )
    package_report: dict[str, Any] | None = None
    model_report: dict[str, Any] | None = None

    if configured:
        if install_if_configured:
            package_report = _install_native_causal_packages()
        model_path = configured
    elif install_if_configured and auto_install:
        package_report = _install_native_causal_packages()
        model_report = _install_pinned_native_causal_model()
        model_path = str(NATIVE_CAUSAL_MODEL_ROOT)
        os.environ["HHS_NATIVE_CAUSAL_LM_MODEL"] = model_path
    else:
        return {
            "ready": False,
            "configured": False,
            "auto_install": auto_install,
            "model_path": None,
            "package_runtime": package_report,
            "model": model_report,
            "smoke": None,
        }

    os.environ.setdefault("HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY", "1")
    os.environ.setdefault("HHS_NATIVE_CAUSAL_LM_CPU_FLOAT32", "1")
    os.environ.setdefault("HHS_NATIVE_CAUSAL_LM_MAX_NEW_TOKENS", "128")
    os.environ.setdefault("HHS_NATIVE_RESPONSE_BLOCK_MAX_NEW_TOKENS", "128")
    os.environ.setdefault("HHS_NATIVE_RESPONSE_MAX_BLOCKS", "2")
    os.environ.setdefault("HHS_NATIVE_LANGUAGE_GENERATION_TIMEOUT_SECONDS", "60")

    smoke = (
        _native_causal_smoke(model_path)
        if install_if_configured
        else None
    )
    return {
        "ready": bool(smoke and smoke.get("ready")),
        "configured": True,
        "auto_install": auto_install,
        "model_path": model_path,
        "package_runtime": package_report,
        "model": model_report,
        "smoke": smoke,
    }


def execute(*, install_if_configured: bool, require_assistant: bool) -> dict[str, Any]:
    word2vec = _word2vec_install(install_if_configured=install_if_configured)
    litert_cli = _litert_cli_status()
    gemma = _gemma_registry_status()
    native_causal = _native_causal_install(
        install_if_configured=install_if_configured,
        require_assistant=require_assistant,
    )

    from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
        HHSNativeLiteRTLMTransport,
    )

    native = HHSNativeLiteRTLMTransport().installation_status()
    native_generative_ready = bool(
        native.get("ready") and native_causal.get("ready")
    )
    assistant_ready = bool(gemma.get("ready") or native_generative_ready)
    report: dict[str, Any] = {
        "schema": "HHS_PRODUCTION_LANGUAGE_ASSET_INSTALLATION_STATUS_V2",
        "assistant_ready": assistant_ready,
        "native_generative_ready": native_generative_ready,
        "selected_provider": (
            "provider:hhs.local.text"
            if native_generative_ready
            else "provider:hhs.litert_lm.gemma4"
            if gemma.get("ready")
            else None
        ),
        "gemma": gemma,
        "litert_lm_cli": litert_cli,
        "word2vec": word2vec,
        "native_hhs": native,
        "native_causal": native_causal,
        "require_assistant": require_assistant,
        "fixture_substitution_allowed": False,
        "status_path": str(STATUS_PATH),
    }
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    if require_assistant and not assistant_ready:
        raise RuntimeError(
            "production assistant installation is incomplete: native-first production "
            "requires a real causal generator that passes direct CLI acceptance, or a "
            "reachable LiteRT-LM generative provider"
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
