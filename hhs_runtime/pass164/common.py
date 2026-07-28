from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.pass150.genome import Hash216Genome

P = 72
THREADS = 64
VM81 = 81
BRIDGE = 5184
VM_PAIRS = 6561
PHASE_PAIRS = 5184
THREAD_PAIRS = 4096
DENSE_CAPACITY = 15841
ZERO216 = "0" * 64
MAX_CLUSTERS = 4096
MAX_BATCH = BRIDGE
OP_DOMAIN = b"HHS-P164-GCMSL-OPERATION-V1\0"
REDUCE_DOMAIN = b"HHS-P164-GCMSL-REDUCTION-V1\0"
INVARIANT_DOMAIN = b"HHS-P164-GCMSL-INVARIANT-V1\0"
JOURNAL_DOMAIN = b"HHS-P164-GCMSL-JOURNAL-V1\0"


class GCMSError(ValueError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def hash216(
    domain: bytes,
    body: Mapping[str, Any],
    *,
    previous_root: str = ZERO216,
    sequence: int = 0,
) -> tuple[tuple[str, ...], str]:
    payload = domain + canonical_bytes(body)
    positions = tuple(
        Hash216Genome.positions(
            payload,
            previous_root=previous_root,
            sequence=sequence,
        )
    )
    return positions, str(Hash216Genome.root(positions))


def sha256_json(domain: bytes, body: Any) -> str:
    return sha256(domain + canonical_bytes(body)).hexdigest()
