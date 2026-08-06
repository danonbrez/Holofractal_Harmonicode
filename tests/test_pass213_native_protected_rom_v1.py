from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    protect_compiled_rom_entry,
)
from hhs_backend.runtime.hhs_pass213_secure_memory_v1 import (
    Pass213SecureMemoryError,
)
from tests.test_pass213_recovery_admission_v1 import compiled_entry

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
ROOT_KEY = bytes(range(32))
ADMISSION_KEY = bytes(reversed(range(32)))


class Pass213Iteration3NativeProtectedROMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory(prefix="pass213-native-rom-")
        cls.library = Path(cls._temp.name) / "libhhs_pass213_secure_arena.so"
        subprocess.run(
            [
                "cc", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", str(SOURCE),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def store(self) -> NativeProtectedCompiledROMStore:
        return NativeProtectedCompiledROMStore(
            library_path=self.library,
            admission_key=ADMISSION_KEY,
            memory_root_key=ROOT_KEY,
            owner_id="PASS213_NATIVE_ROM_TEST",
        )

    def test_recovered_entry_is_stored_in_sealed_native_arena(self) -> None:
        entry = compiled_entry("SECURE_NATIVE_ROM_V1")
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        store = self.store()
        try:
            record = store.inspect_correct_protect_and_admit(carrier)
            self.assertEqual(record.entry_hash216, entry.entry_hash216)
            self.assertEqual(store.lookup_hash216(entry.entry_hash216), entry)
            self.assertEqual(store.lookup_operation(entry.operation_id), entry)
            self.assertEqual(len(store), 1)
            self.assertEqual(len(store.inventory_root()), 64)
        finally:
            receipts = store.close()
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0].event, "DESTROY")
        self.assertTrue(receipts[0].details["zeroized_before_release"])

    def test_store_requires_recovered_admission(self) -> None:
        store = self.store()
        try:
            with self.assertRaisesRegex(
                Pass213SecureMemoryError,
                "RECOVERED_ROM_ADMISSION_REQUIRED",
            ):
                store.admit(compiled_entry())  # type: ignore[arg-type]
        finally:
            store.close()

    def test_identical_admission_is_idempotent(self) -> None:
        entry = compiled_entry("SECURE_NATIVE_DUPLICATE_V1")
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        store = self.store()
        try:
            first = store.inspect_correct_protect_and_admit(carrier)
            second = store.inspect_correct_protect_and_admit(carrier)
            self.assertEqual(second, first)
            self.assertEqual(len(store), 1)
        finally:
            store.close()

    def test_closed_store_rejects_lookup(self) -> None:
        store = self.store()
        store.close()
        with self.assertRaisesRegex(
            Pass213SecureMemoryError,
            "STORE_CLOSED",
        ):
            store.inventory_root()


if __name__ == "__main__":
    unittest.main()
