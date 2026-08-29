from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass194_multimodal_storage_training_v1 import (
    LEGACY_FOUNDATION_ROOT,
    GENESIS_IDENTITY,
    Pass194Error,
    Pass194Runtime,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P194_TEST_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P194_TEST_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


class Pass194RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.key = bytes(range(32))
        self.runtime = Pass194Runtime(self.root, vector_key=self.key)

    def tearDown(self) -> None:
        self.runtime.close()
        self.temp.cleanup()

    def _workspace_and_file(self) -> dict[str, object]:
        self.runtime.ensure_workspace("ws", "owner", authority_execution=authority(1))
        return self.runtime.ingest_bytes(
            "ws",
            "owner",
            "docs/a.txt",
            b"alpha",
            modality="TEXT",
            metadata={"topic": "test"},
            authority_execution=authority(2),
        )

    def test_default_deny_requires_consent_and_fresh_snapshot(self) -> None:
        record = self._workspace_and_file()
        first = self.runtime.create_snapshot("ws", authority_execution=authority(3))
        with self.assertRaisesRegex(Pass194Error, "HHS_P194_TRAINING_CONSENT_DENIED"):
            self.runtime.release_dataset(first["snapshot_id"], authority_execution=authority(4))

        consent = self.runtime.set_consent(
            record["file_version_id"],
            training_allowed=True,
            sharing_allowed=False,
            public_allowed=False,
            license_id="user-authorized-training-v1",
            authority_execution=authority(4),
        )
        self.assertTrue(consent["training_allowed"])
        with self.assertRaisesRegex(Pass194Error, "HHS_P194_TRAINING_CONSENT_DENIED"):
            self.runtime.release_dataset(first["snapshot_id"], authority_execution=authority(5))

        second = self.runtime.create_snapshot("ws", authority_execution=authority(5))
        dataset = self.runtime.release_dataset(
            second["snapshot_id"], authority_execution=authority(6)
        )
        self.assertTrue(dataset["consent_closed"])
        self.assertTrue(dataset["license_closed"])
        self.assertEqual(self.runtime.status()["training_default"], "DENY")

    def test_content_addressed_versions_are_immutable_and_idempotent(self) -> None:
        first = self._workspace_and_file()
        first_blob = self.runtime._blob_path(first["blob_sha256"])
        self.assertTrue(first_blob.is_file())
        self.assertEqual(first_blob.read_bytes(), b"alpha")

        second = self.runtime.ingest_bytes(
            "ws",
            "owner",
            "docs/a.txt",
            b"beta",
            modality="TEXT",
            metadata={"topic": "test"},
            authority_execution=authority(3),
        )
        self.assertEqual(second["version_index"], 2)
        self.assertNotEqual(first["blob_sha256"], second["blob_sha256"])
        self.assertEqual(first_blob.read_bytes(), b"alpha")

        repeated = self.runtime.ingest_bytes(
            "ws",
            "owner",
            "docs/a.txt",
            b"beta",
            modality="TEXT",
            metadata={"topic": "test"},
            authority_execution=authority(4),
        )
        self.assertTrue(repeated["idempotent"])
        self.assertEqual(repeated["file_version_id"], second["file_version_id"])
        self.assertEqual(self.runtime.status()["file_versions"], 2)

    def test_encrypted_vector_projection_is_derived_non_authority(self) -> None:
        record = self._workspace_and_file()
        frame = bytes([7]) * SNAPSHOT_BYTES
        projection = self.runtime.store_vector_projection(
            record["file_version_id"],
            frame,
            model_id="compat-embedding-v1",
            logical_step=11,
            authority_execution=authority(3),
        )
        self.assertFalse(projection["vector_is_source_authority"])
        self.assertFalse(projection["vector_is_consent_authority"])
        self.assertFalse(projection["vector_is_vm81_authority"])
        obj, recovered = self.runtime.vector_store.retrieve(
            projection["operation_key"],
            legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
            genesis_identity=GENESIS_IDENTITY,
        )
        self.assertEqual(obj.object_id, projection["vector_object_id"])
        self.assertEqual(recovered, frame)
        status = self.runtime.status()
        self.assertFalse(status["vector_store_is_source_authority"])
        self.assertFalse(status["vector_store_is_consent_authority"])

    def test_dataset_training_checkpoint_and_delete_propagation(self) -> None:
        record = self._workspace_and_file()
        self.runtime.set_consent(
            record["file_version_id"],
            training_allowed=True,
            license_id="license-ok",
            authority_execution=authority(3),
        )
        snapshot = self.runtime.create_snapshot("ws", authority_execution=authority(4))
        dataset = self.runtime.release_dataset(
            snapshot["snapshot_id"], authority_execution=authority(5)
        )
        run = self.runtime.begin_training_run(
            dataset["dataset_id"],
            run_kind="FINE_TUNE",
            model_base_id="model-base",
            authority_execution=authority(6),
        )
        checkpoint = self.runtime.record_checkpoint(
            run["run_id"],
            artifact_sha256=sha256(b"checkpoint").hexdigest(),
            metrics={"exact_steps": 12, "accepted": True},
            authority_execution=authority(7),
        )
        self.assertFalse(checkpoint["checkpoint_is_vm81_authority"])

        deleted = self.runtime.delete_file(
            record["file_id"],
            reason="user requested deletion",
            authority_execution=authority(8),
        )
        self.assertIn(dataset["dataset_id"], deleted["revoked_dataset_ids"])
        self.assertFalse(self.runtime._blob_path(record["blob_sha256"]).exists())
        dataset_row = self.runtime._connection.execute(
            "SELECT revoked FROM dataset_releases WHERE dataset_id=?",
            (dataset["dataset_id"],),
        ).fetchone()
        run_row = self.runtime._connection.execute(
            "SELECT status FROM training_runs WHERE run_id=?", (run["run_id"],)
        ).fetchone()
        self.assertEqual(int(dataset_row["revoked"]), 1)
        self.assertEqual(run_row["status"], "REVOKED")

    def test_restart_and_replay_validate_receipt_snapshot_dataset_identity(self) -> None:
        record = self._workspace_and_file()
        self.runtime.set_consent(
            record["file_version_id"],
            training_allowed=True,
            license_id="license-ok",
            authority_execution=authority(3),
        )
        snapshot = self.runtime.create_snapshot("ws", authority_execution=authority(4))
        self.runtime.release_dataset(snapshot["snapshot_id"], authority_execution=authority(5))
        first = self.runtime.replay()
        self.assertTrue(first["deterministic_replay"])
        receipt_head = first["receipt_head_hash72"]
        self.runtime.close()
        self.runtime = Pass194Runtime(self.root, vector_key=self.key)
        second = self.runtime.replay()
        self.assertEqual(second["receipt_head_hash72"], receipt_head)
        self.assertTrue(second["snapshot_identity_verified"])
        self.assertTrue(second["dataset_identity_verified"])

    def test_authority_receipt_is_single_use_and_malformed_authority_fails_closed(self) -> None:
        shared = authority(1)
        self.runtime.ensure_workspace("ws", "owner", authority_execution=shared)
        with self.assertRaisesRegex(Pass194Error, "HHS_P194_VM81_AUTHORITY_RECEIPT_REUSED"):
            self.runtime.ensure_workspace("ws2", "owner", authority_execution=shared)
        with self.assertRaisesRegex(Pass194Error, "HHS_P194_VM81_AUTHORITY_REQUIRED"):
            self.runtime.ensure_workspace(
                "ws3", "owner", authority_execution={"receipt": {}}
            )

    def test_canonical_metadata_rejects_float(self) -> None:
        self.runtime.ensure_workspace("ws", "owner", authority_execution=authority(1))
        with self.assertRaisesRegex(Pass194Error, "HHS_P194_FLOAT_CANONICAL_METADATA_FORBIDDEN"):
            self.runtime.ingest_bytes(
                "ws",
                "owner",
                "bad.json",
                b"{}",
                modality="JSON",
                metadata={"score": 0.5},
                authority_execution=authority(2),
            )


if __name__ == "__main__":
    unittest.main()
