from __future__ import annotations

from hashlib import sha256
import unittest

from hash216_projection_scheduler import Hash216ProjectionScheduler
from pass158_gui_projection_runtime import BASE, Pass158GuiProjectionRuntime


class FakeAuthority:
    def positions(self, payload: bytes, *, previous_root: str, sequence: int):
        seed = sha256(previous_root.encode() + sequence.to_bytes(8, "big") + payload).digest()
        return tuple(sha256(seed + index.to_bytes(2, "big")).hexdigest() for index in range(216))

    def root(self, positions):
        return sha256(b"".join(bytes.fromhex(item) for item in positions)).hexdigest()


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.receipts: dict[str, str] = {}
        scheduler = Hash216ProjectionScheduler(
            authority=FakeAuthority(),
            receipt_verifier=lambda receipt, root: self.receipts.get(receipt) == root,
        )
        self.runtime = Pass158GuiProjectionRuntime(scheduler)

    def test_complete_projection_lifecycle(self):
        _, registered = self.runtime.dispatch("POST", f"{BASE}/objects/register", {
            "object_id": "addresses", "object_class": "STATIC_ADDRESS_OBJECT",
            "value": {"count": 5184}, "static": True,
        })
        self.assertEqual(registered["status"], "INDEXED")
        _, observed = self.runtime.dispatch("POST", f"{BASE}/runtime/observe", {
            "object_id": "positions", "object_class": "PHYSICS_POSITION_OBJECT",
            "state": [1, 2, 3],
        })
        self.assertTrue(observed["object"]["changed"])
        _, budget = self.runtime.dispatch("POST", f"{BASE}/frame/telemetry", {
            "frame_sequence": 1, "target_frame_ns": 100, "physics_ns": 20, "render_ns": 20,
        })
        self.assertEqual(budget["classification"], "FRAME_BUDGET_NORMAL")
        _, next_package = self.runtime.dispatch("POST", f"{BASE}/packages/next", {"frame_sequence": 1})
        package = next_package["object"]
        self.assertEqual(package["changed_chunk_count"], 2)
        receipt = "0" * 72
        self.receipts[receipt] = package["projection_root_hash216"]
        _, admitted = self.runtime.dispatch("POST", f"{BASE}/packages/{package['projection_root_hash216']}/admit", {
            "admitted": True, "receipt_hash72": receipt,
        })
        self.assertEqual(admitted["status"], "ADMITTED")

    def test_unverified_admission_is_rejected(self):
        self.runtime.dispatch("POST", f"{BASE}/runtime/observe", {
            "object_id": "positions", "object_class": "PHYSICS_POSITION_OBJECT", "state": [1],
        })
        _, built = self.runtime.dispatch("POST", f"{BASE}/packages/next", {"frame_sequence": 1})
        root = built["object"]["projection_root_hash216"]
        _, missing = self.runtime.dispatch("POST", f"{BASE}/packages/{root}/admit", {"admitted": True})
        self.assertEqual(missing["classification"], "HASH72_RECEIPT_REQUIRED_FOR_ADMISSION")
        _, forged = self.runtime.dispatch("POST", f"{BASE}/packages/{root}/admit", {
            "admitted": True, "receipt_hash72": "1" * 72,
        })
        self.assertEqual(forged["classification"], "HASH72_RECEIPT_MISMATCH")

    def test_snapshot_recovery_endpoint(self):
        self.runtime.dispatch("POST", f"{BASE}/runtime/observe", {
            "object_id": "positions", "object_class": "PHYSICS_POSITION_OBJECT", "state": [1],
        })
        _, snapshot = self.runtime.dispatch("GET", f"{BASE}/snapshot", {})
        new_runtime = Pass158GuiProjectionRuntime(
            Hash216ProjectionScheduler(authority=FakeAuthority())
        )
        _, recovered = new_runtime.dispatch("POST", f"{BASE}/recover", {"snapshot": snapshot["object"]})
        self.assertEqual(recovered["status"], "RECOVERED")
        self.assertEqual(recovered["object"]["objects"], 1)

    def test_unknown_endpoint_rejected(self):
        _, response = self.runtime.dispatch("GET", f"{BASE}/missing", {})
        self.assertEqual(response["status"], "REJECTED")
        self.assertEqual(response["classification"], "ENDPOINT_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
