import base64
from fractions import Fraction
import json

import pytest

from hhs_runtime.pass163.vmrc import (
    BASE64_SYMBOLS,
    COORDINATES,
    SNAPSHOT_BYTES,
    VMRCError,
    VMRCRuntime,
    VMRCSnapshot,
    SparseSnapshot,
    canonical_bytes,
)


def test_geometry_and_transpose():
    snap = VMRCSnapshot()
    assert COORDINATES == 5184
    assert SNAPSHOT_BYTES == 648
    assert BASE64_SYMBOLS == 864
    assert len(snap.thread_projection(0)) == 81
    assert len(snap.position_burst(0)) == 64
    assert all(
        snap.thread_projection(thread)[position]
        == snap.position_burst(position)[thread]
        for thread in range(64)
        for position in range(81)
    )


def test_exact_full_snapshot_base64_roundtrip():
    raw = bytes((index * 37 + 11) % 256 for index in range(SNAPSHOT_BYTES))
    snap = VMRCSnapshot(raw)
    encoded = snap.base64()
    assert len(encoded) == 864
    assert "=" not in encoded
    assert VMRCSnapshot.from_base64(encoded).to_bytes() == raw
    per_word = "".join(
        base64.b64encode(raw[index:index + 8]).decode()
        for index in range(0, len(raw), 8)
    )
    assert len(per_word) == 972
    assert per_word != encoded


def test_base64_negative_paths():
    encoded = VMRCSnapshot().base64()
    with pytest.raises(VMRCError, match="VMRC_MALFORMED_BASE64"):
        VMRCSnapshot.from_base64(encoded + "=")
    with pytest.raises(VMRCError, match="VMRC_MALFORMED_BASE64"):
        VMRCSnapshot.from_base64("!" + encoded[1:])
    with pytest.raises(VMRCError, match="VMRC_INCORRECT_EXPANDED_LENGTH"):
        VMRCSnapshot(b"short")


def test_sparse_zero_and_one_background_roundtrip():
    zero = VMRCSnapshot()
    sparse_zero = zero.compress()
    assert sparse_zero.background == 0
    assert sparse_zero.exceptions == ()
    assert sparse_zero.expand().to_bytes() == zero.to_bytes()
    one = VMRCSnapshot(bytes([0xFF] * SNAPSHOT_BYTES))
    sparse_one = one.compress()
    assert sparse_one.background == 1
    assert sparse_one.exceptions == ()
    assert sparse_one.expand().to_bytes() == one.to_bytes()
    with pytest.raises(VMRCError, match="VMRC_NONCANONICAL_SPARSE_COORDINATES"):
        SparseSnapshot(0, (3, 3))
    with pytest.raises(VMRCError, match="VMRC_SPARSE_COORDINATE_OUT_OF_RANGE"):
        SparseSnapshot(0, (5184,))


def test_runtime_singleton_authority_status():
    runtime = VMRCRuntime()
    status = runtime.status()
    assert status["kernel_authorities"] == 1
    assert status["permanent_indexes"] == 1
    assert status["peer_mutation_authority"] is False
    assert status["threads"] == 64
    assert status["vm81_positions"] == 81


def test_parameter_identity_deduplication_and_float_rejection():
    runtime = VMRCRuntime()
    args = dict(
        type="RATIONAL",
        value={"n": 3, "d": 7},
        domain="TEST",
        phase=4,
        operator="SCALE",
        constraints=("NONZERO",),
        provenance="unit-test",
    )
    first = runtime.register_parameter(**args)
    second = runtime.register_parameter(**args)
    assert first["parameter"]["identity"] == second["parameter"]["identity"]
    assert second["receipt"]["reused"] is True
    with pytest.raises(VMRCError, match="VMRC_CANONICAL_FLOAT_REJECTED"):
        runtime.register_parameter(
            type="FLOAT",
            value=0.5,
            domain="TEST",
            phase=0,
            operator="BAD",
            constraints=(),
            provenance="unit-test",
        )


def test_candidate_commit_hash216_index_and_replay():
    runtime = VMRCRuntime()
    candidate = runtime.submit_candidate(
        thread=7,
        writes={0: 1, 8: 1, 9: 0, 80: -1},
        operation="VMRC_COMMIT",
        expected_input_hash72=runtime.state_hash72,
    )
    result = runtime.execute(candidate)
    assert runtime.snapshot().get(0, 7) == 1
    assert runtime.snapshot().get(8, 7) == 1
    assert runtime.snapshot().get(80, 7) == 0
    validated = result["validation"]["validated"]
    assert len(validated["operation_positions_hash216"]) == 216
    assert len(validated["operation_hash216"]) == 64
    assert len(runtime.index_records()) == 1
    assert runtime.replay()["deterministic_replay"] is True


def test_stale_root_expected_root_and_validation_gate():
    runtime = VMRCRuntime()
    stale = runtime.submit_candidate(
        thread=0,
        writes={1: 1},
        operation="VMRC_COMMIT",
        expected_input_hash72=runtime.state_hash72,
    )
    other = runtime.submit_candidate(
        thread=1,
        writes={1: 1},
        operation="VMRC_COMMIT",
        expected_input_hash72=runtime.state_hash72,
    )
    runtime.execute(other)
    with pytest.raises(VMRCError, match="VMRC_STALE_EPOCH|VMRC_STALE_ROOT"):
        runtime.validate(stale)
    with pytest.raises(VMRCError, match="VMRC_VALIDATION_REQUIRED"):
        runtime.commit("missing")
    bad = runtime.submit_candidate(
        thread=0,
        writes={2: 1},
        operation="VMRC_COMMIT",
        expected_input_hash72=runtime.state_hash72,
        expected_output_hash72=runtime.state_hash72,
    )
    with pytest.raises(VMRCError, match="VMRC_EXPECTED_OUTPUT_ROOT_MISMATCH"):
        runtime.validate(bad)


