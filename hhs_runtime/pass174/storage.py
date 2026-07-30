"""Durable encrypted Hash216 vector storage for Pass 174."""
from __future__ import annotations

from dataclasses import asdict
from base64 import b64decode, b64encode
import json
import os
from pathlib import Path
import sqlite3
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .runtime import (
    EncryptedVectorObject,
    EncryptedVectorStore,
    Hash216Array,
    Pass174Error,
)


def _load_or_create_key(key_path: Path) -> bytes:
    configured = os.environ.get("HHS_PASS174_MASTER_KEY_B64")
    if configured:
        try:
            key = b64decode(configured, validate=True)
        except Exception as exc:
            raise Pass174Error("HHS_P174_MASTER_KEY_MALFORMED") from exc
        if len(key) not in (16, 24, 32):
            raise Pass174Error("HHS_P174_INVALID_AEAD_KEY_LENGTH")
        return key
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        try:
            key = b64decode(key_path.read_text(encoding="ascii").strip(), validate=True)
        except Exception as exc:
            raise Pass174Error("HHS_P174_MASTER_KEY_MALFORMED") from exc
        if len(key) not in (16, 24, 32):
            raise Pass174Error("HHS_P174_INVALID_AEAD_KEY_LENGTH")
        return key
    key = AESGCM.generate_key(bit_length=256)
    descriptor = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, b64encode(key) + b"\n")
    finally:
        os.close(descriptor)
    return key


def _serialize(obj: EncryptedVectorObject) -> str:
    return json.dumps(asdict(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _deserialize(raw: str) -> EncryptedVectorObject:
    data = json.loads(raw)
    hash216 = Hash216Array(
        predecessor=data["hash216"]["predecessor"],
        current=data["hash216"]["current"],
        successor=data["hash216"]["successor"],
        combined=data["hash216"]["combined"],
        character_indexes_sha256=tuple(data["hash216"]["character_indexes_sha256"]),
        index_root_sha256=data["hash216"]["index_root_sha256"],
        logical_identity_sha256=data["hash216"]["logical_identity_sha256"],
    )
    return EncryptedVectorObject(
        object_id=data["object_id"],
        operation_key=data["operation_key"],
        logical_step=int(data["logical_step"]),
        input_hash72=data["input_hash72"],
        output_hash72=data["output_hash72"],
        operation_identity_sha256=data["operation_identity_sha256"],
        hash216=hash216,
        nonce_b64=data["nonce_b64"],
        ciphertext_b64=data["ciphertext_b64"],
        associated_data_sha256=data["associated_data_sha256"],
        key_version=int(data["key_version"]),
        direct_cost_units=int(data["direct_cost_units"]),
        changed_bits=int(data["changed_bits"]),
        parent_object_id=data.get("parent_object_id"),
    )


class PersistentEncryptedVectorStore(EncryptedVectorStore):
    """SQLite-backed store retaining encrypted payloads across process restarts."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        key: bytes | None = None,
        key_path: str | Path | None = None,
        key_version: int = 1,
        active_suffix_limit: int = 72,
    ) -> None:
        self.database_path = Path(database_path).resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_key_path = Path(key_path).resolve() if key_path else self.database_path.with_suffix(".key")
        super().__init__(
            key=key or _load_or_create_key(resolved_key_path),
            key_version=key_version,
            active_suffix_limit=active_suffix_limit,
        )
        self.key_path = resolved_key_path
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pass174_vector_objects (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                object_id TEXT NOT NULL UNIQUE,
                operation_key TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                quarantined INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS pass174_vector_operation_key ON pass174_vector_objects(operation_key, sequence)"
        )
        self._connection.commit()
        self._load()

    def _load(self) -> None:
        rows = self._connection.execute(
            "SELECT object_id, operation_key, payload_json, quarantined FROM pass174_vector_objects ORDER BY sequence"
        ).fetchall()
        for object_id, operation_key, payload_json, quarantined in rows:
            obj = _deserialize(payload_json)
            if obj.object_id != object_id or obj.operation_key != operation_key:
                raise Pass174Error("HHS_P174_PERSISTED_VECTOR_IDENTITY_MISMATCH", object_id)
            obj.hash216.verify()
            self._objects[obj.object_id] = obj
            self._operation_index[obj.operation_key] = obj.object_id
            self._order.append(obj.object_id)
            if quarantined:
                self._quarantined.add(obj.object_id)

    def admit(self, **kwargs: Any) -> EncryptedVectorObject:
        obj = super().admit(**kwargs)
        with self._lock:
            self._connection.execute(
                "INSERT OR REPLACE INTO pass174_vector_objects(object_id, operation_key, payload_json, quarantined) VALUES(?,?,?,?)",
                (obj.object_id, obj.operation_key, _serialize(obj), int(obj.object_id in self._quarantined)),
            )
            self._connection.commit()
        return obj

    def quarantine(self, object_id: str) -> None:
        super().quarantine(object_id)
        with self._lock:
            self._connection.execute(
                "UPDATE pass174_vector_objects SET quarantined=1 WHERE object_id=?",
                (object_id,),
            )
            self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def storage_status(self) -> dict[str, Any]:
        count, quarantined = self._connection.execute(
            "SELECT COUNT(*), COALESCE(SUM(quarantined),0) FROM pass174_vector_objects"
        ).fetchone()
        return {
            "schema": "HHS_P174_PERSISTENT_VECTOR_STORE_STATUS_V1",
            "database_path": str(self.database_path),
            "key_path": str(self.key_path),
            "key_version": self.key_version,
            "objects": int(count),
            "quarantined": int(quarantined),
            "journal_mode": self._connection.execute("PRAGMA journal_mode").fetchone()[0],
            "logical_root_sha256": self.root(),
            "plaintext_persisted": False,
            "authenticated_encryption": "AES_GCM",
        }
