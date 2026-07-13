"""
HHS Live GUI Command Authority Loop v1
======================================

Pass 047 closes the live runtime loop without granting browser authority.  GUI
commands are accepted only as requests; the FastAPI command authority validates
shape, interposes zero-bypass, checks kernel-derived composition, performs
runtime constraint enforcement, emits receipt/kernal tick feedback, and stores a
bounded command result.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from hhs_backend.runtime.live_gui_command_contract_v1 import (
    AUTHORITY,
    GUI_COMMAND_ACCEPTED_FOR_PREFLIGHT,
    GUI_COMMAND_ADMITTED_RECEIPT_ONLY,
    GUI_COMMAND_ADMITTED_AUTHORIZED_EXECUTION,
    GUI_COMMAND_REPLAYED_TO_WEBSOCKET_FEEDBACK,
    GUI_COMMAND_VISIBLE_IN_RUNTIME_PROJECTION,
    REJECT_GUI_COMMAND_NOT_KERNEL_DERIVED,
    REJECT_GUI_COMMAND_WITHOUT_RECEIPT,
    REJECT_GUI_DIRECT_MUTATION,
    VERSION,
    build_gui_command_contract,
    normalize_gui_command,
    validate_gui_command_envelope,
)
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_composed_preflight
from hhs_runtime.hhs_runtime_constraint_enforcement_binding_v1 import enforce_runtime_constraint_boundary
from hhs_runtime.hhs_zero_bypass_runtime_interposer_v1 import guarded_surface_propagation, interpose_runtime_surface
from hhs_backend.runtime.live_authorized_mutation_executor_v1 import LiveAuthorizedMutationExecutor
from hhs_backend.runtime.live_authorized_mutation_contract_v1 import (
    AUTHORIZED_MUTATION,
    GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION,
    REJECT_MUTATION_WITHOUT_RECEIPT,
)

COMMAND_HISTORY_LIMIT = 256


def _hash72(label: str, payload: Mapping[str, Any]) -> str:
    return make_hash72_kernel_witness(label, dict(payload), width=72).digest


@dataclass
class LiveGUICommandAuthorityLoop:
    live_workflow: Optional[Any] = None
    mutation_executor: Optional[LiveAuthorizedMutationExecutor] = None
    history: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    ordered_command_ids: list[str] = field(default_factory=list)
    last_client_sequence_id: Optional[int] = None

    def __post_init__(self):
        if self.mutation_executor is None:
            self.mutation_executor = LiveAuthorizedMutationExecutor(live_workflow=self.live_workflow)

    def _remember(self, record: Dict[str, Any]) -> Dict[str, Any]:
        command_id = str(record.get("command_id") or record.get("command", {}).get("command_id") or "unknown")
        self.history[command_id] = record
        if command_id not in self.ordered_command_ids:
            self.ordered_command_ids.append(command_id)
        while len(self.ordered_command_ids) > COMMAND_HISTORY_LIMIT:
            old = self.ordered_command_ids.pop(0)
            self.history.pop(old, None)
        return record

    async def submit(self, command: Mapping[str, Any]) -> Dict[str, Any]:
        normalized = normalize_gui_command(command)
        validation = validate_gui_command_envelope(normalized, previous_sequence_id=self.last_client_sequence_id)
        contract = build_gui_command_contract(normalized)
        base: Dict[str, Any] = {
            "schema": "HHS_LIVE_GUI_COMMAND_AUTHORITY_DECISION_V1",
            "version": VERSION,
            "authority": AUTHORITY,
            "command_id": normalized.get("command_id"),
            "command": normalized,
            "contract": contract,
            "validation": validation,
            "statuses": [GUI_COMMAND_ACCEPTED_FOR_PREFLIGHT] if validation.get("ok") else [],
            "browser_role": "REQUEST_ONLY_NO_DIRECT_MUTATION",
            "gui_mutated_runtime_truth": False,
        }
        if not validation.get("ok"):
            base.update({
                "ok": False,
                "status": "REJECT_GUI_COMMAND_ENVELOPE",
                "reasons": validation.get("reasons", []),
                "receipt_only_no_handler_invocation": True,
                "command_decision_hash72": _hash72("HHS_LIVE_GUI_COMMAND_REJECTION_V1", base),
            })
            await self._emit_feedback(base)
            return self._remember(base)

        self.last_client_sequence_id = int(normalized.get("client_sequence_id") or 0)

        # Zero-bypass interposition over the requested target surface.
        interposition = interpose_runtime_surface(
            surface=str(normalized.get("target_surface")),
            request_class="canonical_full_witness_chain",
            payload={
                "schema": "HHS_GUI_COMMAND_ZERO_BYPASS_INTERPOSITION_PAYLOAD_V1",
                "command": normalized,
                "contract": contract,
            },
            brute_force_claim=False,
        )
        base["interposition"] = interposition
        if not interposition.get("propagation_allowed"):
            base.update({
                "ok": False,
                "status": "REJECT_GUI_COMMAND_BYPASSES_ZERO_BYPASS_INTERPOSER",
                "reasons": ["zero-bypass interposition rejected command"],
                "receipt_only_no_handler_invocation": True,
            })
            base["command_decision_hash72"] = _hash72("HHS_LIVE_GUI_COMMAND_INTERPOSITION_REJECTION_V1", base)
            await self._emit_feedback(base)
            return self._remember(base)

        guarded = guarded_surface_propagation(
            surface=str(normalized.get("target_surface")),
            attempted_operation=str(normalized.get("requested_operation")),
            payload={"command": normalized, "contract": contract},
            interposition_token=interposition.get("interposition_token"),
        )
        base["guarded_propagation"] = guarded
        if not guarded.get("propagation_allowed"):
            base.update({
                "ok": False,
                "status": "REJECT_GUI_COMMAND_NOT_KERNEL_DERIVED",
                "reasons": [REJECT_GUI_COMMAND_NOT_KERNEL_DERIVED],
                "receipt_only_no_handler_invocation": True,
            })
            base["command_decision_hash72"] = _hash72("HHS_LIVE_GUI_COMMAND_GUARD_REJECTION_V1", base)
            await self._emit_feedback(base)
            return self._remember(base)

        # Kernel-derived composition/cache preflight.  GUI commands target API-like
        # surfaces that may be projected through bounded legacy conformance paths;
        # an unavailable explicit surface is rejected before command execution.
        composition = execute_composed_preflight(
            str(normalized.get("target_surface")),
            operation=str(normalized.get("requested_operation")),
        )
        base["composition"] = composition
        if not composition.get("ok"):
            base.update({
                "ok": False,
                "status": REJECT_GUI_COMMAND_NOT_KERNEL_DERIVED,
                "reasons": [REJECT_GUI_COMMAND_NOT_KERNEL_DERIVED],
                "receipt_only_no_handler_invocation": True,
            })
            base["command_decision_hash72"] = _hash72("HHS_LIVE_GUI_COMMAND_COMPOSITION_REJECTION_V1", base)
            await self._emit_feedback(base)
            return self._remember(base)

        enforcement = enforce_runtime_constraint_boundary(
            surface=str(normalized.get("target_surface")),
            request_class="canonical_full_witness_chain",
            candidate={"command": normalized, "contract": contract, "composition": composition},
            brute_force_claim=False,
        )
        base["enforcement"] = enforcement
        if not enforcement.get("propagation_allowed"):
            base.update({
                "ok": False,
                "status": "REJECT_GUI_COMMAND_NOT_ADMISSIBLE",
                "reasons": [str(enforcement.get("reason_code") or enforcement.get("status"))],
                "receipt_only_no_handler_invocation": True,
            })
            base["command_decision_hash72"] = _hash72("HHS_LIVE_GUI_COMMAND_ENFORCEMENT_REJECTION_V1", base)
            await self._emit_feedback(base)
            return self._remember(base)

        execution_mode = str(normalized.get("execution_mode") or "RECEIPT_ONLY")
        if execution_mode == AUTHORIZED_MUTATION:
            mutation = await self.mutation_executor.execute(
                normalized,
                authority_context={
                    "contract": contract,
                    "interposition": interposition,
                    "guarded_propagation": guarded,
                    "composition": composition,
                    "enforcement": enforcement,
                },
            )
            base["execution_mode"] = execution_mode
            base["authorized_mutation"] = mutation
            base["mutation_receipt"] = mutation.get("mutation_receipt")
            base["receipt_hash72"] = mutation.get("receipt_hash72")
            base["websocket_feedback"] = mutation.get("websocket_feedback")
            base["pre_state_hash72"] = mutation.get("pre_state_hash72")
            base["transformation_hash72"] = mutation.get("transformation_hash72")
            base["post_state_hash72"] = mutation.get("post_state_hash72")
            base["receipt_only_no_handler_invocation"] = False
            if mutation.get("ok") and mutation.get("receipt_hash72"):
                base["ok"] = True
                base["status"] = GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION
                base["statuses"].extend([
                    GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION,
                    GUI_COMMAND_REPLAYED_TO_WEBSOCKET_FEEDBACK,
                    GUI_COMMAND_VISIBLE_IN_RUNTIME_PROJECTION,
                ])
            else:
                base["ok"] = False
                base["status"] = REJECT_MUTATION_WITHOUT_RECEIPT
                base.setdefault("reasons", []).extend(mutation.get("reasons", [REJECT_MUTATION_WITHOUT_RECEIPT]))
            base["command_decision_hash72"] = _hash72("HHS_LIVE_GUI_COMMAND_AUTHORIZED_MUTATION_FINAL_DECISION_V1", base)
            return self._remember(base)

        admitted_status = GUI_COMMAND_ADMITTED_AUTHORIZED_EXECUTION if execution_mode == "AUTHORIZED_EXECUTION" else GUI_COMMAND_ADMITTED_RECEIPT_ONLY
        base["statuses"].extend([admitted_status])
        base["status"] = admitted_status
        base["ok"] = True
        base["execution_mode"] = execution_mode
        base["receipt_only_no_handler_invocation"] = execution_mode != "AUTHORIZED_EXECUTION"
        base["command_decision_hash72"] = _hash72("HHS_LIVE_GUI_COMMAND_AUTHORITY_DECISION_V1", base)
        feedback = await self._emit_feedback(base)
        base["websocket_feedback"] = feedback
        if feedback.get("ok"):
            base["statuses"].extend([GUI_COMMAND_REPLAYED_TO_WEBSOCKET_FEEDBACK, GUI_COMMAND_VISIBLE_IN_RUNTIME_PROJECTION])
        if not feedback.get("receipt_hash72"):
            base["ok"] = False
            base["status"] = REJECT_GUI_COMMAND_WITHOUT_RECEIPT
            base.setdefault("reasons", []).append(REJECT_GUI_COMMAND_WITHOUT_RECEIPT)
        base["command_decision_hash72"] = _hash72("HHS_LIVE_GUI_COMMAND_AUTHORITY_FINAL_DECISION_V1", base)
        return self._remember(base)

    async def _emit_feedback(self, decision: Mapping[str, Any]) -> Dict[str, Any]:
        instruction = {
            "source": "live_gui_command_authority_loop",
            "schema": "HHS_LIVE_GUI_COMMAND_WEBSOCKET_FEEDBACK_INSTRUCTION_V1",
            "command_id": decision.get("command_id"),
            "status": decision.get("status"),
            "ok": bool(decision.get("ok")),
            "command_decision_hash72": decision.get("command_decision_hash72") or _hash72("HHS_LIVE_GUI_COMMAND_FEEDBACK_V1", decision),
            "requested_operation": (decision.get("command") or {}).get("requested_operation"),
            "target_surface": (decision.get("command") or {}).get("target_surface"),
        }
        if self.live_workflow is None:
            return {
                "schema": "HHS_LIVE_GUI_COMMAND_WEBSOCKET_FEEDBACK_RECORD_V1",
                "ok": True,
                "feedback_mode": "SELF_TEST_NO_LIVE_WORKFLOW",
                "instruction": instruction,
                "receipt_hash72": _hash72("HHS_LIVE_GUI_COMMAND_SELF_TEST_FEEDBACK_RECEIPT_V1", instruction),
            }
        emission = await self.live_workflow.tick_once(instruction)
        return {
            "schema": "HHS_LIVE_GUI_COMMAND_WEBSOCKET_FEEDBACK_RECORD_V1",
            "ok": bool(emission.get("ok")),
            "feedback_mode": "LIVE_FASTAPI_KERNEL_TICK",
            "instruction": instruction,
            "emission": emission,
            "receipt_hash72": emission.get("receipt_hash72"),
            "event_hash72": emission.get("event_hash72"),
            "kernel_tick": emission.get("kernel_tick"),
        }

    def status(self, command_id: str) -> Dict[str, Any]:
        record = self.history.get(str(command_id))
        return record or {
            "schema": "HHS_LIVE_GUI_COMMAND_STATUS_RESPONSE_V1",
            "version": VERSION,
            "ok": False,
            "status": "COMMAND_NOT_FOUND",
            "command_id": command_id,
        }

    def history_summary(self) -> Dict[str, Any]:
        records = [self.history[cid] for cid in self.ordered_command_ids if cid in self.history]
        return {
            "schema": "HHS_LIVE_GUI_COMMAND_HISTORY_RESPONSE_V1",
            "version": VERSION,
            "authority": AUTHORITY,
            "command_count": len(records),
            "commands": records[-COMMAND_HISTORY_LIMIT:],
            "bounded_history": True,
            "expanded_metadata_persisted": False,
        }


def run_live_gui_command_authority_self_test() -> Dict[str, Any]:
    async def _run() -> Dict[str, Any]:
        loop = LiveGUICommandAuthorityLoop(live_workflow=None)
        admitted = await loop.submit({"requested_operation": "runtime.tick", "client_sequence_id": 1})
        mutation = await loop.submit({"requested_operation": "runtime.request_status_snapshot", "execution_mode": "AUTHORIZED_MUTATION", "client_sequence_id": 2})
        direct = await loop.submit({
            "requested_operation": "direct.mutate_runtime_truth",
            "contract_schema": "HHS_FORBIDDEN_GUI_DIRECT_MUTATION_V1",
            "target_surface": "browser.local_runtime_state",
            "client_sequence_id": 3,
            "payload": {"mutate_runtime_truth_directly": True},
        })
        status = loop.status(str(admitted.get("command_id")))
        history = loop.history_summary()
        admitted_summary = {
            "command_id": admitted.get("command_id"),
            "ok": admitted.get("ok"),
            "status": admitted.get("status"),
            "statuses": admitted.get("statuses", []),
            "command_decision_hash72": admitted.get("command_decision_hash72"),
            "websocket_feedback_ok": admitted.get("websocket_feedback", {}).get("ok"),
            "websocket_feedback_receipt_hash72": admitted.get("websocket_feedback", {}).get("receipt_hash72"),
            "gui_mutated_runtime_truth": admitted.get("gui_mutated_runtime_truth"),
            "receipt_only_no_handler_invocation": admitted.get("receipt_only_no_handler_invocation"),
        }
        direct_summary = {
            "command_id": direct.get("command_id"),
            "ok": direct.get("ok"),
            "status": direct.get("status"),
            "reasons": direct.get("reasons", []),
            "command_decision_hash72": direct.get("command_decision_hash72"),
        }
        return {
            "schema": "HHS_LIVE_GUI_COMMAND_AUTHORITY_LOOP_SELF_TEST_V1",
            "version": VERSION,
            "ok": bool(admitted.get("ok") and mutation.get("ok") and not direct.get("ok") and status.get("command_id") == admitted.get("command_id") and history.get("command_count") == 3),
            "admitted": admitted_summary,
            "authorized_mutation": {
                "command_id": mutation.get("command_id"),
                "ok": mutation.get("ok"),
                "status": mutation.get("status"),
                "receipt_hash72": mutation.get("receipt_hash72"),
                "pre_state_hash72": mutation.get("pre_state_hash72"),
                "post_state_hash72": mutation.get("post_state_hash72"),
                "gui_mutated_runtime_truth": mutation.get("gui_mutated_runtime_truth"),
                "execution_mode": mutation.get("execution_mode"),
            },
            "direct_mutation_rejection": direct_summary,
            "history": {
                "command_count": history.get("command_count"),
                "bounded_history": history.get("bounded_history"),
                "expanded_metadata_persisted": history.get("expanded_metadata_persisted"),
            },
            "projection_rule": "GUI_REQUESTS_KERNEL_DECIDES_FASTAPI_ENFORCES_WEBSOCKETS_REPORT_GUI_PROJECTS",
        }
    return asyncio.run(_run())


if __name__ == "__main__":
    import json
    print(json.dumps(run_live_gui_command_authority_self_test(), indent=2, sort_keys=True, default=str))
