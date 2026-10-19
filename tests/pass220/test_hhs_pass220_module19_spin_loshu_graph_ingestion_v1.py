import copy
import unittest
from unittest.mock import Mock
from hhs_runtime.hhs_pass220_module19_spin_loshu_graph_ingestion_v1 import (
    RELATIONS, relation_witness, ingest_relation,
)

class Module19Relations(unittest.TestCase):
    def setUp(self):
        self.engine = Mock()
        self.engine.verify_node.side_effect = lambda n: n
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

    def test_all_four_relations_are_typed(self):
        for i, (_, relation, _) in enumerate(RELATIONS):
            self.engine.reset_mock()
            source, target = self.nodes(i)
            ingest_relation(self.engine, source, target,
                            relation_index=i, witness=relation_witness())
            self.assertEqual(self.engine.relate.call_args.kwargs["relation_type"], relation)

if __name__ == "__main__":
    unittest.main()
