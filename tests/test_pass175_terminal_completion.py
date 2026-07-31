from __future__ import annotations

from base64 import b64encode
from hashlib import sha256
from pathlib import Path
from typing import Any
import os

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass175 import (
    EncryptedHash216Store,
    ExactX86Decoder,
    GovernedDeviceFabric,
    HydratedMicrocodeStore,
    NEGATIVE_CORPUS,
    Pass175Error,
    Pass175Runtime,
    SUPPORTED_CORPUS,
    TerminalInstructionRequest,
    TerminalPass175Runtime,
)


class FakeAuthority:
    def __init__(self) -> None:
        self.epoch = 0
        self.state_hash72 = hash72_digest({"schema": "P175_TERMINAL_TEST_GENESIS"}, b"")
        self.calls: list[dict[str, Any]] = []

    def status(self) -> dict[str, Any]:
        return {
            "classification": "P175_TERMINAL_TEST_AUTHORITY",
            "vmrc": {
                "epoch": self.epoch,
                "state_hash72": self.state_hash72,
                "kernel_authorities": 1,
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        predecessor = self.state_hash72
        self.calls.append(dict(kwargs))
        self.epoch += 1
        self.state_hash72 = hash72_digest(
            {"schema": "P175_TERMINAL_TEST_COMMIT", "epoch": self.epoch, "kwargs": kwargs},
            predecessor.encode("ascii"),
        )
        body = {
            "sequence": self.epoch,
            "input_hash72": predecessor,
            "output_hash72": self.state_hash72,
        }
        body["receipt_sha256"] = sha256(repr(sorted(body.items())).encode("utf-8")).hexdigest()
        return {"classification": "P175_TERMINAL_TEST_VM81_COMMIT", "receipt": body}

    def replay(self) -> dict[str, Any]:
        return {
            "classification": "P175_TERMINAL_TEST_AUTHORITY_REPLAY",
            "epoch": self.epoch,
            "state_hash72": self.state_hash72,
            "deterministic_replay": True,
        }


def make_terminal(tmp_path: Path) -> tuple[TerminalPass175Runtime, FakeAuthority]:
    authority = FakeAuthority()
    base = Pass175Runtime(
        authority=authority,
        microcode_store=HydratedMicrocodeStore(tmp_path / "base_microcode.jsonl"),
    )
    secure = EncryptedHash216Store(
        tmp_path / "secure_microcode.sqlite3",
        key_path=tmp_path / "secure_microcode.key",
    )
    return TerminalPass175Runtime(
        base_runtime=base,
        secure_store=secure,
        repository_root=tmp_path.parent,
    ), authority


def test_exact_x86_corpus_reencodes_and_negatives_fail_closed() -> None:
    decoder = ExactX86Decoder()
    retained = set()
    for name, exact, mode in SUPPORTED_CORPUS:
        decoded = decoder.decode(exact, decoder_mode=mode)
        assert decoded.decode_complete, name
        assert decoded.reencode() == exact, name
        assert decoded.exact_bytes_sha256 == sha256(exact).hexdigest()
        retained.add(decoded.retained_encoding_identity_sha256)
    assert len(retained) == len(SUPPORTED_CORPUS)
    for name, exact, mode in NEGATIVE_CORPUS:
        try:
            decoded = decoder.decode(exact, decoder_mode=mode)
        except Pass175Error:
            continue
        assert not decoded.executable or not decoded.decode_complete, name


def test_secure_hash216_store_is_encrypted_indexed_durable_and_restartable(tmp_path: Path) -> None:
    path = tmp_path / "hash216.sqlite3"
    key_path = tmp_path / "hash216.key"
    store = EncryptedHash216Store(path, key_path=key_path)
    record = {"schema": "P175_TEST_RECORD", "ordered": ["0", "01", "1"]}
    metadata = store.admit(record, exact_bytes=b"\x00\x01")
    fetched, restored, exact = store.retrieve(metadata.key_sha256)
    assert restored == record
    assert exact == b"\x00\x01"
    assert len(fetched.hash216_combined) == 216
    assert store.verify()["positional_index_count"] == 216
    receipt = sha256(b"vm81-seal").hexdigest()
    assert store.seal(authority_receipt_sha256=receipt)["sealed"] is True
    root = store.root_sha256
    backup = store.backup(tmp_path / "backup.sqlite3")
    assert backup["bytes"] > 0
    store.close()
    restarted = EncryptedHash216Store(path, key_path=key_path)
    assert restarted.root_sha256 == root
    assert restarted.sealed is True
    assert restarted.verify()["record_count"] == 1
    restarted.close()


def test_governed_device_fabric_covers_required_environment() -> None:
    fabric = GovernedDeviceFabric()
    operations = [
        ("MEMORY", "WRITE", {"address": 0, "data_b64": b64encode(b"A").decode("ascii")}),
        ("PORT_IO", "OUT", {"port": 0x80, "value": 1}),
        ("MMIO", "WRITE", {"address": 4096, "value": 7}),
        ("INTERRUPT", "RAISE", {"vector": 32}),
        ("TIMER", "TICK", {"amount": 1}),
        ("SERIAL", "WRITE", {"data_b64": b64encode(b"HHS").decode("ascii")}),
        ("KEYBOARD", "INGRESS", {"data_b64": b64encode(b"K").decode("ascii")}),
        ("POINTER", "INGRESS", {"x": 1, "y": 2, "buttons": 1}),
        ("BLOCK", "WRITE", {"offset": 0, "data_b64": b64encode(b"B").decode("ascii")}),
        ("FRAMEBUFFER", "WRITE_PIXEL", {"x": 1, "y": 1, "value": 0xFFFFFFFF}),
        ("AUDIO", "WRITE_SAMPLES", {"samples": [0, 1, -1]}),
        ("NETWORK", "INGRESS", {"packet_b64": b64encode(b"packet").decode("ascii")}),
        ("LOADER", "LOAD", {"name": "boot.bin", "image_b64": b64encode(b"BOOT").decode("ascii")}),
        ("RECEIPT", "PROJECT", {"receipt_hash72": "0" * 72}),
    ]
    for device, operation, payload in operations:
        candidate = fabric.candidate(device, operation, payload)
        assert candidate.predecessor_device_root_sha256 == fabric.root_sha256
        event = fabric.commit(candidate, admitted=True)
        assert event.admitted is True
    status = fabric.status()
    assert set(status["registered_devices"]) == {value[0] for value in operations}
    assert status["host_direct_access"] is False
    assert fabric.replay()["deterministic_replay"] is True


def test_canonical_firmware_is_deterministic_and_boots_through_vm81(tmp_path: Path) -> None:
    runtime, authority = make_terminal(tmp_path)
    hydration = runtime.cold_hydrate_terminal(seal=True)
    assert hydration["supported_instruction_forms"] == len(SUPPORTED_CORPUS)
    assert hydration["secure_store"]["sealed"] is True
    boot = runtime.boot_firmware()
    assert boot["ready"] is True
    assert len(boot["stages"]) == 18
    assert len(authority.calls) == 19  # one hydration seal + eighteen ordered stages
    assert runtime.replay()["deterministic_replay"] is True


def test_parallel_candidates_equal_serial_and_state_authority_is_singular(tmp_path: Path) -> None:
    requests = [
        TerminalInstructionRequest(b"\x90", sequence=2, thread_id=2, explicit_delta=((3, 1),)),
        TerminalInstructionRequest(b"\x0f\xa2", sequence=0, thread_id=0, explicit_delta=((1, -1),)),
        TerminalInstructionRequest(b"\x31\xc0", sequence=1, thread_id=1, explicit_delta=((2, 1),)),
    ]
    serial, serial_authority = make_terminal(tmp_path / "serial")
    parallel, parallel_authority = make_terminal(tmp_path / "parallel")
    left = serial.execute_batch(requests, max_workers=1)
    right = parallel.execute_batch(requests, max_workers=8)
    assert left["waves"][0]["candidate_root_sha256"] == right["waves"][0]["candidate_root_sha256"]
    assert serial_authority.state_hash72 == parallel_authority.state_hash72
    assert len(serial_authority.calls) == len(parallel_authority.calls) == 1
    assert right["parallel_state_authority"] is False
    assert right["singleton_vm81_commit_authority"] is True
    assert right["hash72_commit_streams"] == 1


def test_conflicting_candidates_are_recomputed_in_ordered_waves(tmp_path: Path) -> None:
    runtime, authority = make_terminal(tmp_path)
    result = runtime.execute_batch([
        TerminalInstructionRequest(b"\x90", sequence=0, explicit_delta=((7, 1),)),
        TerminalInstructionRequest(b"\x90", sequence=1, explicit_delta=((7, -1),)),
    ])
    assert result["wave_count"] == 2
    assert len(authority.calls) == 2
    assert result["waves"][1]["stale_dependency_recomputed_at_wave_boundary"] is True
    first_output = result["waves"][0]["authority_result"]["receipt"]["output_hash72"]
    assert result["waves"][1]["predecessor_state_root"] == first_output


def test_privileged_and_unsupported_execution_fail_before_authority(tmp_path: Path) -> None:
    runtime, authority = make_terminal(tmp_path)
    with pytest.raises(Pass175Error, match="PRIVILEGED_INSTRUCTION_TRAPPED"):
        runtime.execute_batch([TerminalInstructionRequest(b"\xf4")])
    with pytest.raises(Pass175Error):
        runtime.execute_batch([TerminalInstructionRequest(b"\xd6")])
    assert authority.calls == []


def test_terminal_completion_receipt_with_native_artifact_set(tmp_path: Path) -> None:
    native_root = os.environ.get("HHS_PASS175_NATIVE_ARTIFACT_DIR")
    if not native_root:
        pytest.skip("native terminal artifact set is built by the terminal workflow")
    runtime, _ = make_terminal(tmp_path)
    runtime.cold_hydrate_terminal(seal=True)
    receipt = runtime.terminal_verification(native_root=native_root, require_boot=True)
    assert receipt["terminal_pass175_completion"] is True
    assert receipt["classification"] == (
        "HHS_PASS_175_HASH216_HYDRATED_VM5184_G243_VIRTUAL_INSTRUCTION_PROCESSOR_VERIFIED"
    )
    assert all(receipt["checks"].values())
    assert receipt["native_artifacts"]["complete"] is True
    assert receipt["external_deployment_quota_not_an_acceptance_gate"] is True
    assert len(receipt["receipt_sha256"]) == 64
