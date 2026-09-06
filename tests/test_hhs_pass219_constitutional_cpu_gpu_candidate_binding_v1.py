from dataclasses import replace

import pytest

from hhs_runtime.hhs_pass219_constitutional_cpu_gpu_candidate_binding_v1 import (
    ComputeCandidateEnvelope,
    bind_driver_status,
    evaluate_compute_candidate,
)
from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import EthicsState
from hhs_runtime.hhs_pass219_constitutional_modality_registry_v1 import BASE_INVARIANTS


def _candidate(**changes):
    base = ComputeCandidateEnvelope(
        candidate_id="candidate-1",
        cpu_exact=b"exact-vm81-candidate",
        gpu_candidate=b"exact-vm81-candidate",
        upstream_trace_hash72="h72:upstream",
        provenance=("pass207", "constitutional-compute-binding"),
    )
    return replace(base, **changes)


def test_exact_cpu_gpu_candidate_is_eligible_but_never_authoritative():
    result = evaluate_compute_candidate(_candidate())
    assert result.state is EthicsState.PASS
    assert result.exact_cpu_gpu_equal is True
    assert result.vm81_admission_eligible is True
    assert result.mutation_authority is False
    assert result.hash72_commit_authority is False
    assert result.hash216_commit_authority is False


@pytest.mark.parametrize(
    ("changes", "predicate"),
    [
        ({"gpu_candidate": b"different"}, "CPU_GPU_EXACT_EQUALITY"),
        ({"gpu_verified_against_cpu": False}, "GPU_CPU_VERIFICATION_REQUIRED"),
        ({"deterministic_integer_only": False}, "CANONICAL_FLOAT_OR_NONDETERMINISM_REJECTED"),
        ({"gpu_mutation_authority": True}, "GPU_MUTATION_AUTHORITY_REJECTED"),
        ({"gpu_hash72_authority": True}, "GPU_HASH72_AUTHORITY_REJECTED"),
        ({"gpu_hash216_authority": True}, "GPU_HASH216_AUTHORITY_REJECTED"),
        ({"ranking_confers_authority": True}, "RANKING_AUTHORITY_REJECTED"),
        ({"performance_confers_authority": True}, "PERFORMANCE_AUTHORITY_REJECTED"),
    ],
)
def test_compute_candidate_fail_closed(changes, predicate):
    result = evaluate_compute_candidate(_candidate(**changes))
    assert result.state is EthicsState.FAIL
    assert result.vm81_admission_eligible is False
    assert predicate in result.failed_predicates


def test_invariant_loss_rejects_candidate():
    result = evaluate_compute_candidate(
        _candidate(preserved_invariants=BASE_INVARIANTS[:-1])
    )
    assert result.state is EthicsState.FAIL
    assert "COMPUTE_INVARIANT_LOSS" in result.failed_predicates


def test_driver_status_adapter_preserves_candidate_only_boundary():
    result = bind_driver_status(
        candidate_id="driver-1",
        cpu_exact=b"same",
        gpu_candidate=b"same",
        upstream_trace_hash72="h72:driver",
        provenance=("pass207-driver",),
        verified_against_cpu=True,
        deterministic_integer_only=True,
    )
    assert result.state is EthicsState.PASS
    assert result.vm81_admission_eligible is True
    assert result.mutation_authority is False


def test_missing_provenance_or_trace_fails_at_schema_boundary():
    with pytest.raises(ValueError):
        _candidate(provenance=())
    with pytest.raises(ValueError):
        _candidate(upstream_trace_hash72="")
