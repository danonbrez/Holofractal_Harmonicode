from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HELPERS = runpy.run_path(
    str(
        ROOT
        / "tests"
        / "pass218"
        / "test_pass218_iteration47_manifest_bound_i33_curriculum_advance.py"
    )
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
    with tempfile.TemporaryDirectory(prefix="hhs-p218-i47-") as temporary:
        root = Path(temporary)
        env = HELPERS["prepare_i47"](root)
        runtime = env["i47"]
        generation_before = env["i30_store"].active_generation()
        receipt = runtime.advance()
        proof = runtime.store.active_proof()
        assert proof is not None
        generation_after = env["i30_store"].active_generation()
        first_invocations = runtime.i33_invocation_count
        advance_count_after_first = env["i33"].advance_count
        restarted = HELPERS["Pass218I47ManifestBoundI33CurriculumAdvance"](
            lifecycle=env["lifecycle"],
            i46_store=env["i46"].store,
            i30_store=env["i30_store"],
            i33_advancer=env["i33"],
            state_root=(
                root
                / "state"
                / "cognition"
                / "manifest-bound-i33-curriculum-advance-i47"
            ),
        )
        replay = restarted.advance()
        assert replay == receipt
        assert generation_before == generation_after == env["i30_store"].active_generation()
        evidence = {
            "schema": "HHS-P218-I47-EVIDENCE-V1",
            "iteration": 47,
            "status": receipt["status"],
            "curriculum_status": receipt["curriculum_status"],
            "i46_receipt_hash72": receipt["i46_receipt_hash72"],
            "i32_source_closure_hash72": receipt["i32_source_closure_hash72"],
            "i32_closure_chain_root_hash72": receipt["i32_closure_chain_root_hash72"],
            "curriculum_identity_hash72": receipt["curriculum_identity_hash72"],
            "curriculum_position": receipt["curriculum_position"],
            "source_id": receipt["source_id"],
            "source_sha256": receipt["source_sha256"],
            "source_stage": receipt["source_stage"],
            "previous_closure_hash72": receipt["previous_closure_hash72"],
            "i30_generation_sha256": receipt["i30_generation_sha256"],
            "i33_advance_receipt_hash72": receipt["i33_advance_receipt_hash72"],
            "i33_transition_hash72": receipt["i33_transition_hash72"],
            "i33_cursor_state_sha256": receipt["i33_cursor_state_sha256"],
            "i33_advance_hash216": receipt["i33_advance_hash216"],
            "next_expected_ordinal": receipt["next_expected_ordinal"],
            "next_expected_source_id": receipt["next_expected_source_id"],
            "next_expected_stage": receipt["next_expected_stage"],
            "stage_transition_required": receipt["stage_transition_required"],
            "manifest_bound_i33_curriculum_advance_hash72": receipt[
                "manifest_bound_i33_curriculum_advance_hash72"
            ],
            "i47_validation_hash72": receipt["i47_validation_hash72"],
            "i47_receipt_hash72": receipt["i47_receipt_hash72"],
            "i47_hash216": receipt["i47_hash216"],
            "fresh_i33_invocation_count": first_invocations,
            "frozen_i33_advance_count_after_first": advance_count_after_first,
            "restart_additional_i33_invocations": restarted.i33_invocation_count,
            "exactly_one_i33_call_across_fresh_and_restart": (
                env["i33"].advance_count == 1
            ),
            "i46_complete_source_closure_verified": receipt[
                "i46_complete_source_closure_verified"
            ],
            "i32_exact_closure_verified": receipt["i32_exact_closure_verified"],
            "i33_curriculum_advance_invoked": receipt["i33_curriculum_advance_invoked"],
            "i33_advance_receipt_committed": receipt["i33_advance_receipt_committed"],
            "curriculum_cursor_advanced": receipt["curriculum_cursor_advanced"],
            "i30_semantic_generation_unchanged_across_advance": receipt[
                "i30_semantic_generation_unchanged_across_advance"
            ],
            "restart_safe_exact_advance_adoption": receipt[
                "restart_safe_exact_advance_adoption"
            ],
            "next_source_ingress_invoked": receipt["next_source_ingress_invoked"],
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
            "proof_restart_does_not_require_duplicate_i33_invocation": proof[
                "restart_does_not_require_duplicate_i33_invocation"
            ],
        }
        evidence_sha256 = sha256(canonical(evidence)).hexdigest()
        output = {**evidence, "evidence_sha256": evidence_sha256}
        artifact_root = ROOT / ".i47-evidence"
        artifact_root.mkdir(parents=True, exist_ok=True)
        (artifact_root / "pass218_iteration47_evidence.json").write_bytes(
            canonical(output) + b"\n"
        )
        (artifact_root / "pass218_iteration47_evidence.sha256").write_text(
            evidence_sha256 + "\n", encoding="utf-8"
        )
        print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
