from __future__ import annotations

import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass190_iteration4 import LeaseBusyError  # noqa: E402
from hhs_pass190_iteration5_runtime import AtomicKernelAuthorityContext, SQLITE_LOCK_SLICE_MS  # noqa: E402


class Iteration5RuntimeTests(unittest.TestCase):
    def test_busy_timeout_is_sliced_and_respects_bounded_wait(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "authority.sqlite3"
            context = AtomicKernelAuthorityContext(
                database,
                holder_id="bounded-runtime",
                lease_wait_ns=80_000_000,
            )
            ready = threading.Event()
            release = threading.Event()

            def hold() -> None:
                connection = sqlite3.connect(database, timeout=5)
                connection.execute("BEGIN IMMEDIATE")
                ready.set()
                release.wait(5)
                connection.rollback()
                connection.close()

            thread = threading.Thread(target=hold, daemon=True)
            thread.start()
            self.assertTrue(ready.wait(2))
            started = time.monotonic()
            try:
                with self.assertRaises(LeaseBusyError):
                    context.invoke("system.status", {})
            finally:
                elapsed = time.monotonic() - started
                release.set()
                thread.join(2)
                context.close()
            self.assertLessEqual(SQLITE_LOCK_SLICE_MS, 25)
            self.assertLess(elapsed, 0.35)


if __name__ == "__main__":
    unittest.main(verbosity=2)
