"""Pass 205 replay and receipt-bound HNAN candidate trace tests."""
from unittest.mock import patch

import pytest

from hhs_runtime.pass220.hnan_pass205_readonly_lineage_binding_v1 import (
    HNANContinuationBindingRejected, bind_hnan_trace_to_pass205_parent,
)

ROOT = "r" * 216
RECEIPT = "h" * 72


class ReadOnlyContinuation:
    def __init__(self):
        self.calls = []
        self.parent_receipt = RECEIPT
        self.verify_ok = True
        self.replay_ok = True

    def snapshot(self, root, *, include_payloads):
        self.calls.append("snapshot")
        assert include_payloads is False
        return {
            "continuation_root216": root,
            "receipt_hash72": self.parent_receipt,
            "constraint_root216": "c" * 216,
            "schema_root216": "s" * 216,
        }

    def verify(self, root):
        self.calls.append("verify")
        return {"ok": self.verify_ok, "continuation_root216": root}

    def replay(self, root):
        self.calls.append("replay")
        return {
            "ok": self.replay_ok,
            "target_root216": root,
            "ordered_roots216": [ROOT],
            "ordered_receipts_hash72": [RECEIPT],
        }

    def advance(self, **kwargs):
        raise AssertionError("candidate trace must not call VM81 mutation")

    branch = advance


def _native_trace(branches, *, parent_root216, parent_receipt_hash72, native_library):
    return {
        "parent_root216": parent_root216,
        "parent_receipt_hash72": parent_receipt_hash72,
        "trace_sha256": "f" * 64,
        "native_global_signature64": "123456",
        "branches": [{"branch_id": str(branches[0]), "decision": "UNRESOLVED"}],
        "branch_count": 1,
        "has_rejected": False,
        "has_unresolved": True,
        "all_native_rules_verified": False,
        "candidate_only": True,
        "canonical_vm81_admission": False,
        "hash72_minted": False,
        "hash216_minted": False,
    }


def _bind(runtime, **changes):
    opts = {
        "parent_root216": ROOT,
        "expected_parent_receipt_hash72": RECEIPT,
        "native_library": "/mock/native.so",
    }
    opts.update(changes)
    return bind_hnan_trace_to_pass205_parent(runtime, ["tensor A"], **opts)


def test_branch_trace_is_receipt_bound_and_nonmutating():
    runtime = ReadOnlyContinuation()
    with patch(
        "hhs_runtime.pass220.hnan_pass205_readonly_lineage_binding_v1.inspect_all_native_hnan_branches",
        side_effect=_native_trace,
    ):
        result = _bind(runtime)
    assert runtime.calls == ["snapshot", "verify", "replay"]
    assert result["parent_verified"] and result["parent_replay_verified"]
    assert result["branches"][0]["decision"] == "UNRESOLVED"
    assert result["candidate_only"] and not result["cross_tensor_consensus_proved"]
    assert not result["pass205_continuation_created"]
    assert not result["canonical_vm81_admission"]
    assert not result["hash72_minted"] and not result["hash216_minted"]
    assert len(result["binding_sha256"]) == 64


def test_parent_receipt_mismatch_blocks_native_trace():
    runtime = ReadOnlyContinuation()
    runtime.parent_receipt = "z" * 72
    with patch(
        "hhs_runtime.pass220.hnan_pass205_readonly_lineage_binding_v1.inspect_all_native_hnan_branches"
    ) as native:
        with pytest.raises(HNANContinuationBindingRejected, match="RECEIPT_MISMATCH"):
            _bind(runtime)
        native.assert_not_called()
    assert runtime.calls == ["snapshot"]


@pytest.mark.parametrize("gate, expected", [
    ("verify", "VERIFICATION"),
    ("replay", "REPLAY"),
])
def test_verification_and_replay_fail_closed(gate, expected):
    runtime = ReadOnlyContinuation()
    if gate == "verify":
        runtime.verify_ok = False
    else:
        runtime.replay_ok = False
    with patch(
        "hhs_runtime.pass220.hnan_pass205_readonly_lineage_binding_v1.inspect_all_native_hnan_branches"
    ) as native:
        with pytest.raises(HNANContinuationBindingRejected, match=expected):
            _bind(runtime)
        native.assert_not_called()


def test_native_authority_drift_blocks_binding():
    runtime = ReadOnlyContinuation()
    bad = _native_trace(["A"], parent_root216=ROOT, parent_receipt_hash72=RECEIPT, native_library="x")
    bad["canonical_vm81_admission"] = True
    with patch(
        "hhs_runtime.pass220.hnan_pass205_readonly_lineage_binding_v1.inspect_all_native_hnan_branches",
        return_value=bad,
    ):
        with pytest.raises(HNANContinuationBindingRejected, match="AUTHORITY_OR_PARENT_DRIFT"):
            _bind(runtime)


def test_real_pass205_genesis_snapshot_replay_without_mutation(tmp_path):
    """Use existing Pass 205 native bridge and SQLite snapshot verification."""
    from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
        Pass205ContinuationRuntime,
    )
    runtime = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    genesis = runtime.snapshot(runtime.genesis_root216)
    before = runtime.graph(genesis["continuation_root216"])["children_root216"]
    with patch(
        "hhs_runtime.pass220.hnan_pass205_readonly_lineage_binding_v1.inspect_all_native_hnan_branches",
        side_effect=_native_trace,
    ):
        result = bind_hnan_trace_to_pass205_parent(
            runtime, ["tensor A"], native_library="/mock/native.so",
            parent_root216=genesis["continuation_root216"],
            expected_parent_receipt_hash72=genesis["receipt_hash72"],
        )
    after = runtime.graph(genesis["continuation_root216"])["children_root216"]
    assert before == after == []
    assert result["parent_verified"]
    assert result["parent_replay_verified"]
    assert result["parent_replay_generation_count"] == 1
    assert result["parent_root216"] == genesis["continuation_root216"]
    assert result["parent_receipt_hash72"] == genesis["receipt_hash72"]
    assert not result["pass205_continuation_created"]
