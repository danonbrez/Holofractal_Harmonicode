from __future__ import annotations

import ast
from hashlib import sha256
import os
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218 import (
    CLUSTER_PROBE_SCHEMA,
    ClosedTransactionVectorVM5184Adapter,
    DISASTER_RECOVERY_MANIFEST_SCHEMA,
    OPERATIONAL_AUTHORITY_SCOPE,
    OPERATIONAL_CLUSTER_BACKEND,
    OPERATIONAL_LIFECYCLE_STATUS_SCHEMA,
    PASS218_OPERATIONAL_HARDENING_VERSION,
    PASS218_OPERATIONAL_LIFECYCLE_VERSION,
    Pass218DisasterRecoveryValidationError,
    Pass218EtcdClusterConfig,
    Pass218EtcdClusterMonitor,
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
    Pass218OperationalConfigurationError,
    Pass218OperationalIdentityMismatch,
    Pass218OperationallyHardenedRuntimeLifecycle,
    Pass218OperationalQuorumUnavailable,
    Pass218RuntimeLifecycleNotReady,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    restore_target_from_disaster_recovery_manifest,
    seal_disaster_recovery_manifest,
    validate_cluster_probe,
    validate_disaster_recovery_manifest,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218DistributedOwnershipUnavailable,
)
from hhs_runtime.pass218.operational_hardening_i11 import (
    EtcdV3MutualTLSEndpointPoolClient,
    Pass218EtcdClusterAuthority,
)

ROOT = Path(__file__).resolve().parents[2]
REAL_ENDPOINTS = tuple(
    value.strip()
    for value in os.environ.get("HHS_PASS218_I11_ETCD_ENDPOINTS", "").split(",")
    if value.strip()
)
REAL_EXPECT_QUORUM = os.environ.get("HHS_PASS218_I11_EXPECT_QUORUM", "1") == "1"


def _source(label: str = "A") -> str:
    return (
        "A synthetic narrative exists only to test Iteration 11 operational fencing "
        f"{label}. It must never be retained. A second sentence ensures a "
        "non-empty deterministic structural projection."
    )


