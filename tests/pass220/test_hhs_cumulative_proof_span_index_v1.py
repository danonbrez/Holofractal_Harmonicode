"""Intra-file HARMONICODE proof preservation and source failure regression."""
from pathlib import Path
import tempfile
import unittest

from hhs_runtime.pass220.hhs_cumulative_proof_span_index_v1 import (
    ProofSpanIndexError,
    extract_source_spans,
    build_repository_proof_span_index,
)


SOURCE = (
    "# Module 190 — Recursion\n"
    "Lemma ConstantCoverage == certified shared identities preserve all cells.\n"
    "For each cell x, x==x at its admitted type.\n"
    "Lemma Termination == finite cells and monotone information close.\n"
    "# Module 191 — Continuation\n"
    "P²-pq=1\n"
)


class TestProofSpanIndex(unittest.TestCase):
    def test_named_lemmas_retain_verbatim_text_and_lines(self):
        r = extract_source_spans(path="docs/course/sample.md", source_text=SOURCE)
        named = [e for e in r["entries"] if e["kind"] == "NAMED_PROOF_SPAN"]
        self.assertEqual(len(named), 2)
        self.assertEqual(named[0]["start_line"], 2)
        self.assertEqual(named[0]["end_line"], 3)
        self.assertIn("For each cell x, x==x", named[0]["source_text"])
        self.assertEqual(named[1]["start_line"], 4)
        self.assertEqual(named[1]["end_line"], 4)
        self.assertTrue(all(not e["proof_admission_inferred"] for e in named))
        self.assertEqual(
            named[0]["source_text"],
            SOURCE[named[0]["start_char"]:named[0]["end_char"]],
        )

    def test_math_lines_are_not_reduced_to_proof_status(self):
        r = extract_source_spans(path="docs/course/sample.md", source_text=SOURCE)
        equations = [e for e in r["entries"]
                     if e["kind"] == "MATHEMATICAL_SOURCE_LINE"]
        self.assertEqual(len(equations), 4)
        self.assertIn("Lemma Termination", equations[2]["source_text"])\n        self.assertIn("P²-pq=1", equations[3]["source_text"])
        self.assertTrue(r["candidate_only"])
        self.assertFalse(r["exhaustive_proof_claim"])

    def test_deterministic_replay(self):
        a = extract_source_spans(path="a.lean", source_text=SOURCE)
        b = extract_source_spans(path="a.lean", source_text=SOURCE)
        self.assertEqual(a["index_sha256"], b["index_sha256"])

    def test_full_graph_scan_does_not_use_topic_keyword_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text(SOURCE, encoding="utf-8")
            (root / "b.lean").write_text(
                "theorem tensorReturn : True := by\n  trivial\n",
                encoding="utf-8",
            )
            graph = {
                "roots": {"graph_root_hash216": "0" * 216},
                "files": [
                    {"path": "a.md", "git_blob": "a"},
                    {"path": "b.lean", "git_blob": "b"},
                    {"path": "missing.md", "git_blob": "c"},
                ],
            }
            r = build_repository_proof_span_index(root, graph)
            self.assertEqual(r["examined_text_files"], 2)
            self.assertEqual(r["files_with_discoverable_spans"], 2)
            self.assertEqual(r["named_proof_span_count"], 3)
            self.assertEqual(r["unavailable_sources"], [
                {"path": "missing.md", "reason": "SOURCE_NOT_AVAILABLE"},
            ])
            self.assertFalse(r["all_proofs_discovered"])

    def test_path_traversal_fails_closed(self):
        graph = {"files": [{"path": "../escaped.md"}]}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ProofSpanIndexError, "INVALID_INDEXED_PATH"):
                build_repository_proof_span_index(Path(tmp), graph)


if __name__ == "__main__":
    unittest.main()
