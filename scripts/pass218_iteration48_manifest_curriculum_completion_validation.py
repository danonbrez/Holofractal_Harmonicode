#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 48 curriculum-completion evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
import tempfile

from hhs_runtime.pass218.manifest_bound_curriculum_completion_seal_i48 import (
    Pass218I48ManifestBoundCurriculumCompletionSeal,
)

ROOT = Path(__file__).resolve().parents[1]
TEST = runpy.run_path(
    str(
        ROOT
        / "tests"
        / "pass218"
        / "test_pass218_iteration48_manifest_bound_curriculum_completion_seal.py"
    )
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def build_evidence() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="hhs-p218-i48-") as temporary:
        env = TEST["prepare_i48"](Path(temporary))
        i33_count_before = int(env["i33"].advance_count)
        i30_before = env["i30_store"].active_generation()
        receipt = env["i48"].seal()
        proof = env["i48"].store.active_proof()
        i30_after = env["i30_store"].active_generation()
        i33_count_after = int(env["i33"].advance_count)
        restarted = Pass218I48ManifestBoundCurriculumCompletionSeal(
            lifecycle=env["lifecycle"],
            i47_store=env["i47"].store,
            i30_store=env["i30_store"],
            i33_advancer=env["i33"],
            state_root=env["i48"].store.root,
        )
        replay = restarted.seal()
        i33_count_after_restart = int(env["i33"].advance_count)
        assert proof is not None
        evidence: dict[str, object] = {
            "schema": "HHS-P218-I48-EVIDENCE-V1",
            "iteration": 48,
            "status": receipt["status"],
            "curriculum_status": receipt["curriculum_status"],
            "i47_receipt_hash72": receipt["i47_receipt_hash72"],
            "i33_advance_receipt_hash72": receipt["i33_advance_receipt_hash72"],
            "i33_transition_hash72": receipt["i33_transition_hash72"],
            "i33_authority_root_hash72": receipt["i33_authority_root_hash72"],
            "i33_manifest_hash72": receipt["i33_manifest_hash72"],
            "curriculum_identity_hash72": receipt["curriculum_identity_hash72"],
            "manifest_source_count": receipt["manifest_source_count"],
            "completed_source_count": receipt["completed_source_count"],
            "next_expected_ordinal": receipt["next_expected_ordinal"],
            "next_expected_source_id": receipt["next_expected_source_id"],
            "next_expected_stage": receipt["next_expected_stage"],
            "stage_transition_required": receipt["stage_transition_required"],
            "final_cursor_sha256": receipt["final_cursor_sha256"],
            "final_closure_hash72": receipt["final_closure_hash72"],
            "i30_generation_sha256": receipt["i30_generation_sha256"],
            "i30_canonical_root_hash72": receipt["i30_canonical_root_hash72"],
            "curriculum_completion_proof_hash72": receipt[
                "curriculum_completion_proof_hash72"
            ],
            "i48_validation_hash72": receipt["i48_validation_hash72"],
            "i48_receipt_hash72": receipt["i48_receipt_hash72"],
            "i48_hash216": receipt["i48_hash216"],
            "i47_manifest_bound_curriculum_advance_verified": receipt[
                "i47_manifest_bound_curriculum_advance_verified"
            ],
            "i33_terminal_completion_receipt_verified": receipt[
                "i33_terminal_completion_receipt_verified"
            ],
            "authoritative_manifest_exhausted": receipt[
                "authoritative_manifest_exhausted"
            ],
            "final_cursor_exhausted": receipt["final_cursor_exhausted"],
            "final_cursor_source_count_matches_manifest": receipt[
                "final_cursor_source_count_matches_manifest"
            ],
            "no_next_expected_source_verified": receipt[
                "no_next_expected_source_verified"
            ],
            "i30_semantic_generation_unchanged_at_completion": i30_before
            == i30_after,
            "i30_canonical_root_unchanged_at_completion": receipt[
                "i30_canonical_root_unchanged_at_completion"
            ],
            "i33_advance_count_before_seal": i33_count_before,
            "i33_advance_count_after_seal": i33_count_after,
            "i33_advance_count_after_restart": i33_count_after_restart,
            "i33_not_invoked_by_i48": i33_count_before
            == i33_count_after
            == i33_count_after_restart,
            "restart_exact_receipt_adoption": replay == receipt,
            "restart_additional_i33_invocations": i33_count_after_restart
            - i33_count_after,
            "restart_adoption_count": restarted.restart_adoption_count,
            "source_payload_persisted": proof["source_payload_persisted"],
            "i33_curriculum_advance_invoked": receipt[
                "i33_curriculum_advance_invoked"
            ],
            "next_source_ingress_invoked": receipt["next_source_ingress_invoked"],
            "stage_advance_invoked": receipt["stage_advance_invoked"],
            "stage_advance_permitted": receipt["stage_advance_permitted"],
            "pass219_handoff_authority_minted": receipt[
                "pass219_handoff_authority_minted"
            ],
            "vm81_authorization_invoked": receipt["vm81_authorization_invoked"],
            "canonical_learning_commit_invoked": receipt[
                "canonical_learning_commit_invoked"
            ],
            "truth_promotion": receipt["truth_promotion"],
            "action_authority_minted": receipt["action_authority_minted"],
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
        }
        evidence_sha256 = sha256(canonical_bytes(evidence)).hexdigest()
        return {**evidence, "evidence_sha256": evidence_sha256}


def main() -> None:
    evidence = build_evidence()
    output = ROOT / ".i48-evidence"
    output.mkdir(parents=True, exist_ok=True)
    encoded = canonical_bytes(evidence) + b"\n"
    (output / "evidence.json").write_bytes(encoded)
    (output / "evidence.sha256").write_text(
        str(evidence["evidence_sha256"]) + "\n", encoding="utf-8"
    )
    print(encoded.decode("utf-8").rstrip())
    print("PASS218_ITERATION48_EVIDENCE_SHA256=" + str(evidence["evidence_sha256"]))


if __name__ == "__main__":
    main()
