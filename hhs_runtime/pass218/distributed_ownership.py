"""Pass 218 Iteration 10 distributed canonical ownership and checkpoint CAS.

Iteration 9 proves one writer for processes sharing one lock-coherent POSIX
filesystem. Iteration 10 adds a second, cross-host authority layer backed by an
etcd v3 linearizable lease/CAS surface. The etcd owner key is lease-bound and
ephemeral; the fencing epoch and last-owner record are durable. Canonical I7
checkpoints are also replicated through an owner/fence/checkpoint compare-and-
swap transaction so a replacement host with an unrelated local filesystem can
reconstruct the exact committed Pass-217/VM81 target.

A host is authoritative only while both its local I9 fence and this distributed
fence remain current. Any transport failure, lease loss, owner mismatch, fence
mismatch, or checkpoint CAS conflict is fail-closed. No source text, Pass-165
learning, truth promotion, action authority, or floating-point value is admitted
through this layer.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
import json
import os
import socket
import ssl
from threading import RLock
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.commit_boundary import (
    Pass217VM81CanonicalTarget,
    _canonical_bytes,
    _copy,
    _reject_retained_source_surface,
)
from hhs_runtime.pass218.persistence_compat import (
    restore_target_from_checkpoint,
    validate_checkpoint,
)

PASS218_DISTRIBUTED_OWNERSHIP_VERSION = "HHS-P218-DISTRIBUTED-CANONICAL-OWNERSHIP-I10-V1"
DISTRIBUTED_OWNERSHIP_RECORD_SCHEMA = "HHS-P218-I10-DISTRIBUTED-OWNERSHIP-RECORD-V1"
DISTRIBUTED_CHECKPOINT_RECORD_SCHEMA = "HHS-P218-I10-DISTRIBUTED-CANONICAL-CHECKPOINT-V1"
DISTRIBUTED_AUTHORITY_SCOPE = "ETCD_V3_LINEARIZABLE_LEASE_CAS"
DISTRIBUTED_CONSENSUS_BACKEND = "ETCD_V3"
DEFAULT_ETCD_NAMESPACE = "/hhs/pass218/i10"
DEFAULT_ETCD_TIMEOUT_SECONDS = 3
DEFAULT_ETCD_LEASE_TTL_SECONDS = 30
DEFAULT_ETCD_ACQUIRE_ATTEMPTS = 4


class Pass218DistributedOwnershipError(RuntimeError):
    pass


class Pass218DistributedOwnershipBusy(Pass218DistributedOwnershipError):
    pass


class Pass218DistributedOwnershipUnavailable(Pass218DistributedOwnershipError):
    pass


class Pass218DistributedOwnershipValidationError(Pass218DistributedOwnershipError):
    pass


class Pass218DistributedOwnershipFenceLost(Pass218DistributedOwnershipError):
    pass


class Pass218DistributedCheckpointConflict(Pass218DistributedOwnershipError):
    pass


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _require_positive_int(value: Any, *, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise Pass218DistributedOwnershipValidationError(code)
    return value


def _require_nonnegative_int(value: Any, *, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Pass218DistributedOwnershipValidationError(code)
    return value


def _require_false(record: Mapping[str, Any], key: str) -> None:
    if record.get(key) is not False:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_FORBIDDEN_AUTHORITY_FLAG:" + key
        )


def _canonical_json_record(raw: bytes, *, code: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise Pass218DistributedOwnershipValidationError(code + "_JSON_INVALID") from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != raw:
        raise Pass218DistributedOwnershipValidationError(code + "_NONCANONICAL")
    _reject_retained_source_surface(value)
    return value


def default_distributed_host_id() -> str:
    host = socket.gethostname().strip() or "unknown-host"
    return host[:256]


def default_distributed_owner_id() -> str:
    return f"{default_distributed_host_id()}:{os.getpid()}"


def _validate_identity(value: Any, *, code: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 256:
        raise Pass218DistributedOwnershipValidationError(code)
    return value


def _ownership_payload(
    *,
    owner_id: str,
    host_id: str,
    fence_epoch: int,
    previous_owner_id: str | None,
    previous_host_id: str | None,
    previous_fence_epoch: int,
    lease_id: int,
    lease_ttl_seconds: int,
    consensus_backend: str = DISTRIBUTED_CONSENSUS_BACKEND,
    authority_scope: str = DISTRIBUTED_AUTHORITY_SCOPE,
) -> dict[str, Any]:
    return {
        "schema": DISTRIBUTED_OWNERSHIP_RECORD_SCHEMA,
        "distributed_ownership_version": PASS218_DISTRIBUTED_OWNERSHIP_VERSION,
        "owner_id": owner_id,
        "host_id": host_id,
        "fence_epoch": fence_epoch,
        "previous_owner_id": previous_owner_id,
        "previous_host_id": previous_host_id,
        "previous_fence_epoch": previous_fence_epoch,
        "lease_id": lease_id,
        "lease_ttl_seconds": lease_ttl_seconds,
        "consensus_backend": consensus_backend,
        "authority_scope": authority_scope,
        "linearizable_compare_and_swap": True,
        "split_brain_writer_permitted": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }


def seal_distributed_ownership_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = _copy(payload)
    _reject_retained_source_surface(body)
    if body.get("schema") != DISTRIBUTED_OWNERSHIP_RECORD_SCHEMA:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_OWNERSHIP_SCHEMA_INVALID"
        )
    ownership_hash72 = hash72_digest(
        {"domain": "HHS-P218-I10-DISTRIBUTED-OWNERSHIP-RECORD-V1"},
        body,
    )
    return {**body, "ownership_hash72": ownership_hash72}


def validate_distributed_ownership_record(record: Mapping[str, Any]) -> dict[str, Any]:
    row = _copy(record)
    _reject_retained_source_surface(row)
    required = {
        "schema",
        "distributed_ownership_version",
        "owner_id",
        "host_id",
        "fence_epoch",
        "previous_owner_id",
        "previous_host_id",
        "previous_fence_epoch",
        "lease_id",
        "lease_ttl_seconds",
        "consensus_backend",
        "authority_scope",
        "linearizable_compare_and_swap",
        "split_brain_writer_permitted",
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
        "ownership_hash72",
    }
    if set(row) != required:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_OWNERSHIP_FIELD_SET_INVALID"
        )
    if row.get("schema") != DISTRIBUTED_OWNERSHIP_RECORD_SCHEMA:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_OWNERSHIP_SCHEMA_INVALID"
        )
    if row.get("distributed_ownership_version") != PASS218_DISTRIBUTED_OWNERSHIP_VERSION:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_OWNERSHIP_VERSION_INVALID"
        )
    owner_id = _validate_identity(
        row.get("owner_id"), code="P218_I10_DISTRIBUTED_OWNER_ID_INVALID"
    )
    host_id = _validate_identity(
        row.get("host_id"), code="P218_I10_DISTRIBUTED_HOST_ID_INVALID"
    )
    epoch = _require_positive_int(
        row.get("fence_epoch"), code="P218_I10_DISTRIBUTED_FENCE_INVALID"
    )
    previous_epoch = _require_nonnegative_int(
        row.get("previous_fence_epoch"),
        code="P218_I10_DISTRIBUTED_PREVIOUS_FENCE_INVALID",
    )
    previous_owner = row.get("previous_owner_id")
    previous_host = row.get("previous_host_id")
    if previous_owner is not None:
        _validate_identity(
            previous_owner,
            code="P218_I10_DISTRIBUTED_PREVIOUS_OWNER_INVALID",
        )
    if previous_host is not None:
        _validate_identity(
            previous_host,
            code="P218_I10_DISTRIBUTED_PREVIOUS_HOST_INVALID",
        )
    if epoch == 1:
        if previous_epoch != 0 or previous_owner is not None or previous_host is not None:
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_DISTRIBUTED_GENESIS_PREDECESSOR_INVALID"
            )
    else:
        if (
            previous_epoch != epoch - 1
            or previous_owner is None
            or previous_host is None
        ):
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_DISTRIBUTED_FENCE_CHAIN_INVALID"
            )
    _require_positive_int(
        row.get("lease_id"), code="P218_I10_DISTRIBUTED_LEASE_ID_INVALID"
    )
    _require_positive_int(
        row.get("lease_ttl_seconds"), code="P218_I10_DISTRIBUTED_LEASE_TTL_INVALID"
    )
    if row.get("consensus_backend") != DISTRIBUTED_CONSENSUS_BACKEND:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_BACKEND_INVALID"
        )
    if row.get("authority_scope") != DISTRIBUTED_AUTHORITY_SCOPE:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_SCOPE_INVALID"
        )
    if row.get("linearizable_compare_and_swap") is not True:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CAS_FLAG_INVALID"
        )
    if row.get("split_brain_writer_permitted") is not False:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_SPLIT_BRAIN_FLAG_INVALID"
        )
    for key in (
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
    ):
        _require_false(row, key)
    supplied = row.get("ownership_hash72")
    if not validate_hash72(str(supplied or "")):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_OWNERSHIP_HASH72_INVALID"
        )
    body = {key: _copy(value) for key, value in row.items() if key != "ownership_hash72"}
    if seal_distributed_ownership_record(body)["ownership_hash72"] != supplied:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_OWNERSHIP_HASH72_MISMATCH"
        )
    if owner_id == previous_owner and host_id == previous_host and epoch > 1:
        # Reacquisition by the same process identity is allowed only as a new
        # fence; the identity equality itself does not weaken fencing.
        pass
    return row


def _distributed_checkpoint_payload(
    checkpoint: Mapping[str, Any],
    *,
    ownership: Mapping[str, Any],
    previous_distributed_checkpoint_sha256: str | None,
) -> dict[str, Any]:
    validated = validate_checkpoint(checkpoint)
    owner = validate_distributed_ownership_record(ownership)
    previous = previous_distributed_checkpoint_sha256
    if previous is not None and not _valid_sha256(previous):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_PREVIOUS_CHECKPOINT_SHA256_INVALID"
        )
    return {
        "schema": DISTRIBUTED_CHECKPOINT_RECORD_SCHEMA,
        "distributed_ownership_version": PASS218_DISTRIBUTED_OWNERSHIP_VERSION,
        "fence_epoch": owner["fence_epoch"],
        "owner_id": owner["owner_id"],
        "host_id": owner["host_id"],
        "ownership_hash72": owner["ownership_hash72"],
        "checkpoint_sha256": validated["checkpoint_sha256"],
        "checkpoint_hash72": validated["checkpoint_hash72"],
        "canonical_root_hash72": validated["canonical_target_record"]["canonical_root_hash72"],
        "generation_sequence": validated["generation_sequence"],
        "previous_distributed_checkpoint_sha256": previous,
        "checkpoint": validated,
        "linearizable_compare_and_swap": True,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }


def seal_distributed_checkpoint_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = _copy(payload)
    _reject_retained_source_surface(body)
    if body.get("schema") != DISTRIBUTED_CHECKPOINT_RECORD_SCHEMA:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_SCHEMA_INVALID"
        )
    distributed_checkpoint_hash72 = hash72_digest(
        {"domain": "HHS-P218-I10-DISTRIBUTED-CANONICAL-CHECKPOINT-V1"},
        body,
    )
    return {**body, "distributed_checkpoint_hash72": distributed_checkpoint_hash72}


def validate_distributed_checkpoint_record(record: Mapping[str, Any]) -> dict[str, Any]:
    row = _copy(record)
    _reject_retained_source_surface(row)
    required = {
        "schema",
        "distributed_ownership_version",
        "fence_epoch",
        "owner_id",
        "host_id",
        "ownership_hash72",
        "checkpoint_sha256",
        "checkpoint_hash72",
        "canonical_root_hash72",
        "generation_sequence",
        "previous_distributed_checkpoint_sha256",
        "checkpoint",
        "linearizable_compare_and_swap",
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
        "distributed_checkpoint_hash72",
    }
    if set(row) != required:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_FIELD_SET_INVALID"
        )
    if row.get("schema") != DISTRIBUTED_CHECKPOINT_RECORD_SCHEMA:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_SCHEMA_INVALID"
        )
    if row.get("distributed_ownership_version") != PASS218_DISTRIBUTED_OWNERSHIP_VERSION:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_VERSION_INVALID"
        )
    _require_positive_int(
        row.get("fence_epoch"), code="P218_I10_DISTRIBUTED_CHECKPOINT_FENCE_INVALID"
    )
    _validate_identity(
        row.get("owner_id"), code="P218_I10_DISTRIBUTED_CHECKPOINT_OWNER_INVALID"
    )
    _validate_identity(
        row.get("host_id"), code="P218_I10_DISTRIBUTED_CHECKPOINT_HOST_INVALID"
    )
    if not validate_hash72(str(row.get("ownership_hash72") or "")):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_OWNERSHIP_HASH_INVALID"
        )
    if not _valid_sha256(row.get("checkpoint_sha256")):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_SHA256_INVALID"
        )
    if not validate_hash72(str(row.get("checkpoint_hash72") or "")):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_HASH72_INVALID"
        )
    if not validate_hash72(str(row.get("canonical_root_hash72") or "")):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_ROOT_INVALID"
        )
    _require_nonnegative_int(
        row.get("generation_sequence"),
        code="P218_I10_DISTRIBUTED_CHECKPOINT_SEQUENCE_INVALID",
    )
    previous = row.get("previous_distributed_checkpoint_sha256")
    if previous is not None and not _valid_sha256(previous):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_PREVIOUS_CHECKPOINT_SHA256_INVALID"
        )
    if row.get("linearizable_compare_and_swap") is not True:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_CAS_FLAG_INVALID"
        )
    for key in (
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
    ):
        _require_false(row, key)
    checkpoint = validate_checkpoint(row.get("checkpoint", {}))
    if checkpoint["checkpoint_sha256"] != row["checkpoint_sha256"]:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_INNER_CHECKPOINT_SHA256_MISMATCH"
        )
    if checkpoint["checkpoint_hash72"] != row["checkpoint_hash72"]:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_INNER_CHECKPOINT_HASH72_MISMATCH"
        )
    if (
        checkpoint["canonical_target_record"]["canonical_root_hash72"]
        != row["canonical_root_hash72"]
    ):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_INNER_CHECKPOINT_ROOT_MISMATCH"
        )
    if checkpoint["generation_sequence"] != row["generation_sequence"]:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_INNER_CHECKPOINT_SEQUENCE_MISMATCH"
        )
    supplied = row.get("distributed_checkpoint_hash72")
    if not validate_hash72(str(supplied or "")):
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_SEAL_INVALID"
        )
    body = {
        key: _copy(value)
        for key, value in row.items()
        if key != "distributed_checkpoint_hash72"
    }
    if seal_distributed_checkpoint_record(body)["distributed_checkpoint_hash72"] != supplied:
        raise Pass218DistributedOwnershipValidationError(
            "P218_I10_DISTRIBUTED_CHECKPOINT_SEAL_MISMATCH"
        )
    return row


class Pass218DistributedAuthorityProtocol(Protocol):
    backend_name: str
    authority_scope: str
    lease_ttl_seconds: int

    @property
    def held(self) -> bool: ...

    @property
    def record(self) -> dict[str, Any] | None: ...

    def acquire(self) -> dict[str, Any] | None: ...

    def assert_current(self) -> dict[str, Any]: ...

    def renew(self) -> dict[str, Any]: ...

    def release(self) -> None: ...

    def read_checkpoint(self, *, require_current: bool = True) -> dict[str, Any] | None: ...

    def publish_checkpoint(
        self,
        checkpoint: Mapping[str, Any],
        *,
        expected_previous_checkpoint_sha256: str | None,
    ) -> dict[str, Any]: ...


class EtcdV3HTTPClient:
    """Minimal etcd v3 JSON-gateway client used by the I10 authority."""

    def __init__(
        self,
        endpoint: str,
        *,
        timeout_seconds: int = DEFAULT_ETCD_TIMEOUT_SECONDS,
        authorization: str | None = None,
        ca_file: str | os.PathLike[str] | None = None,
    ) -> None:
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_ETCD_ENDPOINT_REQUIRED"
            )
        parsed = urlparse(endpoint.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_ETCD_ENDPOINT_INVALID"
            )
        self.endpoint = endpoint.strip().rstrip("/")
        self.timeout_seconds = _require_positive_int(
            timeout_seconds, code="P218_I10_ETCD_TIMEOUT_INVALID"
        )
        self.authorization = authorization
        self._ssl_context = None
        if parsed.scheme == "https":
            self._ssl_context = ssl.create_default_context(
                cafile=None if ca_file is None else str(ca_file)
            )

    @staticmethod
    def encode(value: bytes) -> str:
        return b64encode(value).decode("ascii")

    @staticmethod
    def decode(value: str) -> bytes:
        try:
            return b64decode(value, validate=True)
        except Exception as exc:
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_ETCD_BASE64_INVALID"
            ) from exc

    def _request(
        self,
        path: str,
        payload: Mapping[str, Any],
        *,
        first_stream_line: bool = False,
    ) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.authorization:
            headers["Authorization"] = self.authorization
        request = Request(
            self.endpoint + path,
            data=_canonical_bytes(payload),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
                context=self._ssl_context,
            ) as response:
                if first_stream_line:
                    raw = b""
                    for _ in range(4):
                        raw = response.readline(65536)
                        if raw.strip():
                            break
                else:
                    raw = response.read()
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise Pass218DistributedOwnershipUnavailable(
                "P218_I10_ETCD_TRANSPORT_UNAVAILABLE"
            ) from exc
        if not raw:
            return {}
        try:
            result = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise Pass218DistributedOwnershipUnavailable(
                "P218_I10_ETCD_RESPONSE_INVALID"
            ) from exc
        if not isinstance(result, dict):
            raise Pass218DistributedOwnershipUnavailable(
                "P218_I10_ETCD_RESPONSE_INVALID"
            )
        if result.get("error"):
            raise Pass218DistributedOwnershipUnavailable(
                "P218_I10_ETCD_ERROR:" + str(result.get("error"))
            )
        return result

    def range_value(self, key: bytes) -> tuple[bytes | None, dict[str, Any] | None]:
        response = self._request(
            "/v3/kv/range",
            {"key": self.encode(key)},
        )
        rows = response.get("kvs") or []
        if not rows:
            return None, None
        if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_ETCD_RANGE_CARDINALITY_INVALID"
            )
        row = rows[0]
        return self.decode(str(row.get("value", ""))), row

    def lease_grant(self, ttl_seconds: int) -> int:
        ttl = _require_positive_int(
            ttl_seconds, code="P218_I10_ETCD_LEASE_TTL_INVALID"
        )
        response = self._request("/v3/lease/grant", {"TTL": str(ttl)})
        try:
            lease_id = int(response["ID"])
        except Exception as exc:
            raise Pass218DistributedOwnershipUnavailable(
                "P218_I10_ETCD_LEASE_GRANT_INVALID"
            ) from exc
        return _require_positive_int(
            lease_id, code="P218_I10_ETCD_LEASE_ID_INVALID"
        )

    def lease_keepalive(self, lease_id: int) -> int:
        lease = _require_positive_int(
            lease_id, code="P218_I10_ETCD_LEASE_ID_INVALID"
        )
        response = self._request(
            "/v3/lease/keepalive",
            {"ID": str(lease)},
            first_stream_line=True,
        )
        body = response.get("result") if isinstance(response.get("result"), dict) else response
        try:
            ttl = int(body["TTL"])
        except Exception as exc:
            raise Pass218DistributedOwnershipUnavailable(
                "P218_I10_ETCD_KEEPALIVE_INVALID"
            ) from exc
        if ttl < 1:
            raise Pass218DistributedOwnershipFenceLost(
                "P218_I10_DISTRIBUTED_LEASE_EXPIRED"
            )
        return ttl

    def lease_revoke(self, lease_id: int) -> None:
        lease = _require_positive_int(
            lease_id, code="P218_I10_ETCD_LEASE_ID_INVALID"
        )
        self._request("/v3/lease/revoke", {"ID": str(lease)})

    def txn(
        self,
        *,
        compare: list[Mapping[str, Any]],
        success: list[Mapping[str, Any]],
        failure: list[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "/v3/kv/txn",
            {
                "compare": list(compare),
                "success": list(success),
                "failure": [] if failure is None else list(failure),
            },
        )

    def compare_version(self, key: bytes, version: int) -> dict[str, Any]:
        return {
            "key": self.encode(key),
            "target": "VERSION",
            "result": "EQUAL",
            "version": str(version),
        }

    def compare_value(self, key: bytes, value: bytes) -> dict[str, Any]:
        return {
            "key": self.encode(key),
            "target": "VALUE",
            "result": "EQUAL",
            "value": self.encode(value),
        }

    def put_operation(
        self,
        key: bytes,
        value: bytes,
        *,
        lease_id: int | None = None,
    ) -> dict[str, Any]:
        request: dict[str, Any] = {
            "key": self.encode(key),
            "value": self.encode(value),
        }
        if lease_id is not None:
            request["lease"] = str(
                _require_positive_int(
                    lease_id, code="P218_I10_ETCD_LEASE_ID_INVALID"
                )
            )
        return {"request_put": request}


class Pass218EtcdDistributedAuthority:
    """Cross-host writer lease, global fence, and canonical checkpoint CAS."""

    backend_name = DISTRIBUTED_CONSENSUS_BACKEND
    authority_scope = DISTRIBUTED_AUTHORITY_SCOPE

    def __init__(
        self,
        endpoint: str,
        *,
        namespace: str = DEFAULT_ETCD_NAMESPACE,
        owner_id: str | None = None,
        host_id: str | None = None,
        lease_ttl_seconds: int = DEFAULT_ETCD_LEASE_TTL_SECONDS,
        timeout_seconds: int = DEFAULT_ETCD_TIMEOUT_SECONDS,
        authorization: str | None = None,
        ca_file: str | os.PathLike[str] | None = None,
        acquire_attempts: int = DEFAULT_ETCD_ACQUIRE_ATTEMPTS,
    ) -> None:
        self.client = EtcdV3HTTPClient(
            endpoint,
            timeout_seconds=timeout_seconds,
            authorization=authorization,
            ca_file=ca_file,
        )
        if (
            not isinstance(namespace, str)
            or not namespace.startswith("/")
            or namespace.endswith("/")
            or len(namespace) > 512
            or any(character.isspace() for character in namespace)
        ):
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_ETCD_NAMESPACE_INVALID"
            )
        self.namespace = namespace
        self.owner_id = _validate_identity(
            owner_id or default_distributed_owner_id(),
            code="P218_I10_DISTRIBUTED_OWNER_ID_INVALID",
        )
        self.host_id = _validate_identity(
            host_id or default_distributed_host_id(),
            code="P218_I10_DISTRIBUTED_HOST_ID_INVALID",
        )
        self.lease_ttl_seconds = _require_positive_int(
            lease_ttl_seconds, code="P218_I10_DISTRIBUTED_LEASE_TTL_INVALID"
        )
        self.acquire_attempts = _require_positive_int(
            acquire_attempts, code="P218_I10_DISTRIBUTED_ACQUIRE_ATTEMPTS_INVALID"
        )
        self._record: dict[str, Any] | None = None
        self._lost = False
        self._lock = RLock()

    def _key(self, suffix: str) -> bytes:
        return (self.namespace + "/" + suffix).encode("utf-8")

    @property
    def owner_key(self) -> bytes:
        return self._key("owner")

    @property
    def fence_key(self) -> bytes:
        return self._key("fence")

    @property
    def last_owner_key(self) -> bytes:
        return self._key("last-owner")

    @property
    def checkpoint_key(self) -> bytes:
        return self._key("checkpoint")

    @property
    def held(self) -> bool:
        with self._lock:
            return self._record is not None and not self._lost

    @property
    def record(self) -> dict[str, Any] | None:
        with self._lock:
            return None if self._record is None else _copy(self._record)

    def _read_fence(self) -> tuple[int, bytes | None]:
        raw, _ = self.client.range_value(self.fence_key)
        if raw is None:
            return 0, None
        try:
            value = int(raw.decode("ascii"))
        except Exception as exc:
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_DISTRIBUTED_FENCE_STORAGE_INVALID"
            ) from exc
        _require_positive_int(value, code="P218_I10_DISTRIBUTED_FENCE_STORAGE_INVALID")
        if str(value).encode("ascii") != raw:
            raise Pass218DistributedOwnershipValidationError(
                "P218_I10_DISTRIBUTED_FENCE_STORAGE_NONCANONICAL"
            )
        return value, raw

    def _read_last_owner(self) -> tuple[dict[str, Any] | None, bytes | None]:
        raw, _ = self.client.range_value(self.last_owner_key)
        if raw is None:
            return None, None
        return validate_distributed_ownership_record(
            _canonical_json_record(raw, code="P218_I10_LAST_OWNER")
        ), raw

    def _owner_present(self) -> bool:
        raw, _ = self.client.range_value(self.owner_key)
        return raw is not None

    def acquire(self) -> dict[str, Any] | None:
        with self._lock:
            if self._record is not None and not self._lost:
                return self.assert_current()
            self._record = None
            self._lost = False

        for _ in range(self.acquire_attempts):
            if self._owner_present():
                return None
            previous_epoch, previous_fence_raw = self._read_fence()
            previous_owner, previous_owner_raw = self._read_last_owner()
            if previous_epoch == 0 and previous_owner is not None:
                raise Pass218DistributedOwnershipValidationError(
                    "P218_I10_DISTRIBUTED_PREDECESSOR_STORAGE_INVALID"
                )
            if previous_epoch > 0:
                if previous_owner is None or previous_owner["fence_epoch"] != previous_epoch:
                    raise Pass218DistributedOwnershipValidationError(
                        "P218_I10_DISTRIBUTED_PREDECESSOR_STORAGE_INVALID"
                    )
            lease_id = self.client.lease_grant(self.lease_ttl_seconds)
            payload = _ownership_payload(
                owner_id=self.owner_id,
                host_id=self.host_id,
                fence_epoch=previous_epoch + 1,
                previous_owner_id=(
                    None if previous_owner is None else previous_owner["owner_id"]
                ),
                previous_host_id=(
                    None if previous_owner is None else previous_owner["host_id"]
                ),
                previous_fence_epoch=previous_epoch,
                lease_id=lease_id,
                lease_ttl_seconds=self.lease_ttl_seconds,
            )
            record = seal_distributed_ownership_record(payload)
            record_bytes = _canonical_bytes(record)
            next_fence_bytes = str(previous_epoch + 1).encode("ascii")
            compare: list[Mapping[str, Any]] = [
                self.client.compare_version(self.owner_key, 0),
            ]
            if previous_fence_raw is None:
                compare.append(self.client.compare_version(self.fence_key, 0))
            else:
                compare.append(
                    self.client.compare_value(self.fence_key, previous_fence_raw)
                )
            if previous_owner_raw is None:
                compare.append(self.client.compare_version(self.last_owner_key, 0))
            else:
                compare.append(
                    self.client.compare_value(self.last_owner_key, previous_owner_raw)
                )
            response = self.client.txn(
                compare=compare,
                success=[
                    self.client.put_operation(self.fence_key, next_fence_bytes),
                    self.client.put_operation(self.last_owner_key, record_bytes),
                    self.client.put_operation(
                        self.owner_key,
                        record_bytes,
                        lease_id=lease_id,
                    ),
                ],
            )
            if response.get("succeeded") is True:
                with self._lock:
                    self._record = record
                    self._lost = False
                return _copy(record)
            try:
                self.client.lease_revoke(lease_id)
            except Pass218DistributedOwnershipError:
                pass
        return None

    def assert_current(self) -> dict[str, Any]:
        with self._lock:
            if self._record is None or self._lost:
                raise Pass218DistributedOwnershipFenceLost(
                    "P218_I10_DISTRIBUTED_OWNERSHIP_NOT_HELD"
                )
            record = validate_distributed_ownership_record(self._record)
        record_bytes = _canonical_bytes(record)
        fence_bytes = str(record["fence_epoch"]).encode("ascii")
        try:
            response = self.client.txn(
                compare=[
                    self.client.compare_value(self.owner_key, record_bytes),
                    self.client.compare_value(self.fence_key, fence_bytes),
                ],
                success=[],
            )
        except Pass218DistributedOwnershipError:
            with self._lock:
                self._lost = True
            raise
        if response.get("succeeded") is not True:
            with self._lock:
                self._lost = True
            raise Pass218DistributedOwnershipFenceLost(
                "P218_I10_DISTRIBUTED_OWNERSHIP_FENCE_LOST"
            )
        return _copy(record)

    def renew(self) -> dict[str, Any]:
        record = self.assert_current()
        try:
            ttl = self.client.lease_keepalive(int(record["lease_id"]))
        except Pass218DistributedOwnershipError:
            with self._lock:
                self._lost = True
            raise
        if ttl < 1:
            with self._lock:
                self._lost = True
            raise Pass218DistributedOwnershipFenceLost(
                "P218_I10_DISTRIBUTED_LEASE_EXPIRED"
            )
        return self.assert_current()

    def release(self) -> None:
        with self._lock:
            record = self._record
            self._record = None
            self._lost = True
        if record is None:
            return
        try:
            self.client.lease_revoke(int(record["lease_id"]))
        except Pass218DistributedOwnershipError:
            # A failed revoke cannot preserve local authority. The process has
            # already marked itself lost; server-side expiry remains the only
            # route to a successor fence.
            return

    def read_checkpoint(self, *, require_current: bool = True) -> dict[str, Any] | None:
        if require_current:
            self.assert_current()
        raw, _ = self.client.range_value(self.checkpoint_key)
        if raw is None:
            return None
        return validate_distributed_checkpoint_record(
            _canonical_json_record(raw, code="P218_I10_DISTRIBUTED_CHECKPOINT")
        )

    def publish_checkpoint(
        self,
        checkpoint: Mapping[str, Any],
        *,
        expected_previous_checkpoint_sha256: str | None,
    ) -> dict[str, Any]:
        ownership = self.assert_current()
        current_raw, _ = self.client.range_value(self.checkpoint_key)
        current = None
        if current_raw is not None:
            current = validate_distributed_checkpoint_record(
                _canonical_json_record(
                    current_raw,
                    code="P218_I10_DISTRIBUTED_CHECKPOINT",
                )
            )
        if expected_previous_checkpoint_sha256 is None:
            if current is not None:
                raise Pass218DistributedCheckpointConflict(
                    "P218_I10_DISTRIBUTED_CHECKPOINT_EXPECTED_GENESIS"
                )
        else:
            if (
                current is None
                or current["checkpoint_sha256"]
                != expected_previous_checkpoint_sha256
            ):
                raise Pass218DistributedCheckpointConflict(
                    "P218_I10_DISTRIBUTED_CHECKPOINT_PREDECESSOR_MISMATCH"
                )
        validated_checkpoint = validate_checkpoint(checkpoint)
        if (
            current is not None
            and current["checkpoint_sha256"] == validated_checkpoint["checkpoint_sha256"]
            and current["canonical_root_hash72"]
            == validated_checkpoint["canonical_target_record"]["canonical_root_hash72"]
        ):
            return _copy(current)
        payload = _distributed_checkpoint_payload(
            validated_checkpoint,
            ownership=ownership,
            previous_distributed_checkpoint_sha256=(
                None if current is None else current["checkpoint_sha256"]
            ),
        )
        sealed = seal_distributed_checkpoint_record(payload)
        sealed_bytes = _canonical_bytes(sealed)
        owner_bytes = _canonical_bytes(ownership)
        fence_bytes = str(ownership["fence_epoch"]).encode("ascii")
        compare: list[Mapping[str, Any]] = [
            self.client.compare_value(self.owner_key, owner_bytes),
            self.client.compare_value(self.fence_key, fence_bytes),
        ]
        if current_raw is None:
            compare.append(self.client.compare_version(self.checkpoint_key, 0))
        else:
            compare.append(self.client.compare_value(self.checkpoint_key, current_raw))
        response = self.client.txn(
            compare=compare,
            success=[self.client.put_operation(self.checkpoint_key, sealed_bytes)],
        )
        if response.get("succeeded") is not True:
            try:
                self.assert_current()
            except Pass218DistributedOwnershipError:
                raise
            raise Pass218DistributedCheckpointConflict(
                "P218_I10_DISTRIBUTED_CHECKPOINT_CAS_CONFLICT"
            )
        return _copy(sealed)


class Pass218InMemoryConsensusHarness:
    """Deterministic test/reference harness for the I10 authority protocol.

    This is deliberately not a production distributed-consensus backend. It
    exists so unit tests can deterministically inject partition and lease-loss
    states while the production implementation is exercised separately against
    an actual etcd v3 service.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self.available = True
        self.fence_epoch = 0
        self.owner_record: dict[str, Any] | None = None
        self.last_owner_record: dict[str, Any] | None = None
        self.checkpoint_record: dict[str, Any] | None = None
        self._next_lease_id = 1

    def require_available(self) -> None:
        if not self.available:
            raise Pass218DistributedOwnershipUnavailable(
                "P218_I10_CONSENSUS_UNAVAILABLE"
            )

    def set_available(self, value: bool) -> None:
        with self._lock:
            self.available = bool(value)

    def expire_owner(self) -> None:
        with self._lock:
            self.owner_record = None

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "fence_epoch": self.fence_epoch,
                "owner_record": None if self.owner_record is None else _copy(self.owner_record),
                "last_owner_record": (
                    None if self.last_owner_record is None else _copy(self.last_owner_record)
                ),
                "checkpoint_record": (
                    None if self.checkpoint_record is None else _copy(self.checkpoint_record)
                ),
                "available": self.available,
            }


