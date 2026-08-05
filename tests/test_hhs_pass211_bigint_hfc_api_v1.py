from __future__ import annotations

import math

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.pass211_bigint_hfc_routes import router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_status_encode_decode_recover_and_anchored_compare() -> None:
    client = _client()
    status = client.get("/api/runtime/bigint-hfc-carrier/status")
    assert status.status_code == 200
    assert status.json()["packed_shard_bytes"] == 648

    value = math.factorial(72)
    encoded = client.post(
        "/api/runtime/bigint-hfc-carrier/encode",
        json={"ciphertext_hex": hex(value)},
    )
    assert encoded.status_code == 200, encoded.text
    package = encoded.json()
    assert package["shard_count"] == 1

    decoded = client.post(
        "/api/runtime/bigint-hfc-carrier/decode",
        json={"package": package},
    )
    assert decoded.status_code == 200, decoded.text
    assert decoded.json()["ciphertext_hex"] == hex(value)

    recovered = client.post(
        "/api/runtime/bigint-hfc-carrier/recover",
        json={"package": package, "shard_index": 0, "lost_snapshot_index": 35},
    )
    assert recovered.status_code == 200, recovered.text
    assert recovered.json()["status"] == "PASS211_SHARD_ERASURE_RECOVERY_VERIFIED"

    payload = bytearray.fromhex(package["shards"][0]["payload_hex"])
    payload[1000 // 8] ^= 1 << (7 - (1000 % 8))
    compared = client.post(
        "/api/runtime/bigint-hfc-carrier/anchored-compare",
        json={
            "package": package,
            "shard_index": 0,
            "fresh_payload_hex": payload.hex(),
        },
    )
    assert compared.status_code == 200, compared.text
    assert compared.json()["disagreement_cells"] == [1000]


def test_api_rejects_zero_and_tampered_package() -> None:
    client = _client()
    zero = client.post(
        "/api/runtime/bigint-hfc-carrier/encode",
        json={"ciphertext_hex": "0x0"},
    )
    assert zero.status_code == 422
    assert "PASS133_ENVELOPE_REJECTED" in zero.json()["detail"]

    encoded = client.post(
        "/api/runtime/bigint-hfc-carrier/encode",
        json={"ciphertext_hex": "0x133"},
    ).json()
    encoded["package_receipt_hash72"] = "0" * 72
    rejected = client.post(
        "/api/runtime/bigint-hfc-carrier/decode",
        json={"package": encoded},
    )
    assert rejected.status_code == 409
    assert "PACKAGE_RECEIPT_MISMATCH" in rejected.json()["detail"]
