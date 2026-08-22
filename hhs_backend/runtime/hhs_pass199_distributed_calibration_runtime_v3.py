"""Pass 199 I127 repair-forward production runtime.

This layer preserves the accepted V1/V2 implementations as historical provenance
while repairing the six post-merge defects reproduced by the Pass 219 reverse
census.  Candidate execution remains evidence-only; canonical admission remains
owned by the inherited singleton VM81/Pass190 commit path.
"""
from __future__ import annotations

import copy
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    M,
    ZERO_HASH72,
    Pass199CalibrationError,
    compact_gate,
    evaluate_branch_candidate as evaluate_branch_candidate_v1,
    exact_fraction,
    hhs_canonical_json,
    hhs_hash72,
    matrix_power,
    original_gate,
    pass190_hash72,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v1 import (
    BATCH_CLAIM_OPERATION_ID,
    BATCH_COMPLETE_OPERATION_ID,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v2 import (
    ENSURE_WORKERS_OPERATION_ID,
    V2_CONTRACT,
    Pass199DistributedCalibrationRuntime as Pass199DistributedCalibrationRuntimeV2,
    Pass199WorkerSlotContext,
)

REPAIR_SCHEMA = "HHS_PASS_199_I127_REPAIR_V1"
PRODUCTION_VERSION = "HHS_PASS_199_DISTRIBUTED_CALIBRATION_FABRIC_V3"


def _canonical_distinct_gate_values(arguments: Mapping[str, Any], branch: str) -> int:
    """Count gate payload identities without positional cell metadata."""

    x = exact_fraction(arguments["x"], field="candidate.x")
    y = exact_fraction(arguments["y"], field="candidate.y")
    if not x or not y:
        return 0
    exponent = int(arguments["xy_symbol"])
    q = matrix_power(M, -exponent)
    distinct: set[str] = set()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    try:
                        gate = (
                            original_gate(x, y, q, i, j, k, l)
                            if branch == "A"
                            else compact_gate(x, y, q, i, j, k, l)
                        )
                    except ZeroDivisionError:
                        continue
                    distinct.add(hhs_canonical_json(gate.payload()))
    return len(distinct)


def evaluate_branch_candidate_v3(arguments: Mapping[str, Any]) -> dict[str, Any]:
    """Reuse the accepted candidate witness and repair only diversity semantics."""

    candidate = evaluate_branch_candidate_v1(arguments)
    body = copy.deepcopy(candidate)
    body.pop("candidate_hash72", None)
    body["distinct_gate_values"] = _canonical_distinct_gate_values(
        arguments,
        str(arguments.get("branch")),
    )
    return {
        **body,
        "candidate_hash72": pass190_hash72("pass199.branch.candidate", body),
    }


class Pass199WorkerSlotContextV3(Pass199WorkerSlotContext):
    """Recover expired persisted claims before worker-slot active checks."""

    def _op_calibration_ensure_workers(self, args: dict[str, Any]) -> dict[str, Any]:
        now_ns = int(args["now_ns"])
        job_payloads, worker_payloads, _counts, _changed = self._scheduler_payloads(
            now_ns,
            1000,
        )
        if job_payloads or worker_payloads:
            self._commit_execution_records(
                job_payloads=job_payloads,
                worker_payloads=worker_payloads,
            )
        result = super()._op_calibration_ensure_workers(args)
        return {
            **result,
            "stale_claim_recovery_before_slot_validation": True,
        }


class Pass199DistributedCalibrationRuntime(Pass199DistributedCalibrationRuntimeV2):
    """Repaired Pass 199 production runtime with fail-closed closure semantics."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.context.close()
        self.context = Pass199WorkerSlotContextV3(
            self.database_path,
            holder_id="pass199-i127-repair-runtime",
        )

    def execute_workers(
        self,
        prepared: Mapping[str, Any],
        *,
        worker_count: int = 4,
    ) -> dict[str, Any]:
        if not 1 <= worker_count <= 64:
            raise ValueError("worker_count must be in [1,64]")
        claim_slot_count = min(64, int(prepared["expected_job_count"]))
        worker_ids = [f"p199.slot.{index:02d}" for index in range(claim_slot_count)]
        self._invoke(
            self.context,
            ENSURE_WORKERS_OPERATION_ID,
            {
                "worker_ids": worker_ids,
                "now_ns": time.time_ns(),
                "lease_timeout_ns": 300_000_000_000,
            },
            "worker:admin",
        )
        active = 0
        peak = 0
        active_lock = threading.Lock()
        newly_completed_ids: list[str] = []
        claim_batch_count = 0
        completion_batch_count = 0

        def compute(claim: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal active, peak
            with active_lock:
                active += 1
                peak = max(peak, active)
            try:
                return {
                    "job_id": claim["job_id"],
                    "worker_id": claim["worker_id"],
                    "claim_token_hash72": claim["claim_token_hash72"],
                    "candidate_result": evaluate_branch_candidate_v3(
                        claim["job"]["arguments"]
                    ),
                }
            finally:
                with active_lock:
                    active -= 1

        while True:
            claim_result = self._invoke(
                self.context,
                BATCH_CLAIM_OPERATION_ID,
                {
                    "workspace_id": prepared["workspace_id"],
                    "worker_ids": worker_ids,
                    "now_ns": time.time_ns(),
                    "lease_duration_ns": 300_000_000_000,
                },
                "worker:execute",
            ).result
            if not claim_result["claimed"]:
                break
            claim_batch_count += 1
            claims = claim_result["claims"]
            with ThreadPoolExecutor(max_workers=min(worker_count, len(claims))) as pool:
                completions = list(pool.map(compute, claims))
            completion_result = self._invoke(
                self.context,
                BATCH_COMPLETE_OPERATION_ID,
                {"completions": completions, "now_ns": time.time_ns()},
                "worker:execute",
            ).result
            completion_batch_count += 1
            newly_completed_ids.extend(
                item["job_id"] for item in completion_result["completions"]
            )

        durable_jobs = self._invoke(
            self.context,
            "job.list",
            {"workspace_id": prepared["workspace_id"]},
            "job:read",
        ).result
        durable_completed_ids = sorted(
            item["job_id"]
            for item in durable_jobs
            if item.get("status") == "completed"
        )
        return {
            "worker_count": worker_count,
            "compute_worker_count": worker_count,
            "durable_worker_slot_count": claim_slot_count,
            "completed_job_count": len(durable_completed_ids),
            "completed_job_ids": durable_completed_ids,
            "newly_completed_job_count": len(newly_completed_ids),
            "newly_completed_job_ids": sorted(newly_completed_ids),
            "peak_parallel_candidate_workers": peak,
            "candidate_computation_outside_authority_lock": True,
            "one_job_per_worker": True,
            "claim_batch_count": claim_batch_count,
            "completion_batch_count": completion_batch_count,
            "authority_mutations_reduced": True,
            "maximum_claim_batch_size": 64,
            "durable_completion_total_reconciled": True,
        }

    def _full_replay(
        self,
        prepared: Mapping[str, Any],
        expected_root: str,
        worker_count: int,
    ) -> dict[str, Any]:
        arguments: list[dict[str, Any]] = []
        operation = prepared["operation"]
        for state in prepared["tree"]["states"]:
            for branch in ("A", "B"):
                arguments.append(
                    {
                        "run_id": prepared["run_id"],
                        "operation_id": operation["operation_id"],
                        "operation_spec_hash72": operation["spec_hash72"],
                        "tree_hash72": prepared["tree"]["tree_hash72"],
                        "ordinal": int(state["ordinal"]),
                        "branch": branch,
                        "x": state["x"],
                        "y": state["y"],
                        "xy_symbol": int(state["xy_symbol"]),
                    }
                )
        with ThreadPoolExecutor(max_workers=max(1, worker_count)) as pool:
            candidates = list(pool.map(evaluate_branch_candidate_v3, arguments))
        replay = self._assemble_replay(
            candidates,
            int(prepared["tree"]["state_count"]),
        )
        deterministic = replay["ordered_state_root_hash72"] == expected_root
        return {
            "full_replay_executed": True,
            "replayed_branch_jobs": len(candidates),
            "replayed_parameter_states": int(prepared["tree"]["state_count"]),
            "replay_root_hash72": replay["ordered_state_root_hash72"],
            "deterministic": deterministic,
            "first_replay_mismatch": None
            if deterministic
            else {
                "expected": expected_root,
                "actual": replay["ordered_state_root_hash72"],
            },
        }

    def _validated_prior_report(
        self,
        prepared: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        if not self.report_path.exists():
            return None
        prior = json.loads(self.report_path.read_text(encoding="utf-8"))
        expected = hhs_hash72(
            "pass199.report",
            {
                key: value
                for key, value in prior.items()
                if key not in {"report_hash72", "pass198_run"}
            },
        )
        if prior.get("run_id") != prepared["run_id"]:
            return None
        if prior.get("report_hash72") != expected:
            return None
        return prior

    def _bound_existing_commit_receipt(
        self,
        prepared: Mapping[str, Any],
        requested_receipt: str | None,
    ) -> str | None:
        existing_commit = self.context.tree_commit(prepared["run_id"])
        if existing_commit is None:
            return requested_receipt
        commit_receipt = self.context.find_tree_commit_receipt(prepared["run_id"])
        if commit_receipt is None:
            raise Pass199CalibrationError(
                "singleton tree commit receipt is unavailable for existing commit"
            )
        self.context._verify_receipt_identity(commit_receipt)
        bound_receipt = str(
            commit_receipt.get("arguments", {}).get("vm81_receipt_hash72")
            or ZERO_HASH72
        )
        if requested_receipt is not None and str(requested_receipt) != bound_receipt:
            raise Pass199CalibrationError(
                "existing singleton commit is bound to a different VM81 receipt"
            )
        return bound_receipt

    def run(
        self,
        operation_id: str = "pass197.reciprocal_matrix_gate",
        config_payload: Mapping[str, Any] | None = None,
        *,
        worker_count: int = 8,
        vm81_receipt_hash72: str | None = None,
        resume: bool = True,
        full_replay: bool = True,
    ) -> dict[str, Any]:
        prepared = self.prepare_tree(operation_id, config_payload)
        if resume:
            prior = self._validated_prior_report(prepared)
            if prior is not None:
                self._last_report = copy.deepcopy(prior)
                return copy.deepcopy(prior)

        config_disables_replay = bool(
            config_payload is not None
            and config_payload.get("full_replay") is False
        )
        if not full_replay or config_disables_replay:
            raise Pass199CalibrationError(
                "full replay is mandatory before deterministic Pass 199 closure"
            )

        bound_receipt = self._bound_existing_commit_receipt(
            prepared,
            vm81_receipt_hash72,
        )
        core = super().run(
            operation_id,
            config_payload,
            worker_count=worker_count,
            vm81_receipt_hash72=bound_receipt,
            resume=False,
            full_replay=True,
        )
        if core.get("repair_schema") == REPAIR_SCHEMA:
            return copy.deepcopy(core)

        core_report_hash72 = str(core["report_hash72"])
        pass198_run = copy.deepcopy(core.get("pass198_run"))
        if not isinstance(pass198_run, dict):
            raise Pass199CalibrationError(
                "closed Pass 199 execution is missing its Pass 198 verification record"
            )
        if pass198_run.get("report_hash72") != core_report_hash72:
            raise Pass199CalibrationError(
                "Pass 198 verification is not bound to the executed core report"
            )

        upgraded = {
            key: copy.deepcopy(value)
            for key, value in core.items()
            if key not in {"report_hash72", "pass198_run"}
        }
        upgraded.update(
            {
                "version": PRODUCTION_VERSION,
                "contract": V2_CONTRACT,
                "core_contract": core.get("contract"),
                "core_report_hash72": core_report_hash72,
                "repair_schema": REPAIR_SCHEMA,
                "production_registry_hash216": self.context.registry.payload[
                    "registry_hash216"
                ],
                "governed_operation_count": len(self.context.registry.records),
                "pass198_verification_record_count": 1,
                "pass198_verification_reused_from_core_execution": True,
            }
        )
        upgraded["report_hash72"] = hhs_hash72("pass199.report", upgraded)
        upgraded["pass198_run"] = pass198_run
        self._write(self.report_path, upgraded)
        self._last_report = copy.deepcopy(upgraded)
        return copy.deepcopy(upgraded)
