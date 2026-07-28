from __future__ import annotations

import pytest

from hhs_runtime.pass164.gcmsl import (
    BRIDGE_CARDINALITY,
    DENSE_SECOND_ORDER_CAPACITY,
    PHASE_DIMENSION,
    THREAD_DIMENSION,
    VM81_DIMENSION,
    GCMSError,
    GCMSLRuntime,
    InvariantAlgebra,
    ScaleGeometry,
    coordinate_bijection_proof,
    phase_to_vm_thread,
    rank_one_tensor,
    validate_canonical_geometry,
    vm_thread_to_phase,
)


def prepared_runtime(cluster_count=2):
    runtime = GCMSLRuntime()
    for index in range(cluster_count):
        cid = f"cluster-{index}"
        runtime.register_cluster(cid, tile_index=index)
        runtime.grant_capability(cid, "GCMSL_CANDIDATE_COMPUTE")
    return runtime


def submit_pair(runtime, *, reverse=False):
    incoming = runtime.vmrc.state_hash72
    specs = [
        dict(cluster_id="cluster-0", vm81_position=1, thread=2, phase=3, trit=1),
        dict(cluster_id="cluster-1", vm81_position=4, thread=5, phase=6, trit=1),
    ]
    if reverse:
        specs.reverse()
    ids = []
    for spec in specs:
        result = runtime.submit_operation(**spec, incoming_hash72=incoming)
        ids.append(result["operation"]["operation_id"])
    return ids


def test_canonical_dimensions_and_equation():
    assert validate_canonical_geometry()
    assert PHASE_DIMENSION**2 == THREAD_DIMENSION * VM81_DIMENSION == BRIDGE_CARDINALITY
    assert not validate_canonical_geometry(71, 64, 81)


def test_rank_one_tensor():
    tensor = rank_one_tensor()
    assert tensor["determinant"] == 0
    assert tensor["rank"] == 1


def test_full_coordinate_bijection():
    proof = coordinate_bijection_proof()
    assert proof["forward_count"] == BRIDGE_CARDINALITY
    assert proof["inverse_count"] == BRIDGE_CARDINALITY
    assert proof["collisions"] == 0
    assert vm_thread_to_phase(80, 63) == (71, 71)
    assert phase_to_vm_thread(71, 71) == (80, 63)


def test_coordinate_bounds():
    with pytest.raises(GCMSError, match="GCMSL_VM81_POSITION_OUT_OF_RANGE"):
        vm_thread_to_phase(81, 0)
    with pytest.raises(GCMSError, match="GCMSL_THREAD_OUT_OF_RANGE"):
        vm_thread_to_phase(0, 64)
    with pytest.raises(GCMSError, match="GCMSL_PHASE_COORDINATE_OUT_OF_RANGE"):
        phase_to_vm_thread(72, 0)


def test_homogeneous_scale_two_and_recursive_two():
    geometry = ScaleGeometry(scale=2, recursive_level=2)
    assert geometry.validate()
    assert geometry.homogeneous["P_c_squared"] == geometry.homogeneous["p_c_q_c"] == 20736
    assert geometry.homogeneous["dense_capacity"] == DENSE_SECOND_ORDER_CAPACITY * 4
    assert geometry.recursive["P_r_squared"] == geometry.recursive["p_r_q_r"]


def test_authority_remains_singleton_under_scaling():
    runtime = prepared_runtime(4)
    status = runtime.status()
    assert status["clusters"] == 4
    assert status["kernel_authorities"] == 1
    assert status["permanent_indexes"] == 1
    assert status["worker_mutation_authority"] is False


def test_clusters_begin_capability_zero():
    runtime = GCMSLRuntime()
    registered = runtime.register_cluster("cluster-0")
    assert registered["cluster"]["capability_scope"] == ""
    with pytest.raises(GCMSError, match="GCMSL_CAPABILITY_ZERO"):
        runtime.submit_operation(cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1)


def test_backend_equivalence_with_reverse_completion():
    runtime = prepared_runtime()
    ids = submit_pair(runtime)
    operations = [runtime._operations[item] for item in ids]
    comparison = runtime.compare_backends(operations)
    assert comparison["equivalent"]
    assert comparison["cpu_physical_order"] == ids
    assert comparison["gpu_physical_order"] == list(reversed(ids))


