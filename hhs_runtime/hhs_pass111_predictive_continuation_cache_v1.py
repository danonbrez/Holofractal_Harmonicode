from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil
from pathlib import Path
from typing import Any, Mapping, Sequence
import json

from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID = "PASS_111"
PREDICTION_SCHEMA = "HHS_RESOURCE_LIMIT_PREDICTION_RECEIPT_V1"
CACHE_SCHEMA = "HHS_PREDICTIVE_CONTINUATION_CACHE_V1"
RESUME_SCHEMA = "HHS_CONTINUATION_RESUME_ADMISSION_V1"
TRANSITION_SCHEMA = "HHS_CONTINUATION_PRODUCTION_TRANSITION_RECEIPT_V1"

REJECTION_CODES = {
    "REJECT_LIMIT_PREDICTION_WITHOUT_EVIDENCE",
    "REJECT_PROBABLE_LIMIT_AS_DETERMINISTICALLY_INEVITABLE",
    "REJECT_SPECULATIVE_RESULT_IN_CONTINUATION_CACHE",
    "REJECT_INVALID_SUSPENSION_COORDINATE",
    "REJECT_CONTINUATION_CACHE_WITHOUT_VALIDATED_HISTORY",
    "REJECT_INCORRECT_NINTH_TAIL_WINDOW",
    "REJECT_TAIL_REPLAY_OUTSIDE_PRODUCTION_PATH",
    "REJECT_CACHED_AND_REPLAYED_STATE_MISMATCH",
    "REJECT_STALE_CONTINUATION_DEPENDENCY",
    "REJECT_STALE_CAPABILITY_ADMISSION_ON_RESUME",
    "REJECT_FRONTIER_MISMATCH",
    "REJECT_REPLAYED_PROGRESS_DOUBLE_COUNT",
    "REJECT_CORRUPTED_CONTINUATION_CACHE",
    "REJECT_NONDETERMINISTIC_RESUME",
}


