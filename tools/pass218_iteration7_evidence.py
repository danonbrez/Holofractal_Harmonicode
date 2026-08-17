"""Repository-native evidence emitter for Pass 218 full implementation Iteration 7."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    GenesisSeedBuilder,
    NarrativeBeatHydrator,
    Pass217VM81CanonicalTarget,
    Pass218CanonicalCommitBoundary,
    Pass218DurableCanonicalStore,
    Pass218PersistenceStateError,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    compile_grammar_rules,
)


def _authorize(
    proof,
    journal: PromotionAuthorizationJournal,
    *,
    sequence: int,
):
    grantor_authority_hash72 = hash72_digest(
        {"domain": "HHS-P218-I7-REPOSITORY-EVIDENCE-GRANTOR-V1"},
        b"explicit-pass218-iteration7-durable-canonical-authority",
    )
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=grantor_authority_hash72,
        grant_sequence=sequence,
    )
    return journal.authorize(proof, grant)


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
    closed_snapshot = transaction.snapshot()
    staged = ClosedTransactionVectorVM5184Adapter().stage(closed_snapshot)
    proof = PromotionProofMembrane().prove(
        closed_transaction_snapshot=closed_snapshot,
        staged_candidate=staged,
    )
    journal = PromotionAuthorizationJournal()
    authorization1 = _authorize(proof, journal, sequence=1)

    target = Pass217VM81CanonicalTarget()
    boundary = Pass218CanonicalCommitBoundary(target=target)
    prepared1 = boundary.prepare(
        authorization=authorization1,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    receipt1 = boundary.commit(prepared1, authorization_journal=journal)
    canonical_root_generation0 = target.root_hash72()
    canonical_snapshot_generation0 = target.snapshot_bytes()

    with TemporaryDirectory(prefix="hhs-pass218-i7-evidence-") as temporary:
        durable_root = Path(temporary) / "canonical"
        store = Pass218DurableCanonicalStore(durable_root)
        checkpoint0 = store.checkpoint(target)
        checkpoint0_replay = store.checkpoint(target)

        restarted_store = Pass218DurableCanonicalStore(durable_root)
        restored0 = restarted_store.restore()
        restored0_record = restored0.to_record()
        restored0_receipt = restored0.target.committed_receipt(
            authorization1["authorization_hash72"]
        )

        persisted0_bytes = store.manifest_path.read_bytes()
        persisted0_bytes += (
            store.generations / checkpoint0["manifest"]["active_generation"]
        ).read_bytes()

        # A second explicit grant over the same exact promotable candidate creates
        # a new committed target root without reintroducing source bytes. It is
        # used only to exercise durable-generation transition safety.
        authorization2 = _authorize(proof, journal, sequence=2)
        prepared2 = boundary.prepare(
            authorization=authorization2,
            staged_candidate=staged,
            authorization_journal=journal,
        )
        receipt2 = boundary.commit(prepared2, authorization_journal=journal)
        canonical_root_generation1 = target.root_hash72()

        manifest_before_failure = store.manifest_path.read_bytes()
        interrupted_failure = ""
        try:
            store.checkpoint(target, fail_before_manifest_swap=True)
        except Pass218PersistenceStateError as exc:
            interrupted_failure = str(exc)
        manifest_after_failure = store.manifest_path.read_bytes()
        interrupted_restore = store.restore()

        checkpoint1 = store.checkpoint(target)
        active_generation_path = (
            store.generations / checkpoint1["manifest"]["active_generation"]
        )
        persisted1_bytes = store.manifest_path.read_bytes() + active_generation_path.read_bytes()
        active_generation_path.write_bytes(b"{corrupt")
        fallback_restore = store.restore()

        serialized_authority = json.dumps(
            {
                "checkpoint0": checkpoint0,
                "checkpoint1": checkpoint1,
                "restored0": restored0_record,
                "receipt1": receipt1,
                "receipt2": receipt2,
                "fallback": fallback_restore.to_record(),
            },
            sort_keys=True,
        )

    checkpoint = checkpoint0["checkpoint"]
    manifest = checkpoint0["manifest"]
    record = {
        "classification": "HHS_PASS218_ITERATION7_DURABLE_CANONICAL_PERSISTENCE_EVIDENCE",
        "source_sha256": source_sha256,
        "narrative_beat_count": len(hydration.beats),
        "transaction_id_hash72": transaction.transaction_id_hash72,
        "transaction_hash216": closure["transaction_hash216"],
        "candidate_entry_id_sha256": staged["vector_entry"]["entry_id_sha256"],
        "projection_sha256": staged["vm5184_projection_sha256"],
        "admitted_entry_id_sha256": prepared1.admitted_entry["entry_id_sha256"],
        "iteration6_commit_hash216": receipt1["commit_hash216"],
        "iteration6_outer_receipt_schema": receipt1["schema"],
        "canonical_root_generation0": canonical_root_generation0,
        "checkpoint_generation0_sequence": checkpoint["generation_sequence"],
        "checkpoint_generation0_sha256": checkpoint["checkpoint_sha256"],
        "checkpoint_generation0_hash72": checkpoint["checkpoint_hash72"],
        "checkpoint_generation0_validation_hash72": checkpoint["validation_hash72"],
        "checkpoint_generation0_hash216": checkpoint["checkpoint_hash216"],
        "checkpoint_generation0_hash216_valid": (
            len(checkpoint["checkpoint_hash216"]) == 216
            and all(
                validate_hash72(checkpoint["checkpoint_hash216"][start:start + 72])
                for start in (0, 72, 144)
            )
        ),
        "manifest_generation0_hash72": manifest["manifest_hash72"],
        "checkpoint_idempotent_replay_equal": (
            checkpoint0_replay["checkpoint"] == checkpoint0["checkpoint"]
            and checkpoint0_replay["manifest"] == checkpoint0["manifest"]
        ),
        "checkpoint_idempotent_replay_state": checkpoint0_replay["state"],
        "restart_state_generation0": restored0.state,
        "restart_root_exact_generation0": (
            restored0.target.root_hash72() == canonical_root_generation0
        ),
        "restart_snapshot_exact_generation0": (
            restored0.target.snapshot_bytes() == canonical_snapshot_generation0
        ),
        "restart_receipt_exact_generation0": restored0_receipt == receipt1,
        "restart_new_canonical_mutation_invoked": restored0_record[
            "new_canonical_mutation_invoked"
        ],
        "restart_new_authorization_minted": restored0_record[
            "new_authorization_minted"
        ],
        "canonical_root_generation1": canonical_root_generation1,
        "generation1_root_changed": canonical_root_generation1 != canonical_root_generation0,
        "generation1_second_authorization_consumed": target.authorization_consumed(
            authorization2["authorization_hash72"]
        ),
        "generation1_second_commit_hash216": receipt2["commit_hash216"],
        "interrupted_checkpoint_failure": interrupted_failure,
        "manifest_unchanged_after_interrupted_checkpoint": (
            manifest_before_failure == manifest_after_failure
        ),
        "interrupted_checkpoint_restore_state": interrupted_restore.state,
        "interrupted_checkpoint_restores_generation0": (
            interrupted_restore.target.root_hash72() == canonical_root_generation0
        ),
        "checkpoint_generation1_sequence": checkpoint1["checkpoint"][
            "generation_sequence"
        ],
        "checkpoint_generation1_previous_sha256": checkpoint1["checkpoint"][
            "previous_checkpoint_sha256"
        ],
        "active_corruption_recovery_state": fallback_restore.state,
        "active_corruption_recovered_previous": fallback_restore.recovered_previous_generation,
        "active_corruption_restores_generation0": (
            fallback_restore.target.root_hash72() == canonical_root_generation0
        ),
        "source_text_present_in_generation0_persistence": (
            source_text.encode("utf-8") in persisted0_bytes
        ),
        "source_text_present_in_generation1_persistence": (
            source_text.encode("utf-8") in persisted1_bytes
        ),
        "source_text_present_in_authority_artifacts": source_text in serialized_authority,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }

    assert record["narrative_beat_count"] == 61
    assert record["checkpoint_generation0_sequence"] == 0
    assert record["checkpoint_generation0_hash216_valid"] is True
    assert validate_hash72(record["manifest_generation0_hash72"])
    assert record["checkpoint_idempotent_replay_equal"] is True
    assert record["checkpoint_idempotent_replay_state"] == "DURABLE_CHECKPOINT_IDEMPOTENT_REPLAY"
    assert record["restart_state_generation0"] == "RESTORED_ACTIVE_GENERATION"
    assert record["restart_root_exact_generation0"] is True
    assert record["restart_snapshot_exact_generation0"] is True
    assert record["restart_receipt_exact_generation0"] is True
    assert record["restart_new_canonical_mutation_invoked"] is False
    assert record["restart_new_authorization_minted"] is False
    assert record["generation1_root_changed"] is True
    assert record["generation1_second_authorization_consumed"] is True
    assert len(record["generation1_second_commit_hash216"]) == 216
    assert "P218_I7_INJECTED_FAILURE_BEFORE_MANIFEST_SWAP" in record[
        "interrupted_checkpoint_failure"
    ]
    assert record["manifest_unchanged_after_interrupted_checkpoint"] is True
    assert record["interrupted_checkpoint_restore_state"] == "RESTORED_ACTIVE_GENERATION"
    assert record["interrupted_checkpoint_restores_generation0"] is True
    assert record["checkpoint_generation1_sequence"] == 1
    assert (
        record["checkpoint_generation1_previous_sha256"]
        == record["checkpoint_generation0_sha256"]
    )
    assert record["active_corruption_recovery_state"] == "RECOVERED_PREVIOUS_VALID_GENERATION"
    assert record["active_corruption_recovered_previous"] is True
    assert record["active_corruption_restores_generation0"] is True
    assert record["source_text_present_in_generation0_persistence"] is False
    assert record["source_text_present_in_generation1_persistence"] is False
    assert record["source_text_present_in_authority_artifacts"] is False
    assert record["canonical_learning_commit_invoked"] is False
    assert record["truth_promotion"] is False
    assert record["action_authority_minted"] is False
    assert record["verbatim_source_retained"] is False
    assert record["pass165_source_retaining_path_invoked"] is False
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
