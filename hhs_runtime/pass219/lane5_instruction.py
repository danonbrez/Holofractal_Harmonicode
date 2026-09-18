"""Pass 219 typed Lane 5 instruction object and execution gateways.

Upstream repository objects are plug-and-play.  VM81 and HHS-controlled Linux
host/kernel adapters are not: they accept only Lane5Instruction.

Raw objects are first intercepted, queued, dependency-ordered and optimized by
Lane 5.  State-affecting instructions remain non-executable until RNA/C++
cell-wall and signed PQC/environment evidence are bound.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass, replace
from hashlib import sha256
import json
from typing import Any, Callable, Mapping, TypeVar

from hhs_runtime.pass219.lane5_universal_abi_kernel_interceptor import (
    ADMIT_DOWNSTREAM,
    Lane5UniversalTrafficError,
    authorize_downstream_dispatch,
    intercept_abi_traffic,
)

SCHEMA = "HHS_PASS219_LANE5_INSTRUCTION_V1"
TARGET_VM81 = "VM81_RUNTIME"
TARGET_LINUX = "LINUX_KERNEL_HOST"

STATE_QUEUED_OPTIMIZED = "QUEUED_OPTIMIZED"
STATE_OBSERVATION_ADMITTED = "OBSERVATION_ADMITTED"
STATE_RNA_CELL_WALL_BOUND = "RNA_CELL_WALL_BOUND"
STATE_PQC_ADMITTED = "PQC_ADMITTED"
STATE_EXECUTED = "EXECUTED"
STATE_REJECTED = "REJECTED"

T = TypeVar("T")


class Lane5InstructionError(RuntimeError):
    pass


def _normalize_object(value: Any) -> Any:
    if is_dataclass(value):
        return {
            "__dataclass_type__": value.__class__.__qualname__,
            "value": _normalize_object(asdict(value)),
        }
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_object(item)
            for key, item in sorted(value.items(), key=lambda kv: str(kv[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_object(item) for item in value]
    if isinstance(value, (bytes, bytearray, memoryview)):
        raw = bytes(value)
        return {
            "__bytes__": True,
            "length": len(raw),
            "sha256": sha256(raw).hexdigest(),
        }
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if hasattr(value, "__dict__"):
        return {
            "__object_type__": value.__class__.__qualname__,
            "value": _normalize_object(vars(value)),
        }
    return {
        "__object_type__": value.__class__.__qualname__,
        "repr": repr(value),
    }


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize_object(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _digest(label: str, value: Any) -> str:
    return sha256(label.encode("ascii") + b"\0" + _canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class Lane5Instruction:
    schema: str
    target: str
    traffic_class: str
    operation: str
    source_object_type: str
    source_object_digest_sha256: str
    source_object_payload: Any
    dependency_root: str
    read_only: bool
    state_affecting: bool
    lane5_state: str
    zero_bypass_interposed: bool
    mandatory_optimization_dispatch: bool
    sandbox_queue_ticket: str
    sandbox_queue_optimized: bool
    sandbox_queue_reordered: bool
    sandbox_cache_hit: bool
    sandbox_cache_capacity_unit: str
    sandbox_cache_capacity_raw_serial_abi_bytes: int
    mandatory_capability_lineage: tuple[str, ...]
    rna_cpp_cell_wall_routed: bool
    signed_environmental_admission: bool
    pqc_authenticated: bool
    singleton_vm81_authority: bool
    canonical_mutation_authority: bool
    direct_fallback_allowed: bool
    instruction_sha256: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_object_payload"] = _normalize_object(
            self.source_object_payload
        )
        return data


def _instruction_body(
    *,
    target: str,
    traffic_class: str,
    operation: str,
    source_object_type: str,
    source_object_digest_sha256: str,
    dependency_root: str,
    read_only: bool,
    state_affecting: bool,
    lane5_state: str,
    zero_bypass_interposed: bool,
    mandatory_optimization_dispatch: bool,
    sandbox_queue_ticket: str,
    sandbox_queue_optimized: bool,
    sandbox_queue_reordered: bool,
    sandbox_cache_hit: bool,
    sandbox_cache_capacity_unit: str,
    sandbox_cache_capacity_raw_serial_abi_bytes: int,
    mandatory_capability_lineage: tuple[str, ...],
    rna_cpp_cell_wall_routed: bool,
    signed_environmental_admission: bool,
    pqc_authenticated: bool,
    singleton_vm81_authority: bool,
    canonical_mutation_authority: bool,
    direct_fallback_allowed: bool,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "target": target,
        "traffic_class": traffic_class,
        "operation": operation,
        "source_object_type": source_object_type,
        "source_object_digest_sha256": source_object_digest_sha256,
        "dependency_root": dependency_root,
        "read_only": read_only,
        "state_affecting": state_affecting,
        "lane5_state": lane5_state,
        "zero_bypass_interposed": zero_bypass_interposed,
        "mandatory_optimization_dispatch": mandatory_optimization_dispatch,
        "sandbox_queue_ticket": sandbox_queue_ticket,
        "sandbox_queue_optimized": sandbox_queue_optimized,
        "sandbox_queue_reordered": sandbox_queue_reordered,
        "sandbox_cache_hit": sandbox_cache_hit,
        "sandbox_cache_capacity_unit": sandbox_cache_capacity_unit,
        "sandbox_cache_capacity_raw_serial_abi_bytes": (
            sandbox_cache_capacity_raw_serial_abi_bytes
        ),
        "mandatory_capability_lineage": list(mandatory_capability_lineage),
        "rna_cpp_cell_wall_routed": rna_cpp_cell_wall_routed,
        "signed_environmental_admission": signed_environmental_admission,
        "pqc_authenticated": pqc_authenticated,
        "singleton_vm81_authority": singleton_vm81_authority,
        "canonical_mutation_authority": canonical_mutation_authority,
        "direct_fallback_allowed": direct_fallback_allowed,
    }


def lower_object_to_lane5_instruction(
    source_object: Any,
    *,
    target: str,
    traffic_class: str,
    operation: str,
    read_only: bool = False,
    dependency_root: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> Lane5Instruction:
    if target not in (TARGET_VM81, TARGET_LINUX):
        raise Lane5InstructionError(f"LANE5_INSTRUCTION_TARGET_INVALID:{target}")
    source_type = source_object.__class__.__qualname__
    source_digest = _digest("LANE5_SOURCE_OBJECT", source_object)
    payload = {
        "source_object_type": source_type,
        "source_object_digest_sha256": source_digest,
        "dependency_root": dependency_root or "",
        "metadata": dict(metadata or {}),
    }
    if isinstance(source_object, (bytes, bytearray, memoryview)):
        payload["raw_frame_le"] = bytes(source_object)

    intercepted = intercept_abi_traffic(
        traffic_class=traffic_class,
        operation=operation,
        payload=payload,
        read_only=read_only,
    )
    envelope = dict(intercepted["envelope"])
    queue = dict(intercepted["queue_optimization"])
    lineage = tuple(envelope.get("mandatory_capability_lineage") or ())
    if not lineage:
        raise Lane5InstructionError("LANE5_INSTRUCTION_CAPABILITY_LINEAGE_EMPTY")
    if envelope.get("sandbox_queued") is not True:
        raise Lane5InstructionError("LANE5_INSTRUCTION_QUEUE_REQUIRED")
    if envelope.get("sandbox_queue_optimized") is not True:
        raise Lane5InstructionError("LANE5_INSTRUCTION_OPTIMIZATION_REQUIRED")

    effective_dependency = str(
        queue.get("dependency_root")
        or dependency_root
        or ("READ_ONLY" if read_only else "GLOBAL_STATE_AFFECTING_CHAIN")
    )
    state = STATE_OBSERVATION_ADMITTED if read_only else STATE_QUEUED_OPTIMIZED
    body = _instruction_body(
        target=target,
        traffic_class=traffic_class,
        operation=operation,
        source_object_type=source_type,
        source_object_digest_sha256=source_digest,
        dependency_root=effective_dependency,
        read_only=bool(read_only),
        state_affecting=not bool(read_only),
        lane5_state=state,
        zero_bypass_interposed=True,
        mandatory_optimization_dispatch=True,
        sandbox_queue_ticket=str(envelope["sandbox_queue_ticket"]),
        sandbox_queue_optimized=True,
        sandbox_queue_reordered=bool(
            envelope.get("sandbox_queue_reordered")
        ),
        sandbox_cache_hit=bool(envelope.get("sandbox_cache_hit")),
        sandbox_cache_capacity_unit=str(
            envelope["sandbox_cache_capacity_unit"]
        ),
        sandbox_cache_capacity_raw_serial_abi_bytes=int(
            envelope["sandbox_cache_capacity_raw_serial_abi_bytes"]
        ),
        mandatory_capability_lineage=lineage,
        rna_cpp_cell_wall_routed=False,
        signed_environmental_admission=False,
        pqc_authenticated=False,
        singleton_vm81_authority=False,
        canonical_mutation_authority=False,
        direct_fallback_allowed=False,
    )
    return Lane5Instruction(
        **body,
        source_object_payload=source_object,
        instruction_sha256=_digest("LANE5_INSTRUCTION", body),
    )


def bind_rna_cell_wall(
    instruction: Lane5Instruction,
    *,
    rna_receipt: Mapping[str, Any],
) -> Lane5Instruction:
    require_lane5_instruction(
        instruction,
        expected_target=instruction.target,
        require_executable=False,
    )
    receipt = dict(rna_receipt)
    if receipt.get("rna_cpp_cell_wall_routed") is not True:
        raise Lane5InstructionError("LANE5_RNA_CELL_WALL_RECEIPT_REQUIRED")
    if receipt.get("candidate_only") is not True:
        raise Lane5InstructionError("LANE5_RNA_RECEIPT_CANDIDATE_ONLY_REQUIRED")
    body = instruction.to_dict()
    body.pop("source_object_payload", None)
    body.pop("instruction_sha256", None)
    body["lane5_state"] = STATE_RNA_CELL_WALL_BOUND
    body["rna_cpp_cell_wall_routed"] = True
    body["canonical_mutation_authority"] = False
    return replace(
        instruction,
        lane5_state=STATE_RNA_CELL_WALL_BOUND,
        rna_cpp_cell_wall_routed=True,
        canonical_mutation_authority=False,
        instruction_sha256=_digest("LANE5_INSTRUCTION", body),
    )


def bind_signed_pqc_admission(
    instruction: Lane5Instruction,
    *,
    pqc_receipt: Mapping[str, Any],
) -> Lane5Instruction:
    if instruction.read_only:
        raise Lane5InstructionError(
            "LANE5_READ_ONLY_INSTRUCTION_DOES_NOT_REQUIRE_PQC_MUTATION_ADMISSION"
        )
    if instruction.rna_cpp_cell_wall_routed is not True:
        raise Lane5InstructionError("LANE5_RNA_CELL_WALL_BINDING_REQUIRED")
    receipt = dict(pqc_receipt)
    if receipt.get("signed_environmental_admission") is not True:
        raise Lane5InstructionError("LANE5_SIGNED_ENVIRONMENTAL_ADMISSION_REQUIRED")
    if receipt.get("pqc_authenticated") is not True:
        raise Lane5InstructionError("LANE5_PQC_AUTHENTICATION_REQUIRED")
    if receipt.get("decision") != "ADMIT":
        raise Lane5InstructionError("LANE5_PQC_ADMISSION_REJECTED")
    singleton = bool(receipt.get("singleton_vm81_authority"))
    if instruction.target == TARGET_VM81 and not singleton:
        raise Lane5InstructionError("LANE5_SINGLETON_VM81_AUTHORITY_REQUIRED")

    body = instruction.to_dict()
    body.pop("source_object_payload", None)
    body.pop("instruction_sha256", None)
    body["lane5_state"] = STATE_PQC_ADMITTED
    body["signed_environmental_admission"] = True
    body["pqc_authenticated"] = True
    body["singleton_vm81_authority"] = singleton
    body["canonical_mutation_authority"] = False
    return replace(
        instruction,
        lane5_state=STATE_PQC_ADMITTED,
        signed_environmental_admission=True,
        pqc_authenticated=True,
        singleton_vm81_authority=singleton,
        canonical_mutation_authority=False,
        instruction_sha256=_digest("LANE5_INSTRUCTION", body),
    )


def require_lane5_instruction(
    instruction: Any,
    *,
    expected_target: str,
    require_executable: bool = True,
) -> Lane5Instruction:
    if not isinstance(instruction, Lane5Instruction):
        raise Lane5InstructionError("LANE5_INSTRUCTION_REQUIRED")
    if instruction.schema != SCHEMA:
        raise Lane5InstructionError("LANE5_INSTRUCTION_SCHEMA_DRIFT")
    if instruction.target != expected_target:
        raise Lane5InstructionError(
            f"LANE5_INSTRUCTION_TARGET_MISMATCH:{instruction.target}"
        )
    if not instruction.zero_bypass_interposed:
        raise Lane5InstructionError("LANE5_INSTRUCTION_ZERO_BYPASS_REQUIRED")
    if not instruction.mandatory_optimization_dispatch:
        raise Lane5InstructionError(
            "LANE5_INSTRUCTION_MANDATORY_OPTIMIZATION_REQUIRED"
        )
    if not instruction.sandbox_queue_optimized:
        raise Lane5InstructionError("LANE5_INSTRUCTION_QUEUE_OPTIMIZATION_REQUIRED")
    if instruction.direct_fallback_allowed:
        raise Lane5InstructionError("LANE5_INSTRUCTION_DIRECT_FALLBACK_FORBIDDEN")
    if instruction.canonical_mutation_authority:
        raise Lane5InstructionError("LANE5_INSTRUCTION_AUTHORITY_ESCALATION")
    if not require_executable:
        return instruction
    if instruction.read_only:
        if instruction.lane5_state != STATE_OBSERVATION_ADMITTED:
            raise Lane5InstructionError("LANE5_OBSERVATION_ADMISSION_REQUIRED")
        return instruction
    if instruction.lane5_state != STATE_PQC_ADMITTED:
        raise Lane5InstructionError("LANE5_PQC_ADMITTED_INSTRUCTION_REQUIRED")
    if not instruction.rna_cpp_cell_wall_routed:
        raise Lane5InstructionError("LANE5_RNA_CELL_WALL_BINDING_REQUIRED")
    if not instruction.signed_environmental_admission:
        raise Lane5InstructionError("LANE5_SIGNED_ENVIRONMENTAL_ADMISSION_REQUIRED")
    if not instruction.pqc_authenticated:
        raise Lane5InstructionError("LANE5_PQC_AUTHENTICATION_REQUIRED")
    if expected_target == TARGET_VM81 and not instruction.singleton_vm81_authority:
        raise Lane5InstructionError("LANE5_SINGLETON_VM81_AUTHORITY_REQUIRED")
    return instruction


def execute_vm81_instruction(
    instruction: Lane5Instruction,
    executor: Callable[[Any], T],
) -> T:
    admitted = require_lane5_instruction(
        instruction,
        expected_target=TARGET_VM81,
        require_executable=True,
    )
    return executor(admitted.source_object_payload)


def execute_linux_instruction(
    instruction: Lane5Instruction,
    executor: Callable[[Any], T],
) -> T:
    admitted = require_lane5_instruction(
        instruction,
        expected_target=TARGET_LINUX,
        require_executable=True,
    )
    return executor(admitted.source_object_payload)


def validate_instruction_against_universal_dispatch(
    instruction: Lane5Instruction,
    *,
    lane5_receipt: Mapping[str, Any],
    pqc_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Cross-check typed instruction evidence against universal dispatch rules."""
    synthetic = {
        "envelope": {
            "schema": "HHS_PASS219_UNIVERSAL_ABI_LINUX_KERNEL_LANE5_INTERCEPT_V1",
            "traffic_class": instruction.traffic_class,
            "redirected_through_lane5": True,
            "zero_bypass_interposed": instruction.zero_bypass_interposed,
            "mandatory_optimization_dispatch": (
                instruction.mandatory_optimization_dispatch
            ),
            "sandbox_queued": True,
            "sandbox_queue_optimized": instruction.sandbox_queue_optimized,
            "sandbox_serial_bits": 5184,
            "sandbox_record_bytes": 648,
            "sandbox_byte_order": "LITTLE_ENDIAN",
            "canonical_mutation_authority": False,
            "hash72_authority": False,
            "hash216_authority": False,
            "canonical_persistence_authority": False,
            "pqc_key_authority": False,
            "receipt_clock_authority": False,
            "floating_point_canonical_authority": False,
            "read_only": instruction.read_only,
            "sandbox_queue_reordered": instruction.sandbox_queue_reordered,
            "sandbox_cache_hit": instruction.sandbox_cache_hit,
            "envelope_sha256": instruction.instruction_sha256,
        }
    }
    try:
        decision = authorize_downstream_dispatch(
            synthetic,
            lane5_receipt=lane5_receipt,
            pqc_receipt=pqc_receipt,
        )
    except Lane5UniversalTrafficError as exc:
        raise Lane5InstructionError(str(exc)) from exc
    if decision.get("decision") != ADMIT_DOWNSTREAM:
        raise Lane5InstructionError("LANE5_UNIVERSAL_DISPATCH_REJECTED")
    return decision


__all__ = [
    "Lane5Instruction",
    "Lane5InstructionError",
    "SCHEMA",
    "STATE_EXECUTED",
    "STATE_OBSERVATION_ADMITTED",
    "STATE_PQC_ADMITTED",
    "STATE_QUEUED_OPTIMIZED",
    "STATE_REJECTED",
    "STATE_RNA_CELL_WALL_BOUND",
    "TARGET_LINUX",
    "TARGET_VM81",
    "bind_rna_cell_wall",
    "bind_signed_pqc_admission",
    "execute_linux_instruction",
    "execute_vm81_instruction",
    "lower_object_to_lane5_instruction",
    "require_lane5_instruction",
    "validate_instruction_against_universal_dispatch",
]
