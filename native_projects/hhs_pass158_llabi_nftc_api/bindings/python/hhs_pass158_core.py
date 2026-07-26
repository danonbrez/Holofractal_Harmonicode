from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import ctypes as C
import json
import os
from pathlib import Path
from typing import Iterable, Sequence

HHS158_OK = 0
HHS158_BUFFER_TOO_SMALL = 2
HHS158_VALUE_BIGINT = 3
HHS158_VALUE_RATIONAL = 4
HHS158_VALUE_LIST = 7
HHS158_VALUE_TENSOR = 8
HHS158_VALUE_EXPRESSION = 9
HHS158_FLAG_AUTHORITATIVE = 1
HHS158_FLAG_ORDERED = 4
HHS158_FLAG_IMMUTABLE = 8
HHS158_FLAG_PROJECTION = 16
HHS158_FLAG_APPROXIMATE = 32
HHS158_PROJECTION_EXACT_REFERENCE = 1
HHS158_PROJECTION_IEEE754_BINARY64_CONTROL = 2
HHS158_PROJECTION_RENDER_FLOAT32 = 3
HHS158_CAP_VALIDATE = 1 << 0
HHS158_CAP_EXECUTE = 1 << 1
HHS158_CAP_COMMIT = 1 << 2
HHS158_CAP_PROJECT = 1 << 3
HHS158_CAP_SERIALIZE = 1 << 4
HHS158_CAP_COMPOSE = 1 << 5
HHS158_CAP_REGISTER = 1 << 6
HHS158_CAP_INSTANTIATE = 1 << 7
HHS158_CAP_BIND = 1 << 8
HHS158_CAP_REPLAY = 1 << 9
HHS158_MUTATION_INSTANCE = 1
HHS158_OP_BIND_EQ = 0x5810
HHS158_OP_CHAIN_APPEND = 0x5812
HHS158_SERIALIZE_CANONICAL_JSON = 2


class Header(C.Structure):
    _fields_ = [("struct_size", C.c_uint32), ("struct_version", C.c_uint32)]


class ByteSpan(C.Structure):
    _fields_ = [("data", C.POINTER(C.c_uint8)), ("size", C.c_size_t)]


class MutableByteSpan(C.Structure):
    _fields_ = [
        ("data", C.POINTER(C.c_uint8)),
        ("capacity", C.c_size_t),
        ("size_written", C.c_size_t),
    ]


class ContextConfig(C.Structure):
    _fields_ = [
        ("header", Header),
        ("abi_major", C.c_uint32),
        ("abi_minor", C.c_uint32),
        ("max_definitions", C.c_uint32),
        ("max_instances", C.c_uint32),
        ("max_receipts", C.c_uint32),
        ("max_memory_bytes", C.c_uint64),
        ("deterministic_epoch_seconds", C.c_uint64),
        ("flags", C.c_uint32),
        ("reserved", C.c_uint32),
    ]


class Value(C.Structure):
    _fields_ = [
        ("header", Header),
        ("kind", C.c_uint32),
        ("flags", C.c_uint32),
        ("canonical_payload", ByteSpan),
    ]


class CapabilityRequest(C.Structure):
    _fields_ = [
        ("header", Header),
        ("issuer", ByteSpan),
        ("subject", ByteSpan),
        ("application_id", ByteSpan),
        ("object_scope", ByteSpan),
        ("operation_scope", C.c_uint64),
        ("mutation_scope", C.c_uint64),
        ("max_vm81_steps", C.c_uint64),
        ("issued_at", C.c_uint64),
        ("expires_at", C.c_uint64),
        ("revocation_root", ByteSpan),
        ("delegation_policy", C.c_uint32),
        ("flags", C.c_uint32),
    ]


class DefinitionDescriptor(C.Structure):
    _fields_ = [
        ("header", Header),
        ("contract_id", ByteSpan),
        ("schema_version", ByteSpan),
        ("canonical_name", ByteSpan),
        ("object_class", ByteSpan),
        ("canonical_constraints", ByteSpan),
        ("symbol_table", ByteSpan),
        ("numeric_policy", ByteSpan),
        ("operator_policy", ByteSpan),
        ("authority_root", ByteSpan),
        ("ancestry", ByteSpan),
        ("tensor_rank", C.c_uint32),
        ("tensor_shape", C.POINTER(C.c_uint64)),
        ("flags", C.c_uint32),
        ("reserved", C.c_uint32),
    ]


