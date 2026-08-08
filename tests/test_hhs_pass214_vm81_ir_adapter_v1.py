from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha1
from pathlib import Path
import unittest

from hhs_backend.runtime.hhs_pass214_vm81_ir_adapter_v1 import (
    IRBlock,
    IRNode,
    IROp,
    IROperand,
    IRProgram,
    Pass214GovernedIRAdapter,
    Pass214IRValidationError,
)

ROOT = Path(__file__).resolve().parents[1]
FROZEN_RUNTIME = ROOT / "hhs_runtime/HARMONICODE_VM_RUNTIME.c"
FROZEN_RUNTIME_GIT_BLOB_SHA1 = "362cd6e892ae66024333b111aec83f12023fdce3"

H_ENTRY = "1" * 64
H_PARENT = "2" * 64
H_TENSOR = "3" * 64
H_SUCCESSOR = "4" * 64
R_ANCHOR = "0" * 72
R_SUCCESSOR = "a" * 72


@dataclass
class _Tensor:
    tensor_root_hash216: str = H_TENSOR


@dataclass
class _State:
    current_state_root_hash216: str = H_PARENT
    previous_receipt_hash72: str = R_ANCHOR
    tensor_state: _Tensor = field(default_factory=_Tensor)


class _Entry:
    def __init__(self, native_dispatch_id: str) -> None:
        self.native_dispatch_id = native_dispatch_id
        self.validated = False

    def validate(self) -> None:
        self.validated = True


class _Store:
    def __init__(self, entry: _Entry) -> None:
        self.entry = entry
        self.lookups: list[str] = []

    def lookup_hash216(self, entry_hash216: str) -> _Entry:
        self.lookups.append(entry_hash216)
        return self.entry


class _Receipt:
    def __init__(self, native_dispatch_id: str, result: int) -> None:
        self.native_dispatch_id = native_dispatch_id
        self.result_values = (result,)
        self.successor_state_root_hash216 = H_SUCCESSOR
        self.receipt_hash72 = R_SUCCESSOR

    def to_mapping(self) -> dict[str, object]:
        return {
            "native_dispatch_id": self.native_dispatch_id,
            "result_values": self.result_values,
            "successor_state_root_hash216": self.successor_state_root_hash216,
            "receipt_hash72": self.receipt_hash72,
            "singleton_vm81_admission": True,
        }


class _Authority:
    def __init__(self, native_dispatch_id: str = "hhs.native.u64.add.v1") -> None:
        self.protected_store = _Store(_Entry(native_dispatch_id))
        self.runtime_state = _State()
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        native_id = self.protected_store.entry.native_dispatch_id
        values = tuple(request.operands)
        if native_id == "hhs.native.u64.add.v1":
            result = (values[0] + values[1]) & ((1 << 64) - 1)
        elif native_id == "hhs.native.u64.sub.v1":
            result = (values[0] - values[1]) & ((1 << 64) - 1)
        elif native_id == "hhs.native.u64.eq.v1":
            result = int(values[0] == values[1])
        else:
            result = values[0]
        self.runtime_state = _State(
            current_state_root_hash216=H_SUCCESSOR,
            previous_receipt_hash72=R_SUCCESSOR,
            tensor_state=self.runtime_state.tensor_state,
        )
        return _Receipt(native_id, result)


def _git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def _add_node(*, timestamp_ns: int = 10) -> IRNode:
    return IRNode(
        op=IROp.ADD,
        dst=2,
        operands=(IROperand.register(0), IROperand.register(1)),
        entry_hash216=H_ENTRY,
        operation_id="PASS214_TEST_ADD",
        timestamp_ns=timestamp_ns,
        hydration_lane=0,
        read_set=("register.a", "register.b"),
        write_set=("register.result",),
    )


