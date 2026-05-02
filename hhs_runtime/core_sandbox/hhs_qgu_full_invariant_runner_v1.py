from __future__ import annotations

from typing import Any, Dict, Optional

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import AuditedRunner, HHSState, canonicalize_for_hash72
from hhs_runtime.core_sandbox.hhs_qgu_invariant_gate_v1 import (
    QGU_INVARIANT_NAME,
    QGU_OPERATION_NAME,
    QGUInvariantKernelGateAdapter,
    audit_qgu_closure,
)
from hhs_runtime.core_sandbox.hhs_qgu_metric_harmonic_operator_v1 import qgu_metric_harmonic_operator


class QGUInvariantMissingError(RuntimeError):
    pass


def attach_qgu_invariant_to_state(state: HHSState, qgu_result: Dict[str, Any]) -> HHSState:
    audit = audit_qgu_closure(qgu_result, phase=state.phase)
    if not audit.get("locked"):
        raise QGUInvariantMissingError(audit.get("reason", "QGU invariant did not lock"))
    state.tensors[QGU_INVARIANT_NAME] = {
        "required": True,
        "audit": canonicalize_for_hash72(audit),
        "result": canonicalize_for_hash72(qgu_result),
    }
    state.metadata["requires_qgu_invariant"] = True
    state.metadata["qgu_projection_status"] = audit.get("projection_status")
    state.metadata["qgu_balance"] = audit.get("balance")
    state.metadata["qgu_ds2"] = audit.get("ds2")
    return state


def state_has_locked_qgu_invariant(state: HHSState) -> bool:
    qgu = state.tensors.get(QGU_INVARIANT_NAME)
    if not isinstance(qgu, dict):
        return False
    audit = qgu.get("audit", {})
    return audit.get("status") == "LOCKED" and audit.get("locked") is True


class QGUFullInvariantRunner(AuditedRunner):
    """Audited runner with QGU promoted from operation to required invariant."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.gate = QGUInvariantKernelGateAdapter(self.kernel)
        self.state = HHSState()
        self.registry.register(QGU_OPERATION_NAME, qgu_metric_harmonic_operator)
        self.require_qgu_for_all_operations = True

    def _qgu_required_for(self, operation: str) -> bool:
        return self.require_qgu_for_all_operations and operation != QGU_OPERATION_NAME

    def _quarantine_missing_qgu(self, operation: str, args: tuple[Any, ...], input_payload: Optional[Any]) -> Dict[str, Any]:
        reason = "required QGU invariant missing from Manifold9 tensor state"
        pre_state = {
            "phase": self.commitments.phase,
            "operation": operation,
            "args": canonicalize_for_hash72(args),
            "tip": self.commitments.tip_hash72,
            "qgu_required": True,
        }
        receipt = self.commitments.commit_transition(
            operation=operation,
            input_payload=input_payload if input_payload is not None else {"operation": operation, "args": args},
            pre_state=pre_state,
            post_state={"blocked": True, "reason": reason},
            witness={"invariant": QGU_INVARIANT_NAME, "status": "MISSING", "operation": operation},
            gate_status="QUARANTINED",
            reason=reason,
        )
        return {"ok": False, "quarantine": True, "reason": reason, "receipt": receipt.to_dict(), "result_blocked": True}

    def execute(self, operation: str, *args: Any, input_payload: Optional[Any] = None) -> Dict[str, Any]:
        if self._qgu_required_for(operation) and not state_has_locked_qgu_invariant(self.state):
            return self._quarantine_missing_qgu(operation, args, input_payload)
        result = super().execute(operation, *args, input_payload=input_payload)
        if operation == QGU_OPERATION_NAME and result.get("ok") is True:
            qgu_result = result.get("result", {})
            attach_qgu_invariant_to_state(self.state, qgu_result)
        return result

    def install_qgu_constraint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.execute(QGU_OPERATION_NAME, payload, input_payload={"install_invariant": QGU_INVARIANT_NAME, "payload": payload})

    def state_snapshot(self) -> Dict[str, Any]:
        snap = self.state.snapshot()
        snap["qgu_required_for_all_operations"] = self.require_qgu_for_all_operations
        snap["qgu_locked"] = state_has_locked_qgu_invariant(self.state)
        return canonicalize_for_hash72(snap)


def make_qgu_full_invariant_runner() -> QGUFullInvariantRunner:
    return QGUFullInvariantRunner()
