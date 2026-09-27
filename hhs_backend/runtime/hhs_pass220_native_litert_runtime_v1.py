"""Pass 220 LiteRT1 native model/tensor registry and RNA class binding.

The external LiteRT-LM CLI/server is a compatibility/deployment membrane.
Internal model identity and tensor topology are registered in HHS-owned native
records. Model output remains advisory and canonical mutation remains outside
this layer.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from hhs_installer.canonical import hash216
from hhs_runtime.hhs_pass220_python_rna_class_registration_v1 import (
    MEMBER_CONSTRUCTOR,
    MEMBER_FIELD,
    MEMBER_METHOD,
    PythonClassMemberSpec,
    PythonRNAClassRegistry,
)

SCHEMA = "HHS_PASS_220_LITERT1_NATIVE_MODEL_RUNTIME_V1"
MAX_TENSORS = 16
MAX_RANK = 8
HASH216_BYTES = 216
SHA256_BYTES = 32

BACKEND_NATIVE = 1
BACKEND_CPU = 2
BACKEND_GPU = 3
BACKEND_NPU = 4
BACKEND_EXTERNAL = 5

TENSOR_INPUT = 1
TENSOR_OUTPUT = 2

DTYPE_BOOL = 1
DTYPE_INT8 = 2
DTYPE_UINT8 = 3
DTYPE_INT16 = 4
DTYPE_UINT16 = 5
DTYPE_INT32 = 6
DTYPE_UINT32 = 7
DTYPE_INT64 = 8
DTYPE_UINT64 = 9
DTYPE_FLOAT16 = 10
DTYPE_FLOAT32 = 11
DTYPE_FLOAT64 = 12
DTYPE_BFLOAT16 = 13

_DTYPE_BY_NAME = {
    "bool": DTYPE_BOOL,
    "int8": DTYPE_INT8,
    "uint8": DTYPE_UINT8,
    "int16": DTYPE_INT16,
    "uint16": DTYPE_UINT16,
    "int32": DTYPE_INT32,
    "uint32": DTYPE_UINT32,
    "int64": DTYPE_INT64,
    "uint64": DTYPE_UINT64,
    "float16": DTYPE_FLOAT16,
    "float32": DTYPE_FLOAT32,
    "float64": DTYPE_FLOAT64,
    "bfloat16": DTYPE_BFLOAT16,
}

_BACKEND_BY_NAME = {
    "native": BACKEND_NATIVE,
    "cpu": BACKEND_CPU,
    "gpu": BACKEND_GPU,
    "npu": BACKEND_NPU,
    "external": BACKEND_EXTERNAL,
}


class NativeLiteRTRuntimeError(RuntimeError):
    pass


class _Tensor(ctypes.Structure):
    _fields_ = [
        ("tensor_id", ctypes.c_uint32),
        ("role", ctypes.c_uint32),
        ("dtype", ctypes.c_uint32),
        ("rank", ctypes.c_uint32),
        ("dims", ctypes.c_uint64 * MAX_RANK),
        ("name_sha256", ctypes.c_uint8 * SHA256_BYTES),
    ]


class _Descriptor(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("generation", ctypes.c_uint32),
        ("backend", ctypes.c_uint32),
        ("context_tokens", ctypes.c_uint32),
        ("max_output_tokens", ctypes.c_uint32),
        ("tensor_count", ctypes.c_uint32),
        ("input_count", ctypes.c_uint32),
        ("output_count", ctypes.c_uint32),
        ("source_sha256", ctypes.c_uint8 * SHA256_BYTES),
        ("model_identity_hash216", ctypes.c_char * (HASH216_BYTES + 1)),
        ("tensors", _Tensor * MAX_TENSORS),
    ]


class _Registration(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("generation", ctypes.c_uint32),
        ("backend", ctypes.c_uint32),
        ("context_tokens", ctypes.c_uint32),
        ("max_output_tokens", ctypes.c_uint32),
        ("tensor_count", ctypes.c_uint32),
        ("input_count", ctypes.c_uint32),
        ("output_count", ctypes.c_uint32),
        ("registration_fingerprint64", ctypes.c_uint64),
        ("source_sha256", ctypes.c_uint8 * SHA256_BYTES),
        ("model_identity_hash216", ctypes.c_char * (HASH216_BYTES + 1)),
        ("tensors", _Tensor * MAX_TENSORS),
        ("native_registry_authority", ctypes.c_uint8),
        ("model_output_advisory_only", ctypes.c_uint8),
        ("vm81_mutation_authority", ctypes.c_uint8),
        ("hash72_commit_authority", ctypes.c_uint8),
        ("hash216_persistence_authority", ctypes.c_uint8),
        ("floating_point_canonical_authority", ctypes.c_uint8),
        ("external_litert_compatibility_supported", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8),
    ]


@dataclass(frozen=True)
class NativeLiteRTTensorSpec:
    name: str
    role: str
    dtype: str
    shape: tuple[int, ...]


@dataclass(frozen=True)
class NativeLiteRTModelRegistration:
    schema: str
    model_id: str
    model_identity_hash216: str
    source_sha256: str
    generation: int
    backend: str
    context_tokens: int
    max_output_tokens: int
    tensor_count: int
    input_count: int
    output_count: int
    registration_fingerprint64: int
    rna_runtime_class_hash216: str
    rna_runtime_class_fingerprint64: int
    model_output_advisory_only: bool
    vm81_mutation_authority: bool
    hash72_commit_authority: bool
    hash216_persistence_authority: bool
    floating_point_canonical_authority: bool
    external_litert_compatibility_supported: bool


def _stable_u32(domain: str, value: str) -> int:
    raw = int.from_bytes(
        sha256(f"{domain}\0{value}".encode("utf-8")).digest()[:4],
        "big",
    )
    return raw or 1


def _dtype_code(name: str) -> int:
    try:
        return _DTYPE_BY_NAME[str(name).strip().lower()]
    except KeyError as exc:
        raise NativeLiteRTRuntimeError(
            f"HHS_LITERT1_DTYPE_UNSUPPORTED:{name}"
        ) from exc


def _backend_code(name: str) -> int:
    try:
        return _BACKEND_BY_NAME[str(name).strip().lower()]
    except KeyError as exc:
        raise NativeLiteRTRuntimeError(
            f"HHS_LITERT1_BACKEND_UNSUPPORTED:{name}"
        ) from exc


def _runtime_class_members() -> tuple[PythonClassMemberSpec, ...]:
    return (
        PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 0, 0, 1),
        PythonClassMemberSpec("model_identity", MEMBER_FIELD, 1, 1, 0),
        PythonClassMemberSpec("input_tensors", MEMBER_FIELD, 2, 0, 0),
        PythonClassMemberSpec("output_tensors", MEMBER_FIELD, 3, 1, 0),
        PythonClassMemberSpec("invoke", MEMBER_METHOD, 0, 0, 1),
        PythonClassMemberSpec("list_models", MEMBER_METHOD, 1, 1, 0),
        PythonClassMemberSpec("chat_completion", MEMBER_METHOD, 2, 0, 2),
    )


_RUNTIME_CLASS_SOURCE = """class LiteRTModelRuntime:
    def __init__(self, model_identity, input_tensors, output_tensors): ...
    def invoke(self, inputs): ...
    def list_models(self): ...
    def chat_completion(self, messages, tools=None, response_format=None): ...
