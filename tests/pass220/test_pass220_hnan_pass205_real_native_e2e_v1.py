"""Real native HNAN 1.63 + Pass205 lineage end-to-end candidate inspection.

No mocks: compile the inherited exact C/C++ ABI, initialize the existing
Pass205 native continuation runtime, and inspect every conflicting claim.
This deliberately does not invoke Pass205.advance/branch/admission.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    Pass205ContinuationRuntime,
)
from hhs_runtime.pass220.hnan_pass205_readonly_lineage_binding_v1 import (
    HNANContinuationBindingRejected,
    bind_hnan_trace_to_pass205_parent,
)
from hhs_runtime.pass220.hnan_all_branch_native_trace_v1 import (
    NativeBranchTraceRejected,
)

FLAGS = {
    "source_order_preserved": 1,
    "typed_identity_preserved": 1,
    "scalar_substitution_requested": 0,
    "delta_cancellation_requested": 0,
    "floating_infinity_requested": 0,
    "commutation_requested": 0,
    "emptyset_cancellation_requested": 0,
    "equality_reversal_requested": 0,
}


def _compile_native(tmp_path: Path) -> str:
    c_obj, cpp_obj, h_obj = (tmp_path / x for x in
                            ("exact.o", "pqc.o", "hash216.o"))
    library = tmp_path / "libhhs_exact_hnan_e2e.so"
    subprocess.run([
        "cc", "-std=c11", "-O0", "-fPIC", "-Ihhs_runtime/include",
        "-c", "hhs_runtime/c/hhs_runtime_exact_abi.c",
        "-o", str(c_obj),
    ], check=True, timeout=180)
    subprocess.run([
        "c++", "-std=c++17", "-O0", "-fPIC",
        "-Ihhs_runtime/include",
        "-Inative_projects/hhs_pass188_bott_runtime/include",
        "-Inative_projects/hhs_pass189_hqlh_runtime/include",
        "-c", "hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp",
        "-o", str(cpp_obj),
    ], check=True, timeout=180)
    subprocess.run([
        "cc", "-std=c11", "-O0", "-fPIC", "-Ihhs_runtime/include",
        "-c", "hhs_runtime/src/hhs_hash216.c", "-o", str(h_obj),
    ], check=True, timeout=180)
    subprocess.run([
        "c++", "-shared", str(c_obj), str(cpp_obj), str(h_obj),
        "-o", str(library), "-lm", "-lcrypto",
    ], check=True, timeout=180)
    return str(library)


def _branch(branch_id: str, rule: int, lhs: int, rhs: int, relation: int, **guards):
    return {
        "branch_id": branch_id,
        "tensor": f"Tensor({branch_id};xy != yx; AB=P⁴;BA=-P⁴)",
        "claim": {
            "rule_id": rule,
            "lhs_node": lhs,
            "rhs_node": rhs,
            "relation": relation,
            **(FLAGS | guards),
        },
    }


def test_real_native_hnan_full_branch_trace_against_replayed_pass205_parent(tmp_path):
    native_library = _compile_native(tmp_path)
    continuation = Pass205ContinuationRuntime(tmp_path / "continuation.sqlite3")
    parent = continuation.snapshot(continuation.genesis_root216)
    parent_root = parent["continuation_root216"]
    parent_receipt = parent["receipt_hash72"]
    before = continuation.graph(parent_root)["children_root216"]

    branches = [
        _branch("first", 12, 18, 19, 9),
        _branch("contradiction", 12, 18, 19, 9, commutation_requested=1),
        _branch("unresolved", 77, 18, 19, 9),
        _branch("later-valid", 13, 20, 21, 9),
    ]
    bound = bind_hnan_trace_to_pass205_parent(
        continuation, branches, native_library=native_library,
        parent_root216=parent_root,
        expected_parent_receipt_hash72=parent_receipt,
    )
    assert bound["parent_verified"] is True
    assert bound["parent_replay_verified"] is True
    assert bound["parent_replay_generation_count"] == 1
    assert bound["branch_count"] == 4
    assert [row["decision"] for row in bound["branches"]] == [
        "VERIFIED", "REJECTED", "UNRESOLVED", "VERIFIED",
    ]
    assert [row["branch_id"] for row in bound["branches"]] == [
        "first", "contradiction", "unresolved", "later-valid",
    ]
    assert bound["branches"][1]["native_reason_code"] == 10
    assert bound["branches"][2]["native_reason_code"] == 2
    assert bound["branches"][1]["claim_flags"]["commutation_requested"] == 1
    assert bound["has_rejected"] and bound["has_unresolved"]
    assert bound["all_native_rules_verified"] is False
    assert bound["cross_tensor_consensus_proved"] is False
    assert bound["candidate_only"] is True
    assert bound["pass205_continuation_created"] is False
    assert bound["canonical_vm81_admission"] is False
    assert bound["hash72_minted"] is False
    assert bound["hash216_minted"] is False
    assert len(bound["binding_sha256"]) == 64
    assert continuation.graph(parent_root)["children_root216"] == before == []
    assert continuation.verify(parent_root)["ok"]
    assert continuation.replay(parent_root)["ok"]

    # Changing guards with the same first rejection reason is still distinct
    # evidence; no step may flatten these branches or prefer a later module.
    altered = [
        *branches[:1],
        _branch("contradiction", 12, 18, 19, 9,
                commutation_requested=1, emptyset_cancellation_requested=1),
        *branches[2:],
    ]
    second = bind_hnan_trace_to_pass205_parent(
        continuation, altered, native_library=native_library,
        parent_root216=parent_root,
        expected_parent_receipt_hash72=parent_receipt,
    )
    assert second["branches"][1]["native_reason_code"] == 10
    assert second["branch_trace_sha256"] != bound["branch_trace_sha256"]
    assert second["binding_sha256"] != bound["binding_sha256"]
    assert continuation.graph(parent_root)["children_root216"] == []


def test_real_native_library_rejects_unknown_parent_before_branch_execution(tmp_path):
    native_library = _compile_native(tmp_path)
    continuation = Pass205ContinuationRuntime(tmp_path / "continuation.sqlite3")
    parent = continuation.snapshot(continuation.genesis_root216)
    with __import__("pytest").raises(HNANContinuationBindingRejected,
                                      match="PARENT_IDENTITY_OR_RECEIPT_MISMATCH"):
        bind_hnan_trace_to_pass205_parent(
            continuation, [_branch("A", 12, 18, 19, 9)],
            native_library=native_library,
            parent_root216=parent["continuation_root216"],
            expected_parent_receipt_hash72="x" * 72,
        )
    assert continuation.graph(parent["continuation_root216"])["children_root216"] == []
