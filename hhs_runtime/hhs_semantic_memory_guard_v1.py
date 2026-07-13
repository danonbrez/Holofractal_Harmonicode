"""
HHS Semantic Memory Guard v1
============================

Canonical containment seam for semantic memory, embedding, and vector-cache
operations.

Semantic memory is a propagation layer, not an alternate authority surface. This
module binds semantic writes, links, searches, and vector-cache persistence to the
unified Hash72 receipt chain using deterministic 72-symbol payload digests.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional
import json
import uuid

from hhs_runtime.hhs_hash72_kernel_authority_v1 import hash72_kernel_digest, make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger


SEMANTIC_GUARD_SCHEMA = "HHS_SEMANTIC_MEMORY_GUARD_V1"
HASH72_WIDTH = 72


def canonical_json(value: Any) -> str:
    """Stable projection for semantic guard hashing."""

    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def semantic_hash72(value: Any, *, width: int = HASH72_WIDTH) -> str:
    """Return a C u^72 kernel-backed 72-symbol Hash72 digest for semantic/vector payloads."""

    return hash72_kernel_digest("hhs_semantic_memory_guard_v1", canonical_json(value), width=width)


def semantic_hash72_witness(value: Any, *, width: int = HASH72_WIDTH) -> Dict[str, Any]:
    """Full C u^72 Digital DNA witness for semantic/vector payloads."""

    return make_hash72_kernel_witness("hhs_semantic_memory_guard_v1", canonical_json(value), width=width).to_dict()


def is_hash72(value: Any, *, width: int = HASH72_WIDTH) -> bool:
    return isinstance(value, str) and len(value) == width


def normalize_hash72(value: Optional[str], *, payload: Mapping[str, Any]) -> str:
    """Preserve valid Hash72 values and canonically repair absent/invalid ones.

    Older semantic-memory code used SHA-256 hex truncation, which produced 64
    symbols rather than a canonical 72-symbol Hash72 state. This helper prevents
    that shorter digest from becoming an alternate semantic authority path.
    """

    if is_hash72(value):
        return str(value)
    return semantic_hash72({"declared_hash72": value or "", "payload": dict(payload)})


@dataclass(frozen=True)
class SemanticGuardRecord:
    schema: str
    guard_id: str
    action: str
    source: str
    payload_hash72: str
    payload_hash72_kernel_witness: Dict[str, Any]
    payload: Dict[str, Any]
    ledger_entry_count: int
    ledger_tip_hash72: str
    ledger_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSSemanticMemoryGuardError(RuntimeError):
    """Raised when semantic/vector state attempts unguarded propagation."""


def commit_semantic_record(action: str, source: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Commit a semantic-memory operation to the unified Hash72 ledger."""

    if not action:
        raise HHSSemanticMemoryGuardError("semantic guard action is required")
    if not source:
        raise HHSSemanticMemoryGuardError("semantic guard source is required")

    payload_dict = dict(payload)
    pre_record = {
        "schema": SEMANTIC_GUARD_SCHEMA,
        "guard_id": str(uuid.uuid4()),
        "action": action,
        "source": source,
        "payload_hash72": semantic_hash72(payload_dict),
        "payload_hash72_kernel_witness": semantic_hash72_witness(payload_dict),
        "payload": payload_dict,
    }
    ledger = append_payload(f"SEMANTIC_{action}", f"HHSSemanticMemoryGuard.{source}", pre_record)
    record = SemanticGuardRecord(
        schema=SEMANTIC_GUARD_SCHEMA,
        guard_id=pre_record["guard_id"],
        action=action,
        source=source,
        payload_hash72=pre_record["payload_hash72"],
        payload_hash72_kernel_witness=pre_record["payload_hash72_kernel_witness"],
        payload=payload_dict,
        ledger_entry_count=int(ledger.get("entry_count") or 0),
        ledger_tip_hash72=str(ledger.get("tip_hash72") or ""),
        ledger_hash72=str(ledger.get("ledger_hash72") or ""),
    ).to_dict()
    return record


def semantic_memory_guard_self_test() -> Dict[str, Any]:
    payload = {"semantic_text": "guarded semantic memory", "memory_type": "symbolic"}
    normalized = normalize_hash72(None, payload=payload)
    write = commit_semantic_record("MEMORY_WRITE", "self_test", {**payload, "hash72": normalized})
    query = commit_semantic_record("SEARCH_QUERY", "self_test", {"query_hash72": semantic_hash72("guarded")})
    return {
        "schema": "HHS_SEMANTIC_MEMORY_GUARD_SELF_TEST_V1",
        "normalized_hash72_len": len(normalized),
        "write": write,
        "query": query,
        "ledger": verify_unified_ledger(),
    }


if __name__ == "__main__":
    print(semantic_memory_guard_self_test())
