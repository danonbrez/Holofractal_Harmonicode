from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.pass210_holographic_frame_compression_routes import API_PREFIX, router
from hhs_backend.runtime.hhs_pass210_holographic_frame_compression_v1 import (
    REGISTER_LEN,
    affine_fibonacci_mod2,
)


def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_status_and_full_frame_workflow() -> None:
    raw = bytes(index & 1 for index in range(REGISTER_LEN))
    with client() as http:
        status = http.get(f"{API_PREFIX}/status")
        assert status.status_code == 200
        assert all(status.json()["invariants"].values())
        encoded = http.post(f"{API_PREFIX}/frames/encode", json={"register_hex": raw.hex()})
        assert encoded.status_code == 200
        frame_id = encoded.json()["frame_id"]
        decoded = http.post(f"{API_PREFIX}/frames/{frame_id}/decode")
        assert decoded.status_code == 200
        assert decoded.json()["register_hex"] == raw.hex()
        snapshot = http.get(f"{API_PREFIX}/frames/{frame_id}/snapshots/35")
        assert snapshot.status_code == 200
        assert snapshot.json()["section_lengths"] == [89, 55, 89, 55]
        recovered = http.post(
            f"{API_PREFIX}/frames/{frame_id}/recover", json={"lost_index": 35}
        )
        assert recovered.status_code == 200
        assert recovered.json()["register_hex"] == raw.hex()


def test_view_agreement_and_strict_compression_api() -> None:
    raw = affine_fibonacci_mod2(0, 1)
    with client() as http:
        admitted = http.post(
            f"{API_PREFIX}/views/admit", json={"k": 5, "c": 1, "modulus": 361}
        )
        assert admitted.status_code == 200
        assert admitted.json()["inverse_k"] == 289
        rejected = http.post(
            f"{API_PREFIX}/views/admit", json={"k": 6, "c": 1, "modulus": 12}
        )
        assert rejected.status_code == 409
        assert "HFC_NON_BIJECTIVE_VIEW_REJECTED" in rejected.text
        agreement = http.post(
            f"{API_PREFIX}/agree",
            json={
                "register_hex": raw.hex(),
                "modalities": ["raw", "hash72", "hash216", "phase", "frame"],
            },
        )
        assert agreement.status_code == 200
        assert agreement.json()["agreement"] is True
        assert agreement.json()["disagreement_cells"] == []
        compressed = http.post(f"{API_PREFIX}/strict/compress", json={"register_hex": raw.hex()})
        assert compressed.status_code == 200
        decompressed = http.post(
            f"{API_PREFIX}/strict/decompress", json={"package": compressed.json()}
        )
        assert decompressed.status_code == 200
        assert decompressed.json()["register_hex"] == raw.hex()
