"""Fail-closed freshness gate for the Pass 205 native continuation library."""
from __future__ import annotations

import pathlib
import platform
from typing import Any


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _library_path(root: pathlib.Path) -> pathlib.Path:
    build_dir = root / "hhs_runtime" / "builds"
    system = platform.system().lower()
    if system == "windows":
        name = "hhs_pass205_continuation.dll"
    elif system == "darwin":
        name = "libhhs_pass205_continuation.dylib"
    else:
        name = "libhhs_pass205_continuation.so"
    return build_dir / name


def _build_inputs(root: pathlib.Path) -> tuple[pathlib.Path, ...]:
    return (
        root / "hhs_runtime" / "c" / "hhs_pass205_continuation.c",
        root / "hhs_runtime" / "c" / "hhs_pass205_continuation.h",
        root / "hhs_runtime" / "src" / "hhs_hash216.c",
        root / "hhs_runtime" / "include" / "hhs_hash216.h",
    )


def ensure_pass205_native_freshness(root: pathlib.Path | None = None) -> dict[str, Any]:
    """Remove an untrustworthy native artifact before the bridge can load it.

    The existing bridge rebuilds when the library is absent. This guard makes
    absence the fail-closed representation for a stale artifact or a repository
    tree whose required source/header inputs are incomplete.
    """
    resolved_root = pathlib.Path(root or _repo_root()).resolve()
    output = _library_path(resolved_root)
    inputs = _build_inputs(resolved_root)
    missing = [str(path) for path in inputs if not path.is_file()]
    report: dict[str, Any] = {
        "schema": "HHS_PASS_205_NATIVE_FRESHNESS_GUARD_V1",
        "root": str(resolved_root),
        "library": str(output),
        "inputs": [str(path) for path in inputs],
        "missing_inputs": missing,
        "library_existed": output.is_file(),
        "stale": False,
        "removed": False,
        "ready_for_loader": False,
    }

    if not output.is_file():
        report["ready_for_loader"] = not missing
        report["reason"] = "LIBRARY_ABSENT_BUILD_REQUIRED" if not missing else "BUILD_INPUTS_MISSING"
        return report

    if missing:
        output.unlink()
        report.update(
            {
                "stale": True,
                "removed": True,
                "ready_for_loader": False,
                "reason": "PREBUILT_LIBRARY_REJECTED_BUILD_INPUTS_MISSING",
            }
        )
        return report

    newest_input_ns = max(path.stat().st_mtime_ns for path in inputs)
    library_ns = output.stat().st_mtime_ns
    report["newest_input_mtime_ns"] = newest_input_ns
    report["library_mtime_ns"] = library_ns
    if library_ns < newest_input_ns:
        output.unlink()
        report.update(
            {
                "stale": True,
                "removed": True,
                "ready_for_loader": True,
                "reason": "STALE_LIBRARY_REMOVED_REBUILD_REQUIRED",
            }
        )
        return report

    report.update(
        {
            "ready_for_loader": True,
            "reason": "LIBRARY_FRESH",
        }
    )
    return report


PASS205_NATIVE_FRESHNESS_REPORT = ensure_pass205_native_freshness()


__all__ = [
    "PASS205_NATIVE_FRESHNESS_REPORT",
    "ensure_pass205_native_freshness",
]
