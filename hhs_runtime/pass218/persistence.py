"""Pass 218 Iteration 7 durable canonical persistence and restart recovery.

This layer persists only already-committed Iteration-6 Pass-217/VM81 authority.
It never consumes a live Iteration-5 authorization, never reopens a source
transaction, and never invokes Pass-165 learning. Recovery reconstructs the
canonical target from its sealed committed entries, commit receipts, and exact
648-byte VM81 image.

Durability uses content-sealed generation files plus an atomically replaced
manifest. A generation is written and fsync'd before the manifest can point at
it. The manifest retains the immediately previous valid generation so a damaged
active generation can be rejected and the prior checkpoint recovered without
inventing authority.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES, THREADS
from hhs_runtime.pass218.commit_boundary import (
    CANONICAL_ADMISSION_STATUS,
    PASS217_VECTOR_ENTRY_SCHEMA,
    PASS218_CANONICAL_COMMIT_VERSION,
    Pass217VM81CanonicalTarget,
    _TargetState,
    _canonical_bytes,
    _copy,
    _prepare_vm81_shadow,
    _reject_retained_source_surface,
    _valid_hash216,
)

PASS218_PERSISTENCE_VERSION = "HHS-P218-DURABLE-CANONICAL-PERSISTENCE-I7-V1"
CHECKPOINT_SCHEMA = "HHS-P218-I7-DURABLE-CANONICAL-CHECKPOINT-V1"
MANIFEST_SCHEMA = "HHS-P218-I7-DURABLE-CANONICAL-MANIFEST-V1"
RESTORE_SCHEMA = "HHS-P218-I7-DURABLE-CANONICAL-RESTORE-RECEIPT-V1"
GENERATION_DIRNAME = "generations"
MANIFEST_FILENAME = "manifest.json"


class Pass218PersistenceError(RuntimeError):
    pass


class Pass218PersistenceValidationError(Pass218PersistenceError):
    pass


class Pass218PersistenceStateError(Pass218PersistenceError):
    pass


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _require_false(record: Mapping[str, Any], key: str) -> None:
    if record.get(key) is not False:
        raise Pass218PersistenceValidationError(
            "P218_I7_FORBIDDEN_AUTHORITY_FLAG:" + key
        )


def _require_true(record: Mapping[str, Any], key: str) -> None:
    if record.get(key) is not True:
        raise Pass218PersistenceValidationError(
            "P218_I7_REQUIRED_COMMIT_FLAG:" + key
        )


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=".p218-i7-",
        suffix=".tmp",
        dir=str(path.parent),
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        try:
            directory_fd = os.open(str(path.parent), os.O_RDONLY)
        except OSError:
            directory_fd = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _read_canonical_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise Pass218PersistenceValidationError(
            "P218_I7_PERSISTED_FILE_UNREADABLE:" + path.name
        ) from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise Pass218PersistenceValidationError(
            "P218_I7_PERSISTED_JSON_INVALID:" + path.name
        ) from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != raw:
        raise Pass218PersistenceValidationError(
            "P218_I7_PERSISTED_JSON_NONCANONICAL:" + path.name
        )
    _reject_retained_source_surface(value)
    return value


def _generation_filename(sequence: int, checkpoint_sha256: str) -> str:
    if (
        not isinstance(sequence, int)
        or isinstance(sequence, bool)
        or sequence < 0
        or not _valid_sha256(checkpoint_sha256)
    ):
        raise Pass218PersistenceValidationError(
            "P218_I7_GENERATION_IDENTITY_INVALID"
        )
    return f"checkpoint-{sequence:020d}-{checkpoint_sha256}.json"


def _validate_admitted_entry(
    candidate_entry_id_sha256: str,
    entry: Mapping[str, Any],
) -> dict[str, Any]:
    row = _copy(entry)
    _reject_retained_source_surface(row)
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
    if set(row) != required:
        raise Pass218PersistenceValidationError(
            "P218_I7_ADMITTED_ENTRY_FIELD_SET_INVALID"
        )
    if row.get("schema") != PASS217_VECTOR_ENTRY_SCHEMA:
        raise Pass218PersistenceValidationError(
            "P218_I7_ADMITTED_ENTRY_SCHEMA_INVALID"
        )
    if row.get("admission_status") != CANONICAL_ADMISSION_STATUS:
        raise Pass218PersistenceValidationError(
            "P218_I7_ADMITTED_ENTRY_STATE_INVALID"
        )
    for key in (
        "entry_id_sha256",
        "parent_state_sha256",
        "candidate_state_sha256",
        "hash216_transition_sha256",
    ):
        if not _valid_sha256(row.get(key)):
            raise Pass218PersistenceValidationError(
                "P218_I7_ADMITTED_ENTRY_SHA256_INVALID:" + key
            )
    if not _valid_sha256(candidate_entry_id_sha256):
        raise Pass218PersistenceValidationError(
            "P218_I7_CANDIDATE_ENTRY_KEY_INVALID"
        )
    return row


def _validate_commit_receipt(
    authorization_hash72: str,
    receipt: Mapping[str, Any],
    entries: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    row = _copy(receipt)
    _reject_retained_source_surface(row)
    if row.get("schema") != "HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-V1":
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_RECEIPT_SCHEMA_INVALID"
        )
    if row.get("boundary_version") != PASS218_CANONICAL_COMMIT_VERSION:
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_BOUNDARY_VERSION_INVALID"
        )
    if row.get("authorization_hash72") != authorization_hash72:
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_AUTHORIZATION_KEY_MISMATCH"
        )
    for key in (
        "authorization_hash72",
        "prepare_hash72",
        "target_root_before_hash72",
        "target_root_after_hash72",
        "vm81_snapshot_hash72",
        "vm81_state_hash72",
        "vm81_receipts_root_hash72",
        "commit_hash72",
        "receipt_hash72",
    ):
        if not validate_hash72(str(row.get(key) or "")):
            raise Pass218PersistenceValidationError(
                "P218_I7_COMMIT_HASH72_INVALID:" + key
            )
    if not _valid_hash216(row.get("commit_hash216")):
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_HASH216_INVALID"
        )
    for key in (
        "candidate_entry_id_sha256",
        "admitted_entry_id_sha256",
        "projection_sha256",
    ):
        if not _valid_sha256(row.get(key)):
            raise Pass218PersistenceValidationError(
                "P218_I7_COMMIT_SHA256_INVALID:" + key
            )
    _require_true(row, "canonical_vector_store_mutation_invoked")
    _require_true(row, "canonical_vm81_commit_invoked")
    _require_true(row, "authorization_consumed")
    _require_true(row, "atomic_swap")
    for key in (
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
        "canonical_mutation_permitted",
        "failed_partial_commit_possible",
    ):
        _require_false(row, key)
    if row.get("state") != "CANONICAL_COMMITTED":
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_STATE_INVALID"
        )
    if row.get("vm81_commit_count") != THREADS:
        raise Pass218PersistenceValidationError(
            "P218_I7_VM81_COMMIT_COUNT_INVALID"
        )

    candidate_id = row["candidate_entry_id_sha256"]
    entry = entries.get(candidate_id)
    if entry is None:
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_ENTRY_MISSING"
        )
    admitted = _validate_admitted_entry(candidate_id, entry)
    if admitted["entry_id_sha256"] != row["admitted_entry_id_sha256"]:
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_ADMITTED_ENTRY_MISMATCH"
        )

    commit_payload = {
        "schema": "HHS-P218-I6-CANONICAL-COMMIT-PAYLOAD-V1",
        "authorization_hash72": authorization_hash72,
        "prepare_hash72": row["prepare_hash72"],
        "candidate_entry_id_sha256": candidate_id,
        "admitted_entry_id_sha256": row["admitted_entry_id_sha256"],
        "projection_sha256": row["projection_sha256"],
        "target_root_before_hash72": row["target_root_before_hash72"],
        "target_root_after_hash72": row["target_root_after_hash72"],
        "vm81_snapshot_hash72": row["vm81_snapshot_hash72"],
        "vm81_state_hash72": row["vm81_state_hash72"],
        "vm81_commit_count": row["vm81_commit_count"],
        "vm81_receipts_root_hash72": row["vm81_receipts_root_hash72"],
        "canonical_vector_store_mutation_invoked": True,
        "canonical_vm81_commit_invoked": True,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }
    expected_commit_hash72 = hash72_digest(
        {"domain": "HHS-P218-I6-CANONICAL-COMMIT-V1"},
        commit_payload,
    )
    if expected_commit_hash72 != row["commit_hash72"]:
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_HASH72_MISMATCH"
        )

    receipt_payload = {
        "schema": "HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-PAYLOAD-V1",
        "authorization_hash72": authorization_hash72,
        "prepare_hash72": row["prepare_hash72"],
        "commit_hash72": row["commit_hash72"],
        "target_root_after_hash72": row["target_root_after_hash72"],
        "admission_status": CANONICAL_ADMISSION_STATUS,
        "authorization_consumed": True,
        "atomic_swap": True,
        "failed_partial_commit_possible": False,
        "source_retention_path_present": False,
        "learning_commit_path_present": False,
    }
    expected_receipt_hash72 = hash72_digest(
        {"domain": "HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-V1"},
        receipt_payload,
    )
    if expected_receipt_hash72 != row["receipt_hash72"]:
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_RECEIPT_HASH72_MISMATCH"
        )
    expected_hash216 = (
        row["prepare_hash72"] + row["commit_hash72"] + row["receipt_hash72"]
    )
    if expected_hash216 != row["commit_hash216"]:
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMIT_HASH216_MISMATCH"
        )
    return row


def _ordered_receipt_chain(
    commits: Mapping[str, Mapping[str, Any]],
    initial_root_hash72: str,
) -> tuple[dict[str, Any], ...]:
    unused = {key: _copy(value) for key, value in commits.items()}
    ordered: list[dict[str, Any]] = []
    current = initial_root_hash72
    while unused:
        matches = [
            (key, value)
            for key, value in unused.items()
            if value.get("target_root_before_hash72") == current
        ]
        if len(matches) != 1:
            raise Pass218PersistenceValidationError(
                "P218_I7_COMMIT_ROOT_CHAIN_AMBIGUOUS"
            )
        key, value = matches[0]
        ordered.append(value)
        current = value["target_root_after_hash72"]
        del unused[key]
    return tuple(ordered)


def _checkpoint_payload_from_target(
    target: Pass217VM81CanonicalTarget,
    *,
    sequence: int,
    previous_checkpoint_sha256: str | None,
) -> dict[str, Any]:
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
        raise Pass218PersistenceValidationError(
            "P218_I7_CHECKPOINT_SEQUENCE_INVALID"
        )
    if previous_checkpoint_sha256 is not None and not _valid_sha256(
        previous_checkpoint_sha256
    ):
        raise Pass218PersistenceValidationError(
            "P218_I7_PREVIOUS_CHECKPOINT_SHA256_INVALID"
        )
    with target._lock:
        state = target._state
        entries = {key: _copy(value) for key, value in state.entries.items()}
        commits = {key: _copy(value) for key, value in state.commits.items()}
        snapshot = state.runtime.snapshot().to_bytes()
        target_record = target.record()
    if not commits:
        raise Pass218PersistenceStateError(
            "P218_I7_EMPTY_CANONICAL_TARGET_NOT_PERSISTABLE"
        )
    payload = {
        "schema": CHECKPOINT_SCHEMA,
        "persistence_version": PASS218_PERSISTENCE_VERSION,
        "generation_sequence": sequence,
        "previous_checkpoint_sha256": previous_checkpoint_sha256,
        "canonical_target_record": target_record,
        "vm81_snapshot_b64": b64encode(snapshot).decode("ascii"),
        "vm81_snapshot_sha256": sha256(snapshot).hexdigest(),
        "entries_by_candidate_id": entries,
        "commits_by_authorization_hash72": commits,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }
    _reject_retained_source_surface(payload)
    return payload


def seal_checkpoint(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = _copy(payload)
    if body.get("schema") != CHECKPOINT_SCHEMA:
        raise Pass218PersistenceValidationError(
            "P218_I7_CHECKPOINT_SCHEMA_INVALID"
        )
    _reject_retained_source_surface(body)
    canonical = _canonical_bytes(body)
    checkpoint_sha256 = sha256(
        b"HHS-P218-I7-DURABLE-CANONICAL-CHECKPOINT-V1\0" + canonical
    ).hexdigest()
    checkpoint_hash72 = hash72_digest(
        {"domain": "HHS-P218-I7-DURABLE-CANONICAL-CHECKPOINT-V1"},
        body,
    )
    target_root = body["canonical_target_record"]["canonical_root_hash72"]
    validation_payload = {
        "schema": "HHS-P218-I7-DURABLE-CANONICAL-CHECKPOINT-VALIDATION-V1",
        "checkpoint_sha256": checkpoint_sha256,
        "checkpoint_hash72": checkpoint_hash72,
        "canonical_root_hash72": target_root,
        "vm81_snapshot_sha256": body["vm81_snapshot_sha256"],
        "entry_count": len(body["entries_by_candidate_id"]),
        "commit_count": len(body["commits_by_authorization_hash72"]),
        "source_retention_path_present": False,
        "learning_commit_path_present": False,
        "new_mutation_authority_minted": False,
    }
    validation_hash72 = hash72_digest(
        {"domain": "HHS-P218-I7-DURABLE-CANONICAL-CHECKPOINT-VALIDATION-V1"},
        validation_payload,
    )
    checkpoint_hash216 = target_root + checkpoint_hash72 + validation_hash72
    if not _valid_hash216(checkpoint_hash216):
        raise Pass218PersistenceValidationError(
            "P218_I7_CHECKPOINT_HASH216_INVALID"
        )
    return {
        **body,
        "checkpoint_sha256": checkpoint_sha256,
        "checkpoint_hash72": checkpoint_hash72,
        "validation_hash72": validation_hash72,
        "checkpoint_hash216": checkpoint_hash216,
        "hash216_semantics": [
            "CANONICAL_COMMITTED_TARGET",
            "DURABLE_CANONICAL_CHECKPOINT",
            "CHECKPOINT_VALIDATION_RECEIPT",
        ],
    }


def _checkpoint_payload_from_sealed(record: Mapping[str, Any]) -> dict[str, Any]:
    excluded = {
        "checkpoint_sha256",
        "checkpoint_hash72",
        "validation_hash72",
        "checkpoint_hash216",
        "hash216_semantics",
    }
    return {
        key: _copy(value)
        for key, value in record.items()
        if key not in excluded
    }


def validate_checkpoint(record: Mapping[str, Any]) -> dict[str, Any]:
    sealed = _copy(record)
    _reject_retained_source_surface(sealed)
    if sealed.get("schema") != CHECKPOINT_SCHEMA:
        raise Pass218PersistenceValidationError(
            "P218_I7_CHECKPOINT_SCHEMA_INVALID"
        )
    if sealed.get("persistence_version") != PASS218_PERSISTENCE_VERSION:
        raise Pass218PersistenceValidationError(
            "P218_I7_CHECKPOINT_VERSION_INVALID"
        )
    for key in (
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
    ):
        _require_false(sealed, key)

    expected = seal_checkpoint(_checkpoint_payload_from_sealed(sealed))
    for key in (
        "checkpoint_sha256",
        "checkpoint_hash72",
        "validation_hash72",
        "checkpoint_hash216",
        "hash216_semantics",
    ):
        if sealed.get(key) != expected.get(key):
            raise Pass218PersistenceValidationError(
                "P218_I7_CHECKPOINT_SEAL_MISMATCH:" + key
            )

    target_record = sealed.get("canonical_target_record")
    entries = sealed.get("entries_by_candidate_id")
    commits = sealed.get("commits_by_authorization_hash72")
    if not isinstance(target_record, dict):
        raise Pass218PersistenceValidationError(
            "P218_I7_TARGET_RECORD_INVALID"
        )
    if not isinstance(entries, dict) or not entries:
        raise Pass218PersistenceValidationError(
            "P218_I7_ENTRIES_INVALID"
        )
    if not isinstance(commits, dict) or not commits:
        raise Pass218PersistenceValidationError(
            "P218_I7_COMMITS_INVALID"
        )
    _require_false(target_record, "canonical_learning_authority")
    _require_false(target_record, "source_retention_authority")
    if target_record.get("boundary_version") != PASS218_CANONICAL_COMMIT_VERSION:
        raise Pass218PersistenceValidationError(
            "P218_I7_TARGET_BOUNDARY_VERSION_INVALID"
        )
    canonical_root = target_record.get("canonical_root_hash72")
    if not validate_hash72(str(canonical_root or "")):
        raise Pass218PersistenceValidationError(
            "P218_I7_TARGET_ROOT_INVALID"
        )
    if target_record.get("canonical_entry_count") != len(entries):
        raise Pass218PersistenceValidationError(
            "P218_I7_TARGET_ENTRY_COUNT_MISMATCH"
        )
    if target_record.get("canonical_commit_count") != len(commits):
        raise Pass218PersistenceValidationError(
            "P218_I7_TARGET_COMMIT_COUNT_MISMATCH"
        )

    validated_entries = {
        key: _validate_admitted_entry(key, value)
        for key, value in entries.items()
    }
    validated_commits = {
        key: _validate_commit_receipt(key, value, validated_entries)
        for key, value in commits.items()
    }

    initial_root = Pass217VM81CanonicalTarget().root_hash72()
    chain = _ordered_receipt_chain(validated_commits, initial_root)
    if chain[-1]["target_root_after_hash72"] != canonical_root:
        raise Pass218PersistenceValidationError(
            "P218_I7_FINAL_COMMIT_ROOT_MISMATCH"
        )

    try:
        snapshot = b64decode(str(sealed["vm81_snapshot_b64"]), validate=True)
    except Exception as exc:
        raise Pass218PersistenceValidationError(
            "P218_I7_VM81_SNAPSHOT_B64_INVALID"
        ) from exc
    if len(snapshot) != SNAPSHOT_BYTES:
        raise Pass218PersistenceValidationError(
            "P218_I7_VM81_SNAPSHOT_LENGTH_INVALID"
        )
    if b64encode(snapshot).decode("ascii") != sealed["vm81_snapshot_b64"]:
        raise Pass218PersistenceValidationError(
            "P218_I7_VM81_SNAPSHOT_B64_NONCANONICAL"
        )
    if sha256(snapshot).hexdigest() != sealed.get("vm81_snapshot_sha256"):
        raise Pass218PersistenceValidationError(
            "P218_I7_VM81_SNAPSHOT_SHA256_MISMATCH"
        )

    final_receipt = chain[-1]
    if sha256(snapshot).hexdigest() != final_receipt["projection_sha256"]:
        raise Pass218PersistenceValidationError(
            "P218_I7_FINAL_PROJECTION_SHA256_MISMATCH"
        )
    final_entry = validated_entries[final_receipt["candidate_entry_id_sha256"]]
    runtime, vm81_receipts, receipts_root = _prepare_vm81_shadow(
        snapshot,
        dependency_root=final_entry["hash216_transition_sha256"],
    )
    if runtime.epoch != THREADS:
        raise Pass218PersistenceValidationError(
            "P218_I7_RESTORED_VM81_EPOCH_INVALID"
        )
    if runtime.snapshot_hash72 != target_record.get("vm81_snapshot_hash72"):
        raise Pass218PersistenceValidationError(
            "P218_I7_RESTORED_VM81_SNAPSHOT_ROOT_MISMATCH"
        )
    if runtime.state_hash72 != target_record.get("vm81_state_hash72"):
        raise Pass218PersistenceValidationError(
            "P218_I7_RESTORED_VM81_STATE_ROOT_MISMATCH"
        )
    if final_receipt["vm81_snapshot_hash72"] != runtime.snapshot_hash72:
        raise Pass218PersistenceValidationError(
            "P218_I7_FINAL_RECEIPT_VM81_SNAPSHOT_MISMATCH"
        )
    if final_receipt["vm81_state_hash72"] != runtime.state_hash72:
        raise Pass218PersistenceValidationError(
            "P218_I7_FINAL_RECEIPT_VM81_STATE_MISMATCH"
        )
    if final_receipt["vm81_receipts_root_hash72"] != receipts_root:
        raise Pass218PersistenceValidationError(
            "P218_I7_REPLAYED_VM81_RECEIPT_ROOT_MISMATCH"
        )
    if len(vm81_receipts) != THREADS:
        raise Pass218PersistenceValidationError(
            "P218_I7_REPLAYED_VM81_RECEIPT_COUNT_INVALID"
        )

    restored_state = _TargetState(
        runtime=runtime,
        entries=validated_entries,
        commits=validated_commits,
    )
    if Pass217VM81CanonicalTarget._root_for(restored_state) != canonical_root:
        raise Pass218PersistenceValidationError(
            "P218_I7_RESTORED_CANONICAL_ROOT_MISMATCH"
        )
    return sealed


def restore_target_from_checkpoint(
    record: Mapping[str, Any],
) -> Pass217VM81CanonicalTarget:
    sealed = validate_checkpoint(record)
    target_record = sealed["canonical_target_record"]
    entries = {
        key: _copy(value)
        for key, value in sealed["entries_by_candidate_id"].items()
    }
    commits = {
        key: _copy(value)
        for key, value in sealed["commits_by_authorization_hash72"].items()
    }
    snapshot = b64decode(sealed["vm81_snapshot_b64"], validate=True)
    final_receipt = _ordered_receipt_chain(
        commits,
        Pass217VM81CanonicalTarget().root_hash72(),
    )[-1]
    final_entry = entries[final_receipt["candidate_entry_id_sha256"]]
    runtime, _, _ = _prepare_vm81_shadow(
        snapshot,
        dependency_root=final_entry["hash216_transition_sha256"],
    )
    target = Pass217VM81CanonicalTarget()
    with target._lock:
        target._state = _TargetState(
            runtime=runtime,
            entries=entries,
            commits=commits,
        )
        if target._root_for(target._state) != target_record["canonical_root_hash72"]:
            raise Pass218PersistenceValidationError(
                "P218_I7_RESTORE_INSTALL_ROOT_MISMATCH"
            )
    return target


def _manifest_payload(
    *,
    sequence: int,
    active_generation: str,
    active_checkpoint_sha256: str,
    active_checkpoint_hash72: str,
    canonical_root_hash72: str,
    previous_generation: str | None,
    previous_checkpoint_sha256: str | None,
) -> dict[str, Any]:
    return {
        "schema": MANIFEST_SCHEMA,
        "persistence_version": PASS218_PERSISTENCE_VERSION,
        "generation_sequence": sequence,
        "active_generation": active_generation,
        "active_checkpoint_sha256": active_checkpoint_sha256,
        "active_checkpoint_hash72": active_checkpoint_hash72,
        "canonical_root_hash72": canonical_root_hash72,
        "previous_generation": previous_generation,
        "previous_checkpoint_sha256": previous_checkpoint_sha256,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }


def seal_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = _copy(payload)
    if body.get("schema") != MANIFEST_SCHEMA:
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_SCHEMA_INVALID"
        )
    _reject_retained_source_surface(body)
    manifest_hash72 = hash72_digest(
        {"domain": "HHS-P218-I7-DURABLE-CANONICAL-MANIFEST-V1"},
        body,
    )
    return {**body, "manifest_hash72": manifest_hash72}


def validate_manifest(record: Mapping[str, Any]) -> dict[str, Any]:
    manifest = _copy(record)
    _reject_retained_source_surface(manifest)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_SCHEMA_INVALID"
        )
    if manifest.get("persistence_version") != PASS218_PERSISTENCE_VERSION:
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_VERSION_INVALID"
        )
    for key in (
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
    ):
        _require_false(manifest, key)
    supplied = manifest.get("manifest_hash72")
    if not validate_hash72(str(supplied or "")):
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_HASH72_INVALID"
        )
    body = {
        key: _copy(value)
        for key, value in manifest.items()
        if key != "manifest_hash72"
    }
    if seal_manifest(body)["manifest_hash72"] != supplied:
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_HASH72_MISMATCH"
        )
    if not _valid_sha256(manifest.get("active_checkpoint_sha256")):
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_ACTIVE_SHA256_INVALID"
        )
    if not validate_hash72(str(manifest.get("active_checkpoint_hash72") or "")):
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_ACTIVE_HASH72_INVALID"
        )
    if not validate_hash72(str(manifest.get("canonical_root_hash72") or "")):
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_CANONICAL_ROOT_INVALID"
        )
    sequence = manifest.get("generation_sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_SEQUENCE_INVALID"
        )
    if manifest.get("active_generation") != _generation_filename(
        sequence,
        manifest["active_checkpoint_sha256"],
    ):
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_ACTIVE_GENERATION_INVALID"
        )
    previous_sha = manifest.get("previous_checkpoint_sha256")
    previous_generation = manifest.get("previous_generation")
    if (previous_sha is None) != (previous_generation is None):
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_PREVIOUS_PAIR_INVALID"
        )
    if previous_sha is not None and not _valid_sha256(previous_sha):
        raise Pass218PersistenceValidationError(
            "P218_I7_MANIFEST_PREVIOUS_SHA256_INVALID"
        )
    return manifest


@dataclass(frozen=True)
class DurableRestoreResult:
    target: Pass217VM81CanonicalTarget
    checkpoint: Mapping[str, Any]
    manifest: Mapping[str, Any]
    state: str
    recovered_previous_generation: bool
    restore_hash72: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": RESTORE_SCHEMA,
            "persistence_version": PASS218_PERSISTENCE_VERSION,
            "state": self.state,
            "generation_sequence": self.checkpoint["generation_sequence"],
            "checkpoint_sha256": self.checkpoint["checkpoint_sha256"],
            "checkpoint_hash72": self.checkpoint["checkpoint_hash72"],
            "canonical_root_hash72": self.target.root_hash72(),
            "recovered_previous_generation": self.recovered_previous_generation,
            "restore_hash72": self.restore_hash72,
            "new_canonical_mutation_invoked": False,
            "new_authorization_minted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
        }


class Pass218DurableCanonicalStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root)
        self.generations = self.root / GENERATION_DIRNAME
        self.manifest_path = self.root / MANIFEST_FILENAME

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            raise Pass218PersistenceStateError(
                "P218_I7_MANIFEST_NOT_FOUND"
            )
        return validate_manifest(_read_canonical_json(self.manifest_path))

    def _load_generation(
        self,
        filename: str,
        *,
        expected_sha256: str,
    ) -> dict[str, Any]:
        path = self.generations / filename
        checkpoint = validate_checkpoint(_read_canonical_json(path))
        if checkpoint["checkpoint_sha256"] != expected_sha256:
            raise Pass218PersistenceValidationError(
                "P218_I7_GENERATION_SHA256_MISMATCH"
            )
        return checkpoint

    def checkpoint(
        self,
        target: Pass217VM81CanonicalTarget,
        *,
        fail_before_manifest_swap: bool = False,
    ) -> dict[str, Any]:
        previous_manifest = None
        if self.manifest_path.exists():
            previous_manifest = self._load_manifest()
            if previous_manifest["canonical_root_hash72"] == target.root_hash72():
                active = self._load_generation(
                    previous_manifest["active_generation"],
                    expected_sha256=previous_manifest["active_checkpoint_sha256"],
                )
                if (
                    active["canonical_target_record"]["canonical_root_hash72"]
                    == target.root_hash72()
                    and active["vm81_snapshot_sha256"]
                    == sha256(target.snapshot_bytes()).hexdigest()
                ):
                    return {
                        "state": "DURABLE_CHECKPOINT_IDEMPOTENT_REPLAY",
                        "idempotent_replay": True,
                        "checkpoint": active,
                        "manifest": previous_manifest,
                    }

        sequence = (
            0
            if previous_manifest is None
            else previous_manifest["generation_sequence"] + 1
        )
        previous_sha = (
            None
            if previous_manifest is None
            else previous_manifest["active_checkpoint_sha256"]
        )
        payload = _checkpoint_payload_from_target(
            target,
            sequence=sequence,
            previous_checkpoint_sha256=previous_sha,
        )
        checkpoint = seal_checkpoint(payload)
        filename = _generation_filename(
            sequence,
            checkpoint["checkpoint_sha256"],
        )
        generation_path = self.generations / filename
        generation_bytes = _canonical_bytes(checkpoint)
        if generation_path.exists():
            if generation_path.read_bytes() != generation_bytes:
                raise Pass218PersistenceStateError(
                    "P218_I7_GENERATION_PATH_COLLISION"
                )
        else:
            _atomic_write(generation_path, generation_bytes)

        if fail_before_manifest_swap:
            raise Pass218PersistenceStateError(
                "P218_I7_INJECTED_FAILURE_BEFORE_MANIFEST_SWAP"
            )

        manifest = seal_manifest(
            _manifest_payload(
                sequence=sequence,
                active_generation=filename,
                active_checkpoint_sha256=checkpoint["checkpoint_sha256"],
                active_checkpoint_hash72=checkpoint["checkpoint_hash72"],
                canonical_root_hash72=target.root_hash72(),
                previous_generation=(
                    None
                    if previous_manifest is None
                    else previous_manifest["active_generation"]
                ),
                previous_checkpoint_sha256=previous_sha,
            )
        )
        _atomic_write(self.manifest_path, _canonical_bytes(manifest))
        return {
            "state": "DURABLE_CHECKPOINT_COMMITTED",
            "idempotent_replay": False,
            "checkpoint": checkpoint,
            "manifest": manifest,
        }

    def restore(self, *, allow_previous_generation: bool = True) -> DurableRestoreResult:
        manifest = self._load_manifest()
        recovered_previous = False
        try:
            checkpoint = self._load_generation(
                manifest["active_generation"],
                expected_sha256=manifest["active_checkpoint_sha256"],
            )
            if checkpoint["checkpoint_hash72"] != manifest["active_checkpoint_hash72"]:
                raise Pass218PersistenceValidationError(
                    "P218_I7_ACTIVE_CHECKPOINT_HASH72_MISMATCH"
                )
            if (
                checkpoint["canonical_target_record"]["canonical_root_hash72"]
                != manifest["canonical_root_hash72"]
            ):
                raise Pass218PersistenceValidationError(
                    "P218_I7_ACTIVE_CANONICAL_ROOT_MISMATCH"
                )
            state = "RESTORED_ACTIVE_GENERATION"
        except Pass218PersistenceError:
            if not allow_previous_generation:
                raise
            previous_generation = manifest.get("previous_generation")
            previous_sha = manifest.get("previous_checkpoint_sha256")
            if previous_generation is None or previous_sha is None:
                raise
            checkpoint = self._load_generation(
                previous_generation,
                expected_sha256=previous_sha,
            )
            recovered_previous = True
            state = "RECOVERED_PREVIOUS_VALID_GENERATION"

        target = restore_target_from_checkpoint(checkpoint)
        restore_payload = {
            "schema": RESTORE_SCHEMA,
            "checkpoint_sha256": checkpoint["checkpoint_sha256"],
            "checkpoint_hash72": checkpoint["checkpoint_hash72"],
            "canonical_root_hash72": target.root_hash72(),
            "generation_sequence": checkpoint["generation_sequence"],
            "state": state,
            "recovered_previous_generation": recovered_previous,
            "new_canonical_mutation_invoked": False,
            "new_authorization_minted": False,
            "canonical_learning_commit_invoked": False,
            "verbatim_source_retained": False,
        }
        restore_hash72 = hash72_digest(
            {"domain": "HHS-P218-I7-DURABLE-CANONICAL-RESTORE-V1"},
            restore_payload,
        )
        result = DurableRestoreResult(
            target=target,
            checkpoint=checkpoint,
            manifest=manifest,
            state=state,
            recovered_previous_generation=recovered_previous,
            restore_hash72=restore_hash72,
        )
        _reject_retained_source_surface(result.to_record())
        return result
