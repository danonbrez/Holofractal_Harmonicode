#!/usr/bin/env python3
"""Emit deterministic evidence for Pass 218 Iteration 41."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

from hhs_runtime.pass218.atomic_semantic_promotion_i30 import PASS218_I30_TARGET_SCOPE
from hhs_runtime.pass218.manifest_bound_canonical_learning_ingress_i41 import (
    PASS218_I41_COMPLETE_STATUS,
    PASS218_I41_VERSION,
    Pass218I41ManifestBoundCanonicalLearningIngress,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / ".i41-evidence"
EVIDENCE_PATH = EVIDENCE_ROOT / "pass218_iteration41_evidence.json"


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def main() -> int:
    helpers = runpy.run_path(
        str(ROOT / "tests" / "pass218" / "test_pass218_iteration41_manifest_bound_canonical_learning_ingress.py")
    )
    make_i40 = helpers["make_i40"]
    EmptyI30 = helpers["EmptyI30"]
    source = (
        b"Pass 218 Iteration 41 binds the exact durable I40 canonical root to a "
        b"non-authoritative I30-target ingress candidate while requiring the "
        b"independent frozen I27 through I29 semantic validation lineage."
    )
    with TemporaryDirectory(prefix="hhs-p218-i41-") as temporary:
        root = Path(temporary)
        lifecycle, i40 = make_i40(root, source)
        i41_root = root / "state" / "cognition" / "manifest-canonical-learning-ingress-i41"
        first = Pass218I41ManifestBoundCanonicalLearningIngress(
            lifecycle=lifecycle,
            i40_store=i40.store,
            state_root=i41_root,
            i40_status_provider=i40.status,
            i30_status_provider=EmptyI30().status,
        )
        receipt = first.admit()
        candidate = first.store.active_candidate()
        assert candidate is not None
        same_process = first.admit()
        assert same_process == receipt
        restarted = Pass218I41ManifestBoundCanonicalLearningIngress(
            lifecycle=lifecycle,
            i40_store=i40.store,
            state_root=i41_root,
            i40_status_provider=i40.status,
            i30_status_provider=EmptyI30().status,
        )
        restarted_receipt = restarted.admit()
        assert restarted_receipt == receipt
        assert receipt["status"] == PASS218_I41_COMPLETE_STATUS
        assert receipt["target_surface"] == PASS218_I30_TARGET_SCOPE
        assert receipt["i40_canonical_root_hash72"] == i40.store.active_record()["i6_target_root_after_hash72"]
        assert receipt["i30_exact_i27_i29_lineage_required"] is True
        assert receipt["i30_independent_validation_required"] is True
        assert receipt["i30_request_synthesized"] is False
        assert receipt["pass218_i30_canonical_semantic_promotion_invoked"] is False
        assert first.i30_invocation_count == 0
        for path in i41_root.rglob("*"):
            if path.is_file():
                payload = path.read_bytes()
                assert source not in payload
                assert b"source_text" not in payload
        evidence = {
            "schema": "HHS-P218-I41-DETERMINISTIC-EVIDENCE-V1",
            "version": PASS218_I41_VERSION,
            "status": receipt["status"],
            "i40_receipt_hash72": receipt["i40_receipt_hash72"],
            "i40_hash216": receipt["i40_hash216"],
            "i40_canonical_root_hash72": receipt["i40_canonical_root_hash72"],
            "i40_i7_checkpoint_hash72": receipt["i40_i7_checkpoint_hash72"],
            "manifest_bound_commit_persistence_hash72": receipt["manifest_bound_commit_persistence_hash72"],
            "learning_ingress_candidate_hash72": receipt["learning_ingress_candidate_hash72"],
            "target_surface": receipt["target_surface"],
            "i41_validation_hash72": receipt["i41_validation_hash72"],
            "i41_receipt_hash72": receipt["i41_receipt_hash72"],
            "i41_hash216": receipt["i41_hash216"],
            "same_process_replay_equal": same_process == receipt,
            "restart_replay_equal": restarted_receipt == receipt,
            "first_process_admissions": first.admission_count,
            "restart_process_admissions": restarted.admission_count,
            "i30_invocations": first.i30_invocation_count + restarted.i30_invocation_count,
            "i30_exact_i27_i29_lineage_required": True,
            "i30_independent_validation_required": True,
            "i30_request_synthesized": False,
            "pass218_i30_canonical_semantic_promotion_invoked": False,
            "pass218_i31_verbatim_purge_invoked": False,
            "pass218_i32_source_closure_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "curriculum_cursor_advanced": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
            "verbatim_corpus_source_retained": False,
        }
    payload = canonical_bytes(evidence)
    digest = sha256(payload).hexdigest()
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(payload + b"\n")
    print("PASS218_I41_EVIDENCE_SHA256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
