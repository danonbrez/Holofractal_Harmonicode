import unittest
from hhs_runtime.hhs_service_contract_gap_triage_v1 import triage_error, verify_triage, correlate_service_gap, EXACT_STATUS

class TriageTests(unittest.TestCase):
    def setUp(self):
        self.args=dict(service_name="lane5.example",code=5,
                       origin="native_cell_wall.route",
                       observed_boundary="cpp_cell_wall",
                       contract_path="contracts/pass219/example.md",
                       implementation_path="hhs_runtime/cpp/example.cpp")

    def test_registry_and_hydration_correlation(self):
        triage=triage_error(**self.args)
        services=[{"name":"lane5.example","module":"hhs.native","function":"run",
                   "contract_schemas":["ABI"],"guards":["SIGNED_VM81"]}]
        node={"service_name":"lane5.example","hash216":"H"*216}
        result=correlate_service_gap(triage=triage,services=services,hydration_nodes=[node])
        self.assertTrue(result["hydration_record_found"])
        self.assertFalse(result["hydration_proof_verified"])
        self.assertFalse(result["first_violation_verified"])
        self.assertEqual(result["registry_function"],"run")
        absent=correlate_service_gap(triage=triage,services=services,hydration_nodes=[])
        self.assertFalse(absent["hydration_record_found"])
        with self.assertRaisesRegex(ValueError,"SERVICE_INDEX_MISSING"):
            correlate_service_gap(triage=triage,services=[],hydration_nodes=[node])
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS_LANE5"):
            correlate_service_gap(triage=triage,services=services,hydration_nodes=[node,node])

    def test_exact_status_identities(self):
        self.assertEqual(EXACT_STATUS[5],"HHS_EXACT_STATUS_INVARIANT_FAILURE")
        self.assertEqual(EXACT_STATUS[4],"HHS_EXACT_STATUS_VERSION_MISMATCH")

    def test_replay_and_no_false_proof(self):
        record=triage_error(**self.args)
        self.assertTrue(verify_triage(record,**self.args))
        self.assertFalse(record["earliest_violated_boundary_verified"])
        self.assertFalse(record["deployed_ui_e2e_verified"])
        modified=dict(record, cpp_cell_wall_witness_verified=True)
        with self.assertRaisesRegex(ValueError,"TRIAGE_REPLAY_MISMATCH"):
            verify_triage(modified,**self.args)

    def test_unknown_native_code_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_EXACT_STATUS_CODE"):
            triage_error(**dict(self.args,code=134))

    def test_domain_code_kept_without_guessing(self):
        record=triage_error(**dict(self.args,code="ERS_CUSTOM_GATE_FAILURE"))
        self.assertEqual(record["emitted_code"],"ERS_CUSTOM_GATE_FAILURE")
        self.assertIn("UNRESOLVED",record["code_registry"])

if __name__=="__main__":
    unittest.main()
