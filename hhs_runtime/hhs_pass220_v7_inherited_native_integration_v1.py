"""Pass220 V7: *reuse* existing Pass159/Pass169/Lane5/VM81 invariants.

This is transport/orchestration, not a second tensor evaluator or new theorem.
It runs the original native Pass159 source-to-VMIR probe, native HNAN-bound
Pass169 quotient-intent preflight, the existing public Pass169 source registry,
the existing native Lane5 host-ingress bridge and the inherited V7 5184 position
mapping. It never upgrades a source hash into a VM81/Hash72/Hash216 proof.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Any

from hhs_runtime.hhs_pass220_v7_ordered_matrix_geometry_v1 import (
    SOURCE, V7SourceError, parse_quotient, verify_bijection,
)
from hhs_runtime.hhs_tensor_constraint_admissibility_v1 import (
    classify_tensor_state,
)

EXACT_SOURCE = (SOURCE + "\n").encode("ascii")
SCHEMA = "HHS_PASS220_V7_INHERITED_NATIVE_INTEGRATION_V1"
PASS169_632_BYTE_CANONICAL_SOURCE_SCOPE = 632


class V7NativeIntegrationError(RuntimeError):
    pass


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise V7NativeIntegrationError(code)


def _fields(stdout: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        _require(bool(key) and key not in result, "DUPLICATED_OR_EMPTY_NATIVE_FIELD")
        result[key] = value
    return result


def _hash216(candidate: str | None, name: str) -> str:
    _require(isinstance(candidate, str) and len(candidate) == 216,
             "MISSING_NATIVE_HASH216_" + name)
    # Native HARMONICODE Hash216 is a 216-GLYPH string, not SHA-hex.
    # Preserve its ordered glyphs byte-for-byte; avoid a scalar/hex shim.
    _require(all(33 <= ord(c) <= 126 for c in candidate),
             "INVALID_NATIVE_HASH216_" + name)
    return candidate


def validate_frontend_output(stdout: str, exit_code: int, source: bytes) -> dict[str, Any]:
    """Require actual native Pass159 lexer/AST/type/HIR/VMIR and VALIDATE_ONLY."""
    _require(source == EXACT_SOURCE, "V7_EXACT_SOURCE_MISMATCH")
    _require(exit_code == 0, "NATIVE_PASS159_FRONTEND_FAILED")
    result = _fields(stdout)
    _require(result.get("source_bytes") == str(len(source)),
             "NATIVE_PASS159_SOURCE_BYTE_MISMATCH")
    source_root = _hash216(result.get("source_hash216"), "SOURCE")
    graph_root = _hash216(result.get("graph_hash216"), "GRAPH")
    vmir_root = _hash216(result.get("vmir_hash216"), "VMIR")
    _require(result.get("vm81_source_specific_commit_verified") == "false" and
             result.get("hash72_source_specific_execution_receipt_verified") == "false",
             "NATIVE_PASS159_UNAUTHORIZED_COMMIT_CLAIM")
    _require(result.get("source_ingress_authority") ==
             "PASS159_FRONTEND_AND_NATIVE_VALIDATE_ONLY",
             "NATIVE_PASS159_AUTHORITY_SPOOFING")
    status = result.get("native_validate_only_status")
    _require(status is not None and re.fullmatch(r"-?[0-9]+", status) is not None,
             "NATIVE_PASS159_VALIDATE_STATUS_MISSING")
    candidate_receipt = result.get("native_validate_only_receipt_hash216")
    if status == "0":
        candidate_receipt = _hash216(candidate_receipt, "VALIDATE_ONLY_RECEIPT")
    else:
        _require(candidate_receipt is None,
                 "NONVALIDATED_FRONTEND_HAS_UNAUTHORIZED_RECEIPT")
    return {
        "pass159_frontend_chain": "VERIFIED",
        "native_source_hash216": source_root,
        "native_constraint_graph_hash216": graph_root,
        "native_vmir_hash216": vmir_root,
        "native_validate_only_status": int(status),
        "native_validate_only_receipt_hash216": candidate_receipt,
        "native_validate_only_completed": status == "0",
        "canonical_vm81_commit_from_frontend": False,
        "canonical_hash72_receipt_from_frontend": False,
    }


def validate_native_pure_output(stdout: str, exit_code: int, source: bytes) -> dict[str, Any]:
    """Preserve results of existing Pass159 EVALUATE_PURE, never mint authority."""
    _require(exit_code == 0 and source == EXACT_SOURCE,
             "PURE_EXECUTION_EXIT_OR_SOURCE_MISMATCH")
    result = _fields(stdout)
    required = {
        "v7_exact_source": "VERIFIED",
        "source_sha256": sha256(source).hexdigest(),
        "source_bytes": str(len(source)),
        "native_runtime": "PASS159_INHERITED",
        "native_execution_mode": "EVALUATE_PURE",
        "native_commit_policy": "0",
        "native_matrix_quotient_result_certified": "0",
        "source_specific_signed_vm81_commit": "0",
        "source_specific_hash72_hash216_canonical_receipt": "0",
    }
    for name, expected in required.items():
        _require(result.get(name) == expected,
                 "PURE_EXECUTION_AUTHORITY_SCOPE_" + name)
    try:
        status = int(result["pure_native_status"])
        replay = int(result["pure_replay_status"])
    except (KeyError, ValueError) as exc:
        raise V7NativeIntegrationError("PURE_EXECUTION_STATUS_MISSING") from exc
    candidate = result.get("pure_candidate_hash216")
    replay_root = result.get("pure_replay_hash216")
    if status == 0 and candidate is not None:
        _hash216(candidate, "PURE_EXECUTION")
        if replay == 0:
            _hash216(replay_root, "PURE_REPLAY")
        else:
            _require(replay_root is None, "PURE_REPLAY_UNAUTHORIZED_GLYPH")
    else:
        _require(candidate is None and replay_root is None,
                 "PURE_STATUS_INCONSISTENT_RECEIPT")
        _require(replay != 0, "PURE_REPLAY_SUCCESS_WITHOUT_CANDIDATE")
    return {
        "source_sha256": required["source_sha256"],
        "pure_status": status,
        "replay_status": replay,
        "native_pure_candidate_hash216": candidate,
        "native_pure_replay_hash216": replay_root,
        "pure_execution_complete": status == 0 and candidate is not None,
        "pure_replay_complete": replay == 0 and replay_root is not None,
        "canonical_mutation": False,
    }


def validate_hnan_mode_output(stdout: str, exit_code: int) -> dict[str, Any]:
    """Keep valid tensor candidates alive for inherited native type dispatch."""
    result = _fields(stdout)
    _require(exit_code == 0, "V7_NATIVE_DISPATCH_PRECHECK_FAILED")
    required = {
        "v7_source_exact": "1",
        "v7_mode": "UNDECLARED",
        "hnan_15_rule_mask": "0x7FFF",
        "v7_hnan_order_verified": "1",
        "v7_decision": "INHERIT_NATIVE_DISPATCH",
        "v7_reason": "9",
        "v7_native_type_dispatch_required": "1",
        "native_v7_matrix_inverse_proved": "0",
        "native_v7_global_environment_verified": "0",
        "canonical_vm81_admission": "0",
        "canonical_hash72_hash216_commit": "0",
    }
    for key, expected in required.items():
        _require(result.get(key) == expected, "V7_INHERITED_HNAN_CHECK_" + key)
    return {
        "pass219_hnan_inherited_rule_mask": result["hnan_15_rule_mask"],
        "xy_yx_and_zw_wz_order_inherited": True,
        "pass169_quotient_mode": "NATIVE_TYPE_INFERENCE_REQUIRED",
        "native_quotient_mode_decision": "DELEGATE_NATIVE_TYPED_DISPATCH",
        "native_quotient_semantics_not_reproven": True,
        "canonical_vm81_mutation_from_mode_gate": False,
    }


def _native_call(argv: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(argv, capture_output=True, text=True,
                              timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise V7NativeIntegrationError("NATIVE_RUNTIME_UNAVAILABLE") from exc


def integrate(
    source_path: str | Path,
    frontend_binary: str | Path,
    mode_gate_binary: str | Path,
    pure_binary: str | Path | None = None,
) -> dict[str, Any]:
    """Execute inherited real services, preserving V7 source-specific scope."""
    file_path = Path(source_path)
    raw = file_path.read_bytes()
    _require(raw == EXACT_SOURCE, "V7_EXACT_SOURCE_MISMATCH")
    geometry = parse_quotient(raw)
    address = verify_bijection()
    _require(address["bijective_positions"] == 5184 and
             address["address_roundtrip"] == "VERIFIED",
             "V7_VM81_HASH72_ADDRESS_MISMATCH")
    digest = sha256(raw).hexdigest()

    # Existing native Pass159 binary, NOT a Python parser substitute.
    native = _native_call([str(frontend_binary), str(file_path)])
    frontend = validate_frontend_output(native.stdout, native.returncode, raw)

    # Existing native HNAN-linked Pass169 source-specific mode preflight.
    # Deliberately pass zero (UNDECLARED); choosing a mode without an
    # authoritative HHS operator mapping would be a source interpretation.
    gate = _native_call([str(mode_gate_binary), str(file_path), "0"])
    hnan = validate_hnan_mode_output(gate.stdout, gate.returncode)

    # Inherited PASS159 pure expression dispatch, never EXECUTE_AND_COMMIT.
    pure = None
    if pure_binary is not None:
        pure_native = _native_call([str(pure_binary), str(file_path)])
        pure = validate_native_pure_output(pure_native.stdout,
                                           pure_native.returncode, raw)

    # Existing native-backed HHS public ingress/registry; candidate transport
    # does NOT substitute for the 632-byte canonical Pass169 runtime proof.
    from hhs_runtime.pass169.public_service import Pass169AlgebraService
    registry = Pass169AlgebraService(repository_root=Path(__file__).resolve().parents[1])
    registration = registry.register_source(raw.decode("ascii"))
    entry = registration.get("source", {})
    _require(registration.get("ok") is True and
             entry.get("sha256") == digest and
             entry.get("byte_length") == len(raw) and
             entry.get("canonical_authority") is False and
             entry.get("canonical_pass169_corpus") is False,
             "PASS169_REGISTERED_SOURCE_AUTHORITY_MISMATCH")

    # Existing Lane5 native membrane (candidate-only); no direct canonical VM.
    from hhs_backend.lane5_ingress_gateway import Lane5IngressMediator
    ingress = Lane5IngressMediator().mediate(
        raw, provenance="pass220:v7:inherited-native-binding")
    _require(ingress.get("workload_sha256") == digest and
             ingress.get("candidate_only") is True and
             ingress.get("requires_signed_environmental_vm81_admission") is True and
             ingress.get("canonical_vm81_mutation_authority") is False and
             ingress.get("canonical_hash216_authority") is False,
             "LANE5_INHERITED_MEMBRANE_AUTHORITY_MISMATCH")

    # Inherit *actual available* native validations. An unresolved source-
    # specific branch remains PENDING (not contradictory or invalid). The
    # native Pass159/VM81 dispatcher is responsible for resolving it.
    candidate_state = classify_tensor_state(
        required_constraints=(
            "source_identity", "pass159_type_environment", "ordered_hnan",
            "vm81_position_map", "global_denominator",
            "source_specific_quotient_type", "branch_closure",
        ),
        constraint_results={
            "source_identity": True,
            "pass159_type_environment": True,
            "ordered_hnan": hnan["xy_yx_and_zw_wz_order_inherited"],
            "vm81_position_map": address["address_roundtrip"] == "VERIFIED",
            "global_denominator": True,  # inherited native 15-rule HNAN
            "source_specific_quotient_type": None,  # not yet emitted by VMIR
            "branch_closure": None,  # no native exhaustive branch receipt
        },
        candidate_branches=None,
        branches_exhaustively_resolved=False,
    )

    record = {
        "schema": SCHEMA,
        "source_sha256": digest,
        "source_bytes": len(raw),
        "source_original": raw.decode("ascii").rstrip("\n"),
        "ordered_matrix_cells": [
            {"site": cell["macro_site"],
             "byte_offset": cell["source_byte_offset"],
             "source_expression": cell["raw_source_expression"],
             "source_bound_occurrence_sha256": cell["occurrence_sha256"]}
            for cell in geometry["source_bound_macro_sites"]
        ],
        "vm81_hash72_address_bijection": address,
        "inherited_native_pass159": frontend,
        "native_tensor_state_routing": {
            "classification": candidate_state.classification.value,
            "unresolved_constraints": list(candidate_state.unresolved_constraints),
            "candidate_branch_count": None,
            "inherited_signed_vm81_eligible": (
                candidate_state.eligible_for_inherited_signed_vm81
            ),
            "pending_is_not_contradiction": (
                not candidate_state.contradictory_constraints
            ),
            "canonical_vm81_committed": False,
        },
        "inherited_native_pass159_pure_execution": pure,
        "inherited_native_hnan_and_pass169_intent": hnan,
        "pass169_source_registry": entry,
        "inherited_lane5_candidate": ingress,
        "pass169_canonical_632_byte_corpus_receipt_borrowed": False,
        "native_pure_execution_attempted": pure is not None,
        "source_specific_quotient_operator_binding_present": False,
        "native_source_specific_quotient_result_authorized": False,
        "vm81_signed_environmental_commit_performed": False,
        "canonical_hash72_hash216_ledger_written": False,
        "no_new_mathematical_proof_required_for_inherited_rules": True,
        "status": (
            "INHERITED_NATIVE_FRONTEND_VALIDATE_PASS__QUOTIENT_OPERATOR_BINDING_PENDING"
            if frontend["native_validate_only_completed"]
            else "INHERITED_NATIVE_FRONTEND_ONLY__VALIDATE_ONLY_UNRESOLVED"
        ),
    }
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source",required=True,type=Path)
    parser.add_argument("--frontend",required=True,type=Path)
    parser.add_argument("--mode-gate",required=True,type=Path)
    parser.add_argument("--pure-binary",type=Path,default=None)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    record=integrate(args.source,args.frontend,args.mode_gate,args.pure_binary)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",
                        encoding="utf-8")
    print("V7_INHERITED_PASS159_NATIVE_FRONTEND=VERIFIED")
    print("V7_INHERITED_PASS219_HNAN_15_RULES=VERIFIED")
    print("V7_INHERITED_LANE5_NATIVE_CANDIDATE=VERIFIED")
    print("V7_INHERITED_PASS169_SOURCE_REGISTRY=VERIFIED")
    print("V7_INHERITED_VM81_HASH72_5184_ADDRESSING=VERIFIED")
    print("V7_NATIVE_VALIDATE_ONLY_STATUS="+
          str(record["inherited_native_pass159"]["native_validate_only_status"]))
    pure = record["inherited_native_pass159_pure_execution"]
    print("V7_INHERITED_PASS159_PURE_EXEC_STATUS="+
          (str(pure["pure_status"]) if pure is not None else "NOT_EXECUTED"))
    print("V7_INHERITED_PASS159_PURE_REPLAY_STATUS="+
          (str(pure["replay_status"]) if pure is not None else "NOT_EXECUTED"))
    print("V7_TENSOR_STATE_INVALID=0")
    print("V7_TENSOR_STATE_BRANCH_RESOLUTION=PENDING")
    print("V7_QUOTIENT_OPERATOR_SOURCE_BINDING=PENDING")
    print("V7_CANONICAL_VM81_COMMIT=0")


if __name__=="__main__":
    main()
