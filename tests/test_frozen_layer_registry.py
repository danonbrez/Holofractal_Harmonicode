"""Focused negative-case checks for scoped registry guard."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/check_frozen_layer_registry.py"
spec = importlib.util.spec_from_file_location("registry_guard", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RegistryTests(unittest.TestCase):
    def registry(self, paths):
        return {"schema": "hhs.frozen-layer-registry.v1",
                "protected": [{"path": p} for p in paths]}

    def read(self, value):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "registry.json"
            file.write_text(json.dumps(value), encoding="utf-8")
            return module.load_paths(file)

    def test_all_baseline_paths_present(self):
        self.assertEqual(self.read(self.registry(sorted(module.BASELINE))), module.BASELINE)

    def test_registry_expansion(self):
        paths = sorted(module.BASELINE) + ["hhs_runtime/new_frozen_module.py"]
        self.assertIn("hhs_runtime/new_frozen_module.py", self.read(self.registry(paths)))

    def test_missing_baseline_rejected(self):
        with self.assertRaises(ValueError):
            self.read(self.registry([]))

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            self.read(self.registry(sorted(module.BASELINE) * 2))

    def test_parent_traversal_rejected(self):
        with self.assertRaises(ValueError):
            self.read(self.registry(sorted(module.BASELINE) + ["../escape.py"]))

    def test_missing_schema_rejected(self):
        with self.assertRaises(ValueError):
            self.read({"protected": [{"path": p} for p in module.BASELINE]})

    def test_exact_path_violation(self):
        self.assertEqual(module.evaluate(set(module.BASELINE), module.BASELINE),
                         sorted(module.BASELINE))

    def test_new_extension_not_blocked(self):
        self.assertEqual(module.evaluate(["hhs_runtime/new_extension.py"], module.BASELINE), [])

if __name__ == "__main__":
    unittest.main()
