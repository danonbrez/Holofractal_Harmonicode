"""Repository-native evidence emitter for Pass 218 full implementation Iteration 8."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    GenesisSeedBuilder,
    NarrativeBeatHydrator,
    Pass218RuntimeLifecycle,
    Pass218RuntimeLifecycleError,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    compile_grammar_rules,
)


def _authorization(proof, *, sequence: int, label: str):
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=hash72_digest(
            {"domain": "HHS-P218-I8-REPOSITORY-EVIDENCE-GRANTOR-V1"},
            label.encode("utf-8"),
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return journal, authorization


def main() -> None:
    grammar_path = REPOSITORY_ROOT / "hhs_runtime" / "Grammar Correction.csv"
    narrative_path = (
        REPOSITORY_ROOT
        / "creative_writing"
        / "novels"
        / "THE_SMALLEST_PERMISSION.md"
    )
    relation_db = load_wordnet_relations(
        [REPOSITORY_ROOT / "hhs_runtime" / "WordnetAntonyms.csv"],
        require_all=False,
    )
    seed = GenesisSeedBuilder(REPOSITORY_ROOT, relation_db=relation_db).compile(
        ["ability", "abnormal", "authority", "permission", "scope"],
        use_repository_wordnet=False,
    )
    grammar = compile_grammar_rules(grammar_path)
    source_text = narrative_path.read_text("utf-8")
    source_sha256 = sha256(source_text.encode("utf-8")).hexdigest()
    hydration = NarrativeBeatHydrator(paragraphs_per_beat=8).hydrate(
        source_text,
        source_id="the-smallest-permission",
        source_epistemic_class="FICTIONAL_COUNTERFACTUAL",
        genesis_seed=seed,
        grammar_rule_set=grammar,
        expected_source_sha256=source_sha256,
    )

    transaction = SourceTransaction.begin(hydration, source_text)
    closure = transaction.commit_and_purge()
    snapshot = transaction.snapshot()
    staged = ClosedTransactionVectorVM5184Adapter().stage(snapshot)
    proof = PromotionProofMembrane().prove(
        closed_transaction_snapshot=snapshot,
        staged_candidate=staged,
    )

    with tempfile.TemporaryDirectory(prefix="hhs-p218-i8-evidence-") as temporary:
        store_root = Path(temporary)
        lifecycle = Pass218RuntimeLifecycle(store_root)
        pre_start = lifecycle.status()
        first_boot = lifecycle.startup()

        journal1, authorization1 = _authorization(
            proof,
            sequence=1,
            label="iteration8-first-canonical-admission",
        )
        boundary1 = lifecycle.canonical_boundary()
        prepared1 = boundary1.prepare(
            authorization=authorization1,
            staged_candidate=staged,
            authorization_journal=journal1,
        )
        committed1 = lifecycle.commit_prepared(
            prepared1,
            authorization_journal=journal1,
        )
        generation0_root = lifecycle.target.root_hash72()
        generation0_snapshot = lifecycle.target.snapshot_bytes()
        generation0_receipt = committed1["canonical_receipt"]
        generation0_manifest = lifecycle.store._load_manifest()
        generation0_checkpoint_sha256 = committed1["checkpoint_sha256"]

        # Crash-style restart: instantiate a fresh lifecycle without calling
        # shutdown on the first process. Authority must come only from I7 data.
        crash_restart = Pass218RuntimeLifecycle(store_root)
        crash_restart_status = crash_restart.startup()
        crash_restart_receipt = crash_restart.target.committed_receipt(
            authorization1["authorization_hash72"]
        )

        # A second authorized commit deliberately fails after the I6 atomic
        # mutation but before the I7 manifest swap. The gate must stay closed
        # until the already-committed target is durably checkpointed, with no
        # second canonical commit or authorization needed for the retry.
        journal2, authorization2 = _authorization(
            proof,
            sequence=2,
            label="iteration8-second-canonical-admission",
        )
        boundary2 = crash_restart.canonical_boundary()
        prepared2 = boundary2.prepare(
            authorization=authorization2,
            staged_candidate=staged,
            authorization_journal=journal2,
        )
        durability_failure = ""
        try:
            crash_restart.commit_prepared(
                prepared2,
                authorization_journal=journal2,
                fail_before_manifest_swap=True,
            )
        except Pass218RuntimeLifecycleError as exc:
            durability_failure = str(exc)
        blocked_status = crash_restart.status()
        second_receipt_before_retry = crash_restart.target.committed_receipt(
            authorization2["authorization_hash72"]
        )
        second_root_before_retry = crash_restart.target.root_hash72()
        retry_result = crash_restart.retry_pending_durability()
        second_receipt_after_retry = crash_restart.target.committed_receipt(
            authorization2["authorization_hash72"]
        )
        generation1_manifest = crash_restart.store._load_manifest()
        generation1_root = crash_restart.target.root_hash72()

        # Corrupt only the active generation. I7 recovery must reject it and
        # bind the immediately previous sealed generation (generation 0).
        active_path = (
            crash_restart.store.generations
            / generation1_manifest["active_generation"]
        )
        active_path.write_bytes(b"{corrupt")
        fallback_restart = Pass218RuntimeLifecycle(store_root)
        fallback_status = fallback_restart.startup()

        generation_files = sorted(
            path for path in crash_restart.store.generations.glob("checkpoint-*.json")
            if path.is_file()
        )
        persisted_bytes = b"\n".join(path.read_bytes() for path in generation_files)
        authority_serialized = json.dumps(
            {
                "first_boot": first_boot,
                "commit": committed1,
                "crash_restart": crash_restart_status,
                "blocked": blocked_status,
                "fallback": fallback_status,
            },
            sort_keys=True,
        )

        record = {
            "classification": "HHS_PASS218_ITERATION8_RUNTIME_OS_LIFECYCLE_EVIDENCE",
            "source_sha256": source_sha256,
            "narrative_beat_count": len(hydration.beats),
            "transaction_id_hash72": transaction.transaction_id_hash72,
            "transaction_hash216": closure["transaction_hash216"],
            "candidate_entry_id_sha256": staged["vector_entry"]["entry_id_sha256"],
            "projection_sha256": staged["vm5184_projection_sha256"],
            "pre_start_ingestion_enabled": pre_start["ingestion_enabled"],
            "first_boot_state": first_boot["state"],
            "first_boot_ingestion_enabled": first_boot["ingestion_enabled"],
            "generation0_commit_state": committed1["state"],
            "generation0_checkpoint_state": committed1["checkpoint_state"],
            "generation0_checkpoint_sha256": generation0_checkpoint_sha256,
            "generation0_manifest_sequence": generation0_manifest["generation_sequence"],
            "generation0_root_hash72": generation0_root,
            "crash_restart_state": crash_restart_status["state"],
            "crash_restart_ingestion_enabled": crash_restart_status["ingestion_enabled"],
            "crash_restart_root_exact": crash_restart.target.root_hash72() == generation0_root,
            "crash_restart_snapshot_exact": crash_restart.target.snapshot_bytes() == generation0_snapshot,
            "crash_restart_receipt_exact": crash_restart_receipt == generation0_receipt,
            "crash_restart_new_authorization_minted": crash_restart_status[
                "restart_new_authorization_minted"
            ],
            "crash_restart_new_canonical_mutation_invoked": crash_restart_status[
                "restart_new_canonical_mutation_invoked"
            ],
            "durability_failure": durability_failure,
            "durability_failure_gate_closed": blocked_status["ingestion_enabled"] is False,
            "durability_failure_pending": blocked_status["durability_pending"],
            "durability_failure_commit_count": blocked_status["canonical_commit_count"],
            "durability_retry_state": retry_result["state"],
            "durability_retry_gate_reopened": crash_restart.ingestion_enabled,
            "durability_retry_root_unchanged": crash_restart.target.root_hash72() == second_root_before_retry,
            "durability_retry_receipt_unchanged": second_receipt_before_retry == second_receipt_after_retry,
            "generation1_manifest_sequence": generation1_manifest["generation_sequence"],
            "generation1_previous_checkpoint_sha256": generation1_manifest[
                "previous_checkpoint_sha256"
            ],
            "generation1_root_changed": generation1_root != generation0_root,
            "fallback_state": fallback_status["state"],
            "fallback_restore_state": fallback_status["restore_state"],
            "fallback_ingestion_enabled": fallback_status["ingestion_enabled"],
            "fallback_restores_generation0_root": fallback_restart.target.root_hash72() == generation0_root,
            "fallback_restores_generation0_snapshot": fallback_restart.target.snapshot_bytes() == generation0_snapshot,
            "source_text_present_in_persisted_generations": source_text.encode("utf-8") in persisted_bytes,
            "source_text_present_in_authority_records": source_text in authority_serialized,
            "verbatim_source_retained": fallback_status["verbatim_source_retained"],
            "pass165_source_retaining_path_invoked": fallback_status[
                "pass165_source_retaining_path_invoked"
            ],
            "canonical_learning_commit_invoked": fallback_status[
                "canonical_learning_commit_invoked"
            ],
            "truth_promotion": fallback_status["truth_promotion"],
            "action_authority_minted": fallback_status["action_authority_minted"],
        }

        assert record["pre_start_ingestion_enabled"] is False
        assert record["first_boot_state"] == "EMPTY_READY"
        assert record["first_boot_ingestion_enabled"] is True
        assert record["generation0_commit_state"] == "CANONICAL_COMMITTED_DURABLE_READY"
        assert record["generation0_checkpoint_state"] == "DURABLE_CHECKPOINT_COMMITTED"
        assert record["generation0_manifest_sequence"] == 0
        assert record["crash_restart_state"] == "RESTORED_READY"
        assert record["crash_restart_ingestion_enabled"] is True
        assert record["crash_restart_root_exact"] is True
        assert record["crash_restart_snapshot_exact"] is True
        assert record["crash_restart_receipt_exact"] is True
        assert record["crash_restart_new_authorization_minted"] is False
        assert record["crash_restart_new_canonical_mutation_invoked"] is False
        assert "P218_I8_COMMIT_DURABILITY_CHECKPOINT_FAILED" in record["durability_failure"]
        assert record["durability_failure_gate_closed"] is True
        assert record["durability_failure_pending"] is True
        assert record["durability_failure_commit_count"] == 2
        assert record["durability_retry_state"] == "DURABLE_CHECKPOINT_COMMITTED"
        assert record["durability_retry_gate_reopened"] is True
        assert record["durability_retry_root_unchanged"] is True
        assert record["durability_retry_receipt_unchanged"] is True
        assert record["generation1_manifest_sequence"] == 1
        assert record["generation1_previous_checkpoint_sha256"] == generation0_checkpoint_sha256
        assert record["generation1_root_changed"] is True
        assert record["fallback_state"] == "RECOVERED_PREVIOUS_READY"
        assert record["fallback_restore_state"] == "RECOVERED_PREVIOUS_VALID_GENERATION"
        assert record["fallback_ingestion_enabled"] is True
        assert record["fallback_restores_generation0_root"] is True
        assert record["fallback_restores_generation0_snapshot"] is True
        assert record["source_text_present_in_persisted_generations"] is False
        assert record["source_text_present_in_authority_records"] is False
        assert record["verbatim_source_retained"] is False
        assert record["pass165_source_retaining_path_invoked"] is False
        assert record["canonical_learning_commit_invoked"] is False
        assert record["truth_promotion"] is False
        assert record["action_authority_minted"] is False
        print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
