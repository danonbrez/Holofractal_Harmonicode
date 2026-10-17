"""Native C ABI HIR candidate binding tests; NO canonical admission authority."""
from pathlib import Path

from hhs_runtime.pass220.hhs_pass220_ordered4x4_native_hir_bridge_v1 import (
    Ordered4x4NativeHIRBridge,
)

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "hhs_runtime/builds/libhhs_runtime.so"


def test_native_lowering_is_source_locked_and_deterministic():
    assert LIB.is_file(), "dependency-scoped native exact ABI must be built first"
    bridge = Ordered4x4NativeHIRBridge(LIB)
    first = bridge.lower(root=ROOT)
    replay = bridge.lower(root=ROOT)
    assert first == replay
    assert len(first.words) == 81
    assert first.source_sha256 == "a3ba5ca5f31ee76261e5df75c7e9f43a78219d59df36a095a07c0acdf90dbd19"
    assert len(first.topology_sha256) == 64
    assert first.words[0] == 0x483232304e344d50
    assert first.words[2] == 0x2d34
    assert first.words[4] == 1
    assert first.words[8] & 0xff == 255
    assert first.words[67] == (3 << 16) | (15 << 8)
    assert first.words[80] == 0x7673
    assert first.typed_s_unresolved
    assert first.typed_v_unresolved
    assert first.source_identity_verified
    assert first.ordered_topology_verified
    assert not first.vm81_admission_executed
    assert not first.matrix_power_value_derived
    assert not first.hash72_commit_authority
    assert not first.hash216_commit_authority
    assert not first.canonical_vm81_mutation_authority
