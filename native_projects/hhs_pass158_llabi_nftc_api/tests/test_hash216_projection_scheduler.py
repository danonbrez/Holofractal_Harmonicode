from __future__ import annotations

from hashlib import sha256
import json
import unittest

from hash216_projection_scheduler import (
    FrameTelemetry,
    Hash216ProjectionScheduler,
    SNAPSHOT_SCHEMA,
)


class FakeAuthority:
    def positions(self, payload: bytes, *, previous_root: str, sequence: int):
        seed = sha256(previous_root.encode() + sequence.to_bytes(8, "big") + payload).digest()
        return tuple(sha256(seed + index.to_bytes(2, "big")).hexdigest() for index in range(216))

    def root(self, positions):
        return sha256(b"".join(bytes.fromhex(item) for item in positions)).hexdigest()


class SchedulerTests(unittest.TestCase):
    def make(self, **kwargs):
        return Hash216ProjectionScheduler(authority=FakeAuthority(), **kwargs)

    def test_static_identity_is_reused_and_mutation_is_rejected(self):
        scheduler = self.make()
        first = scheduler.register_static_object("addresses", "STATIC_ADDRESS_OBJECT", {"count": 5184})
        second = scheduler.register_static_object("addresses", "STATIC_ADDRESS_OBJECT", {"count": 5184})
        self.assertTrue(first["changed"])
        self.assertFalse(second["changed"])
        with self.assertRaisesRegex(ValueError, "STATIC_OBJECT_MUTATION_REJECTED"):
            scheduler.register_static_object("addresses", "STATIC_ADDRESS_OBJECT", {"count": 1})

    def test_transient_updates_coalesce_by_object_identity(self):
        scheduler = self.make()
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1])
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [2])
        status = scheduler.status()
        self.assertEqual(status["transient_queue"], 1)
        self.assertEqual(status["coalesced_events"], 1)
        package = scheduler.build_projection_package(1)
        self.assertEqual(package["event_count"], 1)
        self.assertEqual(package["changed_chunks"][0]["payload"], [2])

    def test_authoritative_events_are_lossless(self):
        scheduler = self.make()
        scheduler.observe_runtime_state("receipt:1", "RECEIPT_CANDIDATE_OBJECT", {"n": 1}, authoritative=True)
        scheduler.observe_runtime_state("receipt:2", "RECEIPT_CANDIDATE_OBJECT", {"n": 2}, authoritative=True)
        package = scheduler.build_projection_package(1)
        self.assertEqual(package["authoritative_event_count"], 2)
        self.assertEqual(package["event_count"], 2)

    def test_authoritative_queue_is_hard_bounded(self):
        scheduler = self.make(max_authoritative_events=1)
        scheduler.observe_runtime_state("receipt:1", "RECEIPT_CANDIDATE_OBJECT", {"n": 1}, authoritative=True)
        with self.assertRaisesRegex(BufferError, "AUTHORITATIVE_PROJECTION_QUEUE_BOUND"):
            scheduler.observe_runtime_state("receipt:2", "RECEIPT_CANDIDATE_OBJECT", {"n": 2}, authoritative=True)

    def test_frame_budget_normal_pressure_and_critical(self):
        scheduler = self.make()
        normal = scheduler.observe_frame_telemetry(FrameTelemetry(1, 10_000, physics_ns=2_000, render_ns=3_000))
        pressure = scheduler.observe_frame_telemetry(FrameTelemetry(2, 10_000, physics_ns=7_000, render_ns=5_000))
        critical = scheduler.observe_frame_telemetry(FrameTelemetry(3, 10_000, physics_ns=10_000, render_ns=10_000))
        self.assertEqual(normal["classification"], "FRAME_BUDGET_NORMAL")
        self.assertEqual(pressure["classification"], "FRAME_BUDGET_PRESSURE")
        self.assertEqual(critical["classification"], "FRAME_BUDGET_CRITICAL")
        self.assertIn("PHYSICS_CATCHUP", critical["hold_classes"])

    def test_package_is_hash216_indexed_and_non_authoritative(self):
        scheduler = self.make()
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1, 2, 3])
        package = scheduler.build_projection_package(9)
        self.assertEqual(len(package["projection_hash216_positions"]), 216)
        self.assertEqual(len(package["projection_root_hash216"]), 64)
        self.assertFalse(package["mutation_authority"])
        self.assertTrue(package["requires_vm81_validation"])
        self.assertEqual(package["vm81_admission"], "PENDING")

    def test_delta_vectors_are_preserved(self):
        scheduler = self.make()
        delta = {"multiplicative": "1000001/1000000", "additive": "1/1000000", "relative": "1/1000000"}
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1], delta_offset_vector=delta)
        package = scheduler.build_projection_package(1)
        self.assertEqual(package["delta_offset_vectors"][0]["value"], delta)

    def test_vm81_admission_requires_hash72_receipt(self):
        scheduler = self.make()
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1])
        package = scheduler.build_projection_package(1)
        with self.assertRaisesRegex(ValueError, "HASH72_RECEIPT_REQUIRED_FOR_ADMISSION"):
            scheduler.acknowledge_vm81(package["projection_root_hash216"], admitted=True)
        admitted = scheduler.acknowledge_vm81(
            package["projection_root_hash216"], admitted=True, receipt_hash72="0" * 72
        )
        self.assertEqual(admitted["vm81_admission"], "ADMITTED")
        self.assertEqual(admitted["receipt_hash72"], "0" * 72)

    def test_dependency_root_change_invalidates_dependent_chunk(self):
        scheduler = self.make()
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1])
        first = scheduler.observe_runtime_state(
            "render", "RENDER_ATTRIBUTE_OBJECT", {"mode": "points"}, dependencies=["positions"]
        )
        scheduler.build_projection_package(1)
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [2])
        second = scheduler.observe_runtime_state(
            "render", "RENDER_ATTRIBUTE_OBJECT", {"mode": "points"}, dependencies=["positions"]
        )
        self.assertTrue(first["changed"])
        self.assertTrue(second["changed"])
        self.assertNotEqual(first["chunk"]["hash216_root"], second["chunk"]["hash216_root"])

    def test_snapshot_recovery_preserves_identity(self):
        scheduler = self.make()
        scheduler.register_static_object("addresses", "STATIC_ADDRESS_OBJECT", {"count": 5184})
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1, 2, 3])
        scheduler.observe_frame_telemetry(FrameTelemetry(1, 16_666_667, physics_ns=1_000_000))
        snapshot = scheduler.snapshot()
        self.assertEqual(snapshot["schema"], SNAPSHOT_SCHEMA)
        recovered = self.make()
        status = recovered.recover(json.loads(json.dumps(snapshot)))
        self.assertEqual(status["objects"], 2)
        self.assertEqual(status["transient_queue"], 2)

    def test_invalid_telemetry_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "INVALID_FRAME_TELEMETRY"):
            FrameTelemetry(1, 0)
        with self.assertRaisesRegex(ValueError, "INVALID_FRAME_TELEMETRY"):
            FrameTelemetry(1, 10, physics_ns=-1)

    def test_continuation_cache_does_not_alias_object_identity(self):
        scheduler = self.make()
        scheduler.observe_runtime_state("a", "TRANSIENT_STATUS", {"state": "READY"})
        scheduler.observe_runtime_state("b", "TRANSIENT_STATUS", {"state": "READY"})
        self.assertEqual(scheduler.status()["reused_chunks"], 0)
        scheduler.observe_runtime_state("a", "TRANSIENT_STATUS", {"state": "READY"})
        self.assertEqual(scheduler.status()["transient_queue"], 2)


if __name__ == "__main__":
    unittest.main()
