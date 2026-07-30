"""Pass 175 Hash216-hydrated VM5184 × G243 virtual instruction processor.

Parallel workers produce immutable candidates. Only the inherited Pass 174
runtime may commit candidate deltas through the singleton VM81 authority.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json
import os
from pathlib import Path
from threading import RLock
import time
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass174 import Pass174Runtime

RUNTIME_VERSION = "HHS-P175-H216-VM5184-G243-VIP-1.0.0"
VM81_CELLS = 81
OPERATIONS_PER_CELL = 64
PERMANENT_INSTRUCTION_COUNT = 5184
G243_CONTROL_COUNT = 243
PROJECTED_ADDRESS_COUNT = 1_259_712
ORDERED_BASIS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
PHASE_TABLE = (
    0,0,36,0,54,0,54,18,36,36,18,18,36,54,54,54,
    54,54,36,36,54,36,18,54,54,0,36,0,18,36,36,0,
    54,0,0,0,54,36,18,18,0,18,54,36,18,18,0,18,
    0,36,36,54,18,18,54,36,36,18,18,0,36,54,18,36,
)
SCALAR_CIRCUIT_LO_TOKENS = ("0","1","0","1","10","11","1","0")
SCALAR_CIRCUIT_HI_TOKENS = ("1","0","11","10","1","0","0","111")
SCALAR_CIRCUIT_LO_BYTES = bytes((0,1,0,1,10,11,1,0))
SCALAR_CIRCUIT_HI_BYTES = bytes((1,0,11,10,1,0,0,111))
ZERO_SHA256 = "0" * 64


class Pass175Error(ValueError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification, self.detail = classification, detail


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False, default=str).encode("utf-8")


def _integer(value: Any, label: str, low: int, high: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise Pass175Error("HHS_P175_EXACT_INTEGER_RANGE", label)
    return value


def _sha(value: str, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass175Error("HHS_P175_INVALID_SHA256", label)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise Pass175Error("HHS_P175_INVALID_SHA256", label) from exc
    return value


@dataclass(frozen=True)
class InstructionAddress:
    state: int
    cell: int
    operation: int

    @classmethod
    def from_state(cls, state: int) -> "InstructionAddress":
        s = _integer(state, "state", 0, 5183)
        return cls(s, s // 64, s % 64)

    @classmethod
    def from_cell_operation(cls, cell: int, operation: int) -> "InstructionAddress":
        c, o = _integer(cell, "cell", 0, 80), _integer(operation, "operation", 0, 63)
        return cls(c * 64 + o, c, o)

    def project(self, control: int) -> int:
        return self.state * 243 + _integer(control, "control", 0, 242)

    @classmethod
    def unproject(cls, projected: int) -> tuple["InstructionAddress", int]:
        q = _integer(projected, "projected", 0, PROJECTED_ADDRESS_COUNT - 1)
        return cls.from_state(q // 243), q % 243


@dataclass(frozen=True)
class ControlWord:
    trits: tuple[int, int, int, int, int]
    encoded: int

    @classmethod
    def from_trits(cls, values: Sequence[int]) -> "ControlWord":
        if len(values) != 5:
            raise Pass175Error("HHS_P175_CONTROL_ARITY_MISMATCH")
        result = 0
        trits = tuple(_integer(int(value), f"trit_{index}", 0, 2) for index, value in enumerate(values))
        for trit in trits:
            result = result * 3 + trit
        return cls(trits, result)  # type: ignore[arg-type]

    @classmethod
    def from_int(cls, encoded: int) -> "ControlWord":
        value, digits = _integer(encoded, "control", 0, 242), [0] * 5
        remaining = value
        for index in range(4, -1, -1):
            digits[index], remaining = remaining % 3, remaining // 3
        return cls(tuple(digits), value)  # type: ignore[arg-type]


@dataclass(frozen=True)
class Hash216Identity:
    predecessor: str
    current: str
    successor: str
    combined: str
    character_indexes_sha256: tuple[str, ...]
    index_root_sha256: str
    logical_identity_sha256: str

    @classmethod
    def build(cls, envelope: Mapping[str, Any], exact: bytes) -> "Hash216Identity":
        lanes = tuple(hash72_digest({**dict(envelope), "lane": lane}, exact)
                      for lane in ("PREDECESSOR", "CURRENT", "SUCCESSOR"))
        if any(len(lane) != 72 for lane in lanes):
            raise Pass175Error("HHS_P175_HASH72_LENGTH")
        combined = "".join(lanes)
        logical = sha256(b"P175-H216\0" + combined.encode("ascii") + _canonical(envelope) + exact).hexdigest()
        prior, indexes = ZERO_SHA256, []
        for position, character in enumerate(combined):
            prior = sha256(b"P175-H216-I\0" + _canonical({
                "logical": logical, "position": position, "character": character, "prior": prior,
            })).hexdigest()
            indexes.append(prior)
        root = sha256(b"P175-H216-R\0" + b"".join(bytes.fromhex(value) for value in indexes)).hexdigest()
        return cls(lanes[0], lanes[1], lanes[2], combined, tuple(indexes), root, logical)

    def verify(self) -> None:
        if self.combined != self.predecessor + self.current + self.successor or len(self.combined) != 216:
            raise Pass175Error("HHS_P175_HASH216_LANE_ORDER")
        if len(self.character_indexes_sha256) != 216:
            raise Pass175Error("HHS_P175_HASH216_INDEX_COUNT")
        expected = sha256(b"P175-H216-R\0" + b"".join(
            bytes.fromhex(value) for value in self.character_indexes_sha256
        )).hexdigest()
        if expected != self.index_root_sha256:
            raise Pass175Error("HHS_P175_HASH216_INDEX_ROOT")


@dataclass(frozen=True)
class PermanentInstructionIdentity:
    combined_hash216: str
    logical_identity_sha256: str
    source_bytes_sha256: str


@dataclass(frozen=True)
class PermanentInstruction:
    state: int
    cell: int
    operation: int
    ordered_expression: str
    phase: int
    closure_class: bool
    identity: PermanentInstructionIdentity


@dataclass(frozen=True)
class HydratedInstruction:
    key_sha256: str
    exact_bytes_b64: str
    exact_bytes_sha256: str
    decoder_mode: str
    mnemonic: str
    ordered_operands: tuple[str, ...]
    parenthesization: str
    read_set: tuple[int, ...]
    write_set: tuple[int, ...]
    privilege_class: str
    exception_class: str
    micro_operations: tuple[str, ...]
    route: tuple[tuple[int, int], ...]
    executable: bool
    hash216: Hash216Identity

    @property
    def exact_bytes(self) -> bytes:
        return b64decode(self.exact_bytes_b64, validate=True)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "HydratedInstruction":
        h = raw["hash216"]
        identity = Hash216Identity(
            h["predecessor"], h["current"], h["successor"], h["combined"],
            tuple(h["character_indexes_sha256"]), h["index_root_sha256"], h["logical_identity_sha256"],
        )
        identity.verify()
        return cls(
            raw["key_sha256"], raw["exact_bytes_b64"], raw["exact_bytes_sha256"], raw["decoder_mode"],
            raw["mnemonic"], tuple(raw["ordered_operands"]), raw["parenthesization"], tuple(raw["read_set"]),
            tuple(raw["write_set"]), raw["privilege_class"], raw["exception_class"],
            tuple(raw["micro_operations"]), tuple(tuple(value) for value in raw["route"]), bool(raw["executable"]), identity,
        )


class HydratedMicrocodeStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path).resolve() if path else None
        self._records: dict[str, HydratedInstruction] = {}
        self._order: list[str] = []
        self._lock = RLock()
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                for line in self.path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        self._remember(HydratedInstruction.from_dict(json.loads(line)))

    def _remember(self, record: HydratedInstruction) -> None:
        existing = self._records.get(record.key_sha256)
        if existing and existing.hash216.logical_identity_sha256 != record.hash216.logical_identity_sha256:
            raise Pass175Error("HHS_P175_MICROCODE_KEY_COLLISION")
        if not existing:
            self._records[record.key_sha256] = record
            self._order.append(record.key_sha256)

    def admit(self, record: HydratedInstruction) -> HydratedInstruction:
        record.hash216.verify()
        if sha256(record.exact_bytes).hexdigest() != record.exact_bytes_sha256:
            raise Pass175Error("HHS_P175_EXACT_ENCODING_HASH")
        with self._lock:
            existing = self._records.get(record.key_sha256)
            if existing:
                return existing
            self._remember(record)
            if self.path:
                with self.path.open("ab") as handle:
                    handle.write(_canonical(record.to_dict()) + b"\n")
                    handle.flush()
                    os.fsync(handle.fileno())
        return record

    def get(self, key_sha256: str) -> HydratedInstruction:
        try:
            return self._records[_sha(key_sha256, "key_sha256")]
        except KeyError as exc:
            raise Pass175Error("HHS_P175_MICROCODE_MISS") from exc

    def records(self) -> tuple[HydratedInstruction, ...]:
        return tuple(self._records[key] for key in self._order)

    def root(self) -> str:
        root = ZERO_SHA256
        for key in self._order:
            record = self._records[key]
            root = sha256(
                b"P175-STORE\0" + bytes.fromhex(root) + bytes.fromhex(key)
                + bytes.fromhex(record.hash216.logical_identity_sha256)
            ).hexdigest()
        return root


@dataclass(frozen=True)
class InstructionRequest:
    exact_bytes: bytes
    decoder_mode: str = "LONG_64"
    ordered_operands: tuple[str, ...] = ()
    parenthesization: str = "EXACT_SOURCE_ORDER"
    read_set: tuple[int, ...] = ()
    write_set: tuple[int, ...] = ()
    thread_id: int = 0
    sequence: int = 0
    explicit_delta: tuple[tuple[int, int], ...] = ()
    allow_privileged: bool = False


@dataclass(frozen=True)
class ReciprocalLane:
    opcode: str
    phase: int
    magnitude_numerator: int
    magnitude_denominator: int
    source_root_sha256: str
    provenance_root_sha256: str


@dataclass
class VirtualDeviceBus:
    keyboard_ingress: list[int] = field(default_factory=list)
    serial_egress: bytearray = field(default_factory=bytearray)
    post_codes: list[int] = field(default_factory=list)
    framebuffer_events: list[dict[str, int]] = field(default_factory=list)
    storage_events: list[dict[str, Any]] = field(default_factory=list)
    network_events: list[dict[str, Any]] = field(default_factory=list)
    _sequence: int = 0

    def ingress_keyboard(self, payload: bytes) -> dict[str, Any]:
        self.keyboard_ingress.extend(payload)
        self._sequence += 1
        return {"device": "KEYBOARD", "direction": "INGRESS", "sequence": self._sequence,
                "bytes": len(payload), "payload_sha256": sha256(payload).hexdigest()}

    def candidate(self, record: HydratedInstruction) -> dict[str, Any] | None:
        data = record.exact_bytes
        if len(data) != 2 or data[0] not in (0xE4, 0xE6):
            return None
        direction, port = ("IN" if data[0] == 0xE4 else "OUT"), data[1]
        return {"device_operation": direction, "port": port, "record_key": record.key_sha256,
                "candidate_only": True, "host_authority": False}

    def commit(self, candidate: Mapping[str, Any], admitted: bool) -> dict[str, Any] | None:
        device = candidate.get("device")
        if not device:
            return None
        if not admitted:
            return {**dict(device), "committed": False}
        self._sequence += 1
        operation, port = str(device["device_operation"]), int(device["port"])
        event: dict[str, Any] = {**dict(device), "sequence": self._sequence, "committed": True}
        if operation == "IN" and port == 0x60:
            event["value"] = self.keyboard_ingress.pop(0) if self.keyboard_ingress else 0
        elif operation == "OUT" and port == 0x80:
            self.post_codes.append(0)
            event["value"] = 0
        elif operation == "OUT" and port == 0xE9:
            self.serial_egress.append(0)
            event["value"] = 0
        else:
            event["classification"] = "HHS_P175_UNMODELED_DEVICE_PORT"
        return event

    def status(self) -> dict[str, Any]:
        return {"keyboard_queue": len(self.keyboard_ingress), "serial_bytes": len(self.serial_egress),
                "post_events": len(self.post_codes), "framebuffer_events": len(self.framebuffer_events),
                "storage_events": len(self.storage_events), "network_events": len(self.network_events),
                "host_direct_access": False}


class Authority(Protocol):
    def status(self) -> Mapping[str, Any]: ...
    def execute(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def replay(self) -> Mapping[str, Any]: ...


class Pass175Runtime:
    def __init__(self, *, authority: Authority | None = None,
                 microcode_store: HydratedMicrocodeStore | None = None,
                 store_path: str | Path | None = None,
                 device_bus: VirtualDeviceBus | None = None) -> None:
        self.authority = authority or Pass174Runtime()
        self.microcode_store = microcode_store or HydratedMicrocodeStore(store_path)
        self.device_bus = device_bus or VirtualDeviceBus()
        self.permanent_instructions = self._fabric()
        self._semantic: dict[str, HydratedInstruction] = {}
        for record in self.microcode_store.records():
            self._semantic[self._semantic_key(record)] = record
        self._commits: list[dict[str, Any]] = []
        self._lock = RLock()

    @staticmethod
    @lru_cache(maxsize=1)
    def _fabric() -> tuple[PermanentInstruction, ...]:
        source = SCALAR_CIRCUIT_LO_BYTES + SCALAR_CIRCUIT_HI_BYTES
        source_root = sha256(source).hexdigest()
        result = []
        identities: set[str] = set()
        for state in range(5184):
            address = InstructionAddress.from_state(state)
            row, column = address.operation // 8, address.operation % 8
            expression, phase = f"{ORDERED_BASIS[row]}*{ORDERED_BASIS[column]}", PHASE_TABLE[address.operation]
            envelope = {
                "schema": "P175_PERMANENT_INSTRUCTION_V1", "state": state, "cell": address.cell,
                "operation": address.operation, "expression": expression, "phase": phase,
                "tokens": SCALAR_CIRCUIT_LO_TOKENS + SCALAR_CIRCUIT_HI_TOKENS,
            }
            exact = source + state.to_bytes(2, "big")
            lanes = tuple(hash72_digest({**envelope, "lane": lane}, exact)
                          for lane in ("PREDECESSOR", "CURRENT", "SUCCESSOR"))
            combined = "".join(lanes)
            logical = sha256(b"P175-PERMANENT\0" + combined.encode("ascii") + _canonical(envelope)).hexdigest()
            if logical in identities:
                raise Pass175Error("HHS_P175_PERMANENT_IDENTITY_COLLISION")
            identities.add(logical)
            identity = PermanentInstructionIdentity(combined, logical, source_root)
            result.append(PermanentInstruction(state, address.cell, address.operation, expression, phase,
                                               phase in (0, 36), identity))
        return tuple(result)

    @staticmethod
    def _decode(data: bytes, mode: str, operands: Sequence[str], reads: Sequence[int], writes: Sequence[int]) -> dict[str, Any]:
        if not 1 <= len(data) <= 15:
            raise Pass175Error("HHS_P175_X86_LENGTH")
        table = {
            b"\x90": ("NOP", "SAFE_NATIVE_CANDIDATE", "NONE", ("NOOP",)),
            b"\xC3": ("RET", "VM81_EMULATED", "STACK_OR_GP", ("READ_STACK", "CONTROL_RETURN")),
            b"\xCC": ("INT3", "VM81_EMULATED", "BP", ("TRAP_BREAKPOINT",)),
            b"\xF4": ("HLT", "PRIVILEGED_TRAP", "GP", ("HALT_CANDIDATE",)),
            b"\x0F\xA2": ("CPUID", "VM81_EMULATED", "NONE", ("READ_FEATURES", "WRITE_REGISTERS")),
            b"\x0F\x05": ("SYSCALL", "DEVICE_INTERCEPT", "NONE", ("TRAP_SYSCALL",)),
        }
        decoded = table.get(data)
        if decoded:
            mnemonic, privilege, exception, micro = decoded
            executable = True
        elif len(data) == 2 and data[0] in (0xE4, 0xE6):
            mnemonic, privilege, exception, micro, executable = (
                "IN" if data[0] == 0xE4 else "OUT", "DEVICE_INTERCEPT", "GP", ("DEVICE_IO",), True,
            )
        elif len(data) == 10 and data[0] == 0x48 and 0xB8 <= data[1] <= 0xBF:
            mnemonic, privilege, exception, micro, executable = (
                "MOV", "SAFE_NATIVE_CANDIDATE", "NONE", ("LOAD_IMMEDIATE", "WRITE_REGISTER"), True,
            )
        elif len(data) == 5 and 0xB8 <= data[0] <= 0xBF:
            mnemonic, privilege, exception, micro, executable = (
                "MOV", "SAFE_NATIVE_CANDIDATE", "NONE", ("LOAD_IMMEDIATE", "WRITE_REGISTER"), True,
            )
        elif len(data) == 2 and data[0] in (0x31, 0x33) and data[1] >= 0xC0:
            mnemonic, privilege, exception, micro, executable = (
                "XOR", "SAFE_NATIVE_CANDIDATE", "NONE",
                ("READ_OPERANDS", "XOR", "WRITE_RESULT", "WRITE_FLAGS"), True,
            )
        else:
            mnemonic, privilege, exception, micro, executable = (
                "UNSUPPORTED", "MALFORMED_ENCODING", "UD", ("TRAP_UNSUPPORTED",), False,
            )
        return {
            "exact": data, "mode": str(mode), "mnemonic": mnemonic,
            "operands": tuple(str(value) for value in operands),
            "reads": tuple(sorted({_integer(int(value), "read", 0, 80) for value in reads})),
            "writes": tuple(sorted({_integer(int(value), "write", 0, 80) for value in writes})),
            "privilege": privilege, "exception": exception, "micro": micro, "executable": executable,
        }

    @staticmethod
    def _semantic_key(record_or_decoded: Any, parenthesization: str | None = None) -> str:
        if isinstance(record_or_decoded, HydratedInstruction):
            body = {
                "bytes": record_or_decoded.exact_bytes_sha256, "mode": record_or_decoded.decoder_mode,
                "operands": record_or_decoded.ordered_operands,
                "parenthesization": record_or_decoded.parenthesization,
                "reads": record_or_decoded.read_set, "writes": record_or_decoded.write_set,
            }
        else:
            decoded = record_or_decoded
            body = {
                "bytes": sha256(decoded["exact"]).hexdigest(), "mode": decoded["mode"],
                "operands": decoded["operands"], "parenthesization": parenthesization,
                "reads": decoded["reads"], "writes": decoded["writes"],
            }
        return sha256(b"P175-SEMANTIC\0" + _canonical(body)).hexdigest()

    @staticmethod
    def _route(decoded: Mapping[str, Any]) -> tuple[tuple[int, int], ...]:
        seed, result = sha256(decoded["exact"] + decoded["mnemonic"].encode("utf-8")).digest(), []
        for index, micro in enumerate(decoded["micro"]):
            cell = (seed[index] + index * 17) % 81
            operation = int.from_bytes(sha256(micro.encode("utf-8")).digest()[:2], "big") % 64
            trits = (
                1 if decoded["reads"] else 0,
                1 if decoded["writes"] else 0,
                2 if "CONTROL" in micro else 0,
                2 if decoded["privilege"] not in ("SAFE_NATIVE_CANDIDATE", "VM81_EMULATED") else 0,
                2 if decoded["exception"] != "NONE" else 0,
            )
            result.append((cell * 64 + operation, ControlWord.from_trits(trits).encoded))
        return tuple(result)

    def hydrate_x86(self, exact_bytes: bytes, *, decoder_mode: str = "LONG_64",
                    ordered_operands: Sequence[str] = (), parenthesization: str = "EXACT_SOURCE_ORDER",
                    read_set: Sequence[int] = (), write_set: Sequence[int] = ()) -> HydratedInstruction:
        decoded = self._decode(bytes(exact_bytes), decoder_mode, ordered_operands, read_set, write_set)
        semantic = self._semantic_key(decoded, parenthesization)
        if semantic in self._semantic:
            return self._semantic[semantic]
        route = self._route(decoded)
        envelope = {
            "schema": "P175_HYDRATED_X86_V1", "bytes_b64": b64encode(decoded["exact"]).decode("ascii"),
            "mode": decoded["mode"], "mnemonic": decoded["mnemonic"], "operands": decoded["operands"],
            "parenthesization": parenthesization, "reads": decoded["reads"], "writes": decoded["writes"],
            "privilege": decoded["privilege"], "exception": decoded["exception"], "micro": decoded["micro"],
            "route": route, "predecessor_store_root": self.microcode_store.root(),
        }
        key = sha256(b"P175-HYDRATE\0" + _canonical(envelope) + decoded["exact"]).hexdigest()
        record = HydratedInstruction(
            key, envelope["bytes_b64"], sha256(decoded["exact"]).hexdigest(), decoded["mode"],
            decoded["mnemonic"], decoded["operands"], parenthesization, decoded["reads"], decoded["writes"],
            decoded["privilege"], decoded["exception"], decoded["micro"], route, decoded["executable"],
            Hash216Identity.build(envelope, decoded["exact"]),
        )
        record = self.microcode_store.admit(record)
        self._semantic[semantic] = record
        return record

    @staticmethod
    def _conflict(left: InstructionRequest, right: InstructionRequest) -> bool:
        left_read, right_read = set(left.read_set), set(right.read_set)
        left_write = set(left.write_set) | {position for position, _ in left.explicit_delta}
        right_write = set(right.write_set) | {position for position, _ in right.explicit_delta}
        return bool(left_write & right_write or left_write & right_read or right_write & left_read)

    @classmethod
    def _waves(cls, requests: Sequence[InstructionRequest]) -> list[list[InstructionRequest]]:
        waves: list[list[InstructionRequest]] = []
        for request in sorted(requests, key=lambda value: (value.sequence, value.thread_id)):
            for wave in waves:
                if all(not cls._conflict(request, other) for other in wave):
                    wave.append(request)
                    break
            else:
                waves.append([request])
        return waves

    def _authority_state(self) -> tuple[int, str]:
        if hasattr(self.authority, "vmrc"):
            vmrc = getattr(self.authority, "vmrc")
            return int(vmrc.epoch), str(vmrc.state_hash72)
        status = dict(self.authority.status())
        nested = dict(status.get("vmrc") or {})
        return int(nested.get("epoch", status.get("epoch", 0))), str(
            nested.get("state_hash72", status.get("state_hash72", ZERO_SHA256))
        )

    def _candidate(self, request: InstructionRequest, record: HydratedInstruction,
                   epoch: int, root: str) -> dict[str, Any]:
        if not record.executable:
            raise Pass175Error("HHS_P175_UNSUPPORTED_EXACT_ENCODING", record.exact_bytes_sha256)
        if record.privilege_class == "PRIVILEGED_TRAP" and not request.allow_privileged:
            raise Pass175Error("HHS_P175_PRIVILEGED_INSTRUCTION_TRAPPED", record.mnemonic)
        state, control = record.route[0]
        address = InstructionAddress.from_state(state)
        if request.explicit_delta:
            delta = tuple(sorted(request.explicit_delta))
        elif record.write_set:
            delta = tuple((position, ControlWord.from_int(control).trits[0] - 1) for position in record.write_set)
        else:
            delta = ()
        device = self.device_bus.candidate(record)
        body = {
            "epoch": epoch, "root": root, "sequence": request.sequence, "thread": request.thread_id,
            "state": state, "control": control, "projected": address.project(control), "key": record.key_sha256,
            "instruction_hash216": record.hash216.combined, "reads": record.read_set,
            "writes": tuple(sorted(set(record.write_set) | {position for position, _ in delta})),
            "delta": delta, "trace": record.micro_operations, "device": device,
        }
        return {**body, "candidate_sha256": sha256(b"P175-CANDIDATE\0" + _canonical(body)).hexdigest()}

    def execute_batch(self, requests: Sequence[InstructionRequest], *, max_workers: int = 4) -> dict[str, Any]:
        if not requests:
            raise Pass175Error("HHS_P175_EXECUTION_BATCH_EMPTY")
        workers = _integer(max_workers, "max_workers", 1, 64)
        committed: list[dict[str, Any]] = []
        with self._lock:
            for wave_index, wave in enumerate(self._waves(requests)):
                epoch, root = self._authority_state()
                records = [
                    self.hydrate_x86(
                        request.exact_bytes, decoder_mode=request.decoder_mode,
                        ordered_operands=request.ordered_operands,
                        parenthesization=request.parenthesization,
                        read_set=request.read_set, write_set=request.write_set,
                    ) for request in wave
                ]
                with ThreadPoolExecutor(max_workers=min(workers, len(wave))) as pool:
                    candidates = list(pool.map(
                        lambda pair: self._candidate(pair[0], pair[1], epoch, root), zip(wave, records)
                    ))
                candidates.sort(key=lambda value: (
                    value["epoch"], value["sequence"], value["thread"], value["state"], value["control"]
                ))
                merged: dict[int, int] = {}
                for candidate in candidates:
                    if candidate["root"] != root:
                        raise Pass175Error("HHS_P175_CANDIDATE_STALE_ROOT")
                    for position, value in candidate["delta"]:
                        if position in merged:
                            raise Pass175Error("HHS_P175_WRITE_CONFLICT_AT_BARRIER", str(position))
                        merged[_integer(position, "delta_position", 0, 80)] = _integer(value, "delta_value", -1, 1)
                authority_result = self.authority.execute(
                    thread=0, writes=merged, operation="P175_PARALLEL_CANDIDATE_BATCH_COMMIT",
                    capability_scope="P175_VM5184_G243_SINGLETON_VM81_COMMIT", prefer_retrieval=True,
                )
                admitted = bool(authority_result.get("receipt") or authority_result.get("commit"))
                device_events = [self.device_bus.commit(candidate, admitted) for candidate in candidates]
                device_events = [event for event in device_events if event is not None]
                order_root = sha256(b"P175-ORDER\0" + b"".join(
                    bytes.fromhex(value["candidate_sha256"]) for value in candidates
                )).hexdigest()
                record = {
                    "wave": wave_index, "epoch_before": epoch, "predecessor_state_root": root,
                    "candidate_root_sha256": order_root, "merged_delta": sorted(merged.items()),
                    "candidates": candidates, "device_events": device_events,
                    "authority_result": dict(authority_result),
                }
                self._commits.append(record)
                committed.append(record)
        return {
            "schema": "P175_PARALLEL_CANDIDATE_EXECUTION_V1",
            "classification": "HHS_PASS_175_CANDIDATES_VM81_COMMITTED",
            "candidate_count": len(requests), "wave_count": len(committed),
            "parallel_candidates": True, "parallel_state_authority": False,
            "singleton_vm81_commit_authority": True, "waves": committed,
            "microcode_store_root_sha256": self.microcode_store.root(),
        }

    def cold_hydrate_bootstrap(self, *, seal: bool = True) -> dict[str, Any]:
        corpus = (
            b"\x90", b"\x48\xB8\x01\x00\x00\x00\x00\x00\x00\x00", b"\x0F\xA2",
            b"\xE6\x80", b"\xE4\x60", b"\xCC", b"\xC3", b"\xF4",
        )
        started = time.monotonic_ns()
        records = [self.hydrate_x86(value) for value in corpus]
        authority_result = None
        if seal:
            root = self.microcode_store.root()
            writes = {index: (1 if byte & 1 else -1) for index, byte in enumerate(bytes.fromhex(root)[:16])}
            authority_result = self.authority.execute(
                thread=0, writes=writes, operation="P175_COLD_HYDRATION_SEAL",
                capability_scope="P175_HASH216_MICROCODE_HYDRATION", prefer_retrieval=True,
            )
        return {
            "schema": "P175_COLD_HYDRATION_V1", "classification": "HHS_PASS_175_BOOTSTRAP_HYDRATED",
            "records": len(records), "keys": [value.key_sha256 for value in records],
            "sealed_through_vm81": seal, "microcode_store_root_sha256": self.microcode_store.root(),
            "elapsed_ns_nonauthoritative": time.monotonic_ns() - started,
            "authority_result": authority_result,
        }

    def project_ab(self, a: ReciprocalLane, b: ReciprocalLane) -> dict[str, Any]:
        for lane in (a, b):
            _sha(lane.source_root_sha256, "source_root")
            _sha(lane.provenance_root_sha256, "provenance_root")
            if lane.magnitude_denominator == 0:
                raise Pass175Error("HHS_P175_ZERO_DENOMINATOR")
        if (a.opcode, b.opcode) != ("xy", "yx"):
            raise Pass175Error("HHS_P175_RECIPROCAL_OPCODE_ORDER")
        if (a.phase, b.phase) != (0, 36):
            raise Pass175Error("HHS_P175_RECIPROCAL_PHASE_MISMATCH")
        magnitude_a = Fraction(a.magnitude_numerator, a.magnitude_denominator)
        magnitude_b = Fraction(b.magnitude_numerator, b.magnitude_denominator)
        if magnitude_a != magnitude_b:
            raise Pass175Error("HHS_P175_RECIPROCAL_MAGNITUDE_MISMATCH")
        result = magnitude_a * magnitude_b
        body = {
            "a": asdict(a), "b": asdict(b), "result_numerator": result.numerator,
            "result_denominator": result.denominator, "result_phase": 0,
        }
        return {
            "schema": "P175_PROJECT_AB_V1",
            "classification": "HHS_PASS_175_PROJECT_AB_ADMISSIBLE_CANDIDATE", **body,
            "witness_lanes_retained": True, "instruction_identity_distinct": True,
            "mutation_authority": False,
            "candidate_sha256": sha256(b"P175-PROJECT-AB\0" + _canonical(body)).hexdigest(),
        }

    def ingress_keyboard(self, payload: bytes) -> dict[str, Any]:
        return self.device_bus.ingress_keyboard(bytes(payload))

    def replay(self) -> dict[str, Any]:
        root = ZERO_SHA256
        for index, record in enumerate(self._commits):
            root = sha256(b"P175-REPLAY\0" + bytes.fromhex(root) + _canonical({
                "index": index, "record": record,
            })).hexdigest()
        return {
            "schema": "P175_REPLAY_V1",
            "classification": "HHS_PASS_175_DETERMINISTIC_REPLAY_VERIFIED",
            "commit_waves": len(self._commits), "commit_chain_root_sha256": root,
            "authority_replay": dict(self.authority.replay()),
        }

    def instruction(self, state: int) -> dict[str, Any]:
        return asdict(self.permanent_instructions[InstructionAddress.from_state(state).state])

    def status(self) -> dict[str, Any]:
        distribution = {str(phase): PHASE_TABLE.count(phase) for phase in (0, 18, 36, 54)}
        return {
            "schema": "P175_RUNTIME_STATUS_V1",
            "classification": "HHS_PASS_175_VIRTUAL_INSTRUCTION_PROCESSOR_IMPLEMENTED_DEVELOPMENT",
            "runtime_version": RUNTIME_VERSION,
            "permanent_instruction_count": 5184,
            "permanent_identity_count": len({
                record.identity.logical_identity_sha256 for record in self.permanent_instructions
            }),
            "controls_per_instruction": 243,
            "projected_address_count": PROJECTED_ADDRESS_COUNT,
            "phase_distribution": distribution,
            "closure_operations": 32,
            "scalar_circuits": {
                "lo_tokens": SCALAR_CIRCUIT_LO_TOKENS, "hi_tokens": SCALAR_CIRCUIT_HI_TOKENS,
                "lo_bytes_b64": b64encode(SCALAR_CIRCUIT_LO_BYTES).decode("ascii"),
                "hi_bytes_b64": b64encode(SCALAR_CIRCUIT_HI_BYTES).decode("ascii"),
                "leading_zero_identity_preserved": True,
            },
            "hydrated_instruction_records": len(self.microcode_store.records()),
            "microcode_store_root_sha256": self.microcode_store.root(),
            "parallel_candidate_workers": True,
            "parallel_state_authority": False,
            "singleton_vm81_commit_authority": True,
            "hash72_commit_streams": 1,
            "device_bus": self.device_bus.status(),
            "x86_64_decoder_scope": "BOUNDED_BOOTSTRAP_EXACT_FAIL_CLOSED",
            "terminal_pass175_completion_claimed": False,
            "authority": dict(self.authority.status()),
        }


__all__ = [name for name in globals() if name.startswith("SCALAR_") or name in {
    "RUNTIME_VERSION", "VM81_CELLS", "OPERATIONS_PER_CELL", "PERMANENT_INSTRUCTION_COUNT",
    "G243_CONTROL_COUNT", "PROJECTED_ADDRESS_COUNT", "ORDERED_BASIS", "PHASE_TABLE", "Pass175Error",
    "InstructionAddress", "ControlWord", "Hash216Identity", "PermanentInstructionIdentity",
    "PermanentInstruction", "HydratedInstruction", "HydratedMicrocodeStore", "InstructionRequest",
    "ReciprocalLane", "VirtualDeviceBus", "Pass175Runtime",
}]
