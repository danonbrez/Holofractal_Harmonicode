"""Exact, fail-closed x86_64 architectural decoder for Pass 175.

The decoder preserves the complete input encoding.  It does not execute guest
bytes on the host.  Supported forms are lowered into ordered VM81 micro-
operations; unsupported or privileged forms remain inspectable and trapped.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping, Sequence

from .runtime import Pass175Error

LEGACY_PREFIXES: Mapping[int, str] = {
    0xF0: "LOCK",
    0xF2: "REPNE",
    0xF3: "REP",
    0x2E: "CS",
    0x36: "SS",
    0x3E: "DS",
    0x26: "ES",
    0x64: "FS",
    0x65: "GS",
    0x66: "OPERAND_SIZE",
    0x67: "ADDRESS_SIZE",
}
PRIVILEGE_CLASSES = {
    "SAFE_NATIVE_CANDIDATE",
    "VM81_EMULATED",
    "PRIVILEGED_TRAP",
    "DEVICE_INTERCEPT",
    "FEATURE_UNAVAILABLE",
    "MALFORMED_ENCODING",
    "FORBIDDEN_HOST_ESCAPE",
}
REGISTER_NAMES_64 = (
    "RAX", "RCX", "RDX", "RBX", "RSP", "RBP", "RSI", "RDI",
    "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15",
)
REGISTER_NAMES_32 = (
    "EAX", "ECX", "EDX", "EBX", "ESP", "EBP", "ESI", "EDI",
    "R8D", "R9D", "R10D", "R11D", "R12D", "R13D", "R14D", "R15D",
)
FLAG_ALL = ("CF", "PF", "AF", "ZF", "SF", "OF")
FLAG_LOGIC = ("CF", "PF", "ZF", "SF", "OF")


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
class ModRM:
    byte: int
    mod: int
    reg: int
    rm: int
    reg_extended: int
    rm_extended: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class SIB:
    byte: int
    scale: int
    index: int
    base: int
    index_extended: int
    base_extended: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class ExactX86Instruction:
    exact_bytes_b64: str
    exact_bytes_sha256: str
    retained_encoding_identity_sha256: str
    decoder_mode: str
    length: int
    prefix_bytes_b64: str
    prefix_kinds: tuple[str, ...]
    rex_byte: int | None
    vex_bytes_b64: str
    evex_bytes_b64: str
    opcode_map: str
    opcode_bytes_b64: str
    mnemonic: str
    ordered_operands: tuple[str, ...]
    operand_size: int
    address_size: int
    modrm: ModRM | None
    sib: SIB | None
    displacement_b64: str
    immediate_b64: str
    read_set: tuple[str, ...]
    write_set: tuple[str, ...]
    flags_read: tuple[str, ...]
    flags_written: tuple[str, ...]
    privilege_class: str
    exception_class: str
    feature_gates: tuple[str, ...]
    micro_operations: tuple[str, ...]
    executable: bool
    decode_complete: bool
    trailing_bytes_b64: str = ""

    @property
    def exact_bytes(self) -> bytes:
        return b64decode(self.exact_bytes_b64, validate=True)

    def reencode(self) -> bytes:
        """Return the retained exact encoding without normalization."""
        return self.exact_bytes

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        return result


@dataclass(frozen=True)
class InstructionSpec:
    mnemonic: str
    has_modrm: bool = False
    immediate: str = ""
    privilege: str = "SAFE_NATIVE_CANDIDATE"
    exception: str = "NONE"
    features: tuple[str, ...] = ("X86_64_BASE",)
    micro: tuple[str, ...] = ()
    flags_read: tuple[str, ...] = ()
    flags_written: tuple[str, ...] = ()
    operand_pattern: str = ""


PRIMARY: dict[int, InstructionSpec] = {
    0x90: InstructionSpec("NOP", micro=("NOOP",)),
    0xC3: InstructionSpec("RET", privilege="VM81_EMULATED", exception="STACK_OR_GP",
                          micro=("READ_STACK", "CONTROL_RETURN"), operand_pattern="RET"),
    0xCC: InstructionSpec("INT3", privilege="VM81_EMULATED", exception="BP",
                          micro=("TRAP_BREAKPOINT",)),
    0xF4: InstructionSpec("HLT", privilege="PRIVILEGED_TRAP", exception="GP",
                          micro=("HALT_CANDIDATE",)),
    0xFA: InstructionSpec("CLI", privilege="PRIVILEGED_TRAP", exception="GP",
                          micro=("INTERRUPT_MASK_CLEAR",), flags_written=("IF",)),
    0xFB: InstructionSpec("STI", privilege="PRIVILEGED_TRAP", exception="GP",
                          micro=("INTERRUPT_MASK_SET",), flags_written=("IF",)),
    0x9C: InstructionSpec("PUSHFQ", privilege="VM81_EMULATED", exception="STACK_OR_GP",
                          micro=("READ_FLAGS", "WRITE_STACK"), flags_read=("RFLAGS",)),
    0x9D: InstructionSpec("POPFQ", privilege="PRIVILEGED_TRAP", exception="GP",
                          micro=("READ_STACK", "WRITE_FLAGS"), flags_written=("RFLAGS",)),
    0xE8: InstructionSpec("CALL", immediate="REL32", privilege="VM81_EMULATED",
                          exception="STACK_OR_GP", micro=("READ_PC", "WRITE_STACK", "CONTROL_RELATIVE"),
                          operand_pattern="REL"),
    0xE9: InstructionSpec("JMP", immediate="REL32", privilege="VM81_EMULATED",
                          micro=("CONTROL_RELATIVE",), operand_pattern="REL"),
    0xEB: InstructionSpec("JMP", immediate="REL8", privilege="VM81_EMULATED",
                          micro=("CONTROL_RELATIVE",), operand_pattern="REL"),
    0xE4: InstructionSpec("IN", immediate="IMM8", privilege="DEVICE_INTERCEPT", exception="GP",
                          micro=("DEVICE_PORT_READ", "WRITE_ACCUMULATOR"), operand_pattern="PORT_AL"),
    0xE5: InstructionSpec("IN", immediate="IMM8", privilege="DEVICE_INTERCEPT", exception="GP",
                          micro=("DEVICE_PORT_READ", "WRITE_ACCUMULATOR"), operand_pattern="PORT_EAX"),
    0xE6: InstructionSpec("OUT", immediate="IMM8", privilege="DEVICE_INTERCEPT", exception="GP",
                          micro=("READ_ACCUMULATOR", "DEVICE_PORT_WRITE"), operand_pattern="PORT_AL"),
    0xE7: InstructionSpec("OUT", immediate="IMM8", privilege="DEVICE_INTERCEPT", exception="GP",
                          micro=("READ_ACCUMULATOR", "DEVICE_PORT_WRITE"), operand_pattern="PORT_EAX"),
    0x89: InstructionSpec("MOV", has_modrm=True, micro=("READ_REG", "WRITE_RM"),
                          operand_pattern="RM_REG"),
    0x8B: InstructionSpec("MOV", has_modrm=True, micro=("READ_RM", "WRITE_REG"),
                          operand_pattern="REG_RM"),
    0x8D: InstructionSpec("LEA", has_modrm=True, micro=("CALCULATE_EFFECTIVE_ADDRESS", "WRITE_REG"),
                          operand_pattern="REG_MEM"),
    0x87: InstructionSpec("XCHG", has_modrm=True, micro=("READ_REG", "READ_RM", "ATOMIC_SWAP"),
                          operand_pattern="RM_REG"),
    0x31: InstructionSpec("XOR", has_modrm=True,
                          micro=("READ_RM", "READ_REG", "XOR", "WRITE_RM", "WRITE_FLAGS"),
                          flags_written=FLAG_LOGIC, operand_pattern="RM_REG"),
    0x33: InstructionSpec("XOR", has_modrm=True,
                          micro=("READ_REG", "READ_RM", "XOR", "WRITE_REG", "WRITE_FLAGS"),
                          flags_written=FLAG_LOGIC, operand_pattern="REG_RM"),
    0x01: InstructionSpec("ADD", has_modrm=True,
                          micro=("READ_RM", "READ_REG", "ADD_EXACT", "WRITE_RM", "WRITE_FLAGS"),
                          flags_written=FLAG_ALL, operand_pattern="RM_REG"),
    0x03: InstructionSpec("ADD", has_modrm=True,
                          micro=("READ_REG", "READ_RM", "ADD_EXACT", "WRITE_REG", "WRITE_FLAGS"),
                          flags_written=FLAG_ALL, operand_pattern="REG_RM"),
    0x29: InstructionSpec("SUB", has_modrm=True,
                          micro=("READ_RM", "READ_REG", "SUB_EXACT", "WRITE_RM", "WRITE_FLAGS"),
                          flags_written=FLAG_ALL, operand_pattern="RM_REG"),
    0x2B: InstructionSpec("SUB", has_modrm=True,
                          micro=("READ_REG", "READ_RM", "SUB_EXACT", "WRITE_REG", "WRITE_FLAGS"),
                          flags_written=FLAG_ALL, operand_pattern="REG_RM"),
    0x39: InstructionSpec("CMP", has_modrm=True,
                          micro=("READ_RM", "READ_REG", "SUB_EXACT", "WRITE_FLAGS"),
                          flags_written=FLAG_ALL, operand_pattern="RM_REG"),
    0x3B: InstructionSpec("CMP", has_modrm=True,
                          micro=("READ_REG", "READ_RM", "SUB_EXACT", "WRITE_FLAGS"),
                          flags_written=FLAG_ALL, operand_pattern="REG_RM"),
    0x21: InstructionSpec("AND", has_modrm=True,
                          micro=("READ_RM", "READ_REG", "AND", "WRITE_RM", "WRITE_FLAGS"),
                          flags_written=FLAG_LOGIC, operand_pattern="RM_REG"),
    0x23: InstructionSpec("AND", has_modrm=True,
                          micro=("READ_REG", "READ_RM", "AND", "WRITE_REG", "WRITE_FLAGS"),
                          flags_written=FLAG_LOGIC, operand_pattern="REG_RM"),
    0x09: InstructionSpec("OR", has_modrm=True,
                          micro=("READ_RM", "READ_REG", "OR", "WRITE_RM", "WRITE_FLAGS"),
                          flags_written=FLAG_LOGIC, operand_pattern="RM_REG"),
    0x0B: InstructionSpec("OR", has_modrm=True,
                          micro=("READ_REG", "READ_RM", "OR", "WRITE_REG", "WRITE_FLAGS"),
                          flags_written=FLAG_LOGIC, operand_pattern="REG_RM"),
    0x85: InstructionSpec("TEST", has_modrm=True,
                          micro=("READ_RM", "READ_REG", "AND", "WRITE_FLAGS"),
                          flags_written=FLAG_LOGIC, operand_pattern="RM_REG"),
    0xC7: InstructionSpec("MOV", has_modrm=True, immediate="IMM32",
                          micro=("READ_IMMEDIATE", "WRITE_RM"), operand_pattern="RM_IMM"),
    0x81: InstructionSpec("ALU_GROUP", has_modrm=True, immediate="IMM32",
                          micro=("READ_RM", "READ_IMMEDIATE", "GROUP_ALU_EXACT", "WRITE_RESULT", "WRITE_FLAGS"),
                          flags_written=FLAG_ALL, operand_pattern="RM_IMM"),
    0x83: InstructionSpec("ALU_GROUP", has_modrm=True, immediate="IMM8",
                          micro=("READ_RM", "READ_IMMEDIATE", "GROUP_ALU_EXACT", "WRITE_RESULT", "WRITE_FLAGS"),
                          flags_written=FLAG_ALL, operand_pattern="RM_IMM"),
    0xFF: InstructionSpec("GROUP5", has_modrm=True, privilege="VM81_EMULATED",
                          exception="STACK_OR_GP", micro=("GROUP5_CONTROL_OR_ARITHMETIC",),
                          operand_pattern="GROUP5"),
}
SECONDARY: dict[int, InstructionSpec] = {
    0x05: InstructionSpec("SYSCALL", privilege="DEVICE_INTERCEPT",
                          micro=("TRAP_SYSCALL",), features=("X86_64_BASE", "SYSCALL")),
    0x0B: InstructionSpec("UD2", privilege="VM81_EMULATED", exception="UD",
                          micro=("TRAP_INVALID_OPCODE",)),
    0x20: InstructionSpec("MOV_FROM_CR", has_modrm=True, privilege="PRIVILEGED_TRAP",
                          exception="GP", micro=("READ_CONTROL_REGISTER", "WRITE_GPR"),
                          operand_pattern="REG_CR"),
    0x22: InstructionSpec("MOV_TO_CR", has_modrm=True, privilege="PRIVILEGED_TRAP",
                          exception="GP", micro=("READ_GPR", "WRITE_CONTROL_REGISTER"),
                          operand_pattern="CR_REG"),
    0x31: InstructionSpec("RDTSC", privilege="VM81_EMULATED",
                          micro=("READ_VIRTUAL_TSC", "WRITE_EDX_EAX"), features=("X86_64_BASE", "TSC")),
    0xA2: InstructionSpec("CPUID", privilege="VM81_EMULATED",
                          micro=("READ_VIRTUAL_FEATURES", "WRITE_REGISTERS")),
    0xAF: InstructionSpec("IMUL", has_modrm=True,
                          micro=("READ_REG", "READ_RM", "MUL_SIGNED_EXACT", "WRITE_REG", "WRITE_FLAGS"),
                          flags_written=("CF", "OF"), operand_pattern="REG_RM"),
    0xB6: InstructionSpec("MOVZX", has_modrm=True, micro=("READ_RM8", "ZERO_EXTEND", "WRITE_REG"),
                          operand_pattern="REG_RM"),
    0xB7: InstructionSpec("MOVZX", has_modrm=True, micro=("READ_RM16", "ZERO_EXTEND", "WRITE_REG"),
                          operand_pattern="REG_RM"),
    0xBE: InstructionSpec("MOVSX", has_modrm=True, micro=("READ_RM8", "SIGN_EXTEND", "WRITE_REG"),
                          operand_pattern="REG_RM"),
    0xBF: InstructionSpec("MOVSX", has_modrm=True, micro=("READ_RM16", "SIGN_EXTEND", "WRITE_REG"),
                          operand_pattern="REG_RM"),
    0x01: InstructionSpec("SYSTEM_GROUP", has_modrm=True, privilege="PRIVILEGED_TRAP",
                          exception="GP", micro=("SYSTEM_DESCRIPTOR_OPERATION",),
                          operand_pattern="SYSTEM_GROUP"),
    0xAE: InstructionSpec("FENCE_GROUP", has_modrm=True, privilege="VM81_EMULATED",
                          micro=("MEMORY_ORDER_BARRIER",), features=("X86_64_BASE", "SSE2"),
                          operand_pattern="FENCE"),
}


def _register_name(index: int, size: int) -> str:
    table = REGISTER_NAMES_64 if size == 64 else REGISTER_NAMES_32
    return table[index & 0xF]


def _parse_modrm(data: bytes, index: int, rex: int | None, address_size: int) -> tuple[ModRM, SIB | None, bytes, int]:
    if index >= len(data):
        raise Pass175Error("HHS_P175_X86_TRUNCATED_MODRM")
    byte = data[index]
    index += 1
    rex_r = ((rex or 0) >> 2) & 1
    rex_x = ((rex or 0) >> 1) & 1
    rex_b = (rex or 0) & 1
    mod, reg, rm = byte >> 6, (byte >> 3) & 7, byte & 7
    modrm = ModRM(byte, mod, reg, rm, reg | (rex_r << 3), rm | (rex_b << 3))
    sib = None
    displacement_size = 0
    if mod != 3 and rm == 4 and address_size in (32, 64):
        if index >= len(data):
            raise Pass175Error("HHS_P175_X86_TRUNCATED_SIB")
        sib_byte = data[index]
        index += 1
        scale, sib_index, base = sib_byte >> 6, (sib_byte >> 3) & 7, sib_byte & 7
        sib = SIB(
            sib_byte,
            scale,
            sib_index,
            base,
            sib_index | (rex_x << 3),
            base | (rex_b << 3),
        )
        if mod == 0 and base == 5:
            displacement_size = 4
    if mod == 0 and rm == 5 and sib is None:
        displacement_size = 4
    elif mod == 1:
        displacement_size = 1
    elif mod == 2:
        displacement_size = 4
    if index + displacement_size > len(data):
        raise Pass175Error("HHS_P175_X86_TRUNCATED_DISPLACEMENT")
    displacement = data[index:index + displacement_size]
    return modrm, sib, displacement, index + displacement_size


def _memory_operand(modrm: ModRM, sib: SIB | None, displacement: bytes, address_size: int) -> str:
    if modrm.mod == 3:
        return ""
    parts: list[str] = []
    if sib is not None:
        if not (modrm.mod == 0 and sib.base == 5):
            parts.append(REGISTER_NAMES_64[sib.base_extended] if address_size == 64 else REGISTER_NAMES_32[sib.base_extended])
        if sib.index != 4:
            index_name = REGISTER_NAMES_64[sib.index_extended] if address_size == 64 else REGISTER_NAMES_32[sib.index_extended]
            parts.append(f"{index_name}*{1 << sib.scale}")
    elif not (modrm.mod == 0 and modrm.rm == 5):
        parts.append(REGISTER_NAMES_64[modrm.rm_extended] if address_size == 64 else REGISTER_NAMES_32[modrm.rm_extended])
    else:
        parts.append("RIP" if address_size == 64 else "EIP")
    if displacement:
        parts.append(f"DISP:{displacement.hex()}")
    return "MEM[" + "+".join(parts or ["ABSOLUTE"]) + "]"


def _operands(spec: InstructionSpec, opcode: int, operand_size: int, modrm: ModRM | None,
              sib: SIB | None, displacement: bytes, immediate: bytes, rex: int | None,
              address_size: int) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], str]:
    pattern = spec.operand_pattern
    reads: list[str] = []
    writes: list[str] = []
    operands: list[str] = []
    mnemonic = spec.mnemonic
    if 0xB8 <= opcode <= 0xBF:
        register = _register_name((opcode - 0xB8) | (((rex or 0) & 1) << 3), operand_size)
        imm = f"IMM:{immediate.hex()}"
        operands = [register, imm]
        reads = [imm]
        writes = [register]
    elif 0x50 <= opcode <= 0x57:
        register = _register_name((opcode - 0x50) | (((rex or 0) & 1) << 3), 64)
        mnemonic = "PUSH"
        operands = [register]
        reads = [register, "RSP"]
        writes = ["RSP", "STACK"]
    elif 0x58 <= opcode <= 0x5F:
        register = _register_name((opcode - 0x58) | (((rex or 0) & 1) << 3), 64)
        mnemonic = "POP"
        operands = [register]
        reads = ["RSP", "STACK"]
        writes = ["RSP", register]
    elif 0x70 <= opcode <= 0x7F:
        mnemonic = f"JCC_{opcode & 0xF:X}"
        operands = [f"REL:{immediate.hex()}"]
        reads = ["RFLAGS", "RIP"]
        writes = ["RIP"]
    elif pattern == "REL":
        operands = [f"REL:{immediate.hex()}"]
        reads = ["RIP"]
        writes = ["RIP"]
        if mnemonic == "CALL":
            reads.append("RSP")
            writes.extend(("RSP", "STACK"))
    elif pattern in ("PORT_AL", "PORT_EAX"):
        accumulator = "AL" if pattern.endswith("AL") else "EAX"
        port = f"PORT:{int.from_bytes(immediate, 'little')}"
        if mnemonic == "IN":
            operands = [accumulator, port]
            reads = [port]
            writes = [accumulator]
        else:
            operands = [port, accumulator]
            reads = [port, accumulator]
            writes = ["DEVICE_EGRESS"]
    elif pattern == "RET":
        reads = ["RSP", "STACK"]
        writes = ["RSP", "RIP"]
    elif modrm is not None:
        reg = _register_name(modrm.reg_extended, operand_size)
        rm = _register_name(modrm.rm_extended, operand_size) if modrm.mod == 3 else _memory_operand(
            modrm, sib, displacement, address_size
        )
        if pattern == "RM_REG":
            operands = [rm, reg]
            reads = [rm, reg]
            writes = [rm] if mnemonic not in ("CMP", "TEST") else ["RFLAGS"]
        elif pattern in ("REG_RM", "REG_MEM"):
            operands = [reg, rm]
            reads = [rm] if mnemonic in ("MOV", "MOVZX", "MOVSX", "LEA") else [reg, rm]
            writes = [reg]
        elif pattern == "RM_IMM":
            imm = f"IMM:{immediate.hex()}"
            operands = [rm, imm]
            reads = [imm] if mnemonic == "MOV" else [rm, imm]
            writes = [rm]
        elif pattern == "REG_CR":
            cr = f"CR{modrm.reg_extended}"
            operands = [reg, cr]
            reads = [cr]
            writes = [reg]
        elif pattern == "CR_REG":
            cr = f"CR{modrm.reg_extended}"
            operands = [cr, reg]
            reads = [reg]
            writes = [cr]
        elif pattern == "GROUP5":
            extension = modrm.reg
            names = {0: "INC", 1: "DEC", 2: "CALL", 4: "JMP", 6: "PUSH"}
            mnemonic = names.get(extension, "GROUP5_UNSUPPORTED")
            operands = [rm]
            reads = [rm]
            if extension in (0, 1):
                writes = [rm, "RFLAGS"]
            elif extension == 2:
                reads.extend(("RSP", "RIP"))
                writes = ["RSP", "STACK", "RIP"]
            elif extension == 4:
                writes = ["RIP"]
            elif extension == 6:
                reads.append("RSP")
                writes = ["RSP", "STACK"]
        elif pattern == "FENCE":
            fence = {0xE8: "LFENCE", 0xF0: "MFENCE", 0xF8: "SFENCE"}.get(modrm.byte)
            mnemonic = fence or "FENCE_UNSUPPORTED"
            operands = []
            reads = ["MEMORY_ORDER"]
            writes = ["MEMORY_ORDER"]
        elif pattern == "SYSTEM_GROUP":
            extension = modrm.reg
            mnemonic = {0: "SGDT", 1: "SIDT", 2: "LGDT", 3: "LIDT"}.get(extension, "SYSTEM_GROUP")
            operands = [rm]
            reads = [rm] if extension in (2, 3) else ["DESCRIPTOR_TABLE"]
            writes = ["DESCRIPTOR_TABLE"] if extension in (2, 3) else [rm]
    return tuple(operands), tuple(dict.fromkeys(reads)), tuple(dict.fromkeys(writes)), mnemonic


class ExactX86Decoder:
    """Bounded architectural decoder with complete retained-encoding identity."""

    version = "HHS-P175-X86-DECODER-2.0.0"

    def decode(self, exact_bytes: bytes, *, decoder_mode: str = "LONG_64") -> ExactX86Instruction:
        data = bytes(exact_bytes)
        if not 1 <= len(data) <= 15:
            raise Pass175Error("HHS_P175_X86_LENGTH")
        if decoder_mode not in ("LONG_64", "COMPAT_32", "REAL_16"):
            raise Pass175Error("HHS_P175_X86_DECODER_MODE", decoder_mode)

        index = 0
        prefix_bytes = bytearray()
        prefix_kinds: list[str] = []
        rex: int | None = None
        vex = b""
        evex = b""

        while index < len(data) and data[index] in LEGACY_PREFIXES:
            prefix_bytes.append(data[index])
            prefix_kinds.append(LEGACY_PREFIXES[data[index]])
            index += 1
        if index < len(data) and 0x40 <= data[index] <= 0x4F and decoder_mode == "LONG_64":
            rex = data[index]
            prefix_bytes.append(rex)
            prefix_kinds.append("REX")
            index += 1

        if index < len(data) and data[index] == 0xC5:
            if index + 2 > len(data):
                raise Pass175Error("HHS_P175_X86_TRUNCATED_VEX2")
            vex = data[index:index + 2]
            index += 2
        elif index < len(data) and data[index] == 0xC4:
            if index + 3 > len(data):
                raise Pass175Error("HHS_P175_X86_TRUNCATED_VEX3")
            vex = data[index:index + 3]
            index += 3
        elif index < len(data) and data[index] == 0x62:
            if index + 4 > len(data):
                raise Pass175Error("HHS_P175_X86_TRUNCATED_EVEX")
            evex = data[index:index + 4]
            index += 4

        if index >= len(data):
            raise Pass175Error("HHS_P175_X86_MISSING_OPCODE")

        operand_size = 16 if decoder_mode == "REAL_16" else 32
        address_size = 16 if decoder_mode == "REAL_16" else (64 if decoder_mode == "LONG_64" else 32)
        if 0x66 in prefix_bytes:
            operand_size = 16 if operand_size != 16 else 32
        if rex is not None and rex & 0x08:
            operand_size = 64
        if 0x67 in prefix_bytes:
            address_size = 32 if address_size == 64 else (16 if address_size == 32 else 32)

        opcode_map = "PRIMARY"
        opcode_start = index
        opcode = data[index]
        index += 1
        spec: InstructionSpec | None = None

        if vex or evex:
            # Prefix and bytes are retained, but vector execution is deliberately
            # closed until a feature-specific lowering is registered.
            opcode_map = "VEX" if vex else "EVEX"
            opcode_bytes = data[opcode_start:index]
            trailing = data[index:]
            privilege = "FEATURE_UNAVAILABLE"
            feature = "AVX_OR_EVEX"
            return self._record(
                data=data,
                decoder_mode=decoder_mode,
                prefix_bytes=bytes(prefix_bytes),
                prefix_kinds=tuple(prefix_kinds),
                rex=rex,
                vex=vex,
                evex=evex,
                opcode_map=opcode_map,
                opcode_bytes=opcode_bytes,
                mnemonic="FEATURE_UNAVAILABLE",
                ordered_operands=(),
                operand_size=operand_size,
                address_size=address_size,
                modrm=None,
                sib=None,
                displacement=b"",
                immediate=b"",
                reads=(),
                writes=(),
                flags_read=(),
                flags_written=(),
                privilege=privilege,
                exception="UD_IF_FEATURE_DISABLED",
                feature_gates=(feature,),
                micro=("TRAP_FEATURE_UNAVAILABLE",),
                executable=False,
                decode_complete=False,
                trailing=trailing,
            )

        if opcode == 0x0F:
            if index >= len(data):
                raise Pass175Error("HHS_P175_X86_TRUNCATED_OPCODE_MAP")
            second = data[index]
            index += 1
            opcode_map = "0F"
            opcode = second
            if second == 0x38:
                if index >= len(data):
                    raise Pass175Error("HHS_P175_X86_TRUNCATED_0F38")
                opcode_map = "0F38"
                opcode = data[index]
                index += 1
            elif second == 0x3A:
                if index >= len(data):
                    raise Pass175Error("HHS_P175_X86_TRUNCATED_0F3A")
                opcode_map = "0F3A"
                opcode = data[index]
                index += 1
            if opcode_map == "0F":
                if 0x80 <= opcode <= 0x8F:
                    spec = InstructionSpec(
                        f"JCC_{opcode & 0xF:X}",
                        immediate="REL32",
                        privilege="VM81_EMULATED",
                        micro=("READ_FLAGS", "CONTROL_CONDITIONAL_RELATIVE"),
                        flags_read=("RFLAGS",),
                        operand_pattern="REL",
                    )
                elif 0x40 <= opcode <= 0x4F:
                    spec = InstructionSpec(
                        f"CMOVCC_{opcode & 0xF:X}",
                        has_modrm=True,
                        privilege="VM81_EMULATED",
                        micro=("READ_FLAGS", "READ_RM", "CONDITIONAL_WRITE_REG"),
                        flags_read=("RFLAGS",),
                        operand_pattern="REG_RM",
                    )
                elif 0x90 <= opcode <= 0x9F:
                    spec = InstructionSpec(
                        f"SETCC_{opcode & 0xF:X}",
                        has_modrm=True,
                        privilege="VM81_EMULATED",
                        micro=("READ_FLAGS", "CONDITIONAL_WRITE_RM8"),
                        flags_read=("RFLAGS",),
                        operand_pattern="RM_REG",
                    )
                else:
                    spec = SECONDARY.get(opcode)
        else:
            if 0xB8 <= opcode <= 0xBF:
                spec = InstructionSpec("MOV", immediate="IMM_REG", micro=("READ_IMMEDIATE", "WRITE_REGISTER"))
            elif 0x50 <= opcode <= 0x57:
                spec = InstructionSpec("PUSH", privilege="VM81_EMULATED", exception="STACK_OR_GP",
                                       micro=("READ_REGISTER", "WRITE_STACK"))
            elif 0x58 <= opcode <= 0x5F:
                spec = InstructionSpec("POP", privilege="VM81_EMULATED", exception="STACK_OR_GP",
                                       micro=("READ_STACK", "WRITE_REGISTER"))
            elif 0x70 <= opcode <= 0x7F:
                spec = InstructionSpec(
                    f"JCC_{opcode & 0xF:X}", immediate="REL8", privilege="VM81_EMULATED",
                    micro=("READ_FLAGS", "CONTROL_CONDITIONAL_RELATIVE"),
                    flags_read=("RFLAGS",), operand_pattern="REL",
                )
            elif opcode == 0xEA and decoder_mode == "REAL_16":
                spec = InstructionSpec(
                    "JMP_FAR", immediate="PTR16_16", privilege="VM81_EMULATED",
                    micro=("LOAD_CODE_SEGMENT", "CONTROL_ABSOLUTE"), operand_pattern="REL",
                )
            else:
                spec = PRIMARY.get(opcode)

        opcode_bytes = data[opcode_start:index]
        if spec is None:
            return self._record(
                data=data,
                decoder_mode=decoder_mode,
                prefix_bytes=bytes(prefix_bytes),
                prefix_kinds=tuple(prefix_kinds),
                rex=rex,
                vex=vex,
                evex=evex,
                opcode_map=opcode_map,
                opcode_bytes=opcode_bytes,
                mnemonic="UNSUPPORTED",
                ordered_operands=(),
                operand_size=operand_size,
                address_size=address_size,
                modrm=None,
                sib=None,
                displacement=b"",
                immediate=b"",
                reads=(),
                writes=(),
                flags_read=(),
                flags_written=(),
                privilege="MALFORMED_ENCODING",
                exception="UD",
                feature_gates=("UNREGISTERED_FORM",),
                micro=("TRAP_UNSUPPORTED",),
                executable=False,
                decode_complete=False,
                trailing=data[index:],
            )

        modrm = None
        sib = None
        displacement = b""
        if spec.has_modrm:
            modrm, sib, displacement, index = _parse_modrm(data, index, rex, address_size)

        immediate_size = 0
        if spec.immediate == "IMM8" or spec.immediate == "REL8":
            immediate_size = 1
        elif spec.immediate in ("IMM32", "REL32"):
            immediate_size = 4
        elif spec.immediate == "PTR16_16":
            immediate_size = 4
        elif spec.immediate == "IMM_REG":
            immediate_size = 8 if operand_size == 64 else (2 if operand_size == 16 else 4)
        if index + immediate_size > len(data):
            raise Pass175Error("HHS_P175_X86_TRUNCATED_IMMEDIATE")
        immediate = data[index:index + immediate_size]
        index += immediate_size
        trailing = data[index:]

        operands, reads, writes, mnemonic = _operands(
            spec, opcode, operand_size, modrm, sib, displacement, immediate, rex, address_size
        )
        privilege = spec.privilege
        executable = privilege in {
            "SAFE_NATIVE_CANDIDATE", "VM81_EMULATED", "DEVICE_INTERCEPT", "PRIVILEGED_TRAP"
        }
        decode_complete = not trailing and mnemonic not in {
            "GROUP5_UNSUPPORTED", "FENCE_UNSUPPORTED", "SYSTEM_GROUP"
        }
        if trailing:
            privilege = "MALFORMED_ENCODING"
            executable = False
            decode_complete = False
        if "LOCK" in prefix_kinds and mnemonic not in {
            "ADD", "SUB", "AND", "OR", "XOR", "XCHG", "CMP"
        }:
            privilege = "MALFORMED_ENCODING"
            executable = False
            decode_complete = False

        return self._record(
            data=data,
            decoder_mode=decoder_mode,
            prefix_bytes=bytes(prefix_bytes),
            prefix_kinds=tuple(prefix_kinds),
            rex=rex,
            vex=vex,
            evex=evex,
            opcode_map=opcode_map,
            opcode_bytes=opcode_bytes,
            mnemonic=mnemonic,
            ordered_operands=operands,
            operand_size=operand_size,
            address_size=address_size,
            modrm=modrm,
            sib=sib,
            displacement=displacement,
            immediate=immediate,
            reads=reads,
            writes=writes,
            flags_read=spec.flags_read,
            flags_written=spec.flags_written,
            privilege=privilege,
            exception=spec.exception,
            feature_gates=spec.features,
            micro=spec.micro,
            executable=executable,
            decode_complete=decode_complete,
            trailing=trailing,
        )

    def _record(self, *, data: bytes, decoder_mode: str, prefix_bytes: bytes,
                prefix_kinds: tuple[str, ...], rex: int | None, vex: bytes, evex: bytes,
                opcode_map: str, opcode_bytes: bytes, mnemonic: str,
                ordered_operands: tuple[str, ...], operand_size: int, address_size: int,
                modrm: ModRM | None, sib: SIB | None, displacement: bytes, immediate: bytes,
                reads: tuple[str, ...], writes: tuple[str, ...], flags_read: tuple[str, ...],
                flags_written: tuple[str, ...], privilege: str, exception: str,
                feature_gates: tuple[str, ...], micro: tuple[str, ...], executable: bool,
                decode_complete: bool, trailing: bytes) -> ExactX86Instruction:
        if privilege not in PRIVILEGE_CLASSES:
            raise Pass175Error("HHS_P175_X86_PRIVILEGE_CLASS", privilege)
        exact_hash = sha256(data).hexdigest()
        identity_body = {
            "schema": "HHS_P175_EXACT_X86_INSTRUCTION_V2",
            "decoder_version": self.version,
            "decoder_mode": decoder_mode,
            "exact_bytes_sha256": exact_hash,
            "prefix_bytes_b64": b64encode(prefix_bytes).decode("ascii"),
            "prefix_kinds": prefix_kinds,
            "opcode_map": opcode_map,
            "opcode_bytes_b64": b64encode(opcode_bytes).decode("ascii"),
            "mnemonic": mnemonic,
            "ordered_operands": ordered_operands,
            "operand_size": operand_size,
            "address_size": address_size,
            "modrm": modrm.to_dict() if modrm else None,
            "sib": sib.to_dict() if sib else None,
            "displacement_b64": b64encode(displacement).decode("ascii"),
            "immediate_b64": b64encode(immediate).decode("ascii"),
            "read_set": reads,
            "write_set": writes,
            "flags_read": flags_read,
            "flags_written": flags_written,
            "privilege_class": privilege,
            "exception_class": exception,
            "feature_gates": feature_gates,
            "micro_operations": micro,
            "executable": executable,
            "decode_complete": decode_complete,
            "trailing_bytes_b64": b64encode(trailing).decode("ascii"),
        }
        retained = sha256(b"HHS-P175-X86-RETAINED\0" + _canonical(identity_body) + data).hexdigest()
        return ExactX86Instruction(
            exact_bytes_b64=b64encode(data).decode("ascii"),
            exact_bytes_sha256=exact_hash,
            retained_encoding_identity_sha256=retained,
            decoder_mode=decoder_mode,
            length=len(data),
            prefix_bytes_b64=b64encode(prefix_bytes).decode("ascii"),
            prefix_kinds=prefix_kinds,
            rex_byte=rex,
            vex_bytes_b64=b64encode(vex).decode("ascii"),
            evex_bytes_b64=b64encode(evex).decode("ascii"),
            opcode_map=opcode_map,
            opcode_bytes_b64=b64encode(opcode_bytes).decode("ascii"),
            mnemonic=mnemonic,
            ordered_operands=ordered_operands,
            operand_size=operand_size,
            address_size=address_size,
            modrm=modrm,
            sib=sib,
            displacement_b64=b64encode(displacement).decode("ascii"),
            immediate_b64=b64encode(immediate).decode("ascii"),
            read_set=reads,
            write_set=writes,
            flags_read=flags_read,
            flags_written=flags_written,
            privilege_class=privilege,
            exception_class=exception,
            feature_gates=feature_gates,
            micro_operations=micro,
            executable=executable,
            decode_complete=decode_complete,
            trailing_bytes_b64=b64encode(trailing).decode("ascii"),
        )


def _hx(value: str) -> bytes:
    return bytes.fromhex(value.replace(" ", ""))


SUPPORTED_CORPUS: tuple[tuple[str, bytes, str], ...] = (
    ("nop", _hx("90"), "LONG_64"),
    ("pause", _hx("f3 90"), "LONG_64"),
    ("ret", _hx("c3"), "LONG_64"),
    ("int3", _hx("cc"), "LONG_64"),
    ("hlt", _hx("f4"), "LONG_64"),
    ("cli", _hx("fa"), "LONG_64"),
    ("sti", _hx("fb"), "LONG_64"),
    ("pushfq", _hx("9c"), "LONG_64"),
    ("popfq", _hx("9d"), "LONG_64"),
    ("cpuid", _hx("0f a2"), "LONG_64"),
    ("syscall", _hx("0f 05"), "LONG_64"),
    ("rdtsc", _hx("0f 31"), "LONG_64"),
    ("ud2", _hx("0f 0b"), "LONG_64"),
    ("mov_rax_imm64", _hx("48 b8 01 00 00 00 00 00 00 00"), "LONG_64"),
    ("mov_eax_imm32", _hx("b8 01 00 00 00"), "LONG_64"),
    ("mov_r8_imm64", _hx("49 b8 02 00 00 00 00 00 00 00"), "LONG_64"),
    ("push_rax", _hx("50"), "LONG_64"),
    ("pop_rax", _hx("58"), "LONG_64"),
    ("call_rel32", _hx("e8 00 00 00 00"), "LONG_64"),
    ("jmp_rel32", _hx("e9 00 00 00 00"), "LONG_64"),
    ("jmp_rel8", _hx("eb 00"), "LONG_64"),
    ("jz_rel8", _hx("74 00"), "LONG_64"),
    ("jnz_rel32", _hx("0f 85 00 00 00 00"), "LONG_64"),
    ("in_al_60", _hx("e4 60"), "LONG_64"),
    ("out_80_al", _hx("e6 80"), "LONG_64"),
    ("out_e9_al", _hx("e6 e9"), "LONG_64"),
    ("mov_rax_rbx", _hx("48 8b c3"), "LONG_64"),
    ("mov_mem_rax", _hx("48 89 00"), "LONG_64"),
    ("mov_rax_ripdisp", _hx("48 8b 05 78 56 34 12"), "LONG_64"),
    ("mov_rax_sib", _hx("48 8b 44 8b 10"), "LONG_64"),
    ("lea_rax_ripdisp", _hx("48 8d 05 78 56 34 12"), "LONG_64"),
    ("xor_eax_eax", _hx("31 c0"), "LONG_64"),
    ("add_rax_rbx", _hx("48 01 d8"), "LONG_64"),
    ("sub_rax_rbx", _hx("48 29 d8"), "LONG_64"),
    ("cmp_rax_rbx", _hx("48 39 d8"), "LONG_64"),
    ("and_rax_rbx", _hx("48 21 d8"), "LONG_64"),
    ("or_rax_rbx", _hx("48 09 d8"), "LONG_64"),
    ("test_rax_rax", _hx("48 85 c0"), "LONG_64"),
    ("xchg_rax_rbx", _hx("48 87 d8"), "LONG_64"),
    ("mov_mem_imm32", _hx("48 c7 00 01 00 00 00"), "LONG_64"),
    ("add_rax_imm8", _hx("48 83 c0 01"), "LONG_64"),
    ("add_rax_imm32", _hx("48 81 c0 01 00 00 00"), "LONG_64"),
    ("inc_rax", _hx("48 ff c0"), "LONG_64"),
    ("call_rax", _hx("48 ff d0"), "LONG_64"),
    ("jmp_rax", _hx("48 ff e0"), "LONG_64"),
    ("movzx_eax_al", _hx("0f b6 c0"), "LONG_64"),
    ("movsx_eax_al", _hx("0f be c0"), "LONG_64"),
    ("imul_rax_rbx", _hx("48 0f af c3"), "LONG_64"),
    ("cmovz_rax_rbx", _hx("48 0f 44 c3"), "LONG_64"),
    ("setz_al", _hx("0f 94 c0"), "LONG_64"),
    ("lfence", _hx("0f ae e8"), "LONG_64"),
    ("mfence", _hx("0f ae f0"), "LONG_64"),
    ("sfence", _hx("0f ae f8"), "LONG_64"),
    ("mov_rax_cr0", _hx("0f 20 c0"), "LONG_64"),
    ("mov_cr0_rax", _hx("0f 22 c0"), "LONG_64"),
    ("lgdt_rax", _hx("0f 01 10"), "LONG_64"),
    ("reset_far_jump", _hx("ea 00 00 00 f0"), "REAL_16"),
)

NEGATIVE_CORPUS: tuple[tuple[str, bytes, str], ...] = (
    ("truncated_rex_mov", _hx("48 b8 01"), "LONG_64"),
    ("truncated_modrm", _hx("48 8b"), "LONG_64"),
    ("truncated_sib", _hx("48 8b 04"), "LONG_64"),
    ("truncated_disp", _hx("48 8b 05 01"), "LONG_64"),
    ("vex_unavailable", _hx("c5 f8 77"), "LONG_64"),
    ("evex_unavailable", _hx("62 f1 7c 48 58 c0"), "LONG_64"),
    ("unsupported_opcode", _hx("d6"), "LONG_64"),
    ("illegal_lock_nop", _hx("f0 90"), "LONG_64"),
)


def corpus_manifest(decoder: ExactX86Decoder | None = None) -> dict[str, Any]:
    decoder = decoder or ExactX86Decoder()
    positive = []
    for name, data, mode in SUPPORTED_CORPUS:
        record = decoder.decode(data, decoder_mode=mode)
        if record.reencode() != data:
            raise Pass175Error("HHS_P175_X86_REENCODE_MISMATCH", name)
        positive.append({
            "name": name,
            "mode": mode,
            "exact_bytes_b64": b64encode(data).decode("ascii"),
            "exact_bytes_sha256": record.exact_bytes_sha256,
            "retained_encoding_identity_sha256": record.retained_encoding_identity_sha256,
            "mnemonic": record.mnemonic,
            "privilege_class": record.privilege_class,
            "exception_class": record.exception_class,
            "decode_complete": record.decode_complete,
        })
    negative = []
    for name, data, mode in NEGATIVE_CORPUS:
        try:
            record = decoder.decode(data, decoder_mode=mode)
        except Pass175Error as exc:
            negative.append({"name": name, "classification": exc.classification, "trapped": True})
        else:
            negative.append({
                "name": name,
                "classification": record.privilege_class,
                "trapped": not record.executable or not record.decode_complete,
            })
    body = {
        "schema": "HHS_PASS_175_X86_CORPUS_MANIFEST_V1",
        "decoder_version": decoder.version,
        "positive": positive,
        "negative": negative,
    }
    body["root_sha256"] = sha256(b"HHS-P175-X86-CORPUS\0" + _canonical(body)).hexdigest()
    return body


__all__ = [
    "ExactX86Decoder",
    "ExactX86Instruction",
    "InstructionSpec",
    "ModRM",
    "SIB",
    "SUPPORTED_CORPUS",
    "NEGATIVE_CORPUS",
    "corpus_manifest",
]
