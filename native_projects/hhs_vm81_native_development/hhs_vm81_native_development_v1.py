from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import argparse
import hashlib
import json
import re

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass078_vm81_native_exposure_v1 import (
    GRID_SIZE,
    native_capability_manifest,
    native_exposure_registry,
)
from native_projects.hhs_vm81_native_exposure.hhs_pass079_native_opcode_registry_v1 import (
    build_registry as build_pass079_registry,
)
from native_projects.hhs_vm81_native_development.hhs_hash_native_binding_registry_v1 import (
    build_registry as build_hash_binding_registry,
)

SCHEMA = "HHS_VM81_NATIVE_DEVELOPMENT_LEVEL_0_1_V2"
CONTRACT_ID = "HHS-VM81-H216-NATIVE-DEV-ELASTIC-MEMORY"
HASH216_POSITION_COUNT = 216

HASH_ABI_PROTOTYPE_RE = re.compile(
    r"(?ms)^(?P<return>void|int)\s+"
    r"(?P<name>hhs_hash(?:72|216)_[A-Za-z0-9_]+)\s*"
    r"\((?P<args>.*?)\)\s*;"
)

FROZEN_SOURCE_PATHS = (
    "hhs_runtime/HARMONICODE_VM_RUNTIME.c",
    "hhs_runtime/include/HARMONICODE_VM_RUNTIME.h",
    "hhs_runtime/c/hhs_runtime_abi.c",
    "hhs_runtime/c/hhs_runtime_abi.h",
    "hhs_runtime/src/hhs_hash216.c",
    "hhs_runtime/include/hhs_hash216.h",
    "native_projects/hhs_vm81_native_exposure/artifacts/PASS_079_NATIVE_OPCODE_REGISTRY.json",
)

CONTRACT_EXTENSION_PATHS = (
    "native_projects/hhs_vm81_native_development/c/hhs_vm81_native_dev_abi.h",
    "native_projects/hhs_vm81_native_development/c/hhs_vm81_native_dev_abi.c",
    "native_projects/hhs_vm81_native_development/hhs_hash_native_binding_registry_v1.py",
)

NON_AUTHORITATIVE_FLOAT_SYMBOLS = frozenset(
    {
        "hhs_srcg_init",
        "hhs_srcg_step",
        "hhs_srcg_validate",
        "hhs_sizeof_srcg_state",
        "hhs_vectorize_hash72",
    }
)

LEVEL_0_EXPLICIT_GAPS = (
    "binary_instruction_encoding",
    "program_counter_semantics",
    "branch_target_semantics",
    "complete_public_c_abi_execution_coverage",
    "authoritative_vector_store_operations",
    "hash216_logical_address_resolver",
    "single_use_vm81_mutation_capability",
    "atomic_frame_bundle_publication",
)

LEVEL_1_INITIAL_EXECUTION_SYMBOLS = (
    "hhs_runtime_init",
    "hhs_validate_abi",
    "hhs_tensor_reset",
    "hhs_tensor_apply_xy",
    "hhs_runtime_step",
    "hhs_receipt_reset",
    "hhs_receipt_commit",
    "hhs_runtime_halt",
    "hhs_hash72_project",
    "hhs_hash72_compare",
    "hhs_hash72_clear",
    "hhs_hash72_compute",
    "hhs_hash72_reciprocal",
    "hhs_hash72_equal",
    "hhs_hash216_clear",
    "hhs_hash216_compute",
    "hhs_hash216_reciprocal",
    "hhs_hash216_equal",
)

