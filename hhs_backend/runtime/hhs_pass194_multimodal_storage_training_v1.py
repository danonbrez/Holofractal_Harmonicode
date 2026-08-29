"""Pass 194 multimodal storage, snapshot, dataset, and training-lineage runtime.

This module implements the authorized Pass 194 storage boundary by composing
existing HHS primitives. It does not create a second VM81 authority. Every
canonical metadata mutation consumes one already-authorized VM81 execution
receipt, while blob identity, snapshots, encrypted vectors, datasets, and
training/checkpoint records remain bounded data/lineage authorities only.
"""
from __future__ import annotations

from base64 import b64encode
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, Iterator, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import _validated_authorized_tick
from hhs_runtime.pass174.runtime import Hash216Array
from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore

VERSION = "HHS-P194-UMFFHS-SQLCG-EVS-AGITC-VM81-H72-H216-1.0.0"
CONTRACT_ID = "HHS-P194-UMFFHS-SQLCG-EVS-AGITC-VM81-H72-H216"
CONTRACT_AUTHORIZATION_COMMIT = "714f3f3c5c77eab9714be421811ce4fd650a8e99"
CONTRACT_BASELINE = "31aad2b8281c9a68c5f810948dac630dd5a387e0"
FROZEN_I131 = "b8202201bc92470afdd15d701d16ea102aeb3aab"
GENESIS_IDENTITY = sha256(("HHS-P194-GENESIS:" + FROZEN_I131).encode("ascii")).hexdigest()
LEGACY_FOUNDATION_ROOT = sha256(
    ("HHS-P194-INHERITED-FOUNDATION:" + CONTRACT_AUTHORIZATION_COMMIT).encode("ascii")
).hexdigest()
ALLOWED_RUN_KINDS = frozenset({"TRAINING", "FINE_TUNE", "EVALUATION"})
MAX_METADATA_JSON_BYTES = 64 * 1024
MAX_RELATION_TEXT_BYTES = 256
MAX_MODEL_ID_BYTES = 512


