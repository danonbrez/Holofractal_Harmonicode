"""Pass 218 Iteration 6 canonical Pass-217/VM81 commit boundary.

This layer consumes only an already-active Iteration-5 authorization plus its
exact Iteration-4 staged candidate. It does not re-open source transactions,
hydrate source text, invoke Pass-165 learning, or create truth/action authority.

Canonical admission is split into:
    prepare -> atomic commit -> receipt
A complete VM81 image is first proven against the inherited Pass-163 VMRC
authority in an isolated shadow runtime. Only after every one of the 64 VM81
thread lanes commits and the resulting 5,184-bit image exactly equals the
authorized projection may the canonical target atomically replace its state.
"""
from __future__ import annotations

from base64 import b64decode
from dataclasses import dataclass
from hashlib import sha256
import json
from threading import RLock
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import (
    COORDINATES,
    SNAPSHOT_BYTES,
    THREADS,
    VM81_POSITIONS,
    VMRCRuntime,
)

PASS218_CANONICAL_COMMIT_VERSION = "HHS-P218-CANONICAL-COMMIT-I6-V1"
PROMOTION_SCOPE = "PASS217_VECTOR_VM5184_PROMOTION"
PASS217_VECTOR_ENTRY_SCHEMA = "HHS_PASS_217_VECTOR_STORE_ENTRY_V1"
PASS217_VECTOR_SCHEMA_PATH = "contracts/pass217/vector_store.schema.json"
INHERITED_VM81_AUTHORITY = "hhs_runtime.pass163.vmrc.VMRCRuntime"
CANONICAL_ADMISSION_STATUS = "VM81_ADMITTED"
VM81_CAPABILITY_SCOPE = "PASS218_AUTHORIZED_CANONICAL_VM81_IMAGE_ADMISSION"


class Pass218CanonicalCommitError(RuntimeError):
    pass


class Pass218CanonicalCommitValidationError(Pass218CanonicalCommitError):
    pass


class Pass218CanonicalCommitStateError(Pass218CanonicalCommitError):
    pass


class AuthorizationJournalProtocol(Protocol):
    def get(self, authorization_hash72: str) -> dict[str, Any] | None: ...

    def mutation_precondition(
        self,
        authorization_hash72: str,
        *,
        entry_id_sha256: str,
        projection_sha256: str,
        target_scope: str = PROMOTION_SCOPE,
    ) -> bool: ...


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_AUTHORITATIVE_FLOAT_FORBIDDEN"
        )
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            _reject_float(child)


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _copy(value: Any) -> Any:
    return json.loads(_canonical_bytes(value).decode("utf-8"))


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _valid_hash216(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 216
        and all(
            validate_hash72(value[start:start + 72])
            for start in (0, 72, 144)
        )
    )


