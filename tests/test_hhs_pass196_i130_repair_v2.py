from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hhs_backend.api.pass196_integration_routes import _strict_persist_vector
from hhs_backend.runtime.hhs_pass196_integrated_environment_v1 import Pass196Error
from hhs_backend.runtime.hhs_pass196_integrated_environment_v2 import (
    Pass196IntegratedEnvironmentV2,
    _observe_exact,
)


class Pass196I130RepairTests(unittest.TestCase):
    def _repository(self, parent: Path, name: str = "repo") -> Path:
        root = parent / name
        root.mkdir(parents=True)
        files = {
            "HHS_PASS_001_FOUNDATION.md": "# HHS PASS 001 — FOUNDATION\n",
            "hhs_runtime/pass001/runtime.py": "# Pass 001 runtime\ndef run(): return 1\n",
            "tests/test_pass001.py": "# pass001 test\n",
            "hhs_backend/api/runtime_routes.py": "from fastapi import APIRouter\nrouter=APIRouter()\n",
            "native_projects/operation_fabric/registry.json": '{"registry":true}\n',
            "hhs_backend/runtime/hydration_ingest.py": "# hydration ingest\n",
            "hhs_runtime/vector_memristor_store.py": "class PersistentEncryptedVectorStore: pass\n",
            "deploy/digitalocean/hhs.service": "[Service]\nExecStart=/usr/bin/python\n",
            "hhs_runtime/hhs_service_registry_v1.py": "class HHSServiceRegistry: pass\n",
            "applications/holofractal_harmonizer/index.html": "<html><title>Visual IDE</title></html>\n",
            ".github/workflows/validate.yml": "name: validate\n",
        }
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    def test_01_persistent_vector_requires_vm81_hash72_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = self._repository(parent)
            engine = Pass196IntegratedEnvironmentV2(root, state_root=parent / "state", workers=1)
            with self.assertRaisesRegex(Pass196Error, "PASS196_VM81_HASH72_RECEIPT_REQUIRED_FOR_PERSISTENCE"):
                engine.scan(persist_vector=True)
            status = engine.status()
            self.assertEqual(status["phase"], "QUARANTINED")
            self.assertFalse(status["ok"])
            self.assertFalse(status["integration_closed"])

    def test_02_restart_restores_vector_parent_and_predecessor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = self._repository(parent)
            state = parent / "state"
            first_engine = Pass196IntegratedEnvironmentV2(root, state_root=state, workers=1)
            first = first_engine.scan(vm81_receipt_hash72="a" * 72, persist_vector=True)
            first_object = first["vector"]["vector_object_id"]
            first_manifest = first["manifest_hash72"]

            second_engine = Pass196IntegratedEnvironmentV2(root, state_root=state, workers=3)
            second = second_engine.scan(vm81_receipt_hash72="b" * 72, persist_vector=True)
            self.assertEqual(second["vector"]["parent_object_id"], first_object)
            self.assertEqual(second["vector"]["input_hash72"], first_manifest)
            self.assertNotEqual(second["vector"]["vector_object_id"], first_object)

    def test_03_test_only_runtime_named_file_is_not_executable_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            path = root / "tests/test_pass007_runtime.py"
            path.parent.mkdir(parents=True)
            path.write_text("# pass 007 runtime test only\n", encoding="utf-8")
            engine = Pass196IntegratedEnvironmentV2(root, state_root=Path(tmp) / "state", workers=1)
            status = engine.scan(persist_vector=False)
            by_pass = {row["pass_number"]: row for row in status["manifest"]["pass_matrix"]}
            self.assertNotEqual(by_pass[7]["state"], "INTEGRATED")
            self.assertEqual(by_pass[7]["executable_artifacts"], [])

    def test_04_manifest_identity_is_host_and_worker_independent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            left = self._repository(parent, "left")
            right = self._repository(parent, "right")
            one = Pass196IntegratedEnvironmentV2(left, state_root=parent / "s1", workers=1).scan(
                vm81_receipt_hash72="c" * 72, persist_vector=False
            )
            four = Pass196IntegratedEnvironmentV2(right, state_root=parent / "s2", workers=4).scan(
                vm81_receipt_hash72="d" * 72, persist_vector=False
            )
            self.assertEqual(one["manifest_hash72"], four["manifest_hash72"])
            self.assertEqual(one["manifest_hash216"], four["manifest_hash216"])
            self.assertNotEqual(
                one["manifest"]["observation_diagnostics"]["repository_root"],
                four["manifest"]["observation_diagnostics"]["repository_root"],
            )
            self.assertNotEqual(
                one["manifest"]["observation_diagnostics"]["parallel_worker_count"],
                four["manifest"]["observation_diagnostics"]["parallel_worker_count"],
            )

    def test_05_observation_classifies_the_same_bytes_that_are_hashed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            path = root / "hhs_runtime/pass001/runtime.py"
            path.parent.mkdir(parents=True)
            path.write_text("# HHS PASS 001\ndef run(): return 1\n", encoding="utf-8")
            with patch.object(Path, "read_text", side_effect=AssertionError("second text read forbidden")):
                observed = _observe_exact(root, path)
            self.assertEqual(observed["primary_pass"], 1)
            self.assertIn("runtime", observed["surfaces"])
            self.assertTrue(observed["text_scanned"])

    def test_06_failed_rescan_quarantines_stale_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = self._repository(parent)
            engine = Pass196IntegratedEnvironmentV2(root, state_root=parent / "state", workers=1)
            first = engine.scan(persist_vector=False)
            first_hash = first["manifest_hash72"]
            with patch(
                "hhs_backend.runtime.hhs_pass196_integrated_environment_v2._files",
                side_effect=OSError("injected observation failure"),
            ):
                with self.assertRaises(OSError):
                    engine.scan(persist_vector=False)
            status = engine.status()
            self.assertEqual(status["phase"], "QUARANTINED")
            self.assertFalse(status["ok"])
            self.assertFalse(status["integration_closed"])
            self.assertFalse(status["operational"])
            self.assertEqual(status["last_good_manifest_hash72"], first_hash)
            self.assertTrue(status["last_good_is_historical_only"])
            with self.assertRaisesRegex(Pass196Error, "PASS196_CURRENT_MANIFEST_QUARANTINED"):
                engine.manifest()

    def test_07_tool_persist_vector_is_strict_boolean(self) -> None:
        self.assertTrue(_strict_persist_vector({}))
        self.assertTrue(_strict_persist_vector({"persist_vector": True}))
        self.assertFalse(_strict_persist_vector({"persist_vector": False}))
        for invalid in ("false", "true", 0, 1, None, [], {}):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(Pass196Error, "PASS196_PERSIST_VECTOR_STRICT_BOOL_REQUIRED"):
                    _strict_persist_vector({"persist_vector": invalid})

    def test_08_tool_registry_publishes_boolean_argument_schema(self) -> None:
        tools = Pass196IntegratedEnvironmentV2.tools()
        schema = tools["tool_arguments"]["integration.scan"]["persist_vector"]
        self.assertEqual(schema, {"type": "boolean", "default": True})
        self.assertFalse(tools["tool_server_is_authority"])
        self.assertTrue(tools["mutation_requires_vm81_authorized_tick"])

    def test_09_current_service_preserves_state_directory_and_topology(self) -> None:
        service = Path("deploy/digitalocean/hhs-pass196-integrated-environment.service").read_text(
            encoding="utf-8"
        )
        self.assertIn("StateDirectory=hhs", service)
        self.assertIn("WorkingDirectory=/opt/hhs/app", service)
        self.assertIn("HHS_PASS196_STATE_ROOT=/var/lib/hhs/pass196", service)
        self.assertIn("--host 127.0.0.1 --port 8080 --workers 1", service)

    def test_10_v1_remains_historical_provenance(self) -> None:
        v1 = Path("hhs_backend/runtime/hhs_pass196_integrated_environment_v1.py").read_bytes()
        import hashlib

        blob = hashlib.sha1(f"blob {len(v1)}\0".encode("ascii") + v1).hexdigest()
        self.assertEqual(blob, "d2cff008db58a29bf27be20cb3547b9e0018f5e1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
