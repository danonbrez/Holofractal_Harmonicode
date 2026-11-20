"""Test authoritative Pass219 bridge composition without claiming native admission."""
from hashlib import sha256
import tempfile
import unittest

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_lane5_continuation_v1 import (
    VM81_FRAME_BYTES, NativeContinuationError, continue_staged_to_lane5,
)


class BridgeStub:
    def __init__(self, *, altered=None, authority_override=None):
        self.altered = altered or {}
        self.authority_override = authority_override or {}
        self.seen = None

    def authority(self):
        result = {
            "any_byte_serializable_workload": True,
            "workload_class_agnostic": True,
            "streaming_candidate_ingress": True,
            "candidate_only": True,
            "requires_signed_environmental_vm81_admission": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash216_authority": False,
        }
        result.update(self.authority_override)
        return result

    def optimize(self, **kwargs):
        self.seen = kwargs
        workload = kwargs["workload"]
        result = {
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash216_authority": False,
            "requires_signed_environmental_vm81_admission": True,
            "admitted_candidates": 1,
            "workload_sha256": workload.workload_sha256.hex(),
            "workload_byte_count": workload.byte_count,
        }
        result.update(self.altered)
        return result


class TestAdminLane5NativeContinuation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.stage = AdminStreamStaging(self.temp.name)
        self.addCleanup(self.stage.close)
        self.id = self.stage.create("root", "unrecognized.modality")["upload_id"]

    def finalize(self, data):
        for start in range(0, len(data), 648):
            self.stage.append(self.id, "root", start, data[start:start + 648])
        return self.stage.finalize(self.id, "root")

    def test_native_648_byte_frame_width(self):
        self.assertEqual(VM81_FRAME_BYTES, 648)

    def test_unknown_binary_spanning_native_frames(self):
        source = bytes(range(256)) * 7 + b"end"
        self.finalize(source)
        mock = BridgeStub()
        result = continue_staged_to_lane5(self.stage, self.id, "root", bridge_factory=lambda: mock)
        self.assertFalse(result["canonical_hash216_admitted"])
        self.assertEqual(mock.seen["workload"].byte_count, len(source))
        self.assertEqual(mock.seen["workload"].workload_sha256.hex(), sha256(source).hexdigest())
        self.assertEqual(len(tuple(mock.seen["candidates"])), 1)

    def test_unstaged_cannot_be_candidate(self):
        with self.assertRaises(NativeContinuationError):
            continue_staged_to_lane5(self.stage, self.id, "root", bridge_factory=BridgeStub)

    def test_wrong_owner_cannot_read(self):
        self.finalize(b"abc")
        with self.assertRaises(Exception):
            continue_staged_to_lane5(self.stage, self.id, "intruder", bridge_factory=BridgeStub)

    def test_reject_fabricated_canonical_authority(self):
        self.finalize(b"abc")
        with self.assertRaises(NativeContinuationError):
            continue_staged_to_lane5(self.stage, self.id, "root", bridge_factory=lambda: BridgeStub(
                altered={"canonical_hash216_authority": True}))

    def test_reject_missing_native_authority(self):
        self.finalize(b"abc")
        with self.assertRaises(NativeContinuationError):
            continue_staged_to_lane5(self.stage, self.id, "root", bridge_factory=lambda: BridgeStub(
                authority_override={"streaming_candidate_ingress": False}))

    def test_reject_digest_mismatch(self):
        self.finalize(b"abc")
        with self.assertRaises(NativeContinuationError):
            continue_staged_to_lane5(self.stage, self.id, "root", bridge_factory=lambda: BridgeStub(
                altered={"workload_sha256": "0" * 64}))

    def test_empty_object(self):
        self.finalize(b"")
        result = continue_staged_to_lane5(self.stage, self.id, "root", bridge_factory=BridgeStub)
        self.assertEqual(result["native_candidate_receipt"]["workload_byte_count"], 0)


if __name__ == "__main__":
    unittest.main()
