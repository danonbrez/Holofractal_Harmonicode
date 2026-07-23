from __future__ import annotations
import time
from pathlib import Path
from typing import Any
from .common import append_jsonl, atomic_write, canonical_json, sha256_json


class ReceiptWriter:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._chain_tip = "0" * 64
        self._sequence = 0

    def _envelope(self, schema: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._sequence += 1
        body = {
            "schema": schema,
            "sequence": self._sequence,
            "timestamp_ns": time.time_ns(),
            "previous_projection_digest": self._chain_tip,
            "payload": payload,
            "authority_classification": "PREDICTIVE_EVIDENCE_NOT_TRANSITION_AUTHORITY",
        }
        digest = sha256_json(body)
        body["projection_digest"] = digest
        self._chain_tip = digest
        return body

    def write_json(self, filename: str, schema: str, payload: dict[str, Any], *, authoritative: bool = False) -> dict[str, Any]:
        if authoritative:
            obj = {"schema": schema, "payload": payload, "authority_classification": "VM81_AUTHORIZED_TRANSITION_EVIDENCE"}
        else:
            obj = self._envelope(schema, payload)
        atomic_write(self.root / filename, canonical_json(obj) + "\n")
        return obj

    def append(self, filename: str, schema: str, payload: dict[str, Any]) -> dict[str, Any]:
        obj = self._envelope(schema, payload)
        append_jsonl(self.root / filename, obj)
        return obj

    @property
    def chain_tip(self) -> str:
        return self._chain_tip
