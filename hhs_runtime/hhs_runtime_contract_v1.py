"""
HHS Canonical Runtime Contract v1
=================================

Single authoritative interface contract for guarded runtime traffic.

This module is intentionally additive: it does not replace the kernel, Hash72
ledger, IO gateway, service registry, event bus, semantic memory, or persistence
surface. It provides one schema language that those surfaces can emit and verify
so interface drift does not create alternate execution paths.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional
import time
import uuid

from hhs_runtime.hhs_authority_gate_v1 import audit_runtime_authority
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import hash72_kernel_digest, make_hash72_kernel_witness

CONTRACT_VERSION = "HHS_CANONICAL_RUNTIME_CONTRACT_V1"
HASH72_LEN = 72
AUTHORIZED_PACKET_DIRECTIONS = {"INGRESS", "PROPAGATION", "EGRESS", "INTERNAL"}
AUTHORIZED_CONTRACT_TYPES = {
    "execution_request",
    "runtime_packet",
    "receipt",
    "service_descriptor",
    "event",
    "vector_cache_entry",
    "persistence_record",
    "authority_audit",
    "replay_record",
    "api_response",
}


class HHSRuntimeContractError(RuntimeError):
    """Raised when a runtime object violates the canonical contract."""


def is_hash72(value: Any) -> bool:
    return isinstance(value, str) and len(value) == HASH72_LEN


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def payload_hash72(value: Any) -> str:
    """Kernel-backed 72-symbol Hash72 projection for contract payloads."""

    return hash72_kernel_digest("hhs_canonical_runtime_contract_payload_v1", canonical_json(value), width=HASH72_LEN)


def payload_hash72_witness(value: Any) -> Dict[str, Any]:
    """Full C u^72 Digital DNA witness for a contract payload."""

    return make_hash72_kernel_witness("hhs_canonical_runtime_contract_payload_v1", canonical_json(value), width=HASH72_LEN).to_dict()


def contract_hash72(value: Any) -> str:
    return payload_hash72({"contract_version": CONTRACT_VERSION, "value": value})


@dataclass(frozen=True)
class HHSContractValidation:
    ok: bool
    contract_type: str
    schema: str
    hash72: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HHSExecutionRequest:
    request_id: str
    source: str
    operation: str
    payload: Dict[str, Any] = field(default_factory=dict)
    requires_authority: bool = True
    created_at: float = field(default_factory=time.time)
    schema: str = "HHS_EXECUTION_REQUEST_CONTRACT_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["contract_version"] = CONTRACT_VERSION
        data["contract_type"] = "execution_request"
        data["contract_hash72"] = contract_hash72({k: v for k, v in data.items() if k != "contract_hash72"})
        return data


@dataclass(frozen=True)
class HHSRuntimePacket:
    packet_id: str
    direction: str
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    io_receipt: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    schema: str = "HHS_RUNTIME_PACKET_CONTRACT_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["contract_version"] = CONTRACT_VERSION
        data["contract_type"] = "runtime_packet"
        data["payload_hash72"] = payload_hash72(self.payload)
        data["contract_hash72"] = contract_hash72({k: v for k, v in data.items() if k != "contract_hash72"})
        return data


@dataclass(frozen=True)
class HHSReceiptContract:
    state_hash72: str
    receipt_hash72: str
    source: str
    runtime_step: Optional[int] = None
    authority_audit: Dict[str, Any] = field(default_factory=dict)
    unified_ledger: Dict[str, Any] = field(default_factory=dict)
    schema: str = "HHS_RECEIPT_CONTRACT_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["contract_version"] = CONTRACT_VERSION
        data["contract_type"] = "receipt"
        data["contract_hash72"] = contract_hash72({k: v for k, v in data.items() if k != "contract_hash72"})
        return data


@dataclass(frozen=True)
class HHSServiceDescriptorContract:
    name: str
    module: str
    function: str
    service_type: str
    description: str = ""
    requires_authority: bool = True
    request_schema: Dict[str, Any] = field(default_factory=dict)
    response_schema: Dict[str, Any] = field(default_factory=dict)
    schema: str = "HHS_SERVICE_DESCRIPTOR_CONTRACT_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["contract_version"] = CONTRACT_VERSION
        data["contract_type"] = "service_descriptor"
        data["contract_hash72"] = contract_hash72({k: v for k, v in data.items() if k != "contract_hash72"})
        return data


@dataclass(frozen=True)
class HHSEventContract:
    event_id: str
    event_type: str
    source: str
    payload: Dict[str, Any]
    receipt_hash72: str = ""
    parent_event_hash72: str = ""
    created_at_ns: int = field(default_factory=time.time_ns)
    schema: str = "HHS_EVENT_CONTRACT_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["contract_version"] = CONTRACT_VERSION
        data["contract_type"] = "event"
        data["event_hash72"] = contract_hash72({k: v for k, v in data.items() if k not in {"event_hash72", "contract_hash72"}})
        data["contract_hash72"] = contract_hash72(data)
        return data


@dataclass(frozen=True)
class HHSVectorCacheEntryContract:
    key: str
    source: str
    vector_record: Dict[str, Any]
    backing_receipt: Dict[str, Any]
    schema: str = "HHS_VECTOR_CACHE_ENTRY_CONTRACT_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["contract_version"] = CONTRACT_VERSION
        data["contract_type"] = "vector_cache_entry"
        data["vector_hash72"] = payload_hash72(self.vector_record)
        data["contract_hash72"] = contract_hash72({k: v for k, v in data.items() if k != "contract_hash72"})
        return data


@dataclass(frozen=True)
class HHSPersistenceRecordContract:
    path: str
    source: str
    operation: str
    payload_hash72: str
    io_receipt: Dict[str, Any] = field(default_factory=dict)
    schema: str = "HHS_PERSISTENCE_RECORD_CONTRACT_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["contract_version"] = CONTRACT_VERSION
        data["contract_type"] = "persistence_record"
        data["contract_hash72"] = contract_hash72({k: v for k, v in data.items() if k != "contract_hash72"})
        return data


@dataclass(frozen=True)
class HHSAPIResponseContract:
    route: str
    method: str
    status: str
    payload: Dict[str, Any]
    io: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    schema: str = "HHS_API_RESPONSE_CONTRACT_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["contract_version"] = CONTRACT_VERSION
        data["contract_type"] = "api_response"
        data["payload_hash72"] = payload_hash72(self.payload)
        data["contract_hash72"] = contract_hash72({k: v for k, v in data.items() if k != "contract_hash72"})
        return data


def make_execution_request(source: str, operation: str, payload: Optional[Mapping[str, Any]] = None, *, requires_authority: bool = True) -> Dict[str, Any]:
    return HHSExecutionRequest(
        request_id=str(uuid.uuid4()),
        source=source,
        operation=operation,
        payload=dict(payload or {}),
        requires_authority=requires_authority,
    ).to_dict()


def make_runtime_packet(direction: str, source: str, payload: Optional[Mapping[str, Any]] = None, *, io_receipt: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return HHSRuntimePacket(
        packet_id=str(uuid.uuid4()),
        direction=direction,
        source=source,
        payload=dict(payload or {}),
        io_receipt=dict(io_receipt or {}),
    ).to_dict()


def make_receipt_contract(receipt: Mapping[str, Any], *, source: str = "unknown") -> Dict[str, Any]:
    return HHSReceiptContract(
        state_hash72=str(receipt.get("state_hash72") or ""),
        receipt_hash72=str(receipt.get("receipt_hash72") or ""),
        source=source,
        runtime_step=receipt.get("step"),
        authority_audit=dict(receipt.get("authority_audit") or {}),
        unified_ledger=dict(receipt.get("unified_ledger") or {}),
    ).to_dict()


def make_service_descriptor_contract(service: Mapping[str, Any]) -> Dict[str, Any]:
    return HHSServiceDescriptorContract(
        name=str(service.get("name") or ""),
        module=str(service.get("module") or ""),
        function=str(service.get("function") or ""),
        service_type=str(service.get("service_type") or "runtime"),
        description=str(service.get("description") or ""),
        requires_authority=bool(service.get("requires_authority", True)),
        request_schema=dict(service.get("schema") or service.get("request_schema") or {}),
        response_schema=dict(service.get("response_schema") or {}),
    ).to_dict()


def make_api_response_contract(route: str, method: str, payload: Optional[Mapping[str, Any]] = None, *, io: Optional[Mapping[str, Any]] = None, status: str = "ok") -> Dict[str, Any]:
    return HHSAPIResponseContract(
        route=route,
        method=method,
        status=status,
        payload=dict(payload or {}),
        io=dict(io or {}),
    ).to_dict()


def envelope_api_response(route: str, method: str, payload: Mapping[str, Any], *, io: Optional[Mapping[str, Any]] = None, status: str = "ok") -> Dict[str, Any]:
    body = dict(payload or {})
    body.setdefault("schema", "HHS_CANONICAL_API_RESPONSE_ENVELOPE_V1")
    body["runtime_contract"] = make_api_response_contract(route, method, body, io=io, status=status)
    assert_contract(body["runtime_contract"], expected_type="api_response")
    return body


def make_authority_audit_contract(runtime_state: Mapping[str, Any], *, source: str, receipt: Optional[Mapping[str, Any]] = None, require_receipt: bool = True) -> Dict[str, Any]:
    audit = audit_runtime_authority(runtime_state, source=source, receipt=receipt, require_receipt=require_receipt).to_dict()
    audit["schema"] = "HHS_AUTHORITY_AUDIT_CONTRACT_V1"
    audit["contract_version"] = CONTRACT_VERSION
    audit["contract_type"] = "authority_audit"
    audit["contract_hash72"] = contract_hash72(audit)
    return audit


def validate_contract(obj: Mapping[str, Any], *, expected_type: Optional[str] = None, require_hash72: bool = True) -> Dict[str, Any]:
    data = dict(obj or {})
    reasons: list[str] = []
    contract_type = str(data.get("contract_type") or "")
    schema = str(data.get("schema") or "")

    if expected_type and contract_type != expected_type:
        reasons.append(f"contract_type mismatch: expected {expected_type}, got {contract_type or '<missing>'}")
    if contract_type and contract_type not in AUTHORIZED_CONTRACT_TYPES:
        reasons.append(f"unknown contract_type: {contract_type}")
    if not contract_type:
        reasons.append("contract_type is required")
    if not schema:
        reasons.append("schema is required")
    if data.get("contract_version") != CONTRACT_VERSION:
        reasons.append("contract_version mismatch or missing")

    if contract_type == "runtime_packet":
        if data.get("direction") not in AUTHORIZED_PACKET_DIRECTIONS:
            reasons.append("runtime_packet direction is unauthorized")
        if require_hash72 and not is_hash72(data.get("payload_hash72")):
            reasons.append("runtime_packet requires payload_hash72")
    if contract_type == "receipt":
        if require_hash72 and not is_hash72(data.get("state_hash72")):
            reasons.append("receipt requires native state_hash72")
        if require_hash72 and not is_hash72(data.get("receipt_hash72")):
            reasons.append("receipt requires native receipt_hash72")
    if contract_type == "service_descriptor":
        for key in ("name", "module", "function"):
            if not data.get(key):
                reasons.append(f"service_descriptor requires {key}")
    if contract_type == "vector_cache_entry":
        receipt = dict(data.get("backing_receipt") or {})
        if require_hash72 and (not is_hash72(receipt.get("state_hash72")) or not is_hash72(receipt.get("receipt_hash72"))):
            reasons.append("vector_cache_entry requires backing Hash72 receipt")
        if require_hash72 and not is_hash72(data.get("vector_hash72")):
            reasons.append("vector_cache_entry requires vector_hash72")

    if contract_type == "api_response":
        if not data.get("route"):
            reasons.append("api_response requires route")
        if not data.get("method"):
            reasons.append("api_response requires method")
        if require_hash72 and not is_hash72(data.get("payload_hash72")):
            reasons.append("api_response requires payload_hash72")

    validation = HHSContractValidation(
        ok=len(reasons) == 0,
        contract_type=contract_type,
        schema=schema,
        hash72=str(data.get("contract_hash72") or contract_hash72(data)),
        reasons=reasons,
    ).to_dict()
    if reasons:
        return validation
    return validation


def assert_contract(obj: Mapping[str, Any], *, expected_type: Optional[str] = None, require_hash72: bool = True) -> Dict[str, Any]:
    validation = validate_contract(obj, expected_type=expected_type, require_hash72=require_hash72)
    if not validation["ok"]:
        raise HHSRuntimeContractError("HHS runtime contract violation: " + "; ".join(validation["reasons"]))
    return validation


def runtime_contract_self_test() -> Dict[str, Any]:
    fake_hash72 = "H" * HASH72_LEN
    request = make_execution_request("runtime_contract_self_test", "self_test", {"ok": True})
    packet = make_runtime_packet("INGRESS", "runtime_contract_self_test", request)
    receipt = make_receipt_contract({"step": 1, "state_hash72": fake_hash72, "receipt_hash72": fake_hash72}, source="runtime_contract_self_test")
    api_response = make_api_response_contract("/api/runtime/contract/self-test", "GET", {"ok": True})
    service = make_service_descriptor_contract({
        "name": "runtime_contract.self_test",
        "module": "hhs_runtime.hhs_runtime_contract_v1",
        "function": "runtime_contract_self_test",
        "service_type": "contract",
        "description": "Validate canonical runtime contract objects.",
        "requires_authority": True,
    })
    validations = [
        assert_contract(request, expected_type="execution_request"),
        assert_contract(packet, expected_type="runtime_packet"),
        assert_contract(receipt, expected_type="receipt"),
        assert_contract(service, expected_type="service_descriptor"),
        assert_contract(api_response, expected_type="api_response"),
    ]
    return {
        "schema": "HHS_RUNTIME_CONTRACT_SELF_TEST_V1",
        "contract_version": CONTRACT_VERSION,
        "request": request,
        "packet": packet,
        "receipt": receipt,
        "service": service,
        "api_response": api_response,
        "validations": validations,
        "canonical_json_hash72": contract_hash72(canonical_json({"b": 2, "a": 1})),
    }


if __name__ == "__main__":
    print(runtime_contract_self_test())
