"""Repository-native evidence emitter for Pass 218 full implementation Iteration 4."""
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
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    GenesisSeedBuilder,
    NarrativeBeatHydrator,
    NonAuthoritativeVectorStageStore,
    SourceTransaction,
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

    transaction = SourceTransaction.begin(hydration, source_text)
    closure = transaction.commit_and_purge()
    snapshot = transaction.snapshot()

    stage_store = NonAuthoritativeVectorStageStore()
    adapter = ClosedTransactionVectorVM5184Adapter(stage_store=stage_store)
    staged = adapter.stage(snapshot)
    replay = ClosedTransactionVectorVM5184Adapter().stage(snapshot)
    entry = staged["vector_entry"]

    schema = json.loads(
        (REPOSITORY_ROOT / "contracts" / "pass217" / "vector_store.schema.json").read_text("utf-8")
    )
    forward = entry["forward_support"]
    inverse = entry["inverse_support"]

    record = {
        "classification": "HHS_PASS218_ITERATION4_VECTOR_VM5184_STAGING_EVIDENCE",
        "source_sha256": source_sha256,
        "narrative_beat_count": len(hydration.beats),
        "transaction_id_hash72": transaction.transaction_id_hash72,
        "transaction_hash216": closure["transaction_hash216"],
        "purge_receipt_hash72": closure["purge_receipt_hash72"],
        "closed_transaction_required": True,
        "managed_buffer_cleared": closure["managed_buffer_cleared"],
        "vector_entry_schema": entry["schema"],
        "vector_entry_id_sha256": entry["entry_id_sha256"],
        "vector_entry_matches_pass217_required_fields": set(entry) == set(schema["required"]),
        "vector_admission_status": entry["admission_status"],
        "vm5184_projection_bytes": staged["vm5184_projection_bytes"],
        "vm5184_projection_popcount": staged["vm5184_projection_popcount"],
        "forward_support_count": len(forward),
        "inverse_support_count": len(inverse),
        "support_partition_complete": len(forward) + len(inverse) == COORDINATES,
        "support_partition_disjoint": not (set(forward) & set(inverse)),
        "vm5184_expected_snapshot_bytes": SNAPSHOT_BYTES,
        "ordered_path_count": len(entry["ordered_path"]),
        "dependency_frontier_count": len(entry["dependency_frontier"]),
        "staging_hash72": staged["staging_hash72"],
        "validation_hash72": staged["validation_hash72"],
        "staging_hash216": staged["staging_hash216"],
        "staging_hash216_valid": (
            len(staged["staging_hash216"]) == 216
            and all(
                validate_hash72(staged["staging_hash216"][start:start + 72])
                for start in (0, 72, 144)
            )
        ),
        "staging_hash216_semantics": staged["hash216_semantics"],
        "exact_replay_equal": replay == staged,
        "stage_store_candidate_count": stage_store.record()["candidate_count"],
        "inherited_projection_surface": staged["inherited_projection_surface"],
        "inherited_vm_geometry": staged["inherited_vm_geometry"],
        "inherited_instruction_addressing": staged["inherited_instruction_addressing"],
        "inherited_vector_entry_contract": staged["inherited_vector_entry_contract"],
        "verbatim_source_retained": staged["verbatim_source_retained"],
        "truth_promotion": staged["truth_promotion"],
        "action_authority_minted": staged["action_authority_minted"],
        "authoritative_vector_store_promotion": staged["authoritative_vector_store_promotion"],
        "canonical_vm81_commit_invoked": staged["canonical_vm81_commit_invoked"],
        "canonical_learning_commit_invoked": staged["canonical_learning_commit_invoked"],
        "authoritative_float_weights": staged["authoritative_float_weights"],
    }

    assert record["managed_buffer_cleared"] is True
    assert record["vector_entry_matches_pass217_required_fields"] is True
    assert record["vector_admission_status"] == "CANDIDATE"
    assert record["vm5184_projection_bytes"] == 648
    assert record["support_partition_complete"] is True
    assert record["support_partition_disjoint"] is True
    assert record["staging_hash216_valid"] is True
    assert record["exact_replay_equal"] is True
    assert record["stage_store_candidate_count"] == 1
    assert record["authoritative_vector_store_promotion"] is False
    assert record["canonical_vm81_commit_invoked"] is False
    assert record["canonical_learning_commit_invoked"] is False
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
