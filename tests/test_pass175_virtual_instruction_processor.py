from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass175 import (
    ControlWord,
    HydratedMicrocodeStore,
    InstructionAddress,
    InstructionRequest,
    Pass175Error,
    Pass175Runtime,
    ReciprocalLane,
    SCALAR_CIRCUIT_HI_BYTES,
    SCALAR_CIRCUIT_HI_TOKENS,
    SCALAR_CIRCUIT_LO_BYTES,
    SCALAR_CIRCUIT_LO_TOKENS,
)


class FakeAuthority:
    def __init__(self) -> None:
        self.epoch = 0
        self.state_hash72 = hash72_digest({"schema": "P175_TEST_GENESIS"}, b"")
        self.calls: list[dict[str, Any]] = []

    def status(self) -> dict[str, Any]:
        return {
            "classification": "P175_TEST_AUTHORITY",
            "vmrc": {"epoch": self.epoch, "state_hash72": self.state_hash72, "kernel_authorities": 1},
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(dict(kwargs))
        predecessor = self.state_hash72
        self.epoch += 1
        self.state_hash72 = hash72_digest(
            {"schema": "P175_TEST_COMMIT", "epoch": self.epoch, "kwargs": kwargs},
            predecessor.encode("ascii"),
        )
        return {
            "classification": "P175_TEST_VM81_COMMIT",
            "receipt": {
                "sequence": self.epoch,
                "input_hash72": predecessor,
                "output_hash72": self.state_hash72,
            },
        }

    def replay(self) -> dict[str, Any]:
        return {
            "classification": "P175_TEST_AUTHORITY_REPLAY",
            "epoch": self.epoch,
            "state_hash72": self.state_hash72,
            "deterministic_replay": True,
        }


def make_runtime(path: Path | None = None) -> tuple[Pass175Runtime, FakeAuthority]:
    authority = FakeAuthority()
    store = HydratedMicrocodeStore(path)
    return Pass175Runtime(authority=authority, microcode_store=store), authority


def test_all_permanent_addresses_round_trip() -> None:
    seen = set()
    for cell in range(81):
        for operation in range(64):
            address = InstructionAddress.from_cell_operation(cell, operation)
            decoded = InstructionAddress.from_state(address.state)
            assert decoded == address
            seen.add(address.state)
    assert len(seen) == 5184
    assert InstructionAddress.from_state(5183).state == 5183
    assert (5183 + 1) % 5184 == 0


def test_all_g243_controls_round_trip() -> None:
    identities = set()
    for encoded in range(243):
        word = ControlWord.from_int(encoded)
        assert ControlWord.from_trits(word.trits).encoded == encoded
        identities.add(word.trits)
    assert len(identities) == 243


def test_all_projected_addresses_round_trip() -> None:
    last = -1
    for state in range(5184):
        address = InstructionAddress.from_state(state)
        for control in range(243):
            projected = address.project(control)
            decoded, decoded_control = InstructionAddress.unproject(projected)
            assert decoded.state == state
            assert decoded_control == control
            last = projected
    assert last == 1_259_711


def test_permanent_fabric_and_scalar_identity() -> None:
    runtime, _ = make_runtime()
    status = runtime.status()
    assert status["permanent_instruction_count"] == 5184
    assert status["permanent_identity_count"] == 5184
    assert status["phase_distribution"] == {"0": 14, "18": 16, "36": 18, "54": 16}
    assert status["closure_operations"] == 32
    assert tuple(status["scalar_circuits"]["lo_tokens"]) == SCALAR_CIRCUIT_LO_TOKENS
    assert tuple(status["scalar_circuits"]["hi_tokens"]) == SCALAR_CIRCUIT_HI_TOKENS
    assert SCALAR_CIRCUIT_LO_BYTES == bytes((0, 1, 0, 1, 10, 11, 1, 0))
    assert SCALAR_CIRCUIT_HI_BYTES == bytes((1, 0, 11, 10, 1, 0, 0, 111))
    assert runtime.instruction(0)["ordered_expression"] == "x*x"
    assert runtime.instruction(63)["ordered_expression"] == "wz*wz"


def test_hydrated_instruction_preserves_exact_bytes_and_hash216() -> None:
    runtime, _ = make_runtime()
    record = runtime.hydrate_x86(b"\x90")
    assert record.exact_bytes == b"\x90"
    assert record.exact_bytes_sha256 == sha256(b"\x90").hexdigest()
    assert len(record.hash216.combined) == 216
    assert len(record.hash216.character_indexes_sha256) == 216
    record.hash216.verify()
    assert runtime.hydrate_x86(b"\x90").key_sha256 == record.key_sha256


def test_distinct_encodings_retain_distinct_identity() -> None:
    runtime, _ = make_runtime()
    left = runtime.hydrate_x86(b"\xB8\x01\x00\x00\x00")
    right = runtime.hydrate_x86(b"\x48\xB8\x01\x00\x00\x00\x00\x00\x00\x00")
    assert left.mnemonic == right.mnemonic == "MOV"
    assert left.key_sha256 != right.key_sha256
    assert left.exact_bytes_sha256 != right.exact_bytes_sha256


def test_persistent_store_warm_restart_root(tmp_path: Path) -> None:
    path = tmp_path / "microcode.jsonl"
    runtime, _ = make_runtime(path)
    runtime.hydrate_x86(b"\x90")
    runtime.hydrate_x86(b"\x0F\xA2")
    root = runtime.microcode_store.root()
    restarted, _ = make_runtime(path)
    assert restarted.microcode_store.root() == root
    assert len(restarted.microcode_store.records()) == 2


def test_unsupported_and_privileged_encodings_fail_closed() -> None:
    runtime, authority = make_runtime()
    with pytest.raises(Pass175Error, match="HHS_P175_UNSUPPORTED_EXACT_ENCODING"):
        runtime.execute_batch([InstructionRequest(exact_bytes=b"\x62")])
    with pytest.raises(Pass175Error, match="HHS_P175_PRIVILEGED_INSTRUCTION_TRAPPED"):
        runtime.execute_batch([InstructionRequest(exact_bytes=b"\xF4")])
    assert authority.calls == []


def test_parallel_candidates_have_singular_deterministic_commit() -> None:
    requests = [
        InstructionRequest(exact_bytes=b"\x90", sequence=1, thread_id=1, explicit_delta=((1, 1),)),
        InstructionRequest(exact_bytes=b"\x0F\xA2", sequence=0, thread_id=2, explicit_delta=((2, -1),)),
        InstructionRequest(exact_bytes=b"\x31\xC0", sequence=2, thread_id=3, explicit_delta=((3, 1),)),
    ]
    serial, serial_authority = make_runtime()
    parallel, parallel_authority = make_runtime()
    left = serial.execute_batch(requests, max_workers=1)
    right = parallel.execute_batch(requests, max_workers=4)
    assert left["wave_count"] == right["wave_count"] == 1
    assert left["waves"][0]["candidate_root_sha256"] == right["waves"][0]["candidate_root_sha256"]
    assert serial_authority.state_hash72 == parallel_authority.state_hash72
    assert len(serial_authority.calls) == len(parallel_authority.calls) == 1
    assert left["parallel_state_authority"] is False
    assert left["singleton_vm81_commit_authority"] is True


def test_conflicts_are_partitioned_into_ordered_waves() -> None:
    runtime, authority = make_runtime()
    result = runtime.execute_batch([
        InstructionRequest(exact_bytes=b"\x90", sequence=0, explicit_delta=((7, 1),)),
        InstructionRequest(exact_bytes=b"\x90", sequence=1, explicit_delta=((7, -1),)),
    ])
    assert result["wave_count"] == 2
    assert len(authority.calls) == 2
    assert result["waves"][1]["predecessor_state_root"] == result["waves"][0]["authority_result"]["receipt"]["output_hash72"]


def test_cache_hit_never_bypasses_vm81_authority() -> None:
    runtime, authority = make_runtime()
    request = InstructionRequest(exact_bytes=b"\x90", explicit_delta=((4, 1),))
    runtime.execute_batch([request])
    hydrated_count = len(runtime.microcode_store.records())
    runtime.execute_batch([request])
    assert len(runtime.microcode_store.records()) == hydrated_count == 1
    assert len(authority.calls) == 2


def test_guarded_reciprocal_projection() -> None:
    runtime, _ = make_runtime()
    root_a, root_b = sha256(b"a").hexdigest(), sha256(b"b").hexdigest()
    a = ReciprocalLane("xy", 0, 72 * 72, 1, root_a, root_b)
    b = ReciprocalLane("yx", 36, 72 * 72, 1, root_b, root_a)
    result = runtime.project_ab(a, b)
    assert result["result_numerator"] == 72 ** 4
    assert result["result_phase"] == 0
    assert result["witness_lanes_retained"] is True
    with pytest.raises(Pass175Error, match="HHS_P175_RECIPROCAL_PHASE_MISMATCH"):
        runtime.project_ab(a, ReciprocalLane("yx", 37, 72 * 72, 1, root_b, root_a))


def test_bootstrap_hydration_is_sealed_through_vm81() -> None:
    runtime, authority = make_runtime()
    result = runtime.cold_hydrate_bootstrap()
    assert result["records"] == 8
    assert result["sealed_through_vm81"] is True
    assert len(authority.calls) == 1
    assert len(runtime.microcode_store.records()) == 8


def test_governed_keyboard_and_port_io() -> None:
    runtime, authority = make_runtime()
    ingress = runtime.ingress_keyboard(b"A")
    assert ingress["payload_sha256"] == sha256(b"A").hexdigest()
    result = runtime.execute_batch([InstructionRequest(exact_bytes=b"\xE4\x60")])
    event = result["waves"][0]["device_events"][0]
    assert event["device_operation"] == "IN"
    assert event["port"] == 0x60
    assert event["value"] == 65
    assert event["committed"] is True
    assert len(authority.calls) == 1


def test_replay_chain_is_deterministic() -> None:
    runtime, _ = make_runtime()
    runtime.execute_batch([InstructionRequest(exact_bytes=b"\x90", explicit_delta=((1, 1),))])
    first = runtime.replay()
    second = runtime.replay()
    assert first["commit_chain_root_sha256"] == second["commit_chain_root_sha256"]
    assert first["authority_replay"]["deterministic_replay"] is True
