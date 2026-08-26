from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass193_hypersolid_native_egress_v1 import native_probe_source


EXPECTED = "HHS-P193-NATIVE:15705"


def _required() -> bool:
    return os.environ.get("HHS_PASS193_REQUIRE_NATIVE_TARGETS") == "1"


def _tool(name: str) -> str | None:
    path = shutil.which(name)
    if path is None and _required():
        raise AssertionError(f"required native validation tool is missing: {name}")
    return path


class Pass193NativeTargetTests(unittest.TestCase):
    def _source(self, root: Path) -> Path:
        source = root / "pass193_native_probe.c"
        source.write_text(native_probe_source(), encoding="utf-8")
        return source

    def test_linux_x86_64_compile_link_launch_abi_and_determinism(self) -> None:
        compiler = _tool("gcc")
        file_tool = _tool("file")
        if compiler is None or file_tool is None:
            self.skipTest("native x86_64 toolchain unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._source(root)
            binary = root / "pass193-x86_64"
            subprocess.run(
                [
                    compiler,
                    "-std=c11",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-pedantic",
                    str(source),
                    "-o",
                    str(binary),
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            identity = subprocess.run(
                [file_tool, str(binary)],
                check=True,
                text=True,
                capture_output=True,
            ).stdout
            self.assertIn("x86-64", identity)
            first = subprocess.run(
                [str(binary)], check=True, text=True, capture_output=True
            ).stdout.strip()
            second = subprocess.run(
                [str(binary)], check=True, text=True, capture_output=True
            ).stdout.strip()
            self.assertEqual(first, EXPECTED)
            self.assertEqual(first, second)

    def test_linux_arm64_compile_link_launch_abi_and_determinism(self) -> None:
        compiler = _tool("aarch64-linux-gnu-gcc")
        emulator = _tool("qemu-aarch64")
        file_tool = _tool("file")
        if compiler is None or emulator is None or file_tool is None:
            self.skipTest("native ARM64 cross-toolchain unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._source(root)
            binary = root / "pass193-arm64"
            subprocess.run(
                [
                    compiler,
                    "-static",
                    "-std=c11",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-pedantic",
                    str(source),
                    "-o",
                    str(binary),
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            identity = subprocess.run(
                [file_tool, str(binary)],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.lower()
            self.assertIn("aarch64", identity)
            first = subprocess.run(
                [emulator, str(binary)], check=True, text=True, capture_output=True
            ).stdout.strip()
            second = subprocess.run(
                [emulator, str(binary)], check=True, text=True, capture_output=True
            ).stdout.strip()
            self.assertEqual(first, EXPECTED)
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
