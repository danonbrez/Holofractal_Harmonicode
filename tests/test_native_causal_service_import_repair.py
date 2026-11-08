"""Regression tests for the service-UID native causal import probe."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / "tools/diagnose_native_causal_service_import.py"
spec = importlib.util.spec_from_file_location("native_causal_service_probe", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NativeCausalServiceImportProbeTests(unittest.TestCase):
    def test_unimportable_auto_tokenizer_fails_closed(self):
        incomplete = types.ModuleType("transformers")
        with patch.dict(sys.modules, {"transformers": incomplete}):
            result = module.probe()
        self.assertFalse(result["ok"])
        self.assertEqual(result["schema"], "HHS_NATIVE_CAUSAL_SERVICE_IMPORT_PROBE_V1")
        self.assertEqual(result["error_type"], "ImportError")
        self.assertIn("AutoConfig", result["error"])

    def test_resolution_evidence_is_read_only_and_contains_namespace_paths(self):
        incomplete = types.ModuleType("transformers")
        fake_spec = types.SimpleNamespace(origin=None, submodule_search_locations=["/tmp/namespace"])
        with patch.dict(sys.modules, {"transformers": incomplete}), patch.object(module.importlib.util, "find_spec", return_value=fake_spec):
            result = module.probe()
        self.assertIn("resolution_paths", result)
        self.assertTrue(result["resolution_paths"])
        self.assertIn("site_package_paths", result)
        self.assertEqual(result["module_specs"]["transformers"]["search_locations"], ["/tmp/namespace"])
        self.assertFalse(result["ok"])

    def test_workflow_retries_under_service_identity_not_root_only(self):
        workflow = (PATH.parents[1] / ".github/workflows/digitalocean-production-main.yml").read_text(encoding="utf-8")
        self.assertIn('runuser -u hhs -- env PYTHONPATH="$APP_ROOT"', workflow)
        self.assertGreaterEqual(workflow.count("diagnose_native_causal_service_import.py"), 2)
        self.assertIn("--install --force-transformers-reinstall", workflow)
        self.assertIn("rejecting production acceptance", workflow)


if __name__ == "__main__":
    unittest.main()
