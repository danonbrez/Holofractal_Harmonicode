"""Canonical I172 gate assembly over the I172 constructor/router helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)
from hhs_runtime.pass219.pass170_public_app_route_parity_i171 import (
    verify_i171_public_app_route_parity,
)
from hhs_runtime.pass219.pass170_legacy_constructor_router_manifest_i172 import (
    BASE_MAIN,
    CLASSIFICATION,
    CONSTRUCTOR_REGISTRY,
    CONTRACT_ID,
    EXPECTED_TARGET_BLOCKERS,
    ITERATION,
    NEXT_BOUNDARY,
    ROUTER_MANIFEST,
    SCHEMA,
    Pass170I172VerificationError,
    _load_json,
    _verify_constructor_registry,
    _verify_router_manifest,
)


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
        inherited_i171 = {"i171_evidence_verified": False, "blockers": [f"{type(exc).__name__}:{exc}"]}
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

    if inherited_i171.get("i171_evidence_verified") is not True:
        evidence_blockers.append("PASS170_I172_INHERITED_I171_NOT_VERIFIED")
    if inherited_i171.get("delegate_route_count") != 35:
        evidence_blockers.append("PASS170_I172_INHERITED_DELEGATE_ROUTE_COUNT_MISMATCH")
    if inherited_i171.get("combined_registered_route_count") != 47:
        evidence_blockers.append("PASS170_I172_INHERITED_ROUTE_SIGNATURE_COUNT_MISMATCH")

    target_blockers = list(constructor_targets)
    target_blockers.append("PASS170_FULL_OPERATION_RECORDS_PENDING")
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
        "inherited_i171_verified": inherited_i171.get("i171_evidence_verified") is True,
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
    "EXPECTED_TARGET_BLOCKERS",
    "verify_i172_legacy_constructor_router_manifest",
]
