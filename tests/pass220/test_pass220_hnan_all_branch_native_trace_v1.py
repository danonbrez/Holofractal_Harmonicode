"""Tests for candidate-only all-branch native HNAN evaluation."""
import ctypes as C
from unittest.mock import patch

import pytest

from hhs_runtime.pass220.hnan_all_branch_native_trace_v1 import (
    NativeBranchTraceRejected, inspect_all_native_hnan_branches,
)
from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
    Claim, Resolution, GlobalReceipt, MASK, VERSION,
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


def _branch(name, rule, lhs, rhs, relation, **flags):
    return {
        "branch_id": name, "tensor": f"ordered({name},xy,yx)",
        "claim": {
            "rule_id": rule, "lhs_node": lhs, "rhs_node": rhs,
            "relation": relation, **(FLAGS | flags),
        },
    }


class _Global:
    def __call__(self, pointer):
        r = C.cast(pointer, C.POINTER(GlobalReceipt)).contents
        r.version = VERSION
        r.decision = 1
        r.required_rule_mask = MASK
        r.verified_rule_mask = MASK
        r.system_signature64 = 987654321
        return 0


class _Resolve:
    def __init__(self):
        self.calls = []

    def __call__(self, claim_pointer, output_pointer):
        claim = C.cast(claim_pointer, C.POINTER(Claim)).contents
        output = C.cast(output_pointer, C.POINTER(Resolution)).contents
        self.calls.append(claim.rule_id)
        output.rule_id = claim.rule_id
        output.lhs_node = claim.lhs_node
        output.rhs_node = claim.rhs_node
        output.relation = claim.relation
        if claim.rule_id == 77:
            output.decision, output.reason = 3, 2
        elif claim.commutation_requested:
            output.decision, output.reason = 2, 10
        else:
            output.decision, output.reason = 1, 0
            output.exact_rule_match = 1
        return 0


class _Native:
    def __init__(self):
        self.hhs_exact_pass219_hnan_global_system_verify = _Global()
        self.hhs_exact_pass219_hnan_resolve = _Resolve()


def _run(tmp_path, branches, native):
    path = tmp_path / "existing.so"
    path.write_bytes(b"test-injected-function-table")
    with patch(
        "hhs_runtime.pass220.hnan_all_branch_native_trace_v1.C.CDLL",
        return_value=native,
    ):
        return inspect_all_native_hnan_branches(
            branches, native_library=str(path),
            parent_receipt_hash72="a" * 72, parent_root216="b" * 216,
        )


def test_evaluates_every_branch_after_reject_and_unresolved(tmp_path):
    native = _Native()
    branches = [
        _branch("first", 12, 18, 19, 9),
        _branch("second", 12, 18, 19, 9, commutation_requested=1),
        _branch("third", 77, 18, 19, 9),
        _branch("fourth", 13, 20, 21, 9),
    ]
    result = _run(tmp_path, branches, native)
    assert native.hhs_exact_pass219_hnan_resolve.calls == [12, 12, 77, 13]
    assert [x["decision"] for x in result["branches"]] == [
        "VERIFIED", "REJECTED", "UNRESOLVED", "VERIFIED"
    ]
    assert [x["branch_id"] for x in result["branches"]] == [
        "first", "second", "third", "fourth"
    ]
    assert result["has_rejected"] and result["has_unresolved"]
    assert not result["all_native_rules_verified"]
    assert result["candidate_only"]
    assert not result["cross_tensor_consensus_proved"]
    assert not result["canonical_vm81_admission"]
    assert not result["hash72_minted"] and not result["hash216_minted"]
    assert len(result["trace_sha256"]) == 64


def test_source_identity_and_input_order_are_preserved(tmp_path):
    native = _Native()
    branches = [
        _branch("AB", 12, 18, 19, 9),
        _branch("BA", 13, 20, 21, 9),
    ]
    a = _run(tmp_path, branches, native)
    b = _run(tmp_path, list(reversed(branches)), native)
    assert a["branches"][0]["source_text"] == "ordered(AB,xy,yx)"
    assert a["branches"][0]["source_utf8_sha256"] != a["branches"][1]["source_utf8_sha256"]
    assert a["trace_sha256"] != b["trace_sha256"]
    assert a["all_native_rules_verified"]
    assert not a["canonical_vm81_admission"]


def test_duplicate_branch_and_boolean_coercion_rejected(tmp_path):
    native = _Native()
    x = _branch("same", 12, 18, 19, 9)
    with pytest.raises(NativeBranchTraceRejected, match="DUPLICATE"):
        _run(tmp_path, [x, x], native)
    bad = _branch("other", True, 18, 19, 9)
    with pytest.raises(NativeBranchTraceRejected, match="INVALID_UINT32"):
        _run(tmp_path, [bad], native)
    assert not native.hhs_exact_pass219_hnan_resolve.calls


