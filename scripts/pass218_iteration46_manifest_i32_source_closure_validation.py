from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HELPERS = runpy.run_path(
    str(ROOT / "tests" / "pass218" / "test_pass218_iteration46_manifest_bound_i32_source_closure.py")
)


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hhs-p218-i46-") as temporary:
        root = Path(temporary)
        env = HELPERS["prepare_i46"](root)
        runtime = env["runtime"]
        generation_before = env["i30_store"].active_generation()
        receipt = runtime.close()
        proof = runtime.store.active_proof()
        assert proof is not None
        generation_after = env["i30_store"].active_generation()
        first_invocations = runtime.i32_invocation_count
        close_count_after_first = env["closer"].close_count
        restarted = HELPERS["Pass218I46ManifestBoundI32SourceClosure"](
            lifecycle=env["lifecycle"],
            i45_store=env["i45"].store,
            i44_store=env["i44_store"],
            i43_store=env["i43"].store,
            i42_store=env["i42"].store,
            i34_store=env["i34_store"],
            i30_store=env["i30_store"],
            i32_closer=env["closer"],
            state_root=(
                root
                / "state"
                / "cognition"
                / "manifest-bound-i32-source-closure-i46"
            ),
        )
        replay = restarted.close()
        assert replay == receipt
        assert generation_before == generation_after == env["i30_store"].active_generation()
        evidence = {
            "schema": "HHS-P218-I46-EVIDENCE-V1",
            "iteration": 46,
            "status": receipt["status"],
            "closure_status": receipt["closure_status"],
            "i45_receipt_hash72": receipt["i45_receipt_hash72"],
            "i31_purge_receipt_hash72": receipt["i31_purge_receipt_hash72"],
            "i34_ingress_receipt_hash72": receipt["i34_ingress_receipt_hash72"],
            "curriculum_identity_hash72": receipt["curriculum_identity_hash72"],
            "curriculum_position": receipt["curriculum_position"],
            "source_id": receipt["source_id"],
            "source_sha256": receipt["source_sha256"],
            "source_stage": receipt["source_stage"],
            "previous_closure_hash72": receipt["previous_closure_hash72"],
            "i30_generation_sha256": receipt["i30_generation_sha256"],
            "i32_source_closure_hash72": receipt["i32_source_closure_hash72"],
            "i32_closure_chain_root_hash72": receipt["i32_closure_chain_root_hash72"],
            "manifest_bound_i32_source_closure_hash72": receipt[
                "manifest_bound_i32_source_closure_hash72"
            ],
            "i46_validation_hash72": receipt["i46_validation_hash72"],
            "i46_receipt_hash72": receipt["i46_receipt_hash72"],
            "i46_hash216": receipt["i46_hash216"],
            "fresh_i32_invocation_count": first_invocations,
            "frozen_i32_close_count_after_first": close_count_after_first,
            "restart_additional_i32_invocations": restarted.i32_invocation_count,
            "exactly_one_i32_call_across_fresh_and_restart": (
                env["closer"].close_count == 1
            ),
            "i45_complete_purge_verified": receipt["i45_complete_purge_verified"],
            "manifest_cross_lineage_identity_verified": receipt[
                "manifest_cross_lineage_identity_verified"
            ],
            "i32_source_closure_invoked": receipt["i32_source_closure_invoked"],
            "i32_closure_receipt_committed": receipt["i32_closure_receipt_committed"],
            "i30_semantic_generation_unchanged_across_closure": receipt[
                "i30_semantic_generation_unchanged_across_closure"
            ],
            "nonverbatim_source_transaction_durably_closed": receipt[
                "nonverbatim_source_transaction_durably_closed"
            ],
            "restart_safe_exact_closure_adoption": receipt[
                "restart_safe_exact_closure_adoption"
            ],
            "pass218_i33_curriculum_advance_invoked": receipt[
                "pass218_i33_curriculum_advance_invoked"
            ],
            "curriculum_cursor_advanced": receipt["curriculum_cursor_advanced"],
            "stage_advance_permitted": receipt["stage_advance_permitted"],
            "vm81_authorization_invoked": receipt["vm81_authorization_invoked"],
            "truth_promotion": receipt["truth_promotion"],
            "action_authority_minted": receipt["action_authority_minted"],
            "canonical_learning_commit_invoked": receipt[
                "canonical_learning_commit_invoked"
            ],
            "model_activation_invoked": receipt["model_activation_invoked"],
            "verbatim_corpus_source_retained": receipt[
                "verbatim_corpus_source_retained"
            ],
            "physical_memory_erasure_claimed": receipt[
                "physical_memory_erasure_claimed"
            ],
            "external_source_storage_erasure_claimed": receipt[
                "external_source_storage_erasure_claimed"
            ],
            "authoritative_float_weights_created": receipt[
                "authoritative_float_weights_created"
            ],
            "proof_restart_does_not_require_duplicate_i32_invocation": proof[
                "restart_does_not_require_duplicate_i32_invocation"
            ],
        }
        evidence_sha256 = sha256(canonical(evidence)).hexdigest()
        output = {**evidence, "evidence_sha256": evidence_sha256}
        artifact_root = ROOT / ".i46-evidence"
        artifact_root.mkdir(parents=True, exist_ok=True)
        (artifact_root / "pass218_iteration46_evidence.json").write_bytes(
            canonical(output) + b"\n"
        )
        (artifact_root / "pass218_iteration46_evidence.sha256").write_text(
            evidence_sha256 + "\n", encoding="utf-8"
        )
        print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