class InstanceConfig(C.Structure):
    _fields_ = [
        ("header", Header),
        ("instance_nonce", ByteSpan),
        ("owner_capability_domain", ByteSpan),
        ("max_vm81_steps", C.c_uint64),
        ("max_recursion_depth", C.c_uint64),
        ("max_state_bytes", C.c_uint64),
        ("max_receipt_bytes", C.c_uint64),
        ("projection_profile_mask", C.c_uint32),
        ("flags", C.c_uint32),
    ]


class ValidationPolicy(C.Structure):
    _fields_ = [
        ("header", Header),
        ("mode", C.c_uint32),
        ("flags", C.c_uint32),
        ("max_vm81_steps", C.c_uint64),
        ("max_recursion_depth", C.c_uint64),
        ("max_dependency_depth", C.c_uint64),
        ("max_tensor_elements", C.c_uint64),
    ]


class ProjectionProfile(C.Structure):
    _fields_ = [
        ("header", Header),
        ("kind", C.c_uint32),
        ("flags", C.c_uint32),
        ("profile_name", ByteSpan),
        ("decimal_digits", C.c_uint32),
        ("reserved", C.c_uint32),
    ]


class ValidationReport(C.Structure):
    _fields_ = [
        ("header", Header),
        ("status", C.c_int32),
        ("lifecycle_state", C.c_uint32),
        ("checked_constraints", C.c_uint64),
        ("warnings", C.c_uint64),
        ("classification", C.c_char * 96),
        ("state_root", C.c_char * 217),
    ]


class Operation(C.Structure):
    _fields_ = [
        ("header", Header),
        ("opcode", C.c_uint32),
        ("flags", C.c_uint32),
        ("operands", ByteSpan),
    ]


class TransitionDescriptor(C.Structure):
    _fields_ = [
        ("header", Header),
        ("operations", C.POINTER(Operation)),
        ("operation_count", C.c_size_t),
        ("expected_pre_state_root", ByteSpan),
        ("dependency_roots", ByteSpan),
        ("max_vm81_steps", C.c_uint64),
        ("max_recursion_depth", C.c_uint64),
        ("max_output_bytes", C.c_uint64),
        ("projection_policy", C.c_uint32),
        ("delta_policy", C.c_uint32),
        ("commit_policy", C.c_uint32),
        ("flags", C.c_uint32),
    ]


class ExecutionOptions(C.Structure):
    _fields_ = [
        ("header", Header),
        ("max_vm81_steps", C.c_uint64),
        ("max_wall_time_ms", C.c_uint64),
        ("max_cpu_time_ms", C.c_uint64),
        ("max_memory_bytes", C.c_uint64),
        ("atomic_execute_and_commit", C.c_uint32),
        ("allow_hold", C.c_uint32),
        ("cancel_flag", C.POINTER(C.c_uint32)),
    ]


class ExecutionResult(C.Structure):
    _fields_ = [
        ("header", Header),
        ("status", C.c_int32),
        ("lifecycle_state", C.c_uint32),
        ("vm81_steps", C.c_uint64),
        ("witness_flags", C.c_uint64),
        ("classification", C.c_char * 96),
        ("pre_state_root", C.c_char * 217),
        ("post_state_root", C.c_char * 217),
        ("opcode_trace_root", C.c_char * 217),
    ]


class ReplayOptions(C.Structure):
    _fields_ = [
        ("header", Header),
        ("verify_hash72", C.c_uint32),
        ("verify_hash216", C.c_uint32),
        ("verify_semantic_root", C.c_uint32),
        ("flags", C.c_uint32),
    ]


class ReplayResult(C.Structure):
    _fields_ = [
        ("header", Header),
        ("status", C.c_int32),
        ("matched", C.c_uint32),
        ("lifecycle_state", C.c_uint32),
        ("classification", C.c_char * 96),
        ("reconstructed_state_root", C.c_char * 217),
    ]


