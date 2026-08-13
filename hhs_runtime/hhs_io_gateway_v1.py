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

Repeated read-only requests may reuse an immutable, previously committed IO
record when the source, payload identity, and complete runtime-state projection
are unchanged. Reuse accelerates transport; it never creates alternate
authority and never mutates the committed record.

Pass 217 restoration rule:
Production route sources explicitly bound by the cumulative route composer must
traverse the inherited Pass 043 kernel-derived composition preflight before an
IO ingress record may be created or reused. Receipt-backed IO reuse therefore
cannot become a bypass around kernel-derived route composition.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from threading import RLock
from typing import Any, Dict, Mapping, Optional, Tuple
import json
import os
import time
import uuid

from hhs_runtime.hhs_authority_gate_v1 import assert_runtime_authorized
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_unified_hash72_ledger_v1 import (
    append_payload,
    unified_ledger_summary,
    verify_unified_ledger,
    warm_unified_ledger_cache,
)
from hhs_runtime.hhs_runtime_contract_v1 import make_runtime_packet, assert_contract


IO_SCHEMA = "HHS_CANONICAL_IO_RECORD_V1"
VECTOR_SCHEMA = "HHS_VALIDATED_VECTOR_CACHE_RECORD_V1"
AUTHORIZED_DIRECTIONS = {"INGRESS", "PROPAGATION", "EGRESS"}
READ_CACHE_SCHEMA = "HHS_RECEIPT_BACKED_IO_READ_REUSE_V1"


def canonical_json(value: Any) -> str:
    """Stable JSON projection for IO containment records."""

    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def payload_hash72_witness(value: Any, *, width: int = 72) -> Dict[str, Any]:
    """Full C u^72 Digital DNA witness for IO payload projection."""

    return make_hash72_kernel_witness(
        "hhs_canonical_io_payload_v1",
        canonical_json(value),
        width=width,
    ).to_dict()


