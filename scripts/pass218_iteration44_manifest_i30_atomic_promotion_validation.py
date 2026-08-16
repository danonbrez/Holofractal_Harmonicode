from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HELPERS = runpy.run_path(
    str(ROOT / "tests" / "pass218" / "test_pass218_iteration44_manifest_bound_i30_atomic_promotion.py")
)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hhs-p218-i44-") as temporary:
        root = Path(temporary)
        _, lifecycle, request, i43, i43_receipt = HELPERS["prepare_i43"](root)
        promoter = HELPERS["FakeAuthorizedI30Promoter"](i43_receipt)
        runtime = HELPERS["make_i44"](root, lifecycle, i43, promoter)
        receipt = runtime.promote(request)
        proof = runtime.store.active_proof()
        assert proof is not None
        first_invocations = runtime.i30_invocation_count
        restarted = HELPERS["make_i44"](root, lifecycle, i43, promoter)
        replay = restarted.promote(request)
        assert replay == receipt
        assert promoter.promote_calls == 1
        evidence = {
            "schema": "HHS-P218-I44-EVIDENCE-V1",
            "iteration": 44,
            "status": receipt["status"],
            "promotion_status": receipt["promotion_status"],
            "i43_receipt_hash72": receipt["i43_receipt_hash72"],
            "i30_promotion_request_sha256": receipt["i30_promotion_request_sha256"],
            "i30_grant_hash72": receipt["i30_grant_hash72"],
            "i30_promotion_receipt_hash72": receipt["i30_promotion_receipt_hash72"],
            "i30_promoted_object_hash72": receipt["i30_promoted_object_hash72"],
            "i30_target_root_after_hash72": receipt["i30_target_root_after_hash72"],
            "manifest_bound_i30_atomic_promotion_hash72": receipt["manifest_bound_i30_atomic_promotion_hash72"],
            "i44_validation_hash72": receipt["i44_validation_hash72"],
            "i44_receipt_hash72": receipt["i44_receipt_hash72"],
            "i44_hash216": receipt["i44_hash216"],
            "fresh_i30_invocation_count": first_invocations,
            "restart_additional_i30_invocations": restarted.i30_invocation_count,
            "exactly_one_i30_call_across_fresh_and_restart": promoter.promote_calls == 1,
            "i30_atomic_promotion_committed": receipt["i30_atomic_promotion_committed"],
            "vm5184_authoritative_projection_invoked": receipt["vm5184_authoritative_projection_invoked"],
            "vm5184_authoritative_state_committed": receipt["vm5184_authoritative_state_committed"],
            "pass218_i31_verbatim_purge_invoked": receipt["pass218_i31_verbatim_purge_invoked"],
            "pass218_i32_source_closure_invoked": receipt["pass218_i32_source_closure_invoked"],
            "curriculum_cursor_advanced": receipt["curriculum_cursor_advanced"],
            "truth_promotion": receipt["truth_promotion"],
            "action_authority_minted": receipt["action_authority_minted"],
            "canonical_learning_commit_invoked": receipt["canonical_learning_commit_invoked"],
            "model_activation_invoked": receipt["model_activation_invoked"],
            "verbatim_corpus_source_retained": receipt["verbatim_corpus_source_retained"],
            "authoritative_float_weights_created": receipt["authoritative_float_weights_created"],
            "proof_restart_does_not_require_duplicate_i30_invocation": proof["restart_does_not_require_duplicate_i30_invocation"],
        }
        evidence_sha256 = sha256(canonical(evidence)).hexdigest()
        output = {**evidence, "evidence_sha256": evidence_sha256}
        artifact_root = ROOT / ".i44-evidence"
        artifact_root.mkdir(parents=True, exist_ok=True)
        (artifact_root / "pass218_iteration44_evidence.json").write_bytes(canonical(output) + b"\n")
        (artifact_root / "pass218_iteration44_evidence.sha256").write_text(evidence_sha256 + "\n", encoding="utf-8")
        print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
