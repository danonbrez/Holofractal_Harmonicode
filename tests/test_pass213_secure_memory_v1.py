from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_secure_memory_v1 import (
    NativeSecureArena,
    Pass213SecureMemoryError,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
ROOT_KEY = bytes(range(32))


class Pass213Iteration3SecureMemoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory(prefix="pass213-secure-memory-")
        cls.library = Path(cls._temp.name) / "libhhs_pass213_secure_arena.so"
        subprocess.run(
            [
                "cc",
                "-std=c11",
                "-shared",
                "-fPIC",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(SOURCE),
                "-o",
                str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def arena(self, size: int = 4096, sequence: int = 1) -> NativeSecureArena:
        return NativeSecureArena(
            library_path=self.library,
            requested_size=size,
            owner_id="PASS213_TEST_OWNER",
            root_key=ROOT_KEY,
            allocation_sequence=sequence,
        )

    def test_allocation_applies_native_protection(self) -> None:
        arena = self.arena()
        try:
            status = arena.status()
            self.assertTrue(status["locked"])
            self.assertTrue(status["dontdump"])
            self.assertTrue(status["dontfork"])
            self.assertEqual(status["guard_pages"], 2)
            self.assertFalse(status["sealed"])
            self.assertTrue(status["zeroized"])
            self.assertFalse(status["executable"])
            self.assertGreaterEqual(
                status["mapping_size"],
                status["usable_size"] + 2 * status["page_size"],
            )
            self.assertEqual(arena.receipts[0].event, "ALLOCATE")
        finally:
            arena.close()

    def test_write_read_seal_and_zeroize(self) -> None:
        arena = self.arena()
        try:
            payload = b"compiled-rom-entry-v1"
            write_receipt = arena.write(payload, offset=32)
            self.assertEqual(write_receipt.event, "WRITE")
            self.assertEqual(
                arena.read_internal(offset=32, length=len(payload)),
                payload,
            )
            seal_receipt = arena.seal()
            self.assertEqual(seal_receipt.event, "SEAL")
            with self.assertRaisesRegex(
                Pass213SecureMemoryError,
                "HHS_SECURE_ESEALED",
            ):
                arena.write(b"x", offset=0)
            zeroize_receipt = arena.zeroize()
            self.assertEqual(zeroize_receipt.event, "ZEROIZE")
            self.assertTrue(arena.is_zero())
            self.assertEqual(
                arena.read_internal(offset=32, length=len(payload)),
                b"\0" * len(payload),
            )
            self.assertTrue(arena.status()["sealed"])
        finally:
            arena.close()

    def test_bounds_rejected_by_native_arena(self) -> None:
        arena = self.arena(size=64)
        try:
            with self.assertRaisesRegex(
                Pass213SecureMemoryError,
                "HHS_SECURE_EBOUNDS",
            ):
                arena.write(b"abc", offset=63)
            with self.assertRaisesRegex(
                Pass213SecureMemoryError,
                "HHS_SECURE_EBOUNDS",
            ):
                arena.read_internal(offset=64, length=1)
        finally:
            arena.close()

    def test_receipts_form_deterministic_chain_without_payload(self) -> None:
        arena = self.arena(sequence=17)
        try:
            arena.write(b"secret-cache-record")
            arena.seal()
            arena.zeroize()
            receipts = arena.receipts
            self.assertEqual(
                [item.event for item in receipts],
                ["ALLOCATE", "WRITE", "SEAL", "ZEROIZE"],
            )
            for previous, current in zip(receipts, receipts[1:]):
                self.assertEqual(
                    current.previous_receipt_hash216,
                    previous.receipt_hash216,
                )
            rendered = repr([item.to_dict() for item in receipts])
            self.assertNotIn("secret-cache-record", rendered)
            self.assertNotIn("address", rendered)
        finally:
            arena.close()

    def test_close_zeroizes_before_destroy(self) -> None:
        arena = self.arena()
        arena.write(b"destroy-me")
        destroy = arena.close()
        self.assertIsNotNone(destroy)
        assert destroy is not None
        self.assertEqual(destroy.event, "DESTROY")
        self.assertTrue(destroy.details["zeroized_before_release"])
        self.assertIsNone(arena.close())
        with self.assertRaisesRegex(
            Pass213SecureMemoryError,
            "ARENA_CLOSED",
        ):
            arena.status()

    def test_context_manager_destroys_arena(self) -> None:
        with self.arena() as arena:
            arena.write(b"context")
            arena_id = arena.arena_id_hash216
        self.assertEqual(arena.receipts[-1].event, "DESTROY")
        self.assertEqual(arena.receipts[-1].arena_id_hash216, arena_id)

    def test_same_allocation_context_has_same_logical_arena_id(self) -> None:
        first = self.arena(sequence=9)
        second = self.arena(sequence=9)
        try:
            self.assertEqual(
                first.arena_id_hash216,
                second.arena_id_hash216,
            )
        finally:
            first.close()
            second.close()

    def test_different_allocation_sequence_changes_arena_id(self) -> None:
        first = self.arena(sequence=9)
        second = self.arena(sequence=10)
        try:
            self.assertNotEqual(
                first.arena_id_hash216,
                second.arena_id_hash216,
            )
        finally:
            first.close()
            second.close()

    def test_native_owner_token_rejection(self) -> None:
        library = ctypes.CDLL(str(self.library))
        token_pointer = ctypes.POINTER(ctypes.c_uint8)
        library.hhs_secure_arena_create.argtypes = [
            ctypes.c_size_t,
            token_pointer,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        library.hhs_secure_arena_create.restype = ctypes.c_int
        library.hhs_secure_arena_status_get.argtypes = [
            ctypes.c_void_p,
            token_pointer,
            ctypes.c_void_p,
        ]
        library.hhs_secure_arena_status_get.restype = ctypes.c_int
        library.hhs_secure_arena_destroy.argtypes = [
            ctypes.c_void_p,
            token_pointer,
        ]
        library.hhs_secure_arena_destroy.restype = ctypes.c_int

        token_type = ctypes.c_uint8 * 32
        owner = token_type(*([1] * 32))
        attacker = token_type(*([2] * 32))
        handle = ctypes.c_void_p()
        self.assertEqual(
            library.hhs_secure_arena_create(
                4096,
                owner,
                ctypes.byref(handle),
            ),
            0,
        )
        try:
            status_buffer = ctypes.create_string_buffer(256)
            self.assertEqual(
                library.hhs_secure_arena_status_get(
                    handle,
                    attacker,
                    ctypes.cast(status_buffer, ctypes.c_void_p),
                ),
                -7,
            )
        finally:
            self.assertEqual(
                library.hhs_secure_arena_destroy(handle, owner),
                0,
            )

    def test_process_hardening_in_subprocess(self) -> None:
        script = (
            "from hhs_backend.runtime.hhs_pass213_secure_memory_v1 "
            "import NativeSecureArena;"
            f"NativeSecureArena.harden_current_process({str(self.library)!r});"
            "print('HARDENED')"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("HARDENED", completed.stdout)

    def test_invalid_size_and_key_rejected(self) -> None:
        with self.assertRaisesRegex(
            Pass213SecureMemoryError,
            "SIZE_INVALID",
        ):
            self.arena(size=0)
        with self.assertRaisesRegex(
            Pass213SecureMemoryError,
            "KEY_TOO_SHORT",
        ):
            NativeSecureArena(
                library_path=self.library,
                requested_size=4096,
                owner_id="owner",
                root_key=b"short",
                allocation_sequence=1,
            )


if __name__ == "__main__":
    unittest.main()
