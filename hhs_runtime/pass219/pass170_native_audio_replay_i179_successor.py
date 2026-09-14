"""Repair-forward verifier for the frozen I179 native-audio replay boundary.

I179 was intentionally nonterminal: at that point eight FastAPI constructors
remained and six launchers had already been redirected to the canonical public
gateway.  I180/I181 subsequently migrated the remaining route-bearing legacy
constructors and retired two independent FastAPI identities.  This verifier
preserves the I179 evidence as historical baseline while proving that the
current repository is a valid I181 successor rather than treating that later
retirement as I179 drift.

The shared I172 launcher scanner only resolves literal string arguments.  I181
legitimately uses module-level exact string constants for canonical targets, so
this layer resolves only direct module-level string assignments at the exact
``uvicorn.run`` call line.  Dynamic expressions remain unresolved and fail
closed.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_legacy_constructor_retirement_i181 import (
    verify_i181_legacy_constructor_retirement,
)
from hhs_runtime.pass219.pass170_legacy_constructor_router_manifest_i172 import (
    _scan_uvicorn_launchers,
)
from hhs_runtime.pass219.pass170_native_audio_replay_i179 import (
    CANONICAL_GATEWAY,
    CLASSIFICATION,
    Pass170I179VerificationError,
    verify_i179_native_audio_replay,
)

_ALLOWED_SUCCESSOR_DRIFT = {
    "PASS170_I179_CANONICAL_LAUNCHER_PARITY_FAILED",
    "PASS170_I179_FASTAPI_CONSTRUCTOR_COUNT_DRIFT",
}
_I179_BASELINE_CONSTRUCTOR_COUNT = 8
_I181_SUCCESSOR_CONSTRUCTOR_COUNT = 6
_I181_NEWLY_RETIRED_CONSTRUCTOR_COUNT = 2
_I181_CUMULATIVE_RETIRED_CONSTRUCTOR_COUNT = 4


class Pass170I179SuccessorVerificationError(RuntimeError):
    """Raised when current state is neither frozen I179 nor its verified I181 successor."""


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _module_string_constants(tree: ast.Module) -> dict[str, str]:
    constants: dict[str, str] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            value = statement.value
            if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                continue
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = value.value
        elif isinstance(statement, ast.AnnAssign):
            value = statement.value
            if (
                isinstance(statement.target, ast.Name)
                and isinstance(value, ast.Constant)
                and isinstance(value.value, str)
            ):
                constants[statement.target.id] = value.value
    return constants


def _resolve_launcher_target(root: Path, launcher: dict[str, Any]) -> str | None:
    target = launcher.get("target")
    if isinstance(target, str):
        return target
    relative_path = launcher.get("path")
    line = launcher.get("line")
    if not isinstance(relative_path, str) or not isinstance(line, int):
        return None
    try:
        tree = ast.parse((root / relative_path).read_text(encoding="utf-8"), filename=relative_path)
    except (OSError, SyntaxError):
        return None
    constants = _module_string_constants(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or int(getattr(node, "lineno", 0) or 0) != line:
            continue
        name = _call_name(node.func)
        if name != "uvicorn.run" and not name.endswith(".uvicorn.run"):
            continue
        if not node.args:
            return None
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
        if isinstance(first, ast.Name):
            return constants.get(first.id)
        return None
    return None


def verify_i179_native_audio_replay_successor(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    historical = verify_i179_native_audio_replay(root, fail_closed=False)
    historical_blockers = set(historical.get("evidence_blockers") or [])
    unexpected_historical_blockers = sorted(historical_blockers - _ALLOWED_SUCCESSOR_DRIFT)

    i181 = verify_i181_legacy_constructor_retirement(root, fail_closed=False)
    successor_blockers: list[str] = []
    if i181.get("evidence_verified") is not True:
        successor_blockers.extend(
            f"PASS170_I179_I181_SUCCESSOR:{item}"
            for item in (i181.get("evidence_blockers") or ["EVIDENCE_NOT_VERIFIED"])
        )
    if i181.get("fastapi_constructor_count") != _I181_SUCCESSOR_CONSTRUCTOR_COUNT:
        successor_blockers.append("PASS170_I179_I181_SUCCESSOR_CONSTRUCTOR_COUNT_INVALID")
    if i181.get("newly_retired_constructor_count") != _I181_NEWLY_RETIRED_CONSTRUCTOR_COUNT:
        successor_blockers.append("PASS170_I179_I181_SUCCESSOR_RETIREMENT_COUNT_INVALID")
    if i181.get("cumulative_retired_constructor_count") != _I181_CUMULATIVE_RETIRED_CONSTRUCTOR_COUNT:
        successor_blockers.append("PASS170_I179_I181_SUCCESSOR_CUMULATIVE_RETIREMENT_INVALID")

    launchers = _scan_uvicorn_launchers(root)
    resolved_launchers = [
        {**launcher, "resolved_target": _resolve_launcher_target(root, launcher)}
        for launcher in launchers
    ]
    canonical_launchers = [
        launcher
        for launcher in resolved_launchers
        if launcher.get("resolved_target") == CANONICAL_GATEWAY
    ]
    if len(resolved_launchers) != 6:
        successor_blockers.append("PASS170_I179_SUCCESSOR_LAUNCHER_COUNT_DRIFT")
    if len(canonical_launchers) != len(resolved_launchers) or len(canonical_launchers) != 6:
        successor_blockers.append("PASS170_I179_SUCCESSOR_CANONICAL_LAUNCHER_PARITY_FAILED")

    evidence_blockers = sorted(set(unexpected_historical_blockers + successor_blockers))
    evidence_verified = not evidence_blockers
    report = dict(historical)
    report.update(
        {
            "classification": CLASSIFICATION if evidence_verified else "PASS170_I179_EVIDENCE_FAILED",
            "i179_baseline_fastapi_constructor_count": _I179_BASELINE_CONSTRUCTOR_COUNT,
            "fastapi_constructor_count": i181.get("fastapi_constructor_count"),
            "i181_successor_verified": i181.get("evidence_verified") is True,
            "i181_newly_retired_constructor_count": i181.get("newly_retired_constructor_count"),
            "i181_cumulative_retired_constructor_count": i181.get("cumulative_retired_constructor_count"),
            "observed_launcher_count": len(resolved_launchers),
            "canonical_redirect_count": len(canonical_launchers),
            "launcher_successor_resolution_verified": (
                len(resolved_launchers) == 6 and len(canonical_launchers) == 6
            ),
            "historical_i179_evidence_blockers": sorted(historical_blockers),
            "evidence_verified": evidence_verified,
            "evidence_blockers": evidence_blockers,
            "audio_native_abi_verified": evidence_verified,
            "audio_receipt_replay_verified": evidence_verified,
            "audio_internal_ecc_pq_boundary_preserved": evidence_verified,
            "current_successor_target_blockers": list(i181.get("target_blockers") or []),
            "current_successor_next_boundary": i181.get("next_boundary"),
        }
    )
    if evidence_blockers and fail_closed:
        raise Pass170I179SuccessorVerificationError(
            "PASS170_I179_SUCCESSOR_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


__all__ = [
    "Pass170I179SuccessorVerificationError",
    "verify_i179_native_audio_replay_successor",
]