class Pass218InMemoryDistributedAuthority:
    backend_name = DISTRIBUTED_CONSENSUS_BACKEND
    authority_scope = DISTRIBUTED_AUTHORITY_SCOPE

    def __init__(
        self,
        harness: Pass218InMemoryConsensusHarness,
        *,
        owner_id: str,
        host_id: str,
        lease_ttl_seconds: int = DEFAULT_ETCD_LEASE_TTL_SECONDS,
    ) -> None:
        self.harness = harness
        self.owner_id = _validate_identity(
            owner_id, code="P218_I10_DISTRIBUTED_OWNER_ID_INVALID"
        )
        self.host_id = _validate_identity(
            host_id, code="P218_I10_DISTRIBUTED_HOST_ID_INVALID"
        )
        self.lease_ttl_seconds = _require_positive_int(
            lease_ttl_seconds, code="P218_I10_DISTRIBUTED_LEASE_TTL_INVALID"
        )
        self._record: dict[str, Any] | None = None
        self._lost = False

    @property
    def held(self) -> bool:
        return self._record is not None and not self._lost

    @property
    def record(self) -> dict[str, Any] | None:
        return None if self._record is None else _copy(self._record)

    def acquire(self) -> dict[str, Any] | None:
        with self.harness._lock:
            self.harness.require_available()
            if self.harness.owner_record is not None:
                if (
                    self._record is not None
                    and self.harness.owner_record == self._record
                    and not self._lost
                ):
                    return self.assert_current()
                return None
            previous = self.harness.last_owner_record
            previous_epoch = self.harness.fence_epoch
            lease_id = self.harness._next_lease_id
            self.harness._next_lease_id += 1
            record = seal_distributed_ownership_record(
                _ownership_payload(
                    owner_id=self.owner_id,
                    host_id=self.host_id,
                    fence_epoch=previous_epoch + 1,
                    previous_owner_id=(
                        None if previous is None else previous["owner_id"]
                    ),
                    previous_host_id=(
                        None if previous is None else previous["host_id"]
                    ),
                    previous_fence_epoch=previous_epoch,
                    lease_id=lease_id,
                    lease_ttl_seconds=self.lease_ttl_seconds,
                )
            )
            self.harness.fence_epoch = previous_epoch + 1
            self.harness.owner_record = _copy(record)
            self.harness.last_owner_record = _copy(record)
            self._record = record
            self._lost = False
            return _copy(record)

    def assert_current(self) -> dict[str, Any]:
        with self.harness._lock:
            self.harness.require_available()
            if (
                self._record is None
                or self._lost
                or self.harness.owner_record != self._record
                or self.harness.fence_epoch != self._record["fence_epoch"]
            ):
                self._lost = True
                raise Pass218DistributedOwnershipFenceLost(
                    "P218_I10_DISTRIBUTED_OWNERSHIP_FENCE_LOST"
                )
            return _copy(self._record)

    def renew(self) -> dict[str, Any]:
        return self.assert_current()

    def release(self) -> None:
        with self.harness._lock:
            if self.harness.owner_record == self._record:
                self.harness.owner_record = None
            self._record = None
            self._lost = True

    def read_checkpoint(self, *, require_current: bool = True) -> dict[str, Any] | None:
        if require_current:
            self.assert_current()
        with self.harness._lock:
            self.harness.require_available()
            return (
                None
                if self.harness.checkpoint_record is None
                else _copy(self.harness.checkpoint_record)
            )

    def publish_checkpoint(
        self,
        checkpoint: Mapping[str, Any],
        *,
        expected_previous_checkpoint_sha256: str | None,
    ) -> dict[str, Any]:
        ownership = self.assert_current()
        with self.harness._lock:
            self.harness.require_available()
            current = self.harness.checkpoint_record
            if expected_previous_checkpoint_sha256 is None:
                if current is not None:
                    raise Pass218DistributedCheckpointConflict(
                        "P218_I10_DISTRIBUTED_CHECKPOINT_EXPECTED_GENESIS"
                    )
            else:
                if (
                    current is None
                    or current["checkpoint_sha256"]
                    != expected_previous_checkpoint_sha256
                ):
                    raise Pass218DistributedCheckpointConflict(
                        "P218_I10_DISTRIBUTED_CHECKPOINT_PREDECESSOR_MISMATCH"
                    )
            validated = validate_checkpoint(checkpoint)
            if (
                current is not None
                and current["checkpoint_sha256"] == validated["checkpoint_sha256"]
                and current["canonical_root_hash72"]
                == validated["canonical_target_record"]["canonical_root_hash72"]
            ):
                return _copy(current)
            sealed = seal_distributed_checkpoint_record(
                _distributed_checkpoint_payload(
                    validated,
                    ownership=ownership,
                    previous_distributed_checkpoint_sha256=(
                        None if current is None else current["checkpoint_sha256"]
                    ),
                )
            )
            if self.harness.owner_record != ownership:
                self._lost = True
                raise Pass218DistributedOwnershipFenceLost(
                    "P218_I10_DISTRIBUTED_OWNERSHIP_FENCE_LOST"
                )
            self.harness.checkpoint_record = _copy(sealed)
            return _copy(sealed)


