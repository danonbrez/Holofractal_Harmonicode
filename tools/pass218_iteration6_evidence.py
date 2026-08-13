"""Repository-native evidence emitter for Pass 218 full implementation Iteration 6."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

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
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    compile_grammar_rules,
)


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
    grantor_authority_hash72 = hash72_digest(
        {"domain": "HHS-P218-I6-REPOSITORY-EVIDENCE-GRANTOR-V1"},
        b"explicit-pass218-iteration6-canonical-admission-authority",
    )
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=grantor_authority_hash72,
        grant_sequence=1,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)

    target = Pass217VM81CanonicalTarget()
    target_root_before = target.root_hash72()
    target_snapshot_before = target.snapshot_bytes()
    boundary = Pass218CanonicalCommitBoundary(target=target)
    prepared = boundary.prepare(
        authorization=authorization,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    prepare_record = prepared.to_record()

    failure_target = Pass217VM81CanonicalTarget()
    failure_boundary = Pass218CanonicalCommitBoundary(target=failure_target)
    failure_prepared = failure_boundary.prepare(
        authorization=authorization,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    failure_root_before = failure_target.root_hash72()
    failure_snapshot_before = failure_target.snapshot_bytes()
    injected_failure_class = ""
    try:
        failure_boundary.commit(
            failure_prepared,
            authorization_journal=journal,
            fail_before_atomic_swap=True,
        )
    except Exception as exc:
        injected_failure_class = str(exc)
    recovery = failure_boundary.recover_failed_commit(
        failure_prepared,
        authorization_journal=journal,
        reason_code="ITERATION6_REPOSITORY_EVIDENCE_INJECTED_PRE_SWAP_FAILURE",
    )
    recovery_replay = failure_boundary.recover_failed_commit(
        failure_prepared,
        authorization_journal=journal,
        reason_code="ITERATION6_REPOSITORY_EVIDENCE_INJECTED_PRE_SWAP_FAILURE",
    )

    receipt = boundary.commit(prepared, authorization_journal=journal)
    receipt_replay = boundary.commit(prepared, authorization_journal=journal)
    target_record = target.record()
    serialized = json.dumps(
        {
            "prepare": prepare_record,
            "receipt": receipt,
            "target": target_record,
            "recovery": recovery,
        },
        sort_keys=True,
    )

    record = {
        "classification": "HHS_PASS218_ITERATION6_CANONICAL_COMMIT_BOUNDARY_EVIDENCE",
        "source_sha256": source_sha256,
        "narrative_beat_count": len(hydration.beats),
        "transaction_id_hash72": transaction.transaction_id_hash72,
        "transaction_hash216": closure["transaction_hash216"],
        "candidate_entry_id_sha256": staged["vector_entry"]["entry_id_sha256"],
        "projection_sha256": staged["vm5184_projection_sha256"],
        "authorization_hash72": authorization["authorization_hash72"],
        "authorization_state_before_commit": authorization["state"],
        "prepare_hash72": prepared.prepare_hash72,
        "prepare_validation_hash72": prepared.validation_hash72,
        "prepare_hash216": prepared.prepare_hash216,
        "prepare_hash216_valid": (
            len(prepared.prepare_hash216) == 216
            and all(
                validate_hash72(prepared.prepare_hash216[start:start + 72])
                for start in (0, 72, 144)
            )
        ),
        "prepared_admitted_entry_id_sha256": prepared.admitted_entry[
            "entry_id_sha256"
        ],
        "prepared_admission_status": prepared.admitted_entry["admission_status"],
        "prepared_vm81_commit_count": len(prepared.vm81_receipts),
        "prepared_vm81_projection_exact": (
            prepared.shadow_runtime.snapshot().to_bytes() == prepared.projection_bytes
        ),
        "prepare_target_unmutated": target.root_hash72() == target_root_before,
        "injected_failure_class": injected_failure_class,
        "failed_commit_root_unchanged": failure_target.root_hash72() == failure_root_before,
        "failed_commit_snapshot_unchanged": (
            failure_target.snapshot_bytes() == failure_snapshot_before
        ),
        "failed_commit_entry_count": failure_target.record()["canonical_entry_count"],
        "failed_commit_commit_count": failure_target.record()["canonical_commit_count"],
        "recovery_state": recovery["state"],
        "recovery_hash72": recovery["recovery_hash72"],
        "recovery_exact_replay_equal": recovery == recovery_replay,
        "recovery_retry_permitted": recovery["retry_permitted"],
        "commit_hash72": receipt["commit_hash72"],
        "receipt_hash72": receipt["receipt_hash72"],
        "commit_hash216": receipt["commit_hash216"],
        "commit_hash216_valid": (
            len(receipt["commit_hash216"]) == 216
            and all(
                validate_hash72(receipt["commit_hash216"][start:start + 72])
                for start in (0, 72, 144)
            )
        ),
        "commit_state": receipt["state"],
        "commit_exact_replay_equal": receipt == receipt_replay,
        "target_root_before_hash72": target_root_before,
        "target_root_after_hash72": target.root_hash72(),
        "target_root_matches_receipt": (
            target.root_hash72() == receipt["target_root_after_hash72"]
        ),
        "target_snapshot_matches_projection": (
            target.snapshot_bytes() == prepared.projection_bytes
        ),
        "canonical_entry_count": target_record["canonical_entry_count"],
        "canonical_commit_count": target_record["canonical_commit_count"],
        "canonical_vector_store_mutation_invoked": receipt[
            "canonical_vector_store_mutation_invoked"
        ],
        "canonical_vm81_commit_invoked": receipt["canonical_vm81_commit_invoked"],
        "canonical_learning_commit_invoked": receipt[
            "canonical_learning_commit_invoked"
        ],
        "truth_promotion": receipt["truth_promotion"],
        "action_authority_minted": receipt["action_authority_minted"],
        "verbatim_source_retained": receipt["verbatim_source_retained"],
        "pass165_source_retaining_path_invoked": receipt[
            "pass165_source_retaining_path_invoked"
        ],
        "source_text_present_in_authority_artifacts": source_text in serialized,
    }

    assert record["prepare_hash216_valid"] is True
    assert record["prepared_admission_status"] == "VM81_ADMITTED"
    assert record["prepared_vm81_commit_count"] == 64
    assert record["prepared_vm81_projection_exact"] is True
    assert record["prepare_target_unmutated"] is True
    assert "P218_I6_INJECTED_COMMIT_FAILURE_BEFORE_ATOMIC_SWAP" in record[
        "injected_failure_class"
    ]
    assert record["failed_commit_root_unchanged"] is True
    assert record["failed_commit_snapshot_unchanged"] is True
    assert record["failed_commit_entry_count"] == 0
    assert record["failed_commit_commit_count"] == 0
    assert record["recovery_state"] == "RECOVERABLE_PREPARED_NOT_COMMITTED"
    assert record["recovery_exact_replay_equal"] is True
    assert record["recovery_retry_permitted"] is True
    assert record["commit_hash216_valid"] is True
    assert record["commit_state"] == "CANONICAL_COMMITTED"
    assert record["commit_exact_replay_equal"] is True
    assert record["target_root_matches_receipt"] is True
    assert record["target_snapshot_matches_projection"] is True
    assert record["canonical_entry_count"] == 1
    assert record["canonical_commit_count"] == 1
    assert record["canonical_vector_store_mutation_invoked"] is True
    assert record["canonical_vm81_commit_invoked"] is True
    assert record["canonical_learning_commit_invoked"] is False
    assert record["truth_promotion"] is False
    assert record["action_authority_minted"] is False
    assert record["verbatim_source_retained"] is False
    assert record["pass165_source_retaining_path_invoked"] is False
    assert record["source_text_present_in_authority_artifacts"] is False
    assert target_snapshot_before != target.snapshot_bytes()
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
