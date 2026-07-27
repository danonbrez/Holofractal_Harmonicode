#!/usr/bin/env python3
"""HHS native Vulkan loader substrate for graphics and LiteRT-LM GPU execution.

The Vulkan loader is a projection/dispatch dependency. It is not a GPU driver and
never receives HHS mutation authority. This module discovers, validates, stages,
and receipts the system loader used by the native runtime graphics system.
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import json
import os
import platform
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

SCHEMA = "HHS_RUNTIME_GRAPHICS_VULKAN_LOADER_V1"
AUTHORITY = "HHS_GRAPHICS_PROJECTION_SUBSTRATE_AUTHORITY_V1"
REQUIRED_SYMBOLS = (
    "vkGetInstanceProcAddr",
    "vkCreateInstance",
    "vkEnumerateInstanceExtensionProperties",
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNTIME_ROOT = REPO_ROOT / ".hhs" / "runtime" / "graphics" / "vulkan"


def runtime_root() -> Path:
    return Path(os.getenv("HHS_VULKAN_RUNTIME_ROOT", str(DEFAULT_RUNTIME_ROOT))).expanduser()


def local_loader_path() -> Path:
    override = os.getenv("HHS_VULKAN_LOADER_PATH")
    if override:
        return Path(override).expanduser()
    return runtime_root() / "lib" / "libvulkan.so.1"


def _ldconfig_candidates() -> list[str]:
    executable = shutil.which("ldconfig")
    if not executable:
        return []
    try:
        completed = subprocess.run(
            [executable, "-p"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    candidates: list[str] = []
    for line in completed.stdout.splitlines():
        if "libvulkan.so.1" not in line or "=>" not in line:
            continue
        candidate = line.split("=>", 1)[1].strip()
        if candidate and Path(candidate).exists():
            candidates.append(candidate)
    return candidates


def loader_candidates() -> list[str]:
    values: list[str] = []
    explicit = os.getenv("HHS_VULKAN_LOADER_PATH")
    if explicit:
        values.append(explicit)
    local = local_loader_path()
    if local.exists() or local.is_symlink():
        values.append(str(local))
    found = ctypes.util.find_library("vulkan")
    if found:
        values.append(found)
    values.extend(_ldconfig_candidates())
    values.extend([
        "libvulkan.so.1",
        "libvulkan.so",
        "/usr/lib/x86_64-linux-gnu/libvulkan.so.1",
        "/lib/x86_64-linux-gnu/libvulkan.so.1",
        "/usr/lib64/libvulkan.so.1",
        "/usr/lib/libvulkan.so.1",
    ])
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = str(value).strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _load_first(candidates: Iterable[str]) -> tuple[ctypes.CDLL | None, str | None, list[str]]:
    errors: list[str] = []
    for candidate in candidates:
        try:
            return ctypes.CDLL(candidate), candidate, errors
        except OSError as exc:
            errors.append(f"{candidate}: {exc}")
    return None, None, errors


def _decode_api_version(value: int) -> str:
    variant = (value >> 29) & 0x7
    major = (value >> 22) & 0x7F
    minor = (value >> 12) & 0x3FF
    patch = value & 0xFFF
    return f"{variant}.{major}.{minor}.{patch}" if variant else f"{major}.{minor}.{patch}"


def _enumerate_instance_version(loader: ctypes.CDLL) -> Mapping[str, Any]:
    function = getattr(loader, "vkEnumerateInstanceVersion", None)
    if function is None:
        return {"available": False, "raw": None, "version": "1.0"}
    function.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
    function.restype = ctypes.c_int32
    value = ctypes.c_uint32(0)
    result = int(function(ctypes.byref(value)))
    return {
        "available": True,
        "vk_result": result,
        "raw": int(value.value),
        "version": _decode_api_version(int(value.value)) if result == 0 else None,
    }


def _manifest_directories() -> list[Path]:
    directories: list[Path] = []
    for variable in ("VK_DRIVER_FILES", "VK_ICD_FILENAMES"):
        raw = os.getenv(variable, "")
        for entry in raw.split(os.pathsep):
            entry = entry.strip()
            if entry:
                directories.append(Path(entry).expanduser().parent)
    xdg_config_home = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    xdg_data_home = Path(os.getenv("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
    directories.extend([
        runtime_root() / "icd.d",
        xdg_config_home / "vulkan" / "icd.d",
        Path("/etc/vulkan/icd.d"),
        xdg_data_home / "vulkan" / "icd.d",
        Path("/usr/local/share/vulkan/icd.d"),
        Path("/usr/share/vulkan/icd.d"),
    ])
    result: list[Path] = []
    seen: set[str] = set()
    for directory in directories:
        key = str(directory)
        if key not in seen:
            seen.add(key)
            result.append(directory)
    return result


def discover_icd_manifests() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for directory in _manifest_directories():
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            resolved = str(path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)
            record: dict[str, Any] = {"path": resolved, "valid_json": False, "library_path": None}
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                icd = payload.get("ICD") if isinstance(payload, dict) else None
                record["valid_json"] = isinstance(payload, dict)
                if isinstance(icd, dict):
                    record["library_path"] = icd.get("library_path")
                    record["api_version"] = icd.get("api_version")
            except (OSError, json.JSONDecodeError) as exc:
                record["error"] = str(exc)
            records.append(record)
    return records


def inspect_vulkan_loader() -> dict[str, Any]:
    system = platform.system()
    if system == "Android":
        body: dict[str, Any] = {
            "schema": SCHEMA,
            "platform": system,
            "loader_ready": True,
            "loader_source": "ANDROID_OS_PROVIDED",
            "loader_path": "libvulkan.so",
            "required_symbols": list(REQUIRED_SYMBOLS),
            "missing_symbols": [],
            "icd_manifests": [],
            "driver_ready": True,
            "runtime_mutation_authority": False,
            "authority": AUTHORITY,
        }
    elif system != "Linux":
        body = {
            "schema": SCHEMA,
            "platform": system,
            "loader_ready": False,
            "loader_source": "UNSUPPORTED_BY_LINUX_LOADER_INSTALLER",
            "loader_path": None,
            "required_symbols": list(REQUIRED_SYMBOLS),
            "missing_symbols": list(REQUIRED_SYMBOLS),
            "icd_manifests": [],
            "driver_ready": False,
            "runtime_mutation_authority": False,
            "authority": AUTHORITY,
        }
    else:
        loader, selected, errors = _load_first(loader_candidates())
        missing: list[str] = []
        api_version: Mapping[str, Any] | None = None
        if loader is not None:
            missing = [name for name in REQUIRED_SYMBOLS if getattr(loader, name, None) is None]
            if not missing:
                api_version = _enumerate_instance_version(loader)
        manifests = discover_icd_manifests()
        body = {
            "schema": SCHEMA,
            "platform": system,
            "loader_ready": loader is not None and not missing,
            "loader_source": (
                "HHS_RUNTIME_LOCAL"
                if selected and Path(selected).expanduser() == local_loader_path()
                else "SYSTEM"
            ),
            "loader_path": selected,
            "loader_errors": errors,
            "required_symbols": list(REQUIRED_SYMBOLS),
            "missing_symbols": missing,
            "api_version": api_version,
            "icd_manifests": manifests,
            "icd_manifest_count": len(manifests),
            "driver_ready": any(item.get("valid_json") and item.get("library_path") for item in manifests),
            "runtime_mutation_authority": False,
            "authority": AUTHORITY,
        }
        del loader
    body["vulkan_loader_receipt_hash72"] = hash72(
        SCHEMA,
        {key: value for key, value in body.items() if key != "vulkan_loader_receipt_hash72"},
    )
    return body


def _resolve_system_loader() -> Path:
    for candidate in [*_ldconfig_candidates(), *loader_candidates()]:
        path = Path(candidate).expanduser()
        if path.is_absolute() and path.exists():
            return path.resolve()
    raise FileNotFoundError("could not resolve an absolute system libvulkan.so.1 path")


def stage_runtime_loader() -> dict[str, Any]:
    if platform.system() != "Linux":
        return inspect_vulkan_loader()
    source = _resolve_system_loader()
    destination = local_loader_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        destination.unlink()
    try:
        destination.symlink_to(source)
        stage_mode = "absolute_symlink"
    except OSError:
        shutil.copy2(source, destination)
        stage_mode = "copy"
    env_path = runtime_root() / "env.sh"
    env_path.write_text(
        "#!/usr/bin/env bash\n"
        f"export HHS_VULKAN_RUNTIME_ROOT={shlex.quote(str(runtime_root()))}\n"
        f"export HHS_VULKAN_LOADER_PATH={shlex.quote(str(destination))}\n"
        f"export LD_LIBRARY_PATH={shlex.quote(str(destination.parent))}:\"${{LD_LIBRARY_PATH:-}}\"\n",
        encoding="utf-8",
    )
    result = inspect_vulkan_loader()
    result.update({
        "staged": True,
        "stage_mode": stage_mode,
        "staged_source": str(source),
        "staged_destination": str(destination),
        "environment_file": str(env_path),
    })
    result["vulkan_loader_receipt_hash72"] = hash72(
        SCHEMA,
        {key: value for key, value in result.items() if key != "vulkan_loader_receipt_hash72"},
    )
    return result


def write_receipt(result: Mapping[str, Any], path: Path | None = None) -> Path:
    receipt_path = path or runtime_root() / "vulkan-loader-receipt.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(dict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--require-loader", action="store_true")
    parser.add_argument("--require-driver", action="store_true")
    parser.add_argument("--receipt-path")
    args = parser.parse_args()

    result = stage_runtime_loader() if args.stage else inspect_vulkan_loader()
    receipt_path = write_receipt(
        result,
        Path(args.receipt_path).expanduser() if args.receipt_path else None,
    )
    result = {**result, "receipt_path": str(receipt_path)}
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_loader and not result.get("loader_ready"):
        return 1
    if args.require_driver and not result.get("driver_ready"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
