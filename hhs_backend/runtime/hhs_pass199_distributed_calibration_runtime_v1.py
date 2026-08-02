"""Restart-safe public runtime wrapper for the Pass 199 distributed fabric."""
from __future__ import annotations

import copy
import json
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    COMMIT_OPERATION_ID,
    Pass199DistributedCalibrationFabric,
    Pass199DurableCalibrationContext,
    hhs_hash72,
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
    """Public runtime preserving receipt-independent resume identity."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.context.close()
        self.context = RestartSafePass199DurableCalibrationContext(
            self.database_path,
            holder_id="pass199-public-runtime",
        )

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