def _beat(ordinal: int, label: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "ordinal": ordinal,
        "source_span_sha256": sha256(
            f"iteration11-span-{ordinal}-{label}".encode("utf-8")
        ).hexdigest(),
        "paragraph_count": 1,
        "token_count": 31 + ordinal,
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
    genesis = hash72_digest({"domain": "P218-I11-TEST-GENESIS"}, label.encode())
    hydration = hash72_digest({"domain": "P218-I11-TEST-HYDRATION"}, label.encode())
    validation = hash72_digest({"domain": "P218-I11-TEST-VALIDATION"}, label.encode())
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "hydrator_version": "HHS-P218-NARRATIVE-HYDRATOR-I2-V1",
        "source_id": f"iteration11-{label}",
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "source_epistemic_class": "FICTIONAL_COUNTERFACTUAL",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest(
            {"domain": "P218-I11-TEST-GRAMMAR"}, label.encode()
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
            {"domain": "P218-I11-TEST-GRANTOR"}, f"authority-{label}".encode()
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return staged, journal, authorization


def _commit(lifecycle, label: str = "A", *, sequence: int = 1):
    staged, journal, authorization = _authorized(label, sequence=sequence)
    prepared = lifecycle.canonical_boundary().prepare(
        authorization=authorization,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    result = lifecycle.commit_prepared(prepared, authorization_journal=journal)
    return result, authorization


class _FakeClusterClient:
    def __init__(self, statuses: dict[str, dict[str, object]], *, linearizable: bool = True):
        self.statuses = statuses
        self.linearizable = linearizable
        self.last_successful_endpoint = None

    def request_from_member(self, endpoint, path, payload):
        assert path == "/v3/maintenance/status"
        del payload
        value = self.statuses.get(endpoint)
        if value is None:
            raise Pass218DistributedOwnershipUnavailable("P218_I11_TEST_MEMBER_UNAVAILABLE")
        return value

    def range_value(self, key):
        del key
        if not self.linearizable:
            raise Pass218DistributedOwnershipUnavailable("P218_I11_TEST_QUORUM_UNAVAILABLE")
        return None, None


class _Config:
    cluster_name = "test-cluster"
    endpoints = (
        "https://member-a:2379",
        "https://member-b:2379",
        "https://member-c:2379",
    )
    member_count = 3
    quorum_size = 2


def _status(cluster_id: int, member_id: int, leader_id: int = 1):
    return {
        "header": {"cluster_id": str(cluster_id), "member_id": str(member_id)},
        "leader": str(leader_id),
        "version": "3.5.21",
        "raftTerm": "7",
        "raftIndex": "42",
    }


class _FakeMonitor:
    def __init__(self, *, ready: bool = True):
        self.config = _Config()
        self.ready = ready
        self._sequence = 0
        self._last = None

    @property
    def last_probe(self):
        return self._last

    def probe(self):
        self._sequence += 1
        body = {
            "schema": CLUSTER_PROBE_SCHEMA,
            "operational_hardening_version": PASS218_OPERATIONAL_HARDENING_VERSION,
            "operational_authority_scope": OPERATIONAL_AUTHORITY_SCOPE,
            "cluster_name": "test-cluster",
            "probe_sequence": self._sequence,
            "expected_member_count": 3,
            "quorum_size": 2,
            "reachable_member_count": 3 if self.ready else 1,
            "unavailable_member_count": 0 if self.ready else 2,
            "cluster_id": 101 if self.ready else 101,
            "member_ids": [1, 2, 3] if self.ready else [1],
            "leader_ids": [1] if self.ready else [],
            "identity_consistent": True,
            "member_quorum_reachable": self.ready,
            "linearizable_read_ready": self.ready,
            "quorum_ready": self.ready,
            "tls_server_verification_required": True,
            "client_certificate_authentication_required": True,
            "split_brain_writer_permitted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
            "members": [],
            "unavailable_endpoints": [] if self.ready else ["b", "c"],
        }
        self._last = {
            **body,
            "probe_hash72": hash72_digest(
                {"domain": "HHS-P218-I11-ETCD-CLUSTER-PROBE-V1"}, body
            ),
        }
        return self._last

    def require_quorum_ready(self):
        probe = self.probe()
        if not probe["quorum_ready"]:
            raise Pass218OperationalQuorumUnavailable("P218_I11_ETCD_QUORUM_UNAVAILABLE")
        return probe


def _operational_lifecycle(tmp_path, harness, monitor, owner="owner-a", host="host-a"):
    authority = Pass218InMemoryDistributedAuthority(
        harness,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=9,
    )
    return Pass218OperationallyHardenedRuntimeLifecycle(
        tmp_path,
        distributed_authority=authority,
        cluster_monitor=monitor,
        owner_id="local-" + owner,
    )


def test_iteration11_declares_operational_contract() -> None:
    assert PASS218_OPERATIONAL_HARDENING_VERSION == "HHS-P218-DISTRIBUTED-OPERATIONAL-HARDENING-I11-V1"
    assert OPERATIONAL_AUTHORITY_SCOPE == "ETCD_V3_MULTI_MEMBER_MTLS_QUORUM"
    assert OPERATIONAL_CLUSTER_BACKEND == "ETCD_V3_CLUSTER_MTLS"
    assert CLUSTER_PROBE_SCHEMA == "HHS-P218-I11-ETCD-CLUSTER-PROBE-V1"
    assert DISASTER_RECOVERY_MANIFEST_SCHEMA == "HHS-P218-I11-DISASTER-RECOVERY-MANIFEST-V1"
    assert PASS218_OPERATIONAL_LIFECYCLE_VERSION == "HHS-P218-DISTRIBUTED-OPERATIONAL-LIFECYCLE-I11-V1"
    assert OPERATIONAL_LIFECYCLE_STATUS_SCHEMA == "HHS-P218-I11-DISTRIBUTED-OPERATIONAL-LIFECYCLE-STATUS-V1"


def test_cluster_config_requires_three_odd_https_members(tmp_path: Path) -> None:
    ca = tmp_path / "ca.pem"
    cert = tmp_path / "client.pem"
    key = tmp_path / "client-key.pem"
    for path in (ca, cert, key):
        path.write_text("placeholder", encoding="utf-8")
    with pytest.raises(Pass218OperationalConfigurationError):
        Pass218EtcdClusterConfig.build(
            ["https://a:2379", "https://b:2379"],
            ca_file=ca,
            client_cert_file=cert,
            client_key_file=key,
        )
    with pytest.raises(Pass218OperationalConfigurationError):
        Pass218EtcdClusterConfig.build(
            ["http://a:2379", "https://b:2379", "https://c:2379"],
            ca_file=ca,
            client_cert_file=cert,
            client_key_file=key,
        )
    config = Pass218EtcdClusterConfig.build(
        ["https://a:2379", "https://b:2379", "https://c:2379"],
        ca_file=ca,
        client_cert_file=cert,
        client_key_file=key,
    )
    assert config.member_count == 3
    assert config.quorum_size == 2


def test_cluster_config_rejects_duplicate_and_even_members(tmp_path: Path) -> None:
    files = [tmp_path / name for name in ("ca", "cert", "key")]
    for path in files:
        path.write_text("x", encoding="utf-8")
    with pytest.raises(Pass218OperationalConfigurationError):
        Pass218EtcdClusterConfig.build(
            ["https://a:2379", "https://a:2379", "https://c:2379"],
            ca_file=files[0], client_cert_file=files[1], client_key_file=files[2],
        )
    with pytest.raises(Pass218OperationalConfigurationError):
        Pass218EtcdClusterConfig.build(
            [
                "https://a:2379",
                "https://b:2379",
                "https://c:2379",
                "https://d:2379",
            ],
            ca_file=files[0], client_cert_file=files[1], client_key_file=files[2],
        )


def test_probe_requires_identity_majority_leader_and_linearizable_read() -> None:
    statuses = {
        "https://member-a:2379": _status(99, 1),
        "https://member-b:2379": _status(99, 2),
        "https://member-c:2379": _status(99, 3),
    }
    monitor = Pass218EtcdClusterMonitor(_Config(), _FakeClusterClient(statuses), namespace="/x")
    probe = monitor.require_quorum_ready()
    assert probe["quorum_ready"] is True
    assert probe["reachable_member_count"] == 3
    assert probe["member_ids"] == [1, 2, 3]
    assert validate_cluster_probe(probe) == probe


def test_one_member_loss_preserves_three_member_quorum() -> None:
    statuses = {
        "https://member-a:2379": _status(99, 1),
        "https://member-b:2379": _status(99, 2),
    }
    monitor = Pass218EtcdClusterMonitor(_Config(), _FakeClusterClient(statuses), namespace="/x")
    probe = monitor.require_quorum_ready()
    assert probe["reachable_member_count"] == 2
    assert probe["unavailable_member_count"] == 1
    assert probe["quorum_ready"] is True


def test_two_member_loss_blocks_three_member_quorum() -> None:
    statuses = {"https://member-a:2379": _status(99, 1)}
    monitor = Pass218EtcdClusterMonitor(_Config(), _FakeClusterClient(statuses), namespace="/x")
    probe = monitor.probe()
    assert probe["quorum_ready"] is False
    with pytest.raises(Pass218OperationalQuorumUnavailable):
        monitor.require_quorum_ready()


def test_linearizable_failure_blocks_quorum_even_when_members_respond() -> None:
    statuses = {
        "https://member-a:2379": _status(99, 1),
        "https://member-b:2379": _status(99, 2),
        "https://member-c:2379": _status(99, 3),
    }
    monitor = Pass218EtcdClusterMonitor(
        _Config(), _FakeClusterClient(statuses, linearizable=False), namespace="/x"
    )
    assert monitor.probe()["quorum_ready"] is False


def test_cluster_identity_mismatch_is_not_quorum() -> None:
    statuses = {
        "https://member-a:2379": _status(99, 1),
        "https://member-b:2379": _status(100, 2),
        "https://member-c:2379": _status(99, 3),
    }
    monitor = Pass218EtcdClusterMonitor(_Config(), _FakeClusterClient(statuses), namespace="/x")
    probe = monitor.probe()
    assert probe["identity_consistent"] is False
    with pytest.raises(Pass218OperationalIdentityMismatch):
        monitor.require_quorum_ready()


def test_operational_lifecycle_opens_only_with_quorum(tmp_path: Path) -> None:
    lifecycle = _operational_lifecycle(
        tmp_path / "ready",
        Pass218InMemoryConsensusHarness(),
        _FakeMonitor(ready=True),
    )
    status = lifecycle.startup()
    assert status["operational_state"] == "QUORUM_READY"
    assert status["cluster_quorum_ready"] is True
    assert status["ingestion_enabled"] is True
    lifecycle.shutdown()


def test_operational_lifecycle_is_diagnostic_only_without_quorum(tmp_path: Path) -> None:
    lifecycle = _operational_lifecycle(
        tmp_path / "blocked",
        Pass218InMemoryConsensusHarness(),
        _FakeMonitor(ready=False),
    )
    status = lifecycle.startup()
    assert status["state"] == "DISTRIBUTED_OPERATIONAL_QUORUM_BLOCKED"
    assert status["ingestion_enabled"] is False
    assert status["cluster_quorum_ready"] is False
    with pytest.raises(Pass218RuntimeLifecycleNotReady):
        lifecycle.canonical_boundary()
    lifecycle.shutdown()


def test_quorum_loss_revokes_writer_authority(tmp_path: Path) -> None:
    monitor = _FakeMonitor(ready=True)
    lifecycle = _operational_lifecycle(
        tmp_path / "loss",
        Pass218InMemoryConsensusHarness(),
        monitor,
    )
    assert lifecycle.startup()["ingestion_enabled"] is True
    monitor.ready = False
    with pytest.raises(Pass218RuntimeLifecycleNotReady):
        lifecycle.require_ingestion_ready()
    status = lifecycle.status()
    assert status["ingestion_enabled"] is False
    assert status["distributed_writer_authority"] is False
    lifecycle.shutdown()


def test_quorum_recovery_requires_new_distributed_fence(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    first_monitor = _FakeMonitor(ready=True)
    first = _operational_lifecycle(tmp_path / "first", harness, first_monitor, "owner-a", "host-a")
    first_status = first.startup()
    assert first_status["distributed_fence_epoch"] == 1
    first_monitor.ready = False
    with pytest.raises(Pass218RuntimeLifecycleNotReady):
        first.require_ingestion_ready()

    second = _operational_lifecycle(
        tmp_path / "second", harness, _FakeMonitor(ready=True), "owner-b", "host-b"
    )
    second_status = second.startup()
    assert second_status["distributed_fence_epoch"] == 2
    assert second_status["ingestion_enabled"] is True
    second.shutdown()
    first.shutdown()


def test_disaster_recovery_manifest_binds_exact_distributed_checkpoint(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = _operational_lifecycle(
        tmp_path / "dr",
        harness,
        _FakeMonitor(ready=True),
    )
    lifecycle.startup()
    _commit(lifecycle)
    checkpoint = lifecycle.distributed.read_checkpoint()
    assert checkpoint is not None
    manifest = seal_disaster_recovery_manifest(
        cluster_name="test-cluster",
        cluster_id=77,
        snapshot_sha256="a" * 64,
        snapshot_size_bytes=4096,
        snapshot_revision=19,
        snapshot_total_keys=4,
        distributed_checkpoint=checkpoint,
    )
    assert validate_disaster_recovery_manifest(manifest) == manifest
    restored = restore_target_from_disaster_recovery_manifest(manifest)
    assert restored.root_hash72() == lifecycle.target.root_hash72()
    assert restored.snapshot_bytes() == lifecycle.target.snapshot_bytes()
    lifecycle.shutdown()


def test_disaster_recovery_manifest_rejects_snapshot_or_checkpoint_tamper(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    lifecycle = _operational_lifecycle(
        tmp_path / "tamper", harness, _FakeMonitor(ready=True)
    )
    lifecycle.startup()
    _commit(lifecycle)
    checkpoint = lifecycle.distributed.read_checkpoint()
    assert checkpoint is not None
    manifest = seal_disaster_recovery_manifest(
        cluster_name="test-cluster",
        cluster_id=77,
        snapshot_sha256="b" * 64,
        snapshot_size_bytes=8192,
        snapshot_revision=20,
        snapshot_total_keys=5,
        distributed_checkpoint=checkpoint,
    )
    tampered = dict(manifest)
    tampered["snapshot_sha256"] = "c" * 64
    with pytest.raises(Pass218DisasterRecoveryValidationError):
        validate_disaster_recovery_manifest(tampered)
    lifecycle.shutdown()


def test_status_preserves_source_learning_truth_action_exclusions(tmp_path: Path) -> None:
    lifecycle = _operational_lifecycle(
        tmp_path / "status", Pass218InMemoryConsensusHarness(), _FakeMonitor(ready=True)
    )
    status = lifecycle.startup()
    assert status["verbatim_source_retained"] is False
    assert status["pass165_source_retaining_path_invoked"] is False
    assert status["canonical_learning_commit_invoked"] is False
    assert status["truth_promotion"] is False
    assert status["action_authority_minted"] is False
    assert status["split_brain_writer_permitted"] is False
    lifecycle.shutdown()


def test_i11_authority_files_contain_no_float_literals() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "operational_hardening_i11.py",
        ROOT / "hhs_runtime" / "pass218" / "lifecycle_i11.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_lifecycle.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, str(path)


def test_real_three_member_cluster_probe_matches_expected_quorum() -> None:
    if not REAL_ENDPOINTS:
        pytest.skip("real Iteration 11 etcd cluster not configured")
    config = Pass218EtcdClusterConfig.build(
        REAL_ENDPOINTS,
        ca_file=os.environ["HHS_PASS218_I11_ETCD_CA_FILE"],
        client_cert_file=os.environ["HHS_PASS218_I11_ETCD_CLIENT_CERT_FILE"],
        client_key_file=os.environ["HHS_PASS218_I11_ETCD_CLIENT_KEY_FILE"],
        cluster_name="i11-ci-cluster",
        timeout_seconds=2,
    )
    client = EtcdV3MutualTLSEndpointPoolClient(config)
    monitor = Pass218EtcdClusterMonitor(
        config,
        client,
        namespace=os.environ.get("HHS_PASS218_I11_ETCD_NAMESPACE", "/hhs/pass218/i11/pytest"),
    )
    probe = monitor.probe()
    assert probe["quorum_ready"] is REAL_EXPECT_QUORUM
    if REAL_EXPECT_QUORUM:
        assert probe["reachable_member_count"] >= config.quorum_size
        assert probe["identity_consistent"] is True
        assert probe["linearizable_read_ready"] is True
        assert len(probe["member_ids"]) >= config.quorum_size


def test_real_cluster_authority_uses_mtls_endpoint_pool() -> None:
    if not REAL_ENDPOINTS or not REAL_EXPECT_QUORUM:
        pytest.skip("healthy real Iteration 11 etcd cluster not configured")
    config = Pass218EtcdClusterConfig.build(
        REAL_ENDPOINTS,
        ca_file=os.environ["HHS_PASS218_I11_ETCD_CA_FILE"],
        client_cert_file=os.environ["HHS_PASS218_I11_ETCD_CLIENT_CERT_FILE"],
        client_key_file=os.environ["HHS_PASS218_I11_ETCD_CLIENT_KEY_FILE"],
        cluster_name="i11-ci-cluster",
        timeout_seconds=2,
    )
    namespace = os.environ.get("HHS_PASS218_I11_ETCD_NAMESPACE", "/hhs/pass218/i11/pytest") + "/authority"
    authority = Pass218EtcdClusterAuthority(
        config,
        namespace=namespace,
        owner_id="i11-real-owner",
        host_id="i11-real-host",
        lease_ttl_seconds=6,
    )
    record = authority.acquire()
    assert record is not None
    assert record["fence_epoch"] >= 1
    assert authority.assert_current()["ownership_hash72"] == record["ownership_hash72"]
    authority.release()
