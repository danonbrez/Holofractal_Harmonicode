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
    def make(self, *, receipt_registry=None, **kwargs):
        verifier = None
        if receipt_registry is not None:
            verifier = lambda receipt, root: receipt_registry.get(receipt) == root
        return Hash216ProjectionScheduler(
            authority=FakeAuthority(), receipt_verifier=verifier, **kwargs
        )

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

    def test_authoritative_versions_are_retained_losslessly(self):
        scheduler = self.make()
        first = scheduler.observe_runtime_state(
            "receipt:1", "RECEIPT_CANDIDATE_OBJECT", {"n": 1}, authoritative=True
        )
        second = scheduler.observe_runtime_state(
            "receipt:1", "RECEIPT_CANDIDATE_OBJECT", {"n": 2}, authoritative=True
        )
        package = scheduler.build_projection_package(1)
        roots = [chunk["hash216_root"] for chunk in package["changed_chunks"]]
        self.assertEqual(package["authoritative_event_count"], 2)
        self.assertEqual(package["event_count"], 2)
        self.assertEqual(roots, [first["chunk"]["hash216_root"], second["chunk"]["hash216_root"]])

    def test_authoritative_queue_rejects_before_mutating_state(self):
        scheduler = self.make(max_authoritative_events=1)
        scheduler.observe_runtime_state(
            "receipt:1", "RECEIPT_CANDIDATE_OBJECT", {"n": 1}, authoritative=True
        )
        before = scheduler.snapshot()
        with self.assertRaisesRegex(BufferError, "AUTHORITATIVE_PROJECTION_QUEUE_BOUND"):
            scheduler.observe_runtime_state(
                "receipt:2", "RECEIPT_CANDIDATE_OBJECT", {"n": 2}, authoritative=True
            )
        after = scheduler.snapshot()
        self.assertEqual(after["objects"], before["objects"])
        self.assertEqual(after["chunk_history"], before["chunk_history"])
        self.assertEqual(after["event_sequence"], before["event_sequence"])

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

    def test_vm81_admission_requires_verified_hash72_receipt(self):
        scheduler = self.make()
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1])
        package = scheduler.build_projection_package(1)
        root = package["projection_root_hash216"]
        with self.assertRaisesRegex(ValueError, "HASH72_RECEIPT_REQUIRED_FOR_ADMISSION"):
            scheduler.acknowledge_vm81(root, admitted=True)
        with self.assertRaisesRegex(ValueError, "HASH72_RECEIPT_VERIFIER_REQUIRED"):
            scheduler.acknowledge_vm81(root, admitted=True, receipt_hash72="0" * 72)

        registry = {"1" * 72: root}
        verified = self.make(receipt_registry=registry)
        verified.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1])
        verified_package = verified.build_projection_package(1)
        verified_root = verified_package["projection_root_hash216"]
        registry["1" * 72] = verified_root
        with self.assertRaisesRegex(ValueError, "HASH72_RECEIPT_MISMATCH"):
            verified.acknowledge_vm81(verified_root, admitted=True, receipt_hash72="2" * 72)
        admitted = verified.acknowledge_vm81(
            verified_root, admitted=True, receipt_hash72="1" * 72
        )
        self.assertEqual(admitted["vm81_admission"], "ADMITTED")

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
        self.assertNotEqual(first["chunk"]["hash216_root"], second["chunk"]["hash216_root"])

    def test_chain_position_prevents_a_b_a_root_collapse(self):
        scheduler = self.make()
        first = scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1])
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [2])
        third = scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1])
        self.assertNotEqual(first["chunk"]["hash216_root"], third["chunk"]["hash216_root"])
        self.assertEqual(third["chunk"]["version"], 3)

    def test_snapshot_recovery_preserves_all_versioned_chunks(self):
        scheduler = self.make()
        scheduler.register_static_object("addresses", "STATIC_ADDRESS_OBJECT", {"count": 5184})
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1], authoritative=True)
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [2], authoritative=True)
        scheduler.observe_frame_telemetry(FrameTelemetry(1, 16_666_667, physics_ns=1_000_000))
        snapshot = scheduler.snapshot()
        self.assertEqual(snapshot["schema"], SNAPSHOT_SCHEMA)
        self.assertEqual(len(snapshot["chunk_history"]), 3)
        recovered = self.make()
        status = recovered.recover(json.loads(json.dumps(snapshot)))
        self.assertEqual(status["objects"], 2)
        self.assertEqual(status["versioned_chunks"], 3)
        package = recovered.build_projection_package(1)
        self.assertEqual(package["authoritative_event_count"], 2)
        self.assertEqual(len(package["changed_chunks"]), 3)

    def test_snapshot_recovery_recomputes_chunk_identity(self):
        scheduler = self.make()
        scheduler.observe_runtime_state("positions", "PHYSICS_POSITION_OBJECT", [1, 2, 3])
        snapshot = json.loads(json.dumps(scheduler.snapshot()))
        root = snapshot["objects"]["positions"]["hash216_root"]
        snapshot["objects"]["positions"]["payload"] = [9, 9, 9]
        snapshot["chunk_history"][root]["payload"] = [9, 9, 9]
        recovered = self.make()
        with self.assertRaisesRegex(ValueError, "HASH216_SNAPSHOT_IDENTITY_MISMATCH"):
            recovered.recover(snapshot)

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