def test_completion_order_independent_reduction():
    first = prepared_runtime()
    first_ids = submit_pair(first)
    first_result = first.reduce(first_ids)

    second = prepared_runtime()
    second_ids = submit_pair(second, reverse=True)
    second_result = second.reduce(second_ids)

    assert first_result["batch"]["stable_order"] == second_result["batch"]["stable_order"]
    assert first_result["batch"]["backend_equivalence_root"] == second_result["batch"]["backend_equivalence_root"]
    assert first_result["batch"]["invariant"]["closed"]


def test_reduce_and_commit_through_pass163():
    runtime = prepared_runtime()
    ids = submit_pair(runtime)
    reduced = runtime.reduce(ids)
    before = runtime.vmrc.state_hash72
    committed = runtime.commit(reduced["batch"]["batch_id"])
    assert committed["classification"] == "HHS_PASS_164_CLUSTER_COMMIT_ADMITTED"
    assert committed["receipt"]["incoming_hash72"] == before
    assert committed["receipt"]["outgoing_hash72"] == runtime.vmrc.state_hash72
    assert len(committed["pass163_receipts"]) == 2


def test_duplicate_candidate_identity_rejected():
    runtime = prepared_runtime(1)
    incoming = runtime.vmrc.state_hash72
    first = runtime.submit_operation(cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1, incoming_hash72=incoming)
    with pytest.raises(GCMSError, match="GCMSL_DUPLICATE_CANDIDATE_IDENTITY"):
        runtime.submit_operation(cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1, incoming_hash72=incoming)
    with pytest.raises(GCMSError, match="GCMSL_DUPLICATE_CANDIDATE_IDENTITY"):
        runtime.reduce([first["operation"]["operation_id"], first["operation"]["operation_id"]])


def test_write_collision_rejected():
    runtime = prepared_runtime()
    incoming = runtime.vmrc.state_hash72
    a = runtime.submit_operation(cluster_id="cluster-0", vm81_position=2, thread=3, phase=4, trit=1, incoming_hash72=incoming)
    b = runtime.submit_operation(cluster_id="cluster-1", vm81_position=2, thread=3, phase=4, trit=-1, incoming_hash72=incoming)
    with pytest.raises(GCMSError, match="GCMSL_WRITE_COLLISION"):
        runtime.reduce([a["operation"]["operation_id"], b["operation"]["operation_id"]])


def test_stale_root_rejected():
    runtime = prepared_runtime(1)
    with pytest.raises(GCMSError, match="GCMSL_STALE_INCOMING_HASH72"):
        runtime.submit_operation(cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1, incoming_hash72="0" * 72)


def test_noncommutative_requires_explicit_order():
    runtime = prepared_runtime(1)
    operation = runtime.submit_operation(
        cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1,
        operation_class="GCMSL_NONCOMMUTATIVE",
    )
    with pytest.raises(GCMSError, match="GCMSL_NONCOMMUTATIVE_ORDER_REQUIRED"):
        runtime.reduce([operation["operation"]["operation_id"]], required_clusters=["cluster-0"])


def test_explicit_noncommutative_order_is_stable():
    runtime = prepared_runtime(1)
    incoming = runtime.vmrc.state_hash72
    a = runtime.submit_operation(
        cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1,
        operation_class="GCMSL_NONCOMMUTATIVE", noncommutative_order=2, incoming_hash72=incoming,
    )
    b = runtime.submit_operation(
        cluster_id="cluster-0", vm81_position=1, thread=0, phase=0, trit=1,
        operation_class="GCMSL_NONCOMMUTATIVE", noncommutative_order=1, incoming_hash72=incoming,
    )
    result = runtime.reduce([a["operation"]["operation_id"], b["operation"]["operation_id"]], required_clusters=["cluster-0"])
    assert result["batch"]["stable_order"] == [b["operation"]["operation_id"], a["operation"]["operation_id"]]


def test_incomplete_reciprocal_pair_rejected():
    runtime = prepared_runtime(1)
    operation = runtime.submit_operation(
        cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1,
        reciprocal_pair_id="pair-a",
    )
    with pytest.raises(GCMSError, match="GCMSL_INCOMPLETE_RECIPROCAL_PAIR"):
        runtime.reduce([operation["operation"]["operation_id"]], required_clusters=["cluster-0"])


