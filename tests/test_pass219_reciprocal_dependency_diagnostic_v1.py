"""Targeted regression probes for Pass 219 reciprocal dependencies."""
import unittest

from hhs_runtime.pass219.reciprocal_dependency_diagnostic_v1 import (
    Dependency, Verdict, evaluate_dependency_scope,
)


class ReciprocalDependencyTests(unittest.TestCase):
    def test_cycle_retained_without_false_failure(self):
        edges = (
            Dependency(("A",), ("B",), "support", ("e1",)),
            Dependency(("B",), ("A",), "support", ("e2",)),
        )
        result = evaluate_dependency_scope(("A",), edges)
        self.assertEqual(result.verdict, Verdict.ADMISSIBLE)
        self.assertEqual(result.reachable_nodes, ("A", "B"))
        self.assertEqual(result.examined_edges, (0, 1))
        self.assertEqual(edges[0].evidence_ids, ("e1",))

    def test_joint_sources_must_both_be_available(self):
        edges = (Dependency(("flowers", "workers"), ("honey",), "joint-resource"),)
        self.assertEqual(evaluate_dependency_scope(("flowers",), edges).examined_edges, ())
        result = evaluate_dependency_scope(("flowers", "workers"), edges)
        self.assertEqual(result.reachable_nodes, ("flowers", "workers", "honey"))

    def test_unresolved_keeps_zero(self):
        edges = (Dependency(("A",), ("B",), "ecological", unresolved=True),)
        self.assertEqual(evaluate_dependency_scope(("A",), edges).verdict, Verdict.UNRESOLVED)

    def test_proven_forbidden_is_negative(self):
        edges = (Dependency(("A",), ("B",), "proven-cut", proven_forbidden=True),)
        self.assertEqual(evaluate_dependency_scope(("A",), edges).verdict, Verdict.FORBIDDEN)

    def test_limit_fails_open_for_inquiry_not_canonical_admission(self):
        edges = (
            Dependency(("A",), ("B",), "support"),
            Dependency(("B",), ("C",), "support"),
        )
        result = evaluate_dependency_scope(("A",), edges, max_edges=1)
        self.assertTrue(result.truncated)
        self.assertEqual(result.verdict, Verdict.UNRESOLVED)

    def test_ordered_operands_not_commuted(self):
        edges = (Dependency(("A",), ("B",), "directed"),)
        self.assertEqual(evaluate_dependency_scope(("B",), edges).examined_edges, ())
        self.assertEqual(evaluate_dependency_scope(("A",), edges).examined_edges, (0,))

    def test_invalid_record_rejected(self):
        with self.assertRaises(ValueError):
            Dependency((), ("B",), "support")
        with self.assertRaises(ValueError):
            Dependency(("A",), ("B",), "support", unresolved=True, proven_forbidden=True)


if __name__ == "__main__":
    unittest.main()
