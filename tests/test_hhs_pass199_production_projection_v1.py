from __future__ import annotations

import tempfile
import unittest

from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime import (
    PRODUCTION_VERSION,
    Pass199DistributedCalibrationRuntime,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v2 import V2_CONTRACT


class Pass199ProductionProjectionTests(unittest.TestCase):
    def test_production_report_binds_v2_contract_and_preserves_core_provenance(self) -> None:
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
                self.assertNotEqual(report["core_contract"], report["contract"])
                self.assertEqual(report["governed_operation_count"], 49)
                self.assertEqual(runtime.report()["report_hash72"], report["report_hash72"])
                persistent_hashes = {
                    item["report_hash72"]
                    for item in runtime.pass198.list_runs()
                }
                self.assertIn(report["report_hash72"], persistent_hashes)
            finally:
                runtime.close()


if __name__ == "__main__":
    unittest.main()
