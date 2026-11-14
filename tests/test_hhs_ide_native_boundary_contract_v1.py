"""Preservation checks for the HARMONICODE human IDE + agent harness boundary."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts/architecture/hhs_ide_native_boundary_contract_v1.json"


class TestIDENativeBoundaryContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_schema(self):
        self.assertEqual(self.spec["schema"], "HHS_IDE_NATIVE_BOUNDARY_CONTRACT_V1")
        self.assertEqual(self.spec["native_frame_bytes"], 81 * 64 // 8)

    def test_frames_not_payload_limits(self):
        self.assertIs(self.spec["frame_size_is_whole_file_limit"], False)

    def test_frontend_not_native_tensor_layout(self):
        self.assertIs(self.spec["frontend_requires_native_tensor_algorithm_for_layout"], False)

    def test_signed_admission_nonnegotiable(self):
        self.assertIs(self.spec["canonical_admission_required_for_native_mutation"], True)

    def test_each_boundary_declares_compatibility_rules(self):
        by_name = {item["name"]: item for item in self.spec["boundaries"]}
        self.assertEqual(set(by_name), {"frontend_ide", "ingress", "egress", "native_vm81", "lane5"})
        for item in by_name.values():
            self.assertTrue(item["preserve"])
            self.assertTrue(item["native_scope"])
            self.assertTrue(item["prohibit"])

    def test_existing_ide_uses_conventional_services(self):
        ide = (ROOT / "applications/holofractal_harmonizer/src/visual-ide-runtime.mjs").read_text()
        self.assertIn("requestJson(", ide)
        self.assertIn("export async function compile(", ide)
        self.assertIn("export async function run(", ide)
        self.assertIn("export function exportEgress()", ide)

    def test_ingress_is_candidate_only_and_unbounded_native(self):
        bridge = (ROOT / "hhs_python/runtime/hhs_pass219_lane5_unbounded_workload_scaling_bridge.py").read_text()
        self.assertIn("def from_chunks(", bridge)
        self.assertIn("def from_file(", bridge)
        self.assertIn('"candidate_only": bool(', bridge)
        self.assertIn('"requires_signed_environmental_vm81_admission": bool(', bridge)

    def test_guest_pty_is_not_pass190_shell(self):
        guest = (ROOT / "docs/pass220/PASS_220_I043_UBUNTU_GUEST_RUNTIME_PTY_V1.md").read_text()
        self.assertIn("authenticated SSH + PTY transport", guest)
        self.assertIn("not a general", guest)

    def test_contract_is_explicit_in_agent_instructions(self):
        agents = (ROOT / "AGENTS.md").read_text()
        self.assertIn("hhs_ide_native_boundary_contract_v1.json", agents)


if __name__ == "__main__":
    unittest.main()
