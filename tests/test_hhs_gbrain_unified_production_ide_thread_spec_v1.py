"""Structural regression for cumulative GBrain production IDE requirements (PR #914)."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "contracts/architecture/HHS_GBRAIN_UNIFIED_PRODUCTION_IDE_THREAD_SPEC_V1.json"


class TestUnifiedIDEThreadSpecification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))

    def test_identity_and_branch_scope(self):
        s = self.spec
        self.assertEqual(s["schema"], "HHS_GBRAIN_UNIFIED_PRODUCTION_IDE_THREAD_SPEC_V1")
        self.assertEqual(s["pull_request"], 914)
        self.assertEqual(s["merge_target"], "main")
        self.assertIn("OPEN", s["status"])

    def test_all_workspaces_are_included(self):
        workspaces = {w["id"]: w for w in self.spec["workspaces"]}
        self.assertEqual(set(workspaces), {"ide", "audio", "particle", "gbrain", "game", "graphics"})
        self.assertTrue(all(w["requirements"] for w in workspaces.values()))
        self.assertIn("VST3", " ".join(workspaces["audio"]["requirements"]))
        self.assertIn("10,368", " ".join(workspaces["particle"]["requirements"]))
        self.assertIn("Storybook Reel", " ".join(workspaces["game"]["requirements"]))

    def test_complete_template_lifecycle_and_authority(self):
        s = self.spec
        self.assertEqual(s["end_to_end_lifecycle"],
                         ["Open", "Edit", "Execute", "Interact", "Save", "Validate", "Export", "Reopen"])
        self.assertTrue(s["policy"]["no_toy_templates"])
        self.assertTrue(s["policy"]["no_fake_success"])
        self.assertEqual(s["policy"]["missing_dependency"], "BLOCKED, never silently skipped")
        self.assertIn("Δe = 0", s["policy"]["authoritative_invariants"])

    def test_open_status_is_not_mislabeled_complete(self):
        states = self.spec["integration_states"]
        for key in ("ide_redesign", "storybook_primary_removal",
                    "gbrain_signed_canonical_admission"):
            self.assertEqual(states[key], "OPEN")
        self.assertEqual(states["production_deploy"], "NOT_PERFORMED")
        self.assertGreaterEqual(len(self.spec["production_gates"]), 5)


if __name__ == "__main__":
    unittest.main()
