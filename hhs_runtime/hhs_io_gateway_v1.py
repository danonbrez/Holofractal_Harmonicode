"""
HHS Canonical IO Gateway v1
===========================

Sealed-runtime ingress / propagation / egress authority surface.

No external data path should enter, move through, or leave the system except as
one of these authorized forms:

1. Hash72 receipt-chain record emitted by this gateway or another canonical
   authority surface.
2. Validated vector-cache record that carries a backing Hash72 receipt and can
   be traced to the unified ledger.

This module does not alter kernel semantics. It provides a deterministic,
repository-local containment seam for API, GUI, service, filesystem, vector,
and future plugin paths.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional
import json
import time
import uuid

from hhs_runtime.hhs_authority_gate_v1 import assert_runtime_authorized
from hhs_runtime.hhs_hash72_kernel_authority_v1 import hash72_kernel_digest, make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_runtime.hhs_runtime_contract_v1 import make_runtime_packet, assert_contract


IO_SCHEMA = "HHS_CANONICAL_IO_RECORD_V1"
VECTOR_SCHEMA = "HHS_VALIDATED_VECTOR_CACHE_RECORD_V1"
AUTHORIZED_DIRECTIONS = {"INGRESS", "PROPAGATION", "EGRESS"}


def canonical_json(value: Any) -> str:
    """Stable JSON projection for IO containment records."""

    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def payload_hash72(value: Any, *, width: int = 72) -> str:
    """Kernel-backed Hash72 digest over the canonical IO payload projection."""

    return hash72_kernel_digest("hhs_canonical_io_payload_v1", canonical_json(value), width=width)


def payload_hash72_witness(value: Any, *, width: int = 72) -> Dict[str, Any]:
    """Full C u^72 Digital DNA witness for IO payload projection."""

    return make_hash72_kernel_witness("hhs_canonical_io_payload_v1", canonical_json(value), width=width).to_dict()


@dataclass(frozen=True)
class HHSIORecord:
    schema: str
    io_id: str
    direction: str
    source: str
    payload_hash72: str
    payload_hash72_kernel_witness: Dict[str, Any]
    payload: Dict[str, Any]
    runtime_step: Optional[int]
    authority_audit: Dict[str, Any]
    ledger_entry_count: int
    ledger_tip_hash72: str
    ledger_hash72: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSIOGatewayError(RuntimeError):
    """Raised when a data path attempts to bypass canonical IO authority."""


class HHSIOGateway:
    """Canonical sealed-runtime IO gateway."""

    def __init__(self, controller: Any):
        self.controller = controller
        self.history: list[Dict[str, Any]] = []

    def _runtime_state(self) -> Mapping[str, Any]:
        return self.controller.latest_runtime_state()

    def _record(self, direction: str, source: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        if direction not in AUTHORIZED_DIRECTIONS:
            raise HHSIOGatewayError(f"unauthorized IO direction: {direction}")

        payload_dict = dict(payload or {})
        runtime_state = self._runtime_state()
        audit = assert_runtime_authorized(
            runtime_state,
            source=f"HHSIOGateway.{direction.lower()}.{source}",
            require_receipt=False,
        ).to_dict()

        pre_record = {
            "schema": IO_SCHEMA,
            "io_id": str(uuid.uuid4()),
            "direction": direction,
            "source": source,
            "payload_hash72": payload_hash72(payload_dict),
            "payload_hash72_kernel_witness": payload_hash72_witness(payload_dict),
            "payload": payload_dict,
            "runtime_step": runtime_state.get("step"),
            "authority_audit": audit,
        }
        ledger = append_payload(
            f"IO_{direction}",
            f"HHSIOGateway.{direction.lower()}.{source}",
            pre_record,
        )
        runtime_packet = make_runtime_packet(direction, source, payload_dict)
        assert_contract(runtime_packet, expected_type="runtime_packet")
        record = HHSIORecord(
            schema=IO_SCHEMA,
            io_id=pre_record["io_id"],
            direction=direction,
            source=source,
            payload_hash72=pre_record["payload_hash72"],
            payload_hash72_kernel_witness=pre_record["payload_hash72_kernel_witness"],
            payload=payload_dict,
            runtime_step=pre_record["runtime_step"],
            authority_audit=audit,
            ledger_entry_count=int(ledger.get("entry_count") or 0),
            ledger_tip_hash72=str(ledger.get("tip_hash72") or ""),
            ledger_hash72=str(ledger.get("ledger_hash72") or ""),
        ).to_dict()
        record["runtime_contract"] = runtime_packet
        self.history.append(record)
        return record

    def ingress(self, source: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return self._record("INGRESS", source, payload)

    def propagate(self, source: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return self._record("PROPAGATION", source, payload)

    def egress(self, source: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return self._record("EGRESS", source, payload)

    def validate_vector_cache_write(
        self,
        *,
        source: str,
        key: str,
        vector_record: Mapping[str, Any],
        backing_receipt: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Authorize a vector-cache write as receipt-backed propagation.

        Vector data may be cached for search/retrieval efficiency, but the cache
        is not an alternate authority surface. A cache write is admissible only
        when it carries a Hash72 state/receipt pair and is itself recorded in the
        unified ledger.
        """

        if not key:
            raise HHSIOGatewayError("validated vector cache key is required")
        if not backing_receipt.get("state_hash72") or not backing_receipt.get("receipt_hash72"):
            raise HHSIOGatewayError("validated vector cache write requires backing Hash72 state and receipt")

        runtime_state = self._runtime_state()
        audit = assert_runtime_authorized(
            runtime_state,
            source=f"HHSIOGateway.vector_cache.{source}",
            receipt=backing_receipt,
            require_receipt=True,
        ).to_dict()
        record = {
            "schema": VECTOR_SCHEMA,
            "cache_id": str(uuid.uuid4()),
            "source": source,
            "key": key,
            "vector_hash72": payload_hash72(vector_record),
            "vector_hash72_kernel_witness": payload_hash72_witness(vector_record),
            "vector_record": dict(vector_record),
            "backing_receipt": dict(backing_receipt),
            "runtime_step": runtime_state.get("step"),
            "authority_audit": audit,
        }
        ledger = append_payload("VALIDATED_VECTOR_CACHE_WRITE", f"HHSIOGateway.vector_cache.{source}", record)
        record["unified_ledger"] = {
            "entry_count": ledger.get("entry_count"),
            "tip_hash72": ledger.get("tip_hash72"),
            "ledger_hash72": ledger.get("ledger_hash72"),
        }
        self.history.append(record)
        return record

    def status(self) -> Dict[str, Any]:
        ledger = verify_unified_ledger()
        return {
            "schema": "HHS_IO_GATEWAY_STATUS_V1",
            "record_count": len(self.history),
            "last_record": self.history[-1] if self.history else None,
            "ledger": ledger,
            "sealed_runtime_rule": "Only Hash72 receipt-chain records or receipt-backed validated vector-cache records are authorized.",
        }


def io_gateway_self_test() -> Dict[str, Any]:
    from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController

    controller = HHSRuntimeController()
    gateway = HHSIOGateway(controller)
    ingress = gateway.ingress("io_gateway_self_test", {"message": "hello"})
    authorized = controller.authorized_tick(source="io_gateway_self_test.tick")
    vector = gateway.validate_vector_cache_write(
        source="io_gateway_self_test",
        key="self-test-vector",
        vector_record={"dims": 3, "values": [1, 0, -1]},
        backing_receipt=authorized["receipt"],
    )
    egress = gateway.egress("io_gateway_self_test", {"ok": True})
    return {"schema": "HHS_IO_GATEWAY_SELF_TEST_V1", "ingress": ingress, "vector": vector, "egress": egress, "status": gateway.status()}


if __name__ == "__main__":
    print(io_gateway_self_test())
