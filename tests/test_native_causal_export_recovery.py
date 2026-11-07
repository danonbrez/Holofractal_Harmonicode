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

    def test_install_purges_namespace_package_before_reinstall(self):
        versions = dict(module.EXPECTED_RUNTIME_VERSIONS)
        purged = ["/venv/lib/python3.12/site-packages/transformers"]
        with patch.object(module, "_installed_versions", return_value=versions), \
             patch.object(module, "_torch_cpu_runtime", return_value={"ready": True}), \
             patch.object(module, "_transformers_exports_ready", side_effect=[False, True]), \
             patch.object(
                 module,
                 "_purge_broken_transformers_installations",
                 return_value=purged,
             ) as purge, \
             patch.object(module, "_run_pip") as pip:
            result = module._install_runtime()
        purge.assert_called_once_with()
        pip.assert_called_once()
        self.assertEqual(result["purged_broken_transformers"], purged)

    def test_purge_removes_only_broken_transformers_payloads(self):
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            site = Path(raw)
            namespace_shadow = site / "transformers"
            namespace_shadow.mkdir()
            (namespace_shadow / "py.typed").write_text("", encoding="utf-8")
            orphan_dist_info = site / "transformers-4.57.6.dist-info"
            orphan_dist_info.mkdir()
            valid_dist_info = site / "transformers-9.9.9.dist-info"
            valid_dist_info.mkdir()
            (valid_dist_info / "RECORD").write_text("", encoding="utf-8")
            valid_package = site / "otherpkg"
            valid_package.mkdir()
            (valid_package / "__init__.py").write_text("", encoding="utf-8")

            with patch.object(module, "_site_package_paths", return_value=[site]):
                broken = module._broken_transformers_installations()
                purged = module._purge_broken_transformers_installations()

            self.assertEqual(broken, [namespace_shadow])
            self.assertIn(str(namespace_shadow), purged)
            self.assertIn(str(orphan_dist_info), purged)
            self.assertFalse(namespace_shadow.exists())
            self.assertFalse(orphan_dist_info.exists())
            self.assertTrue(valid_dist_info.exists())
            self.assertTrue(valid_package.exists())

    def test_purge_preserves_importable_transformers_package(self):
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            site = Path(raw)
            package = site / "transformers"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            with patch.object(module, "_site_package_paths", return_value=[site]):
                self.assertEqual(module._broken_transformers_installations(), [])
                self.assertEqual(module._purge_broken_transformers_installations(), [])
            self.assertTrue(package.exists())

    def test_resolution_diagnostic_reports_namespace_origin(self):
        completed = subprocess.CompletedProcess(
            [], 0,
            stdout='{"origin": null, "submodule_search_locations": ["/x/transformers"]}\n',
            stderr="",
        )
        with patch.object(module.subprocess, "run", return_value=completed):
            payload = module._transformers_resolution_diagnostic()
        self.assertIsNone(payload["origin"])
        self.assertEqual(payload["submodule_search_locations"], ["/x/transformers"])

    def test_persistent_failure_reports_resolution_diagnostic(self):
        versions = dict(module.EXPECTED_RUNTIME_VERSIONS)
        with patch.object(module, "_installed_versions", return_value=versions), \
             patch.object(module, "_torch_cpu_runtime", return_value={"ready": True}), \
             patch.object(module, "_transformers_exports_ready", return_value=False), \
             patch.object(module, "_purge_broken_transformers_installations", return_value=[]), \
             patch.object(module, "_run_pip"), \
             patch.object(
                 module,
                 "_transformers_resolution_diagnostic",
                 return_value={"origin": None},
             ):
            with self.assertRaises(RuntimeError) as raised:
                module._install_runtime()
        self.assertIn("transformers_resolution=", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