class SerializationOptions(C.Structure):
    _fields_ = [
        ("header", Header),
        ("format", C.c_uint32),
        ("preserve_unknown_fields", C.c_uint32),
        ("max_output_bytes", C.c_uint64),
        ("flags", C.c_uint32),
        ("reserved", C.c_uint32),
    ]


def _header(struct: C.Structure) -> None:
    struct.header.struct_size = C.sizeof(struct)
    struct.header.struct_version = 1


class _PinnedSpan:
    def __init__(self, value: str | bytes):
        raw = value.encode("utf-8") if isinstance(value, str) else bytes(value)
        self.raw = raw
        self.buffer = (C.c_uint8 * max(1, len(raw)))()
        if raw:
            C.memmove(self.buffer, raw, len(raw))
        self.span = ByteSpan(C.cast(self.buffer, C.POINTER(C.c_uint8)), len(raw))


class Hhs158Error(RuntimeError):
    def __init__(self, status: int, classification: str):
        super().__init__(f"{classification} ({status})")
        self.status = status
        self.classification = classification


@dataclass(frozen=True)
class ExactRational:
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if self.denominator <= 0:
            raise ValueError("denominator must be positive")
        reduced = Fraction(self.numerator, self.denominator)
        object.__setattr__(self, "numerator", reduced.numerator)
        object.__setattr__(self, "denominator", reduced.denominator)

    def canonical(self) -> bytes:
        return f"{self.numerator}/{self.denominator}".encode("ascii")

    def __float__(self) -> float:
        raise TypeError("authoritative HHS rationals do not implicitly convert to float")


@dataclass(frozen=True)
class ExecutionSummary:
    status: int
    classification: str
    lifecycle_state: int
    vm81_steps: int
    pre_state_root: str
    post_state_root: str
    opcode_trace_root: str


class NativeLibrary:
    def __init__(self, path: str | os.PathLike[str] | None = None):
        selected = path or os.environ.get("HHS_PASS158_LIBRARY")
        if not selected:
            selected = Path(__file__).resolve().parents[2] / "dist" / "libhhs_pass158.so"
        self.path = Path(selected)
        self.lib = C.CDLL(str(self.path))
        self._declare()

    def _declare(self) -> None:
        l = self.lib
        l.hhs158_status_classification.argtypes = [C.c_int32]
        l.hhs158_status_classification.restype = C.c_char_p
        l.hhs158_context_create.argtypes = [C.POINTER(ContextConfig), C.POINTER(C.c_void_p)]
        l.hhs158_context_create.restype = C.c_int32
        l.hhs158_context_release.argtypes = [C.c_void_p]
        l.hhs158_definition_register.argtypes = [C.c_void_p, C.POINTER(DefinitionDescriptor), C.POINTER(C.c_void_p), C.POINTER(C.c_void_p)]
        l.hhs158_definition_register.restype = C.c_int32
        l.hhs158_definition_id.argtypes = [C.c_void_p, C.POINTER(MutableByteSpan)]
        l.hhs158_definition_id.restype = C.c_int32
        l.hhs158_instance_create.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(InstanceConfig), C.POINTER(C.c_void_p), C.POINTER(C.c_void_p)]
        l.hhs158_instance_create.restype = C.c_int32
        l.hhs158_instance_id.argtypes = [C.c_void_p, C.POINTER(MutableByteSpan)]
        l.hhs158_instance_id.restype = C.c_int32
        l.hhs158_instance_state_root.argtypes = [C.c_void_p, C.POINTER(MutableByteSpan)]
        l.hhs158_instance_state_root.restype = C.c_int32
        l.hhs158_capability_open.argtypes = [C.c_void_p, C.POINTER(CapabilityRequest), C.POINTER(C.c_void_p)]
        l.hhs158_capability_open.restype = C.c_int32
        l.hhs158_capability_release.argtypes = [C.c_void_p]
        l.hhs158_capability_release.restype = None
        l.hhs158_instance_bind.argtypes = [C.c_void_p, ByteSpan, C.POINTER(Value)]
        l.hhs158_instance_bind.restype = C.c_int32
        l.hhs158_instance_bind_authorized.argtypes = [C.c_void_p, C.c_void_p, ByteSpan, C.POINTER(Value), C.POINTER(C.c_void_p)]
        l.hhs158_instance_bind_authorized.restype = C.c_int32
        l.hhs158_instance_validate_static.argtypes = [C.c_void_p, C.POINTER(ValidationPolicy), C.POINTER(ValidationReport)]
        l.hhs158_instance_validate_static.restype = C.c_int32
        l.hhs158_instance_project.argtypes = [C.c_void_p, C.POINTER(ProjectionProfile), C.POINTER(Value), C.POINTER(C.c_void_p)]
        l.hhs158_instance_project.restype = C.c_int32
        l.hhs158_value_release.argtypes = [C.POINTER(Value)]
        l.hhs158_value_release.restype = None
        l.hhs158_transition_create.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(TransitionDescriptor), C.POINTER(C.c_void_p)]
        l.hhs158_transition_create.restype = C.c_int32
        l.hhs158_transition_execute.argtypes = [C.c_void_p, C.POINTER(ExecutionOptions), C.POINTER(ExecutionResult), C.POINTER(C.c_void_p)]
        l.hhs158_transition_execute.restype = C.c_int32
        l.hhs158_receipt_serialize.argtypes = [C.c_void_p, C.POINTER(MutableByteSpan)]
        l.hhs158_receipt_serialize.restype = C.c_int32
        l.hhs158_receipt_replay.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(ReplayOptions), C.POINTER(ReplayResult)]
        l.hhs158_receipt_replay.restype = C.c_int32
        l.hhs158_instance_serialize.argtypes = [C.c_void_p, C.POINTER(SerializationOptions), C.POINTER(MutableByteSpan)]
        l.hhs158_instance_serialize.restype = C.c_int32

    def classification(self, status: int) -> str:
        return self.lib.hhs158_status_classification(status).decode("utf-8")

    def check(self, status: int, *accepted: int) -> int:
        if status != HHS158_OK and status not in accepted:
            raise Hhs158Error(status, self.classification(status))
        return status


