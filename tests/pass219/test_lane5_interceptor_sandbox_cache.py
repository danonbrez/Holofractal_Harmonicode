from __future__ import annotations

import pytest

from hhs_runtime.pass219.lane5_interceptor_sandbox_cache import (
    CALIBRATION_SCHEMA,
    FRAME_BYTES,
    Lane5CacheCalibration,
    Lane5InterceptorSandboxCache,
    Lane5SandboxCacheError,
    MEASURED_MAXIMUM,
    RAW_CAPACITY_UNIT,
    VERIFIED_RAW_BYTE_FLOOR,
    VERIFIED_RAW_LINUX_SERIAL_BYTE_FLOOR,
)


def measured_evidence(max_bytes: int) -> dict[str, object]:
    return {
        "schema": CALIBRATION_SCHEMA,
        "classification": MEASURED_MAXIMUM,
        "capacity_unit": RAW_CAPACITY_UNIT,
        "max_serial_abi_bytes": max_bytes,
        "probe_ceiling_bytes": max_bytes + 4096,
        "page_size": 4096,
        "probe_attempts": 7,
        "benchmark_window_ns": 123456789,
        "benchmark_id": "TEST_RAW_LINUX_SERIAL_ABI_CAPACITY",
        "kernel_id": "Linux test-kernel",
        "libc_id": "glibc test",
        "compiler_id": "gcc test",
        "environment": {
            "system": "Linux",
            "release": "test",
            "machine": "x86_64",
            "processor": "test-cpu",
            "logical_cpu_count": 4,
        },
        "hhs_present": False,
        "vm81_services_present": False,
        "lane5_present": False,
        "rna_services_present": False,
        "hash72_present": False,
        "hash216_present": False,
        "pqc_present": False,
    }


def test_verified_floor_is_raw_linux_bytes_not_vm81_capacity() -> None:
    calibration = Lane5CacheCalibration.verified_floor()
    assert calibration.classification == VERIFIED_RAW_LINUX_SERIAL_BYTE_FLOOR
    assert calibration.capacity_unit == RAW_CAPACITY_UNIT
    assert calibration.max_serial_abi_bytes == VERIFIED_RAW_BYTE_FLOOR
    assert calibration.production_accepted is False
    report = calibration.to_dict()
    assert report["derived_5184_frame_slots"] == VERIFIED_RAW_BYTE_FLOOR // FRAME_BYTES
    assert report["derived_frame_remainder_bytes"] == VERIFIED_RAW_BYTE_FLOOR % FRAME_BYTES
    assert report["derived_values_are_hardware_capacity_authority"] is False
    assert report["vm81_services_present"] is False
    assert report["lane5_present"] is False
    assert report["pqc_present"] is False


def test_measured_calibration_uses_raw_byte_authority() -> None:
    calibration = Lane5CacheCalibration.from_evidence(measured_evidence(10_000))
    assert calibration.production_accepted is True
    assert calibration.capacity_unit == RAW_CAPACITY_UNIT
    assert calibration.max_serial_abi_bytes == 10_000
    assert calibration.derived_5184_frame_slots == 10_000 // FRAME_BYTES
    assert calibration.derived_frame_remainder_bytes == 10_000 % FRAME_BYTES


@pytest.mark.parametrize(
    "flag",
    [
        "hhs_present",
        "vm81_services_present",
        "lane5_present",
        "rna_services_present",
        "hash72_present",
        "hash216_present",
        "pqc_present",
    ],
)
def test_calibration_rejects_service_contamination(flag: str) -> None:
    evidence = measured_evidence(10_000)
    evidence[flag] = True
    with pytest.raises(
        Lane5SandboxCacheError,
        match="SERVICE_CONTAMINATION",
    ):
        Lane5CacheCalibration.from_evidence(evidence)


def test_queue_reorders_reusable_independent_chain_first() -> None:
    sandbox = Lane5InterceptorSandboxCache(
        calibration=Lane5CacheCalibration.from_evidence(
            measured_evidence(FRAME_BYTES * 8)
        )
    )
    first = sandbox.enqueue(
        traffic_class="runtime.abi",
        operation="fresh-A",
        payload={"dependency_root": "A"},
        read_only=False,
    )
    second = sandbox.enqueue(
        traffic_class="runtime.abi",
        operation="reuse-B",
        payload={"dependency_root": "B", "cache_reusable": True},
        read_only=False,
    )
    selected = sandbox.optimize_next()
    assert selected["ticket"] == second["ticket"]
    assert selected["lane5_reordered"] is True
    next_selected = sandbox.optimize_next()
    assert next_selected["ticket"] == first["ticket"]


def test_queue_preserves_fifo_inside_one_state_chain() -> None:
    sandbox = Lane5InterceptorSandboxCache(
        calibration=Lane5CacheCalibration.from_evidence(
            measured_evidence(FRAME_BYTES * 8)
        )
    )
    first = sandbox.enqueue(
        traffic_class="runtime.abi",
        operation="chain-1",
        payload={"dependency_root": "same"},
        read_only=False,
    )
    sandbox.enqueue(
        traffic_class="runtime.abi",
        operation="chain-2-reusable",
        payload={"dependency_root": "same", "cache_reusable": True},
        read_only=False,
    )
    selected = sandbox.optimize_next()
    assert selected["ticket"] == first["ticket"]
    assert selected["lane5_reordered"] is False


def test_cache_evicts_against_raw_byte_ceiling() -> None:
    calibration = Lane5CacheCalibration.from_evidence(
        measured_evidence(FRAME_BYTES * 2 + 17)
    )
    sandbox = Lane5InterceptorSandboxCache(calibration=calibration)
    candidate = {
        "candidate_only": True,
        "canonical_mutation_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
    }
    for index in range(3):
        sandbox.store_candidate(
            cache_key=f"k{index}",
            frame_le=bytes([index]) * FRAME_BYTES,
            candidate_result=candidate,
            source_ticket=f"t{index}",
        )
    status = sandbox.status()
    assert status["capacity_unit"] == RAW_CAPACITY_UNIT
    assert status["capacity_raw_serial_abi_bytes"] == FRAME_BYTES * 2 + 17
    assert status["cache_entries"] == 2
    assert status["resident_payload_bytes"] == FRAME_BYTES * 2
    assert sandbox.get_cached_candidate("k0") is None
    assert sandbox.get_cached_candidate("k1") is not None
    assert sandbox.get_cached_candidate("k2") is not None
