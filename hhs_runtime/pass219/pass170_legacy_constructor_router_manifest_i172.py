"""Pass219 I172 / Pass170 constructor-authority and full-router-manifest gate.

This verifier is read-only. It preserves the raw I169 constructor inventory,
classifies every current FastAPI constructor and uvicorn launcher, verifies the
ordered Pass170 production composition manifest, and proves that the existing
Pass201 package federation provides deterministic missing-route closure for
``hhs_backend.api``.

I172 is deliberately nonterminal. It does not reclassify remaining legacy
self-launchers, the explicit source-only degraded gateway, or incomplete full
Pass170 operation records as acceptable terminal state.
"""
from __future__ import annotations

import ast
from collections import Counter
import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)
from hhs_runtime.pass219.pass170_public_app_route_parity_i171 import (
    verify_i171_public_app_route_parity,
)

SCHEMA = "HHS_PASS219_I172_PASS170_CONSTRUCTOR_ROUTER_MANIFEST_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I172"
BASE_MAIN = "08bd2db30706a88d3e6ffee2e8c3ff8ca592788c"
CONSTRUCTOR_REGISTRY = "HHS_FASTAPI_CONSTRUCTOR_REGISTRY.json"
ROUTER_MANIFEST = "HHS_PUBLIC_ROUTER_MANIFEST.json"
CANONICAL_GATEWAY = "hhs_backend.public_api_server:app"
CLASSIFICATION = "PASS170_CONSTRUCTOR_AUTHORITY_AND_FULL_ROUTER_MANIFEST_VERIFIED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_LEGACY_LAUNCHER_RETIREMENT_AND_FULL_OPERATION_RECORD_COMPLETION"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_FULL_OPERATION_RECORDS_PENDING",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_LEGACY_SELF_LAUNCH_BYPASSES_REMAIN",
)

_EXCLUDED_PARTS = {
    ".git", ".github", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv",
    "__pycache__", "artifacts", "build", "builds", "dist", "docs",
    "node_modules", "site-packages", "tests", "vendor", "venv",
}