class Receipt:
    def __init__(self, context: "Context", handle: C.c_void_p):
        self._context = context
        self._handle = handle

    def serialize(self) -> dict:
        span = MutableByteSpan(None, 0, 0)
        status = self._context.native.lib.hhs158_receipt_serialize(self._handle, C.byref(span))
        self._context.native.check(status, HHS158_BUFFER_TOO_SMALL)
        buffer = (C.c_uint8 * span.size_written)()
        span.data = C.cast(buffer, C.POINTER(C.c_uint8))
        span.capacity = len(buffer)
        self._context.native.check(self._context.native.lib.hhs158_receipt_serialize(self._handle, C.byref(span)))
        return json.loads(bytes(buffer[: span.size_written]))

    def replay(self) -> dict:
        options = ReplayOptions()
        _header(options)
        options.verify_hash72 = options.verify_hash216 = options.verify_semantic_root = 1
        result = ReplayResult()
        status = self._context.native.lib.hhs158_receipt_replay(
            self._context.handle, self._handle, C.byref(options), C.byref(result)
        )
        self._context.native.check(status)
        return {
            "matched": bool(result.matched),
            "classification": bytes(result.classification).split(b"\0", 1)[0].decode(),
            "state_root": bytes(result.reconstructed_state_root).split(b"\0", 1)[0].decode(),
        }


