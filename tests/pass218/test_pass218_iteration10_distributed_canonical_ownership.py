from __future__ import annotations

import ast
from hashlib import sha256
import json
import os
from pathlib import Path
import time

import pytest
from fastapi import FastAPI

from hhs_backend.runtime_os_pass218_lifecycle import install_pass218_runtime_os_lifecycle
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    DISTRIBUTED_AUTHORITY_SCOPE,
    DISTRIBUTED_CHECKPOINT_RECORD_SCHEMA,
    DISTRIBUTED_CONSENSUS_BACKEND,
    DISTRIBUTED_LIFECYCLE_STATUS_SCHEMA,
    DISTRIBUTED_OWNERSHIP_RECORD_SCHEMA,
    PASS218_DISTRIBUTED_LIFECYCLE_VERSION,
    PASS218_DISTRIBUTED_OWNERSHIP_VERSION,
    Pass217VM81CanonicalTarget,
    Pass218DistributedCheckpointConflict,
    Pass218DistributedOwnershipFenceLost,
    Pass218DistributedOwnershipUnavailable,
    Pass218DistributedOwnershipValidationError,
    Pass218DistributedRuntimeLifecycle,
    Pass218EtcdDistributedAuthority,
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
    Pass218MultiprocessRuntimeLifecycle,
    Pass218RuntimeLifecycleError,
    Pass218RuntimeLifecycleNotReady,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    seal_distributed_checkpoint_record,
    seal_distributed_ownership_record,
    validate_distributed_checkpoint_record,
    validate_distributed_ownership_record,
)

ROOT = Path(__file__).resolve().parents[2]
ETCD_ENDPOINT = os.environ.get("HHS_PASS218_I10_ETCD_TEST_ENDPOINT", "").strip()
ETCD_NAMESPACE = os.environ.get(
    "HHS_PASS218_I10_ETCD_TEST_NAMESPACE",
    "/hhs/pass218/i10/pytest",
).rstrip("/")


def _source(label: str = "A") -> str:
    return (
        "A synthetic narrative exists only to test Iteration 10 distributed fencing "
        f"{label}. It must never be retained. A second sentence ensures a "
        "non-empty deterministic structural projection."
    )


def _beat(ordinal: int, label: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "ordinal": ordinal,
        "source_span_sha256": sha256(
            f"iteration10-span-{ordinal}-{label}".encode("utf-8")
        ).hexdigest(),
        "paragraph_count": 1,
        "token_count": 23 + ordinal,
        "sentence_count": 1,
        "dialogue_turn_count": ordinal % 2,
        "perspective_counts": {"first_person": 0, "second_person": 0, "third_person": 1},
        "negation_count": 1,
        "modal_count": 1,
        "authority_count": 1,
        "temporal_count": 1,
        "dominant_perspective": "THIRD_PERSON",
        "relation_types": ["TEMPORAL_SUCCESSION"],
        "distinction_mentions": [],
        "verbatim_source_retained": False,
    }
    payload["beat_hash72"] = hash72_digest(
        {"domain": "HHS-P218-NARRATIVE-BEAT-I2-V1"}, payload
    )
    return payload


def _hydration(label: str = "A") -> dict[str, object]:
    source = _source(label)
    genesis = hash72_digest({"domain": "P218-I10-TEST-GENESIS"}, label.encode())
    hydration = hash72_digest({"domain": "P218-I10-TEST-HYDRATION"}, label.encode())
    validation = hash72_digest({"domain": "P218-I10-TEST-VALIDATION"}, label.encode())
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "hydrator_version": "HHS-P218-NARRATIVE-HYDRATOR-I2-V1",
        "source_id": f"iteration10-{label}",
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "source_epistemic_class": "FICTIONAL_COUNTERFACTUAL",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest(
            {"domain": "P218-I10-TEST-GRAMMAR"}, label.encode()
        ),
        "beats": [_beat(index, label) for index in range(4)],
        "hydration_hash72": hydration,
        "validation_hash72": validation,
        "hash216": genesis + hydration + validation,
        "hash216_semantics": [
            "PREVIOUS_GENESIS_STATE",
            "NEXT_HYDRATION_CANDIDATE",
            "VALIDATION_RECEIPT",
        ],
        "verbatim_source_retained": False,
        "source_text_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "authoritative_vector_store_promotion": False,
        "authoritative_float_weights": False,
    }


