from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
VM81_BIN = ROOT / "hhs_runtime" / "builds" / "hhs_vm81"


def _build_vm81() -> None:
    subprocess.run(
        ["make", "vm81"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def _run_vm81(*args: str) -> str:
    _build_vm81()
    completed = subprocess.run(
        [str(VM81_BIN), "--no-trace", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


class VM81BridgeDemoTests(unittest.TestCase):
    def test_bridge_demo_exercises_control_flow_and_vm_native_results(self) -> None:
        output = _run_vm81()
        self.assertIn("==== HHS PYTHON->VM BRIDGE DEMO ====", output)
        self.assertIn("R0=4", output)
        self.assertIn("R1=5", output)
        self.assertIn("R2=9", output)
        self.assertIn("R3=45", output)
        self.assertIn("R4=54", output)
        self.assertIn("R5=11", output)
        self.assertIn("R6=0", output)
        self.assertNotIn("BRIDGE DEMO FAILED", output)

    def test_default_runtime_path_skips_legacy_float_layers(self) -> None:
        output = _run_vm81("--verify")
        self.assertNotIn("VERIFY m-reciprocal probe", output)
        self.assertIn("Tensor layer count               : 0", output)
        self.assertIn("Genomic layer                    : [1 3 5 7]", output)
