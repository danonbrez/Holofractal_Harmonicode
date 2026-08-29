from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.pass192_fibonacci_routes import _set_runtime_for_tests, router
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass192.runtime import Pass192Runtime


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P192_API_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P192_API_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


class Pass192RoutesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        runtime = Pass192Runtime(Path(self.temp.name))
        _set_runtime_for_tests(runtime)
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        _set_runtime_for_tests(None)
        self.temp.cleanup()

    def test_status_registry_and_full_workflow(self) -> None:
        status = self.client.get("/v1/tensors/fibonacci/status")
        self.assertEqual(status.status_code, 200)
        self.assertFalse(status.json()["float_canonical_authority"])

        registry = self.client.get("/v1/tensors/fibonacci/operation-registry")
        self.assertEqual(registry.status_code, 200)
        self.assertEqual(
            registry.json()["operation_ids"]["create"],
            "P192.CellularFibonacciTensor",
        )

        created = self.client.post(
            "/v1/tensors/fibonacci",
            json={"row": 0, "column": 0, "authority_execution": authority(1)},
        )
        self.assertEqual(created.status_code, 200)
        tensor = created.json()
        self.assertEqual(len(tensor["tensor_id"]), 216)
        tensor_ref = tensor["tensor_id_ref"]

        inspected = self.client.get(f"/v1/tensors/fibonacci/{tensor_ref}")
        self.assertEqual(inspected.status_code, 200)
        self.assertEqual(inspected.json()["tensor_id"], tensor["tensor_id"])

        materialized = self.client.post(
            f"/v1/tensors/fibonacci/{tensor_ref}/materialize",
            json={"depth": 2, "authority_execution": authority(2)},
        )
        self.assertEqual(materialized.status_code, 200)
        self.assertEqual(materialized.json()["node_count"], 75)

        validated = self.client.post(
            f"/v1/tensors/fibonacci/{tensor_ref}/validate"
        )
        self.assertEqual(validated.status_code, 200)
        self.assertTrue(validated.json()["ok"])

        replayed = self.client.post(
            f"/v1/tensors/fibonacci/{tensor_ref}/replay"
        )
        self.assertEqual(replayed.status_code, 200)
        self.assertTrue(replayed.json()["ok"])


if __name__ == "__main__":
    unittest.main()
