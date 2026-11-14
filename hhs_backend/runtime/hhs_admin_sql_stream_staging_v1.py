"""Private, untrusted, arbitrary-length administrator upload staging.

This is a noncanonical SQL metadata + exact-byte spool adapter. Neither staging
nor a SHA-256 source digest proves VM81/Hash216 admission. No executable input
is interpreted in this module; the approved Lane 5 worker owns continuation.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import os
import sqlite3
import threading
import uuid


class StagingError(RuntimeError):
    pass


class AdminStreamStaging:
    """Single-process serialized staging; deploy with one writer or host locking.

    The SQL committed byte offset is authoritative for interrupted writes.
    A restart truncates any uncommitted spool tail before resuming.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.spool = self.root / "spool"
        self.blobs = self.root / "source-sha256"
        for directory in (self.spool, self.blobs):
            directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.db = sqlite3.connect(self.root / "upload-staging.sqlite3", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS intake (
            upload_id TEXT PRIMARY KEY,
            owner TEXT NOT NULL,
            source_name TEXT NOT NULL,
            state TEXT NOT NULL CHECK(state IN ('UPLOADING','STAGED')),
            received_bytes INTEGER NOT NULL,
            sha256 TEXT,
            UNIQUE(upload_id,owner)
        )""")
        self.db.commit()

    @staticmethod
    def _owner(owner: str) -> str:
        if not isinstance(owner, str) or not owner.strip():
            raise StagingError("HOST_VERIFIED_OWNER_REQUIRED")
        return owner

    @staticmethod
    def _uuid(upload_id: str) -> str:
        try:
            parsed = uuid.UUID(upload_id)
            if str(parsed) != upload_id:
                raise ValueError()
        except (ValueError, AttributeError, TypeError) as exc:
            raise StagingError("INVALID_UPLOAD_ID") from exc
        return upload_id

    def _get(self, upload_id: str, owner: str):
        upload_id = self._uuid(upload_id)
        row = self.db.execute(
            "SELECT * FROM intake WHERE upload_id=? AND owner=?",
            (upload_id, self._owner(owner)),
        ).fetchone()
        if row is None:
            raise StagingError("UPLOAD_NOT_FOUND_OR_UNAUTHORIZED")
        return row

    def create(self, owner: str, source_name: str) -> dict:
        owner = self._owner(owner)
        if not isinstance(source_name, str) or not source_name:
            raise StagingError("SOURCE_NAME_REQUIRED")
        upload_id = str(uuid.uuid4())
        with self._lock:
            path = self.spool / upload_id
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
            try:
                self.db.execute(
                    "INSERT INTO intake VALUES (?,?,?,'UPLOADING',0,NULL)",
                    (upload_id, owner, source_name),
                )
                self.db.commit()
            except Exception:
                path.unlink(missing_ok=True)
                raise
        return self.status(upload_id, owner)

    def status(self, upload_id: str, owner: str) -> dict:
        with self._lock:
            row = self._get(upload_id, owner)
            return {
                "upload_id": row["upload_id"],
                "source_name": row["source_name"],
                "state": row["state"],
                "received_bytes": row["received_bytes"],
                "source_sha256": row["sha256"],
                "canonical_hash216_admitted": False,
            }

    def append(self, upload_id: str, owner: str, offset: int, data: bytes) -> dict:
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise StagingError("INVALID_OFFSET")
        if not isinstance(data, bytes):
            raise StagingError("BYTES_REQUIRED")
        with self._lock:
            row = self._get(upload_id, owner)
            if row["state"] != "UPLOADING":
                raise StagingError("UPLOAD_ALREADY_STAGED")
            expected = row["received_bytes"]
            path = self.spool / upload_id
            if not path.is_file() or path.is_symlink():
                raise StagingError("SPOOL_MISSING_OR_INVALID")
            if offset != expected:
                # An already-committed chunk may be retried after a lost response.
                if offset < expected and offset + len(data) <= expected:
                    with path.open("rb") as stream:
                        stream.seek(offset)
                        if stream.read(len(data)) == data:
                            return self.status(upload_id, owner)
                raise StagingError("OFFSET_CONFLICT")
            with path.open("r+b", buffering=0) as stream:
                stream.truncate(expected)  # discard bytes written before an interrupted DB commit
                stream.seek(expected)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            self.db.execute(
                "UPDATE intake SET received_bytes=? WHERE upload_id=? AND owner=? AND state='UPLOADING'",
                (expected + len(data), upload_id, owner),
            )
            self.db.commit()
            return self.status(upload_id, owner)

    def finalize(self, upload_id: str, owner: str, expected_sha256: str | None = None) -> dict:
        with self._lock:
            row = self._get(upload_id, owner)
            if row["state"] == "STAGED":
                if expected_sha256 is not None and expected_sha256 != row["sha256"]:
                    raise StagingError("SOURCE_DIGEST_MISMATCH")
                return self.status(upload_id, owner)
            path = self.spool / upload_id
            if not path.is_file() or path.is_symlink():
                raise StagingError("SPOOL_MISSING_OR_INVALID")
            if path.stat().st_size != row["received_bytes"]:
                with path.open("r+b") as stream:
                    stream.truncate(row["received_bytes"])
                    os.fsync(stream.fileno())
            digest = sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            hexdigest = digest.hexdigest()
            if expected_sha256 is not None and expected_sha256 != hexdigest:
                raise StagingError("SOURCE_DIGEST_MISMATCH")
            target_dir = self.blobs / hexdigest[:2]
            target_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            target = target_dir / hexdigest[2:]
            if not target.exists():
                # Copy into a unique immutable source object; never execute it.
                tmp = target_dir / (upload_id + ".tmp")
                with path.open("rb") as src, tmp.open("xb") as dst:
                    for chunk in iter(lambda: src.read(1024 * 1024), b""):
                        dst.write(chunk)
                    dst.flush()
                    os.fsync(dst.fileno())
                os.replace(tmp, target)
                target.chmod(0o400)
            self.db.execute(
                "UPDATE intake SET state='STAGED', sha256=? WHERE upload_id=? AND owner=?",
                (hexdigest, upload_id, owner),
            )
            self.db.commit()
            path.unlink(missing_ok=True)
            return self.status(upload_id, owner)

    def read_staged(self, upload_id: str, owner: str):
        """Return a verified source location for a *separate* authorized worker.

        Caller must not treat this path or its hash as canonical VM81 admission.
        """
        with self._lock:
            row = self._get(upload_id, owner)
            if row["state"] != "STAGED":
                raise StagingError("UPLOAD_NOT_STAGED")
            path = self.blobs / row["sha256"][:2] / row["sha256"][2:]
            if not path.is_file() or path.is_symlink():
                raise StagingError("STAGED_SOURCE_MISSING")
            return path

    def close(self):
        self.db.close()