def _authorized(label: str = "A", *, sequence: int = 1):
    source = _source(label)
    transaction = SourceTransaction.begin(_hydration(label), source)
    transaction.commit_and_purge()
    snapshot = transaction.snapshot()
    staged = ClosedTransactionVectorVM5184Adapter().stage(snapshot)
    proof = PromotionProofMembrane().prove(
        closed_transaction_snapshot=snapshot,
        staged_candidate=staged,
    )
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=hash72_digest(
            {"domain": "P218-I10-TEST-GRANTOR"}, f"authority-{label}".encode()
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return staged, journal, authorization


def _prepare(lifecycle, label: str = "A", *, sequence: int = 1):
    staged, journal, authorization = _authorized(label, sequence=sequence)
    boundary = lifecycle.canonical_boundary()
    prepared = boundary.prepare(
        authorization=authorization,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    return prepared, journal, authorization


def _commit(lifecycle, label: str = "A", *, sequence: int = 1):
    prepared, journal, authorization = _prepare(lifecycle, label, sequence=sequence)
    result = lifecycle.commit_prepared(prepared, authorization_journal=journal)
    return result, authorization, prepared, journal


def _authority(
    harness: Pass218InMemoryConsensusHarness,
    owner: str,
    host: str,
) -> Pass218InMemoryDistributedAuthority:
    return Pass218InMemoryDistributedAuthority(
        harness,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=9,
    )


class _FailOncePublishAuthority(Pass218InMemoryDistributedAuthority):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_next_publish = False

    def publish_checkpoint(self, checkpoint, *, expected_previous_checkpoint_sha256):
        if self.fail_next_publish:
            self.fail_next_publish = False
            raise Pass218DistributedOwnershipUnavailable(
                "P218_I10_TEST_INJECTED_PUBLICATION_PARTITION"
            )
        return super().publish_checkpoint(
            checkpoint,
            expected_previous_checkpoint_sha256=expected_previous_checkpoint_sha256,
        )


def test_iteration10_declares_distributed_contract() -> None:
    assert PASS218_DISTRIBUTED_OWNERSHIP_VERSION == "HHS-P218-DISTRIBUTED-CANONICAL-OWNERSHIP-I10-V1"
    assert DISTRIBUTED_OWNERSHIP_RECORD_SCHEMA == "HHS-P218-I10-DISTRIBUTED-OWNERSHIP-RECORD-V1"
    assert DISTRIBUTED_CHECKPOINT_RECORD_SCHEMA == "HHS-P218-I10-DISTRIBUTED-CANONICAL-CHECKPOINT-V1"
    assert DISTRIBUTED_AUTHORITY_SCOPE == "ETCD_V3_LINEARIZABLE_LEASE_CAS"
    assert DISTRIBUTED_CONSENSUS_BACKEND == "ETCD_V3"
    assert PASS218_DISTRIBUTED_LIFECYCLE_VERSION == "HHS-P218-DISTRIBUTED-RUNTIME-LIFECYCLE-I10-V1"
    assert DISTRIBUTED_LIFECYCLE_STATUS_SCHEMA == "HHS-P218-I10-DISTRIBUTED-LIFECYCLE-STATUS-V1"


def test_first_distributed_owner_acquires_global_fence_one() -> None:
    harness = Pass218InMemoryConsensusHarness()
    authority = _authority(harness, "owner-a", "host-a")
    record = authority.acquire()
    assert record is not None
    assert record["fence_epoch"] == 1
    assert record["previous_fence_epoch"] == 0
    assert record["previous_owner_id"] is None
    assert record["previous_host_id"] is None
    assert validate_distributed_ownership_record(record) == record


def test_concurrent_remote_host_is_standby() -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = _authority(harness, "owner-a", "host-a")
    second = _authority(harness, "owner-b", "host-b")
    assert first.acquire() is not None
    assert second.acquire() is None


def test_expired_remote_owner_advances_global_fence_and_links_host() -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = _authority(harness, "owner-a", "host-a")
    second = _authority(harness, "owner-b", "host-b")
    assert first.acquire()["fence_epoch"] == 1
    harness.expire_owner()
    takeover = second.acquire()
    assert takeover is not None
    assert takeover["fence_epoch"] == 2
    assert takeover["previous_fence_epoch"] == 1
    assert takeover["previous_owner_id"] == "owner-a"
    assert takeover["previous_host_id"] == "host-a"
    with pytest.raises(Pass218DistributedOwnershipFenceLost):
        first.assert_current()


def test_partition_is_fail_closed() -> None:
    harness = Pass218InMemoryConsensusHarness()
    authority = _authority(harness, "owner-a", "host-a")
    authority.acquire()
    harness.set_available(False)
    with pytest.raises(Pass218DistributedOwnershipUnavailable):
        authority.assert_current()
    assert authority.held is False


def test_tampered_ownership_record_is_rejected() -> None:
    harness = Pass218InMemoryConsensusHarness()
    authority = _authority(harness, "owner-a", "host-a")
    record = authority.acquire()
    tampered = dict(record)
    tampered["host_id"] = "forged-host"
    with pytest.raises(Pass218DistributedOwnershipValidationError):
        validate_distributed_ownership_record(tampered)


def test_distributed_lifecycle_first_host_opens_only_after_both_fences(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    status = lifecycle.startup()
    assert status["state"] == "DISTRIBUTED_EMPTY_READY"
    assert status["ownership_writer_authority"] is True
    assert status["distributed_writer_authority"] is True
    assert status["ownership_fence_epoch"] == 1
    assert status["distributed_fence_epoch"] == 1
    assert status["ingestion_enabled"] is True
    assert status["split_brain_writer_permitted"] is False
    lifecycle.shutdown()


def test_two_hosts_with_unrelated_local_roots_share_one_global_writer(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = Pass218DistributedRuntimeLifecycle(
        tmp_path / "host-a",
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    second = Pass218DistributedRuntimeLifecycle(
        tmp_path / "host-b",
        owner_id="local-b",
        distributed_authority=_authority(harness, "owner-b", "host-b"),
    )
    first_status = first.startup()
    second_status = second.startup()
    assert first_status["distributed_state"] == "PRIMARY"
    assert second_status["state"] == "DISTRIBUTED_OWNERSHIP_STANDBY"
    assert second_status["distributed_writer_authority"] is False
    assert second_status["ingestion_enabled"] is False
    with pytest.raises(Pass218RuntimeLifecycleNotReady):
        second.canonical_boundary()
    first.shutdown()
    second.shutdown()


def test_same_host_still_preserves_iteration9_local_process_exclusion(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    second = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-b",
        distributed_authority=_authority(harness, "owner-b", "host-a"),
    )
    first.startup()
    status = second.startup()
    assert status["state"] == "LOCAL_OWNERSHIP_STANDBY"
    assert status["ownership_writer_authority"] is False
    assert status["distributed_writer_authority"] is False
    first.shutdown()
    second.shutdown()


def test_commit_publishes_sealed_distributed_checkpoint(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    lifecycle.startup()
    result, authorization, _, _ = _commit(lifecycle)
    remote = harness.snapshot()["checkpoint_record"]
    assert remote is not None
    assert validate_distributed_checkpoint_record(remote) == remote
    assert result["distributed_canonical_publication"] is True
    assert result["distributed_checkpoint_sha256"] == remote["checkpoint_sha256"]
    assert result["canonical_root_hash72"] == remote["canonical_root_hash72"]
    assert lifecycle.target.committed_receipt(authorization["authorization_hash72"]) is not None
    lifecycle.shutdown()


def test_cross_host_takeover_restores_exact_root_snapshot_and_i6_receipt(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = Pass218DistributedRuntimeLifecycle(
        tmp_path / "host-a",
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    first.startup()
    result, authorization, _, _ = _commit(first)
    root = first.target.root_hash72()
    snapshot = first.target.snapshot_bytes()
    receipt = result["canonical_receipt"]

    harness.expire_owner()
    second = Pass218DistributedRuntimeLifecycle(
        tmp_path / "host-b",
        owner_id="local-b",
        distributed_authority=_authority(harness, "owner-b", "host-b"),
    )
    status = second.startup()
    assert status["state"] == "DISTRIBUTED_RESTORED_READY"
    assert status["distributed_fence_epoch"] == 2
    assert second.target.root_hash72() == root
    assert second.target.snapshot_bytes() == snapshot
    assert second.target.committed_receipt(authorization["authorization_hash72"]) == receipt
    assert status["restart_new_authorization_minted"] is False
    assert status["restart_new_canonical_mutation_invoked"] is False
    with pytest.raises(Pass218RuntimeLifecycleNotReady):
        first.canonical_boundary()
    second.shutdown()
    first.shutdown()


def test_partition_closes_lifecycle_ingress_immediately(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    lifecycle.startup()
    harness.set_available(False)
    with pytest.raises(Pass218RuntimeLifecycleNotReady):
        lifecycle.require_ingestion_ready()
    assert lifecycle.status()["ingestion_enabled"] is False
    harness.set_available(True)
    lifecycle.shutdown()


def test_failed_global_publication_rolls_back_local_commit_and_keeps_authorization_retryable(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    authority = _FailOncePublishAuthority(
        harness,
        owner_id="owner-a",
        host_id="host-a",
        lease_ttl_seconds=9,
    )
    lifecycle = Pass218DistributedRuntimeLifecycle(
        tmp_path / "host-a",
        owner_id="local-a",
        distributed_authority=authority,
    )
    lifecycle.startup()
    prepared, journal, authorization = _prepare(lifecycle)
    empty_root = lifecycle.target.root_hash72()
    authority.fail_next_publish = True
    with pytest.raises(
        Pass218RuntimeLifecycleError,
        match="P218_I10_DISTRIBUTED_CANONICAL_PUBLICATION_FAILED",
    ):
        lifecycle.commit_prepared(prepared, authorization_journal=journal)
    assert lifecycle.target.root_hash72() == empty_root
    assert lifecycle.target.record()["canonical_commit_count"] == 0
    assert not lifecycle.store.manifest_path.exists()
    assert journal.mutation_precondition(
        authorization["authorization_hash72"],
        entry_id_sha256=prepared.candidate_entry["entry_id_sha256"],
        projection_sha256=authorization["projection_sha256"],
    ) is True
    assert harness.snapshot()["checkpoint_record"] is None
    lifecycle.shutdown()


def test_same_prepared_authorization_can_retry_on_successor_after_failed_publication(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    failing = _FailOncePublishAuthority(
        harness,
        owner_id="owner-a",
        host_id="host-a",
        lease_ttl_seconds=9,
    )
    first = Pass218DistributedRuntimeLifecycle(
        tmp_path / "host-a",
        owner_id="local-a",
        distributed_authority=failing,
    )
    first.startup()
    prepared, journal, authorization = _prepare(first)
    failing.fail_next_publish = True
    with pytest.raises(Pass218RuntimeLifecycleError):
        first.commit_prepared(prepared, authorization_journal=journal)

    replacement = Pass218DistributedRuntimeLifecycle(
        tmp_path / "host-b",
        owner_id="local-b",
        distributed_authority=_authority(harness, "owner-b", "host-b"),
    )
    status = replacement.startup()
    assert status["distributed_fence_epoch"] == 2
    result = replacement.commit_prepared(prepared, authorization_journal=journal)
    assert result["distributed_canonical_publication"] is True
    assert replacement.target.committed_receipt(authorization["authorization_hash72"]) is not None
    replacement.shutdown()
    first.shutdown()


def test_checkpoint_predecessor_cas_rejects_stale_writer(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    lifecycle.startup()
    _commit(lifecycle)
    checkpoint = lifecycle.store.restore().checkpoint
    with pytest.raises(Pass218DistributedCheckpointConflict):
        lifecycle.distributed.publish_checkpoint(
            checkpoint,
            expected_previous_checkpoint_sha256=None,
        )
    lifecycle.shutdown()


def test_distributed_checkpoint_tamper_is_rejected(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    lifecycle.startup()
    _commit(lifecycle)
    record = harness.snapshot()["checkpoint_record"]
    tampered = dict(record)
    tampered["canonical_root_hash72"] = Pass217VM81CanonicalTarget().root_hash72()
    with pytest.raises(Pass218DistributedOwnershipValidationError):
        validate_distributed_checkpoint_record(tampered)
    lifecycle.shutdown()


def test_iteration9_canonical_state_bootstraps_once_into_distributed_authority(tmp_path: Path) -> None:
    local = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="legacy-local")
    local.startup()
    _commit(local, label="legacy")
    root = local.target.root_hash72()
    snapshot = local.target.snapshot_bytes()
    local.shutdown()

    harness = Pass218InMemoryConsensusHarness()
    distributed = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="i10-local",
        distributed_authority=_authority(harness, "i10-owner", "host-a"),
    )
    status = distributed.startup()
    assert status["distributed_restore_state"] == "BOOTSTRAPPED_FROM_VALIDATED_I9_CANONICAL_STATE"
    assert status["distributed_checkpoint_root_hash72"] == root
    assert distributed.target.root_hash72() == root
    assert distributed.target.snapshot_bytes() == snapshot
    distributed.shutdown()


def test_source_text_is_absent_from_distributed_authority_bytes(tmp_path: Path) -> None:
    source = _source("source-purge")
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    lifecycle.startup()
    _commit(lifecycle, label="source-purge")
    serialized = json.dumps(
        harness.snapshot(), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    assert source.encode("utf-8") not in serialized
    lifecycle.shutdown()


def test_runtime_os_defaults_to_iteration9_without_distributed_configuration(
    tmp_path: Path,
    monkeypatch,
) -> None:
    for name in (
        "HHS_PASS218_ETCD_ENDPOINT",
        "HHS_PASS218_DISTRIBUTED_REQUIRED",
    ):
        monkeypatch.delenv(name, raising=False)
    app = FastAPI()
    lifecycle = install_pass218_runtime_os_lifecycle(app, state_root=tmp_path)
    assert isinstance(lifecycle, Pass218MultiprocessRuntimeLifecycle)
    assert not isinstance(lifecycle, Pass218DistributedRuntimeLifecycle)


def test_runtime_os_required_without_etcd_is_diagnostic_fail_closed(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("HHS_PASS218_ETCD_ENDPOINT", raising=False)
    monkeypatch.setenv("HHS_PASS218_DISTRIBUTED_REQUIRED", "1")
    app = FastAPI()
    lifecycle = install_pass218_runtime_os_lifecycle(app, state_root=tmp_path)
    assert isinstance(lifecycle, Pass218DistributedRuntimeLifecycle)
    status = lifecycle.startup()
    assert status["state"] == "DISTRIBUTED_AUTHORITY_UNAVAILABLE"
    assert status["ingestion_enabled"] is False
    assert status["distributed_writer_authority"] is False
    lifecycle.shutdown()


def test_distributed_status_mints_no_learning_truth_or_action_authority(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = Pass218DistributedRuntimeLifecycle(
        tmp_path,
        owner_id="local-a",
        distributed_authority=_authority(harness, "owner-a", "host-a"),
    )
    status = lifecycle.startup()
    assert status["canonical_learning_commit_invoked"] is False
    assert status["truth_promotion"] is False
    assert status["action_authority_minted"] is False
    assert status["verbatim_source_retained"] is False
    assert status["pass165_source_retaining_path_invoked"] is False
    lifecycle.shutdown()


def test_iteration10_surfaces_do_not_import_pass165() -> None:
    for relative in (
        "hhs_runtime/pass218/distributed_ownership.py",
        "hhs_runtime/pass218/lifecycle_i10.py",
    ):
        text = (ROOT / relative).read_text("utf-8")
        assert "pass165" not in "\n".join(
            line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))
        ).lower()


def test_iteration10_authority_surfaces_contain_no_float_literals() -> None:
    for relative in (
        "hhs_runtime/pass218/distributed_ownership.py",
        "hhs_runtime/pass218/lifecycle_i10.py",
        "hhs_runtime/pass218/lifecycle_i9.py",
        "hhs_backend/runtime_os_pass218_lifecycle.py",
    ):
        tree = ast.parse((ROOT / relative).read_text("utf-8"))
        floats = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, relative


@pytest.mark.skipif(not ETCD_ENDPOINT, reason="real etcd endpoint not configured")
def test_real_etcd_v3_acquire_busy_release_takeover() -> None:
    namespace = ETCD_NAMESPACE + "/acquire"
    first = Pass218EtcdDistributedAuthority(
        ETCD_ENDPOINT,
        namespace=namespace,
        owner_id="real-owner-a",
        host_id="real-host-a",
        lease_ttl_seconds=6,
    )
    second = Pass218EtcdDistributedAuthority(
        ETCD_ENDPOINT,
        namespace=namespace,
        owner_id="real-owner-b",
        host_id="real-host-b",
        lease_ttl_seconds=6,
    )
    record = first.acquire()
    assert record is not None and record["fence_epoch"] == 1
    assert second.acquire() is None
    first.release()
    takeover = second.acquire()
    assert takeover is not None
    assert takeover["fence_epoch"] == 2
    assert takeover["previous_owner_id"] == "real-owner-a"
    assert takeover["previous_host_id"] == "real-host-a"
    second.release()


@pytest.mark.skipif(not ETCD_ENDPOINT, reason="real etcd endpoint not configured")
def test_real_etcd_keepalive_preserves_current_owner() -> None:
    authority = Pass218EtcdDistributedAuthority(
        ETCD_ENDPOINT,
        namespace=ETCD_NAMESPACE + "/keepalive",
        owner_id="keepalive-owner",
        host_id="keepalive-host",
        lease_ttl_seconds=6,
    )
    assert authority.acquire() is not None
    renewed = authority.renew()
    assert renewed["fence_epoch"] == 1
    authority.release()


@pytest.mark.skipif(not ETCD_ENDPOINT, reason="real etcd endpoint not configured")
def test_real_etcd_lease_expiry_rejects_stale_owner_and_advances_fence() -> None:
    namespace = ETCD_NAMESPACE + "/expiry"
    first = Pass218EtcdDistributedAuthority(
        ETCD_ENDPOINT,
        namespace=namespace,
        owner_id="expiry-owner-a",
        host_id="expiry-host-a",
        lease_ttl_seconds=2,
    )
    second = Pass218EtcdDistributedAuthority(
        ETCD_ENDPOINT,
        namespace=namespace,
        owner_id="expiry-owner-b",
        host_id="expiry-host-b",
        lease_ttl_seconds=6,
    )
    assert first.acquire()["fence_epoch"] == 1
    takeover = None
    for _ in range(6):
        time.sleep(1)
        takeover = second.acquire()
        if takeover is not None:
            break
    assert takeover is not None
    assert takeover["fence_epoch"] == 2
    with pytest.raises(Pass218DistributedOwnershipFenceLost):
        first.assert_current()
    second.release()
