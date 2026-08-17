from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HELPERS = runpy.run_path(
    str(ROOT / "tests" / "pass218" / "test_pass218_iteration45_manifest_bound_i31_verbatim_purge.py")
)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hhs-p218-i45-") as temporary:
        root = Path(temporary)
        runtime, purger, lifecycle, i30_store, _, i44_store, _ = HELPERS["prepare_i45"](root)
        generation_before = i30_store.active_generation()
        receipt = runtime.purge()
        proof = runtime.store.active_proof()
        assert proof is not None
        first_invocations = runtime.i31_invocation_count
        generation_after = i30_store.active_generation()
        restarted = HELPERS["Pass218I45ManifestBoundI31VerbatimPurge"](
            lifecycle=lifecycle,
            i44_store=i44_store,
            i31_purger=purger,
            state_root=root / "state" / "cognition" / "manifest-bound-i31-verbatim-purge-i45",
        )
        replay = restarted.purge()
        assert replay == receipt
        assert generation_before == generation_after == i30_store.active_generation()
        evidence = {
            "schema": "HHS-P218-I45-EVIDENCE-V1",
            "iteration": 45,
            "status": receipt["status"],
            "purge_status": receipt["purge_status"],
            "i44_receipt_hash72": receipt["i44_receipt_hash72"],
            "i30_promotion_receipt_hash72": receipt["i30_promotion_receipt_hash72"],
            "i30_promoted_object_hash72": receipt["i30_promoted_object_hash72"],
            "i30_canonical_root_hash72": receipt["i30_canonical_root_hash72"],
            "i30_generation_sha256": receipt["i30_generation_sha256"],
            "i31_purge_receipt_hash72": receipt["i31_purge_receipt_hash72"],
            "i31_purge_gate_root_hash72": receipt["i31_purge_gate_root_hash72"],
            "i31_purge_mode": receipt["i31_purge_mode"],
            "manifest_bound_i31_verbatim_purge_hash72": receipt["manifest_bound_i31_verbatim_purge_hash72"],
            "i45_validation_hash72": receipt["i45_validation_hash72"],
            "i45_receipt_hash72": receipt["i45_receipt_hash72"],
            "i45_hash216": receipt["i45_hash216"],
            "fresh_i31_invocation_count": first_invocations,
            "restart_additional_i31_invocations": restarted.i31_invocation_count,
            "exactly_one_i31_call_across_fresh_and_restart": purger.purge_count == 1,
            "i31_verbatim_purge_invoked": receipt["i31_verbatim_purge_invoked"],
            "i31_purge_receipt_committed": receipt["i31_purge_receipt_committed"],
            "i30_semantic_generation_unchanged_across_purge": receipt["i30_semantic_generation_unchanged_across_purge"],
            "managed_buffers_absent_after": receipt["managed_buffers_absent_after"],
            "pass218_i32_source_closure_invoked": receipt["pass218_i32_source_closure_invoked"],
            "curriculum_cursor_advanced": receipt["curriculum_cursor_advanced"],
            "truth_promotion": receipt["truth_promotion"],
            "action_authority_minted": receipt["action_authority_minted"],
            "canonical_learning_commit_invoked": receipt["canonical_learning_commit_invoked"],
            "model_activation_invoked": receipt["model_activation_invoked"],
            "verbatim_corpus_source_retained": receipt["verbatim_corpus_source_retained"],
            "physical_memory_erasure_claimed": receipt["physical_memory_erasure_claimed"],
            "external_source_storage_erasure_claimed": receipt["external_source_storage_erasure_claimed"],
            "authoritative_float_weights_created": receipt["authoritative_float_weights_created"],
            "proof_restart_does_not_require_duplicate_i31_invocation": proof["restart_does_not_require_duplicate_i31_invocation"],
        }
        evidence_sha256 = sha256(canonical(evidence)).hexdigest()
        output = {**evidence, "evidence_sha256": evidence_sha256}
        artifact_root = ROOT / ".i45-evidence"
        artifact_root.mkdir(parents=True, exist_ok=True)
        (artifact_root / "pass218_iteration45_evidence.json").write_bytes(canonical(output) + b"\n")
        (artifact_root / "pass218_iteration45_evidence.sha256").write_text(evidence_sha256 + "\n", encoding="utf-8")
        print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
