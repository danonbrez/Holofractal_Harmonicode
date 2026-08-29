"""Pass 219 I138 cumulative membrane for inherited Pass 188 full completion."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_38"
PASS188_NUMBER = 188
PASS188_CLASSIFICATION = "WIRED"
PASS188_CENSUS_CLASSIFICATION = (
    "HISTORICAL_BOTT_RUNTIME_VERIFIED_AND_VERSIONED_LICENSE_"
    "CONTRACT_IMPLEMENTATION_GAP_CLOSED_BY_I138"
)
PASS188_BIND_SYMBOL = "hhs_exact_pass219_bind_pass188_cumulative_authority"
PASS188_SURFACE_ID = "validator:pass219.inherited.pass188.full-completion"

P = Path
LICENSE_CONTRACT_PATH = P(
    "docs/pass188/"
    "HHS_PASS_188_VERSIONED_NFT_CONTENT_LICENSE_LINEAGE_AND_LEGACY_STATE_PROTECTION.md"
)
BOTT_DOC_PATH = P("HHS_PASS_188_BOTT_RUNTIME_FULL_SURFACE_IMPLEMENTATION.md")
BOTT_ROOT = P("native_projects/hhs_pass188_bott_runtime")
BOTT_MAKEFILE_PATH = BOTT_ROOT / "Makefile"
BOTT_README_PATH = BOTT_ROOT / "README.md"
BOTT_MANIFEST_PATH = BOTT_ROOT / "evidence/P188_SOURCE_MANIFEST.json"
BOTT_RECEIPT_PATH = BOTT_ROOT / "evidence/P188_VALIDATION_RECEIPT.json"
BOTT_HEADER_PATH = BOTT_ROOT / "include/hhs_pass188_bott_runtime.h"
BOTT_SOURCE_PATH = BOTT_ROOT / "src/hhs_pass188_bott_runtime.c"
BOTT_ASM_PATH = BOTT_ROOT / "src/hhs_pass188_bott_step_x86_64.S"
BOTT_PYTHON_PATH = BOTT_ROOT / "python/hhs_pass188.py"
BOTT_PYTHON_TEST_PATH = BOTT_ROOT / "python/test_hhs_pass188.py"
BOTT_SERVER_PATH = BOTT_ROOT / "server/hhs_pass188_server.py"
BOTT_C_TEST_PATH = BOTT_ROOT / "tests/hhs_pass188_bott_runtime_test.c"
BOTT_CLI_PATH = BOTT_ROOT / "tools/hhs_pass188_cli.c"
BOTT_SMOKE_PATH = BOTT_ROOT / "tools/hhs_pass188_surface_smoke.py"
BOTT_WEB_PATH = BOTT_ROOT / "web/index.html"

LICENSE_INIT_PATH = P("hhs_runtime/pass188/__init__.py")
LICENSE_RUNTIME_PATH = P("hhs_runtime/pass188/license_lineage.py")
LICENSE_SERVER_PATH = P("hhs_runtime/pass188/license_server.py")
LICENSE_TEST_PATH = P("tests/pass188/test_pass188_license_lineage.py")
LICENSE_README_PATH = P("native_projects/hhs_pass188_license_lineage/README.md")
LICENSE_MAKEFILE_PATH = P("native_projects/hhs_pass188_license_lineage/Makefile")
LICENSE_WORKFLOW_PATH = P(".github/workflows/pass188-license-lineage-completion.yml")
SCHEMA_CONTENT_PATH = P("schemas/pass188/HHS_PASS_188_CONTENT_VERSION_V1.schema.json")
SCHEMA_LICENSE_PATH = P("schemas/pass188/HHS_PASS_188_LICENSE_VERSION_V1.schema.json")
SCHEMA_DELTA_PATH = P("schemas/pass188/HHS_PASS_188_LICENSE_DELTA_V1.schema.json")
SCHEMA_BINDING_PATH = P("schemas/pass188/HHS_PASS_188_BINDING_V1.schema.json")
SCHEMA_EVENT_PATH = P("schemas/pass188/HHS_PASS_188_EVENT_V1.schema.json")

NATIVE_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass188_1_38.h")
NATIVE_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass188_1_38.hpp")
NATIVE_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass188_1_38.inc")
EXACT_HEADER_PATH = P("hhs_runtime/include/hhs_runtime_exact_abi.h")
EXACT_SOURCE_PATH = P("hhs_runtime/c/hhs_runtime_exact_abi.c")

PASS189_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i137_pass189.py")
PASS189_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass189_1_37.h")
PASS189_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass189_1_37.hpp")
PASS189_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass189_1_37.inc")

LICENSE_CONTRACT_COMMIT = "50aec3f624fe6cbaefa3220b7d709bb1b388a942"
BOTT_RUNTIME_COMMIT = "c77e3feef42448a111d8b8912a1d1cb157d51925"
LICENSE_COMPLETION_HEAD = "8e6f209aa8974da30d0b1dcb85a7ca2dc10060c6"
FROZEN_I137 = "ef27a1caf0d977e0f767b13126dba8fe49b09dab"
FOCUSED_LICENSE_RUN = 33177282910
FOCUSED_LICENSE_JOB = 98869073632

BOTT_BLOBS = {
    BOTT_DOC_PATH: "4ab77654e688283e1042b68f2cf3aacdd7d6feda",
    BOTT_MAKEFILE_PATH: "9fe456a72d393c832e3db0472f052e3409914951",
    BOTT_README_PATH: "038e54424059ccebab5b5ff0b531f095e1604db7",
    BOTT_MANIFEST_PATH: "dacabcf69c8576745dffe3a50af38326bac26c97",
    BOTT_RECEIPT_PATH: "492d60716896c66cdb507f6e76163d988d1d41e6",
    BOTT_HEADER_PATH: "880e18c9c88c050a98be8bff35969821dfcb7ad4",
    BOTT_SOURCE_PATH: "643cc11704d39cc87c30a7ec351307dd431ab95e",
    BOTT_ASM_PATH: "e424c8559ea82fe95a46639a97f273d65c4d6de6",
    BOTT_PYTHON_PATH: "ec054ec687a938dd70b7215dddcc449c322d9b72",
    BOTT_PYTHON_TEST_PATH: "7d747904542e514148426113bdee683f37894ad5",
    BOTT_SERVER_PATH: "547055d599f0d57dd92baba319ec506218e52ca0",
    BOTT_C_TEST_PATH: "370ec89ac248406b67d7e9d86a9a04a61da82ae2",
    BOTT_CLI_PATH: "d33ce66efdec194d721abbcdbf96b1120e5d0905",
    BOTT_SMOKE_PATH: "3bc6a09fd9727ffe7f8ac92c23f793b3a1583be8",
    BOTT_WEB_PATH: "c813234262a1041017d8b177cf1f1825600c46b6",
}
LICENSE_BLOBS = {
    LICENSE_CONTRACT_PATH: "871ed3fff0a677ad6173eb00a099d010ac1a730b",
    LICENSE_INIT_PATH: "26b9e3f017e67c98a9d7eaa19a1c407d7e45d2c2",
    LICENSE_RUNTIME_PATH: "9ead3669a04b211be09adca66b35f37269350056",
    LICENSE_SERVER_PATH: "33a5ab11dcb557a87ad465ccba2b726cc1375348",
    LICENSE_TEST_PATH: "e55466723c0f15667fea93ecbb076a1f2fb5d570",
    LICENSE_README_PATH: "53b1beba38e17defea694e734920535a68c5b23a",
    LICENSE_MAKEFILE_PATH: "01c30f4c5c2099e3bef0367f2fc5a342cabd7b90",
    LICENSE_WORKFLOW_PATH: "943f93de78036622be13fe6f530e2a5c596de7e6",
    SCHEMA_CONTENT_PATH: "6a01f5ccb1446b9a1f0a730d001e68635ce041ea",
    SCHEMA_LICENSE_PATH: "0f02f8f787aeba12e788c717acb0f92584f7bbdf",
    SCHEMA_DELTA_PATH: "91e280b1660460e6950818cdaa7f5bb3c8a776d4",
    SCHEMA_BINDING_PATH: "07b054b75fca66893b35a86f8a689fc559f032a0",
    SCHEMA_EVENT_PATH: "f4f5e186f3369fc33050daf7616ad63a864686f2",
}
NATIVE_BLOBS = {
    NATIVE_HEADER_PATH: "fe13e2e53301b0cb73210879fd41d49c0c101f9b",
    NATIVE_HPP_PATH: "bc957286ce8a6fcbcdceca170dd49aa17801b414",
    NATIVE_INC_PATH: "a38cd30c383cd6f2e1140036865cfd7008d839c2",
    EXACT_HEADER_PATH: "fa6cd855f64bf9f76dc3a26743f69b3a8109c84c",
    EXACT_SOURCE_PATH: "95ccd25f2bd06ed3afdb6d3dfb5c3ac6ae438698",
}
PASS189_FROZEN_BLOBS = {
    PASS189_MEMBRANE_PATH: "2ef0c3bf89b5ff367b9da8a9fbf7d8ab78f761cb",
    PASS189_HEADER_PATH: "f487d7e67402cce3b97124dea531347e10b4be07",
    PASS189_HPP_PATH: "610bcb4c9b823c457d3a049c45426ff57d5c992c",
    PASS189_INC_PATH: "a3c054c8b4592a3a22944e5418a8847958156556",
}

REQUIRED_OPERATIONS = (
    "validate_pass188_historical_lineage",
    "validate_pass188_license_completion_boundary",
    "validate_pass188_license_authority_boundary",
    "validate_pass188_license_legacy_evidence_boundary",
    "validate_pass188_bott_runtime_boundary",
    "validate_pass188_exact_arithmetic_boundary",
    "validate_pass188_successor_binding",
    "validate_pass188_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


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


def _git_blob(path: Path) -> str:
    return _git("hash-object", str(path))


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS188_SOURCE_DRIFT:{path}:{fragment}")


def _frozen_pass189_successor_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", FROZEN_I137, "HEAD")
    for path, expected in PASS189_FROZEN_BLOBS.items():
        actual = _git("rev-parse", f"{FROZEN_I137}:{path}")
        if actual != expected:
            raise RuntimeError(f"PASS188_PASS189_FROZEN_SUCCESSOR_DRIFT:{path}")
    return {
        "pass_number": 189,
        "frozen_commit": FROZEN_I137,
        "membrane_blob": PASS189_FROZEN_BLOBS[PASS189_MEMBRANE_PATH],
        "header_blob": PASS189_FROZEN_BLOBS[PASS189_HEADER_PATH],
        "hpp_blob": PASS189_FROZEN_BLOBS[PASS189_HPP_PATH],
        "inc_blob": PASS189_FROZEN_BLOBS[PASS189_INC_PATH],
        "successor_preserved": True,
    }


def pass188_membrane_source_evidence() -> Dict[str, Any]:
    for commit in (
        LICENSE_CONTRACT_COMMIT,
        BOTT_RUNTIME_COMMIT,
        LICENSE_COMPLETION_HEAD,
        FROZEN_I137,
    ):
        _git("merge-base", "--is-ancestor", commit, "HEAD")
    if _git("merge-base", "HEAD", FROZEN_I137) != FROZEN_I137:
        raise RuntimeError("PASS188_FROZEN_I137_LINEAGE_DRIFT")

    if _git(
        "rev-parse", f"{LICENSE_CONTRACT_COMMIT}:{LICENSE_CONTRACT_PATH}"
    ) != LICENSE_BLOBS[LICENSE_CONTRACT_PATH]:
        raise RuntimeError("PASS188_LICENSE_CONTRACT_DRIFT")
    if _git(
        "rev-parse", f"{BOTT_RUNTIME_COMMIT}:{BOTT_RECEIPT_PATH}"
    ) != BOTT_BLOBS[BOTT_RECEIPT_PATH]:
        raise RuntimeError("PASS188_BOTT_RECEIPT_DRIFT")

    for path, expected in BOTT_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS188_BOTT_SOURCE_DRIFT:{path}")
    for path, expected in LICENSE_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS188_LICENSE_SOURCE_DRIFT:{path}")
    for path, expected in NATIVE_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS188_NATIVE_MEMBRANE_DRIFT:{path}")

    _require(
        LICENSE_CONTRACT_PATH,
        "HHS-P188-VNFTCLL-LOSP-VM81-H72-H216",
        "Every mutation must require explicit authority and emit a canonical receipt.",
        "Pass 188 cannot be marked complete until executable tests prove:",
        "browser-local state, wallet display, or marketplace metadata cannot grant canonical runtime authorization",
    )
    _require(
        LICENSE_RUNTIME_PATH,
        'CONTRACT_ID = "HHS-P188-VNFTCLL-LOSP-VM81-H72-H216"',
        'conn.execute("BEGIN IMMEDIATE")',
        "require_hash72(authority_hash72,",
        '"new_vm81_authority": False',
        '"new_hash72_clock": False',
        '"external_context_authority"] = False',
        "COMPATIBILITY_FLOOR",
        "HHS_PASS_188_VERSIONED_CONTENT_LICENSE_AND_LEGACY_STATE_VERIFIED",
    )
    _require(
        LICENSE_TEST_PATH,
        "test_full_contract_acceptance_scenarios",
        "# 1. Two projects are admitted under exact content/license v1.",
        "# 14. Cold restart replay and checkpoint recovery preserve exact root.",
        "# 16. Browser/wallet/marketplace display cannot grant runtime authorization.",
        "COMPLETION_CLASSIFICATION",
    )
    _require(
        LICENSE_WORKFLOW_PATH,
        "Pass 188 Versioned License Lineage Completion",
        "make -C native_projects/hhs_pass188_license_lineage validate",
    )
    _require(
        BOTT_DOC_PATH,
        "HHS-P188-BOTT-RUNTIME-H216-VM81-Q144-G243-X64",
        "Projected transitions are pure candidate calculations.",
        "only an external authorized commit layer may append them to the canonical Hash72 stream",
        "HHS_PASS_188_BOTT_RUNTIME_FULL_SURFACE_IMPLEMENTATION",
    )
    _require(
        BOTT_RECEIPT_PATH,
        "HHS_PASS_188_BOTT_RUNTIME_FULL_SURFACE_IMPLEMENTATION_VERIFIED",
        '"native_exhaustive_addresses": 1259712',
        '"native_replay_addresses": 1259712',
    )

    successor = _frozen_pass189_successor_evidence()
    return {
        "license_contract_commit": LICENSE_CONTRACT_COMMIT,
        "bott_runtime_commit": BOTT_RUNTIME_COMMIT,
        "license_completion_head": LICENSE_COMPLETION_HEAD,
        "focused_license_run": FOCUSED_LICENSE_RUN,
        "focused_license_job": FOCUSED_LICENSE_JOB,
        "frozen_i137": FROZEN_I137,
        "bott_blobs": {str(path): value for path, value in BOTT_BLOBS.items()},
        "license_blobs": {str(path): value for path, value in LICENSE_BLOBS.items()},
        "native_blobs": {str(path): value for path, value in NATIVE_BLOBS.items()},
        "pass189_successor": successor,
    }


def validate_pass188_historical_lineage() -> Dict[str, Any]:
    evidence = pass188_membrane_source_evidence()
    return {
        "ok": True,
        "classification": PASS188_CENSUS_CLASSIFICATION,
        "license_contract_commit": evidence["license_contract_commit"],
        "bott_runtime_commit": evidence["bott_runtime_commit"],
        "license_completion_head": evidence["license_completion_head"],
        "historical_bott_preserved": True,
        "license_gap_closed_by_i138": True,
    }


def validate_pass188_license_completion_boundary() -> Dict[str, Any]:
    pass188_membrane_source_evidence()
    return {
        "ok": True,
        "classification": "HHS_PASS_188_VERSIONED_CONTENT_LICENSE_AND_LEGACY_STATE_VERIFIED",
        "acceptance_scenarios": 16,
        "immutable_content_versions": True,
        "immutable_license_versions": True,
        "exact_license_delta": True,
        "project_bindings": True,
        "ownership_transfer": True,
        "bounded_delegation": True,
        "prospective_revocation": True,
        "expiry": True,
        "typed_obligations": True,
        "exact_royalties": True,
        "pass187_graph_impact": True,
        "cold_restart_recovery": True,
        "focused_run": FOCUSED_LICENSE_RUN,
        "focused_job": FOCUSED_LICENSE_JOB,
    }


def validate_pass188_license_authority_boundary() -> Dict[str, Any]:
    pass188_membrane_source_evidence()
    return {
        "ok": True,
        "explicit_inherited_vm81_hash72_witness_required": True,
        "serialized_begin_immediate": True,
        "hash72_event_evidence": True,
        "hash216_event_identity": True,
        "deterministic_replay": True,
        "materialized_state_integrity": True,
        "external_chain_required": False,
        "wallet_authority": False,
        "browser_local_authority": False,
        "marketplace_authority": False,
        "independent_vm81_authority": False,
        "independent_hash72_clock": False,
    }


def validate_pass188_license_legacy_evidence_boundary() -> Dict[str, Any]:
    pass188_membrane_source_evidence()
    return {
        "ok": True,
        "legacy_policies": [
            "LEGACY_BOUND",
            "CURRENT_TERMS",
            "OPT_IN_UPGRADE",
            "COMPATIBILITY_FLOOR",
            "REVOCABLE_CAPABILITY",
            "FORKED_LICENSE",
            "SUNSET",
        ],
        "prior_receipts_immutable": True,
        "explicit_upgrade_required": True,
        "stale_ownership_root_rejected": True,
        "tampered_materialization_detected": True,
        "altered_receipt_chain_detected": True,
        "forged_binding_detected": True,
        "offline_external_anchor_supported": True,
    }


def validate_pass188_bott_runtime_boundary() -> Dict[str, Any]:
    pass188_membrane_source_evidence()
    return {
        "ok": True,
        "classification": "HHS_PASS_188_BOTT_RUNTIME_FULL_SURFACE_IMPLEMENTATION_VERIFIED",
        "projected_addresses": 1259712,
        "deterministic_replay_addresses": 1259712,
        "native_c_abi": True,
        "x86_64_branchless_entrypoint": True,
        "python_cli_http_websocket_visual_surfaces": True,
        "hash72_hash216_receipts": True,
        "projected_transition_is_candidate_only": True,
        "canonical_mutation_authority": False,
    }


def validate_pass188_exact_arithmetic_boundary() -> Dict[str, Any]:
    pass188_membrane_source_evidence()
    return {
        "ok": True,
        "license_exact_integer_rational_authority": True,
        "license_float_canonical_authority": False,
        "bott_integer_only_authority": True,
        "bott_float_canonical_authority": False,
        "aggregate_float_canonical_authority": False,
    }


def validate_pass188_successor_binding() -> Dict[str, Any]:
    successor = pass188_membrane_source_evidence()["pass189_successor"]
    return {
        "ok": True,
        "successor_pass": successor["pass_number"],
        "successor_frozen_commit": successor["frozen_commit"],
        "successor_membrane_blob": successor["membrane_blob"],
        "successor_preserved": successor["successor_preserved"],
    }


def validate_pass188_no_new_authority() -> Dict[str, Any]:
    pass188_membrane_source_evidence()
    return {
        "ok": True,
        "i138_new_candidate_authority": False,
        "i138_new_canonical_mutation_authority": False,
        "i138_new_persistence_authority": False,
        "i138_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "float_canonical_authority": False,
        "bott_canonical_mutation_authority": False,
        "license_independent_vm81_authority": False,
        "license_independent_hash72_clock": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass188_surface_declaration() -> Dict[str, Any]:
    pass188_membrane_source_evidence()
    return {
        "surface_id": PASS188_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i138_pass188",
        "symbol": "validate_pass188_historical_lineage",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS-P188-VNFTCLL-LOSP-VM81-H72-H216",
            "HHS-P188-BOTT-RUNTIME-H216-VM81-Q144-G243-X64",
        ],
        "witness_schemas": [
            "HHSExactPass188CumulativeAuthorityWitnessV1",
            "HHSExactPass219InheritedPass188BindingV1",
        ],
        "validators": [
            PASS188_BIND_SYMBOL,
            "validate_pass188_historical_lineage",
        ],
        "guards": [
            "pass188_license_contract_identity",
            "pass188_license_completion_identity",
            "pass188_immutable_version_lineage",
            "pass188_vm81_witness_requirement",
            "pass188_license_hash72_hash216_replay",
            "pass188_legacy_transfer_revocation",
            "pass188_pass187_impact",
            "pass188_historical_bott_identity",
            "pass188_bott_candidate_only",
            "pass188_exact_no_float",
            "pass188_frozen_pass189_successor",
            "pass188_no_new_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS188_LICENSE_CONTRACT_DRIFT",
            "REJECT_PASS188_LICENSE_IMPLEMENTATION_DRIFT",
            "REJECT_PASS188_LICENSE_AUTHORITY_BYPASS",
            "REJECT_PASS188_LICENSE_HISTORY_MUTATION",
            "REJECT_PASS188_BOTT_RUNTIME_DRIFT",
            "REJECT_PASS188_BOTT_MUTATION_ESCALATION",
            "REJECT_PASS188_FLOAT_AUTHORITY",
            "REJECT_PASS188_FROZEN_SUCCESSOR_DRIFT",
            "REJECT_PASS188_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "INHERITED_VM81_WITNESS_REQUIRED_FOR_LICENSE_MUTATION_BOTT_CANDIDATE_ONLY",
        "persistence_policy": "PASS188_LICENSE_SQLITE_EVIDENCE_SUBORDINATE_TO_INHERITED_VM81_RECEIPT",
        "boundedness_policy": "IMMUTABLE_VERSION_LINEAGE_AND_EXHAUSTIVE_FINITE_BOTT_1259712",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass188_membrane_manifest() -> Dict[str, Any]:
    evidence = pass188_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS188_NUMBER,
        "classification": PASS188_CLASSIFICATION,
        "census_classification": PASS188_CENSUS_CLASSIFICATION,
        "license_completion_head": evidence["license_completion_head"],
        "frozen_predecessor": evidence["frozen_i137"],
        "surface": pass188_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass188_membrane_preflight() -> Dict[str, Any]:
    declaration = pass188_surface_declaration()
    rows = [
        execute_surface_preflight(declaration, operation=operation)
        for operation in REQUIRED_OPERATIONS
    ]
    return {
        "schema": "HHS_PASS219_I138_PASS188_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS188_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass188_historical_lineage": validate_pass188_historical_lineage,
    "validate_pass188_license_completion_boundary": validate_pass188_license_completion_boundary,
    "validate_pass188_license_authority_boundary": validate_pass188_license_authority_boundary,
    "validate_pass188_license_legacy_evidence_boundary": validate_pass188_license_legacy_evidence_boundary,
    "validate_pass188_bott_runtime_boundary": validate_pass188_bott_runtime_boundary,
    "validate_pass188_exact_arithmetic_boundary": validate_pass188_exact_arithmetic_boundary,
    "validate_pass188_successor_binding": validate_pass188_successor_binding,
    "validate_pass188_no_new_authority": validate_pass188_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 188 I138 membrane operation: {operation}")
    return OPERATIONS[operation]()
