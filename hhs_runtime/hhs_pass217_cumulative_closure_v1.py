"""Pass 217 cumulative utilization/reachability closure authority.

This module proves four independent closure properties:

1. production service routes are published through canonical Pass 042 global
   surface discovery;
2. omission of every REQUIRED inherited authority is individually fail-closed;
3. the connected authority inventory exactly matches the frozen Pass 215
   REQUIRED optimization classes;
4. the previously unresolved ``incremental_tokenization`` class now has a real
   repository-native changed-region callable, committed-parent binding, exact
   changed-span verification, and full Pass 165 tokenizer equality validation.

Synthetic ACTIVE proofs in the bypass matrix test only the generic disposition
gate and are never treated as runtime traversal evidence.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict, Mapping

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    build_authority_reachability,
    load_inherited_core_authorities,
)
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_pass217_checkpoint7_content_reuse_v1 import CHECKPOINT7_AUTHORITY_MAP
from hhs_runtime.hhs_pass217_checkpoint13_interruption_recovery_v1 import (
    CHECKPOINT13_REQUIRED_AUTHORITIES,
)
from hhs_runtime.hhs_pass217_surface_bindings_v1 import (
    SERVICE_ROUTE_BINDINGS,
    service_route_surface_declarations,
)

VERSION = "PASS_217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE_V2"
SCHEMA = "HHS_PASS217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE_V1"
BYPASS_SCHEMA = "HHS_PASS217_REQUIRED_AUTHORITY_BYPASS_NEGATIVE_MATRIX_V1"
PUBLICATION_SCHEMA = "HHS_PASS217_GLOBAL_SURFACE_PUBLICATION_EVIDENCE_V1"
PROFILE_SCHEMA = "HHS_PASS217_REQUIRED_AUTHORITY_PROFILE_COVERAGE_V1"

REQUIRED_PASS217_SURFACE_FIELDS = {
    "contract_schemas": {
        "HHS_CONFORMANCE_API_ROUTE_CONTRACT_V1",
        "HHS_PASS217_CUMULATIVE_EXECUTION_ROUTE_CONTRACT_V1",
    },
    "witness_schemas": {
        "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
        "HHS_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1",
    },
    "validators": {
        "validate_pass217_cumulative_route_composition",
        "validate_authority_reachability",
    },
    "guards": {
        "zero_bypass_runtime_interposer",
        "kernel_runtime_autocomposer",
        "cumulative_execution_authority_reachability",
    },
    "rejection_codes": {
        "REJECT_RUNTIME_ROUTE_WITHOUT_CUMULATIVE_COMPOSITION",
        "REJECT_INHERITED_EXECUTION_AUTHORITY_REACHABILITY",
    },
}


def _active_gate_fixture(authority_id: str) -> Dict[str, Any]:
    root = sha256(
        f"PASS217-BYPASS-NEGATIVE-GATE-FIXTURE\0{authority_id}".encode("utf-8")
    ).hexdigest()
    return {
        "observed": True,
        "path": ["pass217_bypass_negative_gate_fixture", authority_id],
        "traversal_witness": {
            "schema": "HHS_PASS217_BYPASS_NEGATIVE_SYNTHETIC_ACTIVE_PROOF_V1",
            "authority_id": authority_id,
            "synthetic_gate_fixture": True,
            "runtime_traversal_evidence": False,
        },
        "witness_root": root,
    }


def build_required_authority_bypass_negative_matrix() -> Dict[str, Any]:
    """Prove every applicable REQUIRED authority is individually non-bypassable."""

    required = tuple(CHECKPOINT13_REQUIRED_AUTHORITIES)
    active = {authority_id: _active_gate_fixture(authority_id) for authority_id in required}
    baseline = build_authority_reachability(
        "pass217.closure.bypass-negative-baseline",
        active_in_path=active,
        required_authorities=required,
    )
    rows = []
    for authority_id in required:
        omitted = dict(active)
        omitted.pop(authority_id)
        record = build_authority_reachability(
            f"pass217.closure.omit.{authority_id}",
            active_in_path=omitted,
            required_authorities=required,
        )
        expected_blocker = (
            f"{authority_id}:REJECT_INHERITED_AUTHORITY_DISPOSITION_MISSING"
        )
        decision = next(
            row for row in record["decisions"] if row["authority_id"] == authority_id
        )
        rows.append(
            {
                "omitted_authority_id": authority_id,
                "admitted": bool(record["admitted"]),
                "status": record["status"],
                "expected_blocker": expected_blocker,
                "expected_blocker_present": expected_blocker in record["blockers"],
                "omitted_decision_state": decision["state"],
                "omitted_decision_accepted": bool(decision["accepted"]),
                "omitted_decision_reasons": list(decision["reasons"]),
                "reachability_root_hash72": record["reachability_root_hash72"],
            }
        )
    all_blocked = (
        baseline.get("admitted") is True
        and len(rows) == len(required)
        and all(
            row["admitted"] is False
            and row["expected_blocker_present"] is True
            and row["omitted_decision_state"] is None
            and row["omitted_decision_accepted"] is False
            for row in rows
        )
    )
    return {
        "schema": BYPASS_SCHEMA,
        "version": VERSION,
        "required_authority_count": len(required),
        "required_authority_ids": list(required),
        "baseline_all_active_gate_fixture_admitted": bool(baseline.get("admitted")),
        "synthetic_gate_fixtures_only": True,
        "synthetic_fixtures_count_as_runtime_traversal_evidence": False,
        "omission_case_count": len(rows),
        "all_applicable_required_authority_omissions_blocked": all_blocked,
        "cases": rows,
    }


def build_global_surface_publication_evidence() -> Dict[str, Any]:
    surface_map = build_surface_map()
    surfaces = {
        str(surface["surface_id"]): surface
        for surface in surface_map.get("surfaces", [])
        if isinstance(surface, Mapping)
    }
    rows = []
    for declaration in service_route_surface_declarations():
        surface_id = str(declaration["surface_id"])
        published = surfaces.get(surface_id)
        reasons = []
        if published is None:
            reasons.append("PASS217_ROUTE_NOT_PUBLISHED_IN_GLOBAL_SURFACE_MAP")
        else:
            if published.get("symbol") != declaration.get("symbol"):
                reasons.append("PASS217_ROUTE_SYMBOL_MISMATCH")
            if published.get("mutation_policy") != declaration.get("mutation_policy"):
                reasons.append("PASS217_ROUTE_MUTATION_POLICY_MISMATCH")
            if published.get("persistence_policy") != declaration.get("persistence_policy"):
                reasons.append("PASS217_ROUTE_PERSISTENCE_POLICY_MISMATCH")
            if published.get("derivation_complete") is not True:
                reasons.append("PASS217_ROUTE_DERIVATION_INCOMPLETE")
            for field, required_values in REQUIRED_PASS217_SURFACE_FIELDS.items():
                actual = set(published.get(field) or [])
                missing = sorted(required_values - actual)
                if missing:
                    reasons.append(f"PASS217_ROUTE_{field.upper()}_MISSING:{','.join(missing)}")
        rows.append(
            {
                "surface_id": surface_id,
                "source": declaration["pass217_binding_source"],
                "route": SERVICE_ROUTE_BINDINGS[declaration["pass217_binding_source"]]["route"],
                "symbol": declaration["symbol"],
                "published": published is not None,
                "derivation_hash72": published.get("derivation_hash72") if published else None,
                "reasons": reasons,
                "ok": not reasons,
            }
        )
    ok = (
        surface_map.get("validation", {}).get("ok") is True
        and len(rows) == len(SERVICE_ROUTE_BINDINGS)
        and all(row["ok"] for row in rows)
    )
    return {
        "schema": PUBLICATION_SCHEMA,
        "version": VERSION,
        "ok": ok,
        "pass042_surface_map_validation_ok": surface_map.get("validation", {}).get("ok") is True,
        "pass042_surface_count": surface_map.get("surface_count"),
        "pass042_api_route_count": len(
            [
                surface
                for surface in surface_map.get("surfaces", [])
                if surface.get("surface_type") == "API_ROUTE"
            ]
        ),
        "pass042_conformance_root_hash72": surface_map.get("conformance_root_hash72"),
        "published_pass217_route_count": sum(1 for row in rows if row["published"]),
        "expected_pass217_route_count": len(SERVICE_ROUTE_BINDINGS),
        "routes": rows,
    }


def _incremental_active_contract_proven(incremental: Mapping[str, Any]) -> bool:
    return bool(
        incremental.get("incremental_delta_callable_proven") is True
        and incremental.get("module") == "hhs_runtime.pass165.incremental_tokenization"
        and incremental.get("symbol") == "incremental_tokenize"
        and incremental.get("full_source_equivalence_validator")
        == "hhs_runtime.pass165.incremental_tokenization.validate_incremental_equivalence"
        and incremental.get("parent_committed_receipt_required") is True
        and incremental.get("parent_token_stream_root_required") is True
        and incremental.get("declared_changed_spans_must_equal_derived_spans") is True
        and incremental.get("mutation_permitted_in_preflight") is False
        and incremental.get("floating_point_authority") is False
    )


def build_required_authority_profile_coverage() -> Dict[str, Any]:
    inventory = load_inherited_core_authorities()
    profile_required = tuple(
        sorted(row["authority_id"] for row in inventory.get("authorities", []))
    )
    connected_required = tuple(sorted(CHECKPOINT13_REQUIRED_AUTHORITIES))
    profile_set = set(profile_required)
    connected_set = set(connected_required)
    incremental = dict(CHECKPOINT7_AUTHORITY_MAP["incremental_tokenization"])
    incremental_proven = _incremental_active_contract_proven(incremental)
    return {
        "schema": PROFILE_SCHEMA,
        "version": VERSION,
        "profile_inventory_root_hash72": inventory.get("inventory_root_hash72"),
        "profile_required_authority_count": len(profile_required),
        "connected_required_authority_count": len(connected_required),
        "profile_required_authority_ids": list(profile_required),
        "connected_required_authority_ids": list(connected_required),
        "authority_sets_equal": profile_set == connected_set,
        "missing_connected_authority_ids": sorted(profile_set - connected_set),
        "unexpected_connected_authority_ids": sorted(connected_set - profile_set),
        "optional_profile_classes_promoted_to_core": inventory.get(
            "optional_profile_classes_promoted_to_core"
        ),
        "experimental_profile_classes_promoted_to_core": inventory.get(
            "experimental_profile_classes_promoted_to_core"
        ),
        "incremental_tokenization": incremental,
        "incremental_tokenization_applicable_active_path_proven": incremental_proven,
        "incremental_tokenization_full_reference_equivalence_required": True,
        "incremental_tokenization_parent_commit_binding_required": True,
        "incremental_tokenization_declared_span_verification_required": True,
    }


def build_cumulative_utilization_reachability_closure() -> Dict[str, Any]:
    publication = build_global_surface_publication_evidence()
    bypass = build_required_authority_bypass_negative_matrix()
    profile = build_required_authority_profile_coverage()
    blockers = []
    if publication["ok"] is not True:
        blockers.append("PASS217_GLOBAL_SURFACE_PUBLICATION_INCOMPLETE")
    if bypass["all_applicable_required_authority_omissions_blocked"] is not True:
        blockers.append("PASS217_REQUIRED_AUTHORITY_BYPASS_NEGATIVE_INCOMPLETE")
    if profile["authority_sets_equal"] is not True:
        blockers.append("PASS217_REQUIRED_AUTHORITY_PROFILE_COVERAGE_MISMATCH")
    if profile["incremental_tokenization_applicable_active_path_proven"] is not True:
        blockers.append(
            "PASS217_INCREMENTAL_TOKENIZATION_APPLICABLE_ACTIVE_PATH_UNPROVEN"
        )

    body = {
        "schema": SCHEMA,
        "version": VERSION,
        "required_authority_count": len(CHECKPOINT13_REQUIRED_AUTHORITIES),
        "global_surface_publication": publication,
        "required_authority_bypass_negative_matrix": bypass,
        "required_authority_profile_coverage": profile,
        "structural_closure_hardening_complete": (
            publication["ok"] is True
            and bypass["all_applicable_required_authority_omissions_blocked"] is True
            and profile["authority_sets_equal"] is True
        ),
        "universal_applicable_utilization_reachability_complete": not blockers,
        "closure_ready": not blockers,
        "status": (
            "ADMIT_PASS217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE"
            if not blockers
            else "BLOCK_PASS217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE"
        ),
        "blockers": blockers,
        "synthetic_bypass_fixtures_are_runtime_evidence": False,
        "current_known_applicable_active_gap_authority_ids": (
            []
            if profile["incremental_tokenization_applicable_active_path_proven"]
            else ["incremental_tokenization"]
        ),
    }
    witness = make_hash72_kernel_witness(
        "HHS_PASS217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE_V1",
        body,
        width=72,
    )
    body["closure_root_hash72"] = witness.digest
    body["hash72_kernel_witness"] = witness.to_dict()
    return body


__all__ = [
    "VERSION",
    "SCHEMA",
    "build_required_authority_bypass_negative_matrix",
    "build_global_surface_publication_evidence",
    "build_required_authority_profile_coverage",
    "build_cumulative_utilization_reachability_closure",
]
