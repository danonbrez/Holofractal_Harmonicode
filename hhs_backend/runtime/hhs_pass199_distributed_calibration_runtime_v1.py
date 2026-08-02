"""Restart-safe public runtime wrapper for the Pass 199 distributed fabric."""
from __future__ import annotations

import copy
import json
import time
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    BRANCH_OPERATION_ID,
    COMMIT_OPERATION_ID,
    CONTRACT,
    PASS199_ADMISSION_CAPABILITY,
    PASS199_CAPABILITY,
    VERSION,
    Pass199DistributedCalibrationFabric,
    Pass199DurableCalibrationContext,
    hhs_hash72,
    pass190_hash72,
)


class RestartSafePass199DurableCalibrationContext(Pass199DurableCalibrationContext):
    """Pass 199 context with bounded pagination for commit-receipt recovery."""

    def find_tree_commit_receipt(self, run_id: str) -> dict[str, Any] | None:
        cursor = 0
        match: dict[str, Any] | None = None
        while True:
            page = self.receipts_after(cursor, 1000)
            if not page:
                break
            for receipt in page:
                if (
                    receipt.get("operation_id") == COMMIT_OPERATION_ID
                    and receipt.get("arguments", {}).get("run_id") == run_id
                ):
                    self._verify_receipt_identity(receipt)
                    match = copy.deepcopy(receipt)
            cursor = int(page[-1]["receipt_index"])
        return match


class Pass199DistributedCalibrationRuntime(Pass199DistributedCalibrationFabric):
    """Public runtime preserving bounded scheduler and resume identities."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.context.close()
        self.context = RestartSafePass199DurableCalibrationContext(
            self.database_path,
            holder_id="pass199-public-runtime",
        )

    def prepare_tree(self, operation_id: str, config_payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        operation = self.pass198.get_operation(operation_id)
        tree = self.pass198.parameter_tree(operation_id, config_payload)
        run_id = pass190_hash72(
            "pass199.distributed.run",
            {
                "version": VERSION,
                "operation_id": operation_id,
                "spec_hash72": operation["spec_hash72"],
                "tree_hash72": tree["tree_hash72"],
            },
        )
        workspace_id = f"calibration.{run_id[:32]}"
        self._ensure_capability(PASS199_CAPABILITY)
        self._ensure_capability(PASS199_ADMISSION_CAPABILITY)
        self._ensure_workspace(workspace_id)
        existing_jobs = {
            item["job_id"]
            for item in self._invoke(
                self.context,
                "job.list",
                {"workspace_id": workspace_id},
                "job:read",
            ).result
        }
        submitted_at = time.time_ns()
        submitted = 0
        for state in tree["states"]:
            for branch in ("A", "B"):
                job_id = f"p199.{run_id[:20]}.{int(state['ordinal']):05d}.{branch.lower()}"
                if job_id in existing_jobs:
                    continue
                arguments = {
                    "run_id": run_id,
                    "operation_id": operation_id,
                    "operation_spec_hash72": operation["spec_hash72"],
                    "tree_hash72": tree["tree_hash72"],
                    "ordinal": int(state["ordinal"]),
                    "branch": branch,
                    "x": state["x"],
                    "y": state["y"],
                    "xy_symbol": int(state["xy_symbol"]),
                }
                self._invoke(
                    self.context,
                    "job.submit_execution",
                    {
                        "job_id": job_id,
                        "workspace_id": workspace_id,
                        "operation_id": BRANCH_OPERATION_ID,
                        "arguments": arguments,
                        "required_capabilities": [PASS199_CAPABILITY],
                        "submitted_at_ns": submitted_at,
                        "max_attempts": 3,
                        "retry_backoff_ns": 0,
                        "priority": 0,
                        "metadata": {
                            "pass199_run_id": run_id,
                            "ordinal": int(state["ordinal"]),
                            "branch": branch,
                            "tree_hash72": tree["tree_hash72"],
                            "deterministic_schedule_key": job_id,
                            "contract": CONTRACT,
                        },
                    },
                    "job:write",
                )
                submitted += 1
        return {
            "schema": "HHS_PASS_199_PREPARED_TREE_V1",
            "run_id": run_id,
            "workspace_id": workspace_id,
            "operation": operation,
            "tree": tree,
            "expected_job_count": int(tree["state_count"]) * 2,
            "submitted_job_count": submitted,
            "scheduler_priority": 0,
            "deterministic_ordering": "CANONICAL_JOB_ID_THEN_ORDINAL_COMMIT",
        }

    def run(
        self,
        operation_id: str = "pass197.reciprocal_matrix_gate",
        config_payload: Mapping[str, Any] | None = None,
        *,
        worker_count: int = 4,
        vm81_receipt_hash72: str | None = None,
        resume: bool = True,
        full_replay: bool = True,
    ) -> dict[str, Any]:
        prepared = self.prepare_tree(operation_id, config_payload)
        if resume and self.report_path.exists():
            prior = json.loads(self.report_path.read_text(encoding="utf-8"))
            identity = {
                key: value
                for key, value in prior.items()
                if key not in {"report_hash72", "pass198_run"}
            }
            expected = hhs_hash72("pass199.report", identity)
            if prior.get("run_id") == prepared["run_id"] and prior.get("report_hash72") == expected:
                self._last_report = prior
                return copy.deepcopy(prior)
        return super().run(
            operation_id,
            config_payload,
            worker_count=worker_count,
            vm81_receipt_hash72=vm81_receipt_hash72,
            resume=False,
            full_replay=full_replay,
        )


PASS199_DISTRIBUTED_CALIBRATION_RUNTIME = Pass199DistributedCalibrationRuntime()
