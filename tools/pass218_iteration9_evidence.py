"""Repository-native evidence emitter for Pass 218 full implementation Iteration 9."""
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
    Pass218MultiprocessRuntimeLifecycle,
    Pass218RuntimeLifecycleNotReady,
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
            {"domain": "HHS-P218-I9-REPOSITORY-EVIDENCE-GRANTOR-V1"},
            label.encode("utf-8"),
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return journal, authorization


def main() -> None:
    grammar_path = REPOSITORY_ROOT / "hhs_runtime" / "Grammar Correction.csv"
    narrative_path = REPOSITORY_ROOT / "creative_writing" / "novels" / "THE_SMALLEST_PERMISSION.md"
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

    with tempfile.TemporaryDirectory(prefix="hhs-p218-i9-evidence-") as temporary:
        root = Path(temporary)
        primary = Pass218MultiprocessRuntimeLifecycle(root, owner_id="iteration9-primary")
        standby = Pass218MultiprocessRuntimeLifecycle(root, owner_id="iteration9-standby")

        primary_status = primary.startup()
        standby_status = standby.startup()
        standby_blocked = False
        try:
            standby.canonical_boundary()
        except Pass218RuntimeLifecycleNotReady:
            standby_blocked = True

        journal, authorization = _authorization(
            proof,
            sequence=1,
            label="iteration9-primary-canonical-admission",
        )
        boundary = primary.canonical_boundary()
        prepared = boundary.prepare(
            authorization=authorization,
            staged_candidate=staged,
            authorization_journal=journal,
        )
        committed = primary.commit_prepared(
            prepared,
            authorization_journal=journal,
        )
        root_hash72 = primary.target.root_hash72()
        vm81_snapshot = primary.target.snapshot_bytes()
        canonical_receipt = committed["canonical_receipt"]
        checkpoint_sha256 = committed["checkpoint_sha256"]
        primary.shutdown()

        takeover_status = standby.attempt_ownership_takeover()
        restored_receipt = standby.target.committed_receipt(
            authorization["authorization_hash72"]
        )
        takeover_root_exact = standby.target.root_hash72() == root_hash72
        takeover_snapshot_exact = standby.target.snapshot_bytes() == vm81_snapshot
        takeover_receipt_exact = restored_receipt == canonical_receipt

        contender = Pass218MultiprocessRuntimeLifecycle(root, owner_id="iteration9-contender")
        contender_status = contender.startup()
        contender_blocked = False
        try:
            contender.canonical_boundary()
        except Pass218RuntimeLifecycleNotReady:
            contender_blocked = True

        standby.shutdown()
        second_takeover = contender.attempt_ownership_takeover()

        generation_bytes = b"\n".join(
            path.read_bytes()
            for path in sorted((root / "generations").glob("checkpoint-*.json"))
        )
        ownership_bytes = (root / "ownership.json").read_bytes()
        serialized_authority = generation_bytes + b"\n" + ownership_bytes

        record = {
            "classification": "HHS_PASS218_ITERATION9_MULTIPROCESS_CANONICAL_OWNERSHIP_EVIDENCE",
            "source_sha256": source_sha256,
            "narrative_beat_count": len(hydration.beats),
            "transaction_id_hash72": transaction.transaction_id_hash72,
            "transaction_hash216": closure["transaction_hash216"],
            "candidate_entry_id_sha256": staged["vector_entry"]["entry_id_sha256"],
            "projection_sha256": staged["vm5184_projection_sha256"],
            "primary_state": primary_status["state"],
            "primary_ownership_state": primary_status["ownership_state"],
            "primary_fence_epoch": primary_status["ownership_fence_epoch"],
            "standby_state_while_primary": standby_status["state"],
            "standby_ingestion_enabled_while_primary": standby_status["ingestion_enabled"],
            "standby_writer_authority_while_primary": standby_status["ownership_writer_authority"],
            "standby_canonical_boundary_blocked": standby_blocked,
            "checkpoint_sha256": checkpoint_sha256,
            "canonical_root_hash72": root_hash72,
            "takeover_state": takeover_status["state"],
            "takeover_fence_epoch": takeover_status["ownership_fence_epoch"],
            "takeover_previous_owner": standby.ownership.read_persisted_record()["previous_owner_id"],
            "takeover_root_exact": takeover_root_exact,
            "takeover_snapshot_exact": takeover_snapshot_exact,
            "takeover_receipt_exact": takeover_receipt_exact,
            "takeover_new_authorization_minted": takeover_status["restart_new_authorization_minted"],
            "takeover_new_canonical_mutation_invoked": takeover_status["restart_new_canonical_mutation_invoked"],
            "contender_state_while_standby_primary": contender_status["state"],
            "contender_blocked_while_standby_primary": contender_blocked,
            "second_takeover_state": second_takeover["state"],
            "second_takeover_fence_epoch": second_takeover["ownership_fence_epoch"],
            "second_takeover_root_exact": contender.target.root_hash72() == root_hash72,
            "split_brain_writer_permitted": second_takeover["split_brain_writer_permitted"],
            "source_text_present_in_persisted_authority": source_text.encode("utf-8") in serialized_authority,
            "pass165_source_retaining_path_invoked": second_takeover["pass165_source_retaining_path_invoked"],
            "canonical_learning_commit_invoked": second_takeover["canonical_learning_commit_invoked"],
            "truth_promotion": second_takeover["truth_promotion"],
            "action_authority_minted": second_takeover["action_authority_minted"],
            "verbatim_source_retained": second_takeover["verbatim_source_retained"],
        }

        assert record["primary_state"] == "EMPTY_READY"
        assert record["primary_ownership_state"] == "PRIMARY"
        assert record["primary_fence_epoch"] == 1
        assert record["standby_state_while_primary"] == "OWNERSHIP_STANDBY"
        assert record["standby_ingestion_enabled_while_primary"] is False
        assert record["standby_writer_authority_while_primary"] is False
        assert record["standby_canonical_boundary_blocked"] is True
        assert record["takeover_state"] == "RESTORED_READY"
        assert record["takeover_fence_epoch"] == 2
        assert record["takeover_previous_owner"] == "iteration9-primary"
        assert record["takeover_root_exact"] is True
        assert record["takeover_snapshot_exact"] is True
        assert record["takeover_receipt_exact"] is True
        assert record["takeover_new_authorization_minted"] is False
        assert record["takeover_new_canonical_mutation_invoked"] is False
        assert record["contender_state_while_standby_primary"] == "OWNERSHIP_STANDBY"
        assert record["contender_blocked_while_standby_primary"] is True
        assert record["second_takeover_state"] == "RESTORED_READY"
        assert record["second_takeover_fence_epoch"] == 3
        assert record["second_takeover_root_exact"] is True
        assert record["split_brain_writer_permitted"] is False
        assert record["source_text_present_in_persisted_authority"] is False
        assert record["pass165_source_retaining_path_invoked"] is False
        assert record["canonical_learning_commit_invoked"] is False
        assert record["truth_promotion"] is False
        assert record["action_authority_minted"] is False
        assert record["verbatim_source_retained"] is False
        contender.shutdown()
        print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
