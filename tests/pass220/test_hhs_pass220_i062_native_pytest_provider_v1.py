from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from hhs_runtime.testing.native_pytest_provider_v1 import (
    EXIT_OK,
    NativePytestProvider,
)


ROOT = Path(__file__).resolve().parents[2]
SPECIMEN = ROOT / "tests" / "pass220" / "i062_native_pytest_specimen"
PROVIDER = ROOT / "hhs_runtime" / "testing" / "native_pytest_provider_v1.py"
TRANSACTION = ROOT / "hhs_installer" / "transaction.py"


class NativePytestProviderTests(unittest.TestCase):
    def test_specimen_core_compatibility(self) -> None:
        run = NativePytestProvider(ROOT).run(
            [str(SPECIMEN.relative_to(ROOT))]
        )
        self.assertEqual(run.exit_code, EXIT_OK)
        outcomes = [result.outcome for result in run.results]
        self.assertEqual(outcomes.count("PASS"), 4)
        self.assertEqual(outcomes.count("SKIP"), 1)
        self.assertEqual(outcomes.count("XFAIL"), 1)
        self.assertEqual(len(run.receipt_hash216), 216)
        self.assertFalse(run.authority["external_pytest_execution"])

    def test_receipt_is_deterministic(self) -> None:
        selector = str(SPECIMEN.relative_to(ROOT))
        first = NativePytestProvider(ROOT).run([selector])
        second = NativePytestProvider(ROOT).run([selector])
        self.assertEqual(first.config_hash72, second.config_hash72)
        self.assertEqual(first.collection_hash72, second.collection_hash72)
        self.assertEqual(first.result_hash72, second.result_hash72)
        self.assertEqual(first.receipt_hash216, second.receipt_hash216)

    def test_keyword_and_collect_only(self) -> None:
        selector = str(SPECIMEN.relative_to(ROOT))
        run = NativePytestProvider(ROOT).run(
            [selector],
            keyword="raises",
            collect_only=True,
        )
        self.assertEqual(run.exit_code, EXIT_OK)
        self.assertEqual(run.selected, 1)
        self.assertEqual(run.results, ())

    def test_failure_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "test_failure.py"
            path.write_text(
                "def test_failure():\n    assert False, 'native failure'\n",
                encoding="utf-8",
            )
            run = NativePytestProvider(root).run(["test_failure.py"])
            self.assertEqual(run.exit_code, 1)
            self.assertEqual(run.results[0].outcome, "FAIL")

    def test_native_provider_has_no_external_pytest_execution(self) -> None:
        source = PROVIDER.read_text(encoding="utf-8")
        self.assertNotIn("import pytest", source)
        self.assertNotIn('"-m", "pytest"', source)
        self.assertNotIn("subprocess", source)

    def test_installer_uses_native_provider(self) -> None:
        source = TRANSACTION.read_text(encoding="utf-8")
        self.assertIn(
            '"-m", "hhs_runtime.testing.native_pytest_provider_v1", "-q"',
            source,
        )
        self.assertNotIn('[str(python), "-m", "pytest", "-q", *selected]', source)


if __name__ == "__main__":
    unittest.main()
