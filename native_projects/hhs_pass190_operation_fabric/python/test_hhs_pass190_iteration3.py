from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190 import HHSAuthorityContext  # noqa: E402
from hhs_pass190_iteration3 import (  # noqa: E402
    DEFAULT_NATIVE_LIBRARY,
    HarmonicodeOperationCompiler,
    NativeABI,
    NativeABIError,
    NativeManifest,
    semantic_parity,
)
from hhs_pass190_iteration3_server import build_server  # noqa: E402

TEST_SECRET = "pass190-iteration3-native-test-secret-" + ("x" * 48)


class Iteration3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compiler = HarmonicodeOperationCompiler()
        cls.native = NativeABI(DEFAULT_NATIVE_LIBRARY)

    def setUp(self) -> None:
        self.context = HHSAuthorityContext()
        self.native.reset()

    def test_manifest_covers_registry_in_order(self) -> None:
        manifest = NativeManifest(self.compiler.registry)
        self.assertEqual(list(manifest.by_id), list(self.compiler.registry.by_id))
        self.assertEqual(len(manifest.by_id), 10)
        self.assertEqual(manifest.by_id["math.gcd"]["native_symbol"], "hhs_p190_math_gcd")

    def test_cst_ast_hir_vmir_lowering_and_hashes(self) -> None:
        program = self.compiler.compile_program("# exact program\nAbs(-12)\nGCD(84,30)\n")
        self.assertEqual([item["operation_id"] for item in program["instructions"]], ["python.abs", "math.gcd"])
        self.assertEqual(program["instructions"][0]["cst"]["lexical_source"], "Abs(-12)")
        self.assertEqual(program["instructions"][0]["ast"]["arguments"], {"value": -12})
        self.assertEqual(program["instructions"][1]["hir"]["effect_class"], "pure")
        self.assertEqual(program["instructions"][1]["vmir"]["native_abi_symbol"], "hhs_p190_math_gcd")
        self.assertEqual(len(program["program_hash72"]), 72)
        self.assertEqual(len(program["program_hash216"]), 216)
        self.assertEqual(program, self.compiler.compile_program("# exact program\nAbs(-12)\nGCD(84,30)\n"))

    def test_compiled_execution_uses_canonical_authority(self) -> None:
        program = self.compiler.compile_program("Abs(-9)\nJoin('-', ['a','b'])")
        outputs = self.compiler.execute(program, self.context)
        self.assertEqual([item["result"] for item in outputs], [9, "a-b"])
        self.assertEqual(outputs[0]["requested_surface"], "compiler-vmir")
        self.assertEqual(outputs[1]["receipt"]["predecessor_hash72"], outputs[0]["receipt"]["hash72"])

    def test_native_python_semantic_parity(self) -> None:
        vectors = [
            ("python.len", {"value": [1, 2, 3]}),
            ("python.abs", {"value": -72}),
            ("python.sorted", {"values": [3, 1, 2], "reverse": True}),
            ("list.with_appended", {"source": [1, 2], "value": 3}),
            ("dict.get", {"mapping": {"x": {"n": 7}}, "key": "x", "default": None}),
            ("text.join", {"separator": ":", "values": ["x", "y"]}),
            ("math.gcd", {"a": 84, "b": 30}),
            ("pass189.context.decode", {"address": 51_648_191}),
        ]
        for operation_id, arguments in vectors:
            with self.subTest(operation_id=operation_id):
                python_result = self.context.invoke(operation_id, arguments).result
                native_result = self.native.invoke(operation_id, arguments)
                self.assertTrue(semantic_parity(operation_id, python_result, native_result))

    def test_native_singleton_mutation_profile(self) -> None:
        python_result = self.context.invoke(
            "state.counter.advance",
            {"delta": 5},
            capabilities={"runtime.mutate"},
        ).result
        native_result = self.native.invoke("state.counter.advance", {"delta": 5})
        self.assertTrue(semantic_parity("state.counter.advance", python_result, native_result))
        status = self.native.invoke("system.status", {})
        self.assertEqual(status["counter"], 5)
        self.assertEqual(status["receipt_index"], 1)

    def test_native_profiles_reject_nonrepresentable_values(self) -> None:
        with self.assertRaises(NativeABIError):
            self.native.invoke("python.abs", {"value": 2**80})
        with self.assertRaises(NativeABIError):
            self.native.invoke("python.sorted", {"values": [1, "2"]})
        with self.assertRaises(NativeABIError):
            self.native.invoke("dict.get", {"mapping": {1: "x"}, "key": "1", "default": None})

    def test_manifest_is_machine_readable(self) -> None:
        payload = json.loads((ROOT / "native" / "generated" / "HHS_NATIVE_ABI_MANIFEST_V1.json").read_text())
        self.assertFalse(payload["full_native_parity_claimed"])
        self.assertEqual(payload["operation_count"], 10)

    def test_live_compiler_http_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            server = build_server(
                port=0,
                database=Path(directory) / "authority.sqlite3",
                capability_secret=TEST_SECRET,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                body = json.dumps({"source": "Abs(-11)\nGCD(21,14)"}).encode()
                request = urllib.request.Request(
                    base + "/api/pass190/compile-execute",
                    data=body,
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(request, timeout=5) as response:
                    payload = json.load(response)
                self.assertEqual([item["result"] for item in payload["results"]], [11, 7])
                self.assertEqual(payload["results"][1]["receipt"]["predecessor_hash72"], payload["results"][0]["receipt"]["hash72"])
                with urllib.request.urlopen(base + "/api/pass190/native-abi", timeout=5) as response:
                    manifest = json.load(response)
                self.assertEqual(manifest["operation_count"], 10)
                with urllib.request.urlopen(base + "/openapi.json", timeout=5) as response:
                    openapi = json.load(response)
                self.assertEqual(openapi["x-hhs-iteration"], 3)
                self.assertIn("/api/pass190/compile-execute", openapi["paths"])
                self.assertIn("/api/pass190/integrity", openapi["paths"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
