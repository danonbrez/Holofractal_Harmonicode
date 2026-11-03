"""Cross-language parity for Pass174 Hash216Array.build native lowering."""
import ctypes
import pathlib
import subprocess
import tempfile
import unittest

from hhs_runtime.pass174.runtime import Hash216Array

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "hhs_runtime/acceleration/hhs_lane5_hash216_lower_v1.c"


class Input(ctypes.Structure):
    _fields_ = [
        ("genesis_identity", ctypes.c_char_p),
        ("legacy_foundation_root", ctypes.c_char_p),
        ("operation_identity", ctypes.c_char_p),
        ("logical_step", ctypes.c_uint64),
        ("previous", ctypes.c_char_p),
        ("change", ctypes.c_char_p),
        ("receipt", ctypes.c_char_p),
    ]


class Output(ctypes.Structure):
    _fields_ = [
        ("combined", ctypes.c_char * 217),
        ("logical_identity_sha256", ctypes.c_char * 65),
        ("character_indexes_sha256", (ctypes.c_char * 65) * 216),
        ("index_root_sha256", ctypes.c_char * 65),
    ]


class TestNativeHash216Parity(unittest.TestCase):
    def test_exact_pass174_parity(self):
        with tempfile.TemporaryDirectory() as d:
            lib = pathlib.Path(d) / "liblower.so"
            subprocess.run(
                ["cc", "-O2", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-fPIC", "-shared", str(SOURCE), "-lcrypto", "-o", str(lib)],
                check=True,
            )
            fn = ctypes.CDLL(str(lib)).hhs_hash216_lower_pass174
            fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Output)]
            fn.restype = ctypes.c_int
            alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
            for step in (0, 1, 5184, 10368):
                previous = (alphabet * 2)[:72]
                change = (alphabet[::-1] * 2)[:72]
                receipt = (alphabet[3:] + alphabet[:3])
                args = dict(genesis_identity="1" * 64,
                            legacy_foundation_root="2" * 64,
                            operation_identity="3" * 64,
                            logical_step=step)
                reference = Hash216Array.build(previous, change, receipt, **args)
                native = Input(*(args[k].encode() for k in
                                 ("genesis_identity", "legacy_foundation_root",
                                  "operation_identity")), step,
                               previous.encode(), change.encode(), receipt.encode())
                output = Output()
                self.assertEqual(fn(ctypes.byref(native), ctypes.byref(output)), 0)
                self.assertEqual(output.combined.decode(), reference.combined)
                self.assertEqual(output.logical_identity_sha256.decode(),
                                 reference.logical_identity_sha256)
                self.assertEqual(output.index_root_sha256.decode(),
                                 reference.index_root_sha256)
                self.assertEqual(
                    tuple(bytes(row).split(bytes([0]),1)[0].decode()
                          for row in output.character_indexes_sha256),
                    reference.character_indexes_sha256,
                )
                reference.verify()


if __name__ == "__main__":
    unittest.main()