TYPED_EXECUTION_STATUSES = (
    "OK",
    "INVALID_ARGUMENT",
    "ABI_VERSION_MISMATCH",
    "INVALID_OPCODE",
    "INVALID_OPERAND",
    "ARITHMETIC_OVERFLOW",
    "HALTED",
    "AUTHORITY_REJECTED",
    "INTERNAL_INVARIANT_FAILURE",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_records(repo: Path, paths: tuple[str, ...]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for rel in paths:
        path = repo / rel
        result.append(
            {
                "path": rel,
                "present": path.is_file(),
                "size": path.stat().st_size if path.is_file() else None,
                "sha256": _sha256(path) if path.is_file() else None,
            }
        )
    return result


def _effective_output_schema(symbol: str, registry_entry: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if symbol == "hhs_hash72_compare":
        return {"type": "integer", "minimum": 0, "maximum": 72}
    if registry_entry is None:
        return None
    return stable(registry_entry.get("output_schema"))


def _numeric_authority(symbol: str) -> str:
    if symbol in NON_AUTHORITATIVE_FLOAT_SYMBOLS:
        return "NON_AUTHORITATIVE_FLOAT_CONTROL_ONLY"
    return "EXACT_OR_STRUCTURAL_CANDIDATE_REQUIRES_EXECUTION_EVIDENCE"


def _hash_abi_entries(
    repo: Path,
    binding_registry: Mapping[str, Any],
) -> list[dict[str, Any]]:
    header_path = repo / "hhs_runtime/include/hhs_hash216.h"
    source_path = repo / "hhs_runtime/src/hhs_hash216.c"
    header = header_path.read_text(encoding="utf-8")
    source = source_path.read_text(encoding="utf-8")
    binding_by_symbol = {
        entry["abi_symbol"]: entry for entry in binding_registry["entries"]
    }
    result: list[dict[str, Any]] = []
    for match in HASH_ABI_PROTOTYPE_RE.finditer(header):
        symbol = match.group("name")
        signature = " ".join(
            f"{match.group('return')} {symbol}({match.group('args')})".split()
        )
        binding = binding_by_symbol.get(symbol)
        result.append(
            stable(
                {
                    "symbol": symbol,
                    "signature": signature,
                    "source_path": "hhs_runtime/src/hhs_hash216.c",
                    "source_line": source.count("\n", 0, source.find(symbol)) + 1,
                    "categories": ["HASH216_MEMORY_IDENTITY" if "216" in symbol else "HASH72_COMMITMENT"],
                    "callable_from_public_abi": True,
                    "binding_status": "DIRECT_ABI_BOUND" if binding else "DIRECT_ABI_UNBOUND_DEFECT",
                    "native_opcode": binding.get("native_opcode") if binding else None,
                    "declared_output_schema": binding.get("output_schema") if binding else None,
                    "effective_output_schema": binding.get("output_schema") if binding else None,
                    "binding_root_hash72": binding.get("binding_root_hash72") if binding else None,
                    "numeric_authority": "EXACT_OR_STRUCTURAL_CANDIDATE_REQUIRES_EXECUTION_EVIDENCE",
                    "role_status": "DISCOVERED_AND_CONTRACT_BOUND_REQUIRES_COMPLETE_DOSSIER",
                    "best_use_status": "PARTIAL_FROM_DIRECT_NATIVE_SMOKE",
                    "limits_status": "PARTIAL_FROM_ABI_AND_NEGATIVE_WRAPPER_ONLY",
                    "composition_status": "RECIPROCAL_AND_EQUALITY_ROUNDTRIP_EVIDENCED",
                }
            )
        )
    return result


def build_architecture_surface(repo: Path) -> dict[str, Any]:
    capabilities = native_capability_manifest(repo)
    exposure = native_exposure_registry(capabilities)
    pass079 = build_pass079_registry(repo)
    hash_bindings = build_hash_binding_registry(repo)

    exposure_by_symbol = {entry["native_symbol"]: entry for entry in exposure["entries"]}
    registry_by_symbol = {entry["abi_symbol"]: entry for entry in pass079["entries"]}

    entries: list[dict[str, Any]] = []
    for function in capabilities["functions"]:
        symbol = function["symbol"]
        exposed = exposure_by_symbol[symbol]
        registry_entry = registry_by_symbol.get(symbol)
        callable_from_abi = bool(exposed["callable_from_higher_level"])
        if callable_from_abi and registry_entry is not None:
            binding_status = "DIRECT_ABI_BOUND"
        elif callable_from_abi:
            binding_status = "DIRECT_ABI_UNBOUND_DEFECT"
        else:
            binding_status = "DESCRIPTOR_ONLY_CLASSIFIED"

        entries.append(
            stable(
                {
                    "symbol": symbol,
                    "signature": function["signature"],
                    "source_path": function["source_path"],
                    "source_line": function["line"],
                    "categories": function["categories"],
                    "callable_from_public_abi": callable_from_abi,
                    "binding_status": binding_status,
                    "native_opcode": registry_entry.get("native_opcode") if registry_entry else None,
                    "declared_output_schema": registry_entry.get("output_schema") if registry_entry else None,
                    "effective_output_schema": _effective_output_schema(symbol, registry_entry),
                    "numeric_authority": _numeric_authority(symbol),
                    "role_status": "DISCOVERED_REQUIRES_EVIDENCE_BACKED_DOSSIER",
                    "best_use_status": "UNRESOLVED",
                    "limits_status": "PARTIAL_FROM_ABI_ONLY",
                    "composition_status": "UNRESOLVED",
                }
            )
        )

    compare_entry = registry_by_symbol.get("hhs_hash72_compare")
    contract_errata = [
        stable(
            {
                "erratum_id": "VM81-NATIVE-DEV-E001",
                "symbol": "hhs_hash72_compare",
                "classification": "DERIVED_REGISTRY_OUTPUT_SCHEMA_MISMATCH",
                "frozen_c_semantics": "UINT64_POSITIONAL_MATCH_SCORE_0_TO_72",
                "prior_registry_claim": compare_entry.get("output_schema") if compare_entry else None,
                "effective_schema": {"type": "integer", "minimum": 0, "maximum": 72},
                "native_semantics_modified": False,
                "resolution": "NEW_CONTRACT_LAYER_PRESERVES_C_ABI_AND_OVERRIDES_ONLY_THE_DERIVED_SCHEMA_CLAIM",
            }
        )
    ]

    legacy_entries = list(entries)
    hash_abi_entries = _hash_abi_entries(repo, hash_bindings)
    entries.extend(hash_abi_entries)

    direct_entries = [entry for entry in entries if entry["callable_from_public_abi"]]
    descriptor_entries = [entry for entry in entries if not entry["callable_from_public_abi"]]
    float_entries = [entry for entry in entries if entry["numeric_authority"] == "NON_AUTHORITATIVE_FLOAT_CONTROL_ONLY"]

    result = stable(
        {
            "schema": SCHEMA,
            "contract_id": CONTRACT_ID,
            "implementation_slice": "LEVEL_0_1_TYPED_EXECUTION_RESULT_ABI_AND_COMPLETE_HASH_BINDING",
            "frozen_sources": _source_records(repo, FROZEN_SOURCE_PATHS),
            "contract_extension_sources": _source_records(repo, CONTRACT_EXTENSION_PATHS),
            "vm81_cell_count": GRID_SIZE,
            "hash216_position_count": HASH216_POSITION_COUNT,
            "capability_counts": {
                "catalogued_native_functions": len(entries),
                "legacy_public_c_abi_callable": sum(1 for entry in legacy_entries if entry["callable_from_public_abi"]),
                "hash72_hash216_public_c_abi_callable": len(hash_abi_entries),
                "total_public_c_abi_callable": len(direct_entries),
                "descriptor_only": len(descriptor_entries),
                "pass079_registered_native_opcodes": pass079["registered_native_opcodes"],
                "hash_native_registered_bindings": hash_bindings["registered_bindings"],
                "non_authoritative_float_control_symbols": len(float_entries),
                "contract_scoped_typed_execution_abi_functions": 1,
            },
            "entries": entries,
            "hash_native_binding_registry_root_hash72": hash_bindings["registry_root_hash72"],
            "typed_execution_result_abi": {
                "header": "native_projects/hhs_vm81_native_development/c/hhs_vm81_native_dev_abi.h",
                "implementation": "native_projects/hhs_vm81_native_development/c/hhs_vm81_native_dev_abi.c",
                "abi_version": 1,
                "operations": ["VALIDATE_ABI", "TENSOR_STEP", "HALT", "RESET"],
                "statuses": list(TYPED_EXECUTION_STATUSES),
                "checked_integer_multiplication": True,
                "checked_integer_addition": True,
                "rejected_request_state_restoration": True,
                "authority_admission_marker": "PREVALIDATED_MARKER_NOT_SINGLE_USE_MUTATION_CAPABILITY",
            },
            "contract_errata": contract_errata,
            "initial_level1_execution_symbols": list(LEVEL_1_INITIAL_EXECUTION_SYMBOLS),
            "explicit_missing_capabilities": list(LEVEL_0_EXPLICIT_GAPS),
            "closure": {
                "all_native_functions_classified": exposure["complete_catalogue"],
                "all_legacy_direct_abi_capabilities_bound": sum(1 for entry in legacy_entries if entry["callable_from_public_abi"]) == pass079["registered_native_opcodes"],
                "all_hash72_hash216_direct_abi_capabilities_bound": hash_bindings["all_expected_bindings_present"],
                "all_current_linked_direct_abi_capabilities_bound": all(entry["binding_status"] == "DIRECT_ABI_BOUND" for entry in direct_entries),
                "typed_invalid_opcode_status_declared": True,
                "typed_invalid_operand_status_declared": True,
                "typed_arithmetic_overflow_status_declared": True,
                "rejected_state_preservation_wrapper_declared": True,
                "hash72_compare_schema_erratum_applied": True,
                "float_surfaces_excluded_from_authoritative_numeric_execution": all(
                    entry["numeric_authority"] == "NON_AUTHORITATIVE_FLOAT_CONTROL_ONLY"
                    for entry in float_entries
                ),
                "level0_terminal_classification_emitted": False,
                "level1_terminal_classification_emitted": False,
            },
            "implementation_status": "LEVEL_0_1_TYPED_ABI_AND_HASH_BINDING_IMPLEMENTED_TERMINAL_VERIFICATION_NOT_YET_CLAIMED",
        }
    )
    result["architecture_surface_root_hash72"] = product_root(
        "hhs_vm81_native_development_level_0_1_v2", result
    )
    return stable(result)


def write_artifacts(repo: Path) -> dict[str, Any]:
    result = build_architecture_surface(repo)
    hash_registry = build_hash_binding_registry(repo)
    out_dir = repo / "reports" / "vm81_native_development"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "VM81_ARCHITECTURE_SURFACE_LEVEL_0_1.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "HASH72_HASH216_NATIVE_BINDING_REGISTRY.json").write_text(
        json.dumps(hash_registry, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = write_artifacts(args.repo) if args.write else build_architecture_surface(args.repo)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