def payload_hash72(value: Any, *, width: int = 72) -> str:
    """Kernel-backed Hash72 digest over the canonical IO payload projection."""

    return str(payload_hash72_witness(value, width=width)["digest"])


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
    """Canonical sealed-runtime IO gateway with bounded receipt-backed reuse."""

    def __init__(self, controller: Any):
        self.controller = controller
        self.history: list[Dict[str, Any]] = []
        self._lock = RLock()
        self._witness_cache: "OrderedDict[str, Tuple[str, Dict[str, Any]]]" = OrderedDict()
        self._read_record_cache: "OrderedDict[Tuple[Any, ...], Dict[str, Any]]" = OrderedDict()
        self._active_read_context: Dict[Tuple[str, str], int] = {}
        self._route_composition_cache: Dict[str, Dict[str, Any]] = {}
        self._witness_cache_limit = max(16, int(os.environ.get("HHS_IO_WITNESS_CACHE_SIZE", "512")))
        self._read_cache_limit = max(16, int(os.environ.get("HHS_IO_READ_CACHE_SIZE", "512")))
        self._history_limit = max(32, int(os.environ.get("HHS_IO_HISTORY_SIZE", "2048")))
        self._cache_hits = 0
        self._cache_misses = 0
        self._ledger_warm_status = warm_unified_ledger_cache()

    def _runtime_state(self) -> Mapping[str, Any]:
        return self.controller.latest_runtime_state()

    @staticmethod
    def _runtime_token(runtime_state: Mapping[str, Any]) -> str:
        # The full canonical state projection prevents reuse across any mutation,
        # including changes that do not advance the numeric step counter.
        return canonical_json(runtime_state)

    def _remember_history(self, record: Dict[str, Any]) -> None:
        self.history.append(record)
        overflow = len(self.history) - self._history_limit
        if overflow > 0:
            del self.history[:overflow]

    @staticmethod
    def _lru_get(cache: OrderedDict, key: Any) -> Any:
        value = cache.get(key)
        if value is not None:
            cache.move_to_end(key)
        return value

    @staticmethod
    def _lru_put(cache: OrderedDict, key: Any, value: Any, limit: int) -> None:
        cache[key] = value
        cache.move_to_end(key)
        while len(cache) > limit:
            cache.popitem(last=False)

    def _payload_identity(self, payload: Mapping[str, Any]) -> Tuple[str, Dict[str, Any]]:
        canonical = canonical_json(payload)
        with self._lock:
            cached = self._lru_get(self._witness_cache, canonical)
            if cached is not None:
                digest, witness = cached
                return str(digest), dict(witness)

        witness = make_hash72_kernel_witness(
            "hhs_canonical_io_payload_v1",
            canonical,
            width=72,
        ).to_dict()
        digest = str(witness["digest"])
        with self._lock:
            self._lru_put(
                self._witness_cache,
                canonical,
                (digest, dict(witness)),
                self._witness_cache_limit,
            )
        return digest, witness

    @staticmethod
    def _is_get_ingress(direction: str, payload: Mapping[str, Any]) -> bool:
        return direction == "INGRESS" and str(payload.get("method", "")).upper() == "GET"

    def _read_context_key(self, source: str, runtime_token: str) -> Tuple[str, str]:
        return source, runtime_token

    def _begin_read_context(self, source: str, runtime_token: str) -> None:
        key = self._read_context_key(source, runtime_token)
        self._active_read_context[key] = self._active_read_context.get(key, 0) + 1

    def _consume_read_context(self, source: str, runtime_token: str) -> bool:
        key = self._read_context_key(source, runtime_token)
        count = self._active_read_context.get(key, 0)
        if count <= 0:
            return False
        if count == 1:
            self._active_read_context.pop(key, None)
        else:
            self._active_read_context[key] = count - 1
        return True

    def _route_composition_preflight(
        self,
        direction: str,
        source: str,
        payload: Mapping[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if direction != "INGRESS":
            return None
        preflight = compose_bound_route_ingress(
            source,
            payload,
            cache=self._route_composition_cache,
        )
        if preflight is not None and not preflight.get("ok"):
            raise HHSIOGatewayError(
                "REJECT_RUNTIME_ROUTE_WITHOUT_CUMULATIVE_COMPOSITION:"
                + str(source)
            )
        return preflight

    def _reused_record(
        self,
        record: Dict[str, Any],
        *,
        cache_key: Tuple[Any, ...],
        route_preflight: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        current_ledger = unified_ledger_summary()
        reused = dict(record)
        reused["cache_reuse"] = {
            "schema": READ_CACHE_SCHEMA,
            "reused": True,
            "original_io_id": record.get("io_id"),
            "cache_key_hash72": payload_hash72(list(cache_key)),
            "current_ledger_entry_count": current_ledger.get("entry_count"),
            "current_ledger_tip_hash72": current_ledger.get("tip_hash72"),
            "authority_rule": "IMMUTABLE_RECEIPT_REUSE_ONLY_WHEN_SOURCE_PAYLOAD_AND_RUNTIME_STATE_MATCH",
        }
        if route_preflight is not None:
            # This is the current request's composition proof, not the cached
            # request's proof. The immutable IO record is otherwise unchanged.
            reused["kernel_runtime_route_composition_preflight"] = dict(
                route_preflight
            )
        self._remember_history(reused)
        return reused

    def _record(
        self,
        direction: str,
        source: str,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if direction not in AUTHORIZED_DIRECTIONS:
            raise HHSIOGatewayError(f"unauthorized IO direction: {direction}")

        payload_dict = dict(payload or {})
        # Mandatory route composition precedes receipt creation and receipt-backed
        # read reuse. A cache hit can avoid transport work but cannot avoid the
        # inherited kernel-derived route composer.
        route_preflight = self._route_composition_preflight(
            direction,
            source,
            payload_dict,
        )
        runtime_state = self._runtime_state()
        runtime_token = self._runtime_token(runtime_state)
        payload_digest, payload_witness = self._payload_identity(payload_dict)

        with self._lock:
            reusable_read = self._is_get_ingress(direction, payload_dict)
            if reusable_read:
                self._begin_read_context(source, runtime_token)
            elif direction == "EGRESS":
                reusable_read = self._consume_read_context(source, runtime_token)

            cache_key = (
                direction,
                source,
                payload_digest,
                runtime_token,
            )
            if reusable_read:
                cached_record = self._lru_get(self._read_record_cache, cache_key)
                if cached_record is not None:
                    self._cache_hits += 1
                    return self._reused_record(
                        cached_record,
                        cache_key=cache_key,
                        route_preflight=route_preflight,
                    )
                self._cache_misses += 1

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
            "payload_hash72": payload_digest,
            "payload_hash72_kernel_witness": payload_witness,
            "payload": payload_dict,
            "runtime_step": runtime_state.get("step"),
            "authority_audit": audit,
        }
        if route_preflight is not None:
            pre_record["kernel_runtime_route_composition_preflight"] = dict(
                route_preflight
            )
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
            payload_hash72=payload_digest,
            payload_hash72_kernel_witness=payload_witness,
            payload=payload_dict,
            runtime_step=pre_record["runtime_step"],
            authority_audit=audit,
            ledger_entry_count=int(ledger.get("entry_count") or 0),
            ledger_tip_hash72=str(ledger.get("tip_hash72") or ""),
            ledger_hash72=str(ledger.get("ledger_hash72") or ""),
        ).to_dict()
        record["runtime_contract"] = runtime_packet
        if route_preflight is not None:
            record["kernel_runtime_route_composition_preflight"] = dict(
                route_preflight
            )

        with self._lock:
            if reusable_read:
                self._lru_put(
                    self._read_record_cache,
                    cache_key,
                    dict(record),
                    self._read_cache_limit,
                )
            self._remember_history(record)
        return record

    def ingress(self, source: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return self._record("INGRESS", source, payload)

    def propagate(self, source: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return self._record("PROPAGATION", source, payload)

    def egress(self, source: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return self._record("EGRESS", source, payload)

    def clear_read_cache(self) -> Dict[str, Any]:
        with self._lock:
            removed = len(self._read_record_cache)
            self._read_record_cache.clear()
            self._active_read_context.clear()
            return {
                "schema": "HHS_IO_READ_CACHE_INVALIDATION_V1",
                "removed": removed,
            }

    def validate_vector_cache_write(
        self,
        *,
        source: str,
        key: str,
        vector_record: Mapping[str, Any],
        backing_receipt: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Authorize a vector-cache write as receipt-backed propagation."""

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
        vector_digest, vector_witness = self._payload_identity(dict(vector_record))
        record = {
            "schema": VECTOR_SCHEMA,
            "cache_id": str(uuid.uuid4()),
            "source": source,
            "key": key,
            "vector_hash72": vector_digest,
            "vector_hash72_kernel_witness": vector_witness,
            "vector_record": dict(vector_record),
            "backing_receipt": dict(backing_receipt),
            "runtime_step": runtime_state.get("step"),
            "authority_audit": audit,
        }
        ledger = append_payload(
            "VALIDATED_VECTOR_CACHE_WRITE",
            f"HHSIOGateway.vector_cache.{source}",
            record,
        )
        record["unified_ledger"] = {
            "entry_count": ledger.get("entry_count"),
            "tip_hash72": ledger.get("tip_hash72"),
            "ledger_hash72": ledger.get("ledger_hash72"),
        }
        with self._lock:
            self._remember_history(record)
        return record

    def status(self, *, full_verify: bool = False) -> Dict[str, Any]:
        ledger = verify_unified_ledger() if full_verify else unified_ledger_summary()
        return {
            "schema": "HHS_IO_GATEWAY_STATUS_V1",
            "record_count": len(self.history),
            "last_record": self.history[-1] if self.history else None,
            "ledger": ledger,
            "ledger_validation_mode": "FULL_CHAIN" if full_verify else "INCREMENTAL_APPEND_VALIDATED",
            "cache": {
                "schema": READ_CACHE_SCHEMA,
                "witness_entries": len(self._witness_cache),
                "read_record_entries": len(self._read_record_cache),
                "route_composition_entries": len(self._route_composition_cache),
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "ledger_warm_status": self._ledger_warm_status,
            },
            "sealed_runtime_rule": "Only Hash72 receipt-chain records or receipt-backed validated vector-cache records are authorized; bound production routes additionally require kernel-derived cumulative composition before ingress or read reuse.",
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
    return {
        "schema": "HHS_IO_GATEWAY_SELF_TEST_V1",
        "ingress": ingress,
        "vector": vector,
        "egress": egress,
        "status": gateway.status(full_verify=True),
    }


if __name__ == "__main__":
    print(io_gateway_self_test())
