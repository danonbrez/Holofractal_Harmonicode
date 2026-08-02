from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hhs_backend.runtime.hhs_pass196_integrated_environment_v1 import (
    Pass196IntegratedEnvironment,
)


class Pass196IntegratedEnvironmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repository"
        self.state = Path(self.temp.name) / "state"
        self.root.mkdir(parents=True)

        self._write("HHS_PASS_001_FOUNDATION.md", "# HHS PASS 001 — FOUNDATION\n")
        self._write("hhs_runtime/pass001/runtime.py", "# Pass 001 runtime\ndef run(): return 1\n")
        self._write("tests/test_pass001.py", "# pass001 test\n")

        self._write("HHS_PASS_002_CONTRACT_ONLY.md", "# HHS PASS 002 — CONTRACT ONLY\n")

        self._write("hhs_backend/runtime/pass003_runtime.py", "# HHS PASS 003\ndef run(): return 3\n")
        self._write("evidence/pass003_receipt.json", '{"pass":3,"receipt":"ok"}\n')

        # Global mandatory surface fixtures. They are deliberately distributed
        # across the repository so the scanner must join them into one matrix.
        self._write("hhs_backend/api/runtime_routes.py", "from fastapi import APIRouter\nrouter=APIRouter()\n")
        self._write("native_projects/operation_fabric/registry.json", '{"registry":true}\n')
        self._write("hhs_backend/runtime/hydration_ingest.py", "# hydration ingest\n")
        self._write("hhs_runtime/vector_memristor_store.py", "class PersistentEncryptedVectorStore: pass\n")
        self._write("deploy/digitalocean/hhs.service", "[Service]\nExecStart=/usr/bin/python\n")
        self._write("hhs_runtime/hhs_service_registry_v1.py", "class HHSServiceRegistry: pass\n")
        self._write("applications/holofractal_harmonizer/index.html", "<html><title>Visual IDE</title></html>\n")
        self._write(".github/workflows/validate.yml", "name: validate\n")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_parallel_scan_serializes_pass_matrix_and_encrypted_vector(self) -> None:
        engine = Pass196IntegratedEnvironment(
            self.root,
            state_root=self.state,
            workers=4,
        )
        first = engine.scan(
            vm81_receipt_hash72="a" * 72,
            persist_vector=True,
        )
        manifest = first["manifest"]
        by_pass = {item["pass_number"]: item for item in manifest["pass_matrix"]}

        self.assertEqual(by_pass[1]["state"], "INTEGRATED")
        self.assertEqual(by_pass[2]["state"], "CONTRACT_ONLY")
        self.assertEqual(by_pass[3]["state"], "INTEGRATED")
        self.assertTrue(manifest["surface_matrix"]["complete"])
        self.assertTrue(first["operational"])
        self.assertFalse(first["integration_closed"])
        self.assertFalse(first["ok"])
        self.assertTrue(first["vector"]["persisted"])
        self.assertEqual(first["vector"]["authenticated_encryption"], "AES_GCM")
        self.assertEqual(first["vector"]["snapshot_bytes"], 648)
        self.assertFalse(first["vector"]["plaintext_manifest_persisted"])

        database_bytes = self.state.joinpath("integrated_vectors.sqlite3").read_bytes()
        self.assertNotIn(b"HHS_PASS_002_CONTRACT_ONLY.md", database_bytes)

        second = engine.scan(
            vm81_receipt_hash72="a" * 72,
            persist_vector=False,
        )
        self.assertEqual(first["manifest_hash72"], second["manifest_hash72"])
        self.assertEqual(first["manifest_hash216"], second["manifest_hash216"])

    def test_gap_and_tool_reports_are_explicit(self) -> None:
        engine = Pass196IntegratedEnvironment(
            self.root,
            state_root=self.state,
            workers=2,
        )
        engine.scan(persist_vector=False)
        gaps = engine.gaps()
        self.assertFalse(gaps["complete"])
        self.assertEqual(gaps["unresolved_pass_count"], 1)
        self.assertEqual(gaps["unresolved_passes"][0]["pass_number"], 2)

        tools = engine.tools()
        self.assertEqual(len(tools["tools"]), 4)
        self.assertFalse(tools["tool_server_is_authority"])
        self.assertTrue(tools["mutation_requires_vm81_authorized_tick"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
