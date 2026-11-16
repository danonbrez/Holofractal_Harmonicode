"""Verify Pass160 link repair after immutable source checksum verification."""
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "native_projects/hhs_pass160_validated_transition_runtime"
MAKE = BASE / "assets/source_capsule/Makefile.materialized.repair-forward"
OVERLAY = BASE / "assets/source_capsule/apply_crypto_link_overlay.py"

class TestPass160CryptoLinkRepair(unittest.TestCase):
    def test_generated_build_overlay_preserves_source(self):
        original = MAKE.read_text(encoding="utf-8")
        apply_overlay = runpy.run_path(str(OVERLAY))["apply_overlay"]
        fixed = apply_overlay(original)
        self.assertNotIn("CRYPTO_LIBS ?= -lcrypto", original)
        self.assertIn("CRYPTO_LIBS ?= -lcrypto", fixed)
        for rule in (
            "$(DIST)/libhhs_pass160.so:",
            "$(DIST)/hhs-pass160:",
            "$(DIST)/hhs-pass160-verify:",
            "$(DIST)/hhs-pass160-performance:",
            "sanitizer:",
        ):
            self.assertIn(rule, original)
            self.assertIn(rule, fixed)
        self.assertEqual(fixed.count("$(CRYPTO_LIBS)"), 5)
        self.assertEqual(apply_overlay(fixed), fixed)
        self.assertEqual(MAKE.read_text(encoding="utf-8"), original)

    def test_original_capsule_verified_before_generated_overlay(self):
        root_make = (BASE / "Makefile").read_text(encoding="utf-8")
        self.assertIn("NATIVE_SHA256 := f14c0f49cd6cd0c627d546279c38066968140debcc3911c95af0b42f95a22270", root_make)
        self.assertIn("verify-transport:", root_make)
        self.assertIn("sha256sum -c '$(REFERENCE_SUMS)'", root_make)
        copied = root_make.index("cp assets/source_capsule/Makefile.materialized.repair-forward Makefile.materialized")
        overlay = root_make.index("python3 assets/source_capsule/apply_crypto_link_overlay.py Makefile.materialized")
        self.assertLess(copied, overlay)

    def test_overlay_fails_closed_if_pinned_recipe_is_unrecognizable(self):
        apply_overlay = runpy.run_path(str(OVERLAY))["apply_overlay"]
        with self.assertRaisesRegex(ValueError, "BASELINE_MISMATCH"):
            apply_overlay("not a Pass160 Makefile")
        with self.assertRaisesRegex(ValueError, "PARTIAL_CRYPTO_OVERLAY"):
            apply_overlay("CRYPTO_LIBS ?= -lcrypto\n")


if __name__ == "__main__":
    unittest.main()
