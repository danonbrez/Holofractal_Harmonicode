import pytest

from hhs_runtime.nfv.core import NFVError, NFVObject, TransitionPackage
from hhs_runtime.nfv.graph import DependencyEdge, DependencyGraph
from hhs_runtime.nfv.serialization import (
    HEADER,
    KIND_OBJECT,
    MAGIC,
    SERIALIZATION_VERSION,
    deserialize_graph,
    deserialize_object,
    deserialize_package,
    serialize_graph,
    serialize_object,
    serialize_package,
)
from hhs_runtime.nfv.store import NFVStore, replay_packages


def admit_all(_obj, _candidate):
    return True


def test_dependency_dag_has_stable_topological_order_and_readiness():
    graph = DependencyGraph()
    graph.add_node("parse", {"stage": 1})
    graph.add_node("verify", {"stage": 2})
    graph.add_node("commit", {"stage": 3})
    graph.add_edge(DependencyEdge("parse", "verify", "VALUE_DEPENDS_ON"))
    graph.add_edge(DependencyEdge("verify", "commit", "CLOSURE_DEPENDS_ON"))
    assert graph.topological_order() == ("parse", "verify", "commit")
    assert graph.ready_nodes(()) == ("parse",)
    assert graph.ready_nodes(("parse",)) == ("verify",)


def test_undeclared_dependency_cycle_rejected():
    graph = DependencyGraph()
    graph.add_node("a", {})
    graph.add_node("b", {})
    graph.add_edge(DependencyEdge("a", "b", "VALUE_DEPENDS_ON"))
    with pytest.raises(NFVError, match="NFV_UNDECLARED_DEPENDENCY_CYCLE"):
        graph.add_edge(DependencyEdge("b", "a", "VALUE_DEPENDS_ON"))


def test_bounded_recurrent_graph_requires_explicit_profile():
    profile = {
        "cycle_type": "FIXED_POINT",
        "convergence_predicate": "state_equal",
        "maximum_iterations": 8,
        "termination_state": "CLOSED",
        "resource_bound": 64,
    }
    graph = DependencyGraph(cycle_profile=profile)
    graph.add_node("a", {})
    graph.add_node("b", {})
    graph.add_edge(DependencyEdge("a", "b", "VALUE_DEPENDS_ON"))
    graph.add_edge(DependencyEdge("b", "a", "VALUE_DEPENDS_ON"))
    with pytest.raises(NFVError, match="NFV_RECURRENT_GRAPH_REQUIRES_ITERATIVE_EXECUTOR"):
        graph.topological_order()


def test_graph_serialization_round_trip_preserves_index():
    graph = DependencyGraph()
    graph.add_node("a", {"value": 1})
    graph.add_node("b", {"value": 2})
    graph.add_edge(DependencyEdge("a", "b", "VALUE_DEPENDS_ON"))
    restored = deserialize_graph(serialize_graph(graph))
    assert restored.to_dict() == graph.to_dict()
    assert restored.graph_index() == graph.graph_index()


def test_object_serialization_round_trip_is_exact():
    obj = NFVObject("STATE_VECTOR", {"value": 179971179971}, ("value>=0",), (), "VM81-A")
    encoded = serialize_object(obj)
    restored = deserialize_object(encoded)
    assert restored == obj
    assert serialize_object(restored) == encoded


def test_package_serialization_round_trip_preserves_identity():
    obj = NFVObject("STATE_VECTOR", {"value": 1}, (), (), "VM81-A")
    package = TransitionPackage.prepare(obj, "INVOKE", {"value": 2})
    restored = deserialize_package(serialize_package(package))
    assert restored == package


def test_serialization_rejects_trailing_data():
    obj = NFVObject("STATE_VECTOR", {"value": 1}, (), (), "VM81-A")
    with pytest.raises(NFVError, match="NFV_TRAILING_SERIALIZATION_DATA"):
        deserialize_object(serialize_object(obj) + b"x")


def test_serialization_rejects_noncanonical_json_and_duplicate_fields():
    payload = b'{"a":1, "a":2}'
    encoded = HEADER.pack(MAGIC, SERIALIZATION_VERSION, KIND_OBJECT, len(payload)) + payload
    with pytest.raises(NFVError, match="NFV_DUPLICATE_SERIALIZATION_FIELD"):
        deserialize_object(encoded)


def test_serialization_rejects_authoritative_float():
    obj = NFVObject("STATE_VECTOR", {"value": 1.5}, (), (), "VM81-A")
    with pytest.raises(NFVError, match="NFV_FLOAT_FORBIDDEN"):
        serialize_object(obj)


def test_store_rejects_stale_version_and_preserves_history():
    store = NFVStore()
    original = NFVObject("STATE_VECTOR", {"value": 1}, (), (), "VM81-A")
    ref0 = store.create(original)
    package = TransitionPackage.prepare(original, "INVOKE", {"value": 2})
    ref1, committed, _closed = store.commit(ref0, package, vm81_admit=admit_all)
    assert store.open(ref1) == committed
    with pytest.raises(NFVError, match="NFV_STALE_OBJECT_REFERENCE"):
        store.open(ref0)
    assert store.open(ref0, historical=True) == original
    assert store.history(ref0.lineage_id) == (ref0, ref1)


def test_copy_on_write_increments_generation_and_version():
    store = NFVStore()
    original = NFVObject("STATE_VECTOR", {"value": 1}, (), (), "VM81-A")
    ref0 = store.create(original)
    package = TransitionPackage.prepare(original, "INVOKE", {"value": 2})
    ref1, committed, _closed = store.commit(ref0, package, vm81_admit=admit_all, copy_on_write=True)
    assert ref1.version == ref0.version + 1
    assert ref1.generation == ref0.generation + 1
    assert committed.object_index == ref1.object_index


def test_store_bounds_fail_closed():
    store = NFVStore(max_lineages=1)
    store.create(NFVObject("STATE_VECTOR", {"value": 1}, (), (), "VM81-A"))
    with pytest.raises(NFVError, match="RESOURCE_BOUNDED"):
        store.create(NFVObject("STATE_VECTOR", {"value": 2}, (), (), "VM81-A"))


def test_replay_is_deterministic():
    initial_a = NFVObject("STATE_VECTOR", {"value": 1}, (), (), "VM81-A")
    p1a = TransitionPackage.prepare(initial_a, "INVOKE", {"value": 2})
    state2a, _ = p1a.commit(initial_a, vm81_admit=admit_all)
    p2a = TransitionPackage.prepare(state2a, "INVOKE", {"value": 3})

    initial_b = NFVObject("STATE_VECTOR", {"value": 1}, (), (), "VM81-A")
    p1b = TransitionPackage.prepare(initial_b, "INVOKE", {"value": 2})
    state2b, _ = p1b.commit(initial_b, vm81_admit=admit_all)
    p2b = TransitionPackage.prepare(state2b, "INVOKE", {"value": 3})

    replay_a = replay_packages(initial_a, (p1a, p2a), vm81_admit=admit_all)
    replay_b = replay_packages(initial_b, (p1b, p2b), vm81_admit=admit_all)
    assert replay_a.final_object == replay_b.final_object
    assert replay_a.receipt_chain == replay_b.receipt_chain
    assert replay_a.replay_hash72 == replay_b.replay_hash72
