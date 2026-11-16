"""Dependency-frontier preservation and rejection tests (candidate-only)."""
import copy
import unittest

from hhs_runtime.pass220.hhs_cumulative_lemma_frontier_v1 import (
    CorpusFrontierError, construct_frontier,
)

LEMMA = {"schema": "TEST_INHERITED_LEMMAS", "lemmas": [
    {"id": "a", "status": "EXECUTED_EXACT", "dependencies": []},
    {"id": "b", "status": "CONTRACT_LEMMA", "dependencies": ["a"]},
    {"id": "c", "status": "EXECUTED_EXACT", "dependencies": []},
]}
COURSE = {"source": {"path": "docs/course/example.md", "git_blob_sha": "test"},
          "modules": [{"id": "m", "proof_admitted": False,
                       "canonical_runtime_admitted": False}]}


class TestCumulativeLemmaFrontier(unittest.TestCase):
    def test_unselected_lemmas_and_source_preserved(self):
        result = construct_frontier(lemma_corpora=[LEMMA],
                                    course_indexes=[COURSE], targets=["b"])
        self.assertEqual(result["node_count"], 4)
        self.assertEqual(result["edge_count"], 1)
        self.assertEqual(result["dependency_edges"],
                         [{"premise": "a", "conclusion": "b"}])
        self.assertLess(result["complete_input_frontier_order"].index("a"),
                        result["complete_input_frontier_order"].index("b"))
        self.assertIn("c", result["complete_input_frontier_order"])
        course = next(n for n in result["nodes"] if n["id"] == "m")
        self.assertIs(course["proof_admitted"], False)
        self.assertEqual(result["proofs_newly_admitted"], 0)
        self.assertTrue(result["indexed_coverage_only"])

    def test_deterministic_replay(self):
        first = construct_frontier(lemma_corpora=[LEMMA], course_indexes=[COURSE])
        second = construct_frontier(lemma_corpora=[LEMMA], course_indexes=[COURSE])
        self.assertEqual(first["frontier_sha256"], second["frontier_sha256"])

    def test_missing_parent_fails_closed(self):
        broken = copy.deepcopy(LEMMA)
        broken["lemmas"][1]["dependencies"] = ["missing"]
        with self.assertRaisesRegex(CorpusFrontierError, "MISSING_INHERITED"):
            construct_frontier(lemma_corpora=[broken])

    def test_cyclic_dependency_fails_closed(self):
        broken = copy.deepcopy(LEMMA)
        broken["lemmas"][0]["dependencies"] = ["b"]
        with self.assertRaisesRegex(CorpusFrontierError, "CYCLIC"):
            construct_frontier(lemma_corpora=[broken])

    def test_duplicate_id_fails_closed(self):
        broken = copy.deepcopy(LEMMA)
        broken["lemmas"].append(copy.deepcopy(broken["lemmas"][0]))
        with self.assertRaisesRegex(CorpusFrontierError, "DUPLICATE"):
            construct_frontier(lemma_corpora=[broken])


if __name__ == "__main__":
    unittest.main()
