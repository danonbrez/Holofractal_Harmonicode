"""
HHS Runtime Dataflow Guard v1
=============================

Canonical containment helper for runtime events, websocket packets, and any
other propagation surfaces that may influence system behavior.

This module deliberately reuses the canonical IO gateway instead of creating a
third authority surface. Event/log/stream propagation is admissible only when it
is recorded as Hash72-backed ingress, propagation, or egress.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway, payload_hash72


_DATAFLOW_CONTROLLER: Optional[HHSRuntimeController] = None
_DATAFLOW_GATEWAY: Optional[HHSIOGateway] = None


def dataflow_gateway() -> HHSIOGateway:
    """Return the process-local canonical dataflow gateway."""

    global _DATAFLOW_CONTROLLER, _DATAFLOW_GATEWAY
    if _DATAFLOW_GATEWAY is None:
        _DATAFLOW_CONTROLLER = HHSRuntimeController()
        _DATAFLOW_GATEWAY = HHSIOGateway(_DATAFLOW_CONTROLLER)
    return _DATAFLOW_GATEWAY


def compact_io_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Return the safe transport projection of a canonical IO record.

    The full payload remains committed to the unified ledger. Realtime packets
    receive the compact receipt projection so consumers can verify lineage
    without recursively embedding the entire packet inside itself.
    """

    audit = dict(record.get("authority_audit") or {})
    return {
        "schema": record.get("schema"),
        "io_id": record.get("io_id"),
        "direction": record.get("direction"),
        "source": record.get("source"),
        "payload_hash72": record.get("payload_hash72"),
        "runtime_step": record.get("runtime_step"),
        "ledger_entry_count": record.get("ledger_entry_count"),
        "ledger_tip_hash72": record.get("ledger_tip_hash72"),
        "ledger_hash72": record.get("ledger_hash72"),
        "authority_ok": audit.get("ok"),
        "authority_invariants": audit.get("invariants"),
    }


def _payload_projection(payload: Mapping[str, Any]) -> Dict[str, Any]:
    projected = dict(payload or {})
    projected.pop("io_record", None)
    projected.pop("io_propagation_record", None)
    projected.pop("io_egress_record", None)
    projected.pop("dataflow_hash72", None)
    return projected


def guard_propagation(source: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Commit a runtime propagation event to the canonical IO receipt chain."""

    return dataflow_gateway().propagate(source, _payload_projection(payload))


def guard_egress(source: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Commit a runtime egress packet to the canonical IO receipt chain."""

    return dataflow_gateway().egress(source, _payload_projection(payload))


def attach_propagation_record(source: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a payload copy carrying a compact propagation receipt."""

    packet = deepcopy(dict(payload or {}))
    record = guard_propagation(source, packet)
    packet["io_propagation_record"] = compact_io_record(record)
    packet["dataflow_hash72"] = payload_hash72(_payload_projection(packet))
    return packet


def attach_egress_record(source: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a payload copy carrying a compact egress receipt."""

    packet = deepcopy(dict(payload or {}))
    record = guard_egress(source, packet)
    packet["io_egress_record"] = compact_io_record(record)
    packet["dataflow_hash72"] = payload_hash72(_payload_projection(packet))
    return packet


def runtime_dataflow_guard_self_test() -> Dict[str, Any]:
    propagation = attach_propagation_record(
        "runtime_dataflow_guard_self_test.propagation",
        {"event_type": "self_test", "payload": {"ok": True}},
    )
    egress = attach_egress_record(
        "runtime_dataflow_guard_self_test.egress",
        propagation,
    )
    status = dataflow_gateway().status()
    return {
        "schema": "HHS_RUNTIME_DATAFLOW_GUARD_SELF_TEST_V1",
        "propagation_authority_ok": propagation["io_propagation_record"].get("authority_ok"),
        "egress_authority_ok": egress["io_egress_record"].get("authority_ok"),
        "dataflow_hash72": egress.get("dataflow_hash72"),
        "status": status,
    }


if __name__ == "__main__":
    print(runtime_dataflow_guard_self_test())
