"""Canonical virtual firmware and BIOS image for Pass 175."""
from __future__ import annotations

from base64 import b64encode
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from .runtime import Pass175Error
from .x86_64 import ExactX86Decoder, ExactX86Instruction


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


@dataclass(frozen=True)
class FirmwareStage:
    sequence: int
    name: str
    decoder_mode: str
    exact_bytes_b64: str
    expected_mnemonic: str
    privilege_allowed: bool
    device: str | None
    device_operation: str | None
    device_payload: dict[str, Any]
    stage_identity_sha256: str

    @property
    def exact_bytes(self) -> bytes:
        from base64 import b64decode
        return b64decode(self.exact_bytes_b64, validate=True)


@dataclass(frozen=True)
class FirmwareImage:
    schema: str
    version: str
    rom_base: int
    rom_size: int
    entry_point: int
    reset_vector: int
    exact_image_b64: str
    exact_image_sha256: str
    stage_manifest_root_sha256: str
    image_root_sha256: str
    stages: tuple[FirmwareStage, ...]

    @property
    def exact_image(self) -> bytes:
        from base64 import b64decode
        return b64decode(self.exact_image_b64, validate=True)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalFirmwareBuilder:
    """Build a deterministic 64 KiB virtual BIOS image and boot-stage manifest."""

    ROM_BASE = 0xF0000
    ROM_SIZE = 0x10000
    RESET_VECTOR = 0xFFFF0
    ENTRY_POINT = ROM_BASE

    # Firmware instruction bytes are retained exactly.  They form a minimal
    # bootstrap sequence over the supported decoder corpus, not host-native code.
    STAGE_DEFINITIONS: tuple[tuple[str, str, bytes, str, bool, str | None, str | None, dict[str, Any]], ...] = (
        ("RESET_VECTOR", "REAL_16", bytes.fromhex("ea 00 00 00 f0"), "JMP_FAR", True, None, None, {}),
        ("INTERRUPTS_MASKED", "LONG_64", bytes.fromhex("fa"), "CLI", True, "INTERRUPT", "ACK", {}),
        ("FEATURE_DISCOVERY", "LONG_64", bytes.fromhex("0f a2"), "CPUID", False, None, None, {}),
        ("POST_BEGIN", "LONG_64", bytes.fromhex("e6 80"), "OUT", False, "PORT_IO", "OUT", {"port": 0x80, "value": 0x10}),
        ("SERIAL_READY", "LONG_64", bytes.fromhex("e6 e9"), "OUT", False, "SERIAL", "WRITE", {"data_b64": "SEhTIFAxNzUgQklPUwo="}),
        ("MEMORY_DISCOVERY", "LONG_64", bytes.fromhex("90"), "NOP", False, "MEMORY", "PROTECT", {"address": 0, "permission": "RW"}),
        ("TIMER_READY", "LONG_64", bytes.fromhex("0f 31"), "RDTSC", False, "TIMER", "TICK", {"amount": 1}),
        ("INTERRUPT_CONTROLLER_READY", "LONG_64", bytes.fromhex("90"), "NOP", False, "INTERRUPT", "RAISE", {"vector": 32}),
        ("KEYBOARD_READY", "LONG_64", bytes.fromhex("e4 60"), "IN", False, "KEYBOARD", "INGRESS", {"data_b64": ""}),
        ("POINTER_READY", "LONG_64", bytes.fromhex("90"), "NOP", False, "POINTER", "INGRESS", {"x": 0, "y": 0, "buttons": 0}),
        ("BLOCK_READY", "LONG_64", bytes.fromhex("90"), "NOP", False, "BLOCK", "READ", {"offset": 0, "length": 512}),
        ("FRAMEBUFFER_READY", "LONG_64", bytes.fromhex("90"), "NOP", False, "FRAMEBUFFER", "WRITE_PIXEL", {"x": 0, "y": 0, "value": 0}),
        ("AUDIO_READY", "LONG_64", bytes.fromhex("90"), "NOP", False, "AUDIO", "WRITE_SAMPLES", {"samples": [0]}),
        ("NETWORK_READY", "LONG_64", bytes.fromhex("90"), "NOP", False, "NETWORK", "INGRESS", {"packet_b64": ""}),
        ("LOADER_READY", "LONG_64", bytes.fromhex("90"), "NOP", False, "LOADER", "LOAD", {"name": "hhs-pass174-system-image", "image_b64": ""}),
        ("INTERRUPTS_ENABLED", "LONG_64", bytes.fromhex("fb"), "STI", True, None, None, {}),
        ("POST_COMPLETE", "LONG_64", bytes.fromhex("e6 80"), "OUT", False, "PORT_IO", "OUT", {"port": 0x80, "value": 0xFF}),
        ("BOOT_READY", "LONG_64", bytes.fromhex("f4"), "HLT", True, None, None, {}),
    )

    def __init__(self, decoder: ExactX86Decoder | None = None) -> None:
        self.decoder = decoder or ExactX86Decoder()

    def build(self) -> FirmwareImage:
        image = bytearray(self.ROM_SIZE)
        stages: list[FirmwareStage] = []
        cursor = 0
        stage_roots = []
        for sequence, definition in enumerate(self.STAGE_DEFINITIONS):
            name, mode, exact, expected, allow_privileged, device, operation, payload = definition
            decoded = self.decoder.decode(exact, decoder_mode=mode)
            if decoded.mnemonic != expected:
                raise Pass175Error("HHS_P175_FIRMWARE_DECODE_MISMATCH", name)
            if decoded.reencode() != exact:
                raise Pass175Error("HHS_P175_FIRMWARE_ENCODING_MISMATCH", name)
            if name == "RESET_VECTOR":
                offset = self.RESET_VECTOR - self.ROM_BASE
            else:
                offset = cursor
                cursor += len(exact)
            if offset + len(exact) > self.ROM_SIZE:
                raise Pass175Error("HHS_P175_FIRMWARE_ROM_OVERFLOW")
            image[offset:offset + len(exact)] = exact
            stage_body = {
                "sequence": sequence,
                "name": name,
                "decoder_mode": mode,
                "exact_bytes_b64": b64encode(exact).decode("ascii"),
                "exact_bytes_sha256": decoded.exact_bytes_sha256,
                "retained_encoding_identity_sha256": decoded.retained_encoding_identity_sha256,
                "expected_mnemonic": expected,
                "privilege_allowed": allow_privileged,
                "device": device,
                "device_operation": operation,
                "device_payload": payload,
            }
            stage_identity = sha256(
                b"HHS-P175-FIRMWARE-STAGE\0" + _canonical(stage_body)
            ).hexdigest()
            stage_roots.append(stage_identity)
            stages.append(FirmwareStage(
                sequence=sequence,
                name=name,
                decoder_mode=mode,
                exact_bytes_b64=b64encode(exact).decode("ascii"),
                expected_mnemonic=expected,
                privilege_allowed=allow_privileged,
                device=device,
                device_operation=operation,
                device_payload=dict(payload),
                stage_identity_sha256=stage_identity,
            ))
        image_hash = sha256(image).hexdigest()
        stage_root = sha256(
            b"HHS-P175-FIRMWARE-STAGE-ROOT\0"
            + b"".join(bytes.fromhex(value) for value in stage_roots)
        ).hexdigest()
        body = {
            "schema": "HHS_PASS_175_CANONICAL_FIRMWARE_IMAGE_V1",
            "version": "1.0.0",
            "rom_base": self.ROM_BASE,
            "rom_size": self.ROM_SIZE,
            "entry_point": self.ENTRY_POINT,
            "reset_vector": self.RESET_VECTOR,
            "exact_image_sha256": image_hash,
            "stage_manifest_root_sha256": stage_root,
        }
        image_root = sha256(
            b"HHS-P175-FIRMWARE-IMAGE\0" + _canonical(body) + bytes(image)
        ).hexdigest()
        return FirmwareImage(
            schema=body["schema"],
            version=body["version"],
            rom_base=self.ROM_BASE,
            rom_size=self.ROM_SIZE,
            entry_point=self.ENTRY_POINT,
            reset_vector=self.RESET_VECTOR,
            exact_image_b64=b64encode(image).decode("ascii"),
            exact_image_sha256=image_hash,
            stage_manifest_root_sha256=stage_root,
            image_root_sha256=image_root,
            stages=tuple(stages),
        )

    def verify(self, image: FirmwareImage) -> dict[str, Any]:
        rebuilt = self.build()
        if image != rebuilt:
            raise Pass175Error("HHS_P175_FIRMWARE_RECONSTRUCTION_MISMATCH")
        data = image.exact_image
        reset_offset = image.reset_vector - image.rom_base
        if data[reset_offset:reset_offset + 5] != bytes.fromhex("ea 00 00 00 f0"):
            raise Pass175Error("HHS_P175_FIRMWARE_RESET_VECTOR")
        return {
            "schema": "HHS_PASS_175_FIRMWARE_VERIFICATION_V1",
            "classification": "HHS_PASS_175_FIRMWARE_IMAGE_VERIFIED",
            "image_root_sha256": image.image_root_sha256,
            "exact_image_sha256": image.exact_image_sha256,
            "stage_manifest_root_sha256": image.stage_manifest_root_sha256,
            "stages": len(image.stages),
            "rom_base": image.rom_base,
            "rom_size": image.rom_size,
            "entry_point": image.entry_point,
            "reset_vector": image.reset_vector,
            "deterministic_reconstruction": True,
        }


__all__ = [
    "CanonicalFirmwareBuilder",
    "FirmwareImage",
    "FirmwareStage",
]
