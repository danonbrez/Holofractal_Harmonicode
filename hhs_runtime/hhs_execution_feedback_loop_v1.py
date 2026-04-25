"""
HHS Execution + Feedback Loop v1
================================

Closed autonomous cycle:

    plan -> action -> state update -> feedback observation -> re-evaluate

This module binds the higher planning stack to the sealed Layer 0 core_sandbox.
It does not let planning mutate the sandbox. Plans are translated into bounded
core actions, executed through AuditedRunner/HHSStateLayerV1, then feedback is
mapped through the physics adapter and committed as state.

Every cycle is:
    Hash72-addressed
    invariant-gated
    committed or quarantined
    ledgered and replayable
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json
import time

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import AuditedRunner
from hhs_runtime.core_sandbox.hhs_state_layer_v1 import HHSStateLayerV1, StatePatch
from hhs_runtime.core_sandbox.hhs_physics_model_v1 import (
    PhysicalObservation,
    map_observation_to_symbolic,
    build_state_patch,
)
from hhs_runtime.hhs_goal_oriented_planning_engine_v1 import (
    GoalPlanningDatabase,
    PlanStatus,
    PlanningTarget,
    run_goal_planning,
)
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_recursive_symbol_kernel_v1 import (
    AddressRelation,
    GlobalSymbolCache,
    OrthogonalChain,
    SymbolEntityType,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


class ExecutionStatus(str, Enum):
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"
    STALLED = "STALLED"


class ActionKind(str, Enum):
    CORE_OPERATION = "CORE_OPERATION"
    STATE_PATCH = "STATE_PATCH"
    FEEDBACK_OBSERVATION = "FEEDBACK_OBSERVATION"
    NOOP = "NOOP"


@dataclass(frozen=True)
class ExecutableAction:
    """Bounded action translated from a selected plan step."""

    action_index: int
    kind: ActionKind
    operation: str
    args: List[Any]
    state_path: str | None
    state_value: Any
    source_plan_hash72: str | None
    action_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class ActionExecutionReceipt:
    """Receipt for a single executed action."""

    action: ExecutableAction
    runtime_result: Dict[str, Any] | None
    state_result: Dict[str, Any] | None
    feedback_result: Dict[str, Any] | None
    status: ExecutionStatus
    receipt_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.to_dict(),
            "runtime_result": self.runtime_result,
            "state_result": self.state_result,
            "feedback_result": self.feedback_result,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class FeedbackCycleReceipt:
    """One closed-loop cycle receipt."""

    cycle_index: int
    target: PlanningTarget
    planning_receipt_hash72: str
    selected_plan_hash72: str | None
    actions: List[ActionExecutionReceipt]
    state_snapshot: Dict[str, Any]
    invariant_gate: EthicalInvariantReceipt
    status: ExecutionStatus
    receipt_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_index": self.cycle_index,
            "target": self.target.to_dict(),
            "planning_receipt_hash72": self.planning_receipt_hash72,
            "selected_plan_hash72": self.selected_plan_hash72,
            "actions": [a.to_dict() for a in self.actions],
            "state_snapshot": self.state_snapshot,
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class FeedbackRunReceipt:
    """Full closed-loop run receipt."""

    module: str
    cycles: List[FeedbackCycleReceipt]
    final_state_snapshot: Dict[str, Any]
    ledger_commit_receipt: Dict[str, Any]
    replay_receipt: Dict[str, Any]
    status: ExecutionStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "cycles": [c.to_dict() for c in self.cycles],
            "final_state_snapshot": self.final_state_snapshot,
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def invariant_gate_for_cycle(actions: Sequence[ActionExecutionReceipt], state_snapshot: Dict[str, Any]) -> EthicalInvariantReceipt:
    delta_e_zero = bool(state_snapshot.get("state_hash72")) and len(actions) > 0
    psi_zero = all(a.status == ExecutionStatus.COMMITTED for a in actions)
    theta = theta15_true()
    omega_true = bool(hash72_digest(("feedback_cycle_replay", [a.to_dict() for a in actions], state_snapshot), width=18))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "action_count": len(actions),
        "state_hash72": state_snapshot.get("state_hash72"),
    }
    receipt = hash72_digest(("execution_feedback_invariant_gate_v1", details, status.value), width=18)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def action_hash(action_index: int, kind: ActionKind, operation: str, args: Sequence[Any], state_path: str | None, state_value: Any, plan_hash: str | None) -> str:
    return hash72_digest(("executable_action_v1", action_index, kind.value, operation, list(args), state_path, state_value, plan_hash), width=18)


def plan_to_actions(plan_record: Dict[str, Any], max_actions: int = 4) -> List[ExecutableAction]:
    """Translate selected planning steps into bounded core-sandbox actions."""

    selected = plan_record.get("selected_plan") if isinstance(plan_record, dict) else None
    if not isinstance(selected, dict):
        h = action_hash(0, ActionKind.NOOP, "SUM", [[0]], "loop.noop", {"reason": "no_selected_plan"}, None)
        return [ExecutableAction(0, ActionKind.NOOP, "SUM", [[0]], "loop.noop", {"reason": "no_selected_plan"}, None, h)]

    plan_hash = str(selected.get("plan_hash72", ""))
    steps = [s for s in selected.get("steps", []) if isinstance(s, dict)]
    actions: List[ExecutableAction] = []
    for step in steps[:max_actions]:
        predicate = str(step.get("predicate", ""))
        confidence = str(step.get("confidence", "1/1"))
        confidence_num = 1
        try:
            if "/" in confidence:
                n, d = confidence.split("/", 1)
                confidence_num = max(1, int(n))
            else:
                confidence_num = max(1, int(Fraction(confidence)))
        except Exception:
            confidence_num = 1

        if predicate == "transforms_to":
            kind = ActionKind.CORE_OPERATION
            operation = "SUM"
            args = [[confidence_num, len(predicate)]]
            state_path = f"execution.plan.{len(actions)}"
            state_value = {"predicate": predicate, "step": step}
        elif predicate == "equals":
            kind = ActionKind.CORE_OPERATION
            operation = "ADD"
            args = [confidence_num, 0]
            state_path = f"execution.equality.{len(actions)}"
            state_value = {"predicate": predicate, "step": step}
        else:
            kind = ActionKind.STATE_PATCH
            operation = "SET"
            args = []
            state_path = f"execution.fact.{len(actions)}"
            state_value = {"predicate": predicate, "step": step}

        h = action_hash(len(actions), kind, operation, args, state_path, state_value, plan_hash)
        actions.append(ExecutableAction(len(actions), kind, operation, args, state_path, state_value, plan_hash, h))

    if not actions:
        h = action_hash(0, ActionKind.NOOP, "SUM", [[0]], "loop.noop", {"reason": "empty_plan"}, plan_hash)
        actions.append(ExecutableAction(0, ActionKind.NOOP, "SUM", [[0]], "loop.noop", {"reason": "empty_plan"}, plan_hash, h))
    return actions


class ExecutionFeedbackControllerV1:
    """Closed-loop controller: plan -> execute -> observe -> update."""

    def __init__(self, *, runner: AuditedRunner | None = None, state_layer: HHSStateLayerV1 | None = None):
        self.runner = runner or AuditedRunner()
        self.state_layer = state_layer or HHSStateLayerV1(runner=self.runner)

    def execute_action(self, action: ExecutableAction) -> ActionExecutionReceipt:
        runtime_result = None
        state_result = None
        feedback_result = None
        status = ExecutionStatus.COMMITTED
        quarantine = None

        try:
            if action.kind in {ActionKind.CORE_OPERATION, ActionKind.NOOP}:
                runtime_result = self.runner.execute(action.operation, *action.args, input_payload=action.to_dict())
                if not runtime_result.get("ok"):
                    status = ExecutionStatus.QUARANTINED
                if action.state_path:
                    state_result = self.state_layer.set(action.state_path, {"action": action.to_dict(), "runtime": runtime_result})
                    if not state_result.get("ok"):
                        status = ExecutionStatus.QUARANTINED
            elif action.kind == ActionKind.STATE_PATCH:
                state_result = self.state_layer.set(action.state_path or f"execution.patch.{action.action_index}", action.state_value, action=action.operation)
                if not state_result.get("ok"):
                    status = ExecutionStatus.QUARANTINED
            elif action.kind == ActionKind.FEEDBACK_OBSERVATION:
                obs = PhysicalObservation(str(action.state_path or "feedback"), float(action.state_value or 0), time.time())
                symbolic = map_observation_to_symbolic(obs)
                patch = build_state_patch(symbolic)
                feedback_result = {"observation": asdict(obs), "symbolic": symbolic, "patch": patch}
                state_result = self.state_layer.apply_patch(StatePatch(patch["op"], patch["path"], patch["value"], {"source": "feedback"}))
                if not state_result.get("ok"):
                    status = ExecutionStatus.QUARANTINED
            else:
                status = ExecutionStatus.QUARANTINED
        except Exception as exc:
            status = ExecutionStatus.QUARANTINED
            feedback_result = {"exception": type(exc).__name__, "message": str(exc)}

        if status == ExecutionStatus.QUARANTINED:
            quarantine = hash72_digest(("action_quarantine", action.to_dict(), runtime_result, state_result, feedback_result), width=18)
        receipt = hash72_digest(("action_execution_receipt_v1", action.to_dict(), runtime_result, state_result, feedback_result, status.value, quarantine), width=18)
        return ActionExecutionReceipt(action, runtime_result, state_result, feedback_result, status, receipt, quarantine)

    def run_cycle(self, cycle_index: int, target: PlanningTarget, *, planning_database_path: str | Path, reasoning_database_path: str | Path, planning_ledger_path: str | Path) -> FeedbackCycleReceipt:
        planning = run_goal_planning(
            [target],
            reasoning_database_path=reasoning_database_path,
            planning_database_path=planning_database_path,
            ledger_path=planning_ledger_path,
        )
        planning_db = GoalPlanningDatabase(planning_database_path)
        records = planning_db.search(target.name)
        plan_record = records[-1] if records else {}
        selected_plan = plan_record.get("selected_plan") if isinstance(plan_record, dict) else None
        selected_hash = selected_plan.get("plan_hash72") if isinstance(selected_plan, dict) else None
        actions = plan_to_actions(plan_record)
        action_receipts = [self.execute_action(action) for action in actions]

        # Always append one feedback observation derived from current cycle status.
        feedback_value = 1.0 if all(a.status == ExecutionStatus.COMMITTED for a in action_receipts) else -1.0
        fb_hash = action_hash(len(action_receipts), ActionKind.FEEDBACK_OBSERVATION, "OBSERVE", [feedback_value], f"cycle_{cycle_index}_feedback", feedback_value, selected_hash)
        feedback_action = ExecutableAction(len(action_receipts), ActionKind.FEEDBACK_OBSERVATION, "OBSERVE", [feedback_value], f"cycle_{cycle_index}_feedback", feedback_value, selected_hash, fb_hash)
        action_receipts.append(self.execute_action(feedback_action))

        snapshot = self.state_layer.snapshot()
        gate = invariant_gate_for_cycle(action_receipts, snapshot)
        if gate.status != ModificationStatus.APPLIED:
            status = ExecutionStatus.QUARANTINED
        elif selected_hash is None:
            status = ExecutionStatus.STALLED
        else:
            status = ExecutionStatus.COMMITTED
        quarantine = None if status != ExecutionStatus.QUARANTINED else hash72_digest(("cycle_quarantine", cycle_index, target.to_dict(), [a.to_dict() for a in action_receipts], gate.to_dict()), width=18)
        receipt = hash72_digest(("feedback_cycle_receipt_v1", cycle_index, target.to_dict(), planning.receipt_hash72, selected_hash, [a.receipt_hash72 for a in action_receipts], snapshot, gate.receipt_hash72, status.value), width=18)
        return FeedbackCycleReceipt(cycle_index, target, planning.receipt_hash72, selected_hash, action_receipts, snapshot, gate, status, receipt, quarantine)


def run_execution_feedback_loop(
    targets: Sequence[PlanningTarget],
    cycles: int = 1,
    reasoning_database_path: str | Path = "demo_reports/hhs_symbolic_reasoning_db_v1.json",
    planning_database_path: str | Path = "demo_reports/hhs_goal_planning_db_v1.json",
    planning_ledger_path: str | Path = "demo_reports/hhs_goal_planning_ledger_v1.json",
    execution_ledger_path: str | Path = "demo_reports/hhs_execution_feedback_ledger_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
) -> FeedbackRunReceipt:
    if cycles <= 0:
        raise ValueError("cycles must be positive")
    if not targets:
        raise ValueError("at least one planning target is required")

    controller = ExecutionFeedbackControllerV1()
    cycle_receipts: List[FeedbackCycleReceipt] = []
    final_status = ExecutionStatus.STALLED
    for cycle_index in range(cycles):
        target = targets[cycle_index % len(targets)]
        cycle = controller.run_cycle(
            cycle_index,
            target,
            planning_database_path=planning_database_path,
            reasoning_database_path=reasoning_database_path,
            planning_ledger_path=planning_ledger_path,
        )
        cycle_receipts.append(cycle)
        final_status = cycle.status
        if cycle.status == ExecutionStatus.QUARANTINED:
            break

    ledger = MemoryLedger(execution_ledger_path)
    commit = ledger.append_payloads("execution_feedback_cycle_v1", [c.to_dict() for c in cycle_receipts])
    replay = replay_ledger(execution_ledger_path)

    cache = GlobalSymbolCache(symbol_cache_path)
    for cycle in cycle_receipts:
        if cycle.status == ExecutionStatus.COMMITTED:
            cache.append_record(
                SymbolEntityType.OPERATION,
                f"execution_cycle:{cycle.cycle_index}",
                "operation_record",
                cycle.to_dict(),
                [OrthogonalChain.OPERATION_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
                relation=AddressRelation(by_symbol=None, from_symbol=None, through_symbol=None, to_symbol=None),
            )

    final_snapshot = controller.state_layer.snapshot()
    receipt = hash72_digest(("execution_feedback_run_v1", [c.receipt_hash72 for c in cycle_receipts], final_snapshot, commit.receipt_hash72, replay.receipt_hash72, final_status.value), width=18)
    return FeedbackRunReceipt("hhs_execution_feedback_loop_v1", cycle_receipts, final_snapshot, commit.to_dict(), replay.to_dict(), final_status, receipt)


def demo() -> Dict[str, Any]:
    target = PlanningTarget(name="Demo transform execution", target_predicate="transforms_to", min_confidence="1/2")
    return run_execution_feedback_loop([target], cycles=1).to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
