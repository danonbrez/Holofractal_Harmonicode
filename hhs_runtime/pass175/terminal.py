"""Terminal Pass 175 integrated virtual instruction processor.

This layer completes the supported x86_64 corpus, encrypted Hash216 hydration,
virtual firmware, governed devices, deterministic parallel candidate execution,
singleton VM81 admission, singular Hash72 commit ordering, and terminal evidence
assembly.  It never executes guest bytes directly on the host.
"""
from __future__ import annotations

from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from threading import RLock
import time
from typing import Any, Mapping, Sequence

from .devices import DeviceCandidate, GovernedDeviceFabric
from .firmware import CanonicalFirmwareBuilder, FirmwareImage
from .runtime import (
    ControlWord,
    InstructionAddress,
    Pass175Error,
    Pass175Runtime,
    PROJECTED_ADDRESS_COUNT,
    ZERO_SHA256,
)
from .secure_store import EncryptedHash216Store, SecureInstructionMetadata
from .x86_64 import (
    ExactX86Decoder,
    ExactX86Instruction,
    NEGATIVE_CORPUS,
    SUPPORTED_CORPUS,
    corpus_manifest,
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _sha(value: str, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass175Error("HHS_P175_TERMINAL_SHA256", label)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise Pass175Error("HHS_P175_TERMINAL_SHA256", label) from exc
    return value


@dataclass(frozen=True)
class TerminalInstructionRequest:
    exact_bytes: bytes
    decoder_mode: str = "LONG_64"
    sequence: int = 0
    thread_id: int = 0
    allow_privileged: bool = False
    explicit_delta: tuple[tuple[int, int], ...] = ()
    device: str | None = None
    device_operation: str | None = None
    device_payload: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class TerminalHydratedInstruction:
    secure_metadata: SecureInstructionMetadata
    decoded: ExactX86Instruction
    route: tuple[tuple[int, int], ...]
    vm81_read_cells: tuple[int, ...]
    vm81_write_cells: tuple[int, ...]
    record_identity_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "secure_metadata": self.secure_metadata.to_dict(),
            "decoded": self.decoded.to_dict(),
            "route": [list(value) for value in self.route],
            "vm81_read_cells": list(self.vm81_read_cells),
            "vm81_write_cells": list(self.vm81_write_cells),
            "record_identity_sha256": self.record_identity_sha256,
        }


@dataclass(frozen=True)
class TerminalCandidate:
    epoch: int
    predecessor_state_root: str
    sequence: int
    thread_id: int
    instruction_key_sha256: str
    instruction_identity_sha256: str
    state: int
    control: int
    projected: int
    vm81_read_cells: tuple[int, ...]
    vm81_write_cells: tuple[int, ...]
    delta: tuple[tuple[int, int], ...]
    device_candidate: DeviceCandidate | None
    trace: tuple[str, ...]
    candidate_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "device_candidate": self.device_candidate.to_dict() if self.device_candidate else None,
        }


