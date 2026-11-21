"""SQL AES-GCM -> verified Hash216 positional SHA256 -> C BIOS smoke test."""
import pathlib
import subprocess
import tempfile
import unittest

from hhs_runtime.pass174.runtime import Hash216Array
from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore
from hhs_python.runtime.hhs_lane5_sql_native_bios_v1 import Lane5SQLNativeBIOS

ROOT = pathlib.Path(__file__).resolve().parents[1]


class SQLBIOSRoundTrip(unittest.TestCase):
    def test_encrypted_restart_to_native_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            library = root / "libbios.so"
            subprocess.run([
                "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-shared", "-fPIC",
                str(ROOT / "hhs_runtime/acceleration/hhs_lane5_opcode_bios_v1.c"),
                "-o", str(library),
            ], check=True)
            db = root / "vectors.sqlite3"
            key = bytes(range(32))
            ids = dict(genesis_identity="1"*64, legacy_foundation_root="2"*64,
                       operation_identity="3"*64, logical_step=0)
            alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
            word = (alphabet * 2)[:72]
            index = Hash216Array.build(word, word[::-1], word, **ids)
            frame = bytes([i % 256 for i in range(648)])
            with_store = PersistentEncryptedVectorStore(db, key=key)
            with_store.admit(
                operation_key="native-sql-bios-test", logical_step=0,
                input_hash72=word, output_hash72=word[::-1],
                operation_identity_sha256=ids["operation_identity"],
                hash216=index, output_snapshot=frame,
                legacy_foundation_root=ids["legacy_foundation_root"],
                genesis_identity=ids["genesis_identity"],
                direct_cost_units=0, changed_bits=0,
                parent_object_id=None,
            )
            self.assertEqual(with_store.storage_status()["journal_mode"], "wal")
            self.assertEqual(with_store._connection.execute("PRAGMA synchronous").fetchone()[0], 2)
            with_store.close()
            reopened = PersistentEncryptedVectorStore(db, key=key)
            bios = Lane5SQLNativeBIOS(reopened, library)
            try:
                reference = bios.hydrate(
                    "native-sql-bios-test",
                    legacy_foundation_root=ids["legacy_foundation_root"],
                    genesis_identity=ids["genesis_identity"],
                )
                self.assertEqual(reference.hash216_index_root_sha256,index.index_root_sha256)
                self.assertEqual(bios.read_hash216_position(0), ord(word[0]))
                self.assertEqual(bios.read_hash216_position(215), ord(word[-1]))
                self.assertEqual(bios.read_frame_byte(647), frame[-1])
            finally:
                bios.close()
                reopened.close()


if __name__ == "__main__":
    unittest.main()
