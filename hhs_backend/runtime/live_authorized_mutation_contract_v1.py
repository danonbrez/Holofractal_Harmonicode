"""
HHS Live Authorized Mutation Contract v1
=======================================

Pass 048 promotes a narrow, explicitly allow-listed set of GUI-requested
operations from receipt-only acknowledgement into witnessed live mutation.
The browser remains a request/projection surface only: no UI event directly
becomes runtime truth.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Mapping, Optional
import time
import uuid

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_048_AUTHORIZED_LIVE_MUTATION_EXECUTION_V1"
AUTHORITY = "HHS_FASTAPI_LIVE_AUTHORIZED_MUTATION_AUTHORITY_V1"
COMMAND_SCHEMA = "HHS_LIVE_AUTHORIZED_MUTATION_COMMAND_V1"
CONTRACT_SCHEMA = "HHS_LIVE_AUTHORIZED_MUTATION_CONTRACT_V1"

AUTHORIZED_MUTATION = "AUTHORIZED_MUTATION"
MUTATION_RECEIPT_SCHEMA = "HHS_LIVE_MUTATION_RECEIPT_V1"

REJECT_UI_EVENT_AS_RUNTIME_TRUTH = "REJECT_UI_EVENT_AS_RUNTIME_TRUTH"
REJECT_MUTATION_WITHOUT_PRE_STATE = "REJECT_MUTATION_WITHOUT_PRE_STATE"
REJECT_MUTATION_WITHOUT_TRANSFORMATION_IDENTITY = "REJECT_MUTATION_WITHOUT_TRANSFORMATION_IDENTITY"
REJECT_MUTATION_WITHOUT_POST_STATE = "REJECT_MUTATION_WITHOUT_POST_STATE"
REJECT_MUTATION_WITHOUT_REVERSAL_WITNESS = "REJECT_MUTATION_WITHOUT_REVERSAL_WITNESS"
REJECT_MUTATION_NOT_ALLOWLISTED = "REJECT_MUTATION_NOT_ALLOWLISTED"
REJECT_MUTATION_WITHOUT_KERNEL_DERIVATION = "REJECT_MUTATION_WITHOUT_KERNEL_DERIVATION"
REJECT_MUTATION_WITHOUT_RECEIPT = "REJECT_MUTATION_WITHOUT_RECEIPT"
REJECT_GUI_ASSUMED_SUCCESS_BEFORE_WEBSOCKET_CONFIRMATION = "REJECT_GUI_ASSUMED_SUCCESS_BEFORE_WEBSOCKET_CONFIRMATION"

GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION = "GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION"
GUI_COMMAND_MUTATION_RECEIPT_EMITTED = "GUI_COMMAND_MUTATION_RECEIPT_EMITTED"
GUI_COMMAND_MUTATION_PROJECTED_TO_WEBSOCKET = "GUI_COMMAND_MUTATION_PROJECTED_TO_WEBSOCKET"

AUTHORIZED_MUTATION_OPERATIONS: Dict[str, Dict[str, Any]] = {
    "runtime.tick": {
        "target_surface": "api_route:POST /api/runtime/live/tick",
        "contract_schema": "HHS_LIVE_RUNTIME_TICK_MUTATION_V1",
        "mutation_kind": "KERNEL_TICK_STATE_TRANSITION",
        "reversible": True,
        "mutates_runtime": True,
    },
    "runtime.pause": {
        "target_surface": "service:live_fastapi_workflow.pause",
        "contract_schema": "HHS_LIVE_RUNTIME_PAUSE_MUTATION_V1",
        "mutation_kind": "WORKFLOW_CONTROL_STATE_TRANSITION",
        "reversible": True,
        "mutates_runtime": True,
    },
    "runtime.resume": {
        "target_surface": "service:live_fastapi_workflow.resume",
        "contract_schema": "HHS_LIVE_RUNTIME_RESUME_MUTATION_V1",
        "mutation_kind": "WORKFLOW_CONTROL_STATE_TRANSITION",
        "reversible": True,
        "mutates_runtime": True,
    },
    "runtime.request_status_snapshot": {
        "target_surface": "api_route:GET /api/runtime/live/status",
        "contract_schema": "HHS_LIVE_RUNTIME_STATUS_SNAPSHOT_MUTATION_V1",
        "mutation_kind": "WITNESSED_STATUS_SNAPSHOT",
        "reversible": True,
        "mutates_runtime": False,
    },
    "semantic_cache.refresh_composition_index": {
        "target_surface": "service:semantic_composition_cache.self_test",
        "contract_schema": "HHS_SEMANTIC_CACHE_REFRESH_COMPOSITION_INDEX_MUTATION_V1",
        "mutation_kind": "SEMANTIC_COMPOSITION_INDEX_REFRESH",
        "reversible": True,
        "mutates_runtime": False,
    },
    "expanded_state_decay.sweep": {
        "target_surface": "service:expanded_state_decay_lifecycle.self_test",
        "contract_schema": "HHS_EXPANDED_STATE_DECAY_SWEEP_MUTATION_V1",
        "mutation_kind": "EXPANDED_STATE_DECAY_SWEEP",
        "reversible": True,
        "mutates_runtime": False,
    },
}


def hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


@dataclass(frozen=True)
class LiveAuthorizedMutationCommand:
    schema: str = COMMAND_SCHEMA
    version: str = VERSION
    command_id: str = field(default_factory=lambda: f"gui-command:{uuid.uuid4().hex}")
    mutation_id: str = field(default_factory=lambda: f"mutation:{uuid.uuid4().hex}")
    surface_id: str = "gui:runtime.mutation_panel"
    requested_operation: str = "runtime.tick"
    target_surface: str = "api_route:POST /api/runtime/live/tick"
    contract_schema: str = "HHS_LIVE_RUNTIME_TICK_MUTATION_V1"
    client_sequence_id: int = 1
    payload: Dict[str, Any] = field(default_factory=dict)
    requires_admissibility: bool = True
    execution_mode: str = AUTHORIZED_MUTATION
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_authorized_mutation_command(command: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    data = dict(command or {})
    operation = str(data.get("requested_operation") or data.get("operation") or "runtime.tick")
    defaults = dict(AUTHORIZED_MUTATION_OPERATIONS.get(operation, {}))
    envelope = LiveAuthorizedMutationCommand(
        command_id=str(data.get("command_id") or f"gui-command:{uuid.uuid4().hex}"),
        mutation_id=str(data.get("mutation_id") or f"mutation:{uuid.uuid4().hex}"),
        surface_id=str(data.get("surface_id") or "gui:runtime.mutation_panel"),
        requested_operation=operation,
        target_surface=str(defaults.get("target_surface") or data.get("target_surface") or "unknown"),
        contract_schema=str(defaults.get("contract_schema") or data.get("contract_schema") or ""),
        client_sequence_id=int(data.get("client_sequence_id") or 1),
        payload=dict(data.get("payload") or {}),
        requires_admissibility=bool(data.get("requires_admissibility", True)),
        execution_mode=AUTHORIZED_MUTATION,
    ).to_dict()
    envelope["operation_policy"] = defaults
    envelope["command_root_hash72"] = hash72(COMMAND_SCHEMA, envelope)
    return envelope


def validate_authorized_mutation_command(command: Mapping[str, Any]) -> Dict[str, Any]:
    data = normalize_authorized_mutation_command(command)
    reasons: list[str] = []
    operation = str(data.get("requested_operation") or "")
    if operation.startswith("direct."):
        reasons.append(REJECT_UI_EVENT_AS_RUNTIME_TRUTH)
    if data.get("payload", {}).get("mutate_runtime_truth_directly") or data.get("payload", {}).get("assume_success_locally"):
        reasons.append(REJECT_UI_EVENT_AS_RUNTIME_TRUTH)
    if operation not in AUTHORIZED_MUTATION_OPERATIONS:
        reasons.append(REJECT_MUTATION_NOT_ALLOWLISTED)
    if not data.get("requires_admissibility"):
        reasons.append(REJECT_MUTATION_WITHOUT_KERNEL_DERIVATION)
    if not data.get("contract_schema"):
        reasons.append(REJECT_MUTATION_WITHOUT_KERNEL_DERIVATION)
    if not data.get("target_surface") or data.get("target_surface") == "unknown":
        reasons.append(REJECT_MUTATION_WITHOUT_KERNEL_DERIVATION)
    ok = not reasons
    return {
        "schema": "HHS_LIVE_AUTHORIZED_MUTATION_VALIDATION_V1",
        "version": VERSION,
        "authority": AUTHORITY,
        "ok": ok,
        "status": GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION if ok else "REJECT_LIVE_AUTHORIZED_MUTATION_COMMAND",
        "reasons": sorted(dict.fromkeys(reasons)),
        "command": data,
        "command_root_hash72": data.get("command_root_hash72"),
    }


def build_authorized_mutation_contract(command: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = normalize_authorized_mutation_command(command)
    operation = str(normalized.get("requested_operation"))
    policy = AUTHORIZED_MUTATION_OPERATIONS.get(operation, {})
    contract = {
        "schema": CONTRACT_SCHEMA,
        "version": VERSION,
        "authority": AUTHORITY,
        "command_id": normalized.get("command_id"),
        "mutation_id": normalized.get("mutation_id"),
        "surface_id": normalized.get("surface_id"),
        "requested_operation": operation,
        "target_surface": normalized.get("target_surface"),
        "contract_schema": normalized.get("contract_schema"),
        "execution_mode": AUTHORIZED_MUTATION,
        "operation_policy": policy,
        "required_path": [
            "gui_command_envelope",
            "fastapi_command_endpoint",
            "zero_bypass_interposer",
            "kernel_runtime_autocomposer_or_cache",
            "runtime_constraint_enforcement",
            "pre_state_witness",
            "authorized_mutation_executor",
            "post_state_witness",
            "reversal_witness",
            "mutation_receipt_chain",
            "kernel_event_bridge",
            "websocket_feedback",
            "gui_projection_update",
        ],
        "hard_invariant": "NO_UI_EVENT_DIRECTLY_BECOMES_RUNTIME_TRUTH",
    }
    contract["contract_root_hash72"] = hash72(CONTRACT_SCHEMA, contract)
    return contract


def live_authorized_mutation_contract_self_test() -> Dict[str, Any]:
    admitted = validate_authorized_mutation_command({"requested_operation": "runtime.tick", "client_sequence_id": 1})
    rejected = validate_authorized_mutation_command({
        "requested_operation": "direct.mutate_runtime_truth",
        "payload": {"mutate_runtime_truth_directly": True},
        "client_sequence_id": 2,
    })
    contract = build_authorized_mutation_contract(admitted["command"])
    return {
        "schema": "HHS_LIVE_AUTHORIZED_MUTATION_CONTRACT_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(admitted.get("ok") and not rejected.get("ok") and contract.get("contract_root_hash72")),
        "admitted": admitted,
        "direct_mutation_rejection": rejected,
        "contract": contract,
        "allowlist": sorted(AUTHORIZED_MUTATION_OPERATIONS.keys()),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(live_authorized_mutation_contract_self_test(), indent=2, sort_keys=True, default=str))
