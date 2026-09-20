from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactRuntimeBridge

from hhs_runtime.harmonicode_lane5_rna_self_ingestion_bytecode_v1 import (
    all_triplets,
    compact_word,
    multiplicative_word,
    typed_native_code,
)


def test_native_bytecode_membrane_roundtrips_all_self_ingestion_payloads():
    bridge = HHSExactRuntimeBridge()
    assert bridge.validate() is True
    count = 0
    for state in all_triplets():
        compact = compact_word(state).encode("ascii")
        explicit = multiplicative_word(state).encode("ascii")
        native = bytes((typed_native_code(state)["operation64"],))
        assert bridge.x86_bytecode_roundtrip(compact) == compact
        assert bridge.x86_bytecode_roundtrip(explicit) == explicit
        assert bridge.x86_bytecode_roundtrip(native) == native
        count += 1
    assert count == 64
