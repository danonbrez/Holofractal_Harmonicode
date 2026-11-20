"""Four-pillar Lane 5/ENRS core source projection and exact staging tests."""
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_pass220_lane5_enrs_core_source_discovery_v1 import (
    PILLARS, inspect_core_source_inventory, inspect_staged_core_source,
)

ROOT = Path(__file__).resolve().parents[1]


class TestLane5ENRSCoreSources(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.stage = AdminStreamStaging(temp.name)
        self.addCleanup(self.stage.close)

    def staged(self, data: bytes) -> str:
        upload = self.stage.create("owner", "core-source")["upload_id"]
        for offset in range(0, len(data), 131071):
            self.stage.append(upload, "owner", offset, data[offset:offset + 131071])
        self.stage.finalize(upload, "owner", sha256(data).hexdigest())
        return upload

    def test_four_roles_and_missing_path_are_explicit(self):
        inv = inspect_core_source_inventory(ROOT)
        self.assertEqual(len(inv["pillars"]), 4)
        self.assertEqual(tuple(x["role"] for x in inv["pillars"]), tuple(r for r, _ in PILLARS))
        self.assertFalse(inv["new_canonical_vm81_mutation_authority"])
        self.assertFalse(inv["new_hash72_receipt_authority"])
        self.assertFalse(inv["new_hash216_provenance_authority"])
        self.assertFalse(inv["enrs_execution_performed"])
        for row in inv["pillars"]:
            source = ROOT / row["relative_path"]
            self.assertEqual(row["present_in_checked_tree"], source.is_file())
            if source.is_file():
                raw = source.read_bytes()
                self.assertEqual(row["source_sha256"], sha256(raw).hexdigest())
                self.assertEqual(row["source_bytes"], len(raw))
            else:
                self.assertIsNone(row["source_sha256"])
                self.assertIsNone(row["source_bytes"])

    def test_every_present_pillar_stages_and_replays_exact_bytes(self):
        inv = inspect_core_source_inventory(ROOT)
        for row in inv["pillars"]:
            if not row["present_in_checked_tree"]:
                continue
            with self.subTest(role=row["role"]):
                data = (ROOT / row["relative_path"]).read_bytes()
                upload = self.staged(data)
                result = inspect_staged_core_source(self.stage, upload, "owner", ROOT)
                self.assertEqual(result["matched_pillar"], row["role"])
                self.assertEqual(result["matched_repo_path"], row["relative_path"])
                self.assertEqual(result["source_sha256"], sha256(data).hexdigest())
                self.assertFalse(result["enrs_execution_performed"])
                self.assertFalse(result["vm81_admission_performed"])
                self.assertFalse(result["hash72_receipt_minted"])
                self.assertFalse(result["hash216_provenance_committed"])
                self.assertEqual(self.stage.read_staged(upload, "owner").read_bytes(), data)

    def test_unmatched_and_unauthorized_sources_preserved(self):
        raw = b"unrecognized source\0with exact bytes"
        upload = self.staged(raw)
        result = inspect_staged_core_source(self.stage, upload, "owner", ROOT)
        self.assertIsNone(result["matched_pillar"])
        self.assertTrue(result["unmatched_source_still_staged_and_retrievable"])
        self.assertEqual(self.stage.read_staged(upload, "owner").read_bytes(), raw)
        with self.assertRaises(Exception):
            inspect_staged_core_source(self.stage, upload, "other-owner", ROOT)

    def test_missing_narrative_source_is_not_fabricated(self):
        with tempfile.TemporaryDirectory() as empty:
            inv = inspect_core_source_inventory(empty)
            self.assertFalse(inv["all_four_present_in_checked_tree"])
            self.assertEqual(len(inv["pillars"]), 4)
            self.assertTrue(all(x["source_sha256"] is None for x in inv["pillars"]))
            upload = self.staged(b"unrelated")
            result = inspect_staged_core_source(self.stage, upload, "owner", empty)
            self.assertIsNone(result["matched_pillar"])


if __name__ == "__main__":
    unittest.main()
