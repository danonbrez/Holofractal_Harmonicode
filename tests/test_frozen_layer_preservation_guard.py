"""Regression tests for the initial scoped frozen-layer source guard."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_frozen_layer_preservation.py"
SPEC = importlib.util.spec_from_file_location("frozen_guard", PATH)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class FrozenGuardTests(unittest.TestCase):
    def test_closed_native_change_blocked(self):
        path = "hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py"
        self.assertEqual(guard.violations({path}), [path])

    def test_hash72_change_blocked(self):
        path = "hhs_runtime/hhs_hash72_signing_layer_v1.py"
        self.assertEqual(guard.violations({path}), [path])

    def test_higher_order_addition_allowed_at_source_diff_gate(self):
        self.assertEqual(guard.violations({"hhs_runtime/new_composition.py"}), [])

    def test_similar_name_not_wrongfully_blocked(self):
        self.assertEqual(
            guard.violations({"hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py.extra"}),
            [],
        )

    def test_multiple_violations_sorted(self):
        self.assertEqual(
            guard.violations(set(guard.PROTECTED_EXACT_PATHS)),
            sorted(guard.PROTECTED_EXACT_PATHS),
        )

    def test_empty_base_or_head_is_rejected(self):
        with self.assertRaises(ValueError):
            guard.changed_paths("", "head")


if __name__ == "__main__":
    unittest.main()
