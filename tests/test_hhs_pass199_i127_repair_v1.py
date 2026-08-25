from __future__ import annotations

import tempfile
import time
import unittest
from fractions import Fraction
from pathlib import Path

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    COMMIT_OPERATION_ID,
    M,
    Pass199CalibrationError,
    matrix_power,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v1 import (
    BATCH_CLAIM_OPERATION_ID,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v2 import (
    ENSURE_WORKERS_OPERATION_ID,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v3 import (
    PRODUCTION_VERSION,
    REPAIR_SCHEMA,
    Pass199DistributedCalibrationRuntime,
    evaluate_branch_candidate_v3,
)
from hhs_backend.runtime.pass197_state_v1 import evaluate_state

ONE_CONFIG = {
    "x_values": ["1"],
    "y_values": ["1"],
    "xy_symbol_values": [0],
    "include_domain_rejections": True,
    "full_replay": True,
}

SMALL_CONFIG = {
    "x_values": ["-1", "0", "1"],
    "y_values": ["-1", "1"],
    "xy_symbol_values": [0],
    "include_domain_rejections": True,
    "full_replay": True,
}


def _all_receipts(runtime: Pass199DistributedCalibrationRuntime) -> list[dict]:
    receipts: list[dict] = []
    cursor = 0
    while True:
        page = runtime.context.receipts_after(cursor, 1000)
        if not page:
            break
        receipts.extend(page)
        cursor = int(page[-1]["receipt_index"])
    return receipts


class Pass199I127RepairTests(unittest.TestCase):
    def test_one_execution_records_exactly_one_pass198_verification(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass199DistributedCalibrationRuntime(state_root=root)
            try:
                report = runtime.run(
                    config_payload=ONE_CONFIG,
                    worker_count=2,
                    vm81_receipt_hash72="a" * 72,
                )
                runs = runtime.pass198.list_runs()
                self.assertTrue(report["closed"])
                self.assertEqual(report["version"], PRODUCTION_VERSION)
                self.assertEqual(report["repair_schema"], REPAIR_SCHEMA)
                self.assertEqual(report["pass198_verification_record_count"], 1)
                self.assertEqual(len(runs), 1)
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
                self.assertEqual(len(runtime.pass198.list_simplifications()), 4)
            finally:
                runtime.close()

    def test_full_replay_is_mandatory_before_any_closed_execution(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass199DistributedCalibrationRuntime(state_root=root)
            try:
                with self.assertRaisesRegex(
                    Pass199CalibrationError,
                    "full replay is mandatory",
                ):
                    runtime.run(
                        config_payload=ONE_CONFIG,
                        worker_count=2,
                        vm81_receipt_hash72="b" * 72,
                        full_replay=False,
                    )
                self.assertEqual(runtime.pass198.list_runs(), [])
                commits = [
                    receipt
                    for receipt in _all_receipts(runtime)
                    if receipt["operation_id"] == COMMIT_OPERATION_ID
                ]
                self.assertEqual(commits, [])
            finally:
                runtime.close()

    def test_gate_diversity_matches_canonical_pass197_payload_identity(self) -> None:
        baseline = evaluate_state(
            Fraction(1, 1),
            Fraction(1, 1),
            0,
            matrix_power(M, 0),
        )
        self.assertLess(baseline["distinct_gate_values"], 81)
        base_arguments = {
            "run_id": "r" * 72,
            "operation_id": "pass197.reciprocal_matrix_gate",
            "operation_spec_hash72": "s" * 72,
            "tree_hash72": "t" * 72,
            "ordinal": 0,
            "x": {"numerator": 1, "denominator": 1},
            "y": {"numerator": 1, "denominator": 1},
            "xy_symbol": 0,
        }
        for branch in ("A", "B"):
            candidate = evaluate_branch_candidate_v3(
                {**base_arguments, "branch": branch}
            )
            self.assertEqual(candidate["status"], "ADMITTED")
            self.assertEqual(
                candidate["distinct_gate_values"],
                baseline["distinct_gate_values"],
            )

    def test_existing_singleton_commit_rejects_conflicting_new_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass199DistributedCalibrationRuntime(state_root=root)
            try:
                first = runtime.run(
                    config_payload=ONE_CONFIG,
                    worker_count=2,
                    vm81_receipt_hash72="c" * 72,
                )
                self.assertEqual(
                    first["authority"]["vm81_receipt_hash72"],
                    "c" * 72,
                )
                Path(runtime.report_path).unlink()
                with self.assertRaisesRegex(
                    Pass199CalibrationError,
                    "different VM81 receipt",
                ):
                    runtime.run(
                        config_payload=ONE_CONFIG,
                        worker_count=2,
                        vm81_receipt_hash72="d" * 72,
                        resume=False,
                    )
                recovered = runtime.run(
                    config_payload=ONE_CONFIG,
                    worker_count=2,
                    vm81_receipt_hash72="c" * 72,
                    resume=False,
                )
                self.assertEqual(
                    recovered["authority"]["vm81_receipt_hash72"],
                    "c" * 72,
                )
                commits = [
                    receipt
                    for receipt in _all_receipts(runtime)
                    if receipt["operation_id"] == COMMIT_OPERATION_ID
                ]
                self.assertEqual(len(commits), 1)
                self.assertEqual(
                    commits[0]["arguments"]["vm81_receipt_hash72"],
                    "c" * 72,
                )
            finally:
                runtime.close()

    def test_expired_persisted_worker_slot_recovers_before_slot_validation(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass199DistributedCalibrationRuntime(state_root=root)
            try:
                prepared = runtime.prepare_tree(
                    "pass197.reciprocal_matrix_gate",
                    ONE_CONFIG,
                )
                worker_ids = ["p199.slot.00", "p199.slot.01"]
                now_ns = time.time_ns()
                ensured = runtime._invoke(
                    runtime.context,
                    ENSURE_WORKERS_OPERATION_ID,
                    {
                        "worker_ids": worker_ids,
                        "now_ns": now_ns,
                        "lease_timeout_ns": 1,
                    },
                    "worker:admin",
                ).result
                self.assertTrue(
                    ensured["stale_claim_recovery_before_slot_validation"]
                )
                claimed = runtime._invoke(
                    runtime.context,
                    BATCH_CLAIM_OPERATION_ID,
                    {
                        "workspace_id": prepared["workspace_id"],
                        "worker_ids": worker_ids,
                        "now_ns": now_ns,
                        "lease_duration_ns": 1,
                    },
                    "worker:execute",
                ).result
                self.assertTrue(claimed["claimed"])
            finally:
                runtime.close()

            time.sleep(0.001)
            reopened = Pass199DistributedCalibrationRuntime(state_root=root)
            try:
                report = reopened.run(
                    config_payload=ONE_CONFIG,
                    worker_count=2,
                    vm81_receipt_hash72="e" * 72,
                    resume=False,
                )
                self.assertTrue(report["closed"])
                self.assertEqual(
                    report["worker_fabric"]["completed_job_count"],
                    2,
                )
            finally:
                reopened.close()

    def test_resumed_worker_total_includes_jobs_completed_before_restart(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            runtime = Pass199DistributedCalibrationRuntime(state_root=root)
            try:
                prepared = runtime.prepare_tree(
                    "pass197.reciprocal_matrix_gate",
                    SMALL_CONFIG,
                )
                worker = runtime.execute_workers(prepared, worker_count=3)
                self.assertEqual(
                    worker["completed_job_count"],
                    prepared["expected_job_count"],
                )
                self.assertEqual(
                    worker["newly_completed_job_count"],
                    prepared["expected_job_count"],
                )
            finally:
                runtime.close()

            reopened = Pass199DistributedCalibrationRuntime(state_root=root)
            try:
                report = reopened.run(
                    config_payload=SMALL_CONFIG,
                    worker_count=3,
                    vm81_receipt_hash72="f" * 72,
                    resume=False,
                )
                worker = report["worker_fabric"]
                self.assertTrue(report["closed"])
                self.assertEqual(
                    worker["completed_job_count"],
                    report["summary"]["branch_job_count"],
                )
                self.assertEqual(worker["newly_completed_job_count"], 0)
                self.assertTrue(worker["durable_completion_total_reconciled"])
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
