"""Guard exact typed signed environmental admission handoff from synthetic candidates."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts/pass220/HHS_ADMIN_SQL_LANE5_SIGNED_VM81_HANDOFF_V1.json"


class TestHandoff(unittest.TestCase):
    def test_native_signature_and_no_candidate_escalation(self):
        contract = json.loads(CONTRACT.read_text())
        self.assertEqual(contract["state"], "CANDIDATE_READY_ADMISSION_OPEN")
        self.assertEqual(contract["verification"]["state"], "OPEN")
        native = contract["canonical_entrypoint"]
        header = (ROOT / native["header"]).read_text()
        signature = header[header.index(native["symbol"]):]
        for parameter in native["inputs"] + native["outputs"]:
            name = parameter.split(":", 1)[0]
            self.assertIn(name, signature)
        self.assertIn("HHSExactStatus", header)
        for boundary in contract["hard_boundaries"]:
            self.assertTrue(boundary)
        self.assertIn("source_sha256 exact bytes", contract["candidate_source"]["required_evidence"])
        self.assertIn("canonical_hash216_admitted false", contract["candidate_source"]["required_evidence"])
        self.assertIn("Hash72 Hash216 canonical receipts and replay", contract["verification"]["pending"])

    def test_no_forged_environmental_admission_in_staging_router(self):
        source = (ROOT / "hhs_backend/api/hhs_admin_source_stream_routes_v1.py").read_text()
        self.assertIn("continue_staged_to_lane5", source)
        self.assertNotIn("hhs_exact_pass219_vm81_environment_admit_signed(", source)
        self.assertNotIn("canonical_hash216_admitted = True", source)


if __name__ == "__main__":
    unittest.main()
