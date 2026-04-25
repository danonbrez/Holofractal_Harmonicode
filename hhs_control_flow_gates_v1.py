"""
hhs_control_flow_gates_v1.py

Control-flow gates for the HARMONICODE general runtime.

Purpose
-------
Adds audited IF and LOOP execution on top of hhs_general_runtime_layer_v1.py.

Control-flow contract
---------------------
IF gate:
    condition_hash72
    selected_branch_hash72
    rejected_branch_hash72
    branch_result_receipt
    control_receipt

LOOP gate:
    iteration index
    variant/decreasing measure
    stutter guard
    max-step guard
    iteration receipts
    final closure receipt

This layer does not replace the kernel. It uses AuditedRunner and the default
Hash72 receipt chain as the authority path.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import json

from hhs_general_runtime_layer_v1 import (
    AuditedRunner,
    DEFAULT_KERNEL_PATH,
    canonicalize_for_hash72,
)


@dataclass(frozen=True)
class IFGateResult:
    ok: bool
    selected_branch: str
    result: Any
    control_receipt: Dict[str, Any]
    branch_receipt: Optional[Dict[str, Any]]
    witness: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LOOPGateResult:
    ok: bool
    result: Any
    iterations: int
    control_receipt: Dict[str, Any]
    iteration_receipts: List[Dict[str, Any]]
    witness: Dict[str, Any]
    terminated: bool
    quarantine: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSControlFlowGatesV1:
    """
    Audited control-flow host.

    The branch/loop logic can call normal Python functions, but every committed
    transition is wrapped in the AuditedRunner receipt chain.
    """

    def __init__(self, runner: Optional[AuditedRunner] = None, kernel_path: str | Path = DEFAULT_KERNEL_PATH):
        self.runner = runner or AuditedRunner(kernel_path)

    # ------------------------------------------------------------------
    # IF gate
    # ------------------------------------------------------------------

    def audited_if(
        self,
        *,
        condition: bool,
        then_fn: Callable[[], Any],
        else_fn: Callable[[], Any],
        label: str = "IF_GATE",
    ) -> IFGateResult:
        """
        Execute exactly one branch, but hash-commit both branch identities.

        The selected branch result is audited through the runner. The rejected
        branch is not executed, but its identity and rejection are committed.
        """
        condition_payload = {
            "label": label,
            "condition": bool(condition),
        }
        selected_name = "THEN" if condition else "ELSE"
        rejected_name = "ELSE" if condition else "THEN"

        selected_fn = then_fn if condition else else_fn
        rejected_fn = else_fn if condition else then_fn

        selected_branch_descriptor = {
            "label": label,
            "branch": selected_name,
            "callable": getattr(selected_fn, "__name__", repr(selected_fn)),
        }
        rejected_branch_descriptor = {
            "label": label,
            "branch": rejected_name,
            "callable": getattr(rejected_fn, "__name__", repr(rejected_fn)),
            "status": "REJECTED_NOT_EXECUTED",
        }

        try:
            branch_result = selected_fn()
            # Audit scalar-compatible branch outputs directly. If a branch returns
            # a dict with audit_value, the runner honors that.
            branch_exec = self.runner.execute(
                "SUM",
                [branch_result] if isinstance(branch_result, (int, Fraction)) else [0],
                input_payload={
                    "control": "IF_SELECTED_BRANCH_RESULT",
                    "label": label,
                    "selected_branch": selected_name,
                    "result": canonicalize_for_hash72(branch_result),
                },
            )
            branch_locked = bool(branch_exec.get("ok"))
            gate_status = "LOCKED" if branch_locked else "QUARANTINED"
            reason = "" if branch_locked else "selected branch result failed audit"
            branch_receipt = branch_exec.get("receipt")
        except Exception as exc:
            branch_result = None
            branch_locked = False
            gate_status = "QUARANTINED"
            reason = f"selected branch raised {type(exc).__name__}: {exc}"
            branch_receipt = None

        authority = self.runner.authority
        witness = {
            "gate": "IF",
            "label": label,
            "condition": bool(condition),
            "condition_hash72": authority.commit(condition_payload, domain="HHS_IF_CONDITION"),
            "selected_branch": selected_branch_descriptor,
            "selected_branch_hash72": authority.commit(selected_branch_descriptor, domain="HHS_IF_SELECTED_BRANCH"),
            "rejected_branch": rejected_branch_descriptor,
            "rejected_branch_hash72": authority.commit(rejected_branch_descriptor, domain="HHS_IF_REJECTED_BRANCH"),
            "branch_locked": branch_locked,
            "reason": reason,
        }

        receipt = self.runner.commitments.commit_transition(
            operation="IF_GATE",
            input_payload=condition_payload,
            pre_state={
                "tip": self.runner.commitments.tip_hash72,
                "phase": self.runner.commitments.phase,
                "label": label,
            },
            post_state={
                "selected_branch": selected_name,
                "branch_result": canonicalize_for_hash72(branch_result),
                "branch_receipt": branch_receipt,
            },
            witness=witness,
            gate_status=gate_status,
            reason=reason,
        )

        return IFGateResult(
            ok=receipt.locked,
            selected_branch=selected_name,
            result=canonicalize_for_hash72(branch_result),
            control_receipt=receipt.to_dict(),
            branch_receipt=branch_receipt,
            witness=canonicalize_for_hash72(witness),
        )

    # ------------------------------------------------------------------
    # LOOP gate
    # ------------------------------------------------------------------

    def audited_loop(
        self,
        *,
        initial_state: Any,
        condition_fn: Callable[[Any], bool],
        step_fn: Callable[[Any], Any],
        variant_fn: Callable[[Any], Any],
        max_steps: int = 1024,
        label: str = "LOOP_GATE",
        require_strict_decrease: bool = True,
    ) -> LOOPGateResult:
        """
        Execute a loop with variant/stutter surveillance.

        variant_fn must return a rational/integer-like measure. By default,
        each iteration must strictly decrease the variant.
        """
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")

        state = initial_state
        prev_variant = Fraction(variant_fn(state))
        iteration_receipts: List[Dict[str, Any]] = []
        path: List[Dict[str, Any]] = []
        terminated = False
        quarantine = False
        reason = ""

        for i in range(max_steps):
            condition = bool(condition_fn(state))
            current_variant = Fraction(variant_fn(state))

            iteration_witness = {
                "gate": "LOOP",
                "label": label,
                "iteration": i,
                "condition": condition,
                "current_variant": current_variant,
                "previous_variant": prev_variant,
                "state": canonicalize_for_hash72(state),
            }

            if not condition:
                terminated = True
                reason = "condition false; loop terminated"
                path.append({**iteration_witness, "decision": "TERMINATE"})
                break

            if i > 0:
                if require_strict_decrease and not (current_variant < prev_variant):
                    quarantine = True
                    reason = "loop variant failed strict decrease"
                    path.append({**iteration_witness, "decision": "QUARANTINE_STUTTER"})
                    break
                if not require_strict_decrease and current_variant == prev_variant:
                    quarantine = True
                    reason = "loop variant stutter"
                    path.append({**iteration_witness, "decision": "QUARANTINE_STUTTER"})
                    break

            try:
                next_state = step_fn(state)
            except Exception as exc:
                quarantine = True
                reason = f"step function raised {type(exc).__name__}: {exc}"
                path.append({**iteration_witness, "decision": "QUARANTINE_EXCEPTION"})
                break

            next_variant = Fraction(variant_fn(next_state))
            audit_exec = self.runner.execute(
                "SUM",
                [next_variant],
                input_payload={
                    "control": "LOOP_ITERATION_VARIANT",
                    "label": label,
                    "iteration": i,
                    "variant": next_variant,
                },
            )

            iteration_witness.update({
                "decision": "STEP",
                "next_state": canonicalize_for_hash72(next_state),
                "next_variant": next_variant,
                "iteration_receipt": audit_exec.get("receipt"),
                "iteration_locked": bool(audit_exec.get("ok")),
            })

            path.append(iteration_witness)
            iteration_receipts.append(audit_exec.get("receipt"))

            if not audit_exec.get("ok"):
                quarantine = True
                reason = "iteration variant audit failed"
                break

            state = next_state
            prev_variant = current_variant

        else:
            quarantine = True
            reason = f"max_steps exceeded: {max_steps}"

        gate_status = "LOCKED" if terminated and not quarantine else "QUARANTINED"

        authority = self.runner.authority
        witness = {
            "gate": "LOOP",
            "label": label,
            "initial_state_hash72": authority.commit(initial_state, domain="HHS_LOOP_INITIAL_STATE"),
            "final_state_hash72": authority.commit(state, domain="HHS_LOOP_FINAL_STATE"),
            "iterations": len(iteration_receipts),
            "terminated": terminated,
            "quarantine": quarantine,
            "reason": reason,
            "path": path,
        }

        control_receipt = self.runner.commitments.commit_transition(
            operation="LOOP_GATE",
            input_payload={
                "label": label,
                "initial_state": canonicalize_for_hash72(initial_state),
                "max_steps": max_steps,
            },
            pre_state={
                "tip": self.runner.commitments.tip_hash72,
                "phase": self.runner.commitments.phase,
            },
            post_state={
                "final_state": canonicalize_for_hash72(state),
                "terminated": terminated,
                "quarantine": quarantine,
            },
            witness=witness,
            gate_status=gate_status,
            reason=reason,
        )

        return LOOPGateResult(
            ok=control_receipt.locked,
            result=canonicalize_for_hash72(state),
            iterations=len(iteration_receipts),
            control_receipt=control_receipt.to_dict(),
            iteration_receipts=iteration_receipts,
            witness=canonicalize_for_hash72(witness),
            terminated=terminated,
            quarantine=quarantine,
            reason=reason,
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> Dict[str, Any]:
    gates = HHSControlFlowGatesV1()

    if_result = gates.audited_if(
        condition=True,
        then_fn=lambda: 7,
        else_fn=lambda: 3,
        label="DEMO_IF",
    )

    loop_result = gates.audited_loop(
        initial_state=5,
        condition_fn=lambda s: s > 0,
        step_fn=lambda s: s - 1,
        variant_fn=lambda s: s,
        max_steps=10,
        label="COUNTDOWN",
    )

    return {
        "if_result": if_result.to_dict(),
        "loop_result": loop_result.to_dict(),
        "chain": gates.runner.commitments.verify_chain(),
    }


def main() -> None:
    print(json.dumps(demo(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