class Pass218UnavailableDistributedAuthority:
    """Fail-closed authority used when distributed mode is required but unconfigured."""

    backend_name = DISTRIBUTED_CONSENSUS_BACKEND
    authority_scope = DISTRIBUTED_AUTHORITY_SCOPE
    lease_ttl_seconds = DEFAULT_ETCD_LEASE_TTL_SECONDS

    @property
    def held(self) -> bool:
        return False

    @property
    def record(self) -> None:
        return None

    def _raise(self) -> None:
        raise Pass218DistributedOwnershipUnavailable(
            "P218_I10_DISTRIBUTED_AUTHORITY_UNCONFIGURED"
        )

    def acquire(self) -> None:
        self._raise()

    def assert_current(self) -> dict[str, Any]:
        self._raise()
        raise AssertionError

    def renew(self) -> dict[str, Any]:
        self._raise()
        raise AssertionError

    def release(self) -> None:
        return None

    def read_checkpoint(self, *, require_current: bool = True) -> None:
        if require_current:
            self._raise()
        return None

    def publish_checkpoint(
        self,
        checkpoint: Mapping[str, Any],
        *,
        expected_previous_checkpoint_sha256: str | None,
    ) -> dict[str, Any]:
        self._raise()
        raise AssertionError


def target_from_distributed_checkpoint(
    record: Mapping[str, Any],
) -> Pass217VM81CanonicalTarget:
    distributed = validate_distributed_checkpoint_record(record)
    return restore_target_from_checkpoint(distributed["checkpoint"])


