"""Restart-safe public runtime wrapper for the Pass 199 distributed fabric."""
from __future__ import annotations

import copy
import json
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    Pass199DistributedCalibrationFabric,
    hhs_hash72,
)


class Pass199DistributedCalibrationRuntime(Pass199DistributedCalibrationFabric):
    """Public runtime preserving receipt-independent resume identity."""

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
