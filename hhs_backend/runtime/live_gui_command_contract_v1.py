"""
HHS Live GUI Command Contract v1
================================

Pass 047 defines the command envelope used by the browser GUI to request live
runtime actions.  The browser remains a projection/request layer only: every
command must carry a contract, target surface, client sequence, and must be
submitted to the FastAPI authority loop before any runtime effect is possible.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional
import time
import uuid

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_047_LIVE_GUI_COMMAND_AUTHORITY_LOOP_V1"
COMMAND_SCHEMA = "HHS_LIVE_GUI_COMMAND_ENVELOPE_V1"
CONTRACT_SCHEMA = "HHS_LIVE_GUI_COMMAND_CONTRACT_V1"
AUTHORITY = "HHS_FASTAPI_GUI_COMMAND_AUTHORITY_V1"

REJECT_GUI_DIRECT_MUTATION = "REJECT_GUI_DIRECT_MUTATION"
REJECT_GUI_COMMAND_WITHOUT_CONTRACT = "REJECT_GUI_COMMAND_WITHOUT_CONTRACT"
REJECT_GUI_COMMAND_WITHOUT_SURFACE_DERIVATION = "REJECT_GUI_COMMAND_WITHOUT_SURFACE_DERIVATION"
REJECT_GUI_COMMAND_BYPASSES_ZERO_BYPASS_INTERPOSER = "REJECT_GUI_COMMAND_BYPASSES_ZERO_BYPASS_INTERPOSER"
REJECT_GUI_COMMAND_NOT_KERNEL_DERIVED = "REJECT_GUI_COMMAND_NOT_KERNEL_DERIVED"
REJECT_GUI_COMMAND_WITHOUT_RECEIPT = "REJECT_GUI_COMMAND_WITHOUT_RECEIPT"
REJECT_GUI_COMMAND_SEQUENCE_DRIFT = "REJECT_GUI_COMMAND_SEQUENCE_DRIFT"

GUI_COMMAND_ACCEPTED_FOR_PREFLIGHT = "GUI_COMMAND_ACCEPTED_FOR_PREFLIGHT"
GUI_COMMAND_ADMITTED_RECEIPT_ONLY = "GUI_COMMAND_ADMITTED_RECEIPT_ONLY"
GUI_COMMAND_ADMITTED_AUTHORIZED_EXECUTION = "GUI_COMMAND_ADMITTED_AUTHORIZED_EXECUTION"
GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION = "GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION"
GUI_COMMAND_REPLAYED_TO_WEBSOCKET_FEEDBACK = "GUI_COMMAND_REPLAYED_TO_WEBSOCKET_FEEDBACK"
GUI_COMMAND_VISIBLE_IN_RUNTIME_PROJECTION = "GUI_COMMAND_VISIBLE_IN_RUNTIME_PROJECTION"

ALLOWED_COMMAND_OPERATIONS = {
    "runtime.tick": {
        "target_surface": "api_route:POST /api/runtime/live/tick",
        "contract_schema": "HHS_LIVE_RUNTIME_TICK_COMMAND_V1",
        "execution_mode": "RECEIPT_ONLY",
    },
    "runtime.status": {
        "target_surface": "api_route:GET /api/runtime/live/status",
        "contract_schema": "HHS_LIVE_RUNTIME_STATUS_COMMAND_V1",
        "execution_mode": "RECEIPT_ONLY",
    },
    "runtime.refresh_projection": {
        "target_surface": "api_route:GET /api/runtime/gui/projection/status",
        "contract_schema": "HHS_LIVE_GUI_PROJECTION_REFRESH_COMMAND_V1",
        "execution_mode": "RECEIPT_ONLY",
    },
    "runtime.pause": {
        "target_surface": "service:live_fastapi_workflow.pause",
        "contract_schema": "HHS_LIVE_RUNTIME_PAUSE_MUTATION_V1",
        "execution_mode": "AUTHORIZED_MUTATION",
    },
    "runtime.resume": {
        "target_surface": "service:live_fastapi_workflow.resume",
        "contract_schema": "HHS_LIVE_RUNTIME_RESUME_MUTATION_V1",
        "execution_mode": "AUTHORIZED_MUTATION",
    },
    "runtime.request_status_snapshot": {
        "target_surface": "api_route:GET /api/runtime/live/status",
        "contract_schema": "HHS_LIVE_RUNTIME_STATUS_SNAPSHOT_MUTATION_V1",
        "execution_mode": "AUTHORIZED_MUTATION",
    },
    "semantic_cache.refresh_composition_index": {
        "target_surface": "service:semantic_composition_cache.self_test",
        "contract_schema": "HHS_SEMANTIC_CACHE_REFRESH_COMPOSITION_INDEX_MUTATION_V1",
        "execution_mode": "AUTHORIZED_MUTATION",
    },
    "expanded_state_decay.sweep": {
        "target_surface": "service:expanded_state_decay_lifecycle.self_test",
        "contract_schema": "HHS_EXPANDED_STATE_DECAY_SWEEP_MUTATION_V1",
        "execution_mode": "AUTHORIZED_MUTATION",
    },
}


@dataclass(frozen=True)
class LiveGUICommandEnvelope:
    schema: str = COMMAND_SCHEMA
    version: str = VERSION
    command_id: str = field(default_factory=lambda: f"gui-command:{uuid.uuid4().hex}")
    surface_id: str = "gui:runtime.command_panel"
    requested_operation: str = "runtime.tick"
    target_surface: str = "api_route:POST /api/runtime/live/tick"
    contract_schema: str = "HHS_LIVE_RUNTIME_TICK_COMMAND_V1"
    client_sequence_id: int = 1
    payload: Dict[str, Any] = field(default_factory=dict)
    requires_admissibility: bool = True
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _hash72(label: str, payload: Mapping[str, Any]) -> str:
    return make_hash72_kernel_witness(label, dict(payload), width=72).digest


def normalize_gui_command(command: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Normalize a partial GUI command into the canonical Pass 047 envelope."""

    data = dict(command or {})
    operation = str(data.get("requested_operation") or data.get("operation") or "runtime.tick")
    defaults = dict(ALLOWED_COMMAND_OPERATIONS.get(operation, {}))
    envelope = LiveGUICommandEnvelope(
        command_id=str(data.get("command_id") or f"gui-command:{uuid.uuid4().hex}"),
        surface_id=str(data.get("surface_id") or "gui:runtime.command_panel"),
        requested_operation=operation,
        target_surface=str(data.get("target_surface") or defaults.get("target_surface") or "unknown"),
        contract_schema=str(data.get("contract_schema") or defaults.get("contract_schema") or ""),
        client_sequence_id=int(data.get("client_sequence_id") or 1),
        payload=dict(data.get("payload") or {}),
        requires_admissibility=bool(data.get("requires_admissibility", True)),
    ).to_dict()
    envelope["execution_mode"] = str(data.get("execution_mode") or defaults.get("execution_mode") or "RECEIPT_ONLY")
    envelope["command_root_hash72"] = _hash72(COMMAND_SCHEMA, envelope)
    return envelope


