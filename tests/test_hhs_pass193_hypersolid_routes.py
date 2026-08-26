from __future__ import annotations

from base64 import b64encode
from pathlib import Path
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api import pass193_hypersolid_routes as routes
from hhs_backend.runtime.hhs_pass193_hypersolid_native_egress_v1 import Pass193Runtime
from hhs_runtime.core.hash72_digest_v1 import hash72_digest


LICENSE = {"closed": True, "license_id": "TEST-ONLY-LICENSE"}


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P193_ROUTE_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P193_ROUTE_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


class Pass193RouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = Pass193Runtime(Path(self.temp.name))
        routes._RUNTIME = self.runtime
        app = FastAPI()
        app.include_router(routes.router)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        routes._RUNTIME = None
        self.temp.cleanup()

    def test_url_safe_identity_transport_and_mutation_flow(self) -> None:
        status = self.client.get("/api/runtime/hypersolids/status")
        self.assertEqual(status.status_code, 200)
        self.assertTrue(status.json()["vm81_singleton_required"])
        self.assertFalse(status.json()["float_canonical_authority"])

        created = self.client.post(
            "/api/runtime/hypersolids",
            json={
                "family": "8-cell",
                "dimension": 4,
                "authority_execution": authority(1),
            },
        )
        self.assertEqual(created.status_code, 200)
        root = created.json()
        self.assertEqual(routes._decode_ref(root["object_id_ref"]), root["object_id"])
        self.assertNotIn("/", root["object_id_ref"])

        fetched = self.client.get(
            f"/api/runtime/hypersolids/{root['object_id_ref']}"
        )
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json()["hash216_identity"], root["hash216_identity"])

        rotated = self.client.post(
            f"/api/runtime/hypersolids/{root['object_id_ref']}/rotate",
            json={
                "plane": [0, 3],
                "numerator": 1,
                "denominator": 8,
                "authority_execution": authority(2),
            },
        )
        self.assertEqual(rotated.status_code, 200)
        rotated_body = rotated.json()
        self.assertEqual(rotated_body["transform_history"][-1]["phase"], {"numerator": 1, "denominator": 8})
        self.assertNotEqual(rotated_body["hash216_identity"], root["hash216_identity"])

        projection = self.client.post(
            f"/api/runtime/hypersolids/{rotated_body['object_id_ref']}/project",
            json={"target_dimension": 3},
        )
        self.assertEqual(projection.status_code, 200)
        self.assertEqual(projection.json()["classification"], "NONCANONICAL_PROJECTION")

        replay = self.client.get("/api/runtime/hypersolids/replay/all")
        self.assertEqual(replay.status_code, 200)
        self.assertEqual(replay.json()["receipt_count"], 2)

    def test_native_package_nft_api_separates_identity_from_execution_authority(self) -> None:
        created = self.client.post(
            "/api/runtime/hypersolids",
            json={
                "family": "cube",
                "dimension": 3,
                "authority_execution": authority(1),
            },
        ).json()

        compiled = self.client.post(
            f"/api/runtime/hypersolids/{created['object_id_ref']}/compile",
            json={
                "target": "linux-x86_64-elf",
                "binary_b64": b64encode(b"P193-API-BINARY").decode("ascii"),
                "compiler_identity": "test-cc",
                "compiler_flags": ["-O2"],
                "linker_identity": "test-ld",
                "build_environment": {"profile": "api-test"},
                "evidence": {
                    "compiled": True,
                    "linked": True,
                    "launched": True,
                    "abi_validated": True,
                    "deterministic_workload": True,
                },
                "license_manifest": LICENSE,
                "authority_execution": authority(2),
            },
        )
        self.assertEqual(compiled.status_code, 200)
        artifact = compiled.json()

        package = self.client.post(
            f"/api/runtime/hypersolids/{created['object_id_ref']}/package",
            json={
                "artifact_ids": [artifact["artifact_id"]],
                "capabilities": ["filesystem:read:app"],
                "license_manifest": LICENSE,
                "authority_execution": authority(3),
            },
        )
        self.assertEqual(package.status_code, 200)
        package_body = package.json()

        nft = self.client.post(
            "/api/runtime/hypersolids/nft-executables/create",
            json={
                "package_id": package_body["package_id"],
                "rights": {"license_manifest_identity": "TEST-ONLY-LICENSE"},
                "authority_execution": authority(4),
            },
        )
        self.assertEqual(nft.status_code, 200)
        nft_body = nft.json()
        self.assertFalse(nft_body["execution_authorized"])
        self.assertFalse(nft_body["identity_is_execution_authority"])

        denied = self.client.post(
            f"/api/runtime/hypersolids/nft-executables/{nft_body['nft_executable_id_ref']}/authorize",
            json={
                "identity_verified": True,
                "capability_admitted": False,
                "platform_validated": True,
                "policy_accepted": True,
                "runtime_integrity": True,
                "authority_execution": authority(5),
            },
        )
        self.assertEqual(denied.status_code, 409)
        self.assertEqual(denied.json()["detail"], "HHS_P193_EXECUTION_ADMISSION_DENIED")

        admitted = self.client.post(
            f"/api/runtime/hypersolids/nft-executables/{nft_body['nft_executable_id_ref']}/authorize",
            json={
                "identity_verified": True,
                "capability_admitted": True,
                "platform_validated": True,
                "policy_accepted": True,
                "runtime_integrity": True,
                "authority_execution": authority(6),
            },
        )
        self.assertEqual(admitted.status_code, 200)
        self.assertTrue(admitted.json()["execution_authorized"])
        self.assertFalse(admitted.json()["identity_is_execution_authority"])


if __name__ == "__main__":
    unittest.main()
