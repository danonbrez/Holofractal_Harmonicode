"""Durable append-only storage and interruption recovery for Pass 165.

The durable layer stores only complete ingestion records emitted by the governed
MultimodalLearningService.  It never grants an adapter, tokenizer, or learning
worker commit authority.  Recovery replays each checksummed source record through
the same VM81 admission path and compares the original receipt identity.
"""
from __future__ import annotations

from base64 import b64decode
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

from hhs_runtime.pass163.vmrc import VMRCRuntime
from .ingestion import (
    IngestionError,
    IngestionResult,
    MultimodalLearningService,
    canonical_bytes,
)

JOURNAL_SCHEMA = "HHS_PASS_165_DURABLE_JOURNAL_RECORD_V1"
HEAD_SCHEMA = "HHS_PASS_165_DURABLE_FRONTIER_V1"


class SimulatedInterruption(RuntimeError):
    """Test-only process interruption raised at an explicit durable boundary."""


class DurableMultimodalLearningService(MultimodalLearningService):
    """Pass 165 service with an append-only journal and atomic durable frontier."""

    def __init__(
        self,
        storage_dir: str | os.PathLike[str],
        vm81: VMRCRuntime | None = None,
        *,
        recover: bool = True,
        fault_after: str | None = None,
    ) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.journal_path = self.storage_dir / "ingestion.journal.jsonl"
        self.head_path = self.storage_dir / "frontier.json"
        self.head_temp_path = self.storage_dir / "frontier.json.tmp"
        self.quarantine_path = self.storage_dir / "quarantine.log"
        self._recovering = False
        self._fault_after = fault_after
        super().__init__(vm81=vm81)
        if recover:
            self.recover_durable_state()

    def status(self) -> dict[str, Any]:
        value = super().status()
        value.update(
            {
                "durable": True,
                "storage_dir": str(self.storage_dir),
                "durable_records": len(self._history),
                "journal_exists": self.journal_path.exists(),
                "frontier_exists": self.head_path.exists(),
            }
        )
        return value

    def _interrupt(self, stage: str) -> None:
        if self._fault_after == stage:
            self._fault_after = None
            raise SimulatedInterruption(stage)

    @staticmethod
    def _envelope(record: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema": JOURNAL_SCHEMA,
            "record": record,
            "record_sha256": sha256(canonical_bytes(record)).hexdigest(),
        }

    def _journal_bytes(self) -> bytes:
        return self.journal_path.read_bytes() if self.journal_path.exists() else b""

    def _frontier(self, *, journal_bytes: bytes | None = None) -> dict[str, Any]:
        raw = self._journal_bytes() if journal_bytes is None else journal_bytes
        return {
            "schema": HEAD_SCHEMA,
            "record_count": len(self._history),
            "journal_sha256": sha256(raw).hexdigest(),
            "weight_root": self.weight_root,
            "vm81_state_hash72": self._vm81.state_hash72,
            "last_receipt_hash72": self._history[-1]["receipt_hash72"] if self._history else None,
        }

    def _write_frontier_atomic(self) -> None:
        payload = canonical_bytes(self._frontier()) + b"\n"
        with self.head_temp_path.open("wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        self._interrupt("after_head_temp_fsync")
        os.replace(self.head_temp_path, self.head_path)
        directory_fd = os.open(self.storage_dir, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        self._interrupt("after_head_replace")

    def _persist_latest_record(self) -> None:
        record = dict(self._history[-1])
        line = canonical_bytes(self._envelope(record)) + b"\n"
        self._interrupt("before_journal_append")
        with self.journal_path.open("ab") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        self._interrupt("after_journal_fsync")
        self._write_frontier_atomic()

    def commit_learning_epoch(self, result: IngestionResult) -> dict[str, Any]:
        existed = result.source.source_hash in self._results
        receipt = super().commit_learning_epoch(result)
        if not existed and not self._recovering:
            self._persist_latest_record()
        return receipt

    def _quarantine(self, classification: str, payload: bytes) -> None:
        entry = {
            "classification": classification,
            "payload_sha256": sha256(payload).hexdigest(),
            "byte_length": len(payload),
        }
        with self.quarantine_path.open("ab") as handle:
            handle.write(canonical_bytes(entry) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())

    def _read_complete_envelopes(self) -> list[dict[str, Any]]:
        raw = self._journal_bytes()
        if not raw:
            return []
        if raw.endswith(b"\n"):
            complete, incomplete = raw, b""
        else:
            boundary = raw.rfind(b"\n")
            complete = raw[: boundary + 1] if boundary >= 0 else b""
            incomplete = raw[boundary + 1 :]
        if incomplete:
            self._quarantine("P165_INCOMPLETE_JOURNAL_TAIL", incomplete)
            with self.journal_path.open("wb") as handle:
                handle.write(complete)
                handle.flush()
                os.fsync(handle.fileno())
        envelopes: list[dict[str, Any]] = []
        for line_number, line in enumerate(complete.splitlines(), start=1):
            try:
                envelope = json.loads(line)
            except json.JSONDecodeError as exc:
                raise IngestionError("P165_DURABLE_JOURNAL_TAMPER", f"json:{line_number}") from exc
            if envelope.get("schema") != JOURNAL_SCHEMA or not isinstance(envelope.get("record"), dict):
                raise IngestionError("P165_DURABLE_JOURNAL_TAMPER", f"schema:{line_number}")
            expected = sha256(canonical_bytes(envelope["record"])).hexdigest()
            if envelope.get("record_sha256") != expected:
                raise IngestionError("P165_DURABLE_JOURNAL_TAMPER", f"digest:{line_number}")
            envelopes.append(envelope)
        return envelopes

    def recover_durable_state(self) -> dict[str, Any]:
        envelopes = self._read_complete_envelopes()
        if self.head_temp_path.exists():
            self._quarantine("P165_STALE_FRONTIER_TEMP", self.head_temp_path.read_bytes())
            self.head_temp_path.unlink()
        self._recovering = True
        try:
            for envelope in envelopes:
                record = envelope["record"]
                try:
                    raw = b64decode(record["source_bytes_b64"], validate=True)
                except Exception as exc:
                    raise IngestionError("P165_DURABLE_JOURNAL_TAMPER", "source_base64") from exc
                result = super().ingest_source(
                    raw,
                    declared_media_type=record.get("declared_media_type"),
                    provenance=record["provenance"],
                    authorization_scope=record["authorization_scope"],
                )
                if result["receipt"]["receipt_hash72"] != record.get("receipt_hash72"):
                    raise IngestionError("P165_DURABLE_REPLAY_MISMATCH")
        finally:
            self._recovering = False
        current = self._frontier()
        if self.head_path.exists():
            try:
                prior = json.loads(self.head_path.read_bytes())
            except json.JSONDecodeError:
                prior = None
            if prior is not None and prior.get("record_count", 0) > current["record_count"]:
                raise IngestionError("P165_DURABLE_FRONTIER_AHEAD_OF_JOURNAL")
            if prior != current:
                self._quarantine("P165_STALE_DURABLE_FRONTIER", self.head_path.read_bytes())
        self._write_frontier_atomic()
        return {
            "classification": "P165_DURABLE_RECOVERY_RECEIPT",
            "records": len(envelopes),
            "weight_root": self.weight_root,
            "vm81_state_hash72": self._vm81.state_hash72,
            "deterministic_recovery": True,
        }