class Context:
    def __init__(self, native: NativeLibrary | None = None, *, epoch: int = 1_799_711_799):
        self.native = native or NativeLibrary()
        config = ContextConfig()
        _header(config)
        config.abi_major = 1
        config.abi_minor = 0
        config.max_definitions = 64
        config.max_instances = 128
        config.max_receipts = 128
        config.max_memory_bytes = 16_777_216
        config.deterministic_epoch_seconds = epoch
        handle = C.c_void_p()
        self.native.check(self.native.lib.hhs158_context_create(C.byref(config), C.byref(handle)))
        self.handle = handle
        self.closed = False

    def close(self) -> None:
        if not self.closed:
            self.native.lib.hhs158_context_release(self.handle)
            self.closed = True

    def __enter__(self) -> "Context":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def register_definition(
        self,
        *,
        name: str,
        constraints: str,
        symbols: str,
        shape: Sequence[int],
        ancestry: str = "P154|P155|P156|P156.1|P157",
    ) -> tuple["Definition", Receipt]:
        pinned = [_PinnedSpan(v) for v in (
            "HHS-P158-LLABI-NFTC-API", "1.0.0", name,
            "NON_FUNGIBLE_TENSOR_CONSTRAINT", constraints, symbols,
            "EXACT_SYMBOLIC", "HHS_TYPED_OPERATORS", "PASS_158_INHERITED_ROOT", ancestry,
        )]
        shape_array = (C.c_uint64 * len(shape))(*[int(v) for v in shape])
        descriptor = DefinitionDescriptor()
        _header(descriptor)
        (
            descriptor.contract_id, descriptor.schema_version, descriptor.canonical_name,
            descriptor.object_class, descriptor.canonical_constraints, descriptor.symbol_table,
            descriptor.numeric_policy, descriptor.operator_policy, descriptor.authority_root,
            descriptor.ancestry,
        ) = [p.span for p in pinned]
        descriptor.tensor_rank = len(shape)
        descriptor.tensor_shape = C.cast(shape_array, C.POINTER(C.c_uint64))
        definition = C.c_void_p()
        receipt = C.c_void_p()
        self.native.check(self.native.lib.hhs158_definition_register(
            self.handle, C.byref(descriptor), C.byref(definition), C.byref(receipt)
        ))
        return Definition(self, definition), Receipt(self, receipt)


class Definition:
    def __init__(self, context: Context, handle: C.c_void_p):
        self.context = context
        self.handle = handle

    @property
    def definition_id(self) -> str:
        buffer = (C.c_uint8 * 216)()
        span = MutableByteSpan(C.cast(buffer, C.POINTER(C.c_uint8)), 216, 0)
        self.context.native.check(self.context.native.lib.hhs158_definition_id(self.handle, C.byref(span)))
        return bytes(buffer).decode("ascii")

    def instantiate(self, nonce: bytes) -> tuple["Instance", Receipt]:
        pinned = _PinnedSpan(nonce)
        config = InstanceConfig()
        _header(config)
        config.instance_nonce = pinned.span
        config.max_vm81_steps = 100_000
        config.max_recursion_depth = 72
        config.max_state_bytes = 16_777_216
        config.max_receipt_bytes = 1_048_576
        config.projection_profile_mask = 0xFFFFFFFF
        instance = C.c_void_p()
        receipt = C.c_void_p()
        self.context.native.check(self.context.native.lib.hhs158_instance_create(
            self.context.handle, self.handle, C.byref(config), C.byref(instance), C.byref(receipt)
        ))
        return Instance(self.context, instance), Receipt(self.context, receipt)