"""


class NativeLiteRTModelRegistry:
    def __init__(
        self,
        model_runtime_library: str | Path,
        exact_abi_library: str | Path,
    ):
        self.model_runtime_library = str(Path(model_runtime_library))
        self.exact_abi_library = str(Path(exact_abi_library))
        self._lib = ctypes.CDLL(self.model_runtime_library)
        self._lib.hhs_litert_native_model_runtime_version.restype = ctypes.c_uint32
        self._lib.hhs_litert_native_model_register.argtypes = [
            ctypes.POINTER(_Descriptor),
            ctypes.POINTER(_Registration),
        ]
        self._lib.hhs_litert_native_model_register.restype = ctypes.c_int
        self._lib.hhs_litert_native_model_validate_registration.argtypes = [
            ctypes.POINTER(_Registration),
        ]
        self._lib.hhs_litert_native_model_validate_registration.restype = ctypes.c_int
        if int(self._lib.hhs_litert_native_model_runtime_version()) != 1:
            raise NativeLiteRTRuntimeError(
                "HHS_LITERT1_NATIVE_MODEL_RUNTIME_VERSION_MISMATCH"
            )
        self._rna_registry = PythonRNAClassRegistry(self.exact_abi_library)

    def register(
        self,
        *,
        model_id: str,
        source_identity: str | bytes,
        generation: int,
        backend: str,
        context_tokens: int,
        max_output_tokens: int,
        tensors: Iterable[NativeLiteRTTensorSpec],
    ) -> NativeLiteRTModelRegistration:
        tensor_specs = tuple(tensors)
        if not model_id.strip():
            raise NativeLiteRTRuntimeError("HHS_LITERT1_MODEL_ID_REQUIRED")
        if not 1 <= len(tensor_specs) <= MAX_TENSORS:
            raise NativeLiteRTRuntimeError(
                "HHS_LITERT1_TENSOR_COUNT_OUT_OF_RANGE"
            )
        if isinstance(source_identity, str):
            source_bytes = source_identity.encode("utf-8")
        else:
            source_bytes = bytes(source_identity)
        source_digest = sha256(source_bytes).digest()
        source_hex = source_digest.hex()

        identity = hash216(
            {
                "schema": SCHEMA,
                "model_id": model_id,
                "source_sha256": source_hex,
                "generation": int(generation),
                "backend": str(backend).lower(),
                "context_tokens": int(context_tokens),
                "max_output_tokens": int(max_output_tokens),
                "tensors": [
                    {
                        "name": item.name,
                        "role": item.role,
                        "dtype": item.dtype,
                        "shape": list(item.shape),
                    }
                    for item in tensor_specs
                ],
            },
            domain="HHS-P220-LITERT1-MODEL",
        )
        if len(identity) != HASH216_BYTES or not identity.isascii():
            raise NativeLiteRTRuntimeError(
                "HHS_LITERT1_MODEL_HASH216_INVALID"
            )

        descriptor = _Descriptor()
        descriptor.struct_size = ctypes.sizeof(_Descriptor)
        descriptor.version = 1
        descriptor.generation = int(generation)
        descriptor.backend = _backend_code(backend)
        descriptor.context_tokens = int(context_tokens)
        descriptor.max_output_tokens = int(max_output_tokens)
        descriptor.tensor_count = len(tensor_specs)
        descriptor.input_count = sum(
            1 for item in tensor_specs if item.role == "input"
        )
        descriptor.output_count = sum(
            1 for item in tensor_specs if item.role == "output"
        )
        for index, byte in enumerate(source_digest):
            descriptor.source_sha256[index] = byte
        descriptor.model_identity_hash216 = identity.encode("ascii")

        seen_ids: set[int] = set()
        for index, item in enumerate(tensor_specs):
            if not 1 <= len(item.shape) <= MAX_RANK:
                raise NativeLiteRTRuntimeError(
                    "HHS_LITERT1_TENSOR_RANK_OUT_OF_RANGE"
                )
            if any(
                isinstance(dim, bool) or not isinstance(dim, int) or dim <= 0
                for dim in item.shape
            ):
                raise NativeLiteRTRuntimeError(
                    "HHS_LITERT1_TENSOR_DIMENSION_INVALID"
                )
            role = str(item.role).lower()
            if role not in {"input", "output"}:
                raise NativeLiteRTRuntimeError(
                    f"HHS_LITERT1_TENSOR_ROLE_INVALID:{item.role}"
                )
            tensor_id = _stable_u32(
                "HHS-P220-LITERT1-TENSOR",
                f"{model_id}:{item.name}:{role}",
            )
            if tensor_id in seen_ids:
                raise NativeLiteRTRuntimeError(
                    "HHS_LITERT1_TENSOR_ID_COLLISION"
                )
            seen_ids.add(tensor_id)

            native = descriptor.tensors[index]
            native.tensor_id = tensor_id
            native.role = TENSOR_INPUT if role == "input" else TENSOR_OUTPUT
            native.dtype = _dtype_code(item.dtype)
            native.rank = len(item.shape)
            for dim_index, dim in enumerate(item.shape):
                native.dims[dim_index] = dim
            name_digest = sha256(item.name.encode("utf-8")).digest()
            for byte_index, byte in enumerate(name_digest):
                native.name_sha256[byte_index] = byte

        registration = _Registration()
        status = int(
            self._lib.hhs_litert_native_model_register(
                ctypes.byref(descriptor),
                ctypes.byref(registration),
            )
        )
        if status != 0:
            raise NativeLiteRTRuntimeError(
                f"HHS_LITERT1_NATIVE_MODEL_REGISTRATION_REJECTED:{status}"
            )
        if int(
            self._lib.hhs_litert_native_model_validate_registration(
                ctypes.byref(registration)
            )
        ) != 0:
            raise NativeLiteRTRuntimeError(
                "HHS_LITERT1_NATIVE_MODEL_REGISTRATION_INVALID"
            )

        rna = self._rna_registry.register(
            module_name="hhs.litert",
            class_name="LiteRTModelRuntime",
            source_text=_RUNTIME_CLASS_SOURCE,
            members=_runtime_class_members(),
        )

        return NativeLiteRTModelRegistration(
            schema=SCHEMA,
            model_id=model_id,
            model_identity_hash216=bytes(
                registration.model_identity_hash216
            ).split(b"\0", 1)[0].decode("ascii"),
            source_sha256=bytes(registration.source_sha256).hex(),
            generation=int(registration.generation),
            backend=str(backend).lower(),
            context_tokens=int(registration.context_tokens),
            max_output_tokens=int(registration.max_output_tokens),
            tensor_count=int(registration.tensor_count),
            input_count=int(registration.input_count),
            output_count=int(registration.output_count),
            registration_fingerprint64=int(
                registration.registration_fingerprint64
            ),
            rna_runtime_class_hash216=rna.class_identity_hash216,
            rna_runtime_class_fingerprint64=rna.registration_fingerprint64,
            model_output_advisory_only=bool(
                registration.model_output_advisory_only
            ),
            vm81_mutation_authority=bool(
                registration.vm81_mutation_authority
            ),
            hash72_commit_authority=bool(
                registration.hash72_commit_authority
            ),
            hash216_persistence_authority=bool(
                registration.hash216_persistence_authority
            ),
            floating_point_canonical_authority=bool(
                registration.floating_point_canonical_authority
            ),
            external_litert_compatibility_supported=bool(
                registration.external_litert_compatibility_supported
            ),
        )


def tensor_specs_from_litert_details(
    inputs: Sequence[Mapping[str, Any]],
    outputs: Sequence[Mapping[str, Any]],
) -> tuple[NativeLiteRTTensorSpec, ...]:
    def dtype_name(value: Any) -> str:
        text = str(getattr(value, "name", value)).lower()
        for candidate in _DTYPE_BY_NAME:
            if candidate in text:
                return candidate
        raise NativeLiteRTRuntimeError(
            f"HHS_LITERT1_EXTERNAL_DTYPE_UNSUPPORTED:{text}"
        )

    records: list[NativeLiteRTTensorSpec] = []
    for role, details in (("input", inputs), ("output", outputs)):
        for index, detail in enumerate(details):
            shape_raw = detail.get("shape")
            if shape_raw is None:
                raise NativeLiteRTRuntimeError(
                    "HHS_LITERT1_EXTERNAL_TENSOR_SHAPE_REQUIRED"
                )
            shape = tuple(int(value) for value in shape_raw)
            name = str(detail.get("name") or f"{role}:{index}")
            records.append(
                NativeLiteRTTensorSpec(
                    name=name,
                    role=role,
                    dtype=dtype_name(detail.get("dtype")),
                    shape=shape,
                )
            )
    return tuple(records)


def litert1_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "internal_runtime": "HHS_NATIVE",
        "external_litert_lm_cli_required_for_default_runtime": False,
        "external_litert_lm_compatibility_retained": True,
        "external_openai_compatible_http_retained": True,
        "pass153_litert_interpreter_adapter_retained": True,
        "native_model_tensor_registry": True,
        "python2_rna_runtime_class_binding": True,
        "model_output_advisory_only": True,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "tensor_numeric_execution_next": "NUMPY1_HARMONICODE",
    }


__all__ = [
    "NativeLiteRTModelRegistration",
    "NativeLiteRTModelRegistry",
    "NativeLiteRTRuntimeError",
    "NativeLiteRTTensorSpec",
    "litert1_contract",
    "tensor_specs_from_litert_details",
]
