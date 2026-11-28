import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "hhs_pr914_git_reconciliation_evidence_v1.py"
)
SPEC = importlib.util.spec_from_file_location("hhs_pr914_git_reconciliation_v1", MODULE_PATH)
reconciliation = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(reconciliation)


def run_git(repository, *args):
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


class GitReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name)
        run_git(self.repository, "init", "-q", "-b", "main", ".")
        run_git(self.repository, "config", "user.name", "PR914 Test")
        run_git(self.repository, "config", "user.email", "pr914@example.invalid")
        (self.repository / "shared.txt").write_text("base\n", encoding="utf-8")
        (self.repository / "base_only.txt").write_text("base\n", encoding="utf-8")
        run_git(self.repository, "add", "shared.txt", "base_only.txt")
        run_git(self.repository, "commit", "-qm", "base")
        self.base = run_git(self.repository, "rev-parse", "HEAD")

        run_git(self.repository, "checkout", "-qb", "feature/one")
        (self.repository / "shared.txt").write_text("one\n", encoding="utf-8")
        (self.repository / "one.txt").write_text("one\n", encoding="utf-8")
        run_git(self.repository, "add", "shared.txt", "one.txt")
        run_git(self.repository, "commit", "-qm", "one")
        self.one = run_git(self.repository, "rev-parse", "HEAD")

        run_git(self.repository, "checkout", "-q", "main")
        (self.repository / "shared.txt").write_text("main\n", encoding="utf-8")
        (self.repository / "main.txt").write_text("main\n", encoding="utf-8")
        run_git(self.repository, "add", "shared.txt", "main.txt")
        run_git(self.repository, "commit", "-qm", "main")
        self.main = run_git(self.repository, "rev-parse", "HEAD")

        run_git(self.repository, "checkout", "-qb", "feature/two", self.base)
        (self.repository / "shared.txt").write_text("two\n", encoding="utf-8")
        (self.repository / "two.txt").write_text("two\n", encoding="utf-8")
        run_git(self.repository, "add", "shared.txt", "two.txt")
        run_git(self.repository, "commit", "-qm", "two")
        self.two = run_git(self.repository, "rev-parse", "HEAD")

    def source_record(self, number, head_ref, head_sha, dependencies=None):
        return {
            "pr_number": number,
            "pr_url": f"https://example.invalid/pull/{number}",
            "head_ref": head_ref,
            "head_sha": head_sha,
            "base_ref": "main",
            "base_sha": self.base,
            "pr_base_ancestry": {
                "base_sha": self.base,
                "head_sha": head_sha,
                "merge_base_sha": self.base,
                "behind_by": 0,
                "ahead_by": 1,
            },
            "current_base_ancestry": {
                "base_sha": self.main,
                "head_sha": head_sha,
                "merge_base_sha": self.base,
                "behind_by": 1,
                "ahead_by": 1,
            },
            "current_main_ancestry": {
                "base_sha": self.main,
                "head_sha": head_sha,
                "merge_base_sha": self.base,
                "behind_by": 1,
                "ahead_by": 1,
            },
            "contract_dependencies": dependencies or [],
        }

    def census_bytes(self):
        census = {
            "schema": "HHS_PR914_G0_LIVE_CENSUS_V1",
            "observed_at": "2026-11-23T00:00:00+00:00",
            "repository": "example/repository",
            "main_sha": self.main,
            "pull_requests": [
                self.source_record(2, "feature/two", self.two),
                self.source_record(1, "feature/one", self.one),
            ],
        }
        return json.dumps(census).encode()

    def collect(self):
        census = Path(self.temporary.name) / "census.json"
        census.write_bytes(self.census_bytes())
        args = argparse.Namespace(repository=self.repository, census=census)
        return reconciliation.collect(args), census

    def test_collect_real_git_paths_commits_conflicts_and_overlaps(self):
        refs_before = run_git(self.repository, "show-ref")
        document, census = self.collect()
        self.assertEqual(refs_before, run_git(self.repository, "show-ref"))
        self.assertEqual(2, document["observed_open_pr_count"])
        self.assertTrue(document["git_evidence_complete"])
        self.assertFalse(document["reviews_checks_and_combined_statuses_complete"])
        self.assertFalse(document["semantic_reconciliation_complete"])
        self.assertFalse(document["g1_complete"])
        self.assertFalse(document["candidate_composed"])
        self.assertFalse(document["terminal_dispositions_assigned"])
        self.assertFalse(document["live_ref_refresh_performed"])
        self.assertEqual("NOT_COLLECTED", document["head_moves_since_source_census"])
        self.assertEqual(
            hashlib.sha256(census.read_bytes()).hexdigest(),
            document["source_census"]["sha256"],
        )

        by_number = {record["pr_number"]: record for record in document["pull_requests"]}
        self.assertEqual([2, 1], [record["pr_number"] for record in document["pull_requests"]])
        one = by_number[1]
        self.assertEqual(1, one["pr_number"])
        self.assertEqual({"one.txt", "shared.txt"}, set(one["pr_base_changed_files"]["paths"]))
        self.assertEqual(2, one["pr_base_changed_files"]["count"])
        self.assertEqual([self.one], one["pr_base_commits"]["ids"])
        self.assertEqual([self.one], one["current_base_commits"]["ids"])
        self.assertEqual(
            "CONFLICTED_HYPOTHETICAL_MERGE_TREE",
            one["current_main_merge"]["status"],
        )
        self.assertEqual(["shared.txt"], one["current_main_merge"]["conflict_paths"])
        self.assertFalse(one["current_main_merge"]["integration_candidate"])
        self.assertFalse(one["current_main_merge"]["working_tree_or_ref_modified"])
        self.assertEqual(["shared.txt"], one["overlapping_current_base_paths"])
        self.assertFalse(one["reviews"]["complete"])
        self.assertFalse(one["check_runs"]["complete"])
        self.assertEqual("UNASSESSED", one["disposition"])
        self.assertEqual("UNASSESSED", one["frozen_layer_impact"])
        self.assertEqual("UNASSESSED", one["canonical_source_impact"])
        self.assertIsNone(one["review_authority"])

        overlap = document["current_base_path_overlaps"][0]
        self.assertEqual("shared.txt", overlap["path"])
        self.assertEqual([1, 2], overlap["pr_numbers"])
        self.assertFalse(overlap["semantic_conflict_proven"])
        self.assertEqual([], document["dependency_cycles"])
        json.dumps(document)

    def test_dependency_cycle_detection_preserves_cycle_evidence(self):
        records = [
            {"pr_number": 1, "contract_dependencies": [2]},
            {"pr_number": 2, "contract_dependencies": [3]},
            {"pr_number": 3, "contract_dependencies": [1]},
            {"pr_number": 4, "contract_dependencies": []},
        ]
        self.assertEqual([[1, 2, 3, 1]], reconciliation.dependency_cycles(records))

    def test_name_status_parser_retains_rename_and_modification(self):
        records = reconciliation.parse_name_status_z("R100\0old.txt\0new.txt\0M\0other.txt\0")
        self.assertEqual(
            [
                {"status": "R100", "path": "new.txt", "previous_path": "old.txt"},
                {"status": "M", "path": "other.txt", "previous_path": None},
            ],
            records,
        )

    def test_validation_rejects_candidate_promotion(self):
        document, _ = self.collect()
        document["candidate_composed"] = True
        with self.assertRaises(reconciliation.ReconciliationError):
            reconciliation.validate_document(document)


if __name__ == "__main__":
    unittest.main()
