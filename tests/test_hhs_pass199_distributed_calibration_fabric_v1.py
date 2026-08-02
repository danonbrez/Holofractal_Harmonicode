from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    BRANCH_OPERATION_ID,
    COMMIT_OPERATION_ID,
    COMPLETE_OPERATION_ID,
    PASS199_OPERATION_IDS,
    Pass199DurableCalibrationContext,
    Pass199OperationRegistry,
    StateConflictError,
    evaluate_branch_candidate,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v1 import (
    Pass199DistributedCalibrationRuntime,
)

SMALL_CONFIG = {
    "x_values": ["-1", "0", "1"],
    "y_values": ["-1", "1"],
    "xy_symbol_values": [0],
    "include_domain_rejections": True,
    "full_replay": True,
}


class Pass199DistributedCalibrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "pass199"
        self.runtime = Pass199DistributedCalibrationRuntime(state_root=self.root)

    def tearDown(self) -> None:
        try:
            self.runtime.close()
        finally:
            self.temp.cleanup()

    def test_registry_extends_verified_pass190_surface(self) -> None:
        registry = Pass199OperationRegistry()
        self.assertEqual(tuple(record.operation_id for record in registry.records[-3:]), PASS199_OPERATION_IDS)
        self.assertEqual(len(registry.records), 45)
        self.assertEqual(registry.resolve(BRANCH_OPERATION_ID).effect_class, "pure")
        self.assertEqual(registry.resolve(COMPLETE_OPERATION_ID).effect_class, "mutation")
        self.assertEqual(registry.resolve(COMMIT_OPERATION_ID).effect_class, "mutation")
        self.assertEqual(registry.payload["distributed_calibration_operation_count"], 3)

    def test_small_tree_runs_through_durable_workers_and_singleton_commit(self) -> None:
        report = self.runtime.run(
            config_payload=SMALL_CONFIG,
            worker_count=4,
            vm81_receipt_hash72="7" * 72,
        )
        self.assertTrue(report["closed"])
        self.assertEqual(report["summary"]["evaluated_parameter_states"], 6)
        self.assertEqual(report["summary"]["admitted_parameter_states"], 4)
        self.assertEqual(report["summary"]["domain_rejected_parameter_states"], 2)
        self.assertEqual(report["summary"]["branch_job_count"], 12)
        self.assertEqual(report["summary"]["address_comparisons"], 4 * 5184)
        self.assertEqual(report["singleton_commit"]["canonical_commit_operation_count"], 1)
        self.assertTrue(report["singleton_commit"]["receipt_verified"])
        self.assertTrue(report["replay"]["deterministic"])
        self.assertGreaterEqual(report["worker_fabric"]["peak_parallel_candidate_workers"], 1)
        self.assertEqual(len(self.runtime.pass198.list_simplifications()), 4)

    def test_resume_returns_same_report_without_second_commit(self) -> None:
        first = self.runtime.run(config_payload=SMALL_CONFIG, worker_count=3, vm81_receipt_hash72="8" * 72)
        second = self.runtime.run(config_payload=SMALL_CONFIG, worker_count=3, vm81_receipt_hash72="8" * 72, resume=True)
        self.assertEqual(second["report_hash72"], first["report_hash72"])
        receipts = self.runtime.context.receipts_after(0, 100_000)
        commits = [item for item in receipts if item["operation_id"] == COMMIT_OPERATION_ID]
        self.assertEqual(len(commits), 1)

    def test_prepared_jobs_survive_context_restart(self) -> None:
        prepared = self.runtime.prepare_tree("pass197.reciprocal_matrix_gate", SMALL_CONFIG)
        database = self.runtime.database_path
        self.runtime.context.close()
        self.runtime.context = Pass199DurableCalibrationContext(database, holder_id="pass199-reopened")
        jobs = self.runtime.context.invoke(
            "job.list", {"workspace_id": prepared["workspace_id"]}, capabilities=("job:read",)
        ).result
        self.assertEqual(len(jobs), prepared["expected_job_count"])
        report = self.runtime.run(config_payload=SMALL_CONFIG, worker_count=2, vm81_receipt_hash72="9" * 72)
        self.assertTrue(report["closed"])

    def test_cancel_retry_does_not_change_deterministic_tree_root(self) -> None:
        prepared = self.runtime.prepare_tree("pass197.reciprocal_matrix_gate", SMALL_CONFIG)
        jobs = self.runtime.context.invoke(
            "job.list", {"workspace_id": prepared["workspace_id"]}, capabilities=("job:read",)
        ).result
        self.runtime.cancel_and_retry(jobs[0]["job_id"])
        recovered = self.runtime.run(config_payload=SMALL_CONFIG, worker_count=3, vm81_receipt_hash72="a" * 72)

        other_root = Path(self.temp.name) / "clean"
        clean = Pass199DistributedCalibrationRuntime(state_root=other_root)
        try:
            baseline = clean.run(config_payload=SMALL_CONFIG, worker_count=3, vm81_receipt_hash72="b" * 72)
        finally:
            clean.close()
        self.assertEqual(recovered["state_root_hash72"], baseline["state_root_hash72"])

    def test_stale_worker_claim_recovers_without_root_change(self) -> None:
        prepared = self.runtime.prepare_tree("pass197.reciprocal_matrix_gate", SMALL_CONFIG)
        jobs = self.runtime.context.invoke(
            "job.list", {"workspace_id": prepared["workspace_id"]}, capabilities=("job:read",)
        ).result
        recovery = self.runtime.recover_stale_claim(jobs[0]["job_id"])
        self.assertIn(recovery["recovered"]["status"], {"queued", "retry_wait"})
        report = self.runtime.run(config_payload=SMALL_CONFIG, worker_count=3, vm81_receipt_hash72="c" * 72)
        self.assertTrue(report["closed"])

    def test_tampered_candidate_is_rejected_before_completion(self) -> None:
        prepared = self.runtime.prepare_tree(
            "pass197.reciprocal_matrix_gate",
            {"x_values": ["1"], "y_values": ["1"], "xy_symbol_values": [0]},
        )
        now = 100
        self.runtime._ensure_worker("p199.worker.tamper", now)
        claim = self.runtime.context.invoke(
            "job.claim_next",
            {
                "worker_id": "p199.worker.tamper",
                "workspace_id": prepared["workspace_id"],
                "now_ns": now,
                "lease_duration_ns": 1000,
            },
            capabilities=("worker:execute",),
        ).result
        candidate = evaluate_branch_candidate(claim["job"]["arguments"])
        candidate["cell_value_hashes"][0] = "0" * 72
        with self.assertRaises(StateConflictError):
            self.runtime.context.invoke(
                COMPLETE_OPERATION_ID,
                {
                    "job_id": claim["job"]["job_id"],
                    "worker_id": "p199.worker.tamper",
                    "claim_token_hash72": claim["claim_token_hash72"],
                    "candidate_result": candidate,
                    "now_ns": now + 1,
                },
                capabilities=("worker:execute",),
            )

    def test_direct_authority_execution_of_calibration_job_is_blocked(self) -> None:
        prepared = self.runtime.prepare_tree(
            "pass197.reciprocal_matrix_gate",
            {"x_values": ["1"], "y_values": ["1"], "xy_symbol_values": [0]},
        )
        self.runtime._ensure_worker("p199.worker.direct", 100)
        claim = self.runtime.context.invoke(
            "job.claim_next",
            {
                "worker_id": "p199.worker.direct",
                "workspace_id": prepared["workspace_id"],
                "now_ns": 100,
            },
            capabilities=("worker:execute",),
        ).result
        with self.assertRaises(StateConflictError):
            self.runtime.context.invoke(
                "job.execute_claimed",
                {
                    "job_id": claim["job"]["job_id"],
                    "worker_id": "p199.worker.direct",
                    "claim_token_hash72": claim["claim_token_hash72"],
                    "now_ns": 101,
                },
                capabilities=("worker:execute",),
            )


if __name__ == "__main__":
    unittest.main()
