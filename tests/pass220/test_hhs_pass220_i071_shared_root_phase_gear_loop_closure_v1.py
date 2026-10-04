from __future__ import annotations

import copy
from hashlib import sha256
from pathlib import Path
import unittest

from hhs_runtime.hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 import (
    AUTHORITY_BOUNDARY,
    MAX_SEEN,
    QUDIT_PHASE_SLOTS,
    Pass220I071LoopError,
    SeenState,
    build_nucleus_qudit_surface,
    canonical_bytes,
    decode_phase_slot,
    detect_orbit_exact,
    encode_phase_slot,
    kernel_orbit_contract,
    lift_geometry,
    lower_geometry,
    phase_gear_invariants,
    phase_successor,
    run_phase_gear_loop,
    self_test,
)

ROOT = Path(__file__).resolve().parents[2]
VM_SOURCE = ROOT / "hhs_runtime" / "HARMONICODE_VM_RUNTIME.c"
I042_SOURCE = (
    ROOT / "hhs_runtime" / "hhs_pass220_lane5_multimodal_shared_root_fabric_v1.py"
)
PASS174 = (
    ROOT
    / "HHS_PASS_174_HARMONIC_PHASE_GEAR_HASH216_VM81_VISUAL_IDE_MULTIMODAL_SDLC_RUNTIME.md"
)


def shared_root() -> str:
    return sha256(
        canonical_bytes(
            {
                "root_metadata_seed": "179971.179971",
                "invariant_gate": "1.001",
                "test": "I071",
            }
        )
    ).hexdigest()


