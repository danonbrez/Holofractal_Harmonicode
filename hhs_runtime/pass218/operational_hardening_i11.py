"""Pass 218 Iteration 11 distributed operational hardening.

Iteration 10 established the canonical cross-host writer contract: a process must
hold both the local I9 fence and an etcd-v3 lease/CAS fence. Iteration 11 keeps
that protocol frozen and adds production operational requirements around it:

* an odd, multi-member etcd endpoint set;
* mandatory TLS server verification and client-certificate authentication;
* endpoint failover without weakening linearizable etcd semantics;
* member/cluster identity and quorum probes;
* fail-closed quorum readiness suitable for Runtime-OS lifecycle gating; and
* a sealed disaster-recovery manifest binding an etcd snapshot to the exact
  distributed I10 canonical checkpoint that must be reconstructed after restore.

This module does not implement consensus and does not change I10 ownership or
checkpoint schemas. It consumes etcd consensus and wraps its operational state
with exact HHS validation. No source text, Pass-165 learning, truth promotion,
action authority, or floating-point authority is admitted here.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.commit_boundary import (
    Pass217VM81CanonicalTarget,
    _canonical_bytes,
    _copy,
    _reject_retained_source_surface,
)
from hhs_runtime.pass218.distributed_ownership import (
    DISTRIBUTED_AUTHORITY_SCOPE,
    DEFAULT_ETCD_ACQUIRE_ATTEMPTS,
    DEFAULT_ETCD_LEASE_TTL_SECONDS,
    DEFAULT_ETCD_NAMESPACE,
    DEFAULT_ETCD_TIMEOUT_SECONDS,
    EtcdV3HTTPClient,
    Pass218DistributedOwnershipError,
    Pass218DistributedOwnershipUnavailable,
    Pass218DistributedOwnershipValidationError,
    Pass218EtcdDistributedAuthority,
    target_from_distributed_checkpoint,
    validate_distributed_checkpoint_record,
)

PASS218_OPERATIONAL_HARDENING_VERSION = "HHS-P218-DISTRIBUTED-OPERATIONAL-HARDENING-I11-V1"
OPERATIONAL_AUTHORITY_SCOPE = "ETCD_V3_MULTI_MEMBER_MTLS_QUORUM"
OPERATIONAL_CLUSTER_BACKEND = "ETCD_V3_CLUSTER_MTLS"
CLUSTER_PROBE_SCHEMA = "HHS-P218-I11-ETCD-CLUSTER-PROBE-V1"
DISASTER_RECOVERY_MANIFEST_SCHEMA = "HHS-P218-I11-DISASTER-RECOVERY-MANIFEST-V1"
DEFAULT_CLUSTER_NAME = "hhs-pass218"
MINIMUM_PRODUCTION_MEMBER_COUNT = 3


class Pass218OperationalHardeningError(RuntimeError):
    pass


class Pass218OperationalConfigurationError(Pass218OperationalHardeningError):
    pass


class Pass218OperationalQuorumUnavailable(Pass218OperationalHardeningError):
    pass


class Pass218OperationalIdentityMismatch(Pass218OperationalHardeningError):
    pass


class Pass218DisasterRecoveryValidationError(Pass218OperationalHardeningError):
    pass


def _require_nonnegative_int(value: Any, *, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Pass218OperationalConfigurationError(code)
    return value


def _require_positive_int(value: Any, *, code: str) -> int:
    result = _require_nonnegative_int(value, code=code)
    if result < 1:
        raise Pass218OperationalConfigurationError(code)
    return result


def _require_identifier(value: Any, *, code: str, maximum: int = 256) -> str:
    if not isinstance(value, str):
        raise Pass218OperationalConfigurationError(code)
    normalized = value.strip()
    if not normalized or len(normalized) > maximum:
        raise Pass218OperationalConfigurationError(code)
    return normalized


def _require_sha256(value: Any, *, code: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise Pass218DisasterRecoveryValidationError(code)
    return value


def _require_existing_file(value: str | Path, *, code: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise Pass218OperationalConfigurationError(code)
    return path


def _normalize_endpoint(endpoint: Any) -> str:
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise Pass218OperationalConfigurationError("P218_I11_ETCD_ENDPOINT_INVALID")
    normalized = endpoint.strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme != "https" or not parsed.netloc:
        raise Pass218OperationalConfigurationError(
            "P218_I11_ETCD_HTTPS_ENDPOINT_REQUIRED"
        )
    return normalized


def _parse_numeric(value: Any, *, code: str) -> int:
    if isinstance(value, bool):
        raise Pass218OperationalIdentityMismatch(code)
    if isinstance(value, int):
        return _require_nonnegative_int(value, code=code)
    if isinstance(value, str) and value and value.isdigit():
        return int(value)
    raise Pass218OperationalIdentityMismatch(code)


@dataclass(frozen=True)
class Pass218EtcdClusterConfig:
    """Validated production cluster transport and identity configuration."""

    endpoints: tuple[str, ...]
    ca_file: Path
    client_cert_file: Path
    client_key_file: Path
    cluster_name: str = DEFAULT_CLUSTER_NAME
    timeout_seconds: int = DEFAULT_ETCD_TIMEOUT_SECONDS

    @classmethod
    def build(
        cls,
        endpoints: Sequence[str],
        *,
        ca_file: str | Path,
        client_cert_file: str | Path,
        client_key_file: str | Path,
        cluster_name: str = DEFAULT_CLUSTER_NAME,
        timeout_seconds: int = DEFAULT_ETCD_TIMEOUT_SECONDS,
    ) -> "Pass218EtcdClusterConfig":
        normalized = tuple(_normalize_endpoint(value) for value in endpoints)
        if len(normalized) < MINIMUM_PRODUCTION_MEMBER_COUNT:
            raise Pass218OperationalConfigurationError(
                "P218_I11_ETCD_CLUSTER_REQUIRES_AT_LEAST_THREE_MEMBERS"
            )
        if len(normalized) % 2 == 0:
            raise Pass218OperationalConfigurationError(
                "P218_I11_ETCD_CLUSTER_REQUIRES_ODD_MEMBER_COUNT"
            )
        if len(set(normalized)) != len(normalized):
            raise Pass218OperationalConfigurationError(
                "P218_I11_ETCD_CLUSTER_ENDPOINTS_NOT_UNIQUE"
            )
        return cls(
            endpoints=normalized,
            ca_file=_require_existing_file(
                ca_file, code="P218_I11_ETCD_CA_FILE_REQUIRED"
            ),
            client_cert_file=_require_existing_file(
                client_cert_file,
                code="P218_I11_ETCD_CLIENT_CERT_FILE_REQUIRED",
            ),
            client_key_file=_require_existing_file(
                client_key_file,
                code="P218_I11_ETCD_CLIENT_KEY_FILE_REQUIRED",
            ),
            cluster_name=_require_identifier(
                cluster_name, code="P218_I11_ETCD_CLUSTER_NAME_INVALID"
            ),
            timeout_seconds=_require_positive_int(
                timeout_seconds, code="P218_I11_ETCD_TIMEOUT_INVALID"
            ),
        )

    @property
    def member_count(self) -> int:
        return len(self.endpoints)

    @property
    def quorum_size(self) -> int:
        return self.member_count // 2 + 1

    def diagnostic_record(self) -> dict[str, Any]:
        return {
            "cluster_name": self.cluster_name,
            "member_count": self.member_count,
            "quorum_size": self.quorum_size,
            "endpoints": list(self.endpoints),
            "tls_server_verification_required": True,
            "client_certificate_authentication_required": True,
        }


class EtcdV3MutualTLSEndpointPoolClient(EtcdV3HTTPClient):
    """I10-compatible etcd client with mTLS and bounded endpoint failover.

    Each underlying request is still a normal etcd v3 linearizable operation.
    Endpoint failover only chooses another member through which to submit that
    request; it never treats member-local availability as canonical authority.
    """

    def __init__(
        self,
        config: Pass218EtcdClusterConfig,
        *,
        authorization: str | None = None,
    ) -> None:
        self.cluster_config = config
        self._clients: list[EtcdV3HTTPClient] = []
        for endpoint in config.endpoints:
            client = EtcdV3HTTPClient(
                endpoint,
                timeout_seconds=config.timeout_seconds,
                authorization=authorization,
                ca_file=config.ca_file,
            )
            if client._ssl_context is None:
                raise Pass218OperationalConfigurationError(
                    "P218_I11_ETCD_TLS_CONTEXT_REQUIRED"
                )
            try:
                client._ssl_context.load_cert_chain(
                    certfile=str(config.client_cert_file),
                    keyfile=str(config.client_key_file),
                )
            except Exception as exc:
                raise Pass218OperationalConfigurationError(
                    "P218_I11_ETCD_CLIENT_CERTIFICATE_INVALID"
                ) from exc
            self._clients.append(client)
        self._endpoint_lock = RLock()
        self._preferred_index = 0
        self._last_successful_endpoint: str | None = None
        # Initialize inherited helpers; _request is overridden below.
        super().__init__(
            config.endpoints[0],
            timeout_seconds=config.timeout_seconds,
            authorization=authorization,
            ca_file=config.ca_file,
        )

    @property
    def last_successful_endpoint(self) -> str | None:
        with self._endpoint_lock:
            return self._last_successful_endpoint

    def _ordered_clients(self) -> list[tuple[int, EtcdV3HTTPClient]]:
        with self._endpoint_lock:
            start = self._preferred_index
        count = len(self._clients)
        return [((start + offset) % count, self._clients[(start + offset) % count]) for offset in range(count)]

    def _request(
        self,
        path: str,
        payload: Mapping[str, Any],
        *,
        first_stream_line: bool = False,
    ) -> dict[str, Any]:
        last_error: BaseException | None = None
        for index, client in self._ordered_clients():
            try:
                result = client._request(
                    path,
                    payload,
                    first_stream_line=first_stream_line,
                )
            except Pass218DistributedOwnershipUnavailable as exc:
                last_error = exc
                continue
            with self._endpoint_lock:
                self._preferred_index = index
                self._last_successful_endpoint = client.endpoint
            return result
        raise Pass218DistributedOwnershipUnavailable(
            "P218_I11_ETCD_CLUSTER_TRANSPORT_UNAVAILABLE"
        ) from last_error

    def request_from_member(
        self,
        endpoint: str,
        path: str,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        normalized = _normalize_endpoint(endpoint)
        for client in self._clients:
            if client.endpoint == normalized:
                return client._request(path, payload)
        raise Pass218OperationalConfigurationError(
            "P218_I11_ETCD_MEMBER_ENDPOINT_NOT_CONFIGURED"
        )


class Pass218EtcdClusterAuthority(Pass218EtcdDistributedAuthority):
    """I10 canonical authority transported through an I11 mTLS endpoint pool."""

    backend_name = OPERATIONAL_CLUSTER_BACKEND
    authority_scope = DISTRIBUTED_AUTHORITY_SCOPE
    operational_authority_scope = OPERATIONAL_AUTHORITY_SCOPE

    def __init__(
        self,
        config: Pass218EtcdClusterConfig,
        *,
        namespace: str = DEFAULT_ETCD_NAMESPACE,
        owner_id: str | None = None,
        host_id: str | None = None,
        lease_ttl_seconds: int = DEFAULT_ETCD_LEASE_TTL_SECONDS,
        authorization: str | None = None,
        acquire_attempts: int = DEFAULT_ETCD_ACQUIRE_ATTEMPTS,
    ) -> None:
        super().__init__(
            config.endpoints[0],
            namespace=namespace,
            owner_id=owner_id,
            host_id=host_id,
            lease_ttl_seconds=lease_ttl_seconds,
            timeout_seconds=config.timeout_seconds,
            authorization=authorization,
            ca_file=config.ca_file,
            acquire_attempts=acquire_attempts,
        )
        self.cluster_config = config
        self.client = EtcdV3MutualTLSEndpointPoolClient(
            config,
            authorization=authorization,
        )


class Pass218EtcdClusterMonitor:
    """Exact diagnostic quorum/identity probe for an I11 etcd cluster."""

    def __init__(
        self,
        config: Pass218EtcdClusterConfig,
        client: EtcdV3MutualTLSEndpointPoolClient,
        *,
        namespace: str = DEFAULT_ETCD_NAMESPACE,
    ) -> None:
        self.config = config
        self.client = client
        if (
            not isinstance(namespace, str)
            or not namespace.startswith("/")
            or namespace.endswith("/")
        ):
            raise Pass218OperationalConfigurationError(
                "P218_I11_ETCD_NAMESPACE_INVALID"
            )
        self.namespace = namespace
        self._lock = RLock()
        self._probe_sequence = 0
        self._last_probe: dict[str, Any] | None = None

    @property
    def last_probe(self) -> dict[str, Any] | None:
        with self._lock:
            return None if self._last_probe is None else _copy(self._last_probe)

    def _member_status(self, endpoint: str) -> dict[str, Any]:
        response = self.client.request_from_member(
            endpoint,
            "/v3/maintenance/status",
            {},
        )
        header = response.get("header")
        if not isinstance(header, Mapping):
            raise Pass218OperationalIdentityMismatch(
                "P218_I11_ETCD_STATUS_HEADER_INVALID"
            )
        cluster_id = _parse_numeric(
            header.get("cluster_id"), code="P218_I11_ETCD_CLUSTER_ID_INVALID"
        )
        member_id = _parse_numeric(
            header.get("member_id"), code="P218_I11_ETCD_MEMBER_ID_INVALID"
        )
        leader_id = _parse_numeric(
            response.get("leader", 0), code="P218_I11_ETCD_LEADER_ID_INVALID"
        )
        if cluster_id < 1 or member_id < 1:
            raise Pass218OperationalIdentityMismatch(
                "P218_I11_ETCD_MEMBER_IDENTITY_ZERO"
            )
        return {
            "endpoint": endpoint,
            "cluster_id": cluster_id,
            "member_id": member_id,
            "leader_id": leader_id,
            "version": str(response.get("version") or ""),
            "raft_term": _parse_numeric(
                response.get("raftTerm", 0), code="P218_I11_ETCD_RAFT_TERM_INVALID"
            ),
            "raft_index": _parse_numeric(
                response.get("raftIndex", 0), code="P218_I11_ETCD_RAFT_INDEX_INVALID"
            ),
        }

    def probe(self) -> dict[str, Any]:
        members: list[dict[str, Any]] = []
        unavailable: list[str] = []
        invalid_identity = False
        for endpoint in self.config.endpoints:
            try:
                members.append(self._member_status(endpoint))
            except Pass218DistributedOwnershipError:
                unavailable.append(endpoint)
            except Pass218OperationalIdentityMismatch:
                invalid_identity = True
                unavailable.append(endpoint)

        cluster_ids = sorted({int(member["cluster_id"]) for member in members})
        member_ids = sorted({int(member["member_id"]) for member in members})
        leader_ids = sorted(
            {int(member["leader_id"]) for member in members if int(member["leader_id"]) > 0}
        )
        identity_consistent = (
            not invalid_identity
            and bool(members)
            and len(cluster_ids) == 1
            and len(member_ids) == len(members)
        )
        member_quorum_reachable = len(members) >= self.config.quorum_size
        linearizable_read_ready = False
        if identity_consistent and member_quorum_reachable:
            try:
                self.client.range_value((self.namespace + "/fence").encode("utf-8"))
                linearizable_read_ready = True
            except Pass218DistributedOwnershipError:
                linearizable_read_ready = False
        quorum_ready = bool(
            identity_consistent
            and member_quorum_reachable
            and linearizable_read_ready
            and leader_ids
        )
        with self._lock:
            self._probe_sequence += 1
            sequence = self._probe_sequence
        body = {
            "schema": CLUSTER_PROBE_SCHEMA,
            "operational_hardening_version": PASS218_OPERATIONAL_HARDENING_VERSION,
            "operational_authority_scope": OPERATIONAL_AUTHORITY_SCOPE,
            "cluster_name": self.config.cluster_name,
            "probe_sequence": sequence,
            "expected_member_count": self.config.member_count,
            "quorum_size": self.config.quorum_size,
            "reachable_member_count": len(members),
            "unavailable_member_count": len(unavailable),
            "cluster_id": cluster_ids[0] if identity_consistent else None,
            "member_ids": member_ids,
            "leader_ids": leader_ids,
            "identity_consistent": identity_consistent,
            "member_quorum_reachable": member_quorum_reachable,
            "linearizable_read_ready": linearizable_read_ready,
            "quorum_ready": quorum_ready,
            "tls_server_verification_required": True,
            "client_certificate_authentication_required": True,
            "split_brain_writer_permitted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
            "members": members,
            "unavailable_endpoints": unavailable,
        }
        _reject_retained_source_surface(body)
        sealed = {
            **body,
            "probe_hash72": hash72_digest(
                {"domain": "HHS-P218-I11-ETCD-CLUSTER-PROBE-V1"},
                body,
            ),
        }
        with self._lock:
            self._last_probe = _copy(sealed)
        return sealed

    def require_quorum_ready(self) -> dict[str, Any]:
        probe = self.probe()
        if not probe["identity_consistent"]:
            raise Pass218OperationalIdentityMismatch(
                "P218_I11_ETCD_CLUSTER_IDENTITY_MISMATCH"
            )
        if not probe["quorum_ready"]:
            raise Pass218OperationalQuorumUnavailable(
                "P218_I11_ETCD_QUORUM_UNAVAILABLE"
            )
        return probe


def validate_cluster_probe(record: Mapping[str, Any]) -> dict[str, Any]:
    row = _copy(record)
    _reject_retained_source_surface(row)
    supplied = row.pop("probe_hash72", None)
    if not validate_hash72(str(supplied or "")):
        raise Pass218OperationalIdentityMismatch(
            "P218_I11_CLUSTER_PROBE_HASH72_INVALID"
        )
    if row.get("schema") != CLUSTER_PROBE_SCHEMA:
        raise Pass218OperationalIdentityMismatch(
            "P218_I11_CLUSTER_PROBE_SCHEMA_INVALID"
        )
    if row.get("operational_hardening_version") != PASS218_OPERATIONAL_HARDENING_VERSION:
        raise Pass218OperationalIdentityMismatch(
            "P218_I11_CLUSTER_PROBE_VERSION_INVALID"
        )
    expected = hash72_digest(
        {"domain": "HHS-P218-I11-ETCD-CLUSTER-PROBE-V1"},
        row,
    )
    if expected != supplied:
        raise Pass218OperationalIdentityMismatch(
            "P218_I11_CLUSTER_PROBE_HASH72_MISMATCH"
        )
    return {**row, "probe_hash72": supplied}


def seal_disaster_recovery_manifest(
    *,
    cluster_name: str,
    cluster_id: int,
    snapshot_sha256: str,
    snapshot_size_bytes: int,
    snapshot_revision: int,
    snapshot_total_keys: int,
    distributed_checkpoint: Mapping[str, Any],
) -> dict[str, Any]:
    checkpoint = validate_distributed_checkpoint_record(distributed_checkpoint)
    body = {
        "schema": DISASTER_RECOVERY_MANIFEST_SCHEMA,
        "operational_hardening_version": PASS218_OPERATIONAL_HARDENING_VERSION,
        "cluster_name": _require_identifier(
            cluster_name, code="P218_I11_DR_CLUSTER_NAME_INVALID"
        ),
        "cluster_id": _require_positive_int(
            cluster_id, code="P218_I11_DR_CLUSTER_ID_INVALID"
        ),
        "snapshot_sha256": _require_sha256(
            snapshot_sha256, code="P218_I11_DR_SNAPSHOT_SHA256_INVALID"
        ),
        "snapshot_size_bytes": _require_positive_int(
            snapshot_size_bytes, code="P218_I11_DR_SNAPSHOT_SIZE_INVALID"
        ),
        "snapshot_revision": _require_nonnegative_int(
            snapshot_revision, code="P218_I11_DR_SNAPSHOT_REVISION_INVALID"
        ),
        "snapshot_total_keys": _require_nonnegative_int(
            snapshot_total_keys, code="P218_I11_DR_SNAPSHOT_TOTAL_KEYS_INVALID"
        ),
        "distributed_fence_epoch": checkpoint["fence_epoch"],
        "distributed_checkpoint_sha256": checkpoint["checkpoint_sha256"],
        "distributed_checkpoint_hash72": checkpoint["checkpoint_hash72"],
        "distributed_checkpoint_seal_hash72": checkpoint[
            "distributed_checkpoint_hash72"
        ],
        "canonical_root_hash72": checkpoint["canonical_root_hash72"],
        "generation_sequence": checkpoint["generation_sequence"],
        "distributed_checkpoint": checkpoint,
        "restore_requires_new_fence": True,
        "source_text_present": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }
    _reject_retained_source_surface(body)
    return {
        **body,
        "manifest_hash72": hash72_digest(
            {"domain": "HHS-P218-I11-DISASTER-RECOVERY-MANIFEST-V1"},
            body,
        ),
    }


def validate_disaster_recovery_manifest(record: Mapping[str, Any]) -> dict[str, Any]:
    row = _copy(record)
    _reject_retained_source_surface(row)
    if row.get("schema") != DISASTER_RECOVERY_MANIFEST_SCHEMA:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_MANIFEST_SCHEMA_INVALID"
        )
    if row.get("operational_hardening_version") != PASS218_OPERATIONAL_HARDENING_VERSION:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_MANIFEST_VERSION_INVALID"
        )
    checkpoint = validate_distributed_checkpoint_record(
        row.get("distributed_checkpoint", {})
    )
    if row.get("distributed_fence_epoch") != checkpoint["fence_epoch"]:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_FENCE_MISMATCH"
        )
    if row.get("distributed_checkpoint_sha256") != checkpoint["checkpoint_sha256"]:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_CHECKPOINT_SHA256_MISMATCH"
        )
    if row.get("distributed_checkpoint_hash72") != checkpoint["checkpoint_hash72"]:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_CHECKPOINT_HASH72_MISMATCH"
        )
    if row.get("distributed_checkpoint_seal_hash72") != checkpoint[
        "distributed_checkpoint_hash72"
    ]:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_CHECKPOINT_SEAL_MISMATCH"
        )
    if row.get("canonical_root_hash72") != checkpoint["canonical_root_hash72"]:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_CANONICAL_ROOT_MISMATCH"
        )
    if row.get("generation_sequence") != checkpoint["generation_sequence"]:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_GENERATION_SEQUENCE_MISMATCH"
        )
    _require_identifier(row.get("cluster_name"), code="P218_I11_DR_CLUSTER_NAME_INVALID")
    _require_positive_int(row.get("cluster_id"), code="P218_I11_DR_CLUSTER_ID_INVALID")
    _require_sha256(row.get("snapshot_sha256"), code="P218_I11_DR_SNAPSHOT_SHA256_INVALID")
    _require_positive_int(
        row.get("snapshot_size_bytes"), code="P218_I11_DR_SNAPSHOT_SIZE_INVALID"
    )
    _require_nonnegative_int(
        row.get("snapshot_revision"), code="P218_I11_DR_SNAPSHOT_REVISION_INVALID"
    )
    _require_nonnegative_int(
        row.get("snapshot_total_keys"), code="P218_I11_DR_SNAPSHOT_TOTAL_KEYS_INVALID"
    )
    if row.get("restore_requires_new_fence") is not True:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_RESTORE_FENCE_REQUIREMENT_INVALID"
        )
    for key in (
        "source_text_present",
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
    ):
        if row.get(key) is not False:
            raise Pass218DisasterRecoveryValidationError(
                "P218_I11_DR_FORBIDDEN_AUTHORITY_FLAG:" + key
            )
    supplied = row.get("manifest_hash72")
    if not validate_hash72(str(supplied or "")):
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_MANIFEST_HASH72_INVALID"
        )
    body = {key: _copy(value) for key, value in row.items() if key != "manifest_hash72"}
    expected = hash72_digest(
        {"domain": "HHS-P218-I11-DISASTER-RECOVERY-MANIFEST-V1"},
        body,
    )
    if expected != supplied:
        raise Pass218DisasterRecoveryValidationError(
            "P218_I11_DR_MANIFEST_HASH72_MISMATCH"
        )
    return row


def restore_target_from_disaster_recovery_manifest(
    manifest: Mapping[str, Any],
) -> Pass217VM81CanonicalTarget:
    validated = validate_disaster_recovery_manifest(manifest)
    return target_from_distributed_checkpoint(validated["distributed_checkpoint"])


__all__ = [
    "CLUSTER_PROBE_SCHEMA",
    "DEFAULT_CLUSTER_NAME",
    "DISASTER_RECOVERY_MANIFEST_SCHEMA",
    "MINIMUM_PRODUCTION_MEMBER_COUNT",
    "OPERATIONAL_AUTHORITY_SCOPE",
    "OPERATIONAL_CLUSTER_BACKEND",
    "PASS218_OPERATIONAL_HARDENING_VERSION",
    "EtcdV3MutualTLSEndpointPoolClient",
    "Pass218DisasterRecoveryValidationError",
    "Pass218EtcdClusterAuthority",
    "Pass218EtcdClusterConfig",
    "Pass218EtcdClusterMonitor",
    "Pass218OperationalConfigurationError",
    "Pass218OperationalHardeningError",
    "Pass218OperationalIdentityMismatch",
    "Pass218OperationalQuorumUnavailable",
    "restore_target_from_disaster_recovery_manifest",
    "seal_disaster_recovery_manifest",
    "validate_cluster_probe",
    "validate_disaster_recovery_manifest",
]
