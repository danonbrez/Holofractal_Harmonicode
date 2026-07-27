#!/usr/bin/env python3
"""Probe the accelerator substrate required by the HHS LiteRT-LM provider.

This probe does not install GPU drivers. It verifies that the host exposes the
minimum local execution substrate before HHS attempts to start LiteRT-LM in GPU
mode. Linux and Windows GPU execution require a Vulkan loader and a visible GPU
or accelerator device. macOS GPU execution uses Metal.
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import glob
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from typing import Any, Dict, Iterable

SCHEMA = "HHS_LITERT_LM_ACCELERATOR_PROBE_V1"
VALID_BACKENDS = {"auto", "cpu", "gpu", "npu"}


def _load_first(candidates: Iterable[str]) -> tuple[object | None, str | None, str | None]:
    errors = []
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return ctypes.CDLL(candidate), candidate, None
        except OSError as exc:
            errors.append(f"{candidate}: {exc}")
    return None, None, "; ".join(errors) or "no loader candidate found"


def _linux_gpu_nodes() -> list[str]:
    patterns = (
        "/dev/dri/renderD*",
        "/dev/nvidia[0-9]*",
        "/dev/nvidiactl",
        "/dev/dxg",
    )
    nodes = sorted({path for pattern in patterns for path in glob.glob(pattern)})
    return [path for path in nodes if os.path.exists(path)]


def _vulkan_summary() -> Dict[str, Any]:
    executable = shutil.which("vulkaninfo")
    if not executable:
        return {
            "vulkaninfo_present": False,
            "vulkaninfo_ok": None,
            "vulkaninfo_summary": None,
        }
    completed = subprocess.run(
        [executable, "--summary"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=20,
        check=False,
    )
    summary = completed.stdout[-12000:]
    return {
        "vulkaninfo_present": True,
        "vulkaninfo_ok": completed.returncode == 0,
        "vulkaninfo_summary": summary,
    }


def _probe_gpu() -> Dict[str, Any]:
    system = platform.system()
    result: Dict[str, Any] = {
        "platform": system,
        "accelerator_api": None,
        "loader": None,
        "device_nodes": [],
        "ready": False,
        "reason": "",
    }

    if system == "Darwin":
        result.update({
            "accelerator_api": "metal",
            "ready": True,
            "reason": "macOS GPU execution uses Metal; Vulkan is not required",
        })
        return result

    if system == "Linux":
        candidates = [
            ctypes.util.find_library("vulkan") or "",
            "libvulkan.so.1",
            "libvulkan.so",
        ]
        loader, loader_name, error = _load_first(candidates)
        nodes = _linux_gpu_nodes()
        summary = _vulkan_summary()
        result.update(summary)
        result.update({
            "accelerator_api": "vulkan",
            "loader": loader_name,
            "device_nodes": nodes,
        })
        del loader
        if loader_name is None:
            result["reason"] = f"Vulkan loader unavailable: {error}"
            return result
        if not nodes:
            result["reason"] = (
                "Vulkan loader is present, but no render, NVIDIA, or WSL GPU "
                "device is exposed to this process"
            )
            return result
        if summary["vulkaninfo_present"] and not summary["vulkaninfo_ok"]:
            result["reason"] = "vulkaninfo could not enumerate a usable Vulkan device"
            return result
        result.update({
            "ready": True,
            "reason": "Vulkan loader and GPU device exposure verified",
        })
        return result

    if system == "Windows":
        loader, loader_name, error = _load_first(["vulkan-1.dll"])
        summary = _vulkan_summary()
        result.update(summary)
        result.update({
            "accelerator_api": "vulkan",
            "loader": loader_name,
        })
        del loader
        if loader_name is None:
            result["reason"] = f"Vulkan loader unavailable: {error}"
            return result
        if summary["vulkaninfo_present"] and not summary["vulkaninfo_ok"]:
            result["reason"] = "vulkaninfo could not enumerate a usable Vulkan device"
            return result
        result.update({
            "ready": True,
            "reason": "Windows Vulkan loader is available",
        })
        return result

    result["reason"] = f"GPU probe is not defined for platform {system!r}"
    return result


def probe(backend: str) -> Dict[str, Any]:
    normalized = backend.strip().lower()
    if normalized not in VALID_BACKENDS:
        raise ValueError(f"unsupported backend {backend!r}")

    if normalized == "cpu":
        body: Dict[str, Any] = {
            "schema": SCHEMA,
            "backend": normalized,
            "ready": True,
            "accelerator_required": False,
            "reason": "CPU backend selected",
            "platform": platform.system(),
        }
    elif normalized == "auto":
        body = {
            "schema": SCHEMA,
            "backend": normalized,
            "ready": True,
            "accelerator_required": False,
            "reason": "LiteRT-LM backend selection deferred to model configuration",
            "platform": platform.system(),
        }
    elif normalized == "npu":
        body = {
            "schema": SCHEMA,
            "backend": normalized,
            "ready": False,
            "accelerator_required": True,
            "reason": "NPU probing requires a platform-specific HHS adapter",
            "platform": platform.system(),
        }
    else:
        body = {
            "schema": SCHEMA,
            "backend": normalized,
            "accelerator_required": True,
            **_probe_gpu(),
        }

    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    body["diagnostic_receipt_sha256"] = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        default=os.getenv("HHS_LITERT_LM_BACKEND", "gpu"),
        choices=sorted(VALID_BACKENDS),
    )
    parser.add_argument(
        "--require",
        action="store_true",
        help="return a nonzero status when the selected backend is unavailable",
    )
    args = parser.parse_args()

    result = probe(args.backend)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require and not result.get("ready"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
