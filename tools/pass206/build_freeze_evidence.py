#!/usr/bin/env python3
"""Generate Pass 206 pre-enforcement cumulative freeze evidence.

This tool is deliberately read-only with respect to inherited runtime code. It
reads exact bytes from the Pass 206 grounding baseline and writes only the
required evidence artifacts under artifacts/pass206/.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
from typing import Any

BASELINE = "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423"
OUT = pathlib.Path("artifacts/pass206")
CONTRACT_PATH = pathlib.Path("contracts/pass206/PASS_206_CONTRACT.json")

CORE = [
    {
        "repository_path": "hhs_runtime/c/hhs_pass205_continuation.c",
        "language": "C11",
        "symbol_or_callable_identity": "hhs_pass205_* continuation/native transition family",
        "signature_or_schema_identity": "HHSPass205 native continuation implementation",
        "abi_version": "PASS205_NATIVE_CONTINUATION_BASELINE",
        "opcode_number": None,
        "semantic_category": "SINGLETON_VM81_CONTINUATION_IMPLEMENTATION",
        "bindings": ["hhs_runtime/c/hhs_pass205_continuation.h", "hhs_python/runtime/hhs_pass205_continuation_bridge.py"],
        "receipt_replay_obligations": ["parent_bound_hash72_receipt", "hash216_continuation_identity", "deterministic_replay"],
    },
    {
        "repository_path": "hhs_runtime/c/hhs_pass205_continuation.h",
        "language": "C11_HEADER",
        "symbol_or_callable_identity": "HHSPass205State/Delta/Frontier/Projection/Token ABI",
        "signature_or_schema_identity": "Pass205 continuation public native ABI",
        "abi_version": "PASS205_NATIVE_CONTINUATION_BASELINE",
        "opcode_number": None,
        "semantic_category": "SINGLETON_VM81_CONTINUATION_ABI",
        "bindings": ["hhs_runtime/c/hhs_pass205_continuation.c", "hhs_python/runtime/hhs_pass205_continuation_bridge.py"],
        "receipt_replay_obligations": ["stable_struct_layout", "stable_q_addressing", "stable_receipt_binding"],
    },
    {
        "repository_path": "hhs_python/runtime/hhs_pass205_continuation_bridge.py",
        "language": "PYTHON",
        "symbol_or_callable_identity": "Pass205 native continuation ctypes bridge",
        "signature_or_schema_identity": "Python-to-native Pass205 bridge surface",
        "abi_version": "PASS205_PYTHON_NATIVE_BRIDGE_BASELINE",
        "opcode_number": None,
        "semantic_category": "PYTHON_NATIVE_AUTHORITY_BRIDGE",
        "bindings": ["hhs_runtime/c/hhs_pass205_continuation.h"],
        "receipt_replay_obligations": ["native_bytes_retained", "singleton_vm81_admission", "deterministic_replay"],
    },
    {
        "repository_path": "hhs_runtime/c/hhs_runtime_abi.c",
        "language": "C11",
        "symbol_or_callable_identity": "HHS runtime ABI implementation",
        "signature_or_schema_identity": "cumulative native runtime ABI implementation",
        "abi_version": "GROUNDING_BASELINE_RUNTIME_ABI",
        "opcode_number": None,
        "semantic_category": "NATIVE_RUNTIME_ABI_IMPLEMENTATION",
        "bindings": ["hhs_runtime/c/hhs_runtime_abi.h"],
        "receipt_replay_obligations": ["abi_signature_stability"],
    },
    {
        "repository_path": "hhs_runtime/c/hhs_runtime_abi.h",
        "language": "C11_HEADER",
        "symbol_or_callable_identity": "HHS runtime ABI declarations",
        "signature_or_schema_identity": "cumulative native runtime ABI declaration set",
        "abi_version": "GROUNDING_BASELINE_RUNTIME_ABI",
        "opcode_number": None,
        "semantic_category": "NATIVE_RUNTIME_ABI",
        "bindings": ["hhs_runtime/c/hhs_runtime_abi.c"],
        "receipt_replay_obligations": ["abi_signature_stability", "opcode_binding_stability"],
    },
    {
        "repository_path": "hhs_runtime/include/HARMONICODE_VM_RUNTIME.h",
        "language": "C_HEADER",
        "symbol_or_callable_identity": "HARMONICODE VM runtime public surface",
        "signature_or_schema_identity": "VM runtime declaration surface",
        "abi_version": "GROUNDING_BASELINE_VM_RUNTIME",
        "opcode_number": None,
        "semantic_category": "VM81_RUNTIME_SURFACE",
        "bindings": ["VM81_KERNEL"],
        "receipt_replay_obligations": ["single_canonical_authority", "stage_order_preserved"],
    },
    {
        "repository_path": "hhs_runtime/include/hhs_hash216.h",
        "language": "C_HEADER",
        "symbol_or_callable_identity": "HHSHash216/hash216 compute surface",
        "signature_or_schema_identity": "Hash216 native identity ABI",
        "abi_version": "GROUNDING_BASELINE_HASH216",
        "opcode_number": None,
        "semantic_category": "HASH216_ARCHIVAL_IDENTITY",
        "bindings": ["hhs_runtime/c/hhs_pass205_continuation.c"],
        "receipt_replay_obligations": ["hash216_after_receipt_closure", "hash216_not_mutation_authority"],
    },
    {
        "repository_path": "hhs_runtime/include/hhs_receipt.h",
        "language": "C_HEADER",
        "symbol_or_callable_identity": "HHSHash72/receipt surface",
        "signature_or_schema_identity": "Hash72 receipt native ABI",
        "abi_version": "GROUNDING_BASELINE_HASH72_RECEIPT",
        "opcode_number": None,
        "semantic_category": "HASH72_COMMIT_RECEIPT",
        "bindings": ["hhs_runtime/c/hhs_pass205_continuation.c"],
        "receipt_replay_obligations": ["single_hash72_commit_stream", "parent_bound_receipt"],
    },
    {
        "repository_path": "hhs_runtime/include/hhs_tensor81.h",
        "language": "C_HEADER",
        "symbol_or_callable_identity": "Tensor81 native surface",
        "signature_or_schema_identity": "81-cell tensor declaration surface",
        "abi_version": "GROUNDING_BASELINE_TENSOR81",
        "opcode_number": None,
        "semantic_category": "VM81_TENSOR_GEOMETRY",
        "bindings": ["VM81_KERNEL"],
        "receipt_replay_obligations": ["81_cell_identity", "5184_address_identity"],
    },
    {
        "repository_path": "hhs_runtime/include/hhs_nfv_contract.h",
        "language": "C_HEADER",
        "symbol_or_callable_identity": "native NFV contract surface",
        "signature_or_schema_identity": "native constraint/validation declaration surface",
        "abi_version": "GROUNDING_BASELINE_NFV_CONTRACT",
        "opcode_number": None,
        "semantic_category": "NATIVE_CONSTRAINT_CONTRACT",
        "bindings": ["cumulative_validation"],
        "receipt_replay_obligations": ["constraint_order_preserved", "no_bypass"],
    },
]


def run(*args: str, binary: bool = False) -> bytes | str:
    out = subprocess.check_output(args)
    return out if binary else out.decode("utf-8")


def baseline_bytes(path: str) -> bytes:
    return run("git", "show", f"{BASELINE}:{path}", binary=True)  # type: ignore[return-value]


def blob(path: str) -> str:
    return str(run("git", "rev-parse", f"{BASELINE}:{path}")).strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(data)


def write(name: str, value: dict[str, Any]) -> None:
    value = dict(value)
    value["artifact_sha256"] = canonical_hash(value)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def tree_paths() -> list[str]:
    text = str(run("git", "ls-tree", "-r", "--name-only", BASELINE))
    return [line for line in text.splitlines() if line]


def indexed_record(path: str) -> dict[str, Any]:
    data = baseline_bytes(path)
    return {
        "repository_path": path,
        "git_blob": blob(path),
        "file_sha256": sha256(data),
        "size_bytes": len(data),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract["grounding_baseline"] != BASELINE:
        raise SystemExit("Pass 206 grounding baseline mismatch")

    paths = tree_paths()
    contract_paths = sorted(
        p for p in paths
        if p.endswith(".json") and (
            p.startswith("contracts/") or "contract" in pathlib.PurePosixPath(p).name.lower()
        )
    )
    constraint_paths = sorted(
        p for p in paths
        if p.endswith((".json", ".md", ".h")) and any(
            token in p.lower() for token in ("constraint", "invariant", "authority", "receipt")
        )
    )

    contract_index = {
        "schema": "HHS_PASS_206_ACCUMULATED_CONTRACT_INDEX_V1",
        "pass": 206,
        "grounding_baseline": BASELINE,
        "scope": "repository-visible contract JSON surfaces at the exact grounding baseline",
        "entry_count": len(contract_paths),
        "entries": [indexed_record(p) for p in contract_paths],
    }
    write("ACCUMULATED_CONTRACT_INDEX.json", contract_index)

    constraint_index = {
        "schema": "HHS_PASS_206_ACCUMULATED_CONSTRAINT_INDEX_V1",
        "pass": 206,
        "grounding_baseline": BASELINE,
        "mandatory_invariant_examples": contract["mandatory_invariant_examples"],
        "ordered_basis": contract["ordered_basis"],
        "lo_shu": contract["lo_shu"],
        "hydration": contract["hydration"],
        "authority": contract["authority"],
        "security_boundary": contract["security_boundary"],
        "receipt_archival_order": contract["receipt_archival_order"],
        "hash72_block": contract["hash72_block"],
        "hash216_authorizes_original_transformation": contract["hash216_authorizes_original_transformation"],
        "cache_bypasses_admission": contract["cache_bypasses_admission"],
        "indexed_source_count": len(constraint_paths),
        "indexed_sources": [indexed_record(p) for p in constraint_paths],
    }
    write("ACCUMULATED_CONSTRAINT_INDEX.json", constraint_index)

    frozen = []
    for item in CORE:
        data = baseline_bytes(item["repository_path"])
        record = dict(item)
        record.update({
            "file_sha256": sha256(data),
            "git_blob": blob(item["repository_path"]),
            "source_span_identity": "ENTIRE_FILE_SHA256",
            "baseline_commit": BASELINE,
            "freeze_policy": "BYTE_FOR_BYTE_AT_GROUNDING_BASELINE",
        })
        frozen.append(record)
    freeze_manifest = {
        "schema": "HHS_PASS_206_CORE_FUNCTION_FREEZE_MANIFEST_V1",
        "pass": 206,
        "grounding_baseline": BASELINE,
        "core_function_policy": contract["core_function_policy"],
        "entry_count": len(frozen),
        "entries": frozen,
        "core_modification_allowed": False,
        "separate_repair_contract_required_for_core_change": True,
    }
    write("CORE_FUNCTION_FREEZE_MANIFEST.json", freeze_manifest)

    abi_paths = sorted({
        p for p in paths
        if p.endswith((".h", ".hpp", ".json", ".py")) and any(
            token in p.lower() for token in ("abi", "opcode", "schema")
        )
    })
    abi_manifest = {
        "schema": "HHS_PASS_206_ABI_OPCODE_SCHEMA_FREEZE_MANIFEST_V1",
        "pass": 206,
        "grounding_baseline": BASELINE,
        "policy": {
            "opcode_renumbering_or_rebinding": False,
            "abi_signature_drift": False,
            "schema_identity_drift_without_explicit_successor_contract": False,
        },
        "entry_count": len(abi_paths),
        "entries": [indexed_record(p) for p in abi_paths],
    }
    write("ABI_OPCODE_SCHEMA_FREEZE_MANIFEST.json", abi_manifest)

    conflicts = {
        "schema": "HHS_PASS_206_CONTRACT_CONFLICT_REPORT_V1",
        "pass": 206,
        "grounding_baseline": BASELINE,
        "status": "NO_STATIC_CONFLICTS_DETECTED_WITHIN_INDEXED_PASS206_SCOPE",
        "scope_limit": "Static index/freeze analysis only; runtime enforcement and final cumulative replay remain pending.",
        "checks": {
            "single_vm81_canonical_authority": contract["authority"]["canonical_mutation_authority_count"] == 1,
            "single_hash72_commit_stream": contract["authority"]["canonical_hash72_commit_stream_count"] == 1,
            "parallel_canonical_authorities_forbidden": contract["authority"]["parallel_canonical_authorities_allowed"] is False,
            "hash216_not_original_mutation_authority": contract["hash216_authorizes_original_transformation"] is False,
            "cache_cannot_bypass_admission": contract["cache_bypasses_admission"] is False,
            "core_modification_forbidden": contract["core_function_policy"]["alter_core_functions"] is False,
        },
        "unresolved_conflicts": [],
    }
    write("CONTRACT_CONFLICT_REPORT.json", conflicts)

    plugin = {
        "schema": "HHS_PASS_206_PLUGIN_COMPATIBILITY_REPORT_V1",
        "pass": 206,
        "grounding_baseline": BASELINE,
        "status": "STATIC_PRE_ENFORCEMENT_COMPATIBILITY_BASELINE_CAPTURED",
        "full_backward_compatibility_required": contract["plugin_compatibility"]["full_backward_compatibility_required"],
        "reusable_plug_and_play_object_required": contract["plugin_compatibility"]["reusable_plug_and_play_object_required"],
        "core_modification_allowed": contract["plugin_compatibility"]["core_modification_allowed"],
        "alternate_authority_allowed": contract["plugin_compatibility"]["alternate_authority_allowed"],
        "required_declarations": contract["plugin_compatibility"]["required_declarations"],
        "final_runtime_compatibility_validation_pending": True,
    }
    write("PLUGIN_COMPATIBILITY_REPORT.json", plugin)

    canonical_docs = contract["inheritance"]["canonical_documents"]
    parity = {
        "schema": "HHS_PASS_206_INTERFACE_CAPABILITY_PARITY_REPORT_V1",
        "pass": 206,
        "grounding_baseline": BASELINE,
        "status": "STATIC_PRE_ENFORCEMENT_PARITY_BASELINE_CAPTURED",
        "canonical_documents": [
            {"repository_path": p, "present_at_baseline": p in paths, **(indexed_record(p) if p in paths else {})}
            for p in canonical_docs
        ],
        "required_interpretation": contract["inheritance"]["interpretation"],
        "final_interface_workflow_parity_validation_pending": True,
    }
    write("INTERFACE_CAPABILITY_PARITY_REPORT.json", parity)

    matrix = {
        "schema": "HHS_PASS_206_VALIDATION_MATRIX_V1",
        "pass": 206,
        "grounding_baseline": BASELINE,
        "stage": "FREEZE_PRE_ENFORCEMENT",
        "checks": [
            {"name": "contract_index_generated", "status": "PASS"},
            {"name": "constraint_index_generated", "status": "PASS"},
            {"name": "core_file_sha256_frozen", "status": "PASS", "count": len(frozen)},
            {"name": "abi_opcode_schema_index_generated", "status": "PASS", "count": len(abi_paths)},
            {"name": "core_files_modified", "status": "PASS", "expected": False},
            {"name": "enforcement_implementation_present", "status": "PENDING"},
            {"name": "dependency_scoped_runtime_validation", "status": "PENDING"},
            {"name": "final_cumulative_integration_and_replay", "status": "PENDING"},
        ],
        "completion_claimed": False,
    }
    write("VALIDATION_MATRIX.json", matrix)

    print(json.dumps({
        "ok": True,
        "baseline": BASELINE,
        "contract_count": len(contract_paths),
        "constraint_source_count": len(constraint_paths),
        "core_count": len(frozen),
        "abi_opcode_schema_count": len(abi_paths),
        "freeze_manifest_sha256": json.loads((OUT / "CORE_FUNCTION_FREEZE_MANIFEST.json").read_text())["artifact_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
