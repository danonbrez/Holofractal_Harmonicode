"""Native typed s/v provenance-binding conformance, not matrix-value admission."""
from pathlib import Path
import pytest

from hhs_runtime.pass220.hhs_pass220_ordered4x4_typed_bindings_v1 import (
    AddressedTensorBinding, NativeOrdered4x4BoundExecutor,
)
from hhs_runtime.pass220.hhs_pass220_ordered_4x4_neg4_matrix_tensor_v1 import MatrixTensorHIRReject

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "hhs_runtime/builds/libhhs_runtime.so"
PARENT = "R" * 216


def _binding(name, marker, cell=4, opcode=9, predecessor=PARENT):
    return AddressedTensorBinding(
        symbol=name,
        vm81_cell=cell,
        vm81_operation=opcode,
        harmonicode_5184=marker * 5184,
        predecessor_hash216=predecessor,
    )


def test_bound_native_tensor_roots_track_each_symbol_separately():
    assert LIB.is_file(), "compiled native exact ABI required"
    executor = NativeOrdered4x4BoundExecutor(LIB)
    s = _binding("s", "A", 4, 9)
    v = _binding("v", "B", 8, 17)
    a = executor.execute(s, v, root=ROOT)
    assert a == executor.execute(s, v, root=ROOT)
    assert (a.s_address, a.v_address) == (265, 529)
    assert (a.s_utf8_bytes, a.v_utf8_bytes) == (5184, 5184)
    assert a.ordered_steps == 15
    assert a.source_verified and a.bound_symbolic_execution_verified
    assert a.deterministic_bound_replay_verified
    assert not a.native_binding_authenticity_verified
    assert not a.equation_equality_proved and not a.matrix_value_derived
    assert not a.vm81_admission_executed and not a.hash72_commit_authority and not a.hash216_commit_authority

    s2 = _binding("s", "C", 4, 9)
    changed_s = executor.execute(s2, v, root=ROOT)
    assert changed_s.ordered_node_roots_sha256[10] != a.ordered_node_roots_sha256[10]
    assert changed_s.ordered_node_roots_sha256[13] == a.ordered_node_roots_sha256[13]
    v2 = _binding("v", "D", 8, 17)
    changed_v = executor.execute(s, v2, root=ROOT)
    assert changed_v.ordered_node_roots_sha256[10] == a.ordered_node_roots_sha256[10]
    assert changed_v.ordered_node_roots_sha256[13] != a.ordered_node_roots_sha256[13]

    changed_address = executor.execute(_binding("s", "A", 5, 9), v, root=ROOT)
    assert changed_address.binding_roots_sha256[0] != a.binding_roots_sha256[0]

    unicode_s = AddressedTensorBinding("s", 4, 9, "Δ" + "A" * 5183, PARENT)
    unicode_result = executor.execute(unicode_s, v, root=ROOT)
    assert unicode_result.s_utf8_bytes == 5185
    assert unicode_result.s_address == 265


@pytest.mark.parametrize("invalid", [
    lambda s,v: (AddressedTensorBinding("v",s.vm81_cell,s.vm81_operation,s.harmonicode_5184,PARENT),v),
    lambda s,v: (AddressedTensorBinding("s",81,9,s.harmonicode_5184,PARENT),v),
    lambda s,v: (AddressedTensorBinding("s",4,64,s.harmonicode_5184,PARENT),v),
    lambda s,v: (AddressedTensorBinding("s",True,9,s.harmonicode_5184,PARENT),v),
    lambda s,v: (AddressedTensorBinding("s",4,9,"A"*5183,PARENT),v),
    lambda s,v: (AddressedTensorBinding("s",4,9,"A"*5184,"R"*215),v),
    lambda s,v: (s,AddressedTensorBinding("v",8,17,"B"*5184,"S"*216)),
    lambda s,v: (AddressedTensorBinding("s",4,9,"\x00"+"A"*5183,PARENT),v),
])
def test_invalid_typed_binding_fails_closed(invalid):
    assert LIB.is_file()
    executor = NativeOrdered4x4BoundExecutor(LIB)
    s,v = invalid(_binding("s","A"), _binding("v","B",8,17))
    with pytest.raises(MatrixTensorHIRReject):
        executor.execute(s,v,root=ROOT)