def test_complete_reciprocal_pair_admitted():
    runtime = prepared_runtime(1)
    incoming = runtime.vmrc.state_hash72
    a = runtime.submit_operation(
        cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1,
        reciprocal_pair_id="pair-a", incoming_hash72=incoming,
    )
    b = runtime.submit_operation(
        cluster_id="cluster-0", vm81_position=1, thread=0, phase=71, trit=-1,
        reciprocal_pair_id="pair-a", incoming_hash72=incoming,
    )
    result = runtime.reduce([a["operation"]["operation_id"], b["operation"]["operation_id"]], required_clusters=["cluster-0"])
    assert result["batch"]["invariant"]["omega164"] == 0


def test_incomplete_required_participation_rejected():
    runtime = prepared_runtime(2)
    operation = runtime.submit_operation(cluster_id="cluster-0", vm81_position=0, thread=0, phase=0, trit=1)
    with pytest.raises(GCMSError, match="GCMSL_INCOMPLETE_REQUIRED_CLUSTER_PARTICIPATION"):
        runtime.reduce([operation["operation"]["operation_id"]])


def test_sparse_edge_residency_and_cluster_identity():
    runtime = prepared_runtime(2)
    first = runtime.register_edge(
        level=1, source_cluster="cluster-0", destination_cluster="cluster-1",
        domain="INTERCONNECT_ROUTE", source="0", destination="1",
        exact_weight="3/2", polarity=1,
    )
    second = runtime.register_edge(
        level=2, source_cluster="cluster-0", destination_cluster="cluster-1",
        domain="INTERCONNECT_ROUTE", source="0", destination="1",
        exact_weight="3/2", polarity=1,
    )
    assert first["edge"]["edge_id"] != second["edge"]["edge_id"]
    status = runtime.status()
    assert status["active_edges"] == 2
    assert status["active_edges"] < DENSE_SECOND_ORDER_CAPACITY


def test_pass163_base64_transport_round_trip():
    runtime = prepared_runtime(1)
    encoded = runtime.transport_envelope({"frontier": [1, 2, 3]}, cluster_id="cluster-0")
    decoded = runtime.vmrc.decode_envelope(encoded)
    assert decoded["payload"] == {"frontier": [1, 2, 3]}


def test_invariant_algebra_prevents_scalar_cancellation():
    invariant = InvariantAlgebra(geometry=1, thread=-1)
    assert invariant.residual_norm == 2
    assert invariant.omega == -1
    assert not invariant.closed


def test_replay_and_journal_tamper_detection():
    runtime = prepared_runtime()
    ids = submit_pair(runtime)
    batch = runtime.reduce(ids)["batch"]["batch_id"]
    runtime.commit(batch)
    assert runtime.replay()["deterministic_replay"]
    runtime._journal[1]["cluster"] = {"forged": True}
    with pytest.raises(GCMSError, match="GCMSL_REPLAY_MISMATCH"):
        runtime.replay()


def test_measured_benchmark_separates_capacity_and_residency():
    runtime = prepared_runtime(1)
    report = runtime.benchmark(scale=2, active_edges=8)
    assert report["dense_address_capacity"] == DENSE_SECOND_ORDER_CAPACITY * 4
    assert report["active_edge_count"] == 8
    assert report["sparse_address_compression_factor"] == (DENSE_SECOND_ORDER_CAPACITY * 4) / 8
    assert report["snapshot_base64_symbols"] == 864
    assert report["physical_single_cycle_claimed"] is False


def test_api_surface_is_registered():
    from hhs_backend.api.pass164_gcmsl_routes import router
    paths = {route.path for route in router.routes}
    assert "/api/runtime/gcmsl/status" in paths
    assert "/api/runtime/gcmsl/coordinate-bijection" in paths
    assert "/api/runtime/gcmsl/clusters" in paths
    assert "/api/runtime/gcmsl/reduce" in paths
    assert "/api/runtime/gcmsl/commit" in paths
    assert "/api/runtime/gcmsl/benchmark" in paths
