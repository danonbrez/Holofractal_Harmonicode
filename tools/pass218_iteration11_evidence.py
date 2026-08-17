"""Repository-native seed and disaster-recovery evidence for Pass 218 I11.

`seed` hydrates THE_SMALLEST_PERMISSION.md through I1-I6, commits it through the
I11 quorum-gated lifecycle to a real mTLS etcd cluster, records the exact I10
distributed checkpoint, and cleanly releases the ephemeral owner before an etcd
snapshot is taken.

`recover` runs after that snapshot has been restored into a fresh etcd cluster.
It acquires a new global fence from an unrelated local persistence root, proves
that the distributed checkpoint reconstructs the exact canonical root, VM81
snapshot, and consumed I6 receipt, and seals a disaster-recovery manifest that
binds the real snapshot SHA-256/status to that checkpoint.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
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
    Pass218EtcdClusterAuthority,
    Pass218EtcdClusterConfig,
    Pass218EtcdClusterMonitor,
    Pass218OperationallyHardenedRuntimeLifecycle,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    compile_grammar_rules,
    restore_target_from_disaster_recovery_manifest,
    seal_disaster_recovery_manifest,
    validate_disaster_recovery_manifest,
    validate_distributed_checkpoint_record,
)


def _cluster_config() -> Pass218EtcdClusterConfig:
    endpoints = tuple(
        value.strip()
        for value in os.environ.get("HHS_PASS218_I11_ETCD_ENDPOINTS", "").split(",")
        if value.strip()
    )
    if not endpoints:
        raise RuntimeError("HHS_PASS218_I11_ETCD_ENDPOINTS is required")
    return Pass218EtcdClusterConfig.build(
        endpoints,
        ca_file=os.environ["HHS_PASS218_I11_ETCD_CA_FILE"],
        client_cert_file=os.environ["HHS_PASS218_I11_ETCD_CLIENT_CERT_FILE"],
        client_key_file=os.environ["HHS_PASS218_I11_ETCD_CLIENT_KEY_FILE"],
        cluster_name=os.environ.get("HHS_PASS218_I11_CLUSTER_NAME", "i11-ci-cluster"),
        timeout_seconds=2,
    )


def _lifecycle(root: Path, *, owner: str, host: str):
    config = _cluster_config()
    namespace = os.environ.get(
        "HHS_PASS218_I11_ETCD_NAMESPACE",
        "/hhs/pass218/i11/evidence",
    ).rstrip("/")
    authority = Pass218EtcdClusterAuthority(
        config,
        namespace=namespace,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=9,
    )
    monitor = Pass218EtcdClusterMonitor(config, authority.client, namespace=namespace)
    return Pass218OperationallyHardenedRuntimeLifecycle(
        root,
        owner_id="local-" + owner,
        distributed_authority=authority,
        cluster_monitor=monitor,
    )


def _authorization(proof, *, sequence: int, label: str):
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=hash72_digest(
            {"domain": "HHS-P218-I11-REPOSITORY-EVIDENCE-GRANTOR-V1"},
            label.encode("utf-8"),
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return journal, authorization


def _pipeline():
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
    journal, authorization = _authorization(
        proof,
        sequence=1,
        label="iteration11-operational-hardening-admission",
    )
    return {
        "source_text": source_text,
        "source_sha256": source_sha256,
        "hydration": hydration,
        "transaction": transaction,
        "closure": closure,
        "staged": staged,
        "journal": journal,
        "authorization": authorization,
    }


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _snapshot_status(path: Path) -> dict[str, int]:
    value = json.loads(path.read_text("utf-8"))
    if isinstance(value, list):
        if len(value) != 1 or not isinstance(value[0], dict):
            raise RuntimeError("unexpected etcdutl snapshot status list")
        value = value[0]
    if not isinstance(value, dict):
        raise RuntimeError("unexpected etcdutl snapshot status")

    def number(*keys: str) -> int:
        for key in keys:
            if key in value:
                raw = value[key]
                if isinstance(raw, int) and not isinstance(raw, bool):
                    return raw
                if isinstance(raw, str) and raw.isdigit():
                    return int(raw)
        raise RuntimeError("missing snapshot status key: " + "/".join(keys))

    return {
        "revision": number("revision", "Revision"),
        "total_keys": number("totalKey", "total_key", "totalKeys", "TotalKey"),
        "total_size": number("totalSize", "total_size", "TotalSize"),
    }


def seed(output_dir: Path) -> None:
    pipeline = _pipeline()
    with tempfile.TemporaryDirectory(prefix="hhs-p218-i11-seed-") as temporary:
        lifecycle = _lifecycle(
            Path(temporary) / "seed-host",
            owner="iteration11-seed-owner",
            host="iteration11-seed-host",
        )
        status = lifecycle.startup()
        assert status["cluster_quorum_ready"] is True
        boundary = lifecycle.canonical_boundary()
        prepared = boundary.prepare(
            authorization=pipeline["authorization"],
            staged_candidate=pipeline["staged"],
            authorization_journal=pipeline["journal"],
        )
        committed = lifecycle.commit_prepared(
            prepared,
            authorization_journal=pipeline["journal"],
        )
        checkpoint = lifecycle.distributed.read_checkpoint()
        assert checkpoint is not None
        validate_distributed_checkpoint_record(checkpoint)
        committed_receipt = lifecycle.target.committed_receipt(
            pipeline["authorization"]["authorization_hash72"]
        )
        probe = lifecycle.cluster_monitor.require_quorum_ready()
        source_text = pipeline["source_text"]
        serialized_authority = json.dumps(
            {"owner": lifecycle.distributed.record, "checkpoint": checkpoint},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        evidence = {
            "classification": "HHS_PASS218_ITERATION11_OPERATIONAL_SEED_EVIDENCE",
            "source_sha256": pipeline["source_sha256"],
            "narrative_beat_count": len(pipeline["hydration"].beats),
            "transaction_id_hash72": pipeline["transaction"].transaction_id_hash72,
            "transaction_hash216": pipeline["closure"]["transaction_hash216"],
            "candidate_entry_id_sha256": pipeline["staged"]["vector_entry"]["entry_id_sha256"],
            "projection_sha256": pipeline["staged"]["vm5184_projection_sha256"],
            "cluster_id": probe["cluster_id"],
            "cluster_member_ids": probe["member_ids"],
            "cluster_leader_ids": probe["leader_ids"],
            "cluster_quorum_ready": probe["quorum_ready"],
            "cluster_probe_hash72": probe["probe_hash72"],
            "seed_distributed_fence_epoch": status["distributed_fence_epoch"],
            "canonical_root_hash72": lifecycle.target.root_hash72(),
            "vm81_snapshot_sha256": sha256(lifecycle.target.snapshot_bytes()).hexdigest(),
            "authorization_hash72": pipeline["authorization"]["authorization_hash72"],
            "canonical_receipt": committed_receipt,
            "distributed_checkpoint_sha256": checkpoint["checkpoint_sha256"],
            "distributed_checkpoint_hash72": checkpoint["checkpoint_hash72"],
            "distributed_checkpoint_seal_hash72": checkpoint["distributed_checkpoint_hash72"],
            "source_text_present_in_distributed_authority": source_text.encode("utf-8")
            in serialized_authority,
            "verbatim_source_retained": status["verbatim_source_retained"],
            "pass165_source_retaining_path_invoked": status[
                "pass165_source_retaining_path_invoked"
            ],
            "canonical_learning_commit_invoked": status[
                "canonical_learning_commit_invoked"
            ],
            "truth_promotion": status["truth_promotion"],
            "action_authority_minted": status["action_authority_minted"],
            "commit_receipt_state": committed["state"],
        }
        assert evidence["cluster_quorum_ready"] is True
        assert evidence["source_text_present_in_distributed_authority"] is False
        assert evidence["verbatim_source_retained"] is False
        assert evidence["pass165_source_retaining_path_invoked"] is False
        assert evidence["canonical_learning_commit_invoked"] is False
        assert evidence["truth_promotion"] is False
        assert evidence["action_authority_minted"] is False
        _write_json(output_dir / "seed.json", evidence)
        _write_json(output_dir / "distributed-checkpoint.json", checkpoint)
        lifecycle.shutdown()
        print(json.dumps(evidence, indent=2, sort_keys=True))


def recover(output_dir: Path, snapshot_file: Path, snapshot_status_file: Path) -> None:
    seed_record = json.loads((output_dir / "seed.json").read_text("utf-8"))
    snapshot_status = _snapshot_status(snapshot_status_file)
    snapshot_bytes = snapshot_file.read_bytes()
    with tempfile.TemporaryDirectory(prefix="hhs-p218-i11-recover-") as temporary:
        lifecycle = _lifecycle(
            Path(temporary) / "recovered-host",
            owner="iteration11-recovery-owner",
            host="iteration11-recovery-host",
        )
        status = lifecycle.startup()
        assert status["ingestion_enabled"] is True
        assert status["cluster_quorum_ready"] is True
        checkpoint = lifecycle.distributed.read_checkpoint()
        assert checkpoint is not None
        validate_distributed_checkpoint_record(checkpoint)
        restored_receipt = lifecycle.target.committed_receipt(
            seed_record["authorization_hash72"]
        )
        manifest = seal_disaster_recovery_manifest(
            cluster_name=_cluster_config().cluster_name,
            cluster_id=int(seed_record["cluster_id"]),
            snapshot_sha256=sha256(snapshot_bytes).hexdigest(),
            snapshot_size_bytes=len(snapshot_bytes),
            snapshot_revision=snapshot_status["revision"],
            snapshot_total_keys=snapshot_status["total_keys"],
            distributed_checkpoint=checkpoint,
        )
        validate_disaster_recovery_manifest(manifest)
        manifest_target = restore_target_from_disaster_recovery_manifest(manifest)
        serialized = json.dumps(
            {"checkpoint": checkpoint, "manifest": manifest},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        source_text = (
            REPOSITORY_ROOT
            / "creative_writing"
            / "novels"
            / "THE_SMALLEST_PERMISSION.md"
        ).read_text("utf-8")
        evidence = {
            "classification": "HHS_PASS218_ITERATION11_DISASTER_RECOVERY_EVIDENCE",
            "snapshot_sha256": manifest["snapshot_sha256"],
            "snapshot_size_bytes": manifest["snapshot_size_bytes"],
            "snapshot_revision": manifest["snapshot_revision"],
            "snapshot_total_keys": manifest["snapshot_total_keys"],
            "disaster_recovery_manifest_hash72": manifest["manifest_hash72"],
            "seed_cluster_id": seed_record["cluster_id"],
            "restored_cluster_id": status["cluster_id"],
            "seed_distributed_fence_epoch": seed_record["seed_distributed_fence_epoch"],
            "recovery_distributed_fence_epoch": status["distributed_fence_epoch"],
            "recovery_previous_owner": lifecycle.distributed.record["previous_owner_id"],
            "recovery_previous_host": lifecycle.distributed.record["previous_host_id"],
            "canonical_root_exact": lifecycle.target.root_hash72()
            == seed_record["canonical_root_hash72"],
            "vm81_snapshot_exact": sha256(lifecycle.target.snapshot_bytes()).hexdigest()
            == seed_record["vm81_snapshot_sha256"],
            "consumed_i6_receipt_exact": restored_receipt == seed_record["canonical_receipt"],
            "distributed_checkpoint_exact": checkpoint["checkpoint_sha256"]
            == seed_record["distributed_checkpoint_sha256"],
            "manifest_target_root_exact": manifest_target.root_hash72()
            == seed_record["canonical_root_hash72"],
            "restart_new_authorization_minted": status[
                "restart_new_authorization_minted"
            ],
            "restart_new_canonical_mutation_invoked": status[
                "restart_new_canonical_mutation_invoked"
            ],
            "source_text_present_in_recovery_authority": source_text.encode("utf-8")
            in serialized,
            "cluster_quorum_ready": status["cluster_quorum_ready"],
            "split_brain_writer_permitted": status["split_brain_writer_permitted"],
            "verbatim_source_retained": status["verbatim_source_retained"],
            "pass165_source_retaining_path_invoked": status[
                "pass165_source_retaining_path_invoked"
            ],
            "canonical_learning_commit_invoked": status[
                "canonical_learning_commit_invoked"
            ],
            "truth_promotion": status["truth_promotion"],
            "action_authority_minted": status["action_authority_minted"],
        }
        assert evidence["recovery_distributed_fence_epoch"] > evidence[
            "seed_distributed_fence_epoch"
        ]
        assert evidence["canonical_root_exact"] is True
        assert evidence["vm81_snapshot_exact"] is True
        assert evidence["consumed_i6_receipt_exact"] is True
        assert evidence["distributed_checkpoint_exact"] is True
        assert evidence["manifest_target_root_exact"] is True
        assert evidence["restart_new_authorization_minted"] is False
        assert evidence["restart_new_canonical_mutation_invoked"] is False
        assert evidence["source_text_present_in_recovery_authority"] is False
        assert evidence["cluster_quorum_ready"] is True
        assert evidence["split_brain_writer_permitted"] is False
        assert evidence["verbatim_source_retained"] is False
        assert evidence["pass165_source_retaining_path_invoked"] is False
        assert evidence["canonical_learning_commit_invoked"] is False
        assert evidence["truth_promotion"] is False
        assert evidence["action_authority_minted"] is False
        _write_json(output_dir / "disaster-recovery-manifest.json", manifest)
        _write_json(output_dir / "recovery.json", evidence)
        lifecycle.shutdown()
        print(json.dumps(evidence, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("seed", "recover"))
    parser.add_argument("--output-dir", default=".i11-evidence")
    parser.add_argument("--snapshot-file")
    parser.add_argument("--snapshot-status-file")
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    if args.mode == "seed":
        seed(output_dir)
        return
    if not args.snapshot_file or not args.snapshot_status_file:
        raise RuntimeError("recover requires snapshot file and snapshot status file")
    recover(
        output_dir,
        Path(args.snapshot_file).resolve(),
        Path(args.snapshot_status_file).resolve(),
    )


if __name__ == "__main__":
    main()
