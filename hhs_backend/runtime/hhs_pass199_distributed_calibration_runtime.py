"""Canonical production projection for the verified Pass 199 V2 runtime."""
from __future__ import annotations

import copy
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import hhs_hash72
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v2 import (
    V2_CONTRACT,
    Pass199DistributedCalibrationRuntime as Pass199DistributedCalibrationRuntimeV2,
)

PRODUCTION_VERSION = "HHS_PASS_199_DISTRIBUTED_CALIBRATION_FABRIC_V2"


class Pass199DistributedCalibrationRuntime(Pass199DistributedCalibrationRuntimeV2):
    """Expose the V2 contract while retaining the core contract as provenance."""

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
        report = super().run(
            operation_id,
            config_payload,
            worker_count=worker_count,
            vm81_receipt_hash72=vm81_receipt_hash72,
            resume=resume,
            full_replay=full_replay,
        )
        if report.get("contract") == V2_CONTRACT and report.get("version") == PRODUCTION_VERSION:
            return report
        operation = self.pass198.get_operation(operation_id)
        tree = self.pass198.parameter_tree(operation_id, config_payload)
        core_contract = report.get("contract")
        upgraded = {
            key: copy.deepcopy(value)
            for key, value in report.items()
            if key not in {"report_hash72", "pass198_run"}
        }
        upgraded.update(
            {
                "version": PRODUCTION_VERSION,
                "contract": V2_CONTRACT,
                "core_contract": core_contract,
                "production_registry_hash216": self.context.registry.payload["registry_hash216"],
                "governed_operation_count": len(self.context.registry.records),
            }
        )
        upgraded["report_hash72"] = hhs_hash72("pass199.report", upgraded)
        upgraded["pass198_run"] = self._record_pass198_run(
            {"operation": operation, "tree": tree},
            upgraded,
        )
        self._write(self.report_path, upgraded)
        self._last_report = copy.deepcopy(upgraded)
        return copy.deepcopy(upgraded)


PASS199_DISTRIBUTED_CALIBRATION_RUNTIME = Pass199DistributedCalibrationRuntime()
