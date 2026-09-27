"""Pass 220 Python2: Python/Mojo class registration into Pass 219 RNA cell wall.

This layer builds deterministic class descriptors and invokes the exact C ABI.
It does not inspect live Python class objects and does not mutate VM81 state.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Sequence

from hhs_installer.canonical import hash216

SCHEMA = "HHS_PASS_220_PYTHON2_RNA_CLASS_REGISTRATION_V1"
MAX_MEMBERS = 7
HASH216_BYTES = 216
SHA256_BYTES = 32

MEMBER_CONSTRUCTOR = 1
MEMBER_FIELD = 2
MEMBER_METHOD = 3
MEMBER_CLASS_METHOD = 4
MEMBER_STATIC_METHOD = 5

ROLE_TOEHOLD = 0x0001
ROLE_HAIRPIN = 0x0002


class PythonRNAClassRegistrationError(RuntimeError):
    pass


class _RNADomain(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("domain_id", ctypes.c_uint32),
        ("complement_domain_id", ctypes.c_uint32),
        ("role_flags", ctypes.c_uint32),
        ("phase_basis", ctypes.c_uint8),
        ("orientation", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 2),
    ]


class _RNAStrand(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("strand_id", ctypes.c_uint32),
        ("domain_count", ctypes.c_uint32),
        ("domains", _RNADomain * 8),
    ]


class _RNARule(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("rule_id", ctypes.c_uint32),
        ("kind", ctypes.c_uint32),
        ("source_domain_id", ctypes.c_uint32),
        ("target_domain_id", ctypes.c_uint32),
    ]


class _RNAProgram(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("program_id", ctypes.c_uint32),
        ("rule_count", ctypes.c_uint32),
        ("rules", _RNARule * 16),
    ]


class _Member(ctypes.Structure):
    _fields_ = [
        ("member_id", ctypes.c_uint32),
        ("kind", ctypes.c_uint32),
        ("role_flags", ctypes.c_uint32),
        ("phase_basis", ctypes.c_uint8),
        ("orientation", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 2),
    ]


class _Descriptor(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("module_id", ctypes.c_uint32),
        ("class_id", ctypes.c_uint32),
        ("constructor_member_id", ctypes.c_uint32),
        ("member_count", ctypes.c_uint32),
        ("source_sha256", ctypes.c_uint8 * SHA256_BYTES),
        ("class_identity_hash216", ctypes.c_char * (HASH216_BYTES + 1)),
        ("members", _Member * MAX_MEMBERS),
    ]


class _Registration(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("module_id", ctypes.c_uint32),
        ("class_id", ctypes.c_uint32),
        ("constructor_member_id", ctypes.c_uint32),
        ("member_count", ctypes.c_uint32),
        ("registration_fingerprint64", ctypes.c_uint64),
        ("source_sha256", ctypes.c_uint8 * SHA256_BYTES),
        ("class_identity_hash216", ctypes.c_char * (HASH216_BYTES + 1)),
        ("strand", _RNAStrand),
        ("program", _RNAProgram),
        ("members", _Member * MAX_MEMBERS),
        ("rna_cell_wall_bound", ctypes.c_uint8),
        ("registration_only", ctypes.c_uint8),
        ("class_identity_bound", ctypes.c_uint8),
        ("source_identity_bound", ctypes.c_uint8),
        ("vm81_mutation_authority", ctypes.c_uint8),
        ("hash72_commit_authority", ctypes.c_uint8),
        ("hash216_persistence_authority", ctypes.c_uint8),
        ("floating_point_authority", ctypes.c_uint8),
    ]


@dataclass(frozen=True)
class PythonClassMemberSpec:
    name: str
    kind: int
    phase_basis: int
    orientation: int = 0
    role_flags: int = 0


@dataclass(frozen=True)
class PythonRNAClassRegistration:
    schema: str
    module_name: str
    class_name: str
    module_id: int
    class_id: int
    constructor_member_id: int
    member_names: tuple[str, ...]
    member_ids: tuple[int, ...]
    member_kinds: tuple[int, ...]
    source_sha256: str
    class_identity_hash216: str
    registration_fingerprint64: int
    strand_id: int
    strand_domain_ids: tuple[int, ...]
    program_id: int
    program_rule_count: int
    rna_cell_wall_bound: bool
    registration_only: bool
    vm81_mutation_authority: bool
    hash72_commit_authority: bool
    hash216_persistence_authority: bool
    floating_point_authority: bool


def _stable_u32(domain: str, value: str) -> int:
    digest = sha256(f"{domain}\0{value}".encode("utf-8")).digest()
    result = int.from_bytes(digest[:4], "big")
    return result or 1


def _member_identity(module_name: str, class_name: str, member_name: str) -> int:
    return _stable_u32(
        "HHS-P220-PYTHON2-MEMBER",
        f"{module_name}.{class_name}.{member_name}",
    )


def _class_identity(
    module_name: str,
    class_name: str,
    source_sha256_hex: str,
    members: Sequence[PythonClassMemberSpec],
) -> str:
    value = hash216(
        {
            "schema": SCHEMA,
            "module": module_name,
            "class": class_name,
            "source_sha256": source_sha256_hex,
            "members": [
                {
                    "name": member.name,
                    "kind": member.kind,
                    "phase_basis": member.phase_basis,
                    "orientation": member.orientation,
                    "role_flags": member.role_flags,
                }
                for member in members
            ],
        },
        domain="HHS-P220-PYTHON2-RNA-CLASS",
    )
    if len(value) != HASH216_BYTES or not value.isascii():
        raise PythonRNAClassRegistrationError(
            "HHS_PYTHON2_HASH216_IDENTITY_INVALID"
        )
    return value


class PythonRNAClassRegistry:
    def __init__(self, exact_abi_library: str | Path):
        self.library_path = str(Path(exact_abi_library))
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.hhs_exact_pass220_python_rna_class_version.restype = ctypes.c_uint32
        self._lib.hhs_exact_pass220_python_rna_class_register.argtypes = [
            ctypes.POINTER(_Descriptor),
            ctypes.POINTER(_Registration),
        ]
        self._lib.hhs_exact_pass220_python_rna_class_register.restype = ctypes.c_int
        self._lib.hhs_exact_pass220_python_rna_class_validate_registration.argtypes = [
            ctypes.POINTER(_Registration),
        ]
        self._lib.hhs_exact_pass220_python_rna_class_validate_registration.restype = ctypes.c_int
        self.version = int(self._lib.hhs_exact_pass220_python_rna_class_version())

    def register(
        self,
        *,
        module_name: str,
        class_name: str,
        source_text: str,
        members: Iterable[PythonClassMemberSpec],
    ) -> PythonRNAClassRegistration:
        member_specs = tuple(members)
        if not module_name or not class_name:
            raise PythonRNAClassRegistrationError(
                "HHS_PYTHON2_MODULE_AND_CLASS_REQUIRED"
            )
        if not 1 <= len(member_specs) <= MAX_MEMBERS:
            raise PythonRNAClassRegistrationError(
                "HHS_PYTHON2_MEMBER_COUNT_OUT_OF_RANGE"
            )
        constructor_specs = tuple(
            member for member in member_specs
            if member.kind == MEMBER_CONSTRUCTOR
        )
        if len(constructor_specs) != 1:
            raise PythonRNAClassRegistrationError(
                "HHS_PYTHON2_EXACTLY_ONE_CONSTRUCTOR_REQUIRED"
            )
        if len({member.name for member in member_specs}) != len(member_specs):
            raise PythonRNAClassRegistrationError(
                "HHS_PYTHON2_DUPLICATE_MEMBER_NAME"
            )

        source_bytes = source_text.encode("utf-8")
        source_digest = sha256(source_bytes).digest()
        source_hex = source_digest.hex()
        identity = _class_identity(
            module_name,
            class_name,
            source_hex,
            member_specs,
        )

        descriptor = _Descriptor()
        descriptor.struct_size = ctypes.sizeof(_Descriptor)
        descriptor.version = self.version
        descriptor.module_id = _stable_u32(
            "HHS-P220-PYTHON2-MODULE",
            module_name,
        )
        descriptor.class_id = _stable_u32(
            "HHS-P220-PYTHON2-CLASS",
            f"{module_name}.{class_name}",
        )

        member_ids = tuple(
            _member_identity(module_name, class_name, member.name)
            for member in member_specs
        )
        if len(set(member_ids)) != len(member_ids):
            raise PythonRNAClassRegistrationError(
                "HHS_PYTHON2_MEMBER_ID_COLLISION"
            )
        if descriptor.class_id in member_ids:
            raise PythonRNAClassRegistrationError(
                "HHS_PYTHON2_CLASS_MEMBER_ID_COLLISION"
            )

        constructor_index = next(
            index for index, member in enumerate(member_specs)
            if member.kind == MEMBER_CONSTRUCTOR
        )
        descriptor.constructor_member_id = member_ids[constructor_index]
        descriptor.member_count = len(member_specs)
        for index, byte in enumerate(source_digest):
            descriptor.source_sha256[index] = byte
        descriptor.class_identity_hash216 = identity.encode("ascii")

        for index, (member, member_id) in enumerate(
            zip(member_specs, member_ids)
        ):
            native = descriptor.members[index]
            native.member_id = member_id
            native.kind = member.kind
            native.phase_basis = member.phase_basis
            native.orientation = member.orientation
            native.role_flags = member.role_flags

        registration = _Registration()
        status = int(
            self._lib.hhs_exact_pass220_python_rna_class_register(
                ctypes.byref(descriptor),
                ctypes.byref(registration),
            )
        )
        if status != 0:
            raise PythonRNAClassRegistrationError(
                f"HHS_PYTHON2_RNA_REGISTRATION_REJECTED:{status}"
            )
        validation = int(
            self._lib.hhs_exact_pass220_python_rna_class_validate_registration(
                ctypes.byref(registration)
            )
        )
        if validation != 0:
            raise PythonRNAClassRegistrationError(
                f"HHS_PYTHON2_RNA_REGISTRATION_INVALID:{validation}"
            )

        return PythonRNAClassRegistration(
            schema=SCHEMA,
            module_name=module_name,
            class_name=class_name,
            module_id=int(registration.module_id),
            class_id=int(registration.class_id),
            constructor_member_id=int(registration.constructor_member_id),
            member_names=tuple(member.name for member in member_specs),
            member_ids=member_ids,
            member_kinds=tuple(member.kind for member in member_specs),
            source_sha256=bytes(registration.source_sha256).hex(),
            class_identity_hash216=bytes(
                registration.class_identity_hash216
            ).split(b"\0", 1)[0].decode("ascii"),
            registration_fingerprint64=int(
                registration.registration_fingerprint64
            ),
            strand_id=int(registration.strand.strand_id),
            strand_domain_ids=tuple(
                int(registration.strand.domains[index].domain_id)
                for index in range(registration.strand.domain_count)
            ),
            program_id=int(registration.program.program_id),
            program_rule_count=int(registration.program.rule_count),
            rna_cell_wall_bound=bool(registration.rna_cell_wall_bound),
            registration_only=bool(registration.registration_only),
            vm81_mutation_authority=bool(registration.vm81_mutation_authority),
            hash72_commit_authority=bool(registration.hash72_commit_authority),
            hash216_persistence_authority=bool(
                registration.hash216_persistence_authority
            ),
            floating_point_authority=bool(
                registration.floating_point_authority
            ),
        )


def python2_rna_class_registration_contract() -> dict:
    return {
        "schema": SCHEMA,
        "pass219_rna_rule_grammar": "1.11",
        "pass219_rna_admission_lowering": "1.12",
        "native_cpp_cell_wall_class": "hhs::rna::PythonClassRegistration",
        "maximum_registered_members": MAX_MEMBERS,
        "class_domain_plus_members_must_fit_rna_strand": True,
        "registration_program_executes_state_transition": False,
        "instance_transition_requires_rna_admission": True,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_authority": False,
        "python_runtime_class_registry_is_parallel_authority": False,
        "mojo_future_binding_uses_same_class_identity": True,
    }


__all__ = [
    "MEMBER_CLASS_METHOD",
    "MEMBER_CONSTRUCTOR",
    "MEMBER_FIELD",
    "MEMBER_METHOD",
    "MEMBER_STATIC_METHOD",
    "PythonClassMemberSpec",
    "PythonRNAClassRegistration",
    "PythonRNAClassRegistrationError",
    "PythonRNAClassRegistry",
    "python2_rna_class_registration_contract",
]
