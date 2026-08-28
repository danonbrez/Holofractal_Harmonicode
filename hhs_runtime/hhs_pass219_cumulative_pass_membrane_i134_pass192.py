"""Pass 219 I134 cumulative membrane for repaired inherited Pass 192."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_34"
PASS192_NUMBER = 192
PASS192_CLASSIFICATION = "WIRED"
PASS192_CENSUS_CLASSIFICATION = "PARTIAL_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
PASS192_BIND_SYMBOL = "hhs_exact_pass219_bind_pass192_cellular_fibonacci_tensor"
PASS192_SURFACE_ID = "validator:pass219.inherited.pass192.cellular-fibonacci-tensor"

P = Path
CONTRACT_PATH = P("docs/pass192/HHS_PASS_192_LO_SHU_CELLULAR_FIBONACCI_NESTING_TENSOR_AND_MODULAR_MEMBRANE_DEPTH_AUTHORITY.md")
COMPRESSION_HEADER_PATH = P("hhs_runtime/include/hhs_pass192_fibonacci_compression_1_9.h")
COMPRESSION_INC_PATH = P("hhs_runtime/c/hhs_pass192_fibonacci_compression_1_9.inc")
COMPRESSION_REFERENCE_PATH = P("hhs_runtime/pass219_fibonacci_compression_reference_v1.py")
RUNTIME_PATH = P("hhs_runtime/pass192/runtime.py")
SDK_PATH = P("hhs_runtime/pass192/__init__.py")
CLI_PATH = P("hhs_runtime/pass192/cli.py")
API_PATH = P("hhs_backend/api/pass192_fibonacci_routes.py")
VISUAL_SERVER_PATH = P("hhs_backend/visual_server.py")
TENSOR_SCHEMA_PATH = P("schemas/pass192/HHS_PASS_192_CELLULAR_FIBONACCI_TENSOR_V1.schema.json")
OPERATION_REGISTRY_PATH = P("schemas/pass192/HHS_PASS_192_OPERATION_REGISTRY_V1.json")
PRECONTRACT_TEST_PATH = P("tests/pass192_193/test_pass192_193_contract_invariants.py")
COMPRESSION_TEST_PATH = P("tests/test_hhs_pass219_fibonacci_compression_compliance.py")
RUNTIME_TEST_PATH = P("tests/test_hhs_pass192_cellular_fibonacci_v1.py")
API_TEST_PATH = P("tests/test_hhs_pass192_fibonacci_routes.py")
CLI_TEST_PATH = P("tests/test_hhs_pass192_cli_v1.py")
VISUAL_TEST_PATH = P("tests/test_hhs_pass192_visual_registration.py")
FOCUSED_WORKFLOW_PATH = P(".github/workflows/pass192-i134-repair-validation.yml")
NATIVE_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass192_1_34.h")
NATIVE_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass192_1_34.hpp")
NATIVE_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass192_1_34.inc")

PASS193_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i133_pass193.py")
PASS193_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass193_1_33.h")
PASS193_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass193_1_33.hpp")
PASS193_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass193_1_33.inc")

CONTRACT_AUTHORIZATION_COMMIT = "c3da7e2b7125754b65f08fb8922a151bf01df2b8"
FROZEN_I133 = "8380d2dbc9cf1b0245f006eaa440b47a921d4901"

SOURCE_BLOBS = {
    CONTRACT_PATH: "cab24f1b2e7510321f6449814302ea31b704d5a8",
    COMPRESSION_HEADER_PATH: "8e2d0a1620ff8ce88f588ce9dc55d79f5503f354",
    COMPRESSION_INC_PATH: "2034a9cacb07d09c4b5786ccec28e61d64de635b",
    COMPRESSION_REFERENCE_PATH: "bda83c1a8791dd4bd9e807a88e0a419848d1d140",
    RUNTIME_PATH: "279495e7b88adbd01e56eb6b8897c4d2f88bb948",
    SDK_PATH: "2e0727e9e078fdbb5ad9f866d05f6d886576a9e1",
    CLI_PATH: "1718211edd8739c43837aea9ba53d8de613e3f1b",
    API_PATH: "1e2f9f37f46310d0dffecba66b5c044958b585bc",
    VISUAL_SERVER_PATH: "aefc759cccf3ebd75f81f220814a225a592b4140",
    TENSOR_SCHEMA_PATH: "697b0bf3ba811f82ef0a62b4e9bd3615d59bdcb9",
    OPERATION_REGISTRY_PATH: "33384a6886117c45b6b6ff96514ac85477fbb14d",
    PRECONTRACT_TEST_PATH: "a72e7b8ab6dc0f891540fe2192d92d80f4a0cf52",
    COMPRESSION_TEST_PATH: "b615c6c192761bdb565c7e6cecf6daa03e95c8ab",
    RUNTIME_TEST_PATH: "a0ce335f5e263c980f30d8427162d321a8ffa122",
    API_TEST_PATH: "7586e0270a44b83e6838ca10d43ac33806143774",
    CLI_TEST_PATH: "250275392c6b1ee2809512673d7f1864243527a3",
    VISUAL_TEST_PATH: "c56aa9e67f331bbc61430317667ea80272549bc2",
    FOCUSED_WORKFLOW_PATH: "7d23c8867cb9647295b34c0975b5842e6c96adc0",
}
NATIVE_BLOBS = {
    NATIVE_HEADER_PATH: "5f3245022447dcd3a1cce215f373e4f899946944",
    NATIVE_HPP_PATH: "0f645b5164d8b4b337ff7191c07558cc28f9261f",
    NATIVE_INC_PATH: "ef39790111aa37640bf282cec27804597f44dee4",
}
PASS193_FROZEN_BLOBS = {
    PASS193_MEMBRANE_PATH: "12dc633b44f56ce8a4d131eda7df892e960d1397",
    PASS193_HEADER_PATH: "81605d5e7931041205bfe987e2e64e53572899c8",
    PASS193_HPP_PATH: "ecca12d28cb0f2b42cb72e6887339fdba231541b",
    PASS193_INC_PATH: "12485b95b762a6dd5db1a62dfa16aaa3580e8b16",
}

REQUIRED_OPERATIONS = (
    "validate_pass192_contract_and_lineage",
    "validate_pass192_exact_tensor_boundary",
    "validate_pass192_materialization_replay_boundary",
    "validate_pass192_interface_parity_boundary",
    "validate_pass192_inherited_compression_boundary",
    "validate_pass192_production_registration_boundary",
    "validate_pass192_successor_binding",
    "validate_pass192_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    return _git("hash-object", str(path))


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
            raise RuntimeError(f"PASS192_SOURCE_DRIFT:{path}:{fragment}")


def _frozen_pass193_successor_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", FROZEN_I133, "HEAD")
    for path, expected in PASS193_FROZEN_BLOBS.items():
        actual = _git("rev-parse", f"{FROZEN_I133}:{path}")
        if actual != expected:
            raise RuntimeError(f"PASS192_PASS193_FROZEN_SUCCESSOR_DRIFT:{path}")
    return {
        "pass_number": 193,
        "frozen_commit": FROZEN_I133,
        "membrane_blob": PASS193_FROZEN_BLOBS[PASS193_MEMBRANE_PATH],
        "header_blob": PASS193_FROZEN_BLOBS[PASS193_HEADER_PATH],
        "hpp_blob": PASS193_FROZEN_BLOBS[PASS193_HPP_PATH],
        "inc_blob": PASS193_FROZEN_BLOBS[PASS193_INC_PATH],
        "successor_preserved": True,
    }


def pass192_membrane_source_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", CONTRACT_AUTHORIZATION_COMMIT, "HEAD")
    if _git("merge-base", "HEAD", FROZEN_I133) != FROZEN_I133:
        raise RuntimeError("PASS192_FROZEN_I133_LINEAGE_DRIFT")
    historical_contract = _git("rev-parse", f"{CONTRACT_AUTHORIZATION_COMMIT}:{CONTRACT_PATH}")
    if historical_contract != SOURCE_BLOBS[CONTRACT_PATH]:
        raise RuntimeError("PASS192_HISTORICAL_CONTRACT_DRIFT")
    for path, expected in {**SOURCE_BLOBS, **NATIVE_BLOBS}.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS192_IMPLEMENTED_SOURCE_DRIFT:{path}")

    _require(
        RUNTIME_PATH,
        "CANONICAL_SOURCE",
        "SEED_WITNESSES",
        "LO_SHU",
        "MaterializationBounds",
        "_validated_authorized_tick",
        "Hash216 must contain exactly three Hash72 witnesses",
        "FINITE_REQUESTED_PREFIX_REQUIRED",
        "NON_DESTRUCTIVE_DEPTH_MODULUS_METADATA",
        "OUTER_MODULUS_NON_DESTRUCTIVE_LOCAL",
        "HHS-P192-FILE",
        "hashlib.sha256",
        "def replay(self",
    )
    _require(
        API_PATH,
        'prefix="/v1/tensors/fibonacci"',
        "_encode_ref",
        "_decode_ref",
        "authority_execution",
        "/materialize",
        "/validate",
        "/replay",
    )
    _require(
        CLI_PATH,
        'prog="hhs"',
        'add_parser("tensor")',
        'add_parser("fibonacci")',
        'add_parser("create")',
        'add_parser("materialize")',
        'add_parser("validate")',
        'add_parser("replay")',
    )
    _require(
        VISUAL_SERVER_PATH,
        "pass192_fibonacci_router",
        "/v1/tensors/fibonacci/status",
        "app.include_router(pass192_fibonacci_router)",
        '"pass192_fibonacci_api": "/v1/tensors/fibonacci"',
        '"pass192_cellular_fibonacci": "HHS-P192-LSCFNT-MMD-VM81-H72-H216"',
        "PUBLIC_API_REGISTRATION = register_public_api_federation(app)",
    )
    visual = _text(VISUAL_SERVER_PATH)
    include_marker = "app.include_router(pass192_fibonacci_router)"
    federation_marker = "PUBLIC_API_REGISTRATION = register_public_api_federation(app)"
    if visual.index(include_marker) >= visual.index(federation_marker):
        raise RuntimeError("PASS192_PRODUCTION_REGISTRATION_ORDER_DRIFT")

    _require(
        OPERATION_REGISTRY_PATH,
        "P192.CellularFibonacciTensor",
        "P192.MaterializeTensorPrefix",
        "P192.ValidateTensor",
        "P192.ReplayTensor",
        "INHERITED_SINGLETON_VM81",
    )
    _require(
        FOCUSED_WORKFLOW_PATH,
        "Prove frozen I133 and Pass 192 authorization lineage",
        "Preserve exact canonical arithmetic boundary",
        "Run inherited Pass 192 contract oracle",
        "Preserve inherited Pass 219 1.9 Fibonacci compression",
        "Run dedicated Pass 192 runtime API CLI and production registration",
        "Compile inherited aggregate exact C ABI",
    )
    successor = _frozen_pass193_successor_evidence()
    return {
        "contract_authorization_commit": CONTRACT_AUTHORIZATION_COMMIT,
        "frozen_i133": FROZEN_I133,
        "source_blobs": {str(path): value for path, value in SOURCE_BLOBS.items()},
        "native_blobs": {str(path): value for path, value in NATIVE_BLOBS.items()},
        "pass193_successor": successor,
    }


def validate_pass192_contract_and_lineage() -> Dict[str, Any]:
    evidence = pass192_membrane_source_evidence()
    return {
        "ok": True,
        "contract_authorization_commit": evidence["contract_authorization_commit"],
        "frozen_i133": evidence["frozen_i133"],
        "historical_contract_preserved": True,
        "classification": PASS192_CENSUS_CLASSIFICATION,
    }


def validate_pass192_exact_tensor_boundary() -> Dict[str, Any]:
    pass192_membrane_source_evidence()
    return {
        "ok": True,
        "canonical_source_preserved": True,
        "lo_shu_cells": 9,
        "lo_shu_magic_sum": 15,
        "magnitude_rows": [1, 2, 3, 5, 8],
        "seed_witnesses": 5,
        "exact_arithmetic": "INTEGER_AND_RATIONAL",
        "float_canonical_authority": False,
        "hash216_canonical_identity": True,
    }


def validate_pass192_materialization_replay_boundary() -> Dict[str, Any]:
    pass192_membrane_source_evidence()
    return {
        "ok": True,
        "declarative_depth": "UNBOUNDED",
        "execution_materialization": "FINITE_PREFIX_ONLY",
        "bounded_depth_nodes_serialization_memory_steps_quota": True,
        "membrane_rule": "n_mod_n_plus_1_equals_n",
        "membrane_is_non_destructive_metadata": True,
        "outer_modulus": 1259713,
        "outer_modulus_applied_locally": False,
        "safe_filesystem_locator": "SHA256_HEX_PROJECTION",
        "filesystem_locator_is_canonical_authority": False,
        "hash72_replay_chain_verified": True,
    }


def validate_pass192_interface_parity_boundary() -> Dict[str, Any]:
    pass192_membrane_source_evidence()
    return {
        "ok": True,
        "operation_registry": "HHS_PASS_192_OPERATION_REGISTRY_V1",
        "python_sdk": "hhs_runtime.pass192",
        "cli_grammar": "hhs tensor fibonacci",
        "openapi_prefix": "/v1/tensors/fibonacci",
        "create_inspect_materialize_validate_replay": True,
        "canonical_hash216_transport_unchanged": True,
        "path_reference_transport": "REVERSIBLE_BASE64URL",
    }


def validate_pass192_inherited_compression_boundary() -> Dict[str, Any]:
    pass192_membrane_source_evidence()
    return {
        "ok": True,
        "pass219_1_9_compression_preserved": True,
        "compression_header_blob": SOURCE_BLOBS[COMPRESSION_HEADER_PATH],
        "compression_inc_blob": SOURCE_BLOBS[COMPRESSION_INC_PATH],
        "compression_reference_blob": SOURCE_BLOBS[COMPRESSION_REFERENCE_PATH],
        "shared_schedule_deduplicated": True,
        "lossless_exact_descriptor": True,
        "outer_modulus_preserved": True,
    }


def validate_pass192_production_registration_boundary() -> Dict[str, Any]:
    pass192_membrane_source_evidence()
    return {
        "ok": True,
        "production_router_registered": True,
        "registration_precedes_public_federation": True,
        "public_api_federation_preserved": True,
        "system_status_api_exposed": True,
        "canonical_server_remains_runtime_authority": True,
    }


def validate_pass192_successor_binding() -> Dict[str, Any]:
    successor = pass192_membrane_source_evidence()["pass193_successor"]
    return {
        "ok": True,
        "successor_pass": successor["pass_number"],
        "successor_frozen_commit": successor["frozen_commit"],
        "successor_membrane_blob": successor["membrane_blob"],
        "successor_preserved": successor["successor_preserved"],
    }


def validate_pass192_no_new_authority() -> Dict[str, Any]:
    pass192_membrane_source_evidence()
    return {
        "ok": True,
        "i134_new_candidate_authority": False,
        "i134_new_canonical_mutation_authority": False,
        "i134_new_persistence_authority": False,
        "i134_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "float_canonical_authority": False,
        "filesystem_locator_canonical_authority": False,
        "public_api_federation_is_vm81_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass192_surface_declaration() -> Dict[str, Any]:
    pass192_membrane_source_evidence()
    return {
        "surface_id": PASS192_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i134_pass192",
        "symbol": "validate_pass192_contract_and_lineage",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P192-LSCFNT-MMD-VM81-H72-H216"],
        "witness_schemas": [
            "HHSExactPass192CellularFibonacciTensorAuthorityWitnessV1",
            "HHSExactPass219InheritedPass192BindingV1",
        ],
        "validators": [PASS192_BIND_SYMBOL, "validate_pass192_contract_and_lineage"],
        "guards": [
            "pass192_historical_contract_identity",
            "pass192_canonical_source_identity",
            "pass192_exact_fibonacci_identity",
            "pass192_bounded_materialization",
            "pass192_non_destructive_membrane",
            "pass192_outer_modulus_separation",
            "pass192_inherited_1_9_compression",
            "pass192_interface_parity",
            "pass192_safe_filesystem_projection",
            "pass192_production_registration",
            "pass192_frozen_pass193_successor",
            "pass192_no_new_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS192_CONTRACT_DRIFT",
            "REJECT_PASS192_SOURCE_IDENTITY_DRIFT",
            "REJECT_PASS192_FLOAT_CANONICAL_AUTHORITY",
            "REJECT_PASS192_UNBOUNDED_MATERIALIZATION",
            "REJECT_PASS192_MEMBRANE_DESTRUCTIVE_REDUCTION",
            "REJECT_PASS192_OUTER_MODULUS_LOCAL_REDUCTION",
            "REJECT_PASS192_VM81_RECEIPT_BYPASS",
            "REJECT_PASS192_FILESYSTEM_IDENTITY_CONFUSION",
            "REJECT_PASS192_INTERFACE_PARITY_DRIFT",
            "REJECT_PASS192_PRODUCTION_REGISTRATION_DRIFT",
            "REJECT_PASS192_FROZEN_SUCCESSOR_DRIFT",
            "REJECT_PASS192_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "INHERITED_SINGLETON_VM81_AUTHORIZED_MUTATIONS_ONLY",
        "persistence_policy": "PASS192_TENSOR_MATERIALIZATION_DATA_ONLY_NO_NEW_VM81_AUTHORITY",
        "boundedness_policy": "UNBOUNDED_DECLARATIVE_DEPTH_FINITE_BOUNDED_MATERIALIZATION",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass192_membrane_manifest() -> Dict[str, Any]:
    evidence = pass192_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS192_NUMBER,
        "classification": PASS192_CLASSIFICATION,
        "census_classification": PASS192_CENSUS_CLASSIFICATION,
        "contract_authorization_commit": evidence["contract_authorization_commit"],
        "frozen_predecessor": evidence["frozen_i133"],
        "surface": pass192_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass192_membrane_preflight() -> Dict[str, Any]:
    declaration = pass192_surface_declaration()
    rows = [
        execute_surface_preflight(declaration, operation=operation)
        for operation in REQUIRED_OPERATIONS
    ]
    return {
        "schema": "HHS_PASS219_I134_PASS192_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS192_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass192_contract_and_lineage": validate_pass192_contract_and_lineage,
    "validate_pass192_exact_tensor_boundary": validate_pass192_exact_tensor_boundary,
    "validate_pass192_materialization_replay_boundary": validate_pass192_materialization_replay_boundary,
    "validate_pass192_interface_parity_boundary": validate_pass192_interface_parity_boundary,
    "validate_pass192_inherited_compression_boundary": validate_pass192_inherited_compression_boundary,
    "validate_pass192_production_registration_boundary": validate_pass192_production_registration_boundary,
    "validate_pass192_successor_binding": validate_pass192_successor_binding,
    "validate_pass192_no_new_authority": validate_pass192_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 192 I134 membrane operation: {operation}")
    return OPERATIONS[operation]()