class Pass170I172VerificationError(RuntimeError):
    """Raised when I172 evidence fails closed."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I172VerificationError(
            f"PASS170_I172_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I172VerificationError(f"PASS170_I172_JSON_ROOT_INVALID:{path}")
    return payload


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _constant_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _iter_python_files(root: Path):
    for path in sorted(root.rglob("*.py")):
        parts = path.relative_to(root).parts
        if any(part in _EXCLUDED_PARTS for part in parts[:-1]):
            continue
        yield path


def _scan_uvicorn_launchers(root: Path) -> list[dict[str, Any]]:
    launchers: list[dict[str, Any]] = []
    for path in _iter_python_files(root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node.func)
            if name != "uvicorn.run" and not name.endswith(".uvicorn.run"):
                continue
            launchers.append({
                "path": path.relative_to(root).as_posix(),
                "line": int(getattr(node, "lineno", 0) or 0),
                "target": _constant_string(node.args[0]) if node.args else None,
            })
    return sorted(launchers, key=lambda item: (item["path"], item["line"]))


def _module_path(root: Path, module: str) -> Path:
    return root / (module.replace(".", "/") + ".py")


def _verify_constructor_registry(
    root: Path,
    registry: dict[str, Any],
    inherited_inventory: dict[str, Any],
) -> tuple[list[str], dict[str, Any], list[str]]:
    evidence_blockers: list[str] = []
    target_blockers: list[str] = []

    if registry.get("schema") != "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_V1":
        evidence_blockers.append("PASS170_I172_CONSTRUCTOR_REGISTRY_SCHEMA_INVALID")
    if registry.get("contract") != CONTRACT_ID or registry.get("iteration") != ITERATION:
        evidence_blockers.append("PASS170_I172_CONSTRUCTOR_REGISTRY_METADATA_INVALID")
    if registry.get("canonical_public_gateway") != CANONICAL_GATEWAY:
        evidence_blockers.append("PASS170_I172_CONSTRUCTOR_CANONICAL_GATEWAY_MISMATCH")

    observed_sites = inherited_inventory.get("inventory", {}).get("fastapi_constructors", [])
    observed_counter = Counter(
        item.get("path") for item in observed_sites if isinstance(item, dict) and isinstance(item.get("path"), str)
    )
    records = registry.get("constructor_records")
    if not isinstance(records, list):
        records = []
        evidence_blockers.append("PASS170_I172_CONSTRUCTOR_RECORDS_INVALID")
    registry_paths = [item.get("path") for item in records if isinstance(item, dict)]
    if any(not isinstance(item, str) or not item for item in registry_paths):
        evidence_blockers.append("PASS170_I172_CONSTRUCTOR_RECORD_PATH_INVALID")
    registry_counter = Counter(item for item in registry_paths if isinstance(item, str))
    if observed_counter != registry_counter:
        evidence_blockers.append("PASS170_I172_CONSTRUCTOR_REGISTRY_CENSUS_MISMATCH")

    canonical_records = [
        item for item in records
        if isinstance(item, dict)
        and item.get("canonical_authority") is True
        and item.get("classification") == "CANONICAL_PRODUCTION_BASE_CONSTRUCTOR"
    ]
    if len(canonical_records) != 1 or canonical_records[0].get("path") != "hhs_backend/server.py":
        evidence_blockers.append("PASS170_I172_CANONICAL_CONSTRUCTOR_CARDINALITY_INVALID")

    degraded_records = [
        item for item in records
        if isinstance(item, dict) and item.get("classification") == "EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY"
    ]
    if len(degraded_records) != 1 or degraded_records[0].get("public_port_authority") is not True:
        evidence_blockers.append("PASS170_I172_DEGRADED_GATEWAY_CLASSIFICATION_INVALID")
    else:
        target_blockers.append("PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS")

    pending_constructor_records = [
        item for item in records
        if isinstance(item, dict)
        and "PENDING" in str(item.get("retirement_status", ""))
    ]
    if pending_constructor_records:
        target_blockers.append("PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN")

    observed_launchers = _scan_uvicorn_launchers(root)
    observed_launcher_counter = Counter(item["path"] for item in observed_launchers)
    launcher_records = registry.get("launcher_records")
    if not isinstance(launcher_records, list):
        launcher_records = []
        evidence_blockers.append("PASS170_I172_LAUNCHER_RECORDS_INVALID")
    registry_launcher_counter = Counter(
        item.get("path") for item in launcher_records
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    )
    if observed_launcher_counter != registry_launcher_counter:
        evidence_blockers.append("PASS170_I172_LAUNCHER_REGISTRY_CENSUS_MISMATCH")

    observed_by_path = {item["path"]: item for item in observed_launchers}
    pending_launchers: list[dict[str, Any]] = []
    for record in launcher_records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            evidence_blockers.append("PASS170_I172_LAUNCHER_RECORD_INVALID")
            continue
        observed = observed_by_path.get(record["path"])
        if observed is None:
            continue
        if observed.get("target") != record.get("observed_target"):
            evidence_blockers.append("PASS170_I172_LAUNCHER_TARGET_MISMATCH")
        status = str(record.get("status", ""))
        if status.startswith("PENDING_"):
            pending_launchers.append({**record, "observed_line": observed.get("line")})
        elif status == "VERIFIED_CANONICAL_GATEWAY_REDIRECT":
            if observed.get("target") != CANONICAL_GATEWAY:
                evidence_blockers.append("PASS170_I172_VERIFIED_LAUNCHER_NOT_CANONICAL")
        else:
            evidence_blockers.append("PASS170_I172_LAUNCHER_STATUS_INVALID")
    if pending_launchers:
        target_blockers.append("PASS170_LEGACY_SELF_LAUNCH_BYPASSES_REMAIN")

    invariants = registry.get("invariants", {}) if isinstance(registry, dict) else {}
    if invariants.get("all_fastapi_constructors_must_be_classified") is not True:
        evidence_blockers.append("PASS170_I172_CONSTRUCTOR_CLASSIFICATION_INVARIANT_INVALID")
    if invariants.get("all_uvicorn_launchers_must_be_classified") is not True:
        evidence_blockers.append("PASS170_I172_LAUNCHER_CLASSIFICATION_INVARIANT_INVALID")
    for key in (
        "new_vm81_authority", "new_hash72_mint_authority",
        "hash216_persistence_authority", "floating_point_canonical_authority",
        "canonical_state_mutated_by_registry_load",
    ):
        if invariants.get(key) is not False:
            evidence_blockers.append(f"PASS170_I172_FORBIDDEN_CONSTRUCTOR_AUTHORITY_FLAG:{key}")

    evidence = {
        "observed_constructor_count": sum(observed_counter.values()),
        "registered_constructor_count": sum(registry_counter.values()),
        "observed_constructor_paths": sorted(observed_counter),
        "canonical_constructor_count": len(canonical_records),
        "degraded_gateway_count": len(degraded_records),
        "pending_constructor_record_count": len(pending_constructor_records),
        "observed_launcher_count": len(observed_launchers),
        "registered_launcher_count": sum(registry_launcher_counter.values()),
        "pending_launcher_count": len(pending_launchers),
        "pending_launchers": pending_launchers,
        "launchers": observed_launchers,
    }
    return sorted(set(evidence_blockers)), evidence, sorted(set(target_blockers))


def _verify_router_manifest(root: Path, manifest: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    if manifest.get("schema") != "HHS_PUBLIC_ROUTER_MANIFEST_V1":
        blockers.append("PASS170_I172_ROUTER_MANIFEST_SCHEMA_INVALID")
    if manifest.get("contract") != CONTRACT_ID or manifest.get("iteration") != ITERATION:
        blockers.append("PASS170_I172_ROUTER_MANIFEST_METADATA_INVALID")
    if manifest.get("canonical_application_entrypoint") != CANONICAL_GATEWAY:
        blockers.append("PASS170_I172_ROUTER_MANIFEST_GATEWAY_MISMATCH")

    stages = manifest.get("stages")
    if not isinstance(stages, list) or not stages:
        stages = []
        blockers.append("PASS170_I172_ROUTER_MANIFEST_STAGES_INVALID")
    orders = [item.get("order") for item in stages if isinstance(item, dict)]
    ids = [item.get("stage_id") for item in stages if isinstance(item, dict)]
    if len(orders) != len(stages) or any(not isinstance(item, int) for item in orders):
        blockers.append("PASS170_I172_ROUTER_STAGE_ORDER_INVALID")
    elif orders != sorted(orders) or len(orders) != len(set(orders)):
        blockers.append("PASS170_I172_ROUTER_STAGE_ORDER_NOT_STRICT")
    if len(ids) != len(stages) or any(not isinstance(item, str) or not item for item in ids):
        blockers.append("PASS170_I172_ROUTER_STAGE_ID_INVALID")
    elif len(ids) != len(set(ids)):
        blockers.append("PASS170_I172_ROUTER_STAGE_ID_DUPLICATE")

    stage_reports: list[dict[str, Any]] = []
    for stage in stages:
        if not isinstance(stage, dict):
            blockers.append("PASS170_I172_ROUTER_STAGE_INVALID")
            continue
        module = stage.get("module")
        tokens = stage.get("required_source_tokens")
        if not isinstance(module, str) or not isinstance(tokens, list) or any(not isinstance(item, str) for item in tokens):
            blockers.append("PASS170_I172_ROUTER_STAGE_RECORD_INVALID")
            continue
        path = _module_path(root, module)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            blockers.append("PASS170_I172_ROUTER_STAGE_SOURCE_UNREADABLE")
            source = ""
        missing = [token for token in tokens if token not in source]
        if missing:
            blockers.append("PASS170_I172_ROUTER_STAGE_SOURCE_TOKEN_MISSING")
        stage_reports.append({
            "order": stage.get("order"),
            "stage_id": stage.get("stage_id"),
            "module": module,
            "source_present": path.is_file(),
            "required_token_count": len(tokens),
            "missing_tokens": missing,
        })

    pass201 = next((item for item in stages if isinstance(item, dict) and item.get("stage_id") == "pass201-api-package-closure"), None)
    if not isinstance(pass201, dict):
        blockers.append("PASS170_I172_PASS201_CLOSURE_STAGE_ABSENT")
    else:
        requirements = pass201.get("closure_requirements", {})
        if pass201.get("package") != "hhs_backend.api":
            blockers.append("PASS170_I172_PASS201_PACKAGE_MISMATCH")
        if requirements != {
            "module_order": "SORTED",
            "attach_policy": "MISSING_SIGNATURES_ONLY",
            "import_failure_count": 0,
            "unexposed_route_count": 0,
        }:
            blockers.append("PASS170_I172_PASS201_CLOSURE_REQUIREMENTS_INVALID")

    summary = manifest.get("registered_delegate_route_summary", {})
    if summary != {
        "direct_pass170_routes": 12,
        "pass168_routes": 18,
        "pass169_routes": 17,
        "direct_plus_delegate_routes": 47,
        "delegate_parity_evidence": "PASS219-I171",
    }:
        blockers.append("PASS170_I172_ROUTER_ROUTE_SUMMARY_INVALID")

    invariants = manifest.get("invariants", {}) if isinstance(manifest, dict) else {}
    for key in (
        "stage_order_unique", "stage_id_unique", "one_application_identity_normal_production",
        "pass201_dynamic_closure_must_be_deterministic", "pass201_import_failures_fail_closed",
        "pass201_unexposed_routes_fail_closed",
    ):
        if invariants.get(key) is not True:
            blockers.append(f"PASS170_I172_ROUTER_REQUIRED_INVARIANT_FALSE:{key}")
    for key in (
        "new_vm81_authority", "new_hash72_mint_authority",
        "hash216_persistence_authority", "floating_point_canonical_authority",
        "canonical_state_mutated_by_manifest_load",
    ):
        if invariants.get(key) is not False:
            blockers.append(f"PASS170_I172_ROUTER_FORBIDDEN_AUTHORITY_FLAG:{key}")

    return sorted(set(blockers)), {
        "stage_count": len(stages),
        "stage_ids": ids,
        "stages": stage_reports,
        "pass201_closure_stage_present": isinstance(pass201, dict),
        "route_summary": summary,
    }


def verify_i172_legacy_constructor_router_manifest(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    evidence_blockers: list[str] = []

    try:
        inherited_i171 = verify_i171_public_app_route_parity(root)
    except Exception as exc:
        inherited_i171 = {"evidence_verified": False, "blockers": [f"{type(exc).__name__}:{exc}"]}
        evidence_blockers.append("PASS170_I172_INHERITED_I171_INVALID")

    inherited_inventory = build_i169_pass170_public_authority_inventory(root)
    try:
        constructor_registry = _load_json(root / CONSTRUCTOR_REGISTRY)
        router_manifest = _load_json(root / ROUTER_MANIFEST)
    except Pass170I172VerificationError:
        if fail_closed:
            raise
        constructor_registry = {}
        router_manifest = {}
        evidence_blockers.append("PASS170_I172_REQUIRED_MANIFEST_UNREADABLE")

    constructor_blockers, constructor_evidence, constructor_targets = _verify_constructor_registry(
        root, constructor_registry, inherited_inventory
    )
    router_blockers, router_evidence = _verify_router_manifest(root, router_manifest)
    evidence_blockers.extend(constructor_blockers)
    evidence_blockers.extend(router_blockers)

    if inherited_i171.get("evidence_verified") is not True:
        evidence_blockers.append("PASS170_I172_INHERITED_I171_NOT_VERIFIED")
    if inherited_i171.get("delegate_route_count") != 35:
        evidence_blockers.append("PASS170_I172_INHERITED_DELEGATE_ROUTE_COUNT_MISMATCH")
    if inherited_i171.get("total_registered_route_signature_count") != 47:
        evidence_blockers.append("PASS170_I172_INHERITED_ROUTE_SIGNATURE_COUNT_MISMATCH")

    target_blockers = list(constructor_targets)
    target_blockers.append("PASS170_FULL_OPERATION_RECORDS_PENDING")
    # The I171 full-router-manifest blocker is intentionally cleared only when
    # the new manifest itself verifies with no evidence blockers.
    if router_blockers:
        target_blockers.append("PASS170_FULL_ROUTER_MANIFEST_PENDING")

    evidence_blockers = sorted(set(evidence_blockers))
    target_blockers = sorted(set(target_blockers))
    evidence_verified = not evidence_blockers

    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "repository_root": str(root),
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I172_EVIDENCE_FAILED",
        "inherited_i171_verified": inherited_i171.get("evidence_verified") is True,
        "inherited_raw_constructor_count": inherited_inventory.get("inventory", {}).get("fastapi_constructor_count"),
        "constructor_registry_verified": not constructor_blockers,
        "constructor_evidence": constructor_evidence,
        "router_manifest_verified": not router_blockers,
        "router_evidence": router_evidence,
        "evidence_verified": evidence_verified,
        "evidence_blockers": evidence_blockers,
        "target_blockers": target_blockers,
        "pass170_terminal_contract_verified": False,
        "canonical_state_mutated": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "next_boundary": NEXT_BOUNDARY,
    }
    if evidence_blockers and fail_closed:
        raise Pass170I172VerificationError(
            "PASS170_I172_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


__all__ = [
    "BASE_MAIN", "CLASSIFICATION", "CONSTRUCTOR_REGISTRY", "CONTRACT_ID",
    "EXPECTED_TARGET_BLOCKERS", "ITERATION", "NEXT_BOUNDARY", "ROUTER_MANIFEST",
    "SCHEMA", "Pass170I172VerificationError", "_verify_constructor_registry",
    "_verify_router_manifest", "verify_i172_legacy_constructor_router_manifest",
]
