"""Encrypted durable Hash216 microcode store for terminal Pass 175.

The store is append-only, uses SQLite WAL + FULL synchronous durability, binds
each encrypted record to its predecessor store root, and validates all 216
positional indexes on retrieval and audit.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Any, Mapping

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .runtime import Hash216Identity, Pass175Error, ZERO_SHA256


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _sha(value: str, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass175Error("HHS_P175_SECURE_STORE_SHA256", label)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise Pass175Error("HHS_P175_SECURE_STORE_SHA256", label) from exc
    return value


@dataclass(frozen=True)
class SecureInstructionMetadata:
    sequence: int
    key_sha256: str
    exact_bytes_sha256: str
    predecessor_store_root_sha256: str
    store_root_sha256: str
    hash216_combined: str
    hash216_logical_identity_sha256: str
    hash216_index_root_sha256: str
    aad_sha256: str
    ciphertext_sha256: str
    key_version: int
    durable: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EncryptedHash216Store:
    SCHEMA_VERSION = 1

    def __init__(
        self,
        path: str | Path = ":memory:",
        *,
        key_path: str | Path | None = None,
        key: bytes | None = None,
        key_version: int = 1,
    ) -> None:
        self.path = str(path)
        self.key_version = int(key_version)
        if self.key_version < 1:
            raise Pass175Error("HHS_P175_SECURE_STORE_KEY_VERSION")
        self._lock = RLock()
        self._key_path = Path(key_path).resolve() if key_path is not None else None
        self._key = self._resolve_key(key)
        self._aead = AESGCM(self._key)
        if self.path != ":memory:":
            Path(self.path).resolve().parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._initialize()

    def _resolve_key(self, supplied: bytes | None) -> bytes:
        if supplied is not None:
            candidate = bytes(supplied)
        elif self._key_path and self._key_path.exists():
            candidate = self._key_path.read_bytes()
        else:
            candidate = AESGCM.generate_key(bit_length=256)
            if self._key_path:
                self._key_path.parent.mkdir(parents=True, exist_ok=True)
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                try:
                    descriptor = os.open(self._key_path, flags, 0o600)
                except FileExistsError:
                    candidate = self._key_path.read_bytes()
                else:
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(candidate)
                        handle.flush()
                        os.fsync(handle.fileno())
        if len(candidate) not in (16, 24, 32):
            raise Pass175Error("HHS_P175_SECURE_STORE_KEY_LENGTH")
        return candidate

    def _initialize(self) -> None:
        with self._db:
            self._db.execute("PRAGMA journal_mode=WAL")
            self._db.execute("PRAGMA synchronous=FULL")
            self._db.execute("PRAGMA foreign_keys=ON")
            self._db.execute("PRAGMA temp_store=MEMORY")
            self._db.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    sequence INTEGER PRIMARY KEY,
                    key_sha256 TEXT NOT NULL UNIQUE,
                    exact_bytes_sha256 TEXT NOT NULL,
                    predecessor_store_root_sha256 TEXT NOT NULL,
                    store_root_sha256 TEXT NOT NULL,
                    hash216_combined TEXT NOT NULL,
                    hash216_logical_identity_sha256 TEXT NOT NULL,
                    hash216_index_root_sha256 TEXT NOT NULL,
                    nonce BLOB NOT NULL,
                    ciphertext BLOB NOT NULL,
                    aad_sha256 TEXT NOT NULL,
                    ciphertext_sha256 TEXT NOT NULL,
                    key_version INTEGER NOT NULL,
                    durable INTEGER NOT NULL CHECK (durable IN (0,1))
                )
                """
            )
            self._db.execute(
                """
                CREATE TABLE IF NOT EXISTS positional_indexes (
                    key_sha256 TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    index_sha256 TEXT NOT NULL,
                    PRIMARY KEY (key_sha256, position),
                    FOREIGN KEY (key_sha256) REFERENCES records(key_sha256)
                )
                """
            )
            self._db.execute(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    name TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            self._db.execute(
                "INSERT OR IGNORE INTO metadata(name,value) VALUES('schema','HHS_PASS_175_ENCRYPTED_HASH216_STORE_V1')"
            )
            self._db.execute(
                "INSERT OR IGNORE INTO metadata(name,value) VALUES('store_root_sha256',?)",
                (ZERO_SHA256,),
            )
            self._db.execute(
                "INSERT OR IGNORE INTO metadata(name,value) VALUES('sealed','0')"
            )

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "EncryptedHash216Store":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    @property
    def root_sha256(self) -> str:
        row = self._db.execute(
            "SELECT value FROM metadata WHERE name='store_root_sha256'"
        ).fetchone()
        return str(row["value"]) if row else ZERO_SHA256

    @property
    def sealed(self) -> bool:
        row = self._db.execute("SELECT value FROM metadata WHERE name='sealed'").fetchone()
        return bool(row and row["value"] == "1")

    def _aad(
        self,
        *,
        sequence: int,
        key_sha256: str,
        exact_bytes_sha256: str,
        predecessor_store_root_sha256: str,
        hash216: Hash216Identity,
    ) -> bytes:
        return _canonical({
            "schema": "HHS_PASS_175_ENCRYPTED_HASH216_AAD_V1",
            "sequence": sequence,
            "key_sha256": key_sha256,
            "exact_bytes_sha256": exact_bytes_sha256,
            "predecessor_store_root_sha256": predecessor_store_root_sha256,
            "hash216_logical_identity_sha256": hash216.logical_identity_sha256,
            "hash216_index_root_sha256": hash216.index_root_sha256,
            "key_version": self.key_version,
        })

    @staticmethod
    def _next_root(
        predecessor: str,
        key_sha256: str,
        logical_identity: str,
        index_root: str,
        ciphertext_sha256: str,
    ) -> str:
        # The canonical store root binds immutable instruction identity and
        # positional proof geometry, not randomized AEAD nonce/ciphertext bytes.
        # Ciphertext integrity remains independently authenticated by AES-GCM and
        # ciphertext_sha256. Excluding randomized encryption material makes cold
        # hydration, warm restart, backup, and independent replicas converge on
        # the same canonical microcode-store root.
        _sha(ciphertext_sha256, "ciphertext_sha256")
        return sha256(
            b"HHS-P175-SECURE-STORE-CHAIN-V2\0"
            + bytes.fromhex(predecessor)
            + bytes.fromhex(key_sha256)
            + bytes.fromhex(logical_identity)
            + bytes.fromhex(index_root)
        ).hexdigest()

    def admit(
        self,
        record: Mapping[str, Any],
        *,
        exact_bytes: bytes,
        expected_predecessor_root_sha256: str | None = None,
    ) -> SecureInstructionMetadata:
        exact = bytes(exact_bytes)
        if not exact:
            raise Pass175Error("HHS_P175_SECURE_STORE_EMPTY_ENCODING")
        exact_hash = sha256(exact).hexdigest()
        body = {
            "schema": "HHS_PASS_175_SECURE_INSTRUCTION_RECORD_V1",
            "record": dict(record),
            "exact_bytes_b64": b64encode(exact).decode("ascii"),
            "exact_bytes_sha256": exact_hash,
        }
        record_bytes = _canonical(body)
        key_sha256 = sha256(b"HHS-P175-SECURE-INSTRUCTION-KEY\0" + record_bytes).hexdigest()
        envelope = {
            "schema": "HHS_PASS_175_SECURE_HASH216_ENVELOPE_V1",
            "key_sha256": key_sha256,
            "exact_bytes_sha256": exact_hash,
            "record_identity_sha256": sha256(_canonical(record)).hexdigest(),
        }
        hash216 = Hash216Identity.build(envelope, exact)
        hash216.verify()

        with self._lock:
            existing = self._db.execute(
                "SELECT * FROM records WHERE key_sha256=?", (key_sha256,)
            ).fetchone()
            if existing is not None:
                metadata, existing_record, existing_exact = self.retrieve(key_sha256)
                if existing_exact != exact or existing_record != dict(record):
                    raise Pass175Error("HHS_P175_SECURE_STORE_KEY_COLLISION")
                return metadata

            predecessor = self.root_sha256
            if expected_predecessor_root_sha256 is not None:
                expected = _sha(expected_predecessor_root_sha256, "expected_predecessor_root_sha256")
                if expected != predecessor:
                    raise Pass175Error("HHS_P175_SECURE_STORE_STALE_ROOT")
            sequence_row = self._db.execute(
                "SELECT COALESCE(MAX(sequence), -1) + 1 AS next_sequence FROM records"
            ).fetchone()
            sequence = int(sequence_row["next_sequence"])
            aad = self._aad(
                sequence=sequence,
                key_sha256=key_sha256,
                exact_bytes_sha256=exact_hash,
                predecessor_store_root_sha256=predecessor,
                hash216=hash216,
            )
            nonce = os.urandom(12)
            ciphertext = self._aead.encrypt(nonce, record_bytes, aad)
            ciphertext_hash = sha256(ciphertext).hexdigest()
            next_root = self._next_root(
                predecessor,
                key_sha256,
                hash216.logical_identity_sha256,
                hash216.index_root_sha256,
                ciphertext_hash,
            )
            aad_hash = sha256(aad).hexdigest()

            self._db.execute("BEGIN IMMEDIATE")
            try:
                current = self._db.execute(
                    "SELECT value FROM metadata WHERE name='store_root_sha256'"
                ).fetchone()
                if current is None or str(current["value"]) != predecessor:
                    raise Pass175Error("HHS_P175_SECURE_STORE_STALE_ROOT")
                self._db.execute(
                    """
                    INSERT INTO records(
                        sequence,key_sha256,exact_bytes_sha256,
                        predecessor_store_root_sha256,store_root_sha256,
                        hash216_combined,hash216_logical_identity_sha256,
                        hash216_index_root_sha256,nonce,ciphertext,aad_sha256,
                        ciphertext_sha256,key_version,durable
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,1)
                    """,
                    (
                        sequence,
                        key_sha256,
                        exact_hash,
                        predecessor,
                        next_root,
                        hash216.combined,
                        hash216.logical_identity_sha256,
                        hash216.index_root_sha256,
                        nonce,
                        ciphertext,
                        aad_hash,
                        ciphertext_hash,
                        self.key_version,
                    ),
                )
                self._db.executemany(
                    "INSERT INTO positional_indexes(key_sha256,position,index_sha256) VALUES(?,?,?)",
                    [
                        (key_sha256, position, index_sha)
                        for position, index_sha in enumerate(hash216.character_indexes_sha256)
                    ],
                )
                self._db.execute(
                    "UPDATE metadata SET value=? WHERE name='store_root_sha256'",
                    (next_root,),
                )
                self._db.execute("COMMIT")
            except Exception:
                self._db.execute("ROLLBACK")
                raise

        return SecureInstructionMetadata(
            sequence=sequence,
            key_sha256=key_sha256,
            exact_bytes_sha256=exact_hash,
            predecessor_store_root_sha256=predecessor,
            store_root_sha256=next_root,
            hash216_combined=hash216.combined,
            hash216_logical_identity_sha256=hash216.logical_identity_sha256,
            hash216_index_root_sha256=hash216.index_root_sha256,
            aad_sha256=aad_hash,
            ciphertext_sha256=ciphertext_hash,
            key_version=self.key_version,
            durable=True,
        )

    def _metadata(self, row: sqlite3.Row) -> SecureInstructionMetadata:
        return SecureInstructionMetadata(
            sequence=int(row["sequence"]),
            key_sha256=str(row["key_sha256"]),
            exact_bytes_sha256=str(row["exact_bytes_sha256"]),
            predecessor_store_root_sha256=str(row["predecessor_store_root_sha256"]),
            store_root_sha256=str(row["store_root_sha256"]),
            hash216_combined=str(row["hash216_combined"]),
            hash216_logical_identity_sha256=str(row["hash216_logical_identity_sha256"]),
            hash216_index_root_sha256=str(row["hash216_index_root_sha256"]),
            aad_sha256=str(row["aad_sha256"]),
            ciphertext_sha256=str(row["ciphertext_sha256"]),
            key_version=int(row["key_version"]),
            durable=bool(row["durable"]),
        )

    def retrieve(self, key_sha256: str) -> tuple[SecureInstructionMetadata, dict[str, Any], bytes]:
        key = _sha(key_sha256, "key_sha256")
        row = self._db.execute("SELECT * FROM records WHERE key_sha256=?", (key,)).fetchone()
        if row is None:
            raise Pass175Error("HHS_P175_SECURE_STORE_MISS")
        metadata = self._metadata(row)
        indexes_rows = self._db.execute(
            "SELECT position,index_sha256 FROM positional_indexes WHERE key_sha256=? ORDER BY position",
            (key,),
        ).fetchall()
        indexes = tuple(str(value["index_sha256"]) for value in indexes_rows)
        if len(indexes) != 216 or [int(value["position"]) for value in indexes_rows] != list(range(216)):
            raise Pass175Error("HHS_P175_SECURE_STORE_POSITIONAL_INDEX_COUNT")
        combined = metadata.hash216_combined
        if len(combined) != 216:
            raise Pass175Error("HHS_P175_SECURE_STORE_HASH216_LENGTH")
        root = sha256(
            b"P175-H216-R\0" + b"".join(bytes.fromhex(value) for value in indexes)
        ).hexdigest()
        if root != metadata.hash216_index_root_sha256:
            raise Pass175Error("HHS_P175_SECURE_STORE_POSITIONAL_INDEX_ROOT")

        hash216 = Hash216Identity(
            predecessor=combined[:72],
            current=combined[72:144],
            successor=combined[144:216],
            combined=combined,
            character_indexes_sha256=indexes,
            index_root_sha256=metadata.hash216_index_root_sha256,
            logical_identity_sha256=metadata.hash216_logical_identity_sha256,
        )
        hash216.verify()
        aad = self._aad(
            sequence=metadata.sequence,
            key_sha256=metadata.key_sha256,
            exact_bytes_sha256=metadata.exact_bytes_sha256,
            predecessor_store_root_sha256=metadata.predecessor_store_root_sha256,
            hash216=hash216,
        )
        if sha256(aad).hexdigest() != metadata.aad_sha256:
            raise Pass175Error("HHS_P175_SECURE_STORE_AAD")
        ciphertext = bytes(row["ciphertext"])
        if sha256(ciphertext).hexdigest() != metadata.ciphertext_sha256:
            raise Pass175Error("HHS_P175_SECURE_STORE_CIPHERTEXT_HASH")
        try:
            plaintext = self._aead.decrypt(bytes(row["nonce"]), ciphertext, aad)
        except Exception as exc:
            raise Pass175Error("HHS_P175_SECURE_STORE_AUTHENTICATION") from exc
        payload = json.loads(plaintext)
        exact = b64decode(payload["exact_bytes_b64"], validate=True)
        if sha256(exact).hexdigest() != metadata.exact_bytes_sha256:
            raise Pass175Error("HHS_P175_SECURE_STORE_EXACT_BYTES")
        record = payload["record"]
        expected_key = sha256(b"HHS-P175-SECURE-INSTRUCTION-KEY\0" + _canonical(payload)).hexdigest()
        if expected_key != metadata.key_sha256:
            raise Pass175Error("HHS_P175_SECURE_STORE_KEY_IDENTITY")
        return metadata, dict(record), exact

    def keys(self) -> tuple[str, ...]:
        rows = self._db.execute("SELECT key_sha256 FROM records ORDER BY sequence").fetchall()
        return tuple(str(row["key_sha256"]) for row in rows)

    def seal(self, *, authority_receipt_sha256: str) -> dict[str, Any]:
        receipt = _sha(authority_receipt_sha256, "authority_receipt_sha256")
        with self._lock, self._db:
            self._db.execute(
                "INSERT OR REPLACE INTO metadata(name,value) VALUES('seal_authority_receipt_sha256',?)",
                (receipt,),
            )
            self._db.execute("UPDATE metadata SET value='1' WHERE name='sealed'")
        self.checkpoint()
        return {
            "classification": "HHS_PASS_175_SECURE_STORE_SEALED",
            "store_root_sha256": self.root_sha256,
            "authority_receipt_sha256": receipt,
            "record_count": len(self.keys()),
            "sealed": True,
        }

    def checkpoint(self) -> dict[str, Any]:
        row = self._db.execute("PRAGMA wal_checkpoint(FULL)").fetchone()
        return {
            "schema": "HHS_PASS_175_SECURE_STORE_CHECKPOINT_V1",
            "checkpoint": tuple(row) if row is not None else (),
            "store_root_sha256": self.root_sha256,
            "record_count": len(self.keys()),
        }

    def backup(self, destination: str | Path) -> dict[str, Any]:
        if self.path == ":memory:":
            raise Pass175Error("HHS_P175_SECURE_STORE_BACKUP_IN_MEMORY")
        target = Path(destination).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(target) as backup_db:
            self._db.backup(backup_db)
        data = target.read_bytes()
        return {
            "schema": "HHS_PASS_175_SECURE_STORE_BACKUP_V1",
            "path": str(target),
            "bytes": len(data),
            "sha256": sha256(data).hexdigest(),
            "store_root_sha256": self.root_sha256,
        }

    def verify(self) -> dict[str, Any]:
        root = ZERO_SHA256
        records = 0
        indexes = 0
        prior_sequence = -1
        for key in self.keys():
            metadata, _record, _exact = self.retrieve(key)
            if metadata.sequence != prior_sequence + 1:
                raise Pass175Error("HHS_P175_SECURE_STORE_SEQUENCE")
            if metadata.predecessor_store_root_sha256 != root:
                raise Pass175Error("HHS_P175_SECURE_STORE_CHAIN_PREDECESSOR")
            expected = self._next_root(
                root,
                metadata.key_sha256,
                metadata.hash216_logical_identity_sha256,
                metadata.hash216_index_root_sha256,
                metadata.ciphertext_sha256,
            )
            if expected != metadata.store_root_sha256:
                raise Pass175Error("HHS_P175_SECURE_STORE_CHAIN_ROOT")
            root = expected
            prior_sequence = metadata.sequence
            records += 1
            indexes += 216
        if root != self.root_sha256:
            raise Pass175Error("HHS_P175_SECURE_STORE_ROOT_MISMATCH")
        return {
            "schema": "HHS_PASS_175_SECURE_STORE_VERIFICATION_V1",
            "classification": "HHS_PASS_175_SECURE_STORE_VERIFIED",
            "record_count": records,
            "positional_index_count": indexes,
            "store_root_sha256": root,
            "sealed": self.sealed,
            "wal": self.path != ":memory:",
            "synchronous": "FULL",
            "encryption": "AES_GCM",
            "key_version": self.key_version,
            "durable": self.path != ":memory:",
        }

    def status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_175_SECURE_STORE_STATUS_V1",
            "path": self.path,
            "record_count": len(self.keys()),
            "positional_index_count": len(self.keys()) * 216,
            "store_root_sha256": self.root_sha256,
            "sealed": self.sealed,
            "journal_mode": self._db.execute("PRAGMA journal_mode").fetchone()[0],
            "synchronous": self._db.execute("PRAGMA synchronous").fetchone()[0],
            "encryption": "AES_GCM",
            "key_version": self.key_version,
            "plaintext_exposed": False,
        }


__all__ = [
    "EncryptedHash216Store",
    "SecureInstructionMetadata",
]
