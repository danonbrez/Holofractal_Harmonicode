from __future__ import annotations

import tempfile
import unittest

from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime import (
    PRODUCTION_VERSION,
    REPAIR_SCHEMA,
    Pass199DistributedCalibrationRuntime,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v2 import V2_CONTRACT


class Pass199ProductionProjectionTests(unittest.TestCase):
    def test_production_report_binds_v2_contract_without_duplicate_pass198_run(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass199DistributedCalibrationRuntime(state_root=root)
            try:
                report = runtime.run(
                    config_payload={
                        "x_values": ["1"],
                        "y_values": ["1"],
                        "xy_symbol_values": [0],
                    },
                    worker_count=2,
                    vm81_receipt_hash72="7" * 72,
                )
                self.assertTrue(report["closed"])
                self.assertEqual(report["contract"], V2_CONTRACT)
                self.assertEqual(report["version"], PRODUCTION_VERSION)
                self.assertEqual(report["repair_schema"], REPAIR_SCHEMA)
                self.assertNotEqual(report["core_contract"], report["contract"])
                self.assertEqual(report["governed_operation_count"], 49)
                self.assertEqual(runtime.report()["report_hash72"], report["report_hash72"])
                runs = runtime.pass198.list_runs()
                self.assertEqual(len(runs), 1)
                self.assertEqual(report["pass198_verification_record_count"], 1)
                self.assertTrue(report["pass198_verification_reused_from_core_execution"])
                self.assertEqual(
                    report["pass198_run"]["run_id"],
                    runs[0]["run_id"],
                )
                self.assertEqual(
                    report["pass198_run"]["report_hash72"],
                    report["core_report_hash72"],
                )
                self.assertNotEqual(
                    report["report_hash72"],
                    report["core_report_hash72"],
                )
            finally:
                runtime.close()


if __name__ == "__main__":
    unittest.main()
