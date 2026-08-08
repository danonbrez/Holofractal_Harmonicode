"""Pass 214 governed IR adapter over the Pass 213 singleton VM81 authority.

This module intentionally does not call the frozen VM81 C substrate directly.
It schedules typed IR and delegates every canonical mutation to the Pass 213
governed native-dispatch authority so parent/tensor admission, compiled-ROM
identity, Hash216 successor state, Hash72 receipts, and authenticated ledger
continuity remain single-authority properties.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence

from hhs_backend.runtime.hhs_pass213_native_dispatch_common_v1 import (
    NativeDispatchRequest,
)

SCHEMA = "HHS_PASS_214_VM81_IR_ADAPTER_V1"
CLASSIFICATION = "HHS_PASS_214_GOVERNED_TYPED_IR_ADAPTER"
MAX_REGISTERS = 256
MAX_CALL_DEPTH = 512
DEFAULT_MAX_STEPS = 1 << 20
UINT64_MAX = (1 << 64) - 1


class Pass214IRAdapterError(RuntimeError):
    """Base adapter failure."""


class Pass214IRValidationError(Pass214IRAdapterError):
    """Malformed or non-admissible IR."""


class Pass214IRExecutionError(Pass214IRAdapterError):
    """Execution failed after IR validation."""


class OperandKind(str, Enum):
    REGISTER = "REGISTER"
    IMMEDIATE_U64 = "IMMEDIATE_U64"
    CELL_REF = "CELL_REF"


class IROp(str, Enum):
    NOP = "NOP"
    CONST = "CONST"
    MOVE = "MOVE"

    ADD = "ADD"
    SUB = "SUB"
    XOR = "XOR"
    AND = "AND"
    OR = "OR"
    MUL_MOD = "MUL_MOD"
    ROTL64 = "ROTL64"
    EQ = "EQ"
    SELECT = "SELECT"
    NATIVE = "NATIVE"

    COMPARE_EQ = "COMPARE_EQ"
    COMPARE_NEQ = "COMPARE_NEQ"
    COMPARE_LT = "COMPARE_LT"
    COMPARE_GT = "COMPARE_GT"

    BRANCH_IF = "BRANCH_IF"
    JUMP = "JUMP"
    CALL = "CALL"
    RETURN = "RETURN"
    RECEIPT72 = "RECEIPT72"
    HALT = "HALT"

    # Legacy prototype opcodes that are not admitted as canonical mutations.
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    QGU = "QGU"
    CONSTRAIN = "CONSTRAIN"
    HASH72_PROJECT = "HASH72_PROJECT"


_NATIVE_ID_BY_OP: dict[IROp, str] = {
    IROp.ADD: "hhs.native.u64.add.v1",
    IROp.SUB: "hhs.native.u64.sub.v1",
    IROp.XOR: "hhs.native.u64.xor.v1",
    IROp.AND: "hhs.native.u64.and.v1",
    IROp.OR: "hhs.native.u64.or.v1",
    IROp.MUL_MOD: "hhs.native.u64.mul_mod.v1",
    IROp.ROTL64: "hhs.native.u64.rotl.v1",
    IROp.EQ: "hhs.native.u64.eq.v1",
    IROp.SELECT: "hhs.native.u64.select.v1",
}

_LEGACY_UNADMITTED = {
    IROp.MUL,
    IROp.DIV,
    IROp.MOD,
    IROp.QGU,
    IROp.CONSTRAIN,
    IROp.HASH72_PROJECT,
}


@dataclass(frozen=True)
class IROperand:
    kind: OperandKind
    value: int

    @classmethod
    def register(cls, index: int) -> "IROperand":
        return cls(OperandKind.REGISTER, index)

    @classmethod
    def immediate(cls, value: int) -> "IROperand":
        return cls(OperandKind.IMMEDIATE_U64, value)

    @classmethod
    def cell_ref(cls, index: int) -> "IROperand":
        return cls(OperandKind.CELL_REF, index)


@dataclass(frozen=True)
class IRNode:
    op: IROp
    dst: int | None = None
    operands: tuple[IROperand, ...] = ()
    target_block: int | None = None

    entry_hash216: str | None = None
    operation_id: str | None = None
    native_dispatch_id: str | None = None
    timestamp_ns: int | None = None
    hydration_lane: int = 0
    read_set: tuple[str, ...] = ()
    write_set: tuple[str, ...] = ()


@dataclass(frozen=True)
class IRBlock:
    nodes: tuple[IRNode, ...]


@dataclass(frozen=True)
class IRProgram:
    blocks: tuple[IRBlock, ...]
    entry_block: int = 0


@dataclass
class IRFrame:
    registers: list[int] = field(default_factory=lambda: [0] * MAX_REGISTERS)
    current_block: int = 0
    current_node: int = 0
    last_compare: bool = False
    halted: bool = False
    call_stack: list[tuple[int, int]] = field(default_factory=list)
    dispatch_receipts: list[Mapping[str, Any]] = field(default_factory=list)
    observations: list[Mapping[str, Any]] = field(default_factory=list)
    executed_nodes: int = 0


class _TensorStatePort(Protocol):
    tensor_root_hash216: str


class _RuntimeStatePort(Protocol):
    current_state_root_hash216: str
    previous_receipt_hash72: str
    tensor_state: _TensorStatePort


class _CompiledEntryPort(Protocol):
    native_dispatch_id: str

    def validate(self) -> None: ...


class _ProtectedStorePort(Protocol):
    def lookup_hash216(self, entry_hash216: str) -> _CompiledEntryPort: ...


class GovernedDispatchPort(Protocol):
    runtime_state: _RuntimeStatePort
    protected_store: _ProtectedStorePort

    def execute(self, request: NativeDispatchRequest) -> Any: ...


class _Action(str, Enum):
    CONTINUE = "CONTINUE"
    JUMP = "JUMP"
    CALL = "CALL"
    RETURN = "RETURN"
    HALT = "HALT"


@dataclass(frozen=True)
class _Transfer:
    action: _Action
    target_block: int | None = None


def _strict_u64(value: int, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= UINT64_MAX:
        raise Pass214IRValidationError(code)
    return value


def _require_register(index: int | None, code: str) -> int:
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < MAX_REGISTERS:
        raise Pass214IRValidationError(code)
    return index


def _require_hash216(value: str | None, code: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass214IRValidationError(code)
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass214IRValidationError(code) from exc
    return value


def _require_name(value: str | None, code: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise Pass214IRValidationError(code)
    return value


def _canonical_access_set(values: Sequence[str], code: str) -> tuple[str, ...]:
    items = tuple(str(value) for value in values)
    if items != tuple(sorted(set(items))):
        raise Pass214IRValidationError(code)
    if any(not item or len(item) > 128 for item in items):
        raise Pass214IRValidationError(code)
    return items


class Pass214GovernedIRAdapter:
    """Typed IR scheduler with Pass 213 as the only mutation authority."""

    def __init__(self, *, authority: GovernedDispatchPort) -> None:
        self.authority = authority

    def validate_program(self, program: IRProgram) -> None:
        if not isinstance(program, IRProgram) or not program.blocks:
            raise Pass214IRValidationError("PASS214_IR_PROGRAM_EMPTY")
        if not 0 <= program.entry_block < len(program.blocks):
            raise Pass214IRValidationError("PASS214_IR_ENTRY_BLOCK_INVALID")

        for block_index, block in enumerate(program.blocks):
            if not isinstance(block, IRBlock):
                raise Pass214IRValidationError("PASS214_IR_BLOCK_INVALID")
            for node_index, node in enumerate(block.nodes):
                self._validate_node(program, block_index, node_index, node)

    def _validate_node(
        self,
        program: IRProgram,
        block_index: int,
        node_index: int,
        node: IRNode,
    ) -> None:
        if not isinstance(node, IRNode) or not isinstance(node.op, IROp):
            raise Pass214IRValidationError("PASS214_IR_NODE_INVALID")

        if node.dst is not None:
            _require_register(node.dst, "PASS214_IR_DST_REGISTER_INVALID")

        for operand in node.operands:
            if not isinstance(operand, IROperand):
                raise Pass214IRValidationError("PASS214_IR_OPERAND_INVALID")
            if operand.kind == OperandKind.REGISTER:
                _require_register(operand.value, "PASS214_IR_SRC_REGISTER_INVALID")
            elif operand.kind == OperandKind.IMMEDIATE_U64:
                _strict_u64(operand.value, "PASS214_IR_IMMEDIATE_OUT_OF_RANGE")
            elif operand.kind == OperandKind.CELL_REF:
                raise Pass214IRValidationError(
                    "PASS214_IR_CELL_REF_REQUIRES_EXACT_COMPILED_READ_ADMISSION"
                )
            else:
                raise Pass214IRValidationError("PASS214_IR_OPERAND_KIND_INVALID")

        if node.op in {IROp.BRANCH_IF, IROp.JUMP, IROp.CALL}:
            if (
                isinstance(node.target_block, bool)
                or not isinstance(node.target_block, int)
                or not 0 <= node.target_block < len(program.blocks)
            ):
                raise Pass214IRValidationError("PASS214_IR_TARGET_BLOCK_INVALID")

        if node.op in _LEGACY_UNADMITTED:
            raise Pass214IRValidationError(
                f"PASS214_IR_LEGACY_OPERATION_NOT_ADMITTED:{node.op.value}"
            )

        if node.op in _NATIVE_ID_BY_OP or node.op == IROp.NATIVE:
            if node.dst is None:
                raise Pass214IRValidationError("PASS214_IR_NATIVE_DST_REQUIRED")
            _require_hash216(node.entry_hash216, "PASS214_IR_ENTRY_HASH216_INVALID")
            _require_name(node.operation_id, "PASS214_IR_OPERATION_ID_INVALID")
            if node.op == IROp.NATIVE:
                _require_name(
                    node.native_dispatch_id,
                    "PASS214_IR_NATIVE_DISPATCH_ID_REQUIRED",
                )
            if (
                isinstance(node.timestamp_ns, bool)
                or not isinstance(node.timestamp_ns, int)
                or node.timestamp_ns < 0
            ):
                raise Pass214IRValidationError("PASS214_IR_TIMESTAMP_INVALID")
            if (
                isinstance(node.hydration_lane, bool)
                or not isinstance(node.hydration_lane, int)
                or not 0 <= node.hydration_lane < 40
            ):
                raise Pass214IRValidationError("PASS214_IR_HYDRATION_LANE_INVALID")
            _canonical_access_set(node.read_set, "PASS214_IR_READ_SET_INVALID")
            _canonical_access_set(node.write_set, "PASS214_IR_WRITE_SET_INVALID")

        if node.op == IROp.CONST:
            if node.dst is None or len(node.operands) != 1 or node.operands[0].kind != OperandKind.IMMEDIATE_U64:
                raise Pass214IRValidationError("PASS214_IR_CONST_SHAPE_INVALID")
        elif node.op == IROp.MOVE:
            if node.dst is None or len(node.operands) != 1:
                raise Pass214IRValidationError("PASS214_IR_MOVE_SHAPE_INVALID")
        elif node.op in {
            IROp.COMPARE_EQ,
            IROp.COMPARE_NEQ,
            IROp.COMPARE_LT,
            IROp.COMPARE_GT,
        }:
            if len(node.operands) != 2:
                raise Pass214IRValidationError("PASS214_IR_COMPARE_SHAPE_INVALID")
        elif node.op in _NATIVE_ID_BY_OP or node.op == IROp.NATIVE:
            if not node.operands:
                raise Pass214IRValidationError("PASS214_IR_NATIVE_OPERANDS_REQUIRED")

    def _resolve_operand(self, frame: IRFrame, operand: IROperand) -> int:
        if operand.kind == OperandKind.REGISTER:
            return _strict_u64(
                frame.registers[_require_register(
                    operand.value, "PASS214_IR_SRC_REGISTER_INVALID"
                )],
                "PASS214_IR_REGISTER_VALUE_OUT_OF_RANGE",
            )
        if operand.kind == OperandKind.IMMEDIATE_U64:
            return _strict_u64(operand.value, "PASS214_IR_IMMEDIATE_OUT_OF_RANGE")
        raise Pass214IRExecutionError("PASS214_IR_CELL_REF_BYPASS_FORBIDDEN")

    def _dispatch(self, frame: IRFrame, node: IRNode) -> None:
        expected_native_id = (
            node.native_dispatch_id
            if node.op == IROp.NATIVE
            else _NATIVE_ID_BY_OP[node.op]
        )
        expected_native_id = _require_name(
            expected_native_id, "PASS214_IR_NATIVE_DISPATCH_ID_REQUIRED"
        )
        entry_hash216 = _require_hash216(
            node.entry_hash216, "PASS214_IR_ENTRY_HASH216_INVALID"
        )

        # Read-only preflight prevents an opcode/compiled-entry mismatch from
        # being discovered after the canonical authority has already mutated.
        entry = self.authority.protected_store.lookup_hash216(entry_hash216)
        entry.validate()
        if entry.native_dispatch_id != expected_native_id:
            raise Pass214IRValidationError(
                "PASS214_IR_COMPILED_NATIVE_DISPATCH_MISMATCH"
            )

        state = self.authority.runtime_state
        operands = tuple(self._resolve_operand(frame, item) for item in node.operands)
        request = NativeDispatchRequest(
            entry_hash216=entry_hash216,
            operation_id=_require_name(
                node.operation_id, "PASS214_IR_OPERATION_ID_INVALID"
            ),
            expected_parent_hash216=state.current_state_root_hash216,
            expected_tensor_root_hash216=state.tensor_state.tensor_root_hash216,
            timestamp_ns=int(node.timestamp_ns),
            hydration_lane=node.hydration_lane,
            operands=operands,
            read_set=_canonical_access_set(
                node.read_set, "PASS214_IR_READ_SET_INVALID"
            ),
            write_set=_canonical_access_set(
                node.write_set, "PASS214_IR_WRITE_SET_INVALID"
            ),
        )
        request.validate()

        receipt = self.authority.execute(request)
        if getattr(receipt, "native_dispatch_id", None) != expected_native_id:
            raise Pass214IRExecutionError(
                "PASS214_IR_AUTHORITY_RECEIPT_NATIVE_ID_MISMATCH"
            )
        results = tuple(getattr(receipt, "result_values", ()))
        if len(results) != 1:
            raise Pass214IRExecutionError("PASS214_IR_NATIVE_RESULT_COUNT_INVALID")
        frame.registers[_require_register(
            node.dst, "PASS214_IR_NATIVE_DST_REQUIRED"
        )] = _strict_u64(results[0], "PASS214_IR_NATIVE_RESULT_OUT_OF_RANGE")

        mapping = receipt.to_mapping() if hasattr(receipt, "to_mapping") else {
            "native_dispatch_id": expected_native_id,
            "result_values": results,
        }
        frame.dispatch_receipts.append(mapping)

    def _execute_node(self, frame: IRFrame, node: IRNode) -> _Transfer:
        op = node.op
        if op == IROp.NOP:
            return _Transfer(_Action.CONTINUE)
        if op == IROp.CONST:
            frame.registers[_require_register(
                node.dst, "PASS214_IR_DST_REGISTER_INVALID"
            )] = self._resolve_operand(frame, node.operands[0])
            return _Transfer(_Action.CONTINUE)
        if op == IROp.MOVE:
            frame.registers[_require_register(
                node.dst, "PASS214_IR_DST_REGISTER_INVALID"
            )] = self._resolve_operand(frame, node.operands[0])
            return _Transfer(_Action.CONTINUE)
        if op in _NATIVE_ID_BY_OP or op == IROp.NATIVE:
            self._dispatch(frame, node)
            return _Transfer(_Action.CONTINUE)
        if op in {
            IROp.COMPARE_EQ,
            IROp.COMPARE_NEQ,
            IROp.COMPARE_LT,
            IROp.COMPARE_GT,
        }:
            left = self._resolve_operand(frame, node.operands[0])
            right = self._resolve_operand(frame, node.operands[1])
            if op == IROp.COMPARE_EQ:
                frame.last_compare = left == right
            elif op == IROp.COMPARE_NEQ:
                frame.last_compare = left != right
            elif op == IROp.COMPARE_LT:
                frame.last_compare = left < right
            else:
                frame.last_compare = left > right
            return _Transfer(_Action.CONTINUE)
        if op == IROp.BRANCH_IF:
            if frame.last_compare:
                return _Transfer(_Action.JUMP, node.target_block)
            return _Transfer(_Action.CONTINUE)
        if op == IROp.JUMP:
            return _Transfer(_Action.JUMP, node.target_block)
        if op == IROp.CALL:
            return _Transfer(_Action.CALL, node.target_block)
        if op == IROp.RETURN:
            return _Transfer(_Action.RETURN)
        if op == IROp.RECEIPT72:
            state = self.authority.runtime_state
            frame.observations.append({
                "schema": SCHEMA,
                "kind": "CANONICAL_RECEIPT_HASH72_OBSERVATION",
                "receipt_hash72": state.previous_receipt_hash72,
                "canonical_runtime_mutated": False,
            })
            return _Transfer(_Action.CONTINUE)
        if op == IROp.HALT:
            return _Transfer(_Action.HALT)
        if op in _LEGACY_UNADMITTED:
            raise Pass214IRExecutionError(
                f"PASS214_IR_LEGACY_OPERATION_BYPASS_FORBIDDEN:{op.value}"
            )
        raise Pass214IRExecutionError("PASS214_IR_OPCODE_UNHANDLED")

    def run(
        self,
        program: IRProgram,
        *,
        frame: IRFrame | None = None,
        max_steps: int = DEFAULT_MAX_STEPS,
    ) -> IRFrame:
        self.validate_program(program)
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
            raise Pass214IRValidationError("PASS214_IR_MAX_STEPS_INVALID")

        target = frame or IRFrame()
        if target.executed_nodes == 0 and target.current_block == 0 and target.current_node == 0:
            target.current_block = program.entry_block

        while not target.halted:
            if target.executed_nodes >= max_steps:
                raise Pass214IRExecutionError("PASS214_IR_BOUNDED_EXECUTION_EXCEEDED")
            if not 0 <= target.current_block < len(program.blocks):
                raise Pass214IRExecutionError("PASS214_IR_RUNTIME_BLOCK_OUT_OF_RANGE")

            block = program.blocks[target.current_block]
            if target.current_node >= len(block.nodes):
                if target.current_block + 1 >= len(program.blocks):
                    target.halted = True
                    break
                target.current_block += 1
                target.current_node = 0
                continue

            node = block.nodes[target.current_node]
            transfer = self._execute_node(target, node)
            target.executed_nodes += 1

            if transfer.action == _Action.CONTINUE:
                target.current_node += 1
            elif transfer.action == _Action.JUMP:
                target.current_block = int(transfer.target_block)
                target.current_node = 0
            elif transfer.action == _Action.CALL:
                if len(target.call_stack) >= MAX_CALL_DEPTH:
                    raise Pass214IRExecutionError("PASS214_IR_CALL_STACK_OVERFLOW")
                target.call_stack.append((target.current_block, target.current_node + 1))
                target.current_block = int(transfer.target_block)
                target.current_node = 0
            elif transfer.action == _Action.RETURN:
                if not target.call_stack:
                    raise Pass214IRExecutionError("PASS214_IR_RETURN_WITHOUT_CALL")
                target.current_block, target.current_node = target.call_stack.pop()
            elif transfer.action == _Action.HALT:
                target.halted = True
            else:
                raise Pass214IRExecutionError("PASS214_IR_CONTROL_TRANSFER_INVALID")

        return target


__all__ = [
    "SCHEMA",
    "CLASSIFICATION",
    "MAX_REGISTERS",
    "MAX_CALL_DEPTH",
    "DEFAULT_MAX_STEPS",
    "Pass214IRAdapterError",
    "Pass214IRValidationError",
    "Pass214IRExecutionError",
    "OperandKind",
    "IROp",
    "IROperand",
    "IRNode",
    "IRBlock",
    "IRProgram",
    "IRFrame",
    "GovernedDispatchPort",
    "Pass214GovernedIRAdapter",
]
