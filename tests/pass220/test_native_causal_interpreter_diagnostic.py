import unittest
from unittest.mock import patch
from tools import diagnose_native_causal_interpreter as module

class DiagnosticTests(unittest.TestCase):
    def test_report_contract(self):
        result=module.probe()
        self.assertIsInstance(result["interpreter"],str)
        self.assertIn("transformers",result["packages"])
        self.assertIn("torch",result["packages"])
        self.assertIn("tokenizers",result["packages"])
        self.assertIsInstance(result["errors"],list)
        self.assertIsInstance(result["model_imports_resolved"],bool)

if __name__=="__main__":
    unittest.main()
