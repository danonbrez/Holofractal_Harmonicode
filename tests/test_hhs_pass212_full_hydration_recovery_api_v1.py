from hashlib import sha256

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.pass212_full_hydration_recovery_routes import router
from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import AFFINE_SEED_BYTES


def seeds():
    out=bytearray(); i=0
    while len(out)<AFFINE_SEED_BYTES:
        out.extend(sha256(f'api-pass212-{i}'.encode()).digest()); i+=1
    return bytes(out[:AFFINE_SEED_BYTES])


def client():
    app=FastAPI(); app.include_router(router); return TestClient(app)


def test_status_exposes_full_hydration_capacity():
    response=client().get('/api/runtime/full-hydration-recovery/status')
    assert response.status_code==200
    body=response.json()
    assert body['dimensions']['full_hydration_bits']==50_388_480
    assert body['dimensions']['full_hydration_bytes']==6_298_560
    assert body['protection']['recoverable_missing_physical_shards_per_stripe']==2


def test_encode_and_recover_two_missing_payload_shards():
    c=client()
    encoded=c.post('/api/runtime/full-hydration-recovery/encode-affine',json={
        'seed_hex':seeds().hex(),
        'exception_positions':[101,10001,20001,30001],
    })
    assert encoded.status_code==200, encoded.text
    package=encoded.json()['package']
    refs=[s['stripe'] for s in package['protected']['shards'] if s['role']=='data']
    shard_refs=[f"{s['stripe']}:{s['role']}:{s['index']}" for s in package['protected']['shards'] if s['role']=='data'][:2]
    recovered=c.post('/api/runtime/full-hydration-recovery/recover',json={
        'package':package,
        'unavailable_shards':shard_refs,
    })
    assert recovered.status_code==200, recovered.text
    body=recovered.json()
    assert body['status']=='PASS212_FULL_HYDRATION_RECOVERY_VERIFIED'
    assert body['recovered_bytes']==6_298_560


def test_bad_seed_rejected():
    response=client().post('/api/runtime/full-hydration-recovery/encode-affine',json={'seed_hex':'00'})
    assert response.status_code==422
