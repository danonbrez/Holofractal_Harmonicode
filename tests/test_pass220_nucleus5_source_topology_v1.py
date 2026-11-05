"""Exact source-address coverage for the nucleus-5 tensor."""
import unittest

from hhs_runtime.hhs_pass220_nucleus5_matrixtimes_abp_source_v1 import (
    VERBATIM_SOURCE, Nucleus5Source,
)
from hhs_runtime.hhs_pass220_nucleus5_source_topology_v1 import (
    Nucleus5TopologyError, matrix_occurrences, source_topology,
)


class Nucleus5TopologyTests(unittest.TestCase):
    def test_three_ordered_4x4_matrices_and_all_cells(self):
        matrices = matrix_occurrences()
        self.assertEqual(len(matrices), 3)
        self.assertEqual([len(matrix["cells"]) for matrix in matrices], [16, 16, 16])
        for matrix in matrices:
            self.assertEqual(VERBATIM_SOURCE[matrix["start"]:matrix["end"]],
                             matrix["source"])
            self.assertEqual([(cell["row"], cell["column"]) for cell in matrix["cells"]],
                             [(row, col) for row in range(4) for col in range(4)])
            for cell in matrix["cells"]:
                self.assertEqual(
                    VERBATIM_SOURCE[cell["start"]:cell["end"]],
                    cell["source"],
                )
        self.assertEqual(matrices[0]["cells"][0]["source"],
                         "3334608*x^6*y^4*z^4+-153*z^4*(-x+z)/(x*y)")
        self.assertEqual(matrices[1]["cells"][0]["source"],
                         "1377*(370512+17*x)/(x*y)")
        self.assertEqual(matrices[2]["cells"][0]["source"], "1")

    def test_circuit_gate_source_spans(self):
        for mode in ("ONE_INPUT", "SUCCESSOR_INPUT"):
            topology = source_topology(mode)
            circuit = Nucleus5Source().native_compilation_source_bytes(mode).decode()
            self.assertEqual(topology["matrix_count"], 3)
            self.assertEqual(topology["equality_count"],
                             3 + len(Nucleus5Source().parameter_edges(mode)))
            for gate in topology["equality_occurrences"]:
                self.assertEqual(circuit[gate["start"]:gate["end"]], "==")
            self.assertFalse(topology["native_effectful_vmir_execution_verified"])
            self.assertFalse(topology["canonical_vm81_admission"])
        self.assertEqual(source_topology("SUCCESSOR_INPUT")["equality_count"],
                         source_topology("ONE_INPUT")["equality_count"] + 5)

    def test_fail_closed_malformed_matrix(self):
        with self.assertRaises(Nucleus5TopologyError):
            matrix_occurrences(VERBATIM_SOURCE.replace("{{3334608", "{{{3334608", 1))


if __name__ == "__main__":
    unittest.main()