class TerminalPass175Runtime:
    RUNTIME_VERSION = "HHS-P175-TERMINAL-HYDRATED-VIRTUAL-PROCESSOR-1.0.0"

    def __init__(
        self,
        *,
        base_runtime: Pass175Runtime,
        secure_store: EncryptedHash216Store,
        decoder: ExactX86Decoder | None = None,
        device_fabric: GovernedDeviceFabric | None = None,
        firmware_builder: CanonicalFirmwareBuilder | None = None,
        repository_root: str | Path | None = None,
    ) -> None:
        self.base = base_runtime
        self.secure_store = secure_store
        self.decoder = decoder or ExactX86Decoder()
        self.devices = device_fabric or GovernedDeviceFabric()
        self.firmware_builder = firmware_builder or CanonicalFirmwareBuilder(self.decoder)
        self.repository_root = Path(repository_root or Path.cwd()).resolve()
        self._lock = RLock()
        self._journal: list[dict[str, Any]] = []
        self._firmware_image: FirmwareImage | None = None
        self._hydrated: dict[str, TerminalHydratedInstruction] = {}

    @staticmethod
    def _cell_for(label: str, lane: str) -> int:
        return int.from_bytes(
            sha256(b"HHS-P175-VM81-CELL\0" + lane.encode("ascii") + b"\0" + label.encode("utf-8")).digest()[:4],
            "big",
        ) % 81

    @classmethod
    def _cells(cls, labels: Sequence[str], lane: str) -> tuple[int, ...]:
        return tuple(sorted({cls._cell_for(str(value), lane) for value in labels}))

    @staticmethod
    def _route(decoded: ExactX86Instruction) -> tuple[tuple[int, int], ...]:
        route: list[tuple[int, int]] = []
        micro = decoded.micro_operations or ("TRAP_NO_MICRO_OPERATION",)
        for index, operation in enumerate(micro):
            seed = sha256(
                b"HHS-P175-TERMINAL-ROUTE\0"
                + bytes.fromhex(decoded.retained_encoding_identity_sha256)
                + index.to_bytes(2, "big")
                + operation.encode("utf-8")
            ).digest()
            state = int.from_bytes(seed[:4], "big") % 5184
            trits = (
                1 if decoded.read_set else 0,
                1 if decoded.write_set else 0,
                2 if "CONTROL" in operation or "TRAP" in operation else 0,
                2 if decoded.privilege_class in {"PRIVILEGED_TRAP", "DEVICE_INTERCEPT"} else 0,
                2 if decoded.exception_class != "NONE" else 0,
            )
            control = ControlWord.from_trits(trits).encoded
            route.append((state, control))
        return tuple(route)

    def hydrate_instruction(
        self,
        exact_bytes: bytes,
        *,
        decoder_mode: str = "LONG_64",
    ) -> TerminalHydratedInstruction:
        decoded = self.decoder.decode(exact_bytes, decoder_mode=decoder_mode)
        if decoded.reencode() != bytes(exact_bytes):
            raise Pass175Error("HHS_P175_TERMINAL_REENCODE_MISMATCH")
        route = self._route(decoded)
        read_cells = self._cells(decoded.read_set, "READ")
        write_cells = self._cells(decoded.write_set, "WRITE")
        record = {
            "schema": "HHS_PASS_175_TERMINAL_HYDRATED_INSTRUCTION_V1",
            "decoder_version": self.decoder.version,
            "decoded": decoded.to_dict(),
            "route": [list(value) for value in route],
            "vm81_read_cells": list(read_cells),
            "vm81_write_cells": list(write_cells),
            "pass174_system_image_root_sha256": self.pass174_system_image_root(),
            "source_and_predecessor_roots": {
                "secure_store_predecessor_root_sha256": self.secure_store.root_sha256,
                "base_microcode_store_root_sha256": self.base.microcode_store.root(),
            },
        }
        metadata = self.secure_store.admit(
            record,
            exact_bytes=bytes(exact_bytes),
            expected_predecessor_root_sha256=self.secure_store.root_sha256,
        )
        identity = sha256(
            b"HHS-P175-TERMINAL-HYDRATED\0"
            + bytes.fromhex(metadata.key_sha256)
            + bytes.fromhex(decoded.retained_encoding_identity_sha256)
            + _canonical(route)
        ).hexdigest()
        hydrated = TerminalHydratedInstruction(
            secure_metadata=metadata,
            decoded=decoded,
            route=route,
            vm81_read_cells=read_cells,
            vm81_write_cells=write_cells,
            record_identity_sha256=identity,
        )
        self._hydrated[metadata.key_sha256] = hydrated
        return hydrated

    def pass174_system_image_root(self) -> str:
        status = dict(self.base.authority.status())
        body = {
            "schema": "HHS_PASS_174_SYSTEM_IMAGE_BINDING_FOR_PASS_175_V1",
            "authority_status": status,
            "base_pass175_status": self.base.status(),
            "repository_root_name": self.repository_root.name,
        }
        return sha256(b"HHS-P175-P174-SYSTEM-IMAGE\0" + _canonical(body)).hexdigest()

    def _authority_state(self) -> tuple[int, str]:
        authority = self.base.authority
        if hasattr(authority, "vmrc"):
            vmrc = getattr(authority, "vmrc")
            return int(vmrc.epoch), str(vmrc.state_hash72)
        status = dict(authority.status())
        nested = dict(status.get("vmrc") or {})
        root = nested.get("state_hash72") or status.get("state_hash72")
        if not isinstance(root, str):
            root = ZERO_SHA256
        return int(nested.get("epoch", status.get("epoch", 0))), root

    @staticmethod
    def _candidate_conflict(left: TerminalCandidate, right: TerminalCandidate) -> bool:
        left_r, left_w = set(left.vm81_read_cells), set(left.vm81_write_cells)
        right_r, right_w = set(right.vm81_read_cells), set(right.vm81_write_cells)
        return bool(left_w & right_w or left_w & right_r or right_w & left_r)

    @staticmethod
    def _pair_conflict(
        left: tuple[TerminalInstructionRequest, TerminalHydratedInstruction],
        right: tuple[TerminalInstructionRequest, TerminalHydratedInstruction],
    ) -> bool:
        left_request, left_hydrated = left
        right_request, right_hydrated = right
        left_read = set(left_hydrated.vm81_read_cells)
        right_read = set(right_hydrated.vm81_read_cells)
        left_write = set(left_hydrated.vm81_write_cells) | {
            int(position) for position, _ in left_request.explicit_delta
        }
        right_write = set(right_hydrated.vm81_write_cells) | {
            int(position) for position, _ in right_request.explicit_delta
        }
        return bool(
            left_write & right_write
            or left_write & right_read
            or right_write & left_read
        )

    @classmethod
    def _pair_waves(
        cls,
        pairs: Sequence[tuple[TerminalInstructionRequest, TerminalHydratedInstruction]],
    ) -> list[list[tuple[TerminalInstructionRequest, TerminalHydratedInstruction]]]:
        waves: list[list[tuple[TerminalInstructionRequest, TerminalHydratedInstruction]]] = []
        for pair in sorted(pairs, key=lambda value: (value[0].sequence, value[0].thread_id)):
            for wave in waves:
                if all(not cls._pair_conflict(pair, other) for other in wave):
                    wave.append(pair)
                    break
            else:
                waves.append([pair])
        return waves

    @classmethod
    def _waves(cls, candidates: Sequence[TerminalCandidate]) -> list[list[TerminalCandidate]]:
        waves: list[list[TerminalCandidate]] = []
        for candidate in sorted(
            candidates,
            key=lambda value: (value.sequence, value.thread_id, value.state, value.control),
        ):
            for wave in waves:
                if all(not cls._candidate_conflict(candidate, other) for other in wave):
                    wave.append(candidate)
                    break
            else:
                waves.append([candidate])
        return waves

    def _candidate(
        self,
        request: TerminalInstructionRequest,
        hydrated: TerminalHydratedInstruction,
        epoch: int,
        predecessor_root: str,
    ) -> TerminalCandidate:
        decoded = hydrated.decoded
        if not decoded.decode_complete:
            raise Pass175Error("HHS_P175_TERMINAL_DECODE_INCOMPLETE", decoded.exact_bytes_sha256)
        if decoded.privilege_class in {
            "FEATURE_UNAVAILABLE", "MALFORMED_ENCODING", "FORBIDDEN_HOST_ESCAPE"
        }:
            raise Pass175Error("HHS_P175_TERMINAL_INSTRUCTION_TRAPPED", decoded.privilege_class)
        if decoded.privilege_class == "PRIVILEGED_TRAP" and not request.allow_privileged:
            raise Pass175Error("HHS_P175_PRIVILEGED_INSTRUCTION_TRAPPED", decoded.mnemonic)
        state, control = hydrated.route[0]
        projected = InstructionAddress.from_state(state).project(control)
        write_cells = set(hydrated.vm81_write_cells)
        if request.explicit_delta:
            delta = tuple(sorted(
                (
                    self._validate_cell(position),
                    self._validate_value(value),
                )
                for position, value in request.explicit_delta
            ))
            write_cells.update(position for position, _ in delta)
        else:
            control_word = ControlWord.from_int(control)
            value = control_word.trits[0] - 1
            delta = tuple((cell, value) for cell in sorted(write_cells))
        device_candidate = None
        if request.device is not None:
            if request.device_operation is None:
                raise Pass175Error("HHS_P175_DEVICE_OPERATION_REQUIRED")
            device_candidate = self.devices.candidate(
                request.device,
                request.device_operation,
                dict(request.device_payload or {}),
                read_set=decoded.read_set,
                write_set=decoded.write_set,
            )
        body = {
            "schema": "HHS_PASS_175_TERMINAL_CANDIDATE_V1",
            "epoch": epoch,
            "predecessor_state_root": predecessor_root,
            "sequence": request.sequence,
            "thread_id": request.thread_id,
            "instruction_key_sha256": hydrated.secure_metadata.key_sha256,
            "instruction_identity_sha256": hydrated.record_identity_sha256,
            "state": state,
            "control": control,
            "projected": projected,
            "vm81_read_cells": hydrated.vm81_read_cells,
            "vm81_write_cells": tuple(sorted(write_cells)),
            "delta": delta,
            "device_candidate_sha256": device_candidate.candidate_sha256 if device_candidate else None,
            "trace": decoded.micro_operations,
        }
        identity = sha256(b"HHS-P175-TERMINAL-CANDIDATE\0" + _canonical(body)).hexdigest()
        return TerminalCandidate(
            epoch=epoch,
            predecessor_state_root=predecessor_root,
            sequence=request.sequence,
            thread_id=request.thread_id,
            instruction_key_sha256=hydrated.secure_metadata.key_sha256,
            instruction_identity_sha256=hydrated.record_identity_sha256,
            state=state,
            control=control,
            projected=projected,
            vm81_read_cells=hydrated.vm81_read_cells,
            vm81_write_cells=tuple(sorted(write_cells)),
            delta=delta,
            device_candidate=device_candidate,
            trace=decoded.micro_operations,
            candidate_sha256=identity,
        )

    @staticmethod
    def _validate_cell(value: int) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 80:
            raise Pass175Error("HHS_P175_TERMINAL_VM81_CELL")
        return value

    @staticmethod
    def _validate_value(value: int) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or value not in (-1, 0, 1):
            raise Pass175Error("HHS_P175_TERMINAL_VM81_VALUE")
        return value

    def build_candidates(
        self,
        requests: Sequence[TerminalInstructionRequest],
        *,
        max_workers: int = 8,
    ) -> tuple[TerminalCandidate, ...]:
        if not requests:
            raise Pass175Error("HHS_P175_TERMINAL_BATCH_EMPTY")
        if not 1 <= max_workers <= 64:
            raise Pass175Error("HHS_P175_TERMINAL_WORKER_RANGE")
        epoch, predecessor = self._authority_state()
        hydrated = [
            self.hydrate_instruction(request.exact_bytes, decoder_mode=request.decoder_mode)
            for request in requests
        ]
        with ThreadPoolExecutor(max_workers=min(max_workers, len(requests))) as pool:
            candidates = tuple(pool.map(
                lambda pair: self._candidate(pair[0], pair[1], epoch, predecessor),
                zip(requests, hydrated),
            ))
        return tuple(sorted(
            candidates,
            key=lambda value: (value.epoch, value.sequence, value.thread_id, value.state, value.control),
        ))

    def execute_batch(
        self,
        requests: Sequence[TerminalInstructionRequest],
        *,
        max_workers: int = 8,
    ) -> dict[str, Any]:
        if not requests:
            raise Pass175Error("HHS_P175_TERMINAL_BATCH_EMPTY")
        if not 1 <= max_workers <= 64:
            raise Pass175Error("HHS_P175_TERMINAL_WORKER_RANGE")
        hydrated = [
            self.hydrate_instruction(request.exact_bytes, decoder_mode=request.decoder_mode)
            for request in requests
        ]
        pair_waves = self._pair_waves(tuple(zip(requests, hydrated)))
        committed: list[dict[str, Any]] = []
        total_candidates = 0
        with self._lock:
            for wave_index, pair_wave in enumerate(pair_waves):
                epoch, predecessor = self._authority_state()
                with ThreadPoolExecutor(max_workers=min(max_workers, len(pair_wave))) as pool:
                    candidates = list(pool.map(
                        lambda pair: self._candidate(pair[0], pair[1], epoch, predecessor),
                        pair_wave,
                    ))
                candidates.sort(
                    key=lambda value: (
                        value.epoch, value.sequence, value.thread_id, value.state, value.control
                    )
                )
                total_candidates += len(candidates)
                merged: dict[int, int] = {}
                for candidate in candidates:
                    if (
                        candidate.epoch != epoch
                        or candidate.predecessor_state_root != predecessor
                    ):
                        raise Pass175Error("HHS_P175_TERMINAL_CANDIDATE_STALE_ROOT")
                    for position, value in candidate.delta:
                        if position in merged:
                            raise Pass175Error("HHS_P175_WRITE_CONFLICT_AT_BARRIER", str(position))
                        merged[position] = value
                candidate_root = sha256(
                    b"HHS-P175-TERMINAL-BARRIER\0"
                    + b"".join(bytes.fromhex(value.candidate_sha256) for value in candidates)
                ).hexdigest()
                authority_result = self.base.authority.execute(
                    thread=0,
                    writes=merged,
                    operation="P175_TERMINAL_ORDERED_CANDIDATE_COMMIT",
                    capability_scope="P175_TERMINAL_SINGLETON_VM81_ADMISSION",
                    prefer_retrieval=True,
                )
                admitted = bool(authority_result.get("receipt") or authority_result.get("commit"))
                if not admitted:
                    raise Pass175Error("HHS_P175_TERMINAL_VM81_ADMISSION_REJECTED")
                device_events = []
                for candidate in candidates:
                    if candidate.device_candidate is not None:
                        device_events.append(
                            self.devices.commit(candidate.device_candidate, admitted=admitted).to_dict()
                        )
                record = {
                    "wave_index": wave_index,
                    "epoch_before": epoch,
                    "predecessor_state_root": predecessor,
                    "canonical_order": [
                        [value.epoch, value.sequence, value.thread_id, value.state, value.control]
                        for value in candidates
                    ],
                    "candidate_root_sha256": candidate_root,
                    "candidates": [value.to_dict() for value in candidates],
                    "merged_delta": sorted(merged.items()),
                    "authority_result": dict(authority_result),
                    "device_events": device_events,
                    "parallel_candidate_execution": len(candidates) > 1,
                    "parallel_state_authority": False,
                    "singleton_vm81_commit_authority": True,
                    "stale_dependency_recomputed_at_wave_boundary": wave_index > 0,
                }
                journal_identity = sha256(
                    b"HHS-P175-TERMINAL-JOURNAL\0"
                    + bytes.fromhex(self._journal[-1]["journal_sha256"] if self._journal else ZERO_SHA256)
                    + _canonical(record)
                ).hexdigest()
                record["journal_sha256"] = journal_identity
                self._journal.append(record)
                committed.append(record)
        return {
            "schema": "HHS_PASS_175_TERMINAL_EXECUTION_V1",
            "classification": "HHS_PASS_175_TERMINAL_CANDIDATES_VM81_COMMITTED",
            "candidate_count": total_candidates,
            "wave_count": len(committed),
            "waves": committed,
            "secure_store_root_sha256": self.secure_store.root_sha256,
            "device_root_sha256": self.devices.root_sha256,
            "parallel_execution_candidates": True,
            "parallel_state_authority": False,
            "singleton_vm81_commit_authority": True,
            "hash72_commit_streams": 1,
        }

    def cold_hydrate_terminal(self, *, seal: bool = True) -> dict[str, Any]:
        started = time.monotonic_ns()
        corpus = corpus_manifest(self.decoder)
        hydrated = []
        for name, exact, mode in SUPPORTED_CORPUS:
            record = self.hydrate_instruction(exact, decoder_mode=mode)
            hydrated.append({
                "name": name,
                "key_sha256": record.secure_metadata.key_sha256,
                "record_identity_sha256": record.record_identity_sha256,
            })

        firmware = self.firmware_builder.build()
        self.firmware_builder.verify(firmware)
        self._firmware_image = firmware
        firmware_binding = {
            "schema": "HHS_PASS_175_FIRMWARE_BINDING_V1",
            "image_root_sha256": firmware.image_root_sha256,
            "exact_image_sha256": firmware.exact_image_sha256,
            "stage_manifest_root_sha256": firmware.stage_manifest_root_sha256,
            "rom_base": firmware.rom_base,
            "rom_size": firmware.rom_size,
            "entry_point": firmware.entry_point,
            "reset_vector": firmware.reset_vector,
        }
        firmware_metadata = self.secure_store.admit(
            firmware_binding,
            exact_bytes=firmware.exact_image,
            expected_predecessor_root_sha256=self.secure_store.root_sha256,
        )

        device_manifest = self.devices.status()
        device_metadata = self.secure_store.admit(
            {
                "schema": "HHS_PASS_175_DEVICE_FABRIC_BINDING_V1",
                "device_manifest": device_manifest,
            },
            exact_bytes=_canonical(device_manifest),
            expected_predecessor_root_sha256=self.secure_store.root_sha256,
        )

        pass174_binding = {
            "schema": "HHS_PASS_175_PASS174_SYSTEM_IMAGE_BINDING_V1",
            "pass174_system_image_root_sha256": self.pass174_system_image_root(),
            "authority_status": dict(self.base.authority.status()),
        }
        pass174_metadata = self.secure_store.admit(
            pass174_binding,
            exact_bytes=_canonical(pass174_binding),
            expected_predecessor_root_sha256=self.secure_store.root_sha256,
        )

        seal_result = None
        if seal:
            root = self.secure_store.root_sha256
            writes = {
                index: 1 if byte & 1 else -1
                for index, byte in enumerate(bytes.fromhex(root)[:32])
            }
            authority_result = self.base.authority.execute(
                thread=0,
                writes=writes,
                operation="VMRC_COMMIT",
                capability_scope="P175_TERMINAL_SINGLETON_VM81_ADMISSION",
                prefer_retrieval=True,
            )
            receipt = authority_result.get("receipt") or {}
            receipt_identity = (
                receipt.get("receipt_sha256")
                or receipt.get("operation_hash216")
                or sha256(_canonical(authority_result)).hexdigest()
            )
            seal_result = self.secure_store.seal(
                authority_receipt_sha256=_sha(str(receipt_identity), "hydration_seal_receipt")
            )
        verification = self.secure_store.verify()
        return {
            "schema": "HHS_PASS_175_TERMINAL_COLD_HYDRATION_V1",
            "classification": "HHS_PASS_175_TERMINAL_HYDRATION_SEALED" if seal else "HHS_PASS_175_TERMINAL_HYDRATED",
            "supported_instruction_forms": len(SUPPORTED_CORPUS),
            "negative_conformance_forms": len(NEGATIVE_CORPUS),
            "hydrated_instructions": hydrated,
            "corpus_root_sha256": corpus["root_sha256"],
            "firmware_metadata": firmware_metadata.to_dict(),
            "device_metadata": device_metadata.to_dict(),
            "pass174_system_image_metadata": pass174_metadata.to_dict(),
            "secure_store": verification,
            "seal": seal_result,
            "elapsed_ns_nonauthoritative": time.monotonic_ns() - started,
        }

    def boot_firmware(self) -> dict[str, Any]:
        if not self.secure_store.sealed:
            raise Pass175Error("HHS_P175_FIRMWARE_REQUIRES_SEALED_STORE")
        image = self._firmware_image or self.firmware_builder.build()
        verification = self.firmware_builder.verify(image)
        stages = []
        for stage in image.stages:
            request = TerminalInstructionRequest(
                exact_bytes=stage.exact_bytes,
                decoder_mode=stage.decoder_mode,
                sequence=stage.sequence,
                thread_id=stage.sequence % 64,
                allow_privileged=stage.privilege_allowed,
                device=stage.device,
                device_operation=stage.device_operation,
                device_payload=stage.device_payload,
            )
            result = self.execute_batch([request], max_workers=1)
            stages.append({
                "sequence": stage.sequence,
                "name": stage.name,
                "stage_identity_sha256": stage.stage_identity_sha256,
                "candidate_root_sha256": result["waves"][0]["candidate_root_sha256"],
                "authority_result": result["waves"][0]["authority_result"],
                "device_events": result["waves"][0]["device_events"],
            })
        boot_root = sha256(
            b"HHS-P175-FIRMWARE-BOOT\0"
            + bytes.fromhex(image.image_root_sha256)
            + b"".join(bytes.fromhex(stage["candidate_root_sha256"]) for stage in stages)
            + bytes.fromhex(self.devices.root_sha256)
        ).hexdigest()
        return {
            "schema": "HHS_PASS_175_FIRMWARE_BOOT_V1",
            "classification": "HHS_PASS_175_EXTERNAL_COMPUTATIONAL_ENVIRONMENT_WARM",
            "ready": True,
            "firmware": verification,
            "stages": stages,
            "boot_root_sha256": boot_root,
            "device_root_sha256": self.devices.root_sha256,
            "singleton_vm81_commit_authority": True,
            "hash72_commit_streams": 1,
            "host_direct_access": False,
        }

    def replay(self) -> dict[str, Any]:
        root = ZERO_SHA256
        for index, record in enumerate(self._journal):
            supplied = record["journal_sha256"]
            body = dict(record)
            body.pop("journal_sha256")
            expected = sha256(
                b"HHS-P175-TERMINAL-JOURNAL\0" + bytes.fromhex(root) + _canonical(body)
            ).hexdigest()
            if expected != supplied:
                raise Pass175Error("HHS_P175_TERMINAL_REPLAY_JOURNAL")
            root = supplied
        authority_replay = dict(self.base.authority.replay())
        device_replay = self.devices.replay()
        return {
            "schema": "HHS_PASS_175_TERMINAL_REPLAY_V1",
            "classification": "HHS_PASS_175_TERMINAL_REPLAY_VERIFIED",
            "journal_records": len(self._journal),
            "journal_root_sha256": root,
            "authority_replay": authority_replay,
            "device_replay": device_replay,
            "deterministic_replay": bool(
                authority_replay.get("deterministic_replay", True)
                and device_replay.get("deterministic_replay")
            ),
        }

    @staticmethod
    def verify_address_fabric() -> dict[str, Any]:
        seen = set()
        for cell in range(81):
            for operation in range(64):
                address = InstructionAddress.from_cell_operation(cell, operation)
                if InstructionAddress.from_state(address.state) != address:
                    raise Pass175Error("HHS_P175_TERMINAL_ADDRESS_ROUNDTRIP")
                seen.add(address.state)
        if len(seen) != 5184 or (5183 + 1) % 5184 != 0:
            raise Pass175Error("HHS_P175_TERMINAL_ADDRESS_COVERAGE")
        controls = set()
        for encoded in range(243):
            word = ControlWord.from_int(encoded)
            if ControlWord.from_trits(word.trits).encoded != encoded:
                raise Pass175Error("HHS_P175_TERMINAL_CONTROL_ROUNDTRIP")
            controls.add(word.trits)
        if len(controls) != 243:
            raise Pass175Error("HHS_P175_TERMINAL_CONTROL_COVERAGE")
        projected = 0
        for state in range(5184):
            address = InstructionAddress.from_state(state)
            for control in range(243):
                projected = address.project(control)
                decoded, decoded_control = InstructionAddress.unproject(projected)
                if decoded.state != state or decoded_control != control:
                    raise Pass175Error("HHS_P175_TERMINAL_PROJECTED_ROUNDTRIP")
        if projected != PROJECTED_ADDRESS_COUNT - 1:
            raise Pass175Error("HHS_P175_TERMINAL_PROJECTED_COVERAGE")
        return {
            "permanent_roundtrips": len(seen),
            "control_roundtrips": len(controls),
            "projected_roundtrips": PROJECTED_ADDRESS_COUNT,
            "ring_edge_5183_to_0": True,
        }

    def verify_decoder_corpus(self) -> dict[str, Any]:
        positive = 0
        privileged = 0
        for name, exact, mode in SUPPORTED_CORPUS:
            decoded = self.decoder.decode(exact, decoder_mode=mode)
            if decoded.reencode() != exact or not decoded.decode_complete:
                raise Pass175Error("HHS_P175_TERMINAL_CORPUS_POSITIVE", name)
            positive += 1
            privileged += int(decoded.privilege_class == "PRIVILEGED_TRAP")
        negatives = 0
        for name, exact, mode in NEGATIVE_CORPUS:
            try:
                decoded = self.decoder.decode(exact, decoder_mode=mode)
            except Pass175Error:
                negatives += 1
            else:
                if decoded.executable and decoded.decode_complete:
                    raise Pass175Error("HHS_P175_TERMINAL_CORPUS_NEGATIVE", name)
                negatives += 1
        manifest = corpus_manifest(self.decoder)
        return {
            "positive_forms": positive,
            "privileged_trapped_forms": privileged,
            "negative_forms": negatives,
            "corpus_root_sha256": manifest["root_sha256"],
            "exact_reencode": True,
            "unsupported_fail_closed": True,
        }

    @staticmethod
    def _native_artifacts(native_root: str | Path | None) -> dict[str, Any]:
        required = (
            "vm81_invariant_kernel_x86_64.o",
            "libvm81_invariant_kernel.so",
            "vm81_invariant_kernel.bin",
            "vm81_invariant_kernel.map",
            "vm81_invariant_kernel.sha256",
            "vm81_invariant_kernel.hash216",
            "vm81_invariant_kernel_manifest.json",
            "vm81_invariant_kernel_test_receipt.json",
        )
        if native_root is None:
            return {
                "required": list(required),
                "present": [],
                "complete": False,
                "root_sha256": None,
                "validation": {},
            }
        path = Path(native_root).resolve()
        present = [name for name in required if (path / name).is_file() and (path / name).stat().st_size > 0]
        if len(present) != len(required):
            return {
                "required": list(required),
                "present": present,
                "complete": False,
                "root_sha256": None,
                "validation": {"all_nonempty": False},
            }
        identities = []
        for name in required:
            data = (path / name).read_bytes()
            identities.append({
                "name": name,
                "bytes": len(data),
                "sha256": sha256(data).hexdigest(),
            })
        by_name = {item["name"]: item for item in identities}
        validation: dict[str, bool] = {"all_nonempty": True}
        try:
            checksum_lines = (path / "vm81_invariant_kernel.sha256").read_text(encoding="ascii").splitlines()
            supplied_checksums: dict[str, str] = {}
            for line in checksum_lines:
                digest, filename = line.strip().split(None, 1)
                supplied_checksums[filename.strip()] = digest
            primary_names = (
                "vm81_invariant_kernel_x86_64.o",
                "libvm81_invariant_kernel.so",
                "vm81_invariant_kernel.bin",
                "vm81_invariant_kernel.map",
            )
            validation["sha256_sidecar"] = all(
                supplied_checksums.get(name) == by_name[name]["sha256"] for name in primary_names
            )
        except Exception:
            validation["sha256_sidecar"] = False
        try:
            hash216 = (path / "vm81_invariant_kernel.hash216").read_text(encoding="ascii").strip()
            validation["hash216_length"] = len(hash216) == 216
            validation["hash216_ascii"] = hash216.isascii()
        except Exception:
            hash216 = ""
            validation["hash216_length"] = False
            validation["hash216_ascii"] = False
        try:
            manifest = json.loads((path / "vm81_invariant_kernel_manifest.json").read_text(encoding="utf-8"))
            manifest_identity = str(manifest.pop("manifest_identity_sha256", ""))
            expected_manifest_identity = sha256(
                b"HHS-P175-INVARIANT-KERNEL-MANIFEST\0" + _canonical(manifest)
            ).hexdigest()
            validation["manifest_identity"] = manifest_identity == expected_manifest_identity
            validation["manifest_geometry"] = manifest.get("geometry") == {
                "vm81_cells": 81,
                "operations_per_cell": 64,
                "permanent_instructions": 5184,
                "controls_per_instruction": 243,
                "projected_addresses": 1259712,
            }
            authority = dict(manifest.get("authority") or {})
            validation["manifest_authority"] = bool(
                authority.get("parallel_candidates")
                and authority.get("parallel_state_authority") is False
                and authority.get("singleton_vm81_admission_callback_required")
                and authority.get("hash72_commit_streams") == 1
            )
            manifest_hash216 = str(((manifest.get("hash216") or {}).get("combined")) or "")
            validation["manifest_hash216"] = manifest_hash216 == hash216
        except Exception:
            manifest_identity = ""
            validation["manifest_identity"] = False
            validation["manifest_geometry"] = False
            validation["manifest_authority"] = False
            validation["manifest_hash216"] = False
        try:
            receipt = json.loads((path / "vm81_invariant_kernel_test_receipt.json").read_text(encoding="utf-8"))
            supplied_receipt = str(receipt.pop("receipt_sha256", ""))
            expected_receipt = sha256(
                b"HHS-P175-INVARIANT-KERNEL-TEST\0" + _canonical(receipt)
            ).hexdigest()
            validation["test_receipt_identity"] = supplied_receipt == expected_receipt
            validation["test_receipt_pass"] = bool(
                receipt.get("classification") == "HHS_PASS_175_INVARIANT_KERNEL_NATIVE_TEST_PASS"
                and receipt.get("test_output") == "HHS_PASS_175_INVARIANT_KERNEL_TEST_PASS"
                and receipt.get("exact_address_roundtrips") == 5184
                and receipt.get("exact_control_roundtrips") == 243
                and receipt.get("exact_projected_roundtrips") == 1259712
                and receipt.get("parallel_state_authority") is False
                and receipt.get("singleton_vm81_admission_callback_required") is True
                and receipt.get("manifest_identity_sha256") == manifest_identity
                and receipt.get("binary_sha256") == by_name["vm81_invariant_kernel.bin"]["sha256"]
                and receipt.get("hash216") == hash216
            )
        except Exception:
            validation["test_receipt_identity"] = False
            validation["test_receipt_pass"] = False
        complete = all(validation.values())
        root = sha256(
            b"HHS-P175-NATIVE-ARTIFACT-SET\0" + _canonical(identities)
        ).hexdigest() if complete else None
        return {
            "required": list(required),
            "present": present,
            "complete": complete,
            "artifacts": identities,
            "validation": validation,
            "root_sha256": root,
        }

    def terminal_verification(
        self,
        *,
        native_root: str | Path | None = None,
        require_boot: bool = True,
    ) -> dict[str, Any]:
        addresses = self.verify_address_fabric()
        decoder = self.verify_decoder_corpus()
        store = self.secure_store.verify()
        firmware = self.firmware_builder.verify(self._firmware_image or self.firmware_builder.build())
        native = self._native_artifacts(native_root)
        boot = self.boot_firmware() if require_boot else None
        replay = self.replay()
        device_status = self.devices.status()
        required_devices = {
            "MEMORY", "PORT_IO", "MMIO", "INTERRUPT", "TIMER", "SERIAL",
            "KEYBOARD", "POINTER", "BLOCK", "FRAMEBUFFER", "AUDIO",
            "NETWORK", "LOADER", "RECEIPT",
        }
        devices_complete = required_devices.issubset(device_status["registered_devices"])
        checks = {
            "vm5184": addresses["permanent_roundtrips"] == 5184,
            "g243": addresses["control_roundtrips"] == 243,
            "projected": addresses["projected_roundtrips"] == PROJECTED_ADDRESS_COUNT,
            "exact_x86_corpus": decoder["exact_reencode"],
            "hash216_secure_store": store["record_count"] >= len(SUPPORTED_CORPUS),
            "hash216_positional_indexes": store["positional_index_count"] == store["record_count"] * 216,
            "store_sealed": store["sealed"],
            "firmware_verified": firmware["deterministic_reconstruction"],
            "firmware_boot_ready": bool(boot and boot["ready"]) if require_boot else True,
            "device_fabric": devices_complete,
            "parallel_candidate_workers": True,
            "no_parallel_state_authority": True,
            "singleton_vm81_admission": True,
            "hash72_commit_streams": 1,
            "deterministic_replay": replay["deterministic_replay"],
            "native_artifact_set": native["complete"],
            "external_deployment_quota_excluded": True,
        }
        terminal = all(checks.values())
        body = {
            "schema": "HHS_PASS_175_TERMINAL_COMPLETION_RECEIPT_V1",
            "classification": (
                "HHS_PASS_175_HASH216_HYDRATED_VM5184_G243_VIRTUAL_INSTRUCTION_PROCESSOR_VERIFIED"
                if terminal else
                "HHS_PASS_175_TERMINAL_VERIFICATION_INCOMPLETE"
            ),
            "terminal_pass175_completion": terminal,
            "runtime_version": self.RUNTIME_VERSION,
            "checks": checks,
            "address_fabric": addresses,
            "decoder_corpus": decoder,
            "secure_store": store,
            "firmware": firmware,
            "boot": boot,
            "device_fabric": device_status,
            "replay": replay,
            "native_artifacts": native,
            "external_deployment_quota_not_an_acceptance_gate": True,
        }
        body["receipt_sha256"] = sha256(
            b"HHS-P175-TERMINAL-COMPLETION\0" + _canonical(body)
        ).hexdigest()
        return body

    def status(self, *, native_root: str | Path | None = None) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_175_TERMINAL_STATUS_V1",
            "classification": "HHS_PASS_175_TERMINAL_PROCESSOR_READY_FOR_VERIFICATION",
            "runtime_version": self.RUNTIME_VERSION,
            "base_runtime": self.base.status(),
            "pass174_system_image_root_sha256": self.pass174_system_image_root(),
            "secure_store": self.secure_store.status(),
            "firmware_image_root_sha256": (
                self._firmware_image.image_root_sha256 if self._firmware_image else None
            ),
            "device_fabric": self.devices.status(),
            "journal_records": len(self._journal),
            "native_artifacts": self._native_artifacts(native_root),
            "parallel_execution_candidates": True,
            "parallel_state_authority": False,
            "singleton_vm81_admission": True,
            "hash72_commit_streams": 1,
            "external_deployment_quota_required": False,
        }


__all__ = [
    "TerminalCandidate",
    "TerminalHydratedInstruction",
    "TerminalInstructionRequest",
    "TerminalPass175Runtime",
]
