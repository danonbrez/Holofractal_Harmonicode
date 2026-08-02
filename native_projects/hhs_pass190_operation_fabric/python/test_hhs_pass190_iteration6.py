from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190 import CapabilityDeniedError, StateConflictError, hash72  # noqa: E402
from hhs_pass190_capability import issue_capability_token  # noqa: E402
from hhs_pass190_iteration2 import PersistentStoreError  # noqa: E402
from hhs_pass190_iteration6_compiler import ResourceOperationCompiler  # noqa: E402
from hhs_pass190_iteration6_registry import RESOURCE_OPERATION_IDS, ExpandedOperationRegistry  # noqa: E402
from hhs_pass190_iteration6_runtime import UnifiedResourceRegistryContext  # noqa: E402
from hhs_pass190_iteration6_server import build_server  # noqa: E402

SECRET = "pass190-iteration6-resource-secret-" + ("s" * 48)
ALL_SCOPES = {
    "workspace:write", "workspace:read", "artifact:write", "artifact:read",
    "provider:admin", "provider:read", "capability:admin", "capability:read",
    "job:write", "job:read",
}


class Iteration6Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "authority.sqlite3"
        self.context = UnifiedResourceRegistryContext(self.db, holder_id="iteration6-test")

    def tearDown(self) -> None:
        try:
            self.context.close()
        except sqlite3.ProgrammingError:
            pass
        self.temp.cleanup()

    def invoke(self, operation_id: str, arguments: dict, *scopes: str):
        return self.context.invoke(operation_id, arguments, capabilities=scopes)

    def define_scope(self, scope: str) -> None:
        self.invoke(
            "capability.define",
            {"scope": scope, "description": f"Definition for {scope}"},
            "capability:admin",
        )

    def create_workspace(self, workspace_id: str = "workspace.one"):
        return self.invoke(
            "workspace.create",
            {"workspace_id": workspace_id, "name": "Workspace One", "metadata": {"owner": "tests"}},
            "workspace:write",
        )

    def test_expanded_registry_has_exact_overlay_and_hashes(self) -> None:
        registry = ExpandedOperationRegistry()
        self.assertEqual(len(registry.records), 31)
        self.assertEqual(registry.payload["native_operation_count"], 10)
        self.assertEqual(registry.payload["governed_operation_count"], 31)
        self.assertEqual(tuple(registry.by_id)[-21:], RESOURCE_OPERATION_IDS)
        self.assertEqual(len(registry.payload["registry_hash216"]), 216)
        for operation_id in RESOURCE_OPERATION_IDS:
            self.assertEqual(len(registry.resolve(operation_id).raw["Hash216_identity"]), 216)

    def test_resource_mutations_are_capability_gated(self) -> None:
        with self.assertRaises(CapabilityDeniedError):
            self.context.invoke("workspace.create", {"workspace_id": "w", "name": "No capability"})
        admitted = self.create_workspace("workspace.gated")
        self.assertEqual(admitted.result["workspace_id"], "workspace.gated")

    def test_workspace_lifecycle_is_exact_and_sorted(self) -> None:
        self.create_workspace("workspace.z")
        self.create_workspace("workspace.a")
        updated = self.invoke(
            "workspace.update",
            {"workspace_id": "workspace.a", "name": "Updated", "metadata": {"revision": 2}},
            "workspace:write",
        )
        self.assertEqual(updated.result["version"], 2)
        self.assertEqual(updated.result["name"], "Updated")
        listed = self.invoke("workspace.list", {}, "workspace:read").result
        self.assertEqual([item["workspace_id"] for item in listed], ["workspace.a", "workspace.z"])
        archived = self.invoke(
            "workspace.archive", {"workspace_id": "workspace.a"}, "workspace:write"
        ).result
        self.assertTrue(archived["archived"])
        visible = self.invoke("workspace.list", {}, "workspace:read").result
        self.assertEqual([item["workspace_id"] for item in visible], ["workspace.z"])
        all_items = self.invoke(
            "workspace.list", {"include_archived": True}, "workspace:read"
        ).result
        self.assertEqual(len(all_items), 2)

    def test_artifacts_are_immutable_and_workspace_bound(self) -> None:
        self.create_workspace()
        content_hash = hash72("test.artifact", {"bytes": "exact"})
        artifact = self.invoke(
            "artifact.register",
            {
                "artifact_id": "artifact.one",
                "workspace_id": "workspace.one",
                "media_type": "application/json",
                "content_hash72": content_hash,
                "size_bytes": 17,
                "metadata": {"format": "exact"},
            },
            "artifact:write",
        ).result
        self.assertEqual(artifact["content_hash72"], content_hash)
        self.assertEqual(len(artifact["record_hash72"]), 72)
        with self.assertRaises(StateConflictError):
            self.invoke(
                "artifact.register",
                {
                    "artifact_id": "artifact.one",
                    "workspace_id": "workspace.one",
                    "media_type": "text/plain",
                    "content_hash72": content_hash,
                    "size_bytes": 1,
                },
                "artifact:write",
            )
        listed = self.invoke(
            "artifact.list", {"workspace_id": "workspace.one"}, "artifact:read"
        ).result
        self.assertEqual([item["artifact_id"] for item in listed], ["artifact.one"])

    def test_provider_and_job_lifecycle_preserve_constraints(self) -> None:
        self.create_workspace()
        provider = self.invoke(
            "provider.register",
            {
                "provider_id": "provider.local",
                "provider_kind": "native",
                "endpoint": "http://127.0.0.1:9000",
                "enabled": True,
            },
            "provider:admin",
        ).result
        self.assertFalse(provider["secret_material_present"])
        submitted = self.invoke(
            "job.submit",
            {
                "job_id": "job.one",
                "workspace_id": "workspace.one",
                "operation_id": "system.status",
                "arguments": {},
                "provider_id": "provider.local",
            },
            "job:write",
        ).result
        self.assertEqual(submitted["status"], "queued")
        with self.assertRaises(StateConflictError):
            self.invoke(
                "provider.set_enabled",
                {"provider_id": "provider.local", "enabled": False},
                "provider:admin",
            )
        claimed = self.invoke(
            "job.claim", {"job_id": "job.one", "worker_id": "worker.one"}, "job:write"
        ).result
        self.assertEqual(claimed["status"], "running")
        completed = self.invoke(
            "job.complete", {"job_id": "job.one", "result": {"ok": True}}, "job:write"
        ).result
        self.assertEqual(completed["status"], "completed")
        disabled = self.invoke(
            "provider.set_enabled",
            {"provider_id": "provider.local", "enabled": False},
            "provider:admin",
        ).result
        self.assertFalse(disabled["enabled"])

    def test_job_declares_defined_target_capability(self) -> None:
        self.create_workspace()
        self.define_scope("workspace:read")
        with self.assertRaises(Exception):
            self.invoke(
                "job.submit",
                {
                    "job_id": "job.missing.scope",
                    "workspace_id": "workspace.one",
                    "operation_id": "workspace.get",
                    "arguments": {"workspace_id": "workspace.one"},
                },
                "job:write",
            )
        submitted = self.invoke(
            "job.submit",
            {
                "job_id": "job.scoped",
                "workspace_id": "workspace.one",
                "operation_id": "workspace.get",
                "arguments": {"workspace_id": "workspace.one"},
                "required_capabilities": ["workspace:read"],
            },
            "job:write",
        ).result
        self.assertEqual(submitted["required_capabilities"], ["workspace:read"])
        with self.assertRaises(StateConflictError):
            self.invoke(
                "workspace.archive", {"workspace_id": "workspace.one"}, "workspace:write"
            )
        failed = self.invoke(
            "job.fail", {"job_id": "job.scoped", "error": {"code": "cancelled"}}, "job:write"
        ).result
        self.assertEqual(failed["status"], "failed")
        archived = self.invoke(
            "workspace.archive", {"workspace_id": "workspace.one"}, "workspace:write"
        ).result
        self.assertTrue(archived["archived"])

    def test_persistence_restart_and_integrity(self) -> None:
        self.create_workspace()
        before = self.context.resource_registry_report()
        self.context.close()
        self.context = UnifiedResourceRegistryContext(self.db, holder_id="iteration6-restored")
        after = self.context.resource_registry_report()
        self.assertEqual(after["counts"]["workspaces"], 1)
        self.assertEqual(after["resource_registry_hash72"], before["resource_registry_hash72"])
        integrity = self.context.integrity_report()
        self.assertTrue(integrity["resource_registry_verified"])
        self.assertEqual(integrity["governed_operation_count"], 31)
        self.assertEqual(integrity["native_operation_count"], 10)

    def test_resource_replay_does_not_mutate_state(self) -> None:
        admitted = self.create_workspace()
        state_root = self.context.state_root
        receipt_count = self.context.integrity_report()["receipt_count"]
        replayed = self.context.replay(admitted.receipt["hash72"])
        self.assertTrue(replayed.replay_verified)
        self.assertEqual(replayed.result, admitted.result)
        self.assertEqual(self.context.state_root, state_root)
        self.assertEqual(self.context.integrity_report()["receipt_count"], receipt_count)

    def test_compiler_preserves_native_and_exact_fallback(self) -> None:
        compiler = ResourceOperationCompiler()
        native = compiler.compile_instruction("Abs(-7)")
        fallback = compiler.compile_instruction("WorkspaceCreate('workspace.compiled','Compiled')")
        self.assertTrue(native.vmir["native_available"])
        self.assertFalse(fallback.vmir["native_available"])
        self.assertEqual(fallback.vmir["native_profile"], "vm81-exact-authority-fallback-v1")
        program = compiler.compile_program(
            "WorkspaceCreate('workspace.compiled','Compiled')\nWorkspaceGet('workspace.compiled')"
        )
        outputs = compiler.execute(program, self.context, capabilities={"workspace:write", "workspace:read"})
        self.assertEqual(outputs[-1]["result"]["name"], "Compiled")
        self.assertEqual(program["governed_operation_count"], 31)
        self.assertEqual(program["native_operation_count"], 10)

    def test_resource_record_tamper_is_rejected_after_valid_state_root_update(self) -> None:
        self.create_workspace()
        self.context.close()
        connection = sqlite3.connect(self.db)
        rows = dict(connection.execute("SELECT key,value_json FROM authority_meta"))
        state = json.loads(rows["state"])
        state["resource_registries"]["workspaces"]["workspace.one"]["name"] = "tampered"
        connection.execute(
            "UPDATE authority_meta SET value_json=? WHERE key='state'",
            (json.dumps(state, sort_keys=True, separators=(",", ":")),),
        )
        connection.execute(
            "UPDATE authority_meta SET value_json=? WHERE key='state_root'",
            (json.dumps(hash72("pass190.state", state)),),
        )
        connection.commit()
        connection.close()
        with self.assertRaises(PersistentStoreError):
            UnifiedResourceRegistryContext(self.db, holder_id="tamper-probe")
        self.context = UnifiedResourceRegistryContext(Path(self.temp.name) / "replacement.sqlite3")

    def test_live_server_direct_routes_registry_and_compiler(self) -> None:
        token = issue_capability_token(
            SECRET,
            principal="iteration6-client",
            scopes=ALL_SCOPES,
            ttl_seconds=300,
            now=int(time.time()),
            nonce="iteration6-live",
        )
        server = build_server(port=0, context=self.context, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            request = Request(
                base + "/api/pass190/operations/workspace.create",
                data=json.dumps({"workspace_id": "workspace.http", "name": "HTTP"}).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "HHS-Capability " + token,
                },
                method="POST",
            )
            created = json.loads(urlopen(request, timeout=5).read())
            self.assertEqual(created["result"]["workspace_id"], "workspace.http")
            report = json.loads(urlopen(base + "/api/pass190/resource-registry", timeout=5).read())
            self.assertEqual(report["counts"]["workspaces"], 1)
            compile_request = Request(
                base + "/api/pass190/compile",
                data=json.dumps({"source": "WorkspaceGet('workspace.http')"}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            compiled = json.loads(urlopen(compile_request, timeout=5).read())
            self.assertFalse(compiled["program"]["instructions"][0]["vmir"]["native_available"])
            openapi = json.loads(urlopen(base + "/openapi.json", timeout=5).read())
            self.assertEqual(openapi["x-hhs-iteration"], 6)
            self.assertEqual(openapi["x-hhs-governed-operation-count"], 31)
            self.assertIn("/api/pass190/resource-registry", openapi["paths"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.context = UnifiedResourceRegistryContext(self.db, holder_id="iteration6-after-server")

    def test_direct_protected_route_rejects_missing_token(self) -> None:
        server = build_server(port=0, context=self.context, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(
                f"http://127.0.0.1:{server.server_address[1]}/api/pass190/operations/workspace.create",
                data=json.dumps({"workspace_id": "workspace.denied", "name": "Denied"}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as caught:
                urlopen(request, timeout=5)
            self.assertEqual(caught.exception.code, 401)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.context = UnifiedResourceRegistryContext(self.db, holder_id="iteration6-after-denied")


if __name__ == "__main__":
    unittest.main(verbosity=2)