def test_bounds_foreign_lane_and_capability_zero():
    runtime = VMRCRuntime()
    with pytest.raises(VMRCError, match="VMRC_RESOURCE_BOUND"):
        runtime.submit_candidate(
            thread=64,
            writes={},
            operation="VMRC_COMMIT",
            expected_input_hash72=runtime.state_hash72,
        )
    with pytest.raises(VMRCError, match="VMRC_RESOURCE_BOUND"):
        runtime.submit_candidate(
            thread=0,
            writes={81: 1},
            operation="VMRC_COMMIT",
            expected_input_hash72=runtime.state_hash72,
        )
    with pytest.raises(VMRCError, match="VMRC_FOREIGN_LANE_MUTATION_DENIED"):
        runtime.submit_coordinate_candidate(
            thread=0,
            writes={(1, 1): 1},
            operation="VMRC_COMMIT",
            expected_input_hash72=runtime.state_hash72,
        )
    with pytest.raises(VMRCError, match="VMRC_CAPABILITY_ZERO"):
        runtime.submit_candidate(
            thread=0,
            writes={},
            operation="VMRC_COMMIT",
            expected_input_hash72=runtime.state_hash72,
            capability_scope="",
        )


def test_bounded_phase_gear_propagation():
    runtime = VMRCRuntime()
    runtime.register_gear((1, 3), (2, 3), direction=1)
    runtime.register_gear((2, 3), (3, 3), direction=-1)
    candidate = runtime.submit_candidate(
        thread=3,
        writes={1: 1},
        operation="VMRC_GEAR_PROPAGATE",
        expected_input_hash72=runtime.state_hash72,
    )
    runtime.execute(candidate)
    snap = runtime.snapshot()
    assert snap.get(1, 3) == 1
    assert snap.get(2, 3) == 1
    assert snap.get(3, 3) == 0


def test_path_dependent_exact_memristor():
    runtime = VMRCRuntime()
    first = runtime.propose_memristor(
        "a",
        "b",
        conductance=(1, 3),
        polarity=1,
    )
    runtime.admit_memristor(first)
    second = runtime.propose_memristor(
        "a",
        "b",
        conductance=(1, 6),
        polarity=-1,
        prior_identity=first.identity,
    )
    assert Fraction(second.conductance) == Fraction(1, 2)
    assert second.admitted_history == (first.identity,)
    assert second.reuse_count == 1
    with pytest.raises(VMRCError, match="VMRC_CANONICAL_FLOAT_REJECTED"):
        runtime.propose_memristor("a", "b", conductance=0.5, polarity=1)


def test_exact_continuation_key_and_invalidation():
    runtime = VMRCRuntime()
    candidate = runtime.submit_candidate(
        thread=2,
        writes={4: 1},
        operation="VMRC_COMMIT",
        expected_input_hash72=runtime.state_hash72,
    )
    result = runtime.execute(candidate)
    key = result["commit"]["continuation_key"]
    assert runtime.cache_lookup(key)["classification"] == "VMRC_CACHE_REUSE"
    partial = dict(key)
    partial["capability_scope"] = "OTHER"
    with pytest.raises(VMRCError, match="VMRC_CACHE_MISS"):
        runtime.cache_lookup(partial)
    runtime.cache_invalidate(key)
    with pytest.raises(VMRCError, match="VMRC_CACHE_MISS"):
        runtime.cache_lookup(key)


def _metadata(runtime):
    status = runtime.status()
    return dict(
        operation_class="VMRC_VALIDATE",
        source_architecture="x86_64",
        target_architecture="VM81",
        runtime_epoch=runtime.epoch,
        incoming_hash72=runtime.state_hash72,
        thread_mask="1",
        port_mask="1",
        read_set_root="0" * 64,
        write_set_root="1" * 64,
        dependency_root="2" * 64,
        parameter_root=status["parameter_root"],
        phase_gear_graph_root=status["phase_gear_root"],
        expected_expanded_state_root=runtime.state_hash72,
        receipt_nonce="n-1",
    )


def test_canonical_abi_envelope_and_tamper_rejection():
    runtime = VMRCRuntime()
    encoded = runtime.base64_envelope(
        {"hello": "vm81"},
        **_metadata(runtime),
    )
    decoded = runtime.decode_envelope(encoded)
    assert decoded["payload"] == {"hello": "vm81"}
    raw = json.loads(base64.b64decode(encoded))
    raw["payload_length"] += 1
    tampered = base64.b64encode(canonical_bytes(raw)).decode()
    with pytest.raises(VMRCError, match="VMRC_HASH_MISMATCH"):
        runtime.decode_envelope(tampered)


def test_replay_detects_journal_tampering():
    runtime = VMRCRuntime()
    candidate = runtime.submit_candidate(
        thread=1,
        writes={1: 1},
        operation="VMRC_COMMIT",
        expected_input_hash72=runtime.state_hash72,
    )
    runtime.execute(candidate)
    runtime._journal[-1]["output_hash72"] = runtime._journal[0]["state_hash72"]
    with pytest.raises(VMRCError, match="VMRC_REPLAY_MISMATCH"):
        runtime.replay()
