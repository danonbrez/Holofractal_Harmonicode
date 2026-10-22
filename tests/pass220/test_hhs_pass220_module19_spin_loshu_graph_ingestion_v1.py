import copy
import unittest
from unittest.mock import Mock
from hhs_runtime.hhs_pass220_module19_spin_loshu_graph_ingestion_v1 import (
    RELATIONS, relation_witness, ingest_relation, bind_i028_constructor_graph_candidate,
)

class Module19Relations(unittest.TestCase):
    def setUp(self):
        self.engine = Mock()
        self.engine.verify_node.side_effect = lambda n: n
        # Explicitly model the inherited Pass128 non-escalation method.
        self.engine.assert_no_execution_escalation = Mock(return_value=None)
        self.engine.relate.return_value = {
            "execution_authority": False, "mutation_authority": False,
            "executable": False,
        }

    def nodes(self, i=0):
        return ({"normalized_proposition": RELATIONS[i][0]},
                {"normalized_proposition": RELATIONS[i][2]})

    def test_ordered_ingestion(self):
        source, target = self.nodes()
        edge = ingest_relation(self.engine, source, target,
                               relation_index=0, witness=relation_witness())
        self.assertIs(edge, self.engine.relate.return_value)
        self.engine.relate.assert_called_once()
        kwargs = self.engine.relate.call_args.kwargs
        self.assertEqual(kwargs["relation_type"], "DEFINES")
        self.assertTrue(kwargs["directed"])
        self.assertEqual(kwargs["evidence_roots"], [relation_witness()["evidence_sha256"]])
        self.engine.assert_no_execution_escalation.assert_called_once_with(edge)

    def test_swapped_endpoints_rejected(self):
        source, target = self.nodes()
        with self.assertRaisesRegex(ValueError, "ORDERED_ENDPOINT"):
            ingest_relation(self.engine, target, source,
                            relation_index=0, witness=relation_witness())
        self.engine.relate.assert_not_called()

    def test_altered_ledger_rejected(self):
        source, target = self.nodes()
        altered = copy.deepcopy(relation_witness())
        altered["ordered_operands"][0] = "S·x"
        with self.assertRaisesRegex(ValueError, "WITNESS_MISMATCH"):
            ingest_relation(self.engine, source, target,
                            relation_index=0, witness=altered)
        self.engine.relate.assert_not_called()

    def test_authority_escalation_rejected(self):
        source, target = self.nodes()
        altered = relation_witness()
        altered["hash216_mint_authority"] = True
        with self.assertRaisesRegex(ValueError, "WITNESS_MISMATCH"):
            ingest_relation(self.engine, source, target,
                            relation_index=0, witness=altered)

    def test_i028_graph_binding_requires_complete_ordered_edges(self):
        evidence = relation_witness()["evidence_sha256"]
        edges = [
            {"relation_type": relation, "directed": True,
             "relation_evidence_roots": [evidence],
             "knowledge_edge_root_hash72": str(i) * 72,
             "execution_authority": False, "mutation_authority": False,
             "executable": False}
            for i, (_, relation, _) in enumerate(RELATIONS)
        ]
        self.engine.verify_edge.side_effect = lambda e: e
        roots = {"pipeline_root_hash72": "P"*72,
                 "constructor_graph_root_hash72": "G"*72,
                 "witness": relation_witness()}
        out = bind_i028_constructor_graph_candidate(self.engine, edges, **roots)
        self.assertEqual(out["ordered_edge_roots"], [str(i)*72 for i in range(4)])
        self.assertFalse(out["i028_native_abi_invoked"])
        self.assertFalse(out["hash216_mint_authority"])
        with self.assertRaisesRegex(ValueError, "COMPLETE_DIRECTED"):
            bind_i028_constructor_graph_candidate(self.engine, edges[:3], **roots)
        with self.assertRaisesRegex(ValueError, "INHERITED_HASH72"):
            bind_i028_constructor_graph_candidate(
                self.engine, edges, **{**roots, "pipeline_root_hash72": ""})
        reordered = list(edges)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        with self.assertRaisesRegex(ValueError, "ORDERED_EDGE"):
            bind_i028_constructor_graph_candidate(self.engine, reordered, **roots)
        forged = [dict(x) for x in edges]
        forged[2]["mutation_authority"] = True
        with self.assertRaisesRegex(ValueError, "ORDERED_EDGE"):
            bind_i028_constructor_graph_candidate(self.engine, forged, **roots)

    def test_all_four_relations_are_typed(self):
        for i, (_, relation, _) in enumerate(RELATIONS):
            self.engine.reset_mock()
            source, target = self.nodes(i)
            ingest_relation(self.engine, source, target,
                            relation_index=i, witness=relation_witness())
            self.assertEqual(self.engine.relate.call_args.kwargs["relation_type"], relation)

if __name__ == "__main__":
    unittest.main()
