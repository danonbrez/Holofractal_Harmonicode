"""Additive Pass160 linker receipt: frozen source hashes remain unchanged."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "native_projects/hhs_pass160_validated_transition_runtime"
MAKE = BASE / "assets/source_capsule/Makefile.materialized.repair-forward"


class TestPass160CryptoLinkRepair(unittest.TestCase):
    def test_repair_forward_link_targets_include_crypto(self):
        source = MAKE.read_text(encoding="utf-8")
        self.assertIn("CRYPTO_LIBS ?= -lcrypto", source)
        for rule in (
            "$(DIST)/libhhs_pass160.so:",
            "$(DIST)/hhs-pass160:",
            "$(DIST)/hhs-pass160-verify:",
            "$(DIST)/hhs-pass160-performance:",
            "sanitizer:",
        ):
            self.assertIn(rule, source)
        self.assertEqual(source.count("$(CRYPTO_LIBS)"), 5)
        self.assertIn("$(CC) -shared $^ -o $@ $(CRYPTO_LIBS)", source)

    def test_original_source_capsule_identity_remains_pinned(self):
        root_make = (BASE / "Makefile").read_text(encoding="utf-8")
        self.assertIn("NATIVE_SHA256 := f14c0f49cd6cd0c627d546279c38066968140debcc3911c95af0b42f95a22270", root_make)
        self.assertIn("verify-transport:", root_make)
        self.assertIn("Makefile.materialized.repair-forward Makefile.materialized", root_make)


if __name__ == "__main__":
    unittest.main()
