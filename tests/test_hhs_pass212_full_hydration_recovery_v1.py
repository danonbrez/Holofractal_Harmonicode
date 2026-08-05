from hashlib import sha256
import pytest

from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
    AFFINE_SEED_BYTES,
    FULL_FRAME_COUNT,
    FULL_HYDRATION_BITS,
    FULL_HYDRATION_BYTES,
    LOCAL_FRAME_BYTES,
    FullHydrationRecoveryRuntime,
    Pass212UnrecoverableError,
    Pass212ValidationError,
    apply_bit_exceptions,
    generate_affine_hydration,
)


def seed_bytes():
    out=bytearray()
    counter=0
    while len(out)<AFFINE_SEED_BYTES:
        out.extend(sha256(f'pass212-seed-{counter}'.encode()).digest())
        counter+=1
    return bytes(out[:AFFINE_SEED_BYTES])


def deterministic_bytes(length):
    out=bytearray(); counter=0
    while len(out)<length:
        out.extend(sha256(b'raw'+counter.to_bytes(8,'big')).digest()); counter+=1
    return bytes(out[:length])


def test_dimensions():
    rt=FullHydrationRecoveryRuntime()
    status=rt.status()
    assert FULL_HYDRATION_BITS == 50_388_480
    assert FULL_HYDRATION_BYTES == 6_298_560
    assert status['dimensions']['full_frame_count'] == 9_720
    assert status['dimensions']['affine_seed_bytes'] == 2_430


def test_affine_full_hydration_compresses_and_recovers_two_shards():
    rt=FullHydrationRecoveryRuntime()
    state=generate_affine_hydration(seed_bytes())
    assert len(state)==FULL_HYDRATION_BYTES
    positions=tuple(range(101, 101+4096*997, 997))
    state=apply_bit_exceptions(state, positions)
    pkg=rt.encode(state)
    assert pkg.codec == 'AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR'
    assert pkg.compressed_payload_bytes < 100_000
    assert rt.decode(pkg)==state
    data_refs=[s.ref for s in pkg.protected.shards if s.role=='data']
    assert len(data_refs)>=2
    degraded=rt.without_shards(pkg, data_refs[:2])
    assert rt.decode(degraded)==state


def test_data_plus_parity_loss_recovers():
    rt=FullHydrationRecoveryRuntime()
    state=generate_affine_hydration(seed_bytes())
    pkg=rt.encode(state)
    stripe0=[s for s in pkg.protected.shards if s.stripe==0]
    data=next(s.ref for s in stripe0 if s.role=='data')
    p0=next(s.ref for s in stripe0 if s.role=='parity0')
    assert rt.decode(rt.without_shards(pkg,[data,p0]))==state


def test_over_budget_fails_closed():
    rt=FullHydrationRecoveryRuntime()
    pkg=rt.encode(generate_affine_hydration(seed_bytes()))
    refs=[s.ref for s in pkg.protected.shards if s.stripe==0 and s.role=='data'][:3]
    with pytest.raises(Pass212UnrecoverableError):
        rt.decode(rt.without_shards(pkg, refs))


def test_corruption_detected():
    rt=FullHydrationRecoveryRuntime()
    pkg=rt.encode(generate_affine_hydration(seed_bytes()))
    ref=next(s.ref for s in pkg.protected.shards if s.role=='data')
    with pytest.raises(Pass212ValidationError):
        rt.decode(rt.corrupt_shard(pkg,ref))


def test_raw_full_capacity_fallback_and_last_stripe_recovery():
    rt=FullHydrationRecoveryRuntime()
    state=deterministic_bytes(FULL_HYDRATION_BYTES)
    pkg=rt.encode(state)
    assert pkg.codec == 'RAW_PACKED_FALLBACK'
    assert pkg.protected.data_shard_count == FULL_FRAME_COUNT
    assert pkg.protected.stripe_count == 40
    last_stripe=max(s.stripe for s in pkg.protected.shards)
    ref=next(s.ref for s in pkg.protected.shards if s.stripe==last_stripe and s.role=='data')
    assert rt.decode(rt.without_shards(pkg,[ref]))==state