__all__ = [
    "DEFAULT_ETCD_ACQUIRE_ATTEMPTS",
    "DEFAULT_ETCD_LEASE_TTL_SECONDS",
    "DEFAULT_ETCD_NAMESPACE",
    "DEFAULT_ETCD_TIMEOUT_SECONDS",
    "DISTRIBUTED_AUTHORITY_SCOPE",
    "DISTRIBUTED_CHECKPOINT_RECORD_SCHEMA",
    "DISTRIBUTED_CONSENSUS_BACKEND",
    "DISTRIBUTED_OWNERSHIP_RECORD_SCHEMA",
    "PASS218_DISTRIBUTED_OWNERSHIP_VERSION",
    "EtcdV3HTTPClient",
    "Pass218DistributedAuthorityProtocol",
    "Pass218DistributedCheckpointConflict",
    "Pass218DistributedOwnershipBusy",
    "Pass218DistributedOwnershipError",
    "Pass218DistributedOwnershipFenceLost",
    "Pass218DistributedOwnershipUnavailable",
    "Pass218DistributedOwnershipValidationError",
    "Pass218EtcdDistributedAuthority",
    "Pass218InMemoryConsensusHarness",
    "Pass218InMemoryDistributedAuthority",
    "Pass218UnavailableDistributedAuthority",
    "default_distributed_host_id",
    "default_distributed_owner_id",
    "seal_distributed_checkpoint_record",
    "seal_distributed_ownership_record",
    "target_from_distributed_checkpoint",
    "validate_distributed_checkpoint_record",
    "validate_distributed_ownership_record",
]