class Pass194Error(RuntimeError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass194Error("HHS_P194_FLOAT_CANONICAL_METADATA_FORBIDDEN", path)
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _bounded_text(value: str, label: str, limit: int) -> str:
    if not isinstance(value, str) or not value:
        raise Pass194Error("HHS_P194_TEXT_REQUIRED", label)
    if len(value.encode("utf-8")) > limit:
        raise Pass194Error("HHS_P194_TEXT_LIMIT", label)
    return value


def _hash72(domain: str, payload: Any) -> str:
    return hash72_digest({"domain": domain, "contract": CONTRACT_ID}, payload)


def _sha256_id(domain: str, payload: Any) -> str:
    return sha256(domain.encode("ascii") + b"\0" + _canonical(payload)).hexdigest()


def _authority_lineage(execution: Mapping[str, Any]) -> tuple[str, str]:
    try:
        validated = _validated_authorized_tick(execution)
    except Exception as exc:
        raise Pass194Error("HHS_P194_VM81_AUTHORITY_REQUIRED") from exc
    receipt = validated["receipt"]
    state_hash72 = receipt["state_hash72"]
    receipt_hash72 = receipt["receipt_hash72"]
    if not validate_hash72(state_hash72) or not validate_hash72(receipt_hash72):
        raise Pass194Error("HHS_P194_VM81_AUTHORITY_HASH72_INVALID")
    return state_hash72, receipt_hash72


class Pass194Runtime:
    """Canonical Pass 194 relational/storage runtime.

    Source bytes are content addressed and immutable. SQL is the metadata
    authority after a validated VM81 execution receipt is consumed. Vectors are
    encrypted derived projections and carry no source, consent, dataset, or
    mutation authority.
    """

    def __init__(self, state_root: str | Path, *, vector_key: bytes | None = None) -> None:
        self.state_root = Path(state_root).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.blob_root = self.state_root / "blobs" / "sha256"
        self.snapshot_root = self.state_root / "snapshots"
        self.blob_root.mkdir(parents=True, exist_ok=True)
        self.snapshot_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "pass194.sqlite3"
        self.vector_database_path = self.state_root / "pass194_vectors.sqlite3"
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._init_schema()
        self.vector_store = PersistentEncryptedVectorStore(
            self.vector_database_path,
            key=vector_key,
            key_path=self.state_root / "pass194_vectors.key",
        )

    def _init_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS workspaces (
                workspace_id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                created_receipt_hash72 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id),
                logical_path TEXT NOT NULL,
                active_version_id TEXT,
                tombstoned INTEGER NOT NULL DEFAULT 0,
                created_receipt_hash72 TEXT NOT NULL,
                UNIQUE(workspace_id, logical_path)
            );
            CREATE TABLE IF NOT EXISTS file_versions (
                file_version_id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL REFERENCES files(file_id),
                version_index INTEGER NOT NULL,
                blob_sha256 TEXT NOT NULL,
                source_hash72 TEXT NOT NULL,
                modality TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                created_receipt_hash72 TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0,
                UNIQUE(file_id, version_index)
            );
            CREATE TABLE IF NOT EXISTS relationships (
                edge_id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id),
                from_object_id TEXT NOT NULL,
                relation TEXT NOT NULL,
                to_object_id TEXT NOT NULL,
                created_receipt_hash72 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                file_version_id TEXT NOT NULL REFERENCES file_versions(file_version_id),
                training_allowed INTEGER NOT NULL DEFAULT 0,
                sharing_allowed INTEGER NOT NULL DEFAULT 0,
                public_allowed INTEGER NOT NULL DEFAULT 0,
                license_id TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_receipt_hash72 TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS consent_active_idx
                ON consent_records(file_version_id, active);
            CREATE TABLE IF NOT EXISTS vector_projections (
                projection_id TEXT PRIMARY KEY,
                file_version_id TEXT NOT NULL REFERENCES file_versions(file_version_id),
                vector_object_id TEXT NOT NULL,
                operation_key TEXT NOT NULL,
                model_id TEXT NOT NULL,
                hash216_index_root_sha256 TEXT NOT NULL,
                vector_is_source_authority INTEGER NOT NULL DEFAULT 0,
                vector_is_consent_authority INTEGER NOT NULL DEFAULT 0,
                vector_is_vm81_authority INTEGER NOT NULL DEFAULT 0,
                created_receipt_hash72 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id),
                manifest_json TEXT NOT NULL,
                manifest_hash72 TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0,
                created_receipt_hash72 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dataset_releases (
                dataset_id TEXT PRIMARY KEY,
                snapshot_id TEXT NOT NULL REFERENCES snapshots(snapshot_id),
                manifest_json TEXT NOT NULL,
                dataset_hash72 TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0,
                created_receipt_hash72 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS training_runs (
                run_id TEXT PRIMARY KEY,
                dataset_id TEXT NOT NULL REFERENCES dataset_releases(dataset_id),
                run_kind TEXT NOT NULL,
                model_base_id TEXT NOT NULL,
                status TEXT NOT NULL,
                training_provider_is_vm81_authority INTEGER NOT NULL DEFAULT 0,
                created_receipt_hash72 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL REFERENCES training_runs(run_id),
                artifact_sha256 TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                checkpoint_is_vm81_authority INTEGER NOT NULL DEFAULT 0,
                created_receipt_hash72 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tombstones (
                object_type TEXT NOT NULL,
                object_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_receipt_hash72 TEXT NOT NULL,
                PRIMARY KEY(object_type, object_id)
            );
            CREATE TABLE IF NOT EXISTS receipts (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                object_id TEXT NOT NULL,
                authority_state_hash72 TEXT NOT NULL,
                authority_receipt_hash72 TEXT NOT NULL UNIQUE,
                previous_receipt_hash72 TEXT,
                payload_json TEXT NOT NULL,
                receipt_hash72 TEXT NOT NULL UNIQUE
            );
            """
        )
        self._connection.commit()

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Cursor]:
        cursor = self._connection.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")
            yield cursor
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()

    def _receipt(
        self,
        cursor: sqlite3.Cursor,
        *,
        event: str,
        object_id: str,
        payload: Mapping[str, Any],
        authority_execution: Mapping[str, Any],
    ) -> str:
        state_hash72, authority_receipt_hash72 = _authority_lineage(authority_execution)
        prior_row = cursor.execute(
            "SELECT receipt_hash72 FROM receipts ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        previous = str(prior_row[0]) if prior_row else None
        body = {
            "event": event,
            "object_id": object_id,
            "authority_state_hash72": state_hash72,
            "authority_receipt_hash72": authority_receipt_hash72,
            "previous_receipt_hash72": previous,
            "payload": dict(payload),
        }
        receipt_hash72 = _hash72("HHS-P194-MUTATION-RECEIPT-V1", body)
        try:
            cursor.execute(
                """
                INSERT INTO receipts(
                    event, object_id, authority_state_hash72,
                    authority_receipt_hash72, previous_receipt_hash72,
                    payload_json, receipt_hash72
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    event,
                    object_id,
                    state_hash72,
                    authority_receipt_hash72,
                    previous,
                    _canonical(dict(payload)).decode("utf-8"),
                    receipt_hash72,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise Pass194Error("HHS_P194_VM81_AUTHORITY_RECEIPT_REUSED") from exc
        return receipt_hash72

    def _blob_path(self, blob_sha256: str) -> Path:
        return self.blob_root / blob_sha256[:2] / blob_sha256[2:]

    def _write_blob(self, data: bytes) -> str:
        blob_sha256 = sha256(data).hexdigest()
        target = self._blob_path(blob_sha256)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if sha256(target.read_bytes()).hexdigest() != blob_sha256:
                raise Pass194Error("HHS_P194_BLOB_IDENTITY_COLLISION", blob_sha256)
            return blob_sha256
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(descriptor, data)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        if sha256(target.read_bytes()).hexdigest() != blob_sha256:
            raise Pass194Error("HHS_P194_BLOB_WRITE_VERIFICATION_FAILED", blob_sha256)
        return blob_sha256

    def ensure_workspace(
        self,
        workspace_id: str,
        owner_id: str,
        *,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        workspace_id = _bounded_text(workspace_id, "workspace_id", 256)
        owner_id = _bounded_text(owner_id, "owner_id", 256)
        with self._tx() as cursor:
            existing = cursor.execute(
                "SELECT owner_id, created_receipt_hash72 FROM workspaces WHERE workspace_id=?",
                (workspace_id,),
            ).fetchone()
            if existing:
                if existing["owner_id"] != owner_id:
                    raise Pass194Error("HHS_P194_WORKSPACE_OWNER_MISMATCH")
                return {
                    "workspace_id": workspace_id,
                    "owner_id": owner_id,
                    "created_receipt_hash72": existing["created_receipt_hash72"],
                    "idempotent": True,
                }
            payload = {"workspace_id": workspace_id, "owner_id": owner_id}
            receipt = self._receipt(
                cursor,
                event="WORKSPACE_CREATE",
                object_id=workspace_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            cursor.execute(
                "INSERT INTO workspaces(workspace_id, owner_id, created_receipt_hash72) VALUES(?,?,?)",
                (workspace_id, owner_id, receipt),
            )
        return {**payload, "created_receipt_hash72": receipt, "idempotent": False}

    def ingest_bytes(
        self,
        workspace_id: str,
        owner_id: str,
        logical_path: str,
        data: bytes,
        *,
        modality: str = "BINARY",
        metadata: Mapping[str, Any] | None = None,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise Pass194Error("HHS_P194_BYTES_REQUIRED")
        raw = bytes(data)
        workspace_id = _bounded_text(workspace_id, "workspace_id", 256)
        owner_id = _bounded_text(owner_id, "owner_id", 256)
        logical_path = _bounded_text(logical_path, "logical_path", 4096)
        modality = _bounded_text(modality.upper(), "modality", 64)
        metadata_dict = dict(metadata or {})
        metadata_bytes = _canonical(metadata_dict)
        if len(metadata_bytes) > MAX_METADATA_JSON_BYTES:
            raise Pass194Error("HHS_P194_METADATA_LIMIT")

        workspace = self._connection.execute(
            "SELECT owner_id FROM workspaces WHERE workspace_id=?", (workspace_id,)
        ).fetchone()
        if workspace is None:
            raise Pass194Error("HHS_P194_WORKSPACE_NOT_FOUND")
        if workspace["owner_id"] != owner_id:
            raise Pass194Error("HHS_P194_WORKSPACE_OWNER_MISMATCH")

        blob_sha256 = self._write_blob(raw)
        source_hash72 = _hash72(
            "HHS-P194-SOURCE-BYTES-V1",
            {"blob_sha256": blob_sha256, "size_bytes": len(raw)},
        )

        with self._tx() as cursor:
            file_row = cursor.execute(
                "SELECT * FROM files WHERE workspace_id=? AND logical_path=?",
                (workspace_id, logical_path),
            ).fetchone()
            if file_row is None:
                file_id = _sha256_id(
                    "HHS-P194-FILE-ID-V1",
                    {"workspace_id": workspace_id, "logical_path": logical_path},
                )
                version_index = 1
                created_file = True
            else:
                file_id = str(file_row["file_id"])
                if int(file_row["tombstoned"]):
                    raise Pass194Error("HHS_P194_FILE_TOMBSTONED", file_id)
                active = cursor.execute(
                    "SELECT * FROM file_versions WHERE file_version_id=?",
                    (file_row["active_version_id"],),
                ).fetchone()
                if (
                    active
                    and active["blob_sha256"] == blob_sha256
                    and active["metadata_json"] == metadata_bytes.decode("utf-8")
                    and active["modality"] == modality
                ):
                    return {
                        "file_id": file_id,
                        "file_version_id": active["file_version_id"],
                        "version_index": int(active["version_index"]),
                        "blob_sha256": blob_sha256,
                        "source_hash72": active["source_hash72"],
                        "idempotent": True,
                        "training_allowed": False,
                    }
                version_index = int(
                    cursor.execute(
                        "SELECT COALESCE(MAX(version_index),0) FROM file_versions WHERE file_id=?",
                        (file_id,),
                    ).fetchone()[0]
                ) + 1
                created_file = False

            file_version_id = _sha256_id(
                "HHS-P194-FILE-VERSION-ID-V1",
                {
                    "file_id": file_id,
                    "version_index": version_index,
                    "blob_sha256": blob_sha256,
                    "source_hash72": source_hash72,
                    "modality": modality,
                    "metadata": metadata_dict,
                },
            )
            payload = {
                "workspace_id": workspace_id,
                "file_id": file_id,
                "file_version_id": file_version_id,
                "logical_path": logical_path,
                "version_index": version_index,
                "blob_sha256": blob_sha256,
                "source_hash72": source_hash72,
                "modality": modality,
                "size_bytes": len(raw),
                "metadata": metadata_dict,
                "default_training_allowed": False,
                "default_sharing_allowed": False,
                "default_public_allowed": False,
            }
            receipt = self._receipt(
                cursor,
                event="FILE_VERSION_INGEST",
                object_id=file_version_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            if created_file:
                cursor.execute(
                    """
                    INSERT INTO files(
                        file_id, workspace_id, logical_path, active_version_id,
                        tombstoned, created_receipt_hash72
                    ) VALUES(?,?,?,?,0,?)
                    """,
                    (file_id, workspace_id, logical_path, file_version_id, receipt),
                )
            cursor.execute(
                """
                INSERT INTO file_versions(
                    file_version_id, file_id, version_index, blob_sha256,
                    source_hash72, modality, size_bytes, metadata_json,
                    created_receipt_hash72, revoked
                ) VALUES(?,?,?,?,?,?,?,?,?,0)
                """,
                (
                    file_version_id,
                    file_id,
                    version_index,
                    blob_sha256,
                    source_hash72,
                    modality,
                    len(raw),
                    metadata_bytes.decode("utf-8"),
                    receipt,
                ),
            )
            cursor.execute(
                "UPDATE files SET active_version_id=? WHERE file_id=?",
                (file_version_id, file_id),
            )
            consent_id = _sha256_id(
                "HHS-P194-CONSENT-ID-V1",
                {"file_version_id": file_version_id, "ordinal": 0},
            )
            cursor.execute(
                """
                INSERT INTO consent_records(
                    consent_id, file_version_id, training_allowed,
                    sharing_allowed, public_allowed, license_id,
                    active, created_receipt_hash72
                ) VALUES(?,?,0,0,0,NULL,1,?)
                """,
                (consent_id, file_version_id, receipt),
            )
        return {
            "file_id": file_id,
            "file_version_id": file_version_id,
            "version_index": version_index,
            "blob_sha256": blob_sha256,
            "source_hash72": source_hash72,
            "receipt_hash72": receipt,
            "idempotent": False,
            "training_allowed": False,
        }

    def set_consent(
        self,
        file_version_id: str,
        *,
        training_allowed: bool,
        sharing_allowed: bool = False,
        public_allowed: bool = False,
        license_id: str | None = None,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        if public_allowed and not sharing_allowed:
            raise Pass194Error("HHS_P194_PUBLIC_REQUIRES_SHARING")
        if training_allowed and not license_id:
            raise Pass194Error("HHS_P194_TRAINING_LICENSE_REQUIRED")
        if license_id is not None:
            license_id = _bounded_text(license_id, "license_id", 512)
        with self._tx() as cursor:
            row = cursor.execute(
                "SELECT revoked FROM file_versions WHERE file_version_id=?",
                (file_version_id,),
            ).fetchone()
            if row is None:
                raise Pass194Error("HHS_P194_FILE_VERSION_NOT_FOUND")
            if int(row["revoked"]):
                raise Pass194Error("HHS_P194_FILE_VERSION_REVOKED")
            prior_count = int(
                cursor.execute(
                    "SELECT COUNT(*) FROM consent_records WHERE file_version_id=?",
                    (file_version_id,),
                ).fetchone()[0]
            )
            consent_id = _sha256_id(
                "HHS-P194-CONSENT-ID-V1",
                {"file_version_id": file_version_id, "ordinal": prior_count},
            )
            payload = {
                "file_version_id": file_version_id,
                "training_allowed": bool(training_allowed),
                "sharing_allowed": bool(sharing_allowed),
                "public_allowed": bool(public_allowed),
                "license_id": license_id,
            }
            receipt = self._receipt(
                cursor,
                event="CONSENT_SET",
                object_id=consent_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            cursor.execute(
                "UPDATE consent_records SET active=0 WHERE file_version_id=?",
                (file_version_id,),
            )
            cursor.execute(
                """
                INSERT INTO consent_records(
                    consent_id, file_version_id, training_allowed,
                    sharing_allowed, public_allowed, license_id,
                    active, created_receipt_hash72
                ) VALUES(?,?,?,?,?,?,1,?)
                """,
                (
                    consent_id,
                    file_version_id,
                    int(training_allowed),
                    int(sharing_allowed),
                    int(public_allowed),
                    license_id,
                    receipt,
                ),
            )
        return {**payload, "consent_id": consent_id, "receipt_hash72": receipt}

    def link_objects(
        self,
        workspace_id: str,
        from_object_id: str,
        relation: str,
        to_object_id: str,
        *,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        relation = _bounded_text(relation, "relation", MAX_RELATION_TEXT_BYTES)
        payload = {
            "workspace_id": workspace_id,
            "from_object_id": _bounded_text(from_object_id, "from_object_id", 512),
            "relation": relation,
            "to_object_id": _bounded_text(to_object_id, "to_object_id", 512),
        }
        edge_id = _sha256_id("HHS-P194-RELATIONSHIP-ID-V1", payload)
        with self._tx() as cursor:
            if cursor.execute(
                "SELECT 1 FROM workspaces WHERE workspace_id=?", (workspace_id,)
            ).fetchone() is None:
                raise Pass194Error("HHS_P194_WORKSPACE_NOT_FOUND")
            existing = cursor.execute(
                "SELECT created_receipt_hash72 FROM relationships WHERE edge_id=?",
                (edge_id,),
            ).fetchone()
            if existing:
                return {**payload, "edge_id": edge_id, "idempotent": True}
            receipt = self._receipt(
                cursor,
                event="RELATIONSHIP_LINK",
                object_id=edge_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            cursor.execute(
                """
                INSERT INTO relationships(
                    edge_id, workspace_id, from_object_id, relation,
                    to_object_id, created_receipt_hash72
                ) VALUES(?,?,?,?,?,?)
                """,
                (
                    edge_id,
                    workspace_id,
                    payload["from_object_id"],
                    relation,
                    payload["to_object_id"],
                    receipt,
                ),
            )
        return {**payload, "edge_id": edge_id, "receipt_hash72": receipt, "idempotent": False}

    def store_vector_projection(
        self,
        file_version_id: str,
        projection_frame: bytes,
        *,
        model_id: str,
        logical_step: int,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        if not isinstance(logical_step, int) or isinstance(logical_step, bool) or logical_step < 0:
            raise Pass194Error("HHS_P194_EXACT_LOGICAL_STEP_REQUIRED")
        model_id = _bounded_text(model_id, "model_id", MAX_MODEL_ID_BYTES)
        file_version = self._connection.execute(
            "SELECT source_hash72, revoked FROM file_versions WHERE file_version_id=?",
            (file_version_id,),
        ).fetchone()
        if file_version is None:
            raise Pass194Error("HHS_P194_FILE_VERSION_NOT_FOUND")
        if int(file_version["revoked"]):
            raise Pass194Error("HHS_P194_FILE_VERSION_REVOKED")

        state_hash72, authority_receipt_hash72 = _authority_lineage(authority_execution)
        frame = bytes(projection_frame)
        projection_hash72 = _hash72(
            "HHS-P194-VECTOR-PROJECTION-FRAME-V1",
            {"frame_b64": b64encode(frame).decode("ascii"), "model_id": model_id},
        )
        operation_identity = sha256(
            _canonical(
                {
                    "file_version_id": file_version_id,
                    "model_id": model_id,
                    "logical_step": logical_step,
                    "projection_hash72": projection_hash72,
                }
            )
        ).hexdigest()
        hash216 = Hash216Array.build(
            str(file_version["source_hash72"]),
            projection_hash72,
            authority_receipt_hash72,
            genesis_identity=GENESIS_IDENTITY,
            logical_step=logical_step,
            operation_identity=operation_identity,
            legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
        )
        operation_key = sha256(
            b"HHS-P194-VECTOR-OP-V1\0"
            + bytes.fromhex(operation_identity)
            + bytes.fromhex(hash216.index_root_sha256)
        ).hexdigest()
        vector_object = self.vector_store.admit(
            operation_key=operation_key,
            logical_step=logical_step,
            input_hash72=str(file_version["source_hash72"]),
            output_hash72=projection_hash72,
            operation_identity_sha256=operation_identity,
            hash216=hash216,
            output_snapshot=frame,
            legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
            genesis_identity=GENESIS_IDENTITY,
            direct_cost_units=0,
            changed_bits=0,
            parent_object_id=None,
        )
        projection_id = _sha256_id(
            "HHS-P194-VECTOR-PROJECTION-ID-V1",
            {
                "file_version_id": file_version_id,
                "vector_object_id": vector_object.object_id,
                "model_id": model_id,
            },
        )
        payload = {
            "file_version_id": file_version_id,
            "projection_id": projection_id,
            "vector_object_id": vector_object.object_id,
            "operation_key": operation_key,
            "model_id": model_id,
            "hash216_index_root_sha256": hash216.index_root_sha256,
            "vector_is_source_authority": False,
            "vector_is_consent_authority": False,
            "vector_is_vm81_authority": False,
            "authority_state_hash72": state_hash72,
        }
        with self._tx() as cursor:
            receipt = self._receipt(
                cursor,
                event="VECTOR_PROJECTION_STORE",
                object_id=projection_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            cursor.execute(
                """
                INSERT INTO vector_projections(
                    projection_id, file_version_id, vector_object_id,
                    operation_key, model_id, hash216_index_root_sha256,
                    vector_is_source_authority, vector_is_consent_authority,
                    vector_is_vm81_authority, created_receipt_hash72
                ) VALUES(?,?,?,?,?,?,0,0,0,?)
                """,
                (
                    projection_id,
                    file_version_id,
                    vector_object.object_id,
                    operation_key,
                    model_id,
                    hash216.index_root_sha256,
                    receipt,
                ),
            )
        return {**payload, "receipt_hash72": receipt}

    def _active_consent(self, cursor: sqlite3.Cursor, file_version_id: str) -> sqlite3.Row:
        row = cursor.execute(
            """
            SELECT * FROM consent_records
            WHERE file_version_id=? AND active=1
            ORDER BY rowid DESC LIMIT 1
            """,
            (file_version_id,),
        ).fetchone()
        if row is None:
            raise Pass194Error("HHS_P194_CONSENT_MISSING", file_version_id)
        return row

    def _workspace_manifest(self, cursor: sqlite3.Cursor, workspace_id: str) -> Dict[str, Any]:
        file_rows = cursor.execute(
            """
            SELECT f.file_id, f.logical_path, f.active_version_id, f.tombstoned,
                   fv.file_version_id, fv.version_index, fv.blob_sha256,
                   fv.source_hash72, fv.modality, fv.size_bytes,
                   fv.metadata_json, fv.revoked
            FROM files f
            JOIN file_versions fv ON fv.file_version_id=f.active_version_id
            WHERE f.workspace_id=?
            ORDER BY f.logical_path, f.file_id
            """,
            (workspace_id,),
        ).fetchall()
        files: list[Dict[str, Any]] = []
        for row in file_rows:
            consent = self._active_consent(cursor, str(row["file_version_id"]))
            vectors = cursor.execute(
                """
                SELECT projection_id, vector_object_id, operation_key, model_id,
                       hash216_index_root_sha256
                FROM vector_projections
                WHERE file_version_id=?
                ORDER BY projection_id
                """,
                (row["file_version_id"],),
            ).fetchall()
            files.append(
                {
                    "file_id": row["file_id"],
                    "logical_path": row["logical_path"],
                    "file_version_id": row["file_version_id"],
                    "version_index": int(row["version_index"]),
                    "blob_sha256": row["blob_sha256"],
                    "source_hash72": row["source_hash72"],
                    "modality": row["modality"],
                    "size_bytes": int(row["size_bytes"]),
                    "metadata": json.loads(row["metadata_json"]),
                    "revoked": bool(row["revoked"]),
                    "tombstoned": bool(row["tombstoned"]),
                    "consent": {
                        "consent_id": consent["consent_id"],
                        "training_allowed": bool(consent["training_allowed"]),
                        "sharing_allowed": bool(consent["sharing_allowed"]),
                        "public_allowed": bool(consent["public_allowed"]),
                        "license_id": consent["license_id"],
                    },
                    "vector_projections": [dict(vector) for vector in vectors],
                }
            )
        relationships = [
            dict(row)
            for row in cursor.execute(
                """
                SELECT edge_id, from_object_id, relation, to_object_id
                FROM relationships WHERE workspace_id=? ORDER BY edge_id
                """,
                (workspace_id,),
            ).fetchall()
        ]
        return {
            "schema": "HHS_P194_HYDRATION_SNAPSHOT_MANIFEST_V1",
            "workspace_id": workspace_id,
            "files": files,
            "relationships": relationships,
            "vector_presence_is_source_authority": False,
            "snapshot_is_training_authorization": False,
        }

    def create_snapshot(
        self,
        workspace_id: str,
        *,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        with self._tx() as cursor:
            if cursor.execute(
                "SELECT 1 FROM workspaces WHERE workspace_id=?", (workspace_id,)
            ).fetchone() is None:
                raise Pass194Error("HHS_P194_WORKSPACE_NOT_FOUND")
            manifest = self._workspace_manifest(cursor, workspace_id)
            manifest_hash72 = _hash72("HHS-P194-SNAPSHOT-MANIFEST-V1", manifest)
            snapshot_id = _sha256_id(
                "HHS-P194-SNAPSHOT-ID-V1",
                {"manifest_hash72": manifest_hash72, "manifest": manifest},
            )
            existing = cursor.execute(
                "SELECT manifest_json FROM snapshots WHERE snapshot_id=?",
                (snapshot_id,),
            ).fetchone()
            if existing:
                return {
                    "snapshot_id": snapshot_id,
                    "manifest_hash72": manifest_hash72,
                    "idempotent": True,
                }
            payload = {
                "snapshot_id": snapshot_id,
                "workspace_id": workspace_id,
                "manifest_hash72": manifest_hash72,
                "file_version_ids": [item["file_version_id"] for item in manifest["files"]],
                "snapshot_is_training_authorization": False,
            }
            receipt = self._receipt(
                cursor,
                event="SNAPSHOT_CREATE",
                object_id=snapshot_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            manifest_json = _canonical(manifest).decode("utf-8")
            cursor.execute(
                """
                INSERT INTO snapshots(
                    snapshot_id, workspace_id, manifest_json, manifest_hash72,
                    revoked, created_receipt_hash72
                ) VALUES(?,?,?,?,0,?)
                """,
                (snapshot_id, workspace_id, manifest_json, manifest_hash72, receipt),
            )
        snapshot_path = self.snapshot_root / f"{snapshot_id}.json"
        encoded = _canonical(manifest)
        if snapshot_path.exists():
            if snapshot_path.read_bytes() != encoded:
                raise Pass194Error("HHS_P194_SNAPSHOT_IMMUTABILITY_VIOLATION", snapshot_id)
        else:
            descriptor = os.open(snapshot_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(descriptor, encoded)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return {
            "snapshot_id": snapshot_id,
            "manifest_hash72": manifest_hash72,
            "receipt_hash72": receipt,
            "idempotent": False,
        }

    def _validate_snapshot_training_closure(
        self, cursor: sqlite3.Cursor, snapshot_row: sqlite3.Row
    ) -> tuple[Dict[str, Any], list[str]]:
        if int(snapshot_row["revoked"]):
            raise Pass194Error("HHS_P194_SNAPSHOT_REVOKED")
        manifest = json.loads(snapshot_row["manifest_json"])
        file_version_ids: list[str] = []
        for item in manifest["files"]:
            file_version_id = str(item["file_version_id"])
            file_version_ids.append(file_version_id)
            if item["revoked"] or item["tombstoned"]:
                raise Pass194Error("HHS_P194_SNAPSHOT_CONTAINS_REVOKED_SOURCE", file_version_id)
            snapshot_consent = item["consent"]
            if snapshot_consent.get("training_allowed") is not True:
                raise Pass194Error("HHS_P194_TRAINING_CONSENT_DENIED", file_version_id)
            if not snapshot_consent.get("license_id"):
                raise Pass194Error("HHS_P194_TRAINING_LICENSE_MISSING", file_version_id)
            current = self._active_consent(cursor, file_version_id)
            if (
                not int(current["training_allowed"])
                or not current["license_id"]
                or current["consent_id"] != snapshot_consent["consent_id"]
            ):
                raise Pass194Error("HHS_P194_CONSENT_DRIFT_REQUIRES_NEW_SNAPSHOT", file_version_id)
            version = cursor.execute(
                "SELECT revoked FROM file_versions WHERE file_version_id=?",
                (file_version_id,),
            ).fetchone()
            if version is None or int(version["revoked"]):
                raise Pass194Error("HHS_P194_FILE_VERSION_REVOKED", file_version_id)
        return manifest, file_version_ids

    def release_dataset(
        self,
        snapshot_id: str,
        *,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        with self._tx() as cursor:
            snapshot = cursor.execute(
                "SELECT * FROM snapshots WHERE snapshot_id=?", (snapshot_id,)
            ).fetchone()
            if snapshot is None:
                raise Pass194Error("HHS_P194_SNAPSHOT_NOT_FOUND")
            manifest, file_version_ids = self._validate_snapshot_training_closure(cursor, snapshot)
            dataset_manifest = {
                "schema": "HHS_P194_DATASET_RELEASE_MANIFEST_V1",
                "snapshot_id": snapshot_id,
                "snapshot_manifest_hash72": snapshot["manifest_hash72"],
                "file_version_ids": file_version_ids,
                "consent_ids": [item["consent"]["consent_id"] for item in manifest["files"]],
                "license_ids": [item["consent"]["license_id"] for item in manifest["files"]],
                "source_blob_sha256": [item["blob_sha256"] for item in manifest["files"]],
                "vector_projection_ids": [
                    vector["projection_id"]
                    for item in manifest["files"]
                    for vector in item["vector_projections"]
                ],
                "vector_presence_is_training_authorization": False,
            }
            dataset_hash72 = _hash72("HHS-P194-DATASET-RELEASE-V1", dataset_manifest)
            dataset_id = _sha256_id(
                "HHS-P194-DATASET-ID-V1",
                {"dataset_hash72": dataset_hash72, "manifest": dataset_manifest},
            )
            existing = cursor.execute(
                "SELECT created_receipt_hash72 FROM dataset_releases WHERE dataset_id=?",
                (dataset_id,),
            ).fetchone()
            if existing:
                return {
                    "dataset_id": dataset_id,
                    "dataset_hash72": dataset_hash72,
                    "idempotent": True,
                }
            payload = {
                "dataset_id": dataset_id,
                "snapshot_id": snapshot_id,
                "dataset_hash72": dataset_hash72,
                "file_version_ids": file_version_ids,
                "consent_closed": True,
                "license_closed": True,
            }
            receipt = self._receipt(
                cursor,
                event="DATASET_RELEASE",
                object_id=dataset_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            cursor.execute(
                """
                INSERT INTO dataset_releases(
                    dataset_id, snapshot_id, manifest_json, dataset_hash72,
                    revoked, created_receipt_hash72
                ) VALUES(?,?,?,?,0,?)
                """,
                (
                    dataset_id,
                    snapshot_id,
                    _canonical(dataset_manifest).decode("utf-8"),
                    dataset_hash72,
                    receipt,
                ),
            )
        return {**payload, "receipt_hash72": receipt, "idempotent": False}

    def _validate_dataset_current(self, cursor: sqlite3.Cursor, dataset_id: str) -> sqlite3.Row:
        row = cursor.execute(
            "SELECT * FROM dataset_releases WHERE dataset_id=?", (dataset_id,)
        ).fetchone()
        if row is None:
            raise Pass194Error("HHS_P194_DATASET_NOT_FOUND")
        if int(row["revoked"]):
            raise Pass194Error("HHS_P194_DATASET_REVOKED")
        manifest = json.loads(row["manifest_json"])
        for file_version_id, consent_id in zip(
            manifest["file_version_ids"], manifest["consent_ids"]
        ):
            version = cursor.execute(
                "SELECT revoked FROM file_versions WHERE file_version_id=?",
                (file_version_id,),
            ).fetchone()
            if version is None or int(version["revoked"]):
                raise Pass194Error("HHS_P194_DATASET_SOURCE_REVOKED", file_version_id)
            consent = self._active_consent(cursor, file_version_id)
            if (
                consent["consent_id"] != consent_id
                or not int(consent["training_allowed"])
                or not consent["license_id"]
            ):
                raise Pass194Error("HHS_P194_DATASET_CONSENT_REVOKED", file_version_id)
        return row

    def begin_training_run(
        self,
        dataset_id: str,
        *,
        run_kind: str,
        model_base_id: str,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        run_kind = _bounded_text(run_kind.upper(), "run_kind", 64)
        if run_kind not in ALLOWED_RUN_KINDS:
            raise Pass194Error("HHS_P194_RUN_KIND_INVALID")
        model_base_id = _bounded_text(model_base_id, "model_base_id", MAX_MODEL_ID_BYTES)
        with self._tx() as cursor:
            dataset = self._validate_dataset_current(cursor, dataset_id)
            ordinal = int(
                cursor.execute(
                    "SELECT COUNT(*) FROM training_runs WHERE dataset_id=?",
                    (dataset_id,),
                ).fetchone()[0]
            )
            run_id = _sha256_id(
                "HHS-P194-TRAINING-RUN-ID-V1",
                {
                    "dataset_id": dataset_id,
                    "dataset_hash72": dataset["dataset_hash72"],
                    "run_kind": run_kind,
                    "model_base_id": model_base_id,
                    "ordinal": ordinal,
                },
            )
            payload = {
                "run_id": run_id,
                "dataset_id": dataset_id,
                "run_kind": run_kind,
                "model_base_id": model_base_id,
                "training_provider_is_vm81_authority": False,
            }
            receipt = self._receipt(
                cursor,
                event="TRAINING_RUN_BEGIN",
                object_id=run_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            cursor.execute(
                """
                INSERT INTO training_runs(
                    run_id, dataset_id, run_kind, model_base_id, status,
                    training_provider_is_vm81_authority, created_receipt_hash72
                ) VALUES(?,?,?,?, 'AUTHORIZED_PENDING_EXTERNAL_EXECUTION', 0, ?)
                """,
                (run_id, dataset_id, run_kind, model_base_id, receipt),
            )
        return {**payload, "status": "AUTHORIZED_PENDING_EXTERNAL_EXECUTION", "receipt_hash72": receipt}

    def record_checkpoint(
        self,
        run_id: str,
        *,
        artifact_sha256: str,
        metrics: Mapping[str, Any] | None,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        if (
            not isinstance(artifact_sha256, str)
            or len(artifact_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in artifact_sha256)
        ):
            raise Pass194Error("HHS_P194_CHECKPOINT_SHA256_INVALID")
        metrics_dict = dict(metrics or {})
        metrics_json = _canonical(metrics_dict).decode("utf-8")
        with self._tx() as cursor:
            run = cursor.execute(
                "SELECT dataset_id, status FROM training_runs WHERE run_id=?", (run_id,)
            ).fetchone()
            if run is None:
                raise Pass194Error("HHS_P194_TRAINING_RUN_NOT_FOUND")
            if run["status"] == "REVOKED":
                raise Pass194Error("HHS_P194_TRAINING_RUN_REVOKED")
            self._validate_dataset_current(cursor, str(run["dataset_id"]))
            ordinal = int(
                cursor.execute(
                    "SELECT COUNT(*) FROM checkpoints WHERE run_id=?", (run_id,)
                ).fetchone()[0]
            )
            checkpoint_id = _sha256_id(
                "HHS-P194-CHECKPOINT-ID-V1",
                {
                    "run_id": run_id,
                    "artifact_sha256": artifact_sha256,
                    "metrics": metrics_dict,
                    "ordinal": ordinal,
                },
            )
            payload = {
                "checkpoint_id": checkpoint_id,
                "run_id": run_id,
                "artifact_sha256": artifact_sha256,
                "metrics": metrics_dict,
                "checkpoint_is_vm81_authority": False,
            }
            receipt = self._receipt(
                cursor,
                event="CHECKPOINT_RECORD",
                object_id=checkpoint_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            cursor.execute(
                """
                INSERT INTO checkpoints(
                    checkpoint_id, run_id, artifact_sha256, metrics_json,
                    checkpoint_is_vm81_authority, created_receipt_hash72
                ) VALUES(?,?,?,?,0,?)
                """,
                (checkpoint_id, run_id, artifact_sha256, metrics_json, receipt),
            )
            cursor.execute(
                "UPDATE training_runs SET status='CHECKPOINT_RECORDED' WHERE run_id=?",
                (run_id,),
            )
        return {**payload, "receipt_hash72": receipt}

    def _revoke_datasets_for_versions(
        self, cursor: sqlite3.Cursor, file_version_ids: Sequence[str]
    ) -> list[str]:
        targets = set(file_version_ids)
        revoked: list[str] = []
        for row in cursor.execute(
            "SELECT dataset_id, manifest_json, revoked FROM dataset_releases"
        ).fetchall():
            if int(row["revoked"]):
                continue
            manifest = json.loads(row["manifest_json"])
            if targets.intersection(manifest["file_version_ids"]):
                dataset_id = str(row["dataset_id"])
                cursor.execute(
                    "UPDATE dataset_releases SET revoked=1 WHERE dataset_id=?",
                    (dataset_id,),
                )
                cursor.execute(
                    "UPDATE training_runs SET status='REVOKED' WHERE dataset_id=?",
                    (dataset_id,),
                )
                revoked.append(dataset_id)
        return revoked

    def delete_file(
        self,
        file_id: str,
        *,
        reason: str,
        authority_execution: Mapping[str, Any],
    ) -> Dict[str, Any]:
        reason = _bounded_text(reason, "reason", 1024)
        removed_blobs: list[str] = []
        with self._tx() as cursor:
            file_row = cursor.execute(
                "SELECT tombstoned FROM files WHERE file_id=?", (file_id,)
            ).fetchone()
            if file_row is None:
                raise Pass194Error("HHS_P194_FILE_NOT_FOUND")
            if int(file_row["tombstoned"]):
                return {"file_id": file_id, "tombstoned": True, "idempotent": True}
            versions = cursor.execute(
                "SELECT file_version_id, blob_sha256 FROM file_versions WHERE file_id=?",
                (file_id,),
            ).fetchall()
            version_ids = [str(row["file_version_id"]) for row in versions]
            blob_ids = [str(row["blob_sha256"]) for row in versions]
            revoked_datasets = self._revoke_datasets_for_versions(cursor, version_ids)
            payload = {
                "file_id": file_id,
                "reason": reason,
                "file_version_ids": version_ids,
                "revoked_dataset_ids": revoked_datasets,
            }
            receipt = self._receipt(
                cursor,
                event="FILE_DELETE_TOMBSTONE",
                object_id=file_id,
                payload=payload,
                authority_execution=authority_execution,
            )
            cursor.execute("UPDATE files SET tombstoned=1 WHERE file_id=?", (file_id,))
            cursor.execute("UPDATE file_versions SET revoked=1 WHERE file_id=?", (file_id,))
            cursor.execute(
                """
                INSERT OR REPLACE INTO tombstones(
                    object_type, object_id, reason, created_receipt_hash72
                ) VALUES('FILE',?,?,?)
                """,
                (file_id, reason, receipt),
            )
            for blob_sha256 in blob_ids:
                references = int(
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM file_versions fv
                        JOIN files f ON f.file_id=fv.file_id
                        WHERE fv.blob_sha256=? AND f.tombstoned=0
                        """,
                        (blob_sha256,),
                    ).fetchone()[0]
                )
                if references == 0:
                    removed_blobs.append(blob_sha256)
        for blob_sha256 in removed_blobs:
            path = self._blob_path(blob_sha256)
            if path.exists():
                path.unlink()
        return {
            "file_id": file_id,
            "tombstoned": True,
            "revoked_dataset_ids": revoked_datasets,
            "removed_blob_sha256": removed_blobs,
            "receipt_hash72": receipt,
            "idempotent": False,
        }

    def status(self) -> Dict[str, Any]:
        def count(table: str, where: str = "") -> int:
            return int(self._connection.execute(f"SELECT COUNT(*) FROM {table} {where}").fetchone()[0])

        return {
            "schema": "HHS_P194_STORAGE_TRAINING_STATUS_V1",
            "version": VERSION,
            "contract_authorization_commit": CONTRACT_AUTHORIZATION_COMMIT,
            "database_path": str(self.database_path),
            "journal_mode": self._connection.execute("PRAGMA journal_mode").fetchone()[0],
            "synchronous": int(self._connection.execute("PRAGMA synchronous").fetchone()[0]),
            "workspaces": count("workspaces"),
            "files": count("files"),
            "active_files": count("files", "WHERE tombstoned=0"),
            "file_versions": count("file_versions"),
            "vector_projections": count("vector_projections"),
            "snapshots": count("snapshots"),
            "dataset_releases": count("dataset_releases"),
            "training_runs": count("training_runs"),
            "checkpoints": count("checkpoints"),
            "receipts": count("receipts"),
            "vector_store": self.vector_store.storage_status(),
            "blob_store_is_content_authority": True,
            "sql_context_graph_is_metadata_authority": True,
            "vector_store_is_source_authority": False,
            "vector_store_is_consent_authority": False,
            "snapshot_is_training_authorization": False,
            "training_provider_is_vm81_authority": False,
            "vm81_authority_is_inherited": True,
            "training_default": "DENY",
            "sharing_default": "DENY",
            "public_default": "DENY",
        }

    def replay(self) -> Dict[str, Any]:
        previous: str | None = None
        rows = self._connection.execute("SELECT * FROM receipts ORDER BY sequence").fetchall()
        for expected_sequence, row in enumerate(rows, start=1):
            if int(row["sequence"]) != expected_sequence:
                raise Pass194Error("HHS_P194_RECEIPT_SEQUENCE_DRIFT")
            if row["previous_receipt_hash72"] != previous:
                raise Pass194Error("HHS_P194_RECEIPT_CHAIN_DRIFT")
            payload = json.loads(row["payload_json"])
            body = {
                "event": row["event"],
                "object_id": row["object_id"],
                "authority_state_hash72": row["authority_state_hash72"],
                "authority_receipt_hash72": row["authority_receipt_hash72"],
                "previous_receipt_hash72": previous,
                "payload": payload,
            }
            expected = _hash72("HHS-P194-MUTATION-RECEIPT-V1", body)
            if expected != row["receipt_hash72"]:
                raise Pass194Error("HHS_P194_RECEIPT_REPLAY_MISMATCH")
            previous = str(row["receipt_hash72"])

        for row in self._connection.execute("SELECT * FROM snapshots").fetchall():
            manifest = json.loads(row["manifest_json"])
            expected_hash72 = _hash72("HHS-P194-SNAPSHOT-MANIFEST-V1", manifest)
            if expected_hash72 != row["manifest_hash72"]:
                raise Pass194Error("HHS_P194_SNAPSHOT_HASH72_DRIFT")
            expected_id = _sha256_id(
                "HHS-P194-SNAPSHOT-ID-V1",
                {"manifest_hash72": expected_hash72, "manifest": manifest},
            )
            if expected_id != row["snapshot_id"]:
                raise Pass194Error("HHS_P194_SNAPSHOT_ID_DRIFT")
            path = self.snapshot_root / f"{row['snapshot_id']}.json"
            if not path.exists() or path.read_bytes() != _canonical(manifest):
                raise Pass194Error("HHS_P194_SNAPSHOT_FILE_DRIFT")

        for row in self._connection.execute("SELECT * FROM dataset_releases").fetchall():
            manifest = json.loads(row["manifest_json"])
            expected_hash72 = _hash72("HHS-P194-DATASET-RELEASE-V1", manifest)
            if expected_hash72 != row["dataset_hash72"]:
                raise Pass194Error("HHS_P194_DATASET_HASH72_DRIFT")
            expected_id = _sha256_id(
                "HHS-P194-DATASET-ID-V1",
                {"dataset_hash72": expected_hash72, "manifest": manifest},
            )
            if expected_id != row["dataset_id"]:
                raise Pass194Error("HHS_P194_DATASET_ID_DRIFT")

        return {
            "schema": "HHS_P194_REPLAY_RECEIPT_V1",
            "version": VERSION,
            "records": len(rows),
            "receipt_head_hash72": previous,
            "deterministic_replay": True,
            "snapshot_identity_verified": True,
            "dataset_identity_verified": True,
            "vector_store_root_sha256": self.vector_store.root(),
            "vector_store_is_authority": False,
        }

    def close(self) -> None:
        self.vector_store.close()
        self._connection.close()


__all__ = [
    "VERSION",
    "CONTRACT_ID",
    "CONTRACT_AUTHORIZATION_COMMIT",
    "CONTRACT_BASELINE",
    "FROZEN_I131",
    "GENESIS_IDENTITY",
    "LEGACY_FOUNDATION_ROOT",
    "Pass194Error",
    "Pass194Runtime",
]