class Pass214GovernedIRAdapterTests(unittest.TestCase):
    def test_frozen_runtime_blob_is_unchanged(self) -> None:
        self.assertEqual(_git_blob_sha1(FROZEN_RUNTIME), FROZEN_RUNTIME_GIT_BLOB_SHA1)

    def test_adapter_source_has_no_direct_frozen_vm_mutation_path(self) -> None:
        source = (ROOT / "hhs_backend/runtime/hhs_pass214_vm81_ir_adapter_v1.py").read_text()
        for forbidden in (
            "apply_instruction(",
            "vm81_step(",
            "#include \"HARMONICODE_VM_RUNTIME.c\"",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("NativeDispatchRequest", source)
        self.assertIn("self.authority.execute(request)", source)

    def test_scalar_add_routes_through_single_governed_authority(self) -> None:
        authority = _Authority()
        adapter = Pass214GovernedIRAdapter(authority=authority)
        program = IRProgram(
            blocks=(
                IRBlock(nodes=(
                    IRNode(op=IROp.CONST, dst=0, operands=(IROperand.immediate(5),)),
                    IRNode(op=IROp.CONST, dst=1, operands=(IROperand.immediate(7),)),
                    _add_node(),
                    IRNode(op=IROp.HALT),
                )),
            )
        )
        frame = adapter.run(program)
        self.assertEqual(frame.registers[2], 12)
        self.assertEqual(len(authority.requests), 1)
        request = authority.requests[0]
        self.assertEqual(request.operands, (5, 7))
        self.assertEqual(request.expected_parent_hash216, H_PARENT)
        self.assertEqual(request.expected_tensor_root_hash216, H_TENSOR)
        self.assertEqual(len(frame.dispatch_receipts), 1)
        self.assertTrue(frame.dispatch_receipts[0]["singleton_vm81_admission"])

    def test_compiled_dispatch_mismatch_fails_before_mutation(self) -> None:
        authority = _Authority(native_dispatch_id="hhs.native.u64.sub.v1")
        adapter = Pass214GovernedIRAdapter(authority=authority)
        program = IRProgram(
            blocks=(IRBlock(nodes=(
                IRNode(op=IROp.CONST, dst=0, operands=(IROperand.immediate(5),)),
                IRNode(op=IROp.CONST, dst=1, operands=(IROperand.immediate(7),)),
                _add_node(),
            )),)
        )
        with self.assertRaisesRegex(
            Pass214IRValidationError, "COMPILED_NATIVE_DISPATCH_MISMATCH"
        ):
            adapter.run(program)
        self.assertEqual(authority.requests, [])

    def test_cell_reference_ambiguity_is_rejected_not_reinterpreted(self) -> None:
        authority = _Authority()
        adapter = Pass214GovernedIRAdapter(authority=authority)
        program = IRProgram(
            blocks=(IRBlock(nodes=(
                IRNode(op=IROp.MOVE, dst=0, operands=(IROperand.cell_ref(5),)),
            )),)
        )
        with self.assertRaisesRegex(Pass214IRValidationError, "CELL_REF"):
            adapter.run(program)
        self.assertEqual(authority.requests, [])

    def test_legacy_unadmitted_mutations_fail_closed(self) -> None:
        for op in (IROp.MUL, IROp.DIV, IROp.MOD, IROp.QGU, IROp.CONSTRAIN, IROp.HASH72_PROJECT):
            authority = _Authority()
            adapter = Pass214GovernedIRAdapter(authority=authority)
            program = IRProgram(blocks=(IRBlock(nodes=(IRNode(op=op),)),))
            with self.assertRaisesRegex(Pass214IRValidationError, "NOT_ADMITTED"):
                adapter.run(program)
            self.assertEqual(authority.requests, [])

    def test_branch_transfer_switches_block_without_stale_block_execution(self) -> None:
        authority = _Authority()
        adapter = Pass214GovernedIRAdapter(authority=authority)
        program = IRProgram(
            blocks=(
                IRBlock(nodes=(
                    IRNode(op=IROp.CONST, dst=0, operands=(IROperand.immediate(9),)),
                    IRNode(op=IROp.CONST, dst=1, operands=(IROperand.immediate(9),)),
                    IRNode(
                        op=IROp.COMPARE_EQ,
                        operands=(IROperand.register(0), IROperand.register(1)),
                    ),
                    IRNode(op=IROp.BRANCH_IF, target_block=2),
                )),
                IRBlock(nodes=(
                    IRNode(op=IROp.CONST, dst=5, operands=(IROperand.immediate(99),)),
                    IRNode(op=IROp.HALT),
                )),
                IRBlock(nodes=(
                    IRNode(op=IROp.CONST, dst=5, operands=(IROperand.immediate(42),)),
                    IRNode(op=IROp.HALT),
                )),
            )
        )
        frame = adapter.run(program)
        self.assertEqual(frame.registers[5], 42)
        self.assertTrue(frame.halted)

    def test_call_and_return_restore_exact_continuation(self) -> None:
        authority = _Authority()
        adapter = Pass214GovernedIRAdapter(authority=authority)
        program = IRProgram(
            blocks=(
                IRBlock(nodes=(
                    IRNode(op=IROp.CALL, target_block=1),
                    IRNode(op=IROp.CONST, dst=7, operands=(IROperand.immediate(22),)),
                    IRNode(op=IROp.HALT),
                )),
                IRBlock(nodes=(
                    IRNode(op=IROp.CONST, dst=6, operands=(IROperand.immediate(11),)),
                    IRNode(op=IROp.RETURN),
                )),
            )
        )
        frame = adapter.run(program)
        self.assertEqual(frame.registers[6], 11)
        self.assertEqual(frame.registers[7], 22)
        self.assertEqual(frame.call_stack, [])

    def test_receipt72_is_observation_not_projection_identity(self) -> None:
        authority = _Authority()
        adapter = Pass214GovernedIRAdapter(authority=authority)
        program = IRProgram(
            blocks=(IRBlock(nodes=(
                IRNode(op=IROp.RECEIPT72),
                IRNode(op=IROp.HALT),
            )),)
        )
        frame = adapter.run(program)
        self.assertEqual(authority.requests, [])
        self.assertEqual(frame.observations[0]["receipt_hash72"], R_ANCHOR)
        self.assertFalse(frame.observations[0]["canonical_runtime_mutated"])


if __name__ == "__main__":
    unittest.main()
