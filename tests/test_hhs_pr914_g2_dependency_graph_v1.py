"""G2 deterministic topology checks: parent orientation, cycle witness, fail-closed."""
import copy
import json
from pathlib import Path
import unittest

from tools.hhs_pr914_g2_dependency_graph import evaluate

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts/architecture/HHS_PR914_G2_DEPENDENCY_CONFLICT_AND_CANDIDATE_COMPOSITION_CONTRACT_V1.json"
INVENTORY = ROOT / "contracts/architecture/HHS_PR914_OPEN_BRANCH_INVENTORY_20261123.json"


class TestG2ExecutableGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_seed_all_21_edges_and_parent_first(self):
        graph = evaluate(self.contract, self.inventory)
        self.assertEqual(graph["preserved_edge_count"], 21)
        self.assertEqual(graph["dependency_orientation"], "PARENT_BEFORE_DEPENDENT")
        self.assertEqual(graph["cycle_components"], [])
        self.assertIsNotNone(graph["topological_order"])
        order = {v: i for i, v in enumerate(graph["topological_order"])}
        for edge in graph["preserved_edge_evidence"]:
            self.assertLess(order[edge["required_parent_node_id"]],
                            order[edge["dependent_node_id"]])
        for n in range(509, 522):
            self.assertLess(order[f"PR:{n:06d}"], order[f"PR:{n+1:06d}"])

    def test_determinism_and_candidate_block(self):
        g1 = evaluate(self.contract, self.inventory)
        g2 = evaluate(self.contract, self.inventory)
        self.assertEqual(g1, g2)
        self.assertFalse(g1["candidate_composed"])
        self.assertFalse(g1["g2_complete"])
        self.assertFalse(g1["main_merge_authorized"])
        self.assertIn("G2_BLOCKED_STALE_REFS", g1["blocking_reasons"])

    def test_cycle_preserved_and_order_withheld(self):
        c = copy.deepcopy(self.contract)
        c["known_dependency_edge_seed"]["edges"][-1] = {
            "dependent_pr": 509, "required_parent_pr": 522
        }
        graph = evaluate(c, self.inventory)
        self.assertEqual(graph["preserved_edge_count"], 21)
        self.assertIn("G2_BLOCKED_DEPENDENCY_CYCLE", graph["blocking_reasons"])
        self.assertIsNone(graph["topological_order"])
        self.assertTrue(any("PR:000509" in component for component in graph["cycle_components"]))

    def test_edge_orientation_and_count_guards(self):
        c = copy.deepcopy(self.contract)
        c["known_dependency_edge_seed"]["orientation"] = "DEPENDENT_BEFORE_PARENT"
        with self.assertRaisesRegex(ValueError, "ORIENTATION"):
            evaluate(c, self.inventory)
        c = copy.deepcopy(self.contract)
        c["known_dependency_edge_seed"]["edges"].pop()
        with self.assertRaisesRegex(ValueError, "COUNT"):
            evaluate(c, self.inventory)

    def test_missing_live_parent_is_explicit(self):
        i = copy.deepcopy(self.inventory)
        i["entries"] = [e for e in i["entries"] if e["number"] != 917]
        graph = evaluate(self.contract, i)
        self.assertIn("PR:000917", graph["unresolved_external_parent_or_dependent_nodes"])
        blocked = {r["node_id"]: r["unresolved_parent_nodes"]
                   for r in graph["blocked_by_dependency"]}
        self.assertIn("PR:000917", blocked["PR:000918"])
        self.assertIn("G2_BLOCKED_INCOMPLETE_GRAPH", graph["blocking_reasons"])

    def test_live_refresh_without_full_g1_never_promotes(self):
        refresh = {
            "main_sha": "a" * 40, "pagination_complete": True,
            "g1_complete": False, "entries": [],
        }
        graph = evaluate(self.contract, self.inventory, refresh)
        self.assertFalse(graph["candidate_composed"])
        self.assertIn("G2_BLOCKED_INCOMPLETE_GRAPH", graph["blocking_reasons"])


if __name__ == "__main__":
    unittest.main()
