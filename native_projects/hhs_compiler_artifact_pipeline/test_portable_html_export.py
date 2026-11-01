"""Portable HTML export contract checks. Run: python -m unittest discover -s native_projects/hhs_compiler_artifact_pipeline -p 'test_portable_html_export.py'"""
import hashlib
import unittest
from portable_html_export import package_html, ExportContractError, REQUIRED

DOC = "<!doctype html><html><head></head><body>offline</body></html>"
RUNTIME = """globalThis.HHSPortableVM81={
  admit(){},receiptHash72(){},verifyHash216(){},hydrateLane5(){},
  transition(){},selfTest(){return true}
};"""
def manifest():
    return dict(capabilities={name:True for name in REQUIRED},
                runtime_sha256=hashlib.sha256(RUNTIME.encode()).hexdigest(),
                canonical_source_commit="known-test-commit",
                selftest_vector_sha256="known-test-witness")

class TestPortableExport(unittest.TestCase):
    def test_embeds_runtime_and_manifest(self):
        result=package_html(DOC,RUNTIME,manifest())
        self.assertIn('hhs-portable-vm81-runtime',result)
        self.assertIn('HHS_EXPORT_RUNTIME_SELFTEST_FAILED',result)
        self.assertNotIn('src="',result)
    def test_rejects_missing_native_capabilities(self):
        m=manifest()
        m["capabilities"]["hash216_replay"]=False
        with self.assertRaisesRegex(ExportContractError,"hash216_replay"):
            package_html(DOC,RUNTIME,m)
    def test_rejects_runtime_digest_mismatch(self):
        with self.assertRaisesRegex(ExportContractError,"SHA-256"):
            package_html(DOC,RUNTIME+" ",manifest())
    def test_rejects_missing_provenance(self):
        m=manifest()
        m.pop("canonical_source_commit")
        with self.assertRaisesRegex(ExportContractError,"source commit"):
            package_html(DOC,RUNTIME,m)
    def test_rejects_html_breakout(self):
        with self.assertRaisesRegex(ExportContractError,"script terminator"):
            package_html(DOC,RUNTIME+"</script>",manifest())
if __name__=="__main__":
    unittest.main()
