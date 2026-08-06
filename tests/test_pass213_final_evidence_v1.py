from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    FULL_HYDRATION_DOMAIN,
    canonical_bytes,
)
from hhs_backend.runtime.hhs_pass213_final_evidence_v1 import (
    EvidenceProfile,
    Pass213FinalEvidenceError,
    run_final_evidence,
    validate_final_evidence,
)


def assert_no_float(test: unittest.TestCase, value: object) -> None:
    if isinstance(value, float):
        test.fail(f"final evidence contains float: {value!r}")
    if isinstance(value, dict):
        for child in value.values():
            assert_no_float(test, child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            assert_no_float(test, child)


class Pass213FinalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        native_root = Path(os.environ.get("TMPDIR", "/tmp"))
        secure_library = native_root / "libhhs_pass213_secure_arena.so"
        dispatch_library = native_root / "libhhs_pass213_native_dispatch.so"
        if not secure_library.exists() or not dispatch_library.exists():
            raise RuntimeError("PASS213_FINAL_EVIDENCE_NATIVE_LIBRARIES_MISSING")
        cls._temp = tempfile.TemporaryDirectory(prefix="pass213-final-evidence-test-")
        cls.evidence = run_final_evidence(
            secure_library_path=secure_library,
            dispatch_library_path=dispatch_library,
            workdir=cls._temp.name,
            profile=EvidenceProfile(
                exact_lookup_iterations=32,
                parametric_iterations=8,
                tensor_route_iterations=128,
                dispatch_iterations=4,
            ),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def test_full_hydration_recovery_and_resumed_execution(self) -> None:
        evidence = self.evidence
        self.assertTrue(validate_final_evidence(evidence))
        self.assertEqual(evidence["iteration"], 11)
        self.assertTrue(evidence["canonical_runtime_closed"])
        self.assertFalse(evidence["protected_material_exposed"])
        self.assertFalse(evidence["physical_addresses_exposed"])
        semantic = evidence["semantic"]
        hydration = semantic["full_hydration"]
        self.assertEqual(hydration["full_hydration_bits"], FULL_HYDRATION_DOMAIN)
        self.assertEqual(hydration["missing_shard_count"], 2)
        self.assertEqual(hydration["recovery_outcome"], "RECOVERED")
        self.assertTrue(hydration["recovered_state_matches"])
        self.assertTrue(hydration["corruption_detected_before_interpretation"])
        self.assertTrue(hydration["deterministic_replay"])
        self.assertTrue(semantic["moving_tensor"]["round_trip_valid"])
        self.assertTrue(semantic["moving_tensor"]["closure_wrap_valid"])
        compiled = semantic["compiled_reuse"]
        self.assertEqual(compiled["changed_paths"], ("operands.x",))
        self.assertEqual(
            compiled["affected_constraint_ids"], ("sum-bits", "x-range")
        )
        self.assertEqual(compiled["reused_constraint_ids"], ("mode", "y-range"))
        dispatch = semantic["native_dispatch"]
        self.assertTrue(dispatch["resumed_after_recovery"])
        self.assertTrue(dispatch["uninterrupted_and_resumed_receipts_equal"])
        self.assertTrue(dispatch["ledger_chains_valid"])
        self.assertEqual(dispatch["final_sequence"], 4)
        assert_no_float(self, evidence)
        round_tripped = json.loads(canonical_bytes(evidence).decode("utf-8"))
        self.assertTrue(validate_final_evidence(round_tripped))

    def test_semantic_or_observation_tamper_is_rejected(self) -> None:
        semantic_tamper = deepcopy(self.evidence)
        semantic_tamper["semantic"]["native_dispatch"]["final_sequence"] = 5
        with self.assertRaisesRegex(
            Pass213FinalEvidenceError, "SEMANTIC_ROOT_MISMATCH"
        ):
            validate_final_evidence(semantic_tamper)

        observation_tamper = deepcopy(self.evidence)
        observation_tamper["performance_observations"]["moving_tensor"][
            "elapsed_ns"
        ] += 1
        with self.assertRaisesRegex(
            Pass213FinalEvidenceError, "OBSERVATION_ROOT_MISMATCH"
        ):
            validate_final_evidence(observation_tamper)


if __name__ == "__main__":
    unittest.main()