def _reject_retained_source_surface(value: Any) -> None:
    """Reject any source-retaining payload from crossing the canonical boundary."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in {
                "source_text",
                "source_bytes",
                "raw_source",
                "raw_source_text",
                "managed_buffer",
                "managed_buffer_b64",
                "verbatim_source",
            } and child not in (None, "", b"", [], {}):
                raise Pass218CanonicalCommitValidationError(
                    "P218_I6_SOURCE_RETENTION_FIELD_FORBIDDEN:" + str(key)
                )
            if normalized == "verbatim_source_retained" and child is not False:
                raise Pass218CanonicalCommitValidationError(
                    "P218_I6_VERBATIM_SOURCE_RETENTION_FORBIDDEN"
                )
            if normalized == "canonical_learning_commit_invoked" and child is not False:
                raise Pass218CanonicalCommitValidationError(
                    "P218_I6_LEARNING_COMMIT_PATH_FORBIDDEN"
                )
            _reject_retained_source_surface(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_retained_source_surface(child)


def _entry_candidate_identity(entry: Mapping[str, Any]) -> str:
    body = {key: _copy(value) for key, value in entry.items() if key != "entry_id_sha256"}
    return sha256(
        b"HHS-P218-I4-P217-VECTOR-ENTRY\0" + _canonical_bytes(body)
    ).hexdigest()


def _admitted_entry(candidate: Mapping[str, Any]) -> dict[str, Any]:
    body = {
        key: _copy(value)
        for key, value in candidate.items()
        if key != "entry_id_sha256"
    }
    body["admission_status"] = CANONICAL_ADMISSION_STATUS
    body["bracketing"] = "P218_I6_AUTHORIZED_CANONICAL_VM81_ADMISSION"
    admitted_id = sha256(
        b"HHS-P218-I6-P217-VECTOR-ADMISSION\0" + _canonical_bytes(body)
    ).hexdigest()
    return {"entry_id_sha256": admitted_id, **body}


def _validate_candidate_entry(entry: Mapping[str, Any]) -> None:
    required = {
        "schema",
        "entry_id_sha256",
        "parent_state_sha256",
        "candidate_state_sha256",
        "hash216_transition_sha256",
        "forward_support",
        "inverse_support",
        "ordered_path",
        "bracketing",
        "dependency_frontier",
        "collision_bucket",
        "admission_status",
    }
    if set(entry) != required:
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VECTOR_ENTRY_FIELD_SET_INVALID"
        )
    if entry.get("schema") != PASS217_VECTOR_ENTRY_SCHEMA:
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VECTOR_ENTRY_SCHEMA_INVALID"
        )
    if entry.get("admission_status") != "CANDIDATE":
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VECTOR_ENTRY_NOT_CANDIDATE"
        )
    if _entry_candidate_identity(entry) != entry.get("entry_id_sha256"):
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VECTOR_ENTRY_IDENTITY_MISMATCH"
        )
    for key in (
        "entry_id_sha256",
        "parent_state_sha256",
        "candidate_state_sha256",
        "hash216_transition_sha256",
    ):
        if not _valid_sha256(entry.get(key)):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_VECTOR_ENTRY_SHA256_INVALID:" + key
            )
    for key in ("forward_support", "inverse_support", "dependency_frontier"):
        values = list(entry.get(key, ()))
        if (
            values != sorted(set(values))
            or any(
                not isinstance(item, int)
                or isinstance(item, bool)
                or not 0 <= item < COORDINATES
                for item in values
            )
        ):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_VECTOR_ENTRY_SUPPORT_INVALID:" + key
            )
    forward = set(entry["forward_support"])
    inverse = set(entry["inverse_support"])
    if forward & inverse or len(forward) + len(inverse) != COORDINATES:
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VECTOR_SUPPORT_PARTITION_INVALID"
        )
    if not isinstance(entry.get("ordered_path"), list) or not entry["ordered_path"]:
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VECTOR_ORDERED_PATH_INVALID"
        )
    bucket = entry.get("collision_bucket")
    if not isinstance(bucket, int) or isinstance(bucket, bool) or bucket < 0:
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VECTOR_COLLISION_BUCKET_INVALID"
        )


def _projection_bit(projection: bytes, position: int, thread: int) -> int:
    coordinate = position * THREADS + thread
    byte_index, bit_index = divmod(coordinate, 8)
    return (projection[byte_index] >> (7 - bit_index)) & 1


def _prepare_vm81_shadow(
    projection: bytes,
    *,
    dependency_root: str,
) -> tuple[VMRCRuntime, tuple[dict[str, Any], ...], str]:
    if len(projection) != SNAPSHOT_BYTES:
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VM5184_PROJECTION_LENGTH_INVALID"
        )
    runtime = VMRCRuntime()
    receipts: list[dict[str, Any]] = []
    for thread in range(THREADS):
        writes = {
            position: (1 if _projection_bit(projection, position, thread) else -1)
            for position in range(VM81_POSITIONS)
        }
        candidate = runtime.submit_candidate(
            thread=thread,
            writes=writes,
            operation="VMRC_COMMIT",
            expected_input_hash72=runtime.state_hash72,
            dependency_root=dependency_root,
            capability_scope=VM81_CAPABILITY_SCOPE,
            source_architecture="PASS218_I6_PREPARED_FULL_IMAGE",
            target_architecture="VM81",
        )
        validation = runtime.validate(candidate)
        commit = runtime.commit(candidate.candidate_id)
        receipts.append(
            {
                "thread": thread,
                "candidate_id": candidate.candidate_id,
                "validation_receipt_hash72": validation["receipt"]["receipt_hash72"],
                "commit_receipt_hash72": commit["receipt"]["receipt_hash72"],
                "output_hash72": commit["receipt"]["output_hash72"],
                "operation_hash216": commit["receipt"]["operation_hash216"],
                "epoch": commit["receipt"]["epoch"],
            }
        )
    if runtime.snapshot().to_bytes() != projection:
        raise Pass218CanonicalCommitValidationError(
            "P218_I6_VM81_SHADOW_PROJECTION_MISMATCH"
        )
    receipts_root = hash72_digest(
        {"domain": "HHS-P218-I6-VM81-PREPARE-RECEIPTS-V1"},
        receipts,
    )
    return runtime, tuple(receipts), receipts_root


@dataclass(frozen=True)
class PreparedCanonicalAdmission:
    authorization: Mapping[str, Any]
    staged_candidate: Mapping[str, Any]
    candidate_entry: Mapping[str, Any]
    admitted_entry: Mapping[str, Any]
    projection_bytes: bytes
    shadow_runtime: VMRCRuntime
    vm81_receipts: tuple[Mapping[str, Any], ...]
    vm81_receipts_root_hash72: str
    target_root_before_hash72: str
    prepare_hash72: str
    validation_hash72: str
    prepare_hash216: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-I6-CANONICAL-PREPARE-V1",
            "boundary_version": PASS218_CANONICAL_COMMIT_VERSION,
            "authorization_hash72": self.authorization["authorization_hash72"],
            "candidate_entry_id_sha256": self.candidate_entry["entry_id_sha256"],
            "admitted_entry_id_sha256": self.admitted_entry["entry_id_sha256"],
            "projection_sha256": self.authorization["projection_sha256"],
            "projection_hash72": self.staged_candidate["vm5184_projection_hash72"],
            "target_root_before_hash72": self.target_root_before_hash72,
            "vm81_prepared_snapshot_hash72": self.shadow_runtime.snapshot_hash72,
            "vm81_prepared_state_hash72": self.shadow_runtime.state_hash72,
            "vm81_prepare_commit_count": len(self.vm81_receipts),
            "vm81_prepare_receipts_root_hash72": self.vm81_receipts_root_hash72,
            "prepare_hash72": self.prepare_hash72,
            "validation_hash72": self.validation_hash72,
            "prepare_hash216": self.prepare_hash216,
            "hash216_semantics": [
                "ITERATION5_ACTIVE_AUTHORIZATION",
                "CANONICAL_TARGET_PREPARE",
                "PREPARE_VALIDATION_RECEIPT",
            ],
            "pass217_vector_schema": PASS217_VECTOR_ENTRY_SCHEMA,
            "pass217_vector_schema_path": PASS217_VECTOR_SCHEMA_PATH,
            "inherited_vm81_authority": INHERITED_VM81_AUTHORITY,
            "canonical_vector_store_mutation_invoked": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
        }


@dataclass(frozen=True)
class _TargetState:
    runtime: VMRCRuntime
    entries: Mapping[str, Mapping[str, Any]]
    commits: Mapping[str, Mapping[str, Any]]


class Pass217VM81CanonicalTarget:
    """Atomic canonical target for Pass-217 vector entries and current VM81 image."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._state = _TargetState(runtime=VMRCRuntime(), entries={}, commits={})

    @staticmethod
    def _root_for(state: _TargetState) -> str:
        entry_rows = [
            {
                "candidate_entry_id_sha256": key,
                "admitted_entry_id_sha256": value["entry_id_sha256"],
                "candidate_state_sha256": value["candidate_state_sha256"],
                "hash216_transition_sha256": value["hash216_transition_sha256"],
                "admission_status": value["admission_status"],
            }
            for key, value in sorted(state.entries.items())
        ]
        commit_rows = [
            {
                "authorization_hash72": key,
                "prepare_hash72": value["prepare_hash72"],
                "candidate_entry_id_sha256": value["candidate_entry_id_sha256"],
                "admitted_entry_id_sha256": value["admitted_entry_id_sha256"],
                "projection_sha256": value["projection_sha256"],
            }
            for key, value in sorted(state.commits.items())
        ]
        payload = {
            "schema": "HHS-P218-I6-CANONICAL-TARGET-ROOT-V1",
            "entry_rows": entry_rows,
            "commit_rows": commit_rows,
            "vm81_epoch": state.runtime.epoch,
            "vm81_snapshot_hash72": state.runtime.snapshot_hash72,
            "vm81_state_hash72": state.runtime.state_hash72,
        }
        return hash72_digest(
            {"domain": "HHS-P218-I6-CANONICAL-TARGET-ROOT-V1"},
            payload,
        )

    def root_hash72(self) -> str:
        with self._lock:
            return self._root_for(self._state)

    def snapshot_bytes(self) -> bytes:
        with self._lock:
            return self._state.runtime.snapshot().to_bytes()

    def authorization_consumed(self, authorization_hash72: str) -> bool:
        with self._lock:
            return authorization_hash72 in self._state.commits

    def committed_receipt(self, authorization_hash72: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._state.commits.get(authorization_hash72)
            return None if row is None else _copy(row)

    def record(self) -> dict[str, Any]:
        with self._lock:
            return {
                "schema": "HHS-P218-I6-CANONICAL-PASS217-VM81-TARGET-V1",
                "boundary_version": PASS218_CANONICAL_COMMIT_VERSION,
                "pass217_vector_schema": PASS217_VECTOR_ENTRY_SCHEMA,
                "pass217_vector_schema_path": PASS217_VECTOR_SCHEMA_PATH,
                "inherited_vm81_authority": INHERITED_VM81_AUTHORITY,
                "canonical_root_hash72": self._root_for(self._state),
                "canonical_entry_count": len(self._state.entries),
                "canonical_commit_count": len(self._state.commits),
                "vm81_epoch": self._state.runtime.epoch,
                "vm81_snapshot_hash72": self._state.runtime.snapshot_hash72,
                "vm81_state_hash72": self._state.runtime.state_hash72,
                "canonical_learning_authority": False,
                "source_retention_authority": False,
            }


class Pass218CanonicalCommitBoundary:
    def __init__(self, target: Pass217VM81CanonicalTarget | None = None) -> None:
        self.target = target or Pass217VM81CanonicalTarget()

    @staticmethod
    def _authorization_record(
        authorization: Mapping[str, Any],
        journal: AuthorizationJournalProtocol,
    ) -> dict[str, Any]:
        record = _copy(authorization)
        if record.get("schema") != "HHS-P218-I5-PROMOTION-AUTHORIZATION-V1":
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_SCHEMA_INVALID"
            )
        auth_hash = record.get("authorization_hash72")
        if not validate_hash72(str(auth_hash or "")):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_HASH72_INVALID"
            )
        journal_record = journal.get(str(auth_hash))
        if journal_record is None or journal_record != record:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_NOT_ACTIVE_EXACT_JOURNAL_RECORD"
            )
        if record.get("state") != "AUTHORIZED_PENDING_CANONICAL_COMMIT":
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_STATE_INVALID"
            )
        if record.get("target_scope") != PROMOTION_SCOPE:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_SCOPE_INVALID"
            )
        if record.get("proof_required") is not True or record.get("grant_required") is not True:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_PROOF_GRANT_REQUIREMENT_INVALID"
            )
        if record.get("canonical_mutation_permitted") is not True:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_MUTATION_NOT_PERMITTED"
            )
        return record

    @staticmethod
    def _stage_record(
        staged_candidate: Mapping[str, Any],
        authorization: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any], bytes]:
        staged = _copy(staged_candidate)
        _reject_retained_source_surface(staged)
        if staged.get("schema") != "HHS-P218-I4-VECTOR-VM5184-STAGE-CANDIDATE-V1":
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_STAGE_SCHEMA_INVALID"
            )
        if staged.get("authoritative_vector_store_promotion") is not False:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_STAGE_ALREADY_AUTHORITATIVE"
            )
        if staged.get("canonical_vm81_commit_invoked") is not False:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_STAGE_VM81_ALREADY_COMMITTED"
            )
        if staged.get("canonical_learning_commit_invoked") is not False:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_STAGE_LEARNING_PATH_FORBIDDEN"
            )
        entry = staged.get("vector_entry")
        if not isinstance(entry, Mapping):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_VECTOR_ENTRY_MISSING"
            )
        entry = _copy(entry)
        _validate_candidate_entry(entry)
        if entry["entry_id_sha256"] != authorization.get("entry_id_sha256"):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_ENTRY_BINDING_MISMATCH"
            )
        if staged.get("staging_hash72") != authorization.get("staging_hash72"):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_STAGING_BINDING_MISMATCH"
            )
        try:
            projection = b64decode(str(staged["vm5184_projection_b64"]), validate=True)
        except Exception as exc:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_PROJECTION_B64_INVALID"
            ) from exc
        if len(projection) != SNAPSHOT_BYTES:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_PROJECTION_LENGTH_INVALID"
            )
        projection_sha256 = sha256(projection).hexdigest()
        if projection_sha256 != staged.get("vm5184_projection_sha256"):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_PROJECTION_SHA256_MISMATCH"
            )
        if projection_sha256 != authorization.get("projection_sha256"):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_AUTHORIZATION_PROJECTION_BINDING_MISMATCH"
            )
        if hash72_digest(b"", projection) != staged.get("vm5184_projection_hash72"):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_PROJECTION_HASH72_MISMATCH"
            )
        return staged, entry, projection

    def prepare(
        self,
        *,
        authorization: Mapping[str, Any],
        staged_candidate: Mapping[str, Any],
        authorization_journal: AuthorizationJournalProtocol,
    ) -> PreparedCanonicalAdmission:
        auth = self._authorization_record(authorization, authorization_journal)
        staged, candidate_entry, projection = self._stage_record(
            staged_candidate, auth
        )
        if not authorization_journal.mutation_precondition(
            auth["authorization_hash72"],
            entry_id_sha256=candidate_entry["entry_id_sha256"],
            projection_sha256=sha256(projection).hexdigest(),
            target_scope=PROMOTION_SCOPE,
        ):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_ACTIVE_MUTATION_PRECONDITION_FAILED"
            )
        if self.target.authorization_consumed(auth["authorization_hash72"]):
            existing = self.target.committed_receipt(auth["authorization_hash72"])
            if existing is None:
                raise Pass218CanonicalCommitStateError(
                    "P218_I6_CONSUMED_AUTHORIZATION_RECEIPT_MISSING"
                )
            raise Pass218CanonicalCommitStateError(
                "P218_I6_AUTHORIZATION_ALREADY_CONSUMED"
            )

        target_root_before = self.target.root_hash72()
        admitted = _admitted_entry(candidate_entry)
        shadow, vm81_receipts, receipts_root = _prepare_vm81_shadow(
            projection,
            dependency_root=candidate_entry["hash216_transition_sha256"],
        )
        prepare_payload = {
            "schema": "HHS-P218-I6-CANONICAL-PREPARE-PAYLOAD-V1",
            "authorization_hash72": auth["authorization_hash72"],
            "candidate_entry_id_sha256": candidate_entry["entry_id_sha256"],
            "admitted_entry_id_sha256": admitted["entry_id_sha256"],
            "staging_hash72": auth["staging_hash72"],
            "projection_sha256": auth["projection_sha256"],
            "projection_hash72": staged["vm5184_projection_hash72"],
            "target_root_before_hash72": target_root_before,
            "vm81_prepared_snapshot_hash72": shadow.snapshot_hash72,
            "vm81_prepared_state_hash72": shadow.state_hash72,
            "vm81_prepare_commit_count": len(vm81_receipts),
            "vm81_prepare_receipts_root_hash72": receipts_root,
            "pass217_vector_schema": PASS217_VECTOR_ENTRY_SCHEMA,
            "inherited_vm81_authority": INHERITED_VM81_AUTHORITY,
            "canonical_mutation_invoked": False,
            "verbatim_source_retained": False,
        }
        prepare_hash72 = hash72_digest(
            {"domain": "HHS-P218-I6-CANONICAL-PREPARE-V1"},
            prepare_payload,
        )
        validation_payload = {
            "schema": "HHS-P218-I6-CANONICAL-PREPARE-VALIDATION-V1",
            "prepare_hash72": prepare_hash72,
            "authorization_active": True,
            "candidate_binding_exact": True,
            "projection_binding_exact": True,
            "pass217_schema_exact": True,
            "vm81_projection_exact": shadow.snapshot().to_bytes() == projection,
            "vm81_thread_commit_count_exact": len(vm81_receipts) == THREADS,
            "target_unmutated": self.target.root_hash72() == target_root_before,
            "source_retention_path_present": False,
            "learning_commit_path_present": False,
        }
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I6-CANONICAL-PREPARE-VALIDATION-V1"},
            validation_payload,
        )
        prepare_hash216 = (
            auth["authorization_hash72"] + prepare_hash72 + validation_hash72
        )
        if not _valid_hash216(prepare_hash216):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_PREPARE_HASH216_INVALID"
            )
        prepared = PreparedCanonicalAdmission(
            authorization=auth,
            staged_candidate=staged,
            candidate_entry=candidate_entry,
            admitted_entry=admitted,
            projection_bytes=projection,
            shadow_runtime=shadow,
            vm81_receipts=vm81_receipts,
            vm81_receipts_root_hash72=receipts_root,
            target_root_before_hash72=target_root_before,
            prepare_hash72=prepare_hash72,
            validation_hash72=validation_hash72,
            prepare_hash216=prepare_hash216,
        )
        _reject_retained_source_surface(prepared.to_record())
        return prepared

    def commit(
        self,
        prepared: PreparedCanonicalAdmission,
        *,
        authorization_journal: AuthorizationJournalProtocol,
        fail_before_atomic_swap: bool = False,
    ) -> dict[str, Any]:
        auth = _copy(prepared.authorization)
        auth_hash = auth["authorization_hash72"]
        existing = self.target.committed_receipt(auth_hash)
        if existing is not None:
            if existing.get("prepare_hash72") != prepared.prepare_hash72:
                raise Pass218CanonicalCommitStateError(
                    "P218_I6_IDEMPOTENT_COMMIT_PREPARE_CONFLICT"
                )
            return existing
        if not authorization_journal.mutation_precondition(
            auth_hash,
            entry_id_sha256=prepared.candidate_entry["entry_id_sha256"],
            projection_sha256=auth["projection_sha256"],
            target_scope=PROMOTION_SCOPE,
        ):
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_COMMIT_AUTHORIZATION_NO_LONGER_ACTIVE"
            )
        if prepared.shadow_runtime.snapshot().to_bytes() != prepared.projection_bytes:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_PREPARED_VM81_IMAGE_CHANGED"
            )
        if self.target.root_hash72() != prepared.target_root_before_hash72:
            raise Pass218CanonicalCommitStateError(
                "P218_I6_CANONICAL_TARGET_CHANGED_AFTER_PREPARE"
            )

        with self.target._lock:
            state = self.target._state
            current_root = self.target._root_for(state)
            if current_root != prepared.target_root_before_hash72:
                raise Pass218CanonicalCommitStateError(
                    "P218_I6_CANONICAL_TARGET_CHANGED_AFTER_PREPARE"
                )
            existing_locked = state.commits.get(auth_hash)
            if existing_locked is not None:
                if existing_locked.get("prepare_hash72") != prepared.prepare_hash72:
                    raise Pass218CanonicalCommitStateError(
                        "P218_I6_IDEMPOTENT_COMMIT_PREPARE_CONFLICT"
                    )
                return _copy(existing_locked)

            prospective_entries = dict(state.entries)
            prospective_entries[prepared.candidate_entry["entry_id_sha256"]] = _copy(
                prepared.admitted_entry
            )
            commit_index_row = {
                "authorization_hash72": auth_hash,
                "prepare_hash72": prepared.prepare_hash72,
                "candidate_entry_id_sha256": prepared.candidate_entry["entry_id_sha256"],
                "admitted_entry_id_sha256": prepared.admitted_entry["entry_id_sha256"],
                "projection_sha256": auth["projection_sha256"],
            }
            prospective_commits = dict(state.commits)
            prospective_commits[auth_hash] = commit_index_row
            prospective_state = _TargetState(
                runtime=prepared.shadow_runtime,
                entries=prospective_entries,
                commits=prospective_commits,
            )
            target_root_after = self.target._root_for(prospective_state)

            commit_payload = {
                "schema": "HHS-P218-I6-CANONICAL-COMMIT-PAYLOAD-V1",
                "authorization_hash72": auth_hash,
                "prepare_hash72": prepared.prepare_hash72,
                "candidate_entry_id_sha256": prepared.candidate_entry["entry_id_sha256"],
                "admitted_entry_id_sha256": prepared.admitted_entry["entry_id_sha256"],
                "projection_sha256": auth["projection_sha256"],
                "target_root_before_hash72": current_root,
                "target_root_after_hash72": target_root_after,
                "vm81_snapshot_hash72": prepared.shadow_runtime.snapshot_hash72,
                "vm81_state_hash72": prepared.shadow_runtime.state_hash72,
                "vm81_commit_count": len(prepared.vm81_receipts),
                "vm81_receipts_root_hash72": prepared.vm81_receipts_root_hash72,
                "canonical_vector_store_mutation_invoked": True,
                "canonical_vm81_commit_invoked": True,
                "canonical_learning_commit_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "verbatim_source_retained": False,
                "pass165_source_retaining_path_invoked": False,
            }
            commit_hash72 = hash72_digest(
                {"domain": "HHS-P218-I6-CANONICAL-COMMIT-V1"},
                commit_payload,
            )
            receipt_payload = {
                "schema": "HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-PAYLOAD-V1",
                "authorization_hash72": auth_hash,
                "prepare_hash72": prepared.prepare_hash72,
                "commit_hash72": commit_hash72,
                "target_root_after_hash72": target_root_after,
                "admission_status": CANONICAL_ADMISSION_STATUS,
                "authorization_consumed": True,
                "atomic_swap": True,
                "failed_partial_commit_possible": False,
                "source_retention_path_present": False,
                "learning_commit_path_present": False,
            }
            receipt_hash72 = hash72_digest(
                {"domain": "HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-V1"},
                receipt_payload,
            )
            commit_hash216 = (
                prepared.prepare_hash72 + commit_hash72 + receipt_hash72
            )
            if not _valid_hash216(commit_hash216):
                raise Pass218CanonicalCommitValidationError(
                    "P218_I6_COMMIT_HASH216_INVALID"
                )
            receipt = {
                "schema": "HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-V1",
                "boundary_version": PASS218_CANONICAL_COMMIT_VERSION,
                **commit_payload,
                "commit_hash72": commit_hash72,
                "receipt_hash72": receipt_hash72,
                "commit_hash216": commit_hash216,
                "hash216_semantics": [
                    "CANONICAL_TARGET_PREPARE",
                    "ATOMIC_CANONICAL_COMMIT",
                    "CANONICAL_COMMIT_RECEIPT",
                ],
                "state": "CANONICAL_COMMITTED",
                "authorization_consumed": True,
                "canonical_mutation_permitted": False,
                "atomic_swap": True,
                "failed_partial_commit_possible": False,
            }
            _reject_retained_source_surface(receipt)
            if fail_before_atomic_swap:
                raise Pass218CanonicalCommitStateError(
                    "P218_I6_INJECTED_COMMIT_FAILURE_BEFORE_ATOMIC_SWAP"
                )

            committed_rows = dict(prospective_commits)
            committed_rows[auth_hash] = _copy(receipt)
            committed_state = _TargetState(
                runtime=prepared.shadow_runtime,
                entries=prospective_entries,
                commits=committed_rows,
            )
            if self.target._root_for(committed_state) != target_root_after:
                raise Pass218CanonicalCommitStateError(
                    "P218_I6_CANONICAL_ROOT_SEAL_MISMATCH"
                )
            self.target._state = committed_state
            return _copy(receipt)

    def recover_failed_commit(
        self,
        prepared: PreparedCanonicalAdmission,
        *,
        authorization_journal: AuthorizationJournalProtocol,
        reason_code: str,
    ) -> dict[str, Any]:
        if not isinstance(reason_code, str) or not reason_code:
            raise Pass218CanonicalCommitValidationError(
                "P218_I6_RECOVERY_REASON_REQUIRED"
            )
        auth_hash = str(prepared.authorization["authorization_hash72"])
        if self.target.authorization_consumed(auth_hash):
            receipt = self.target.committed_receipt(auth_hash)
            if receipt is None:
                raise Pass218CanonicalCommitStateError(
                    "P218_I6_CONSUMED_AUTHORIZATION_RECEIPT_MISSING"
                )
            return receipt
        if self.target.root_hash72() != prepared.target_root_before_hash72:
            raise Pass218CanonicalCommitStateError(
                "P218_I6_RECOVERY_TARGET_ROOT_CHANGED"
            )
        active = authorization_journal.mutation_precondition(
            auth_hash,
            entry_id_sha256=prepared.candidate_entry["entry_id_sha256"],
            projection_sha256=prepared.authorization["projection_sha256"],
            target_scope=PROMOTION_SCOPE,
        )
        recovery_payload = {
            "schema": "HHS-P218-I6-FAILED-COMMIT-RECOVERY-V1",
            "authorization_hash72": auth_hash,
            "prepare_hash72": prepared.prepare_hash72,
            "candidate_entry_id_sha256": prepared.candidate_entry["entry_id_sha256"],
            "projection_sha256": prepared.authorization["projection_sha256"],
            "target_root_hash72": self.target.root_hash72(),
            "reason_code": reason_code,
            "authorization_still_active": active,
            "canonical_vector_store_mutation_invoked": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "verbatim_source_retained": False,
        }
        recovery_hash72 = hash72_digest(
            {"domain": "HHS-P218-I6-FAILED-COMMIT-RECOVERY-V1"},
            recovery_payload,
        )
        return {
            **recovery_payload,
            "recovery_hash72": recovery_hash72,
            "state": (
                "RECOVERABLE_PREPARED_NOT_COMMITTED"
                if active
                else "ABORTED_AUTHORIZATION_REVOKED"
            ),
            "retry_permitted": active,
            "truth_promotion": False,
            "action_authority_minted": False,
            "pass165_source_retaining_path_invoked": False,
        }
