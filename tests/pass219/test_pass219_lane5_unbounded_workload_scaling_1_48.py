from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import zlib

import pytest

from hhs_python.runtime.hhs_pass219_lane5_unbounded_workload_scaling_bridge import (
    FULL_MANIFOLD_MODULUS,
    Lane5RouteCandidate,
    Lane5WorkloadEnvelope,
    Pass219Lane5UnboundedWorkloadBridge,
)

ROOT = Path(__file__).resolve().parents[2]


def _address(domain: bytes, digest: bytes) -> int:
    return int.from_bytes(sha256(domain + digest).digest(), "big") % FULL_MANIFOLD_MODULUS


def _candidates(digest: bytes) -> list[Lane5RouteCandidate]:
    rows: list[Lane5RouteCandidate] = [
        Lane5RouteCandidate(
            route_witness_sha256=sha256(b"invalid-phase" + digest).digest(),
            reciprocal_witness_sha256=sha256(b"invalid-reciprocal" + digest).digest(),
            phase_slot=9,
            trinary_collapse=0,
            binary_collapse=0,
        )
    ]
    phases = (0, 18, 36, 54)
    trinary = (-1, 0, 1)
    for index in range(24):
        witness = b"\x00" * 32 if index == 17 else sha256(b"route" + index.to_bytes(4, "big") + digest).digest()
        rows.append(
            Lane5RouteCandidate(
                route_witness_sha256=witness,
                reciprocal_witness_sha256=sha256(b"reciprocal" + index.to_bytes(4, "big") + digest).digest(),
                phase_slot=phases[index % len(phases)],
                trinary_collapse=trinary[index % len(trinary)],
                binary_collapse=index % 2,
                evidence_count=5,
                contradiction_check_count=1,
            )
        )
    return rows


def _workloads() -> dict[str, bytes]:
    binary = bytes(range(256)) * 257
    return {
        "text": ("Lane 5 deterministic workload routing\n" * 4096).encode(),
        "json": json.dumps({"records": list(range(4096)), "mode": "exact"}, sort_keys=True).encode(),
        "source": (b"int main(void){return 0;}\n" * 8192),
        "binary": binary,
        "image_like": b"\x89PNG\r\n\x1a\n" + binary,
        "audio_like": b"RIFF" + (len(binary) + 36).to_bytes(4, "little") + b"WAVEfmt " + binary,
        "video_like": b"\x00\x00\x00\x18ftypmp42" + binary,
        "tensor_bytes": b"TENSOR\x00" + b"".join(value.to_bytes(4, "little", signed=True) for value in range(-4096, 4096)),
        "compressed": zlib.compress(binary, level=9),
        "empty": b"",
    }


def test_authority_exposes_full_manifold_constant_memory_workload_scaling() -> None:
    authority = Pass219Lane5UnboundedWorkloadBridge().authority()
    assert authority["version"] == 0x00010030
    assert authority["namespace_id"] == 0x00021930
    assert authority["full_manifold_address_bytes"] == 56
    assert authority["full_manifold_bigint_addressing"] is True
    assert authority["any_byte_serializable_workload"] is True
    assert authority["workload_class_agnostic"] is True
    assert authority["streaming_candidate_ingress"] is True
    assert authority["constant_memory_candidate_reduction"] is True
    assert authority["fixed_candidate_batch_required"] is False
    assert authority["intermediate_materialization_required"] is False
    assert authority["candidate_only"] is True
    assert authority["canonical_vm81_mutation_authority"] is False
    assert authority["canonical_hash216_authority"] is False
    assert authority["requires_signed_environmental_vm81_admission"] is True


def test_chunk_partition_does_not_change_workload_identity() -> None:
    payload = bytes(range(251)) * 10003
    direct = Lane5WorkloadEnvelope.from_bytes(payload, provenance="partition-test")
    chunks = [payload[index:index + 7919] for index in range(0, len(payload), 7919)]
    streamed = Lane5WorkloadEnvelope.from_chunks(chunks, provenance="partition-test")
    assert streamed == direct
    assert streamed.byte_count == len(payload)
    assert streamed.workload_sha256 == sha256(payload).digest()


def test_real_repository_files_use_same_streaming_identity_at_multiple_chunk_sizes() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "hhs_runtime" / "c" / "hhs_runtime_exact_abi.c",
        ROOT / "hhs_runtime" / "include" / "hhs_runtime_exact_abi.h",
    ]
    for path in paths:
        expected = Lane5WorkloadEnvelope.from_file(path, provenance=f"repo:{path.relative_to(ROOT).as_posix()}", chunk_bytes=4096)
        alternate = Lane5WorkloadEnvelope.from_file(path, provenance=f"repo:{path.relative_to(ROOT).as_posix()}", chunk_bytes=65537)
        assert alternate == expected
        assert expected.byte_count == path.stat().st_size


@pytest.mark.parametrize("workload_class,payload", list(_workloads().items()))
def test_every_byte_serializable_workload_class_uses_same_native_lane5_path(workload_class: str, payload: bytes) -> None:
    bridge = Pass219Lane5UnboundedWorkloadBridge()
    envelope = Lane5WorkloadEnvelope.from_chunks(
        (payload[index:index + 8191] for index in range(0, len(payload), 8191)),
        provenance=f"workload-class:{workload_class}",
    )
    previous = _address(b"previous", envelope.workload_sha256)
    current = _address(b"current", envelope.workload_sha256)
    goal = FULL_MANIFOLD_MODULUS - 1 if workload_class == "tensor_bytes" else _address(b"goal", envelope.workload_sha256)
    forbidden = sha256(b"forbidden" + envelope.workload_sha256).digest()
    candidates = _candidates(envelope.workload_sha256)

    result = bridge.optimize(
        workload=envelope,
        previous_address=previous,
        current_address=current,
        goal_address=goal,
        forbidden_boundary_sha256=forbidden,
        candidates=candidates,
    )
    replay = bridge.optimize(
        workload=envelope,
        previous_address=previous,
        current_address=current,
        goal_address=goal,
        forbidden_boundary_sha256=forbidden,
        candidates=candidates,
    )

    assert result == replay
    assert result["offered_candidates"] == 25
    assert result["admitted_candidates"] == 24
    assert result["native_rejected_candidates"] == 1
    assert result["selected_address"] == goal
    assert result["workload_byte_count"] == len(payload)
    assert result["workload_sha256"] == sha256(payload).hexdigest()
    assert result["route_witness_sha256"] == (b"\x00" * 32).hex()
    assert result["materialized_intermediate_states"] == 0
    assert result["candidate_only"] is True
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash216_authority"] is False
    assert result["requires_signed_environmental_vm81_admission"] is True


def test_out_of_manifold_coordinates_fail_before_native_call() -> None:
    bridge = Pass219Lane5UnboundedWorkloadBridge()
    envelope = Lane5WorkloadEnvelope.from_bytes(b"x", provenance="overflow-test")
    with pytest.raises(ValueError, match=r"0 <= value < 72\^72"):
        bridge.optimize(
            workload=envelope,
            previous_address=0,
            current_address=1,
            goal_address=FULL_MANIFOLD_MODULUS,
            forbidden_boundary_sha256=sha256(b"forbidden").digest(),
            candidates=_candidates(envelope.workload_sha256),
        )
