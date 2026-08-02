from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "worker"))

from hhs_pass190 import ArgumentValidationError, StateConflictError, hash72  # noqa: E402
from hhs_pass190_capability import issue_capability_token  # noqa: E402
from hhs_pass190_iteration2 import PersistentStoreError  # noqa: E402
from hhs_pass190_iteration7 import DurableExecutionContext  # noqa: E402
from hhs_pass190_iteration7_compiler import DurableExecutionCompiler  # noqa: E402
from hhs_pass190_iteration7_registry import EXECUTION_OPERATION_IDS, Iteration7OperationRegistry  # noqa: E402
from hhs_pass190_iteration7_server import build_server  # noqa: E402
from hhs_pass190_iteration7_worker import DurableWorker  # noqa: E402

SECRET = "pass190-iteration7-worker-secret-" + ("w" * 48)
CONTROL = {"worker:admin", "worker:read", "worker:execute", "scheduler:write"}
ALL_SCOPES = CONTROL | {
    "workspace:write", "workspace:read", "artifact:write", "artifact:read",
    "provider:admin", "provider:read", "capability:admin", "capability:read",
    "job:write", "job:read",
}


class Iteration7Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "authority.sqlite3"
        self.context = DurableExecutionContext(self.db, holder_id="iteration7-test")

    def tearDown(self) -> None:
        try:
            self.context.close()
        except sqlite3.ProgrammingError:
            pass
        self.temp.cleanup()

    def invoke(self, operation_id: str, arguments: dict, *scopes: str):
        return self.context.invoke(operation_id, arguments, capabilities=scopes)

    def create_workspace(self, workspace_id: str = "workspace.one") -> None:
        self.invoke("workspace.create", {"workspace_id": workspace_id, "name": workspace_id}, "workspace:write")

    def define_scope(self, scope: str) -> None:
        self.invoke(
            "capability.define", {"scope": scope, "description": f"Definition for {scope}"},
            "capability:admin",
        )

    def register_worker(self, worker_id: str = "worker.one", capabilities: list[str] | None = None, now_ns: int = 100, lease_timeout_ns: int = 1000):
        return self.invoke(
            "worker.register",
            {
                "worker_id": worker_id,
                "capabilities": capabilities or [],
                "labels": ["test"],
                "lease_timeout_ns": lease_timeout_ns,
                "now_ns": now_ns,
            },
            "worker:admin",
        ).result

    def submit_abs(self, job_id: str, *, now_ns: int = 100, priority: int = 0, max_attempts: int = 3, dependencies: list[str] | None = None):
        return self.invoke(
            "job.submit_execution",
            {
                "job_id": job_id,
                "workspace_id": "workspace.one",
                "operation_id": "python.abs",
                "arguments": {"value": -7},
                "dependency_job_ids": dependencies or [],
                "submitted_at_ns": now_ns,
                "priority": priority,
                "max_attempts": max_attempts,
            },
            "job:write",
        ).result

    def test_registry_adds_exact_execution_overlay(self) -> None:
        registry = Iteration7OperationRegistry()
        self.assertEqual(len(registry.records), 42)
        self.assertEqual(registry.payload["native_operation_count"], 10)
        self.assertEqual(registry.payload["execution_operation_count"], 11)
        self.assertEqual(tuple(registry.by_id)[-11:], EXECUTION_OPERATION_IDS)
        self.assertEqual(len(registry.payload["registry_hash216"]), 216)
        for operation_id in EXECUTION_OPERATION_IDS:
            self.assertEqual(len(registry.resolve(operation_id).raw["Hash216_identity"]), 216)

    def test_worker_registry_requires_defined_target_capabilities(self) -> None:
        with self.assertRaises(ArgumentValidationError):
            self.register_worker(capabilities=["workspace:read"])
        self.define_scope("workspace:read")
        worker = self.register_worker(capabilities=["workspace:read"])
        self.assertEqual(worker["capabilities"], ["workspace:read"])
        self.assertEqual(len(worker["record_hash72"]), 72)
        listed = self.invoke("worker.list", {}, "worker:read").result
        self.assertEqual([item["worker_id"] for item in listed], ["worker.one"])

    def test_submit_execution_preserves_dependencies_and_schedule(self) -> None:
        self.create_workspace()
        first = self.submit_abs("job.first", now_ns=100)
        second = self.submit_abs("job.second", now_ns=100, dependencies=["job.first"])
        self.assertEqual(first["status"], "queued")
        self.assertEqual(second["status"], "scheduled")
        self.assertEqual(second["dependency_job_ids"], ["job.first"])
        self.assertEqual(len(second["execution_request_hash72"]), 72)
        with self.assertRaises(StateConflictError):
            self.invoke("workspace.archive", {"workspace_id": "workspace.one"}, "workspace:write")

    def test_claim_is_priority_ordered_and_execution_is_receipt_bound(self) -> None:
        self.create_workspace()
        self.register_worker()
        self.submit_abs("job.low", priority=1)
        self.submit_abs("job.high", priority=10)
        claim = self.invoke(
            "job.claim_next", {"worker_id": "worker.one", "now_ns": 100}, "worker:execute"
        ).result
        self.assertTrue(claim["claimed"])
        self.assertEqual(claim["job"]["job_id"], "job.high")
        execution = self.invoke(
            "job.execute_claimed",
            {
                "job_id": "job.high",
                "worker_id": "worker.one",
                "claim_token_hash72": claim["claim_token_hash72"],
                "now_ns": 100,
            },
            "worker:execute",
        )
        self.assertTrue(execution.result["executed"])
        self.assertEqual(execution.result["target_result"], 7)
        self.assertEqual(execution.result["job"]["status"], "completed")
        self.assertEqual(len(execution.result["execution_hash72"]), 72)
        replayed = self.context.replay(execution.receipt["hash72"])
        self.assertTrue(replayed.replay_verified)
        self.assertEqual(replayed.result, execution.result)

    def test_worker_capability_coverage_controls_claim(self) -> None:
        self.create_workspace()
        self.define_scope("workspace:read")
        self.register_worker("worker.public")
        self.register_worker("worker.scoped", ["workspace:read"])
        self.invoke(
            "job.submit_execution",
            {
                "job_id": "job.scoped",
                "workspace_id": "workspace.one",
                "operation_id": "workspace.get",
                "arguments": {"workspace_id": "workspace.one"},
                "required_capabilities": ["workspace:read"],
                "submitted_at_ns": 100,
            },
            "job:write",
        )
        none = self.invoke(
            "job.claim_next", {"worker_id": "worker.public", "now_ns": 100}, "worker:execute"
        ).result
        self.assertFalse(none["claimed"])
        claimed = self.invoke(
            "job.claim_next", {"worker_id": "worker.scoped", "now_ns": 100}, "worker:execute"
        ).result
        self.assertEqual(claimed["job"]["job_id"], "job.scoped")

    def test_scheduler_releases_dependency_after_completion(self) -> None:
        self.create_workspace()
        self.register_worker()
        self.submit_abs("job.parent")
        self.submit_abs("job.child", dependencies=["job.parent"])
        claim = self.invoke("job.claim_next", {"worker_id": "worker.one", "now_ns": 100}, "worker:execute").result
        self.invoke(
            "job.execute_claimed",
            {"job_id": "job.parent", "worker_id": "worker.one", "claim_token_hash72": claim["claim_token_hash72"], "now_ns": 100},
            "worker:execute",
        )
        tick = self.invoke("scheduler.tick", {"now_ns": 101}, "scheduler:write").result
        self.assertIn("job.child", tick["changed_job_ids"])
        child = self.invoke("job.get", {"job_id": "job.child"}, "job:read").result
        self.assertEqual(child["status"], "queued")

    def test_failed_execution_retries_then_exhausts_budget(self) -> None:
        self.create_workspace()
        self.register_worker(lease_timeout_ns=1000)
        self.invoke(
            "job.submit_execution",
            {
                "job_id": "job.failure",
                "workspace_id": "workspace.one",
                "operation_id": "python.sorted",
                "arguments": {"values": [1, "incomparable"]},
                "submitted_at_ns": 100,
                "max_attempts": 2,
                "retry_backoff_ns": 10,
            },
            "job:write",
        )
        claim1 = self.invoke("job.claim_next", {"worker_id": "worker.one", "now_ns": 100}, "worker:execute").result
        failed1 = self.invoke(
            "job.execute_claimed",
            {"job_id": "job.failure", "worker_id": "worker.one", "claim_token_hash72": claim1["claim_token_hash72"], "now_ns": 100},
            "worker:execute",
        ).result
        self.assertFalse(failed1["executed"])
        self.assertEqual(failed1["job"]["status"], "retry_wait")
        self.invoke("worker.heartbeat", {"worker_id": "worker.one", "now_ns": 110}, "worker:execute")
        self.invoke("scheduler.tick", {"now_ns": 110}, "scheduler:write")
        claim2 = self.invoke("job.claim_next", {"worker_id": "worker.one", "now_ns": 110}, "worker:execute").result
        failed2 = self.invoke(
            "job.execute_claimed",
            {"job_id": "job.failure", "worker_id": "worker.one", "claim_token_hash72": claim2["claim_token_hash72"], "now_ns": 110},
            "worker:execute",
        ).result
        self.assertEqual(failed2["job"]["status"], "failed")
        self.assertEqual(failed2["job"]["attempt"], 2)

    def test_cancellation_releases_running_worker(self) -> None:
        self.create_workspace()
        self.register_worker()
        self.submit_abs("job.cancel")
        self.invoke("job.claim_next", {"worker_id": "worker.one", "now_ns": 100}, "worker:execute")
        cancelled = self.invoke(
            "job.cancel", {"job_id": "job.cancel", "reason": {"operator": True}, "now_ns": 101}, "job:write"
        ).result
        self.assertEqual(cancelled["status"], "cancelled")
        worker = self.invoke("worker.get", {"worker_id": "worker.one"}, "worker:read").result
        self.assertIsNone(worker["current_job_id"])

    def test_stale_worker_lease_is_recovered_by_scheduler(self) -> None:
        self.create_workspace()
        self.register_worker(lease_timeout_ns=10)
        self.submit_abs("job.stale", max_attempts=2)
        self.invoke(
            "job.claim_next", {"worker_id": "worker.one", "now_ns": 100, "lease_duration_ns": 10},
            "worker:execute",
        )
        tick = self.invoke("scheduler.tick", {"now_ns": 110}, "scheduler:write").result
        self.assertIn("job.stale", tick["changed_job_ids"])
        job = self.invoke("job.get", {"job_id": "job.stale"}, "job:read").result
        self.assertEqual(job["status"], "queued")
        self.assertIsNone(job["worker_id"])

    def test_terminal_dependency_fails_child(self) -> None:
        self.create_workspace()
        self.register_worker()
        self.invoke(
            "job.submit_execution",
            {
                "job_id": "job.parent",
                "workspace_id": "workspace.one",
                "operation_id": "python.sorted",
                "arguments": {"values": [1, "x"]},
                "submitted_at_ns": 100,
                "max_attempts": 1,
            },
            "job:write",
        )
        self.submit_abs("job.child", dependencies=["job.parent"])
        claim = self.invoke("job.claim_next", {"worker_id": "worker.one", "now_ns": 100}, "worker:execute").result
        self.invoke(
            "job.execute_claimed",
            {"job_id": "job.parent", "worker_id": "worker.one", "claim_token_hash72": claim["claim_token_hash72"], "now_ns": 100},
            "worker:execute",
        )
        self.invoke("scheduler.tick", {"now_ns": 101}, "scheduler:write")
        child = self.invoke("job.get", {"job_id": "job.child"}, "job:read").result
        self.assertEqual(child["status"], "failed")
        self.assertEqual(child["error"]["type"], "dependency_terminal")

    def test_persistence_restart_and_worker_tamper_rejection(self) -> None:
        self.create_workspace()
        self.register_worker()
        before = self.context.execution_runtime_report()
        self.context.close()
        self.context = DurableExecutionContext(self.db, holder_id="iteration7-restored")
        after = self.context.execution_runtime_report()
        self.assertEqual(after["worker_count"], 1)
        self.assertEqual(after["execution_runtime_hash72"], before["execution_runtime_hash72"])
        self.context.close()
        connection = sqlite3.connect(self.db)
        rows = dict(connection.execute("SELECT key,value_json FROM authority_meta"))
        state = json.loads(rows["state"])
        state["execution_runtime"]["workers"]["worker.one"]["labels"] = ["tampered"]
        connection.execute("UPDATE authority_meta SET value_json=? WHERE key='state'", (json.dumps(state, sort_keys=True, separators=(",", ":")),))
        connection.execute("UPDATE authority_meta SET value_json=? WHERE key='state_root'", (json.dumps(hash72("pass190.state", state)),))
        connection.commit()
        connection.close()
        with self.assertRaises(PersistentStoreError):
            DurableExecutionContext(self.db, holder_id="iteration7-tamper")
        self.context = DurableExecutionContext(Path(self.temp.name) / "replacement.sqlite3")

    def test_compiler_and_worker_process_execute_fallback(self) -> None:
        compiler = DurableExecutionCompiler()
        instruction = compiler.compile_instruction("WorkerList()")
        self.assertFalse(instruction.vmir["native_available"])
        program = compiler.compile_program("WorkerList()")
        self.assertEqual(program["governed_operation_count"], 42)
        self.assertEqual(program["execution_operation_count"], 11)
        self.create_workspace()
        self.submit_abs("job.worker")
        worker = DurableWorker(self.context, "worker.process", clock_ns=lambda: 100)
        result = worker.run_once(100)
        self.assertTrue(result["execution"]["executed"])
        self.assertEqual(result["execution"]["job"]["status"], "completed")

    def test_live_server_projects_execution_runtime(self) -> None:
        token = issue_capability_token(
            SECRET, principal="iteration7-client", scopes=ALL_SCOPES,
            ttl_seconds=300, now=int(time.time()), nonce="iteration7-live",
        )
        server = build_server(port=0, context=self.context, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            request = Request(
                base + "/api/pass190/operations/worker.register",
                data=json.dumps({"worker_id": "worker.http", "now_ns": 100}).encode(),
                headers={"Content-Type": "application/json", "Authorization": "HHS-Capability " + token},
                method="POST",
            )
            registered = json.loads(urlopen(request, timeout=5).read())
            self.assertEqual(registered["result"]["worker_id"], "worker.http")
            report = json.loads(urlopen(base + "/api/pass190/execution-runtime", timeout=5).read())
            self.assertEqual(report["worker_count"], 1)
            self.assertEqual(report["governed_operation_count"], 42)
            openapi = json.loads(urlopen(base + "/openapi.json", timeout=5).read())
            self.assertEqual(openapi["x-hhs-iteration"], 7)
            self.assertIn("/api/pass190/execution-runtime", openapi["paths"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.context = DurableExecutionContext(self.db, holder_id="iteration7-after-server")


if __name__ == "__main__":
    unittest.main(verbosity=2)
