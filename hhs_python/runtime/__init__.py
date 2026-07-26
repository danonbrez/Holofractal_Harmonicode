"""HHS Python runtime package compatibility boundary.

The current slotted ``HHSRuntimeState`` is the canonical Python state model.
Several inherited persistence and replay surfaces still address its former
computed attributes. This package installs those attributes as deterministic
properties backed by existing state fields and ``runtime_metadata``; it does
not add a parallel state object or execution authority.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from .hhs_runtime_state import HHSRuntimeState

COMPATIBILITY_VERSION = "HHS_RUNTIME_STATE_STORE_COMPATIBILITY_V1"


def _canonical_state_payload(state: HHSRuntimeState) -> Dict[str, Any]:
    payload = state.to_dict()
    metadata = dict(payload.get("runtime_metadata") or {})
    for key in (
        "_compat_state_hash72",
        "_compat_receipt_hash72",
        "_compat_prev_receipt_hash72",
    ):
        metadata.pop(key, None)
    payload["runtime_metadata"] = metadata
    return payload


def _compat_hash72(value: Any) -> str:
    serialized = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return (digest + digest[:8])[:72]


def _get_receipt_hash72(state: HHSRuntimeState) -> str:
    explicit = state.runtime_metadata.get("_compat_receipt_hash72")
    if explicit:
        return str(explicit)
    receipt = state.latest_receipt()
    return str(receipt.receipt_hash72) if receipt else ""


def _set_receipt_hash72(state: HHSRuntimeState, value: str) -> None:
    state.runtime_metadata["_compat_receipt_hash72"] = str(value or "")


def _get_prev_receipt_hash72(state: HHSRuntimeState) -> str:
    explicit = state.runtime_metadata.get("_compat_prev_receipt_hash72")
    if explicit:
        return str(explicit)
    if len(state.receipts) >= 2:
        return str(state.receipts[-2].receipt_hash72)
    return ""


def _set_prev_receipt_hash72(state: HHSRuntimeState, value: str) -> None:
    state.runtime_metadata["_compat_prev_receipt_hash72"] = str(value or "")


def _get_state_hash72(state: HHSRuntimeState) -> str:
    explicit = state.runtime_metadata.get("_compat_state_hash72")
    if explicit:
        return str(explicit)
    receipt = state.latest_receipt()
    if receipt and receipt.source_hash72:
        return str(receipt.source_hash72)
    return _compat_hash72(_canonical_state_payload(state))


def _set_state_hash72(state: HHSRuntimeState, value: str) -> None:
    state.runtime_metadata["_compat_state_hash72"] = str(value or "")


def _get_timestamp_ns(state: HHSRuntimeState) -> int:
    return int(state.updated_ns)


def _set_timestamp_ns(state: HHSRuntimeState, value: int) -> None:
    state.updated_ns = int(value)


def _serialize_deterministic(state: HHSRuntimeState) -> str:
    return json.dumps(
        state.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _compute_state_hash72(state: HHSRuntimeState) -> str:
    return _compat_hash72(_canonical_state_payload(state))


def _diff(state: HHSRuntimeState, other: HHSRuntimeState) -> Dict[str, Any]:
    left = state.to_dict()
    right = other.to_dict()
    keys = sorted(set(left) | set(right))
    return {
        key: {"left": left.get(key), "right": right.get(key)}
        for key in keys
        if left.get(key) != right.get(key)
    }


def install_runtime_state_store_compatibility() -> str:
    if getattr(HHSRuntimeState, "_hhs_store_compatibility", None) == COMPATIBILITY_VERSION:
        return COMPATIBILITY_VERSION

    HHSRuntimeState.receipt_hash72 = property(  # type: ignore[attr-defined]
        _get_receipt_hash72,
        _set_receipt_hash72,
    )
    HHSRuntimeState.prev_receipt_hash72 = property(  # type: ignore[attr-defined]
        _get_prev_receipt_hash72,
        _set_prev_receipt_hash72,
    )
    HHSRuntimeState.state_hash72 = property(  # type: ignore[attr-defined]
        _get_state_hash72,
        _set_state_hash72,
    )
    HHSRuntimeState.timestamp_ns = property(  # type: ignore[attr-defined]
        _get_timestamp_ns,
        _set_timestamp_ns,
    )
    HHSRuntimeState.serialize_deterministic = _serialize_deterministic  # type: ignore[attr-defined]
    HHSRuntimeState.compute_state_hash72 = _compute_state_hash72  # type: ignore[attr-defined]
    HHSRuntimeState.diff = _diff  # type: ignore[attr-defined]
    HHSRuntimeState._hhs_store_compatibility = COMPATIBILITY_VERSION  # type: ignore[attr-defined]
    return COMPATIBILITY_VERSION


install_runtime_state_store_compatibility()

__all__ = [
    "HHSRuntimeState",
    "COMPATIBILITY_VERSION",
    "install_runtime_state_store_compatibility",
]
