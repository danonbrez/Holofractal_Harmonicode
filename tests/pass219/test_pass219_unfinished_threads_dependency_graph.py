"""Bounded tests for global unfinished-thread graph integrity."""
import unittest
from scripts.pass219_unfinished_threads_dependency_graph import graph_from_inventory

class GraphTests(unittest.TestCase):
    def setUp(self):
        self.inventory = {
            "schema": "HHS_PASS219_GLOBAL_BRANCH_PR_ADMISSION_INVENTORY_V1",
            "repository": "owner/repo",
            "orphan_branches_without_open_pr": ["thread/unfinished"],
            "open_prs": [
                {"number": 10, "title": "candidate", "head": "branch/a",
                 "head_sha": "a"*40, "body": "Requires #11",
                 "integration_candidate": True, "blocking_checks": [], "url": "https://example.com/10"},
                {"number": 11, "title": "unfinished", "head": "branch/b",
                 "head_sha": "b"*40, "body": "",
                 "integration_candidate": False, "blocking_checks": ["lean"],
                 "url": "https://example.com/11"}]}

    def test_every_thread_and_contract(self):
        graph=graph_from_inventory(self.inventory)
        self.assertEqual(set(graph["nodes"]), {
            "PASS219_CPP_LEAN_PROOF_ENFORCEMENT", "pr:10", "pr:11",
            "branch:thread/unfinished"})
        self.assertEqual(sum(e["kind"]=="must_pass_contract" for e in graph["edges"]), 3)

    def test_reference_is_unverified_not_auto_merge(self):
        graph=graph_from_inventory(self.inventory)
        self.assertIn({"from":"pr:10","to":"pr:11",
                       "kind":"referenced_pr_unverified"},graph["edges"])
        self.assertEqual(graph["nodes"]["pr:11"]["status"],"unfinished")

    def test_deterministic_review_order_not_merger_authority(self):
        graph=graph_from_inventory(self.inventory)
        self.assertEqual(graph["review_order_not_merge_authority"],
                         sorted(["pr:10", "pr:11", "branch:thread/unfinished"]))
        self.assertNotIn("merged", graph["nodes"]["pr:10"])

    def test_merged_repair_inherits_same_contract(self):
        self.inventory["mainline_repair_obligations"] = [{
            "source_pr": 774, "main_sha": "c"*40,
            "blockers": ["clock overflow", "UQCEL malformed"],
            "next": "repair on main and replay admission"}]
        graph = graph_from_inventory(self.inventory)
        repair = graph["nodes"]["repair:774"]
        self.assertEqual(repair["status"], "unfinished")
        self.assertFalse(repair["proof_closure_verified"])
        self.assertFalse(repair["native_replay_verified"])
        self.assertFalse(repair["exact_main_verified"])
        self.assertIn({"from":"repair:774",
                       "to":"PASS219_CPP_LEAN_PROOF_ENFORCEMENT",
                       "kind":"must_pass_contract"}, graph["edges"])
        self.assertIn({"from":"repair:774","to":"source_pr:774",
                       "kind":"inherited_provenance_non_scheduling"}, graph["edges"])

    def test_no_phantom_dependency(self):
        self.inventory["open_prs"][0]["body"]="References #99999"
        graph=graph_from_inventory(self.inventory)
        self.assertFalse(any(e["kind"]=="referenced_pr_unverified" for e in graph["edges"]))

if __name__=="__main__":
    unittest.main()
