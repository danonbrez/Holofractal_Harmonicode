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

    def test_cumulative_mergeability_contract_is_prioritized_and_evidential(self):
        checklist_path = ROOT / self.spec["mergeability_checklist"]
        self.assertTrue(checklist_path.exists())
        checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
        self.assertEqual(checklist["schema"], "HHS_GBRAIN_HARNESS_CUMULATIVE_MERGEABILITY_CHECKLIST_V1")
        self.assertEqual([phase["id"] for phase in checklist["phases"]], self.spec["mergeability_phase_order"])
        self.assertEqual([phase["priority"] for phase in checklist["phases"]], list(range(9)))
        self.assertEqual(checklist["phases"][0]["id"], "P0")
        self.assertEqual(checklist["phases"][1]["depends_on"], ["P0"])
        security = checklist["phases"][-1]
        self.assertEqual(security["id"], "P8")
        self.assertIs(security["not_priority_override"], True)
        self.assertEqual(self.spec["supply_chain_merge_gate"]["clearance_status"], "OPEN")
        self.assertIn("P6.4", security["mandatory_before"])
        self.assertIn("production_deployment", security["mandatory_before"])
        forensic_items = [item for section in security["sections"] for item in section["items"]]
        self.assertEqual(len(forensic_items), 20)
        self.assertTrue(all(item["state"] == "OPEN" and item["evidence"] == [] for item in forensic_items))

        self.assertIn("GBrain", checklist["phases"][0]["title"])
        self.assertIn("OPEN", checklist["completion_states"])
        self.assertIn("signed_vm81_receipts", checklist["evidence_fields"])
        self.assertIn("deployment_sha_and_runtime_receipts", checklist["evidence_fields"])
        all_ids = [item["id"] for phase in checklist["phases"] for item in phase["items"]]
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertGreaterEqual(len(all_ids), 25)
        for phase in checklist["phases"]:
            for item in phase["items"]:
                self.assertEqual(item["state"], "OPEN")
                self.assertEqual(item["evidence"], [])
                self.assertTrue(item["requirement"])
        text = checklist_path.read_text(encoding="utf-8")
        for pr in ("#691", "#803", "#909", "#911", "#912", "#916", "#908", "#913", "#914", "#915", "#917", "#918"):
            self.assertIn(pr, text)

    def test_contract_is_explicit_in_agent_instructions(self):
        agents = (ROOT / "AGENTS.md").read_text()
        self.assertIn("hhs_ide_native_boundary_contract_v1.json", agents)


if __name__ == "__main__":
    unittest.main()