class Capability:
    def __init__(self, context: Context, handle: C.c_void_p):
        self.context = context
        self.handle = handle
        self.closed = False

    def close(self) -> None:
        if not self.closed:
            self.context.native.lib.hhs158_capability_release(self.handle)
            self.closed = True

    def __enter__(self) -> "Capability":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class Instance:
    def __init__(self, context: Context, handle: C.c_void_p):
        self.context = context
        self.handle = handle

    def _fixed(self, function_name: str) -> str:
        buffer = (C.c_uint8 * 216)()
        span = MutableByteSpan(C.cast(buffer, C.POINTER(C.c_uint8)), 216, 0)
        fn = getattr(self.context.native.lib, function_name)
        self.context.native.check(fn(self.handle, C.byref(span)))
        return bytes(buffer).decode("ascii")

    @property
    def instance_id(self) -> str:
        return self._fixed("hhs158_instance_id")

    @property
    def state_root(self) -> str:
        return self._fixed("hhs158_instance_state_root")

    def capability(self, *, commit: bool = True) -> Capability:
        values = [_PinnedSpan(v) for v in (
            "HHS_PASS158_AUTHORITY", "python-binding", "org.hhs.pass158.python", self.instance_id,
        )]
        request = CapabilityRequest()
        _header(request)
        request.issuer, request.subject, request.application_id, request.object_scope = [p.span for p in values]
        request.operation_scope = HHS158_CAP_BIND | HHS158_CAP_VALIDATE | HHS158_CAP_EXECUTE | HHS158_CAP_PROJECT | HHS158_CAP_SERIALIZE | HHS158_CAP_REPLAY
        if commit:
            request.operation_scope |= HHS158_CAP_COMMIT
        request.mutation_scope = HHS158_MUTATION_INSTANCE
        request.max_vm81_steps = 100_000
        request.issued_at = 1_799_711_700
        request.expires_at = 1_799_719_999
        handle = C.c_void_p()
        self.context.native.check(self.context.native.lib.hhs158_capability_open(
            self.context.handle, C.byref(request), C.byref(handle)
        ))
        return Capability(self.context, handle)

    def bind_rational(self, symbol: str, value: ExactRational, capability: Capability | None = None) -> Receipt:
        owned_capability = capability is None
        active_capability = capability or self.capability(commit=True)
        symbol_pin = _PinnedSpan(symbol)
        payload_pin = _PinnedSpan(value.canonical())
        native_value = Value()
        _header(native_value)
        native_value.kind = HHS158_VALUE_RATIONAL
        native_value.flags = HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE
        native_value.canonical_payload = payload_pin.span
        receipt_handle = C.c_void_p()
        try:
            self.context.native.check(self.context.native.lib.hhs158_instance_bind_authorized(
                self.handle, active_capability.handle, symbol_pin.span, C.byref(native_value), C.byref(receipt_handle)
            ))
            return Receipt(self.context, receipt_handle)
        finally:
            if owned_capability:
                active_capability.close()

    def bind_ordered_list(self, symbol: str, values: Iterable[str], capability: Capability | None = None) -> Receipt:
        owned_capability = capability is None
        active_capability = capability or self.capability(commit=True)
        symbol_pin = _PinnedSpan(symbol)
        payload_pin = _PinnedSpan(json.dumps(list(values), separators=(",", ":")))
        native_value = Value()
        _header(native_value)
        native_value.kind = HHS158_VALUE_LIST
        native_value.flags = HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_ORDERED | HHS158_FLAG_IMMUTABLE
        native_value.canonical_payload = payload_pin.span
        receipt_handle = C.c_void_p()
        try:
            self.context.native.check(self.context.native.lib.hhs158_instance_bind_authorized(
                self.handle, active_capability.handle, symbol_pin.span, C.byref(native_value), C.byref(receipt_handle)
            ))
            return Receipt(self.context, receipt_handle)
        finally:
            if owned_capability:
                active_capability.close()

    def validate(self) -> dict:
        policy = ValidationPolicy()
        _header(policy)
        policy.mode = 3
        policy.max_vm81_steps = 100_000
        policy.max_recursion_depth = 72
        policy.max_dependency_depth = 72
        policy.max_tensor_elements = 5_184
        report = ValidationReport()
        self.context.native.check(self.context.native.lib.hhs158_instance_validate_static(
            self.handle, C.byref(policy), C.byref(report)
        ))
        return {
            "classification": bytes(report.classification).split(b"\0", 1)[0].decode(),
            "state_root": bytes(report.state_root).split(b"\0", 1)[0].decode(),
            "checked_constraints": report.checked_constraints,
        }

    def project(self, profile: str = "IEEE754_BINARY64_CONTROL") -> tuple[dict, Receipt]:
        kinds = {
            "EXACT_REFERENCE": HHS158_PROJECTION_EXACT_REFERENCE,
            "IEEE754_BINARY64_CONTROL": HHS158_PROJECTION_IEEE754_BINARY64_CONTROL,
            "RENDER_FLOAT32": HHS158_PROJECTION_RENDER_FLOAT32,
        }
        try:
            kind = kinds[profile]
        except KeyError as exc:
            raise ValueError("TYPE_MISMATCH") from exc
        profile_pin = _PinnedSpan(profile)
        native_profile = ProjectionProfile()
        _header(native_profile)
        native_profile.kind = kind
        native_profile.profile_name = profile_pin.span
        native_profile.decimal_digits = 17 if kind == HHS158_PROJECTION_IEEE754_BINARY64_CONTROL else 9
        value = Value()
        receipt_handle = C.c_void_p()
        self.context.native.check(self.context.native.lib.hhs158_instance_project(
            self.handle, C.byref(native_profile), C.byref(value), C.byref(receipt_handle)
        ))
        try:
            payload = bytes(C.string_at(value.canonical_payload.data, value.canonical_payload.size)).decode("utf-8")
            result = {
                "profile": profile,
                "kind": int(value.kind),
                "flags": int(value.flags),
                "payload": payload,
                "approximate": bool(value.flags & HHS158_FLAG_APPROXIMATE),
                "authority": "PROJECTION_ONLY" if value.flags & HHS158_FLAG_PROJECTION else "EXACT_REFERENCE",
            }
        finally:
            self.context.native.lib.hhs158_value_release(C.byref(value))
        return result, Receipt(self.context, receipt_handle)

    def execute(self, capability: Capability, operations: Sequence[tuple[int, str]], *, commit: bool = True) -> tuple[ExecutionSummary, Receipt]:
        pins = [_PinnedSpan(operands) for _, operands in operations]
        native_ops = (Operation * len(operations))()
        for index, ((opcode, _), pin) in enumerate(zip(operations, pins)):
            _header(native_ops[index])
            native_ops[index].opcode = opcode
            native_ops[index].operands = pin.span
        root_pin = _PinnedSpan(self.state_root)
        descriptor = TransitionDescriptor()
        _header(descriptor)
        descriptor.operations = C.cast(native_ops, C.POINTER(Operation))
        descriptor.operation_count = len(operations)
        descriptor.expected_pre_state_root = root_pin.span
        descriptor.max_vm81_steps = 10_000
        descriptor.max_recursion_depth = 72
        descriptor.max_output_bytes = 1_048_576
        transition = C.c_void_p()
        self.context.native.check(self.context.native.lib.hhs158_transition_create(
            self.handle, capability.handle, C.byref(descriptor), C.byref(transition)
        ))
        options = ExecutionOptions()
        _header(options)
        options.max_vm81_steps = 10_000
        options.atomic_execute_and_commit = int(commit)
        result = ExecutionResult()
        receipt = C.c_void_p()
        self.context.native.check(self.context.native.lib.hhs158_transition_execute(
            transition, C.byref(options), C.byref(result), C.byref(receipt)
        ))
        summary = ExecutionSummary(
            status=result.status,
            classification=bytes(result.classification).split(b"\0", 1)[0].decode(),
            lifecycle_state=result.lifecycle_state,
            vm81_steps=result.vm81_steps,
            pre_state_root=bytes(result.pre_state_root).split(b"\0", 1)[0].decode(),
            post_state_root=bytes(result.post_state_root).split(b"\0", 1)[0].decode(),
            opcode_trace_root=bytes(result.opcode_trace_root).split(b"\0", 1)[0].decode(),
        )
        return summary, Receipt(self.context, receipt)

    def serialize(self) -> bytes:
        options = SerializationOptions()
        _header(options)
        options.format = HHS158_SERIALIZE_CANONICAL_JSON
        options.preserve_unknown_fields = 1
        options.max_output_bytes = 1_048_576
        span = MutableByteSpan(None, 0, 0)
        self.context.native.check(
            self.context.native.lib.hhs158_instance_serialize(self.handle, C.byref(options), C.byref(span)),
            HHS158_BUFFER_TOO_SMALL,
        )
        buffer = (C.c_uint8 * span.size_written)()
        span.data = C.cast(buffer, C.POINTER(C.c_uint8))
        span.capacity = len(buffer)
        self.context.native.check(self.context.native.lib.hhs158_instance_serialize(
            self.handle, C.byref(options), C.byref(span)
        ))
        return bytes(buffer[: span.size_written])


__all__ = [
    "NativeLibrary", "Context", "Definition", "Instance", "Capability", "Receipt",
    "ExactRational", "ExecutionSummary", "Hhs158Error",
    "HHS158_OP_BIND_EQ", "HHS158_OP_CHAIN_APPEND",
]
