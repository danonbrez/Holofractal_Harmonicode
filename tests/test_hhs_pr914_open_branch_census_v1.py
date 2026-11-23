"""Offline regressions for the PR914 read-only census collector."""
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hhs_pr914_open_branch_census_v1.py"
SPEC = importlib.util.spec_from_file_location("hhs_pr914_open_branch_census_v1", MODULE_PATH)
census = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(census)


def pr(number, head_ref, base_ref="main", head_sha=None, base_sha="b" * 40):
    return {
        "number": number,
        "head": {"ref": head_ref, "sha": head_sha or (str(number) * 40)[:40]},
        "base": {"ref": base_ref, "sha": base_sha},
    }


class CensusTests(unittest.TestCase):
    def test_cross_pr_dependency_parents_are_preserved(self):
        pulls = [
            pr(918, "feature/child", "feature/parent"),
            pr(917, "feature/parent"),
            pr(914, "feature/coordinator"),
        ]
        parents = census.dependency_parents(pulls)
        self.assertEqual(parents[918], [917])
        self.assertEqual(parents[917], [])
        self.assertEqual(parents[914], [])

    def test_branch_join_retains_unpr_and_duplicate_tips(self):
        head_sha = "a" * 40
        duplicate_sha = "d" * 40
        branches = [
            {"name": "main", "commit": {"sha": "f" * 40}},
            {"name": "feature/open", "commit": {"sha": head_sha}},
            {"name": "archive/copy-a", "commit": {"sha": duplicate_sha}},
            {"name": "archive/copy-b", "commit": {"sha": duplicate_sha}},
        ]
        records = census.build_branch_records(branches, [pr(914, "feature/open", head_sha=head_sha)])
        by_name = {row["name"]: row for row in records}
        self.assertEqual(by_name["feature/open"]["open_pr_numbers"], [914])
        self.assertTrue(by_name["feature/open"]["matches_all_linked_open_pr_heads"])
        self.assertEqual(
            by_name["archive/copy-a"]["classification"],
            "UNPR_BRANCH_REQUIRES_RECONCILIATION",
        )
        self.assertEqual(by_name["archive/copy-a"]["disposition"], "UNASSESSED")
        groups = census.duplicate_tip_groups(records)
        self.assertEqual(groups, [{
            "sha": duplicate_sha,
            "branch_names": ["archive/copy-a", "archive/copy-b"],
            "semantic_equivalence_proven": False,
        }])

    def test_snapshot_delta_keeps_additions_removals_and_head_moves(self):
        snapshot = {"pull_requests": [
            {"pr_number": 1, "head_sha": "a" * 40},
            {"pr_number": 2, "head_sha": None},
        ]}
        live = [
            {"number": 2, "head": {"sha": "b" * 40}},
            {"number": 3, "head": {"sha": "c" * 40}},
        ]
        delta = census.snapshot_delta(snapshot, live)
        self.assertEqual(delta["added_pr_numbers"], [3])
        self.assertEqual(delta["no_longer_open_pr_numbers"], [1])
        self.assertEqual(delta["head_sha_changes"], [])
        self.assertTrue(delta["comparison_complete"])

    def test_snapshot_delta_reports_nonnull_head_move(self):
        snapshot = {"entries": [{"pr_number": 914, "head_sha": "a" * 40}]}
        live = [{"number": 914, "head": {"sha": "b" * 40}}]
        delta = census.snapshot_delta(snapshot, live)
        self.assertEqual(delta["head_sha_changes"], [{
            "pr_number": 914,
            "previous": "a" * 40,
            "current": "b" * 40,
        }])

    def test_rev_list_counts_are_ordered_behind_then_ahead(self):
        self.assertEqual(census.parse_rev_list_counts("7 11\n"), (7, 11))
        with self.assertRaises(census.CensusError):
            census.parse_rev_list_counts("not-a-count")

    def test_document_guard_rejects_count_or_authority_escalation(self):
        document = {
            "observed_open_pr_count": 1,
            "observed_branch_count": 1,
            "integrated": False,
            "automatic_mass_merge_authorized": False,
            "requires_refresh_before_any_merge": True,
            "pull_requests": [{"disposition": "UNASSESSED"}],
            "branches": [{"disposition": "UNASSESSED"}],
        }
        census.validate_census_document(document)
        invalid = dict(document, integrated=True)
        with self.assertRaises(census.CensusError):
            census.validate_census_document(invalid)
        invalid = dict(document, observed_branch_count=2)
        with self.assertRaises(census.CensusError):
            census.validate_census_document(invalid)


if __name__ == "__main__":
    unittest.main()
