import unittest
from hhs_runtime.hhs_pass220_lane5_5184_constraint_proof_v1 import (
    prove_candidate_grid, verify_candidate_grid
)

def cells():
    return [{"linear5184": i, "cell81": i//64, "operation64": i%64,
             "hash72_major": i//72, "hash72_minor": i%72,
             "bigint_decimal": str(i),
             "canonical_mutation_authority": False, "hash72_mint_authority": False,
             "hash216_mint_authority": False, "persistence_authority": False}
            for i in range(5184)]

class Proof5184Tests(unittest.TestCase):
    def setUp(self):
        self.cells = cells()
        self.gates = [{"order": 0, "constraint_id": "HNAN-0",
                       "closed": True, "bypassed": True,
                       "gain": "1", "phase_written": False}]
        self.roots = {"pipeline_root": "P"*72, "graph_root": "G"*72}

    def proof(self):
        return prove_candidate_grid(self.cells, ordered_constraints=self.gates, **self.roots)

    def test_exact_replay(self):
        original = self.proof()
        self.assertEqual(original, verify_candidate_grid(
            self.cells, ordered_constraints=self.gates, claimed_proof=original, **self.roots))
        self.assertFalse(original["signed_vm81_admission_verified"])

    def test_position_swap_rejected(self):
        self.cells[4], self.cells[5] = self.cells[5], self.cells[4]
        with self.assertRaisesRegex(ValueError, "POSITION_ORDER"):
            self.proof()

    def test_bigint_serialization_rejected(self):
        self.cells[0]["bigint_decimal"] = "00"
        with self.assertRaisesRegex(ValueError, "NONCANONICAL"):
            self.proof()

    def test_hnan_phase_write_rejected(self):
        self.gates[0]["phase_written"] = True
        with self.assertRaisesRegex(ValueError, "HNAN_BYPASS"):
            self.proof()

    def test_authority_escalation_rejected(self):
        self.cells[17]["hash216_mint_authority"] = True
        with self.assertRaisesRegex(ValueError, "UNAUTHORIZED"):
            self.proof()

    def test_tampered_proof_rejected(self):
        prior = self.proof()
        self.cells[33]["bigint_decimal"] = "99999"
        with self.assertRaisesRegex(ValueError, "REPLAY_PROOF_MISMATCH"):
            verify_candidate_grid(self.cells, ordered_constraints=self.gates,
                                  claimed_proof=prior, **self.roots)

if __name__ == "__main__":
    unittest.main()
