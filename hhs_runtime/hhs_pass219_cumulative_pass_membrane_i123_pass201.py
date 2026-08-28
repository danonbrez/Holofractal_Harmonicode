"""Pass 219 I123 read-only membrane for accepted Pass 201 public API federation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i122_pass202 import pass202_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_23"
PASS201_NUMBER = 201
PASS201_CLASSIFICATION = "WIRED"
PASS201_CENSUS_CLASSIFICATION = "MISSING_MEMBRANE_EXPOSURE"
PASS201_BIND_SYMBOL = "hhs_exact_pass219_bind_pass201_public_api_federation"
PASS201_SURFACE_ID = "validator:pass219.inherited.pass201.public-api-federation"

P = Path
CONTRACT_PATH = P("HHS_PASS_201_PUBLIC_API_FEDERATION.md")
WORKFLOW_PATH = P(".github/workflows/pass201-public-api-federation.yml")
RUNTIME_V1_PATH = P("hhs_backend/runtime/hhs_pass201_public_api_federation_v1.py")
PRODUCTION_PATH = P("hhs_backend/runtime/hhs_pass201_public_api_federation.py")
PUBLIC_ROUTES_PATH = P("hhs_backend/api/public_api_registry_routes.py")
CONTRACT_TEST_PATH = P("tests/test_hhs_pass201_public_api_federation_v1.py")
VALIDATOR_PATH = P("scripts/pass201_public_api_validation.py")
RESTART_PATH = P("docs/pass201/RESTART_RECORD.md")
PASS202_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i122_pass202.py")

PRIMARY_BASE = "0da486d86b55074baadd4a3e5cffb5f87893526b"
VALIDATED_EXECUTABLE_HEAD = "2f5299b44b6ee01af73e43a57d27cc7c6e2f7eda"
EVIDENCE_HEAD = "f7fbd3007c7e08d5566e5176eb4eed955f44b739"
ACCEPTED_MERGE = "0e3f8a49b4a9b1e5b9b79e0dc73adebeef933f58"
FROZEN_I122 = "a8d08be6d16722df6f42f1f88eef2a83f895107e"

HISTORICAL_BLOBS = {
    CONTRACT_PATH: "88a34ca711b2b85dc8fa157a71125ce6d31919a8",
    WORKFLOW_PATH: "0171e64ba9ef1228c05852fc51c375abed21abdd",
    RUNTIME_V1_PATH: "99a5b966b2885a24b5d3d1a47b39b3eb7060d211",
    PRODUCTION_PATH: "5b07f7369e702afef69358081d3ab67519dc91e1",
    PUBLIC_ROUTES_PATH: "84e5acdcbea9c5f85ac38a1b792733c52b232edb",
    CONTRACT_TEST_PATH: "da90ba15304e4fd73b987151b01c7db459f2f93c",
    VALIDATOR_PATH: "0489ccba5d6d1b5a7ceda04c13621091ece8f3c7",
}

HISTORICAL_CLOSURE = {
    "api_modules": 37,
    "imported_api_modules": 37,
    "api_import_failures": 0,
    "routers": 39,
    "router_routes_discovered": 452,
    "existing_routes_preserved": 273,
    "routes_attached_by_federation": 179,
    "unexposed_router_routes": 0,
    "public_routes": 449,
    "public_services": 68,
    "public_pass_modules": 41,
    "openapi_paths": 421,
    "openapi_missing_operations": 0,
    "validated_public_endpoints": 12,
}

REQUIRED_OPERATIONS = (
    "validate_pass201_squash_identity",
    "validate_pass201_router_closure",
    "validate_pass201_deterministic_catalog",
    "validate_pass201_public_tool_boundary",
    "validate_pass201_production_projection",
    "validate_pass202_successor_binding",
    "validate_pass201_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS201_SOURCE_BOUNDARY_DRIFT:{path}:{fragment}")


def pass201_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_MERGE, "HEAD") != "":
        raise RuntimeError("PASS201_ACCEPTED_MERGE_ANCESTRY_OUTPUT")
    evidence_merge_base = _git("merge-base", EVIDENCE_HEAD, "HEAD")
    if evidence_merge_base != PRIMARY_BASE:
        raise RuntimeError(f"PASS201_SQUASH_LINEAGE_DRIFT:{evidence_merge_base}")

    for path, expected in HISTORICAL_BLOBS.items():
        historical = _git("rev-parse", f"{ACCEPTED_MERGE}:{path}")
        if historical != expected:
            raise RuntimeError(f"PASS201_HISTORICAL_BLOB_DRIFT:{path}:{historical}")
        current = _git_blob(path)
        if current != expected:
            raise RuntimeError(f"PASS201_FROZEN_I122_BLOB_DRIFT:{path}:{current}")

    _require(
        CONTRACT_PATH,
        "HHS-P201-PUBLIC-API-FEDERATION-SERVICE-PASS-ROUTER-OPENAPI",
        "attach each missing route exactly once",
        "Existing explicit router composition remains valid",
        "route identifier is a deterministic SHA-256 digest",
        "It is an index identity, not runtime authority",
        "does not create a generic arbitrary Python-call surface",
        "static `/` remains last",
    )
    _require(
        RUNTIME_V1_PATH,
        "register_all_api_routers",
        '"unexposed_route_count"',
        '"arbitrary_python_execution_public": False',
        '"native_authority_routes_preserved": True',
        'payload["catalog_sha256"] = _digest(payload)',
    )
    _require(
        PRODUCTION_PATH,
        "Production federation with canonical OpenAPI path normalization",
        "_openapi_path",
        "PASS201_PUBLIC_API_FEDERATION = PublicAPIFederation()",
        "register_public_api_federation",
    )
    _require(
        PUBLIC_ROUTES_PATH,
        '/status")',
        '/catalog")',
        '/routes")',
        '/services")',
        '/passes")',
        '/openapi")',
        '/tools")',
        '/tools/invoke")',
        '"arbitrary_python_execution_public": False',
        '"tool_server_is_runtime_authority": False',
    )
    _require(
        CONTRACT_TEST_PATH,
        "test_all_api_modules_import_and_all_router_routes_are_exposed",
        "test_catalog_identity_is_deterministic",
        "test_static_root_mount_is_last",
    )
    _require(
        VALIDATOR_PATH,
        'report["import_failure_count"] == 0',
        'report["unexposed_route_count"] == 0',
        'catalog["openapi_missing_count"] == 0',
        "public_routes_precede_unknown_api_fallback",
        "deterministic_restart_projection",
    )
    _require(
        WORKFLOW_PATH,
        "Run public API federation tests",
        "Execute production public API validation",
        "Verify federation wiring and claim boundary",
    )
    _require(
        RESTART_PATH,
        "Successful run: `30784863958`",
        "Validated executable head: `2f5299b44b6ee01af73e43a57d27cc7c6e2f7eda`",
        "Artifact:\n\n- ID: `8844926215`",
        "sha256:903bd1196a08ba4f1976348e190a59122e35b907fce1dc197062caaa2397499f",
    )

    successor = pass202_membrane_source_evidence()
    return {
        "primary_base": PRIMARY_BASE,
        "validated_executable_head": VALIDATED_EXECUTABLE_HEAD,
        "evidence_head": EVIDENCE_HEAD,
        "accepted_merge": ACCEPTED_MERGE,
        "frozen_i122": FROZEN_I122,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "historical_closure": dict(HISTORICAL_CLOSURE),
        "canonical_successful_run": 30784863958,
        "receipt_updated_successful_run": 30785029454,
        "artifact_id": 8844926215,
        "artifact_digest": "sha256:903bd1196a08ba4f1976348e190a59122e35b907fce1dc197062caaa2397499f",
        "pass202_successor": successor,
    }


def validate_pass201_squash_identity() -> Dict[str, Any]:
    s = pass201_membrane_source_evidence()
    return {
        "ok": True,
        "pull_request": 142,
        "primary_base": s["primary_base"],
        "validated_executable_head": s["validated_executable_head"],
        "evidence_head": s["evidence_head"],
        "accepted_merge": s["accepted_merge"],
        "squash_aware": True,
        "historical_source_blobs_unchanged_at_frozen_i122": True,
    }


def validate_pass201_router_closure() -> Dict[str, Any]:
    s = pass201_membrane_source_evidence()
    return {
        "ok": True,
        **s["historical_closure"],
        "all_registered_routers_public": True,
        "missing_routes_attached_only": True,
        "existing_explicit_routes_preserved": True,
    }


def validate_pass201_deterministic_catalog() -> Dict[str, Any]:
    pass201_membrane_source_evidence()
    return {
        "ok": True,
        "route_identity": "SHA256_CANONICAL_ROUTE_INDEX",
        "route_identity_is_runtime_authority": False,
        "service_catalog_public": True,
        "pass_module_catalog_public": True,
        "openapi_projection_complete": True,
        "deterministic_restart_projection": True,
    }


def validate_pass201_public_tool_boundary() -> Dict[str, Any]:
    pass201_membrane_source_evidence()
    return {
        "ok": True,
        "catalog_tool_interface_bounded": True,
        "arbitrary_python_execution_public": False,
        "tool_server_is_runtime_authority": False,
        "native_mutating_routes_keep_inherited_authority": True,
    }


def validate_pass201_production_projection() -> Dict[str, Any]:
    pass201_membrane_source_evidence()
    return {
        "ok": True,
        "openapi_path_converter_normalization": True,
        "public_routes_precede_unknown_api_fallback": True,
        "visual_server_static_root_last": True,
        "application_ide_static_root_last": True,
        "native_routes_reordered": False,
    }


def validate_pass202_successor_binding() -> Dict[str, Any]:
    successor = pass201_membrane_source_evidence()["pass202_successor"]
    return {
        "ok": True,
        "successor_pass": 202,
        "successor_primary_merge": successor["primary_merge"],
        "successor_bootstrap_merge": successor["bootstrap_merge"],
        "successor_preserved": True,
    }


def validate_pass201_no_new_authority() -> Dict[str, Any]:
    pass201_membrane_source_evidence()
    return {
        "ok": True,
        "i123_new_public_execution_authority": False,
        "i123_new_canonical_mutation_authority": False,
        "i123_new_persistence_authority": False,
        "i123_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
    }


def pass201_surface_declaration() -> Dict[str, Any]:
    pass201_membrane_source_evidence()
    return {
        "surface_id": PASS201_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i123_pass201",
        "symbol": "validate_pass201_squash_identity",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P201-PUBLIC-API-FEDERATION-SERVICE-PASS-ROUTER-OPENAPI"],
        "witness_schemas": ["HHSExactPass201PublicAPIFederationWitnessV1", "HHSExactPass219InheritedPass201BindingV1"],
        "validators": [PASS201_BIND_SYMBOL, "validate_pass201_squash_identity"],
        "guards": [
            "pass201_squash_identity",
            "pass201_immutable_source_identity",
            "pass201_router_closure",
            "pass201_deterministic_catalog",
            "pass201_bounded_tool_boundary",
            "pass201_pass202_successor_preserved",
        ],
        "rejection_codes": [
            "REJECT_PASS201_SQUASH_IDENTITY_DRIFT",
            "REJECT_PASS201_SOURCE_IDENTITY_DRIFT",
            "REJECT_PASS201_ROUTER_CLOSURE_DRIFT",
            "REJECT_PASS201_CATALOG_DRIFT",
            "REJECT_PASS201_TOOL_AUTHORITY_DRIFT",
            "REJECT_PASS201_PASS202_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS201_PUBLIC_CATALOG_READ_ONLY_BINDING",
        "boundedness_policy": "PASS_201_VERIFIED_FEDERATION_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass201_membrane_manifest() -> Dict[str, Any]:
    s = pass201_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS201_NUMBER,
        "classification": PASS201_CLASSIFICATION,
        "census_classification": PASS201_CENSUS_CLASSIFICATION,
        "pass219_c_abi_surface": PASS201_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass201PublicAPIFederation",
        "primary_pull_request": 142,
        "accepted_merge": s["accepted_merge"],
        "evidence_head": s["evidence_head"],
        "frozen_i122": s["frozen_i122"],
        "historical_squash_identity_bound": True,
        "immutable_source_identity_bound": True,
        "router_closure_bound": True,
        "deterministic_catalog_bound": True,
        "bounded_tool_boundary_bound": True,
        "native_route_authority_preserved_bound": True,
        "pass202_successor_bound": True,
        "pass219_new_public_execution_authority": False,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "historical_blobs": s["historical_blobs"],
        "historical_closure": s["historical_closure"],
        "surface": pass201_surface_declaration(),
    }


def preflight_pass201_membrane() -> Dict[str, Any]:
    declaration = pass201_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I123_PASS201_MEMBRANE_PREFLIGHT_V1",
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS201_SURFACE_ID,
        "operations": rows,
        "manifest": pass201_membrane_manifest(),
    }


if __name__ == "__main__":
    print(json.dumps(preflight_pass201_membrane(), indent=2, sort_keys=True))
