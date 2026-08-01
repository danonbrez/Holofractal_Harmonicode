import unittest

from hhs_pass189 import (
    CONTEXTUAL_STATES,
    GLOBAL_NUCLEUS,
    LO_SHU_POSITIVE_DELTAS,
    EquationObject,
    HydrationRuntime,
    decode_context,
    derive_lo_shu_positive_deltas,
    encode_context,
    extract_membranes,
    local_cell,
    signed_xnor,
    ternary_orientation,
    xnor_bit,
)


class Pass189Tests(unittest.TestCase):
    def test_context_boundaries_and_roundtrip(self):
        for extended in (0, 1, 40, 41, 1_259_711 * 41, CONTEXTUAL_STATES - 1):
            decoded = decode_context(extended)
            self.assertEqual(encode_context(decoded), extended)
        maximum = decode_context(CONTEXTUAL_STATES - 1)
        self.assertEqual((maximum.cell81, maximum.operation64, maximum.g243, maximum.local_k), (80, 63, 242, 20))
        with self.assertRaises(ValueError):
            decode_context(CONTEXTUAL_STATES)

    def test_lo_shu_derivation_and_reciprocity(self):
        self.assertEqual(derive_lo_shu_positive_deltas(), LO_SHU_POSITIVE_DELTAS)
        for cell in range(81):
            for k in range(-20, 21):
                self.assertEqual(local_cell(local_cell(cell, k), -k), cell)

    def test_xnor_and_ternary(self):
        self.assertEqual([(xnor_bit(a, b), signed_xnor(a, b)) for a in (0, 1) for b in (0, 1)], [(1, 1), (0, -1), (0, -1), (1, 1)])
        self.assertEqual(ternary_orientation(GLOBAL_NUCLEUS, 0, 0)[0], 0)
        self.assertEqual(ternary_orientation(41, 0, 0)[0], 1)
        self.assertEqual(ternary_orientation(39, 0, 0)[0], -1)
        self.assertEqual(ternary_orientation(41, 0, 1)[0], -1)

    def test_exact_membranes_are_distinct(self):
        source = "List(01,xy)==(yx=01)+(zw*wz)"
        membranes = extract_membranes(source)
        operators = [item.operator for item in membranes]
        self.assertIn(",", operators)
        self.assertIn("=", operators)
        self.assertIn("==", operators)
        self.assertIn("*", operators)
        self.assertTrue(all(item.outer_boundary == item.interior_states + 1 for item in membranes))
        self.assertTrue(any(item.kind == "LIST" for item in membranes))
        self.assertTrue(any(item.exact_source == "(yx=01)" for item in membranes))

    def test_sparse_hydration_v72_hash_and_replay(self):
        runtime = HydrationRuntime()
        node = runtime.hydrate(projected=1_259_711, path=[20, -20, 0, 8], source="x==x", xnor_a=1, xnor_b=1)
        self.assertEqual(len(node.v72), 72)
        self.assertEqual(len(node.hash72), 72)
        self.assertEqual(len(node.hash216), 216)
        self.assertEqual(node.transition_receipt["coordinate_drift"], 0)
        self.assertEqual(runtime.cache_size, 1)
        self.assertTrue(runtime.replay(node))
        repeated = runtime.hydrate(projected=1_259_711, path=[20, -20, 0, 8], source="x==x", xnor_a=1, xnor_b=1, admit=False)
        self.assertNotEqual(repeated.hash72, node.hash72)
        self.assertLess(runtime.cache_size, 41 ** 4)

    def test_equation_object_shared_projections(self):
        equation = EquationObject.create(
            "V==I*R",
            units={"V": "volt", "I": "ampere", "R": "ohm"},
            dimensions={"V": "electric_potential", "I": "electric_current", "R": "resistance"},
            bindings=[{"variable": "V", "port": "A0"}],
            calibration=[{"variable": "V", "scale": {"numerator": 1, "denominator": 1}, "offset": 0}],
            postulates=[{"name": "ohmic-region", "domain": "0<=V<=5", "falsification_test": "residual<=1/100"}],
        )
        projections = equation.projections(7)
        identities = {value["equation_hash72"] for value in projections.values()}
        self.assertEqual(len(identities), 1)
        self.assertFalse(projections["breadboard"]["output_authorized"])
        self.assertEqual(projections["worldline"]["receipt_index"], 7)

    def test_invalid_postulate_rejected(self):
        with self.assertRaises(ValueError):
            EquationObject.create("x==x", postulates=[{"name": "incomplete"}])

    def test_malformed_membrane_rejected(self):
        with self.assertRaises(ValueError):
            extract_membranes("List(x,y")

    def test_ordered_identity_hash_sensitivity(self):
        runtime = HydrationRuntime()
        forward = runtime.hydrate(projected=7, source="xy*yx", admit=False)
        reverse = runtime.hydrate(projected=7, source="yx*xy", admit=False)
        self.assertNotEqual(forward.hash72, reverse.hash72)
        self.assertNotEqual(forward.hash216, reverse.hash216)


if __name__ == "__main__":
    unittest.main()