def validate_gui_command_envelope(command: Mapping[str, Any], *, previous_sequence_id: Optional[int] = None) -> Dict[str, Any]:
    """Validate GUI command shape before interposition/enforcement."""

    data = normalize_gui_command(command)
    reasons: list[str] = []
    if data.get("schema") != COMMAND_SCHEMA:
        reasons.append("REJECT_GUI_COMMAND_SCHEMA_MISMATCH")
    if not data.get("contract_schema"):
        reasons.append(REJECT_GUI_COMMAND_WITHOUT_CONTRACT)
    if not data.get("target_surface") or data.get("target_surface") == "unknown":
        reasons.append(REJECT_GUI_COMMAND_WITHOUT_SURFACE_DERIVATION)
    if str(data.get("requested_operation", "")).startswith("direct."):
        reasons.append(REJECT_GUI_DIRECT_MUTATION)
    if data.get("payload", {}).get("mutate_runtime_truth_directly"):
        reasons.append(REJECT_GUI_DIRECT_MUTATION)
    if previous_sequence_id is not None and int(data.get("client_sequence_id") or 0) <= int(previous_sequence_id):
        reasons.append(REJECT_GUI_COMMAND_SEQUENCE_DRIFT)
    if not data.get("requires_admissibility"):
        reasons.append(REJECT_GUI_COMMAND_BYPASSES_ZERO_BYPASS_INTERPOSER)
    ok = not reasons
    return {
        "schema": "HHS_LIVE_GUI_COMMAND_VALIDATION_DECISION_V1",
        "version": VERSION,
        "ok": ok,
        "status": GUI_COMMAND_ACCEPTED_FOR_PREFLIGHT if ok else "REJECT_GUI_COMMAND_ENVELOPE",
        "reasons": reasons,
        "command": data,
        "command_root_hash72": data.get("command_root_hash72"),
        "authority": AUTHORITY,
    }


def build_gui_command_contract(command: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = normalize_gui_command(command)
    contract = {
        "schema": CONTRACT_SCHEMA,
        "version": VERSION,
        "authority": AUTHORITY,
        "command_id": normalized.get("command_id"),
        "surface_id": normalized.get("surface_id"),
        "requested_operation": normalized.get("requested_operation"),
        "target_surface": normalized.get("target_surface"),
        "contract_schema": normalized.get("contract_schema"),
        "execution_mode": normalized.get("execution_mode"),
        "required_path": [
            "gui_command_envelope",
            "fastapi_command_endpoint",
            "zero_bypass_interposer",
            "kernel_runtime_autocomposer_or_cache",
            "runtime_constraint_enforcement",
            "receipt_chain",
            "kernel_event_bridge",
            "websocket_feedback",
            "gui_projection_update",
        ],
        "browser_authority": "REQUEST_ONLY_NO_DIRECT_MUTATION",
    }
    contract["contract_root_hash72"] = _hash72(CONTRACT_SCHEMA, contract)
    return contract


def live_gui_command_contract_self_test() -> Dict[str, Any]:
    command = normalize_gui_command({"requested_operation": "runtime.tick", "client_sequence_id": 7})
    validation = validate_gui_command_envelope(command)
    direct = validate_gui_command_envelope({
        "requested_operation": "direct.mutate_runtime_truth",
        "contract_schema": "HHS_FORBIDDEN_DIRECT_MUTATION_V1",
        "target_surface": "browser.local_state",
        "payload": {"mutate_runtime_truth_directly": True},
    })
    contract = build_gui_command_contract(command)
    return {
        "schema": "HHS_LIVE_GUI_COMMAND_CONTRACT_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(validation.get("ok") and not direct.get("ok") and contract.get("contract_root_hash72")),
        "command": command,
        "validation": validation,
        "direct_mutation_rejection": direct,
        "contract": contract,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(live_gui_command_contract_self_test(), indent=2, sort_keys=True, default=str))
