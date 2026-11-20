import hashlib
import unittest

from hhs_runtime.hhs_pass220_module196_lean_source_identity_v1 import (
    ROOT, LEAN_PATH, build_module196_proof_identity,
)


class Module196LeanSourceIdentityTests(unittest.TestCase):
    def test_exact_source_identity_and_stable_replay(self):
        source = (ROOT / LEAN_PATH).read_bytes()
        digest = hashlib.sha256(source).hexdigest()
        first = build_module196_proof_identity(expected_sha256=digest)
        second = build_module196_proof_identity(source=source, expected_sha256=digest)
        self.assertEqual(first, second)
        self.assertEqual(first["source_sha256"], digest)
        self.assertEqual(len(first["theorem_identity_hash72"]), 72)
        self.assertEqual(len(first["dependency_identity_hash72"]), 72)
        self.assertNotEqual(first["theorem_identity_hash72"],
                            first["dependency_identity_hash72"])
        self.assertFalse(first["vm81_mutation_authority"])
        self.assertFalse(first["hash72_commit_authority"])
        self.assertFalse(first["hash216_persistence_authority"])

    def test_tampered_source_rejected(self):
        original = (ROOT / LEAN_PATH).read_bytes()
        digest = hashlib.sha256(original).hexdigest()
        with self.assertRaisesRegex(ValueError, "M196_LEAN_SOURCE_SHA256_MISMATCH"):
            build_module196_proof_identity(source=original + b"\n-- mutation\n",
                                            expected_sha256=digest)

    def test_unproved_declaration_rejected(self):
        original = (ROOT / LEAN_PATH).read_bytes()
        with self.assertRaisesRegex(ValueError, "M196_LEAN_UNCHECKED_PROOF_TERM"):
            build_module196_proof_identity(source=original + b"\ntheorem forged : True := by sorry\n")

    def test_missing_declaration_rejected(self):
        original = (ROOT / LEAN_PATH).read_bytes()
        with self.assertRaisesRegex(ValueError, "M196_LEAN_DECLARATIONS_MISSING"):
            build_module196_proof_identity(source=original.replace(
                b"theorem fractal_square", b"theorem renamed_fractal_square"))


if __name__ == "__main__":
    unittest.main()
