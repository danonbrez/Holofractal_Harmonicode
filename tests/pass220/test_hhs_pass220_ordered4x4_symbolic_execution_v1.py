"""Pass220 exact native symbolic 4x4 ordered operator execution, no value claims."""
from pathlib import Path

from hhs_runtime.pass220.hhs_pass220_ordered4x4_symbolic_execution_v1 import (
    NativeOrdered4x4SymbolicExecutor,
)

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "hhs_runtime/builds/libhhs_runtime.so"


def test_exact_symbolic_operator_sequence_and_replay():
    assert LIB.is_file(), "dependency-scoped c-abi build required"
    executor = NativeOrdered4x4SymbolicExecutor(LIB)
    a = executor.execute(root=ROOT)
    b = executor.execute(root=ROOT)
    assert a == b
    assert a.operator_steps == 15
    assert a.maximum_stack_depth == 3
    assert (a.matrices_bound, a.symbols_bound) == (4, 2)
    assert len(a.ordered_node_roots) == 15
    assert len(set(a.ordered_node_roots)) == 15
    assert a.ordered_node_roots[-1] == a.result_root_sha256
    assert a.source_sha256 == "a3ba5ca5f31ee76261e5df75c7e9f43a78219d59df36a095a07c0acdf90dbd19"
    assert a.exact_symbolic_program_executed
    assert a.deterministic_symbolic_replay_verified
    assert not a.expression_equality_proved
    assert not a.matrix_power_value_derived
    assert not a.vm81_admission_executed
    assert not a.hash72_commit_authority
    assert not a.hash216_commit_authority