class I071SharedRootPhaseGearLoopTests(unittest.TestCase):
    def test_vm81_detector_semantics_match_authoritative_c_source(self) -> None:
        source = VM_SOURCE.read_text(encoding="utf-8")
        for required in (
            "static uint64_t detect_orbit",
            "strcmp(vm->seen[i].hash, hash) == 0",
            "return cur - vm->seen[i].step",
            "vm->seen_count < MAX_SEEN",
            "vm->orbit_halted = 1",
            "if (opt->halt_on_orbit && vm->orbit_halted) break",
        ):
            self.assertIn(required, source)
        contract = kernel_orbit_contract()
        self.assertEqual(contract["seen_capacity"], 8192)
        self.assertTrue(contract["op_halt_is_distinct"])

    def test_detector_returns_first_seen_period_and_does_not_duplicate(self) -> None:
        a = "0" * 72
        b = "1" * 72
        seen: list[SeenState] = []
        self.assertEqual(detect_orbit_exact(seen, a, 0), 0)
        self.assertEqual(detect_orbit_exact(seen, b, 1), 0)
        self.assertEqual(len(seen), 2)
        self.assertEqual(detect_orbit_exact(seen, a, 7), 7)
        self.assertEqual(len(seen), 2)

    def test_detector_capacity_matches_vm81_miss_behavior(self) -> None:
        seen: list[SeenState] = []
        self.assertEqual(detect_orbit_exact(seen, "0" * 72, 0, max_seen=2), 0)
        self.assertEqual(detect_orbit_exact(seen, "1" * 72, 1, max_seen=2), 0)
        self.assertEqual(detect_orbit_exact(seen, "2" * 72, 2, max_seen=2), 0)
        self.assertEqual(len(seen), 2)
        self.assertEqual(detect_orbit_exact(seen, "0" * 72, 9, max_seen=2), 9)

    def test_phase_slot_encode_decode_and_successor_cycle(self) -> None:
        self.assertEqual(QUDIT_PHASE_SLOTS, 72)
        for slot in range(72):
            channel, outcome = decode_phase_slot(slot)
            self.assertEqual(encode_phase_slot(channel, outcome), slot)
            self.assertEqual(phase_successor(slot), (slot + 1) % 72)
        slot = 0
        visited = []
        for _ in range(72):
            visited.append(slot)
            slot = phase_successor(slot)
        self.assertEqual(len(set(visited)), 72)
        self.assertEqual(slot, 0)

    def test_i042_shared_root_contract_is_preserved_without_runtime_import(self) -> None:
        source = I042_SOURCE.read_text(encoding="utf-8")
        for required in (
            'ROOT_METADATA_SEED_TEXT = "179971.179971"',
            'INVARIANT_GATE_TEXT = "1.001"',
            "def shared_multimodal_root_sha256()",
            '"vm81x64": 81 * 64',
            '"hash72_square": 72 * 72',
            '"q144xh36": 144 * 36',
        ):
            self.assertIn(required, source)

    def test_pass174_phase_gear_contract_remains_5184(self) -> None:
        text = PASS174.read_text(encoding="utf-8")
        for required in (
            "64=8^2",
            "72=8\\cdot9",
            "81=9^2",
            "\\operatorname{lcm}(64,72,81)=5184",
        ):
            self.assertIn(required, text)
        inv = phase_gear_invariants()
        self.assertTrue(inv["coordinate_closure"])
        self.assertEqual(inv["phase_gear_determinant"], 0)
        self.assertEqual(inv["phase_lock_period"], 5184)

    def test_each_nucleus_builds_exact_72_state_qudit_surface(self) -> None:
        root = shared_root()
        for nucleus in range(9):
            surface = build_nucleus_qudit_surface(
                shared_root_sha256=root,
                nucleus_index=nucleus,
            )
            self.assertEqual(len(surface), 72)
            self.assertEqual(len({x.geometry_hash72 for x in surface}), 72)
            self.assertEqual(
                sorted({x.vm81_cell_id for x in surface}),
                list(range(9 * nucleus, 9 * nucleus + 9)),
            )

    def test_lower_lift_preserves_orbit_identity_not_lineage(self) -> None:
        root = shared_root()
        surface = build_nucleus_qudit_surface(
            shared_root_sha256=root,
            nucleus_index=2,
        )
        lineage = "0" * 216
        lifted = lift_geometry(
            surface[11],
            nesting_depth=13,
            lineage_hash216=lineage,
            hydration_root_sha256="a" * 64,
        )
        self.assertEqual(lower_geometry(lifted), surface[11].geometry_hash72)
        changed = copy.deepcopy(lifted)
        changed["lineage_hash216"] = "1" * 216
        self.assertEqual(lower_geometry(changed), surface[11].geometry_hash72)

    def test_loop_closes_at_72_without_premature_repeat(self) -> None:
        result = run_phase_gear_loop(
            shared_root_sha256=shared_root(),
            nucleus_index=4,
            nesting_depth=0,
            halt_on_orbit=True,
            max_steps=72,
        )
        self.assertEqual(result["orbit_period"], 72)
        self.assertEqual(result["seen_unique_geometries"], 72)
        self.assertEqual(result["visited_records"], 73)
        self.assertTrue(result["geometry_returned"])
        self.assertTrue(result["lineage_advanced"])
        self.assertTrue(result["orbit_halted"])
        self.assertTrue(result["halted"])
        self.assertFalse(any(x["orbit_period"] for x in result["trace"][:-1]))

    def test_same_detector_period_after_global_lift(self) -> None:
        root = shared_root()
        periods = []
        final_geometries = []
        for depth in (0, 1, 7, 72):
            result = run_phase_gear_loop(
                shared_root_sha256=root,
                nucleus_index=6,
                nesting_depth=depth,
                halt_on_orbit=True,
                max_steps=72,
            )
            periods.append(result["orbit_period"])
            final_geometries.append(result["trace"][-1]["geometry_hash72"])
        self.assertEqual(periods, [72, 72, 72, 72])
        self.assertEqual(len(set(final_geometries)), 1)

    def test_orbit_halt_and_joint_convergence_remain_distinct(self) -> None:
        root = shared_root()
        orbit_only = run_phase_gear_loop(
            shared_root_sha256=root,
            nucleus_index=0,
            halt_on_orbit=True,
            orientation_closed=False,
            constraint_closed=False,
            max_steps=72,
        )
        fully_closed = run_phase_gear_loop(
            shared_root_sha256=root,
            nucleus_index=0,
            halt_on_orbit=True,
            orientation_closed=True,
            constraint_closed=True,
            max_steps=72,
        )
        self.assertTrue(orbit_only["halted"])
        self.assertFalse(orbit_only["converged"])
        self.assertTrue(fully_closed["halted"])
        self.assertTrue(fully_closed["converged"])

    def test_hash216_history_advances_even_when_geometry_returns(self) -> None:
        result = run_phase_gear_loop(
            shared_root_sha256=shared_root(),
            nucleus_index=8,
            nesting_depth=3,
            halt_on_orbit=True,
            max_steps=72,
        )
        self.assertEqual(
            result["trace"][0]["geometry_hash72"],
            result["trace"][-1]["geometry_hash72"],
        )
        self.assertNotEqual(
            result["trace"][0]["lineage_hash216"],
            result["trace"][-1]["lineage_hash216"],
        )

    def test_invalid_types_fail_closed(self) -> None:
        with self.assertRaises(Pass220I071LoopError):
            run_phase_gear_loop(
                shared_root_sha256=shared_root(),
                nucleus_index=True,
            )
        with self.assertRaises(Pass220I071LoopError):
            run_phase_gear_loop(
                shared_root_sha256="not-a-root",
                nucleus_index=0,
            )
        with self.assertRaises(Pass220I071LoopError):
            detect_orbit_exact([], "0" * 71, 0)

    def test_authority_boundary_remains_candidate_only(self) -> None:
        self.assertTrue(AUTHORITY_BOUNDARY["candidate_only"])
        self.assertTrue(AUTHORITY_BOUNDARY["vm81_detector_semantics_preserved"])
        self.assertTrue(AUTHORITY_BOUNDARY["lower_lift_orbit_identity_preserved"])
        self.assertFalse(AUTHORITY_BOUNDARY["floating_point_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_hash72_commit_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_hash216_commit_authority"])
        self.assertFalse(
            AUTHORITY_BOUNDARY["canonical_hash216_persistence_authority"]
        )

    def test_self_test_closes(self) -> None:
        report = self_test()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["check_count"], report["pass_count"])
        self.assertEqual(report["failed"], [])
        self.assertLessEqual(MAX_SEEN, 8192)


if __name__ == "__main__":
    unittest.main()
