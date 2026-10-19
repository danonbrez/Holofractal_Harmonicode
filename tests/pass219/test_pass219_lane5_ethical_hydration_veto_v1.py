import unittest
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import _lane5_hydration_ethical_veto

class Lane5HydrationEthicalTests(unittest.TestCase):
    def evidence(self):
        return {
            **{key: True for key in (
                "typed_ingress_verified", "inherited_lanes_1_4_verified",
                "constructor_provenance_verified", "ordered_tensor_gates_verified",
                "external_interface_equivalent", "scope_and_consent_verified",
                "verification_procedures_bound", "temporary_harness_release_planned",
                "hydration_precedes_composition", "conway_candidate_only",
            )},
            **{key: False for key in (
                "direct_canonical_mutation_authority", "direct_hash72_mint_authority",
                "direct_hash216_mint_authority", "direct_persistence_authority",
            )},
            "pipeline_root_hash72": "P"*72,
            "constructor_graph_root_hash72": "G"*72,
        }

    def test_complete_candidate_is_not_authority(self):
        r = _lane5_hydration_ethical_veto(self.evidence())
        self.assertFalse(r["vetoed"])
        self.assertFalse(r["native_constructor_admitted"])
        self.assertFalse(r["canonical_mint_authority"])

    def test_missing_hydration_blocks(self):
        e = self.evidence()
        e["hydration_precedes_composition"] = False
        self.assertIn("hydration_precedes_composition", _lane5_hydration_ethical_veto(e)["unresolved_constraints"])

    def test_lost_interface_equivalence_blocks(self):
        e = self.evidence()
        e["external_interface_equivalent"] = False
        self.assertTrue(_lane5_hydration_ethical_veto(e)["vetoed"])

    def test_canonical_mint_escalation_blocks(self):
        e = self.evidence()
        e["direct_hash216_mint_authority"] = True
        self.assertIn("direct_hash216_mint_authority", _lane5_hydration_ethical_veto(e)["unresolved_constraints"])

    def test_missing_root_blocks(self):
        e = self.evidence()
        e["constructor_graph_root_hash72"] = ""
        self.assertTrue(_lane5_hydration_ethical_veto(e)["vetoed"])

    def test_candidate_conway_only(self):
        e = self.evidence()
        e["conway_candidate_only"] = False
        self.assertTrue(_lane5_hydration_ethical_veto(e)["vetoed"])

if __name__ == "__main__":
    unittest.main()
