"""Repository-native evidence emitter for Pass 218 full implementation Iteration 3."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations
from hhs_runtime.pass218 import (
    DeterministicStructuralStore,
    GenesisSeedBuilder,
    NarrativeBeatHydrator,
    SourceTransaction,
    TransactionPhase,
    compile_grammar_rules,
)


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

    store = DeterministicStructuralStore()
    tx = SourceTransaction.begin(hydration, source_text, store=store)
    tx.validate()
    tx.commit_structural()
    pending_before_purge = store.is_pending(tx.transaction_id_hash72)
    admitted_before_purge = store.is_admitted(tx.transaction_id_hash72)
    closure = tx.purge_and_close()
    snapshot = tx.snapshot()

    replay_store = DeterministicStructuralStore()
    replay = SourceTransaction.restore(snapshot, store=replay_store)

    interrupted = SourceTransaction.begin(hydration, source_text)
    interrupted.validate()
    interrupted.commit_structural()
    interrupted_snapshot = interrupted.snapshot()
    recovered_store = DeterministicStructuralStore()
    recovered = SourceTransaction.restore(interrupted_snapshot, store=recovered_store)
    recovery_receipt = recovered.recover_interrupted_commit()

    rejected = SourceTransaction.begin(hydration, source_text + "\nchecksum-mismatch")

    record = {
        "classification": "HHS_PASS218_ITERATION3_SOURCE_TRANSACTION_MEMBRANE_EVIDENCE",
        "transaction_id_hash72": tx.transaction_id_hash72,
        "transaction_phase": tx.phase.name,
        "transaction_hash216": closure["transaction_hash216"],
        "transaction_hash216_valid": (
            len(closure["transaction_hash216"]) == 216
            and all(validate_hash72(closure["transaction_hash216"][start:start + 72]) for start in (0, 72, 144))
        ),
        "transaction_hash216_semantics": closure["hash216_semantics"],
        "structural_record_hash72": closure["structural_record_hash72"],
        "purge_receipt_hash72": closure["purge_receipt_hash72"],
        "memory_root_hash72": closure["memory_root_hash72"],
        "pending_before_purge": pending_before_purge,
        "admitted_before_purge": admitted_before_purge,
        "admitted_after_purge": store.is_admitted(tx.transaction_id_hash72),
        "managed_source_bytes_after_close": tx.managed_source_bytes,
        "managed_buffer_zeroized": closure["managed_buffer_zeroized"],
        "managed_buffer_cleared": closure["managed_buffer_cleared"],
        "physical_memory_erasure_claimed": closure["physical_memory_erasure_claimed"],
        "snapshot_hash72": snapshot["snapshot_hash72"],
        "snapshot_source_buffer_serialized": snapshot["source_buffer_serialized"],
        "journal_valid": tx.verify_journal(),
        "closed_replay_phase": replay.phase.name,
        "closed_replay_admitted": replay_store.is_admitted(replay.transaction_id_hash72),
        "closed_replay_receipt_equal": replay.closure_receipt == closure,
        "interrupted_recovery_phase": recovered.phase.name,
        "interrupted_recovery_reason": recovery_receipt["payload"]["reason"],
        "interrupted_recovery_admitted": recovered_store.is_admitted(recovered.transaction_id_hash72),
        "rejected_checksum_phase": rejected.phase.name,
        "rejected_checksum_source_bytes_after_reject": rejected.managed_source_bytes,
        "rejected_checksum_purge_receipt_valid": validate_hash72(rejected.purge_receipt["purge_receipt_hash72"]),
        "source_sha256": source_sha256,
        "narrative_beat_count": len(hydration.beats),
        "verbatim_source_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "authoritative_vector_store_promotion": False,
        "authoritative_float_weights": False,
    }
    assert tx.phase == TransactionPhase.CLOSED
    assert record["pending_before_purge"] is True
    assert record["admitted_before_purge"] is False
    assert record["admitted_after_purge"] is True
    assert record["managed_source_bytes_after_close"] == 0
    assert record["closed_replay_admitted"] is True
    assert record["interrupted_recovery_admitted"] is False
    assert record["rejected_checksum_source_bytes_after_reject"] == 0
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
