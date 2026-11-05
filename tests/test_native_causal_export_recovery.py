"""Regression coverage for broken pinned transformers exports in production."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / "tools/provision_native_causal_model.py"
spec = importlib.util.spec_from_file_location("native_causal_provision_test", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RuntimeExportRecoveryTests(unittest.TestCase):
    def test_export_probe_checks_actual_imports_in_fresh_interpreter(self):
        with patch.object(module.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)) as run:
            self.assertFalse(module._transformers_exports_ready())
            command = run.call_args.args[0]
            self.assertEqual(command[:2], [sys.executable, "-c"])
            self.assertIn("AutoTokenizer", command[2])
            self.assertIn("AutoModelForCausalLM", command[2])

    def test_pinned_versions_do_not_mask_broken_exports(self):
        versions = dict(module.EXPECTED_RUNTIME_VERSIONS)
        with patch.object(module, "_installed_versions", return_value=versions), \
             patch.object(module, "_torch_cpu_runtime", return_value={"ready": True}), \
             patch.object(module, "_transformers_exports_ready", return_value=False):
            self.assertFalse(module._runtime_ready())

    def test_install_reinstalls_broken_transformers_even_when_pinned(self):
        versions = dict(module.EXPECTED_RUNTIME_VERSIONS)
        with patch.object(module, "_installed_versions", return_value=versions), \
             patch.object(module, "_torch_cpu_runtime", return_value={"ready": True}), \
             patch.object(module, "_transformers_exports_ready", side_effect=[False, True]), \
             patch.object(module, "_run_pip") as pip:
            result = module._install_runtime()
        pip.assert_called_once()
        self.assertEqual(pip.call_args.args[0][:2], ["--force-reinstall", "--requirement"])
        self.assertTrue(result["exact_versions_verified"])


if __name__ == "__main__":
    unittest.main()
