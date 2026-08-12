"""Repository-native evidence emitter for Pass 218 full implementation Iteration 5."""
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

    membrane = PromotionProofMembrane()
    proof = membrane.prove(
        closed_transaction_snapshot=snapshot,
        staged_candidate=staged,
    )
    proof_replay = membrane.prove(
        closed_transaction_snapshot=snapshot,
        staged_candidate=staged,
    )

    grantor_authority_hash72 = hash72_digest(
        {"domain": "HHS-P218-I5-REPOSITORY-EVIDENCE-GRANTOR-V1"},
        b"explicit-pass218-iteration5-evidence-authority",
    )
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=grantor_authority_hash72,
        grant_sequence=1,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    authorization_replay = PromotionAuthorizationJournal().authorize(proof, grant)

    rollback_grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=grantor_authority_hash72,
        grant_sequence=2,
    )
    rollback_journal = PromotionAuthorizationJournal()
    rollback_authorization = rollback_journal.authorize(proof, rollback_grant)
    rolled_back = rollback_journal.rollback(
        rollback_authorization["authorization_hash72"],
        reason_code="ITERATION5_DETERMINISTIC_PRECOMMIT_ROLLBACK_EVIDENCE",
    )
    rollback_replay = rollback_journal.rollback(
        rollback_authorization["authorization_hash72"],
        reason_code="ITERATION5_DETERMINISTIC_PRECOMMIT_ROLLBACK_EVIDENCE",
    )

    proof_record = proof.to_record()
    grant_record = grant.to_record()
    record = {
        "classification": "HHS_PASS218_ITERATION5_PROMOTION_ADMISSION_PROOF_EVIDENCE",
        "source_sha256": source_sha256,
        "narrative_beat_count": len(hydration.beats),
        "transaction_id_hash72": transaction.transaction_id_hash72,
        "transaction_hash216": closure["transaction_hash216"],
        "staging_hash72": staged["staging_hash72"],
        "staging_validation_hash72": staged["validation_hash72"],
        "staging_entry_id_sha256": staged["vector_entry"]["entry_id_sha256"],
        "staging_projection_sha256": staged["vm5184_projection_sha256"],
        "proof_hash72": proof.proof_hash72,
        "proof_validation_hash72": proof.validation_hash72,
        "proof_hash216": proof.proof_hash216,
        "proof_hash216_valid": (
            len(proof.proof_hash216) == 216
            and all(
                validate_hash72(proof.proof_hash216[start:start + 72])
                for start in (0, 72, 144)
            )
        ),
        "proof_exact_replay_equal": proof.to_record() == proof_replay.to_record(),
        "proof_promotable": proof_record["promotable"],
        "proof_self_grants_authority": proof_record["explicit_authority_grant_present"],
        "proof_canonical_mutation_permitted": proof_record[
            "canonical_mutation_permitted"
        ],
        "grantor_authority_hash72": grantor_authority_hash72,
        "grant_hash72": grant.grant_hash72,
        "grant_validation_hash72": grant.validation_hash72,
        "grant_hash216": grant.grant_hash216,
        "grant_exact_candidate_binding": (
            grant.entry_id_sha256 == proof.entry_id_sha256
            and grant.staging_hash72 == proof.staging_hash72
            and grant.projection_sha256 == proof.projection_sha256
            and grant.proof_hash72 == proof.proof_hash72
        ),
        "grant_learning_authority": grant_record["learning_authority_granted"],
        "authorization_hash72": authorization["authorization_hash72"],
        "authorization_hash216": authorization["authorization_hash216"],
        "authorization_state": authorization["state"],
        "authorization_exact_replay_equal": authorization == authorization_replay,
        "authorization_requires_proof": authorization["proof_required"],
        "authorization_requires_grant": authorization["grant_required"],
        "authorization_mutation_precondition": journal.mutation_precondition(
            authorization["authorization_hash72"],
            entry_id_sha256=proof.entry_id_sha256,
            projection_sha256=proof.projection_sha256,
        ),
        "rollback_state": rolled_back["state"],
        "rollback_hash72": rolled_back["rollback_hash72"],
        "rollback_exact_replay_equal": rolled_back == rollback_replay,
        "rollback_mutation_precondition": rollback_journal.mutation_precondition(
            rollback_authorization["authorization_hash72"],
            entry_id_sha256=proof.entry_id_sha256,
            projection_sha256=proof.projection_sha256,
        ),
        "journal_authorization_count": journal.record()["authorization_count"],
        "canonical_vector_store_mutation_invoked": authorization[
            "canonical_vector_store_mutation_invoked"
        ],
        "canonical_vm81_commit_invoked": authorization[
            "canonical_vm81_commit_invoked"
        ],
        "canonical_learning_commit_invoked": authorization[
            "canonical_learning_commit_invoked"
        ],
        "truth_promotion": authorization["truth_promotion"],
        "action_authority_minted": authorization["action_authority_minted"],
        "verbatim_source_retained": authorization["verbatim_source_retained"],
    }

    assert record["proof_hash216_valid"] is True
    assert record["proof_exact_replay_equal"] is True
    assert record["proof_promotable"] is True
    assert record["proof_self_grants_authority"] is False
    assert record["proof_canonical_mutation_permitted"] is False
    assert record["grant_exact_candidate_binding"] is True
    assert record["grant_learning_authority"] is False
    assert record["authorization_state"] == "AUTHORIZED_PENDING_CANONICAL_COMMIT"
    assert record["authorization_exact_replay_equal"] is True
    assert record["authorization_requires_proof"] is True
    assert record["authorization_requires_grant"] is True
    assert record["authorization_mutation_precondition"] is True
    assert record["rollback_state"] == "ROLLED_BACK_BEFORE_CANONICAL_COMMIT"
    assert record["rollback_exact_replay_equal"] is True
    assert record["rollback_mutation_precondition"] is False
    assert record["canonical_vector_store_mutation_invoked"] is False
    assert record["canonical_vm81_commit_invoked"] is False
    assert record["canonical_learning_commit_invoked"] is False
    assert record["truth_promotion"] is False
    assert record["action_authority_minted"] is False
    assert record["verbatim_source_retained"] is False
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
