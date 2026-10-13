from __future__ import annotations

import copy
import unittest

from hhs_runtime.hhs_pass220_i082_neural_tensor_graph_v1 import (
    AUTHORITY, NEURON_COUNT, NeuralTensorGraphError, graph_specification,
    ordered_ast, sample_native_neuron, validate_graph_specification,
    validate_sample_native_neuron,
)


class I082NeuralTensorGraphTests(unittest.TestCase):
    def test_exact_geometry_and_no_floats(self):
        spec = graph_specification()
        self.assertEqual(spec["neuron_count"], 86805555555)
        self.assertEqual(spec["positions_per_neuron"], 5184)
        self.assertEqual(spec["logical_positions"], 449999999997120)
        self.assertEqual(spec["exact_numeric_projection"]["coefficient_numerator"], 1406249999991)
        self.assertEqual(spec["exact_numeric_projection"]["coefficient_denominator"], 312500000000)
        self.assertTrue(spec["vm81_address_witness"]["exact_cover_0_80"])
        self.assertTrue(validate_graph_specification(spec))

    def test_ordered_native_ast_retains_source(self):
        branches = ordered_ast()["ordered_equality_chain"]
        self.assertEqual(len(branches), 3)
        self.assertEqual(branches[0]["ordered_mul"][0]["ordered_divide"][0]["ordered_mul"][1], {"atom": "x"})
        self.assertEqual(branches[1]["ordered_divide"][1]["ordered_mul"], [{"atom": "x"}, {"atom": "y"}])
        self.assertEqual(branches[2]["ordered_mul"][2]["ordered_power"], [{"atom": "w"}, {"atom": "u"}])
        self.assertNotEqual(branches[1]["ordered_divide"][1]["ordered_mul"], [{"atom": "y"}, {"atom": "x"}])

    def test_sample_bindings_are_inherited_and_deterministic(self):
        first = sample_native_neuron(0, 0)
        last = sample_native_neuron(NEURON_COUNT - 1, 8)
        self.assertEqual(first, sample_native_neuron(0, 0))
        self.assertEqual(first["vm81_cell_addresses"], list(range(9)))
        self.assertEqual(last["vm81_cell_addresses"], list(range(72, 81)))
        self.assertEqual(len(first["inherited_i070_candidate_hash216"]), 216)
        self.assertEqual(len(first["sample_candidate_hash72"]), 72)
        self.assertTrue(validate_sample_native_neuron(last))

    def test_invalid_node_and_nucleus_fail_closed(self):
        for node, nucleus in ((-1, 0), (NEURON_COUNT, 0), (True, 0), (0, 9), (0, True), (0, 1.0)):
            with self.subTest(node=node, nucleus=nucleus):
                with self.assertRaises(NeuralTensorGraphError):
                    sample_native_neuron(node, nucleus)

    def test_tampering_fails_closed(self):
        spec = graph_specification()
        tampered = copy.deepcopy(spec)
        tampered["ordered_ast"]["ordered_equality_chain"][2]["ordered_mul"].reverse()
        with self.assertRaises(NeuralTensorGraphError):
            validate_graph_specification(tampered)
        sample = sample_native_neuron(0, 4)
        sample["neuron_id"] = 1
        with self.assertRaises(NeuralTensorGraphError):
            validate_sample_native_neuron(sample)

    def test_authority_not_promoted(self):
        self.assertTrue(AUTHORITY["candidate_only"])
        self.assertFalse(AUTHORITY["native_ordered_closure_proven"])
        self.assertFalse(AUTHORITY["canonical_vm81_mutation_authority"])
        self.assertFalse(AUTHORITY["canonical_hash216_persistence_authority"])
        self.assertFalse(AUTHORITY["all_edges_materialized"])


if __name__ == "__main__":
    unittest.main()