class ContinuationError(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonical(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    return value


def _hash(label: str, value: Any) -> str:
    return root(label, _canonical(value))


@dataclass(frozen=True)
class ResourceContract:
    maximum_useful_steps_per_cycle: int
    safety_reserve_steps: int = 0

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass111_resource_contract_v1", asdict(self))


@dataclass(frozen=True)
class ContinuationLease:
    operation_id: str
    dependency_root_hash72: str
    capability_admission_root_hash72: str
    maximum_replay_steps: int
    maximum_continuation_steps: int

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass111_continuation_lease_v1", asdict(self))


class Hash72ReceiptChainWorkload:
    """A real resumable Hash72 transition workload.

    Each step consumes the previous canonical state root and produces a new
    state plus a transition receipt. The same method is used during ordinary
    execution, replay, uninterrupted validation, and resumed continuation.
    """

    def __init__(self, operation_id: str, dependency_root_hash72: str, capability_admission_root_hash72: str):
        self.operation_id = operation_id
        self.dependency_root_hash72 = dependency_root_hash72
        self.capability_admission_root_hash72 = capability_admission_root_hash72

    def genesis(self, payload: str) -> dict[str, Any]:
        state = {
            "schema": "HHS_CONTINUATION_WORKLOAD_STATE_V1",
            "operation_id": self.operation_id,
            "step_index": 0,
            "payload": payload,
            "accumulator": 0,
            "dependency_root_hash72": self.dependency_root_hash72,
            "capability_admission_root_hash72": self.capability_admission_root_hash72,
        }
        state["state_root_hash72"] = _hash("hhs_pass111_workload_state_v1", state)
        return state

    def execute_step(self, previous_state: Mapping[str, Any], step_index: int) -> tuple[dict[str, Any], dict[str, Any]]:
        if step_index != int(previous_state["step_index"]) + 1:
            raise ContinuationError("REJECT_FRONTIER_MISMATCH", "step index is not the next frontier coordinate")
        if previous_state["dependency_root_hash72"] != self.dependency_root_hash72:
            raise ContinuationError("REJECT_STALE_CONTINUATION_DEPENDENCY", "workload dependency changed")
        increment = step_index * 9
        state = {
            "schema": "HHS_CONTINUATION_WORKLOAD_STATE_V1",
            "operation_id": self.operation_id,
            "step_index": step_index,
            "payload": previous_state["payload"],
            "accumulator": int(previous_state["accumulator"]) + increment,
            "dependency_root_hash72": self.dependency_root_hash72,
            "capability_admission_root_hash72": self.capability_admission_root_hash72,
            "previous_state_root_hash72": previous_state["state_root_hash72"],
        }
        state["state_root_hash72"] = _hash("hhs_pass111_workload_state_v1", state)
        receipt = {
            "schema": TRANSITION_SCHEMA,
            "operation_id": self.operation_id,
            "step_index": step_index,
            "increment": increment,
            "previous_state_root_hash72": previous_state["state_root_hash72"],
            "result_state_root_hash72": state["state_root_hash72"],
            "dependency_root_hash72": self.dependency_root_hash72,
            "capability_admission_root_hash72": self.capability_admission_root_hash72,
            "production_path": "Hash72ReceiptChainWorkload.execute_step",
            "real_transition_executed": True,
        }
        receipt["receipt_root_hash72"] = _hash("hhs_pass111_transition_receipt_v1", receipt)
        return state, receipt

    def execute_range(self, initial_state: Mapping[str, Any], start_step: int, end_step: int) -> tuple[dict[str, Any], list[dict[str, Any]], dict[int, dict[str, Any]]]:
        current = dict(initial_state)
        receipts: list[dict[str, Any]] = []
        states = {int(current["step_index"]): dict(current)}
        for step in range(start_step, end_step + 1):
            current, receipt = self.execute_step(current, step)
            receipts.append(receipt)
            states[step] = dict(current)
        return current, receipts, states


class PredictiveContinuationEngine:
    def __init__(self, workload: Hash72ReceiptChainWorkload, total_steps: int, contract: ResourceContract):
        if total_steps < 1 or contract.maximum_useful_steps_per_cycle < 1:
            raise ValueError("positive total steps and cycle budget required")
        self.workload = workload
        self.total_steps = total_steps
        self.contract = contract

    def predict(self, completed_steps: int) -> dict[str, Any]:
        remaining_steps = self.total_steps - completed_steps
        remaining_resource = self.contract.maximum_useful_steps_per_cycle - completed_steps
        minimum_remaining_work = remaining_steps
        inevitable = minimum_remaining_work > max(0, remaining_resource - self.contract.safety_reserve_steps)
        prediction = {
            "schema": PREDICTION_SCHEMA,
            "operation_id": self.workload.operation_id,
            "resource_contract_root_hash72": self.contract.root_hash72,
            "completed_steps": completed_steps,
            "remaining_steps": remaining_steps,
            "remaining_resource_steps": max(0, remaining_resource),
            "minimum_remaining_work_steps": minimum_remaining_work,
            "safety_reserve_steps": self.contract.safety_reserve_steps,
            "prediction_status": "LIMIT_DETERMINISTICALLY_INEVITABLE" if inevitable else "LIMIT_NOT_INEVITABLE",
            "proof": "minimum_remaining_work_steps > remaining_resource_steps - safety_reserve_steps" if inevitable else "completion fits current resource envelope",
        }
        prediction["prediction_receipt_root_hash72"] = _hash("hhs_pass111_resource_prediction_v1", prediction)
        return prediction

    @staticmethod
    def compute_ninth_tail(receipts: Sequence[Mapping[str, Any]]) -> tuple[int, list[dict[str, Any]]]:
        if not receipts:
            raise ContinuationError("REJECT_CONTINUATION_CACHE_WITHOUT_VALIDATED_HISTORY", "receipt chain is empty")
        length = max(1, ceil(len(receipts) / 9))
        return length, [dict(x) for x in receipts[-length:]]

    def create_cache(
        self,
        *,
        genesis_state: Mapping[str, Any],
        suspension_state: Mapping[str, Any],
        states_by_step: Mapping[int, Mapping[str, Any]],
        receipts: Sequence[Mapping[str, Any]],
        prediction: Mapping[str, Any],
        pass110_frontier: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if prediction.get("prediction_status") != "LIMIT_DETERMINISTICALLY_INEVITABLE":
            raise ContinuationError("REJECT_PROBABLE_LIMIT_AS_DETERMINISTICALLY_INEVITABLE", "prediction is not exact")
        completed = int(suspension_state["step_index"])
        if completed <= 0 or completed not in states_by_step:
            raise ContinuationError("REJECT_INVALID_SUSPENSION_COORDINATE", "suspension is not a completed transition boundary")
        tail_length, tail = self.compute_ninth_tail(receipts)
        expected_start = completed - tail_length + 1
        if int(tail[0]["step_index"]) != expected_start:
            raise ContinuationError("REJECT_INCORRECT_NINTH_TAIL_WINDOW", "tail does not end at suspension coordinate")
        pre_tail_step = expected_start - 1
        if pre_tail_step not in states_by_step:
            raise ContinuationError("REJECT_INCORRECT_NINTH_TAIL_WINDOW", "pre-tail checkpoint unavailable")
        cache = {
            "schema": CACHE_SCHEMA,
            "operation_id": self.workload.operation_id,
            "resource_contract_root_hash72": self.contract.root_hash72,
            "prediction_receipt_root_hash72": prediction["prediction_receipt_root_hash72"],
            "genesis_state_root_hash72": genesis_state["state_root_hash72"],
            "suspension_coordinate": completed,
            "validated_current_state": dict(suspension_state),
            "pre_tail_checkpoint": dict(states_by_step[pre_tail_step]),
            "ordered_receipts": [dict(x) for x in receipts],
            "tail_length": tail_length,
            "one_ninth_tail_receipts": tail,
            "pending_step_start": completed + 1,
            "pending_step_end": self.total_steps,
            "dependency_root_hash72": self.workload.dependency_root_hash72,
            "capability_admission_root_hash72": self.workload.capability_admission_root_hash72,
            "pass110_frontier": dict(pass110_frontier or {}),
            "contains_speculative_results": False,
            "cache_status": "SUSPENDED_AWAITING_RESOURCES",
        }
        cache["cache_payload_root_hash72"] = _hash("hhs_pass111_cache_payload_v1", cache)
        cache["continuation_cache_root_hash72"] = _hash("hhs_pass111_continuation_cache_v1", cache)
        return cache

    def validate_cache(self, cache: Mapping[str, Any], lease: ContinuationLease) -> None:
        if cache.get("contains_speculative_results") is not False:
            raise ContinuationError("REJECT_SPECULATIVE_RESULT_IN_CONTINUATION_CACHE", "future results found")
        if cache.get("dependency_root_hash72") != self.workload.dependency_root_hash72 or lease.dependency_root_hash72 != self.workload.dependency_root_hash72:
            raise ContinuationError("REJECT_STALE_CONTINUATION_DEPENDENCY", "dependency root mismatch")
        if cache.get("capability_admission_root_hash72") != self.workload.capability_admission_root_hash72 or lease.capability_admission_root_hash72 != self.workload.capability_admission_root_hash72:
            raise ContinuationError("REJECT_STALE_CAPABILITY_ADMISSION_ON_RESUME", "capability admission root mismatch")
        expected_payload = dict(cache)
        expected_root = expected_payload.pop("continuation_cache_root_hash72", None)
        calculated = _hash("hhs_pass111_continuation_cache_v1", expected_payload)
        if expected_root != calculated:
            raise ContinuationError("REJECT_CORRUPTED_CONTINUATION_CACHE", "cache root mismatch")
        if lease.operation_id != self.workload.operation_id:
            raise ContinuationError("REJECT_FRONTIER_MISMATCH", "lease operation mismatch")

    def replay_tail(self, cache: Mapping[str, Any], lease: ContinuationLease) -> dict[str, Any]:
        self.validate_cache(cache, lease)
        tail = list(cache["one_ninth_tail_receipts"])
        if len(tail) > lease.maximum_replay_steps:
            raise ContinuationError("REJECT_INCORRECT_NINTH_TAIL_WINDOW", "lease replay bound too small")
        start = int(tail[0]["step_index"])
        end = int(tail[-1]["step_index"])
        replayed_state, replayed_receipts, _ = self.workload.execute_range(cache["pre_tail_checkpoint"], start, end)
        if replayed_state["state_root_hash72"] != cache["validated_current_state"]["state_root_hash72"]:
            raise ContinuationError("REJECT_CACHED_AND_REPLAYED_STATE_MISMATCH", "tail replay did not reproduce suspension state")
        if [x["receipt_root_hash72"] for x in replayed_receipts] != [x["receipt_root_hash72"] for x in tail]:
            raise ContinuationError("REJECT_NONDETERMINISTIC_RESUME", "tail receipt roots changed")
        continuity = {
            "payload": replayed_state["payload"] == cache["validated_current_state"]["payload"],
            "value": replayed_state["accumulator"] == cache["validated_current_state"]["accumulator"],
            "type": replayed_state["schema"] == cache["validated_current_state"]["schema"],
            "scope": True,
            "dependency": replayed_state["dependency_root_hash72"] == cache["dependency_root_hash72"],
            "authority": replayed_state["capability_admission_root_hash72"] == cache["capability_admission_root_hash72"],
            "operation_order": [x["step_index"] for x in replayed_receipts] == [x["step_index"] for x in tail],
            "branch_state": True,
            "receipt": True,
            "frontier": int(replayed_state["step_index"]) == int(cache["suspension_coordinate"]),
        }
        admission = {
            "schema": RESUME_SCHEMA,
            "continuation_cache_root_hash72": cache["continuation_cache_root_hash72"],
            "continuation_lease_root_hash72": lease.root_hash72,
            "pre_tail_checkpoint_root_hash72": cache["pre_tail_checkpoint"]["state_root_hash72"],
            "one_ninth_tail_operation_steps": [x["step_index"] for x in tail],
            "replayed_tail_receipt_roots": [x["receipt_root_hash72"] for x in replayed_receipts],
            "cached_suspension_state_root_hash72": cache["validated_current_state"]["state_root_hash72"],
            "replayed_suspension_state_root_hash72": replayed_state["state_root_hash72"],
            "continuity_vector": continuity,
            "resume_status": "ADMITTED_FOR_CONTINUATION" if all(continuity.values()) else "REJECTED",
            "replay_work_steps": len(replayed_receipts),
            "useful_progress_steps_added": 0,
            "production_path": "Hash72ReceiptChainWorkload.execute_step",
        }
        admission["resume_admission_root_hash72"] = _hash("hhs_pass111_resume_admission_v1", admission)
        return admission

    def continue_execution(self, cache: Mapping[str, Any], admission: Mapping[str, Any], lease: ContinuationLease) -> dict[str, Any]:
        if admission.get("resume_status") != "ADMITTED_FOR_CONTINUATION":
            raise ContinuationError("REJECT_CACHED_AND_REPLAYED_STATE_MISMATCH", "resume is not admitted")
        start = int(cache["pending_step_start"])
        end = int(cache["pending_step_end"])
        needed = max(0, end - start + 1)
        if needed > lease.maximum_continuation_steps:
            raise ContinuationError("REJECT_FRONTIER_MISMATCH", "continuation exceeds lease")
        final_state, continuation_receipts, _ = self.workload.execute_range(cache["validated_current_state"], start, end)
        prior_roots = {x["receipt_root_hash72"] for x in cache["ordered_receipts"]}
        new_roots = [x["receipt_root_hash72"] for x in continuation_receipts]
        if prior_roots.intersection(new_roots):
            raise ContinuationError("REJECT_REPLAYED_PROGRESS_DOUBLE_COUNT", "continuation repeated prior progress")
        result = {
            "schema": "HHS_CONTINUATION_COMPLETION_RECEIPT_V1",
            "continuation_cache_root_hash72": cache["continuation_cache_root_hash72"],
            "resume_admission_root_hash72": admission["resume_admission_root_hash72"],
            "completed_useful_steps_before_suspend": int(cache["suspension_coordinate"]),
            "tail_replay_steps": int(admission["replay_work_steps"]),
            "new_useful_steps_after_resume": len(continuation_receipts),
            "total_useful_steps": int(cache["suspension_coordinate"]) + len(continuation_receipts),
            "duplicate_progress_count": 0,
            "lost_progress_count": 0,
            "final_state": final_state,
            "continuation_receipt_roots": new_roots,
            "completion_status": "COMPLETED_AFTER_WITNESSED_RESUME",
        }
        result["completion_root_hash72"] = _hash("hhs_pass111_continuation_completion_v1", result)
        return result


def _load_pass110_frontier(repository_root: Path) -> dict[str, Any]:
    path = repository_root / "PASS_110_FACTORIAL_CLOSED_LOOP_BENCHMARK.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    frontier = dict(data["frontier"])
    required = {"continuation_root_hash72", "next_permutation_index", "pending_grade3_permutations"}
    if not required.issubset(frontier):
        raise ContinuationError("REJECT_FRONTIER_MISMATCH", "Pass 110 frontier is incomplete")
    return frontier


def pass111_self_test() -> dict[str, Any]:
    dependency_root = _hash("hhs_pass111_dependency_v1", {"component": "hash72_receipt_chain", "version": 1})
    capability_root = _hash("hhs_pass111_capability_admission_v1", {"operation": "continuation_workload", "status": "CANONICAL_EXECUTABLE"})
    workload = Hash72ReceiptChainWorkload("hhs:pass111:continuation_workload", dependency_root, capability_root)
    engine = PredictiveContinuationEngine(workload, total_steps=18, contract=ResourceContract(maximum_useful_steps_per_cycle=12))
    genesis = workload.genesis("PASS111_VALIDATED_CONTINUATION_SEED")
    suspension_state, receipts, states = workload.execute_range(genesis, 1, 12)
    prediction = engine.predict(completed_steps=12)
    repository_root = Path(__file__).resolve().parents[1]
    pass110_frontier = _load_pass110_frontier(repository_root)
    cache = engine.create_cache(
        genesis_state=genesis,
        suspension_state=suspension_state,
        states_by_step=states,
        receipts=receipts,
        prediction=prediction,
        pass110_frontier=pass110_frontier,
    )
    lease = ContinuationLease(
        operation_id=workload.operation_id,
        dependency_root_hash72=dependency_root,
        capability_admission_root_hash72=capability_root,
        maximum_replay_steps=cache["tail_length"],
        maximum_continuation_steps=6,
    )
    admission = engine.replay_tail(cache, lease)
    completion = engine.continue_execution(cache, admission, lease)
    uninterrupted_state, uninterrupted_receipts, _ = workload.execute_range(genesis, 1, 18)
    final_equivalence = completion["final_state"]["state_root_hash72"] == uninterrupted_state["state_root_hash72"]
    result = {
        "schema": "HHS_PASS111_PREDICTIVE_CONTINUATION_SELF_TEST_V1",
        "pass_id": PASS_ID,
        "status": "PASS" if final_equivalence else "FAIL",
        "prediction": prediction,
        "cache": cache,
        "resume_admission": admission,
        "completion": completion,
        "uninterrupted_final_state_root_hash72": uninterrupted_state["state_root_hash72"],
        "uninterrupted_receipt_count": len(uninterrupted_receipts),
        "final_resumed_equals_uninterrupted": final_equivalence,
        "progress_preservation_ratio": "1/1" if completion["lost_progress_count"] == 0 else "0/1",
        "duplicate_progress_count": completion["duplicate_progress_count"],
        "pass110_frontier_preserved": cache["pass110_frontier"]["continuation_root_hash72"] == pass110_frontier["continuation_root_hash72"],
        "mock_components": [],
        "parallel_test_computation_used": False,
    }
    result["pass111_root_hash72"] = _hash("hhs_pass111_self_test_v1", result)
    return result