def test_missing_native_library_never_falls_back_to_host_scalar():
    with pytest.raises(NativeBranchTraceRejected, match="LIBRARY_REQUIRED"):
        inspect_all_native_hnan_branches(
            [_branch("a", 12, 18, 19, 9)],
            native_library="/absent/hhs.so",
            parent_receipt_hash72="a" * 72,
            parent_root216="b" * 216,
        )


def test_malformed_later_branch_rejected_before_any_native_call(tmp_path):
    native = _Native()
    valid = _branch("first", 12, 18, 19, 9)
    invalid = _branch("second", 13, 20, 21, 9)
    invalid["claim"].pop("relation")
    with pytest.raises(NativeBranchTraceRejected, match="CLAIM_SHAPE"):
        _run(tmp_path, [valid, invalid], native)
    assert native.hhs_exact_pass219_hnan_resolve.calls == []


def test_guard_flags_are_retained_even_when_native_reason_is_unchanged(tmp_path):
    native = _Native()
    base = _branch("same", 12, 18, 19, 9, commutation_requested=1)
    distinct = _branch(
        "same", 12, 18, 19, 9, commutation_requested=1,
        emptyset_cancellation_requested=1,
    )
    first = _run(tmp_path, [base], native)
    second = _run(tmp_path, [distinct], native)
    assert first["branches"][0]["decision"] == "REJECTED"
    assert second["branches"][0]["decision"] == "REJECTED"
    assert first["branches"][0]["native_reason_code"] == second["branches"][0]["native_reason_code"]
    assert first["branches"][0]["claim_flags"]["emptyset_cancellation_requested"] == 0
    assert second["branches"][0]["claim_flags"]["emptyset_cancellation_requested"] == 1
    assert first["trace_sha256"] != second["trace_sha256"]


def test_real_compiled_native_hnan_all_branches(tmp_path):
    """Compile inherited runtime and invoke real C ABI on all branch verdicts.

    This exercises the same build boundary as the existing recursive HNAN
    native preflight test; no replacement native implementation is introduced.
    """
    import subprocess
    from pathlib import Path

    source = Path("hhs_runtime/c/hhs_runtime_exact_abi.c")
    assert source.is_file()
    c_object = tmp_path / "hhs_exact.o"
    cpp_object = tmp_path / "hhs_pqc.o"
    hash_object = tmp_path / "hhs_hash216.o"
    library = tmp_path / "libhhs_branch_trace.so"
    subprocess.run([
        "cc", "-std=c11", "-O0", "-fPIC", "-Ihhs_runtime/include",
        "-c", str(source), "-o", str(c_object),
    ], check=True, timeout=180)
    subprocess.run([
        "c++", "-std=c++17", "-O0", "-fPIC",
        "-Ihhs_runtime/include",
        "-Inative_projects/hhs_pass188_bott_runtime/include",
        "-Inative_projects/hhs_pass189_hqlh_runtime/include",
        "-c", "hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp",
        "-o", str(cpp_object),
    ], check=True, timeout=180)
    subprocess.run([
        "cc", "-std=c11", "-O0", "-fPIC", "-Ihhs_runtime/include",
        "-c", "hhs_runtime/src/hhs_hash216.c", "-o", str(hash_object),
    ], check=True, timeout=180)
    subprocess.run([
        "c++", "-shared", str(c_object), str(cpp_object), str(hash_object),
        "-o", str(library), "-lm", "-lcrypto",
    ], check=True, timeout=180)
    branches = [
        _branch("good-12", 12, 18, 19, 9),
        _branch("bad-commute", 12, 18, 19, 9, commutation_requested=1),
        _branch("unknown", 77, 18, 19, 9),
        _branch("good-13", 13, 20, 21, 9),
    ]
    result = inspect_all_native_hnan_branches(
        branches, native_library=str(library),
        parent_receipt_hash72="a" * 72,
        parent_root216="b" * 216,
    )
    assert [row["decision"] for row in result["branches"]] == [
        "VERIFIED", "REJECTED", "UNRESOLVED", "VERIFIED"
    ]
    assert result["branches"][1]["native_reason_code"] == 10
    assert result["branches"][2]["native_reason_code"] == 2
    assert result["branches"][1]["claim_flags"]["commutation_requested"] == 1
    assert result["branches"][3]["exact_rule_match"]
    assert result["has_rejected"] and result["has_unresolved"]
    assert not result["canonical_vm81_admission"]
    assert not result["hash72_minted"] and not result["hash216_minted"]
