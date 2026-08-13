"""Repository-native evidence emitter for Pass 218 Iteration 10.

This script requires a real etcd v3 endpoint through
HHS_PASS218_I10_ETCD_TEST_ENDPOINT. It proves that two hosts with unrelated
local I7 stores cannot become simultaneous canonical writers, that a lease-expiry
takeover advances the global fence, and that the successor reconstructs exact
Pass-217/VM81 authority from the distributed sealed checkpoint without source
text or new authorization/mutation during restart.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
import time

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    GenesisSeedBuilder,
    NarrativeBeatHydrator,
    Pass218DistributedRuntimeLifecycle,
    Pass218EtcdDistributedAuthority,
    Pass218RuntimeLifecycleNotReady,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    compile_grammar_rules,
    validate_distributed_checkpoint_record,
)


def _authorization(proof, *, sequence: int, label: str):
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=hash72_digest(
            {"domain": "HHS-P218-I10-REPOSITORY-EVIDENCE-GRANTOR-V1"},
            label.encode("utf-8"),
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return journal, authorization


def _authority(endpoint: str, namespace: str, owner: str, host: str, ttl: int):
    return Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=ttl,
        timeout_seconds=3,
    )


def main() -> None:
    endpoint = os.environ.get("HHS_PASS218_I10_ETCD_TEST_ENDPOINT", "").strip()
    if not endpoint:
        raise RuntimeError("HHS_PASS218_I10_ETCD_TEST_ENDPOINT is required")
    namespace = os.environ.get(
        "HHS_PASS218_I10_ETCD_TEST_NAMESPACE",
        "/hhs/pass218/i10/evidence",
    ).rstrip("/") + "/repository-evidence"

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
    journal, authorization = _authorization(
        proof,
        sequence=1,
        label="iteration10-cross-host-admission",
    )

    with tempfile.TemporaryDirectory(prefix="hhs-p218-i10-hosts-") as temporary:
        root = Path(temporary)
        host_a = Pass218DistributedRuntimeLifecycle(
            root / "host-a",
            owner_id="iteration10-local-a",
            distributed_authority=_authority(
                endpoint,
                namespace,
                "iteration10-owner-a",
                "iteration10-host-a",
                3,
            ),
        )
        host_b = Pass218DistributedRuntimeLifecycle(
            root / "host-b",
            owner_id="iteration10-local-b",
            distributed_authority=_authority(
                endpoint,
                namespace,
                "iteration10-owner-b",
                "iteration10-host-b",
                6,
            ),
        )

        host_a_status = host_a.startup()
        host_b_standby = host_b.startup()
        host_b_boundary_blocked = False
        try:
            host_b.canonical_boundary()
        except Pass218RuntimeLifecycleNotReady:
            host_b_boundary_blocked = True

        boundary = host_a.canonical_boundary()
        prepared = boundary.prepare(
            authorization=authorization,
            staged_candidate=staged,
            authorization_journal=journal,
        )
        committed = host_a.commit_prepared(
            prepared,
            authorization_journal=journal,
        )
        canonical_root = host_a.target.root_hash72()
        vm81_snapshot = host_a.target.snapshot_bytes()
        canonical_receipt = committed["canonical_receipt"]
        remote_before = host_a.distributed.read_checkpoint()
        assert remote_before is not None
        validate_distributed_checkpoint_record(remote_before)

        # Do not renew host A. The lease-bound etcd owner key expires while its
        # local process and local I9 lock remain alive, modeling host isolation
        # from consensus rather than a graceful shutdown.
        takeover_status = None
        for _ in range(8):
            time.sleep(1)
            takeover_status = host_b.attempt_ownership_takeover()
            if takeover_status["distributed_state"] == "PRIMARY":
                break
        assert takeover_status is not None

        stale_host_a_blocked = False
        try:
            host_a.canonical_boundary()
        except Pass218RuntimeLifecycleNotReady:
            stale_host_a_blocked = True

        restored_receipt = host_b.target.committed_receipt(
            authorization["authorization_hash72"]
        )
        remote_after = host_b.distributed.read_checkpoint()
        assert remote_after is not None
        validate_distributed_checkpoint_record(remote_after)

        serialized_authority = json.dumps(
            {
                "owner": host_b.distributed.record,
                "checkpoint": remote_after,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        record = {
            "classification": "HHS_PASS218_ITERATION10_DISTRIBUTED_CANONICAL_OWNERSHIP_EVIDENCE",
            "source_sha256": source_sha256,
            "narrative_beat_count": len(hydration.beats),
            "transaction_id_hash72": transaction.transaction_id_hash72,
            "transaction_hash216": closure["transaction_hash216"],
            "candidate_entry_id_sha256": staged["vector_entry"]["entry_id_sha256"],
            "projection_sha256": staged["vm5184_projection_sha256"],
            "host_a_state": host_a_status["state"],
            "host_a_local_fence_epoch": host_a_status["ownership_fence_epoch"],
            "host_a_distributed_fence_epoch": host_a_status["distributed_fence_epoch"],
            "host_a_distributed_owner": host_a_status["distributed_owner_id"],
            "host_b_state_while_a_primary": host_b_standby["state"],
            "host_b_distributed_writer_while_a_primary": host_b_standby[
                "distributed_writer_authority"
            ],
            "host_b_ingestion_while_a_primary": host_b_standby["ingestion_enabled"],
            "host_b_boundary_blocked_while_a_primary": host_b_boundary_blocked,
            "distributed_checkpoint_sha256": remote_before["checkpoint_sha256"],
            "distributed_checkpoint_hash72": remote_before["checkpoint_hash72"],
            "distributed_checkpoint_seal_hash72": remote_before[
                "distributed_checkpoint_hash72"
            ],
            "canonical_root_hash72": canonical_root,
            "takeover_state": takeover_status["state"],
            "takeover_distributed_fence_epoch": takeover_status["distributed_fence_epoch"],
            "takeover_previous_owner": host_b.distributed.record["previous_owner_id"],
            "takeover_previous_host": host_b.distributed.record["previous_host_id"],
            "takeover_root_exact": host_b.target.root_hash72() == canonical_root,
            "takeover_snapshot_exact": host_b.target.snapshot_bytes() == vm81_snapshot,
            "takeover_receipt_exact": restored_receipt == canonical_receipt,
            "takeover_checkpoint_exact": remote_after["checkpoint_sha256"]
            == remote_before["checkpoint_sha256"],
            "takeover_new_authorization_minted": takeover_status[
                "restart_new_authorization_minted"
            ],
            "takeover_new_canonical_mutation_invoked": takeover_status[
                "restart_new_canonical_mutation_invoked"
            ],
            "stale_host_a_blocked_after_lease_expiry": stale_host_a_blocked,
            "split_brain_writer_permitted": takeover_status[
                "split_brain_writer_permitted"
            ],
            "source_text_present_in_distributed_authority": source_text.encode("utf-8")
            in serialized_authority,
            "pass165_source_retaining_path_invoked": takeover_status[
                "pass165_source_retaining_path_invoked"
            ],
            "canonical_learning_commit_invoked": takeover_status[
                "canonical_learning_commit_invoked"
            ],
            "truth_promotion": takeover_status["truth_promotion"],
            "action_authority_minted": takeover_status["action_authority_minted"],
            "verbatim_source_retained": takeover_status["verbatim_source_retained"],
        }

        assert record["host_a_state"] == "DISTRIBUTED_EMPTY_READY"
        assert record["host_a_local_fence_epoch"] == 1
        assert record["host_a_distributed_fence_epoch"] == 1
        assert record["host_b_state_while_a_primary"] == "DISTRIBUTED_OWNERSHIP_STANDBY"
        assert record["host_b_distributed_writer_while_a_primary"] is False
        assert record["host_b_ingestion_while_a_primary"] is False
        assert record["host_b_boundary_blocked_while_a_primary"] is True
        assert record["takeover_state"] == "DISTRIBUTED_RESTORED_READY"
        assert record["takeover_distributed_fence_epoch"] == 2
        assert record["takeover_previous_owner"] == "iteration10-owner-a"
        assert record["takeover_previous_host"] == "iteration10-host-a"
        assert record["takeover_root_exact"] is True
        assert record["takeover_snapshot_exact"] is True
        assert record["takeover_receipt_exact"] is True
        assert record["takeover_checkpoint_exact"] is True
        assert record["takeover_new_authorization_minted"] is False
        assert record["takeover_new_canonical_mutation_invoked"] is False
        assert record["stale_host_a_blocked_after_lease_expiry"] is True
        assert record["split_brain_writer_permitted"] is False
        assert record["source_text_present_in_distributed_authority"] is False
        assert record["pass165_source_retaining_path_invoked"] is False
        assert record["canonical_learning_commit_invoked"] is False
        assert record["truth_promotion"] is False
        assert record["action_authority_minted"] is False
        assert record["verbatim_source_retained"] is False

        host_b.shutdown()
        host_a.shutdown()
        print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
