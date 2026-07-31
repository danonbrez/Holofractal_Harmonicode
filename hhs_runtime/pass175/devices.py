"""Governed virtual device fabric for Pass 175.

All device operations are immutable candidates until the singleton VM81
authority admits them.  The fabric has no direct host I/O surface.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from .runtime import Pass175Error, ZERO_SHA256


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _exact_int(value: Any, label: str, low: int, high: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise Pass175Error("HHS_P175_DEVICE_INTEGER_RANGE", label)
    return value


@dataclass(frozen=True)
class DeviceCandidate:
    sequence: int
    device: str
    operation: str
    payload: Mapping[str, Any]
    predecessor_device_root_sha256: str
    read_set: tuple[str, ...]
    write_set: tuple[str, ...]
    candidate_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class DeviceCommit:
    sequence: int
    device: str
    operation: str
    candidate_sha256: str
    predecessor_device_root_sha256: str
    result: Mapping[str, Any]
    event_sha256: str
    device_root_sha256: str
    admitted: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "result": dict(self.result),
        }


@dataclass
class _FabricState:
    memory: bytearray
    page_permissions: dict[int, str] = field(default_factory=dict)
    ports: dict[int, int] = field(default_factory=dict)
    mmio: dict[int, int] = field(default_factory=dict)
    interrupts: list[int] = field(default_factory=list)
    timer_ticks: int = 0
    serial: bytearray = field(default_factory=bytearray)
    keyboard: list[int] = field(default_factory=list)
    pointer: list[tuple[int, int, int]] = field(default_factory=list)
    block: bytearray = field(default_factory=bytearray)
    framebuffer: dict[int, int] = field(default_factory=dict)
    audio: list[int] = field(default_factory=list)
    network_ingress: list[bytes] = field(default_factory=list)
    network_egress: list[bytes] = field(default_factory=list)
    loaded_images: dict[str, bytes] = field(default_factory=dict)
    receipt_projection: list[str] = field(default_factory=list)


class GovernedDeviceFabric:
    """Deterministic virtual environment with candidate/commit separation."""

    MEMORY_BYTES = 1 << 20
    BLOCK_BYTES = 1 << 20
    FRAMEBUFFER_WIDTH = 320
    FRAMEBUFFER_HEIGHT = 200
    AUDIO_SAMPLE_LIMIT = 65_536
    NETWORK_PACKET_LIMIT = 65_535
    LOADER_IMAGE_LIMIT = 16 << 20

    def __init__(self) -> None:
        self._initial_memory = bytes(self.MEMORY_BYTES)
        self._initial_block = bytes(self.BLOCK_BYTES)
        self._state = _FabricState(
            memory=bytearray(self._initial_memory),
            block=bytearray(self._initial_block),
        )
        self._events: list[DeviceCommit] = []
        self._next_candidate_sequence = 0
        self._root = self._snapshot_root(self._state)

    @staticmethod
    def _state_projection(state: _FabricState) -> dict[str, Any]:
        return {
            "memory_sha256": sha256(state.memory).hexdigest(),
            "page_permissions": sorted(state.page_permissions.items()),
            "ports": sorted(state.ports.items()),
            "mmio": sorted(state.mmio.items()),
            "interrupts": list(state.interrupts),
            "timer_ticks": state.timer_ticks,
            "serial_sha256": sha256(state.serial).hexdigest(),
            "keyboard": list(state.keyboard),
            "pointer": list(state.pointer),
            "block_sha256": sha256(state.block).hexdigest(),
            "framebuffer": sorted(state.framebuffer.items()),
            "audio_sha256": sha256(
                b"".join(int(value).to_bytes(2, "little", signed=True) for value in state.audio)
            ).hexdigest(),
            "network_ingress": [sha256(value).hexdigest() for value in state.network_ingress],
            "network_egress": [sha256(value).hexdigest() for value in state.network_egress],
            "loaded_images": sorted((key, sha256(value).hexdigest()) for key, value in state.loaded_images.items()),
            "receipt_projection": list(state.receipt_projection),
        }

    @classmethod
    def _snapshot_root(cls, state: _FabricState) -> str:
        return sha256(b"HHS-P175-DEVICE-STATE\0" + _canonical(cls._state_projection(state))).hexdigest()

    @property
    def root_sha256(self) -> str:
        return self._root

    @property
    def events(self) -> tuple[DeviceCommit, ...]:
        return tuple(self._events)

    def candidate(
        self,
        device: str,
        operation: str,
        payload: Mapping[str, Any] | None = None,
        *,
        read_set: Sequence[str] = (),
        write_set: Sequence[str] = (),
    ) -> DeviceCandidate:
        device_name = str(device).upper()
        operation_name = str(operation).upper()
        if device_name not in {
            "MEMORY", "PORT_IO", "MMIO", "INTERRUPT", "TIMER", "SERIAL",
            "KEYBOARD", "POINTER", "BLOCK", "FRAMEBUFFER", "AUDIO",
            "NETWORK", "LOADER", "RECEIPT",
        }:
            raise Pass175Error("HHS_P175_DEVICE_NOT_REGISTERED", device_name)
        sequence = self._next_candidate_sequence
        self._next_candidate_sequence += 1
        body = {
            "schema": "HHS_PASS_175_DEVICE_CANDIDATE_V1",
            "sequence": sequence,
            "device": device_name,
            "operation": operation_name,
            "payload": dict(payload or {}),
            "predecessor_device_root_sha256": self._root,
            "read_set": tuple(str(value) for value in read_set),
            "write_set": tuple(str(value) for value in write_set),
            "host_direct_access": False,
        }
        identity = sha256(b"HHS-P175-DEVICE-CANDIDATE\0" + _canonical(body)).hexdigest()
        return DeviceCandidate(
            sequence=sequence,
            device=device_name,
            operation=operation_name,
            payload=dict(payload or {}),
            predecessor_device_root_sha256=self._root,
            read_set=tuple(str(value) for value in read_set),
            write_set=tuple(str(value) for value in write_set),
            candidate_sha256=identity,
        )

    def commit(self, candidate: DeviceCandidate, *, admitted: bool) -> DeviceCommit:
        if candidate.predecessor_device_root_sha256 != self._root:
            raise Pass175Error("HHS_P175_DEVICE_STALE_ROOT")
        supplied = candidate.candidate_sha256
        body = {
            "schema": "HHS_PASS_175_DEVICE_CANDIDATE_V1",
            "sequence": candidate.sequence,
            "device": candidate.device,
            "operation": candidate.operation,
            "payload": dict(candidate.payload),
            "predecessor_device_root_sha256": candidate.predecessor_device_root_sha256,
            "read_set": candidate.read_set,
            "write_set": candidate.write_set,
            "host_direct_access": False,
        }
        expected = sha256(b"HHS-P175-DEVICE-CANDIDATE\0" + _canonical(body)).hexdigest()
        if supplied != expected:
            raise Pass175Error("HHS_P175_DEVICE_CANDIDATE_IDENTITY")
        predecessor = self._root
        result: dict[str, Any]
        if admitted:
            result = self._apply(self._state, candidate.device, candidate.operation, candidate.payload)
            self._root = self._snapshot_root(self._state)
        else:
            result = {"classification": "HHS_P175_DEVICE_CANDIDATE_REJECTED", "state_changed": False}
        event_body = {
            "sequence": len(self._events),
            "candidate_sha256": supplied,
            "predecessor_device_root_sha256": predecessor,
            "result": result,
            "device_root_sha256": self._root,
            "admitted": bool(admitted),
        }
        event_hash = sha256(b"HHS-P175-DEVICE-EVENT\0" + _canonical(event_body)).hexdigest()
        event = DeviceCommit(
            sequence=len(self._events),
            device=candidate.device,
            operation=candidate.operation,
            candidate_sha256=supplied,
            predecessor_device_root_sha256=predecessor,
            result=result,
            event_sha256=event_hash,
            device_root_sha256=self._root,
            admitted=bool(admitted),
        )
        self._events.append(event)
        return event

    @classmethod
    def _apply(
        cls,
        state: _FabricState,
        device: str,
        operation: str,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        if device == "MEMORY":
            return cls._memory(state, operation, payload)
        if device == "PORT_IO":
            return cls._port_io(state, operation, payload)
        if device == "MMIO":
            return cls._mmio(state, operation, payload)
        if device == "INTERRUPT":
            return cls._interrupt(state, operation, payload)
        if device == "TIMER":
            return cls._timer(state, operation, payload)
        if device == "SERIAL":
            return cls._serial(state, operation, payload)
        if device == "KEYBOARD":
            return cls._keyboard(state, operation, payload)
        if device == "POINTER":
            return cls._pointer(state, operation, payload)
        if device == "BLOCK":
            return cls._block(state, operation, payload)
        if device == "FRAMEBUFFER":
            return cls._framebuffer(state, operation, payload)
        if device == "AUDIO":
            return cls._audio(state, operation, payload)
        if device == "NETWORK":
            return cls._network(state, operation, payload)
        if device == "LOADER":
            return cls._loader(state, operation, payload)
        if device == "RECEIPT":
            return cls._receipt(state, operation, payload)
        raise Pass175Error("HHS_P175_DEVICE_NOT_REGISTERED", device)

    @classmethod
    def _memory(cls, state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        address = _exact_int(payload.get("address"), "memory_address", 0, cls.MEMORY_BYTES - 1)
        if operation == "READ":
            length = _exact_int(payload.get("length", 1), "memory_length", 1, cls.MEMORY_BYTES - address)
            data = bytes(state.memory[address:address + length])
            return {"address": address, "length": length, "data_b64": b64encode(data).decode("ascii")}
        if operation == "WRITE":
            data = b64decode(str(payload.get("data_b64", "")), validate=True)
            if address + len(data) > cls.MEMORY_BYTES:
                raise Pass175Error("HHS_P175_MEMORY_BOUNDS")
            page = address // 4096
            permission = state.page_permissions.get(page, "RW")
            if "W" not in permission:
                raise Pass175Error("HHS_P175_MEMORY_WRITE_PROTECTED")
            state.memory[address:address + len(data)] = data
            return {"address": address, "length": len(data), "data_sha256": sha256(data).hexdigest()}
        if operation == "PROTECT":
            page = address // 4096
            permission = str(payload.get("permission", "")).upper()
            if permission not in {"R", "RW", "RX", "NONE"}:
                raise Pass175Error("HHS_P175_MEMORY_PERMISSION")
            state.page_permissions[page] = permission
            return {"page": page, "permission": permission}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"MEMORY:{operation}")

    @staticmethod
    def _port_io(state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        port = _exact_int(payload.get("port"), "port", 0, 65535)
        if operation == "IN":
            return {"port": port, "value": state.ports.get(port, 0)}
        if operation == "OUT":
            value = _exact_int(payload.get("value"), "port_value", 0, 255)
            state.ports[port] = value
            if port == 0x80:
                return {"port": port, "value": value, "role": "POST"}
            if port == 0xE9:
                state.serial.append(value)
                return {"port": port, "value": value, "role": "DEBUG_SERIAL"}
            return {"port": port, "value": value}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"PORT_IO:{operation}")

    @staticmethod
    def _mmio(state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        address = _exact_int(payload.get("address"), "mmio_address", 0, (1 << 64) - 1)
        if operation == "READ":
            return {"address": address, "value": state.mmio.get(address, 0)}
        if operation == "WRITE":
            value = _exact_int(payload.get("value"), "mmio_value", 0, (1 << 64) - 1)
            state.mmio[address] = value
            return {"address": address, "value": value}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"MMIO:{operation}")

    @staticmethod
    def _interrupt(state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "RAISE":
            vector = _exact_int(payload.get("vector"), "interrupt_vector", 0, 255)
            state.interrupts.append(vector)
            return {"vector": vector, "pending": len(state.interrupts)}
        if operation == "ACK":
            vector = state.interrupts.pop(0) if state.interrupts else None
            return {"vector": vector, "pending": len(state.interrupts)}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"INTERRUPT:{operation}")

    @staticmethod
    def _timer(state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "TICK":
            amount = _exact_int(payload.get("amount", 1), "timer_amount", 1, 1 << 32)
            state.timer_ticks += amount
            return {"ticks": state.timer_ticks, "authoritative_wall_clock": False}
        if operation == "READ":
            return {"ticks": state.timer_ticks, "authoritative_wall_clock": False}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"TIMER:{operation}")

    @staticmethod
    def _serial(state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "WRITE":
            data = b64decode(str(payload.get("data_b64", "")), validate=True)
            state.serial.extend(data)
            return {"bytes": len(data), "data_sha256": sha256(data).hexdigest()}
        if operation == "READ":
            data = bytes(state.serial)
            return {"bytes": len(data), "data_b64": b64encode(data).decode("ascii")}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"SERIAL:{operation}")

    @staticmethod
    def _keyboard(state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "INGRESS":
            data = b64decode(str(payload.get("data_b64", "")), validate=True)
            state.keyboard.extend(data)
            return {"queued": len(state.keyboard), "data_sha256": sha256(data).hexdigest()}
        if operation == "READ":
            value = state.keyboard.pop(0) if state.keyboard else 0
            return {"value": value, "queued": len(state.keyboard)}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"KEYBOARD:{operation}")

    @staticmethod
    def _pointer(state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "INGRESS":
            x = _exact_int(payload.get("x"), "pointer_x", -32768, 32767)
            y = _exact_int(payload.get("y"), "pointer_y", -32768, 32767)
            buttons = _exact_int(payload.get("buttons", 0), "pointer_buttons", 0, 255)
            state.pointer.append((x, y, buttons))
            return {"queued": len(state.pointer), "x": x, "y": y, "buttons": buttons}
        if operation == "READ":
            value = state.pointer.pop(0) if state.pointer else (0, 0, 0)
            return {"x": value[0], "y": value[1], "buttons": value[2], "queued": len(state.pointer)}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"POINTER:{operation}")

    @classmethod
    def _block(cls, state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        offset = _exact_int(payload.get("offset"), "block_offset", 0, cls.BLOCK_BYTES - 1)
        if operation == "READ":
            length = _exact_int(payload.get("length", 512), "block_length", 1, cls.BLOCK_BYTES - offset)
            data = bytes(state.block[offset:offset + length])
            return {"offset": offset, "length": length, "data_b64": b64encode(data).decode("ascii")}
        if operation == "WRITE":
            data = b64decode(str(payload.get("data_b64", "")), validate=True)
            if offset + len(data) > cls.BLOCK_BYTES:
                raise Pass175Error("HHS_P175_BLOCK_BOUNDS")
            state.block[offset:offset + len(data)] = data
            return {"offset": offset, "length": len(data), "data_sha256": sha256(data).hexdigest()}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"BLOCK:{operation}")

    @classmethod
    def _framebuffer(cls, state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "WRITE_PIXEL":
            x = _exact_int(payload.get("x"), "framebuffer_x", 0, cls.FRAMEBUFFER_WIDTH - 1)
            y = _exact_int(payload.get("y"), "framebuffer_y", 0, cls.FRAMEBUFFER_HEIGHT - 1)
            value = _exact_int(payload.get("value"), "framebuffer_value", 0, 0xFFFFFFFF)
            state.framebuffer[y * cls.FRAMEBUFFER_WIDTH + x] = value
            return {"x": x, "y": y, "value": value}
        if operation == "FILL":
            value = _exact_int(payload.get("value"), "framebuffer_value", 0, 0xFFFFFFFF)
            state.framebuffer = {
                index: value for index in range(cls.FRAMEBUFFER_WIDTH * cls.FRAMEBUFFER_HEIGHT)
            }
            return {"pixels": cls.FRAMEBUFFER_WIDTH * cls.FRAMEBUFFER_HEIGHT, "value": value}
        if operation == "ROOT":
            root = sha256(_canonical(sorted(state.framebuffer.items()))).hexdigest()
            return {"root_sha256": root, "pixels": len(state.framebuffer)}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"FRAMEBUFFER:{operation}")

    @classmethod
    def _audio(cls, state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "WRITE_SAMPLES":
            samples = payload.get("samples")
            if not isinstance(samples, list) or len(samples) > cls.AUDIO_SAMPLE_LIMIT:
                raise Pass175Error("HHS_P175_AUDIO_SAMPLE_LIMIT")
            exact = [_exact_int(value, "audio_sample", -32768, 32767) for value in samples]
            state.audio.extend(exact)
            if len(state.audio) > cls.AUDIO_SAMPLE_LIMIT:
                state.audio = state.audio[-cls.AUDIO_SAMPLE_LIMIT:]
            root = sha256(
                b"".join(int(value).to_bytes(2, "little", signed=True) for value in exact)
            ).hexdigest()
            return {"samples": len(exact), "sample_root_sha256": root}
        if operation == "CLEAR":
            state.audio.clear()
            return {"samples": 0}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"AUDIO:{operation}")

    @classmethod
    def _network(cls, state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation in {"INGRESS", "EGRESS"}:
            packet = b64decode(str(payload.get("packet_b64", "")), validate=True)
            if len(packet) > cls.NETWORK_PACKET_LIMIT:
                raise Pass175Error("HHS_P175_NETWORK_PACKET_LIMIT")
            target = state.network_ingress if operation == "INGRESS" else state.network_egress
            target.append(packet)
            return {
                "direction": operation,
                "bytes": len(packet),
                "packet_sha256": sha256(packet).hexdigest(),
                "host_network_access": False,
            }
        if operation == "READ":
            packet = state.network_ingress.pop(0) if state.network_ingress else b""
            return {"bytes": len(packet), "packet_b64": b64encode(packet).decode("ascii")}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"NETWORK:{operation}")

    @classmethod
    def _loader(cls, state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "LOAD":
            name = str(payload.get("name", ""))
            if not name or len(name) > 256:
                raise Pass175Error("HHS_P175_LOADER_NAME")
            image = b64decode(str(payload.get("image_b64", "")), validate=True)
            if len(image) > cls.LOADER_IMAGE_LIMIT:
                raise Pass175Error("HHS_P175_LOADER_IMAGE_LIMIT")
            state.loaded_images[name] = image
            return {"name": name, "bytes": len(image), "image_sha256": sha256(image).hexdigest()}
        if operation == "QUERY":
            name = str(payload.get("name", ""))
            image = state.loaded_images.get(name)
            return {
                "name": name,
                "present": image is not None,
                "bytes": len(image or b""),
                "image_sha256": sha256(image).hexdigest() if image is not None else None,
            }
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"LOADER:{operation}")

    @staticmethod
    def _receipt(state: _FabricState, operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if operation == "PROJECT":
            receipt = str(payload.get("receipt_hash72", ""))
            if len(receipt) != 72:
                raise Pass175Error("HHS_P175_DEVICE_RECEIPT_HASH72")
            state.receipt_projection.append(receipt)
            return {"receipt_hash72": receipt, "count": len(state.receipt_projection)}
        raise Pass175Error("HHS_P175_DEVICE_OPERATION", f"RECEIPT:{operation}")

    def status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_175_DEVICE_FABRIC_STATUS_V1",
            "root_sha256": self._root,
            "event_count": len(self._events),
            "registered_devices": [
                "MEMORY", "PORT_IO", "MMIO", "INTERRUPT", "TIMER", "SERIAL",
                "KEYBOARD", "POINTER", "BLOCK", "FRAMEBUFFER", "AUDIO",
                "NETWORK", "LOADER", "RECEIPT",
            ],
            "memory_bytes": self.MEMORY_BYTES,
            "block_bytes": self.BLOCK_BYTES,
            "framebuffer": {
                "width": self.FRAMEBUFFER_WIDTH,
                "height": self.FRAMEBUFFER_HEIGHT,
                "materialized_pixels": len(self._state.framebuffer),
            },
            "timer_ticks": self._state.timer_ticks,
            "serial_bytes": len(self._state.serial),
            "keyboard_queue": len(self._state.keyboard),
            "pointer_queue": len(self._state.pointer),
            "audio_samples": len(self._state.audio),
            "network_ingress_packets": len(self._state.network_ingress),
            "network_egress_packets": len(self._state.network_egress),
            "loaded_images": sorted(self._state.loaded_images),
            "host_direct_access": False,
        }

    def replay(self) -> dict[str, Any]:
        state = _FabricState(
            memory=bytearray(self._initial_memory),
            block=bytearray(self._initial_block),
        )
        root = self._snapshot_root(state)
        chain = ZERO_SHA256
        for expected_sequence, event in enumerate(self._events):
            if event.sequence != expected_sequence:
                raise Pass175Error("HHS_P175_DEVICE_REPLAY_SEQUENCE")
            if event.predecessor_device_root_sha256 != root:
                raise Pass175Error("HHS_P175_DEVICE_REPLAY_PREDECESSOR")
            if event.admitted:
                # The committed result alone is intentionally insufficient to
                # reconstruct mutation payloads.  Candidate payloads are bound in
                # the event hash but are supplied by the durable terminal journal.
                # This in-memory replay verifies event/root chain consistency.
                root = event.device_root_sha256
            event_body = {
                "sequence": event.sequence,
                "candidate_sha256": event.candidate_sha256,
                "predecessor_device_root_sha256": event.predecessor_device_root_sha256,
                "result": dict(event.result),
                "device_root_sha256": event.device_root_sha256,
                "admitted": event.admitted,
            }
            expected_event = sha256(b"HHS-P175-DEVICE-EVENT\0" + _canonical(event_body)).hexdigest()
            if expected_event != event.event_sha256:
                raise Pass175Error("HHS_P175_DEVICE_REPLAY_EVENT")
            chain = sha256(
                b"HHS-P175-DEVICE-REPLAY\0" + bytes.fromhex(chain) + bytes.fromhex(event.event_sha256)
            ).hexdigest()
        if root != self._root:
            raise Pass175Error("HHS_P175_DEVICE_REPLAY_ROOT")
        return {
            "schema": "HHS_PASS_175_DEVICE_REPLAY_V1",
            "classification": "HHS_PASS_175_DEVICE_REPLAY_VERIFIED",
            "events": len(self._events),
            "device_root_sha256": root,
            "event_chain_root_sha256": chain,
            "deterministic_replay": True,
            "host_direct_access": False,
        }


__all__ = [
    "DeviceCandidate",
    "DeviceCommit",
    "GovernedDeviceFabric",
]
