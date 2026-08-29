from __future__ import annotations

from base64 import b64encode
from pathlib import Path
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api import pass194_storage_training_routes as routes
from hhs_backend.runtime.hhs_pass194_multimodal_storage_training_v1 import Pass194Runtime
from hhs_runtime.core.hash72_digest_v1 import hash72_digest


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P194_ROUTE_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P194_ROUTE_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


class Pass194RouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = Pass194Runtime(Path(self.temp.name), vector_key=bytes(range(32)))
        routes._RUNTIME = self.runtime
        app = FastAPI()
        app.include_router(routes.router)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        routes._RUNTIME = None
        self.runtime.close()
        self.temp.cleanup()

    def test_status_and_governed_dataset_flow(self) -> None:
        status = self.client.get("/api/runtime/storage-training/status")
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.json()["training_default"], "DENY")
        self.assertFalse(status.json()["vector_store_is_source_authority"])

        workspace = self.client.post(
            "/api/runtime/storage-training/workspaces",
            json={
                "workspace_id": "ws",
                "owner_id": "owner",
                "authority_execution": authority(1),
            },
        )
        self.assertEqual(workspace.status_code, 200)

        upload = self.client.post(
            "/api/runtime/storage-training/files",
            json={
                "workspace_id": "ws",
                "owner_id": "owner",
                "logical_path": "training/input.txt",
                "data_b64": b64encode(b"hello pass194").decode("ascii"),
                "modality": "TEXT",
                "metadata": {"source": "user"},
                "authority_execution": authority(2),
            },
        )
        self.assertEqual(upload.status_code, 200)
        file_version_id = upload.json()["file_version_id"]

        denied_snapshot = self.client.post(
            "/api/runtime/storage-training/snapshots",
            json={"workspace_id": "ws", "authority_execution": authority(3)},
        )
        self.assertEqual(denied_snapshot.status_code, 200)
        denied_dataset = self.client.post(
            "/api/runtime/storage-training/datasets",
            json={
                "snapshot_id": denied_snapshot.json()["snapshot_id"],
                "authority_execution": authority(4),
            },
        )
        self.assertEqual(denied_dataset.status_code, 409)
        self.assertEqual(denied_dataset.json()["detail"], "HHS_P194_TRAINING_CONSENT_DENIED")

        consent = self.client.post(
            "/api/runtime/storage-training/consent",
            json={
                "file_version_id": file_version_id,
                "training_allowed": True,
                "sharing_allowed": False,
                "public_allowed": False,
                "license_id": "user-license-v1",
                "authority_execution": authority(4),
            },
        )
        self.assertEqual(consent.status_code, 200)

        snapshot = self.client.post(
            "/api/runtime/storage-training/snapshots",
            json={"workspace_id": "ws", "authority_execution": authority(5)},
        )
        self.assertEqual(snapshot.status_code, 200)
        dataset = self.client.post(
            "/api/runtime/storage-training/datasets",
            json={
                "snapshot_id": snapshot.json()["snapshot_id"],
                "authority_execution": authority(6),
            },
        )
        self.assertEqual(dataset.status_code, 200)
        self.assertTrue(dataset.json()["consent_closed"])

        replay = self.client.get("/api/runtime/storage-training/replay")
        self.assertEqual(replay.status_code, 200)
        self.assertTrue(replay.json()["deterministic_replay"])

    def test_invalid_base64_and_authority_fail_closed(self) -> None:
        self.client.post(
            "/api/runtime/storage-training/workspaces",
            json={
                "workspace_id": "ws",
                "owner_id": "owner",
                "authority_execution": authority(1),
            },
        )
        invalid = self.client.post(
            "/api/runtime/storage-training/files",
            json={
                "workspace_id": "ws",
                "owner_id": "owner",
                "logical_path": "bad.bin",
                "data_b64": "%%not-base64%%",
                "authority_execution": authority(2),
            },
        )
        self.assertEqual(invalid.status_code, 400)

        bad_authority = self.client.post(
            "/api/runtime/storage-training/files",
            json={
                "workspace_id": "ws",
                "owner_id": "owner",
                "logical_path": "bad.bin",
                "data_b64": b64encode(b"x").decode("ascii"),
                "authority_execution": {"receipt": {}},
            },
        )
        self.assertEqual(bad_authority.status_code, 409)
        self.assertEqual(bad_authority.json()["detail"], "HHS_P194_VM81_AUTHORITY_REQUIRED")


if __name__ == "__main__":
    unittest.main()
