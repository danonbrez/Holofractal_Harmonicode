import unittest
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import _lane5_hydration_ethical_veto

class Lane5HydrationEthicalTests(unittest.TestCase):
    def evidence(self):
        return {
            **{key: True for key in (
                "typed_ingress_verified", "inherited_lanes_1_4_verified",
                "constructor_provenance_verified", "ordered_tensor_gates_verified",
                "external_interface_equivalent", "external_input_type_verified",
                "external_output_type_verified", "observable_behavior_verified",
                "scope_and_consent_verified",
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

    def test_independent_input_output_behavior_checks(self):
        for key in ("external_input_type_verified",
                    "external_output_type_verified",
                    "observable_behavior_verified"):
            evidence = self.evidence()
            evidence[key] = False
            result = _lane5_hydration_ethical_veto(evidence)
            self.assertTrue(result["vetoed"])
            self.assertIn(key, result["unresolved_constraints"])

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


    def test_rejected_candidate_never_enters_authorized_tick(self):
        from unittest.mock import patch, Mock
        from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import admit_and_execute_local
        from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import EthicalDecision
        approved = Mock()
        approved.evaluation.decision = EthicalDecision.EXECUTE_LOCAL_PROVISIONAL
        approved.evaluation.scope.effective_scope = ()
        approved.to_dict.return_value = {"checked": True}
        approved.trace_receipt_hash72 = "A" * 72
        controller = Mock()
        evidence = self.evidence()
        evidence["external_interface_equivalent"] = False
        with patch("hhs_runtime.hhs_pass219_vm81_admission_bridge_v1.evaluate_action_v2", return_value=approved):
            result = admit_and_execute_local(
                Mock(), [], Mock(), controller=controller,
                lane5_hydration_evidence=evidence,
            )
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["lane5_hydration_ethical_gate"]["vetoed"])
        self.assertFalse(result["canonical_vm81_mutation_performed"])
        controller.authorized_tick.assert_not_called()

    def test_valid_candidate_does_not_bypass_ethics_denial(self):
        from unittest.mock import patch, Mock
        from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import admit_and_execute_local
        from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import EthicalDecision
        denied = Mock()
        denied.evaluation.decision = EthicalDecision.HOLD
        denied.evaluation.scope.effective_scope = ()
        denied.to_dict.return_value = {"checked": True}
        controller = Mock()
        with patch("hhs_runtime.hhs_pass219_vm81_admission_bridge_v1.evaluate_action_v2", return_value=denied):
            result = admit_and_execute_local(
                Mock(), [], Mock(), controller=controller,
                lane5_hydration_evidence=self.evidence(),
            )
        self.assertFalse(result["execution_allowed"])
        controller.authorized_tick.assert_not_called()

if __name__ == "__main__":
    unittest.main()
