from __future__ import annotations

import asyncio

from hhs_backend.runtime.runtime_event_bus import HHSRuntimeEventBus
from hhs_backend.runtime.runtime_event_schema import HHSRuntimeEventEnvelope, compute_hash72
from hhs_runtime.hhs_runtime_dataflow_guard_v1 import runtime_dataflow_guard_self_test
from hhs_runtime.runtime_event_bus import RuntimeEventBus
from hhs_runtime.runtime_event_schema import HHSEvent


def test_runtime_event_schema_hash72_is_native_72_symbols():
    digest = compute_hash72({"b": 2, "a": 1})
    assert isinstance(digest, str)
    assert len(digest) == 72
    assert digest == compute_hash72({"a": 1, "b": 2})


def test_backend_event_bus_attaches_propagation_receipt():
    bus = HHSRuntimeEventBus()
    event = bus.create_event("unit.event", {"ok": True}, "test")
    receipt = event.metadata.get("io_propagation_record")
    assert receipt
    assert receipt["direction"] == "PROPAGATION"
    assert receipt["authority_ok"] is True
    assert len(receipt["payload_hash72"]) == 72


def test_runtime_event_bus_payload_is_guarded():
    async def run():
        bus = RuntimeEventBus()
        event = HHSEvent(event_type="runtime", payload={"ok": True})
        await bus.emit(event)
        return event

    event = asyncio.run(run())
    receipt = event.payload.get("io_propagation_record")
    assert receipt
    assert receipt["direction"] == "PROPAGATION"
    assert receipt["authority_ok"] is True


def test_dataflow_guard_self_test_passes():
    result = runtime_dataflow_guard_self_test()
    assert result["propagation_authority_ok"] is True
    assert result["egress_authority_ok"] is True
    assert len(result["dataflow_hash72"]) == 72
    assert result["status"]["ledger"]["ok"] is True


def test_event_envelope_hash_verifies_after_native_hash72_change():
    envelope = HHSRuntimeEventEnvelope(
        event_id="evt-1",
        event_type="runtime.step",
        runtime_id="runtime-test",
        branch_id="main",
        schema_version="v1",
        created_at_ns=1,
        parent_event_hash72="GENESIS",
        receipt_hash72="receipt-test",
        payload={"z": 1, "a": 2},
    )
    assert len(envelope.event_hash72) == 72
    assert envelope.verify_event_hash72() is True
