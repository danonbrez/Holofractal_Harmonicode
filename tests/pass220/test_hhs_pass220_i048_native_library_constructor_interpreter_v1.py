from __future__ import annotations

import ctypes
import struct
import subprocess

import pytest

from hhs_runtime.hhs_pass220_i047_native_library_training_dataset_v1 import (
    REFERENCE_ORIGIN,
    build_library_training_record,
    typed_value_from_bytes,
)
from hhs_runtime.hhs_pass220_i048_native_library_constructor_interpreter_v1 import (
    Pass220I048InterpreterError,
    build_constructor_registry,
    build_native_constructor_binding,
    constructor_equivalence_witness,
    i048_self_test,
    interpret_library_call,
    validate_interpreter_plan,
    validate_native_constructor_binding,
)


def _compile_library(tmp_path):
    source = tmp_path / "i048_fixture.c"
    source.write_text(
        "#include <stdint.h>\n"
        "int64_t hhs_affine_i64(int64_t x,int64_t y){return x*3+y*2;}\n",
        encoding="utf-8",
    )
    shared = tmp_path / "libi048_fixture.so"
    subprocess.run(
        [
            "cc",
            "-shared",
            "-fPIC",
            "-std=c11",
            "-O2",
            str(source),
            "-o",
            str(shared),
        ],
        check=True,
    )
    return shared


def _i64(value: int):
    return typed_value_from_bytes(
        data_type="i64",
        encoding="little-endian-twos-complement",
        payload=struct.pack("<q", value),
        semantic_value=str(value),
    )


def _record(tmp_path, *, side_effect_class="PURE"):
    shared = _compile_library(tmp_path)
    function = ctypes.CDLL(str(shared)).hhs_affine_i64
    function.argtypes = [ctypes.c_int64, ctypes.c_int64]
    function.restype = ctypes.c_int64
    raw = shared.read_bytes()
    metadata = {
        "library_id": "i048-affine",
        "library_format": "ELF_SHARED_OBJECT",
        "architecture": "x86_64",
        "abi": "SYSV_AMD64",
        "provenance": "I048_TEST_SOURCE_LIBRARY",
        "codec_boundary": {
            "ingress_encoder_id": "I64_IN",
            "egress_decoder_id": "I64_OUT",
            "preserve_external_contract": True,
        },
        "byte_regions": [
            {
                "region_id": "IMAGE",
                "start": 0,
                "length": len(raw),
                "kind": "RAW_LIBRARY_BYTES",
            }
        ],
        "entrypoints": [
            {
                "entrypoint_id": "affine",
                "symbol": "hhs_affine_i64",
                "inputs": [
                    {
                        "name": "x",
                        "data_type": "i64",
                        "encoding": "little-endian-twos-complement",
                    },
                    {
                        "name": "y",
                        "data_type": "i64",
                        "encoding": "little-endian-twos-complement",
                    },
                ],
                "outputs": [
                    {
                        "name": "return",
                        "data_type": "i64",
                        "encoding": "little-endian-twos-complement",
                    }
                ],
                "side_effect_class": side_effect_class,
                "state_boundary": "NONE",
                "math_operator_identities": ["MUL_I64", "ADD_I64"],
                "constructor_dependencies": [],
                "phase_relationships": ["ORDERED_DEPENDENCY"],
                "timing_constraints": [
                    "SOURCE_ORDER_NOT_SCHEDULER_AUTHORITY"
                ],
                "vm81_relationships": ["LANE5_BIND"],
                "rna_relationships": ["LANE5_TRANSCRIBE"],
            }
        ],
        "relationships": [
            {
                "relation_id": "R0",
                "relation_type": "BYTE_REGION_CONTAINS_SYMBOL",
                "source": "IMAGE",
                "target": "affine",
                "order": 0,
                "attributes": {},
            }
        ],
        "dependencies": [],
        "hash72_hash216_lineage_hints": [
            "BIND_AT_LANE5_HYDRATION"
        ],
    }
    vectors = []
    for index, (x, y) in enumerate(
        ((0, 0), (1, 2), (-7, 9), (1234567, -765432))
    ):
        observed = int(function(x, y))
        vectors.append(
            {
                "vector_id": f"v{index}",
                "entrypoint_id": "affine",
                "reference_origin": REFERENCE_ORIGIN,
                "inputs": [_i64(x), _i64(y)],
                "outputs": [_i64(observed)],
                "observation": {
                    "source_library_invoked": True,
                    "observed_output": True,
                    "captured_by": "ctypes-source-library",
                },
            }
        )
    return build_library_training_record(
        source_bytes=raw,
        metadata=metadata,
        reference_vectors=vectors,
    )


def test_self_test():
    assert i048_self_test()["ok"] is True


def test_binding_preserves_external_contract_and_read_only_compiler(tmp_path):
    record = _record(tmp_path)
    binding = build_native_constructor_binding(record, "affine")
    assert validate_native_constructor_binding(binding, record)["ok"]
    assert binding["abi"] == "SYSV_AMD64"
    assert binding["inputs"] == record["metadata"]["entrypoints"][0]["inputs"]
    assert binding["outputs"] == record["metadata"]["entrypoints"][0]["outputs"]
    assert binding["codec_boundary"] == record["metadata"]["codec_boundary"]
    assert binding["compiler_ir_artifact"]["target"] == "HHS_IR"
    assert binding["compiler_ir_artifact"]["execution_authorized"] is False
    assert binding["execution_authorized"] is False
    assert binding["canonical_vm81_mutation_authority"] is False
    assert binding["canonical_hash72_mint_authority"] is False
    assert binding["canonical_hash216_persistence_authority"] is False


def test_reference_inputs_replay_source_observed_outputs_exactly(tmp_path):
    record = _record(tmp_path)
    for vector in record["reference_vectors"]:
        plan = interpret_library_call(
            record,
            "affine",
            vector["inputs"],
        )
        assert validate_interpreter_plan(plan, record)["ok"]
        assert plan["status"] == "REFERENCE_VECTOR_REPLAY_ADMITTED"
        assert plan["result_origin"] == REFERENCE_ORIGIN
        assert tuple(plan["outputs"]) == tuple(vector["outputs"])
        assert plan["interpreter_fabricated_result"] is False


def test_unseen_input_fails_closed_without_fabricated_result(tmp_path):
    record = _record(tmp_path)
    plan = interpret_library_call(
        record,
        "affine",
        [_i64(41), _i64(17)],
    )
    assert validate_interpreter_plan(plan, record)["ok"]
    assert plan["status"] == "NATIVE_CONSTRUCTOR_EXECUTION_REQUIRED"
    assert plan["runtime_adapter_required"] is True
    assert plan["lane5_native_constructor_required_for_unseen_inputs"] is True
    assert tuple(plan["outputs"]) == ()
    assert plan["generalized_constructor_equivalence_claimed"] is False


@pytest.mark.parametrize("effect", ("STATEFUL_BOUNDED", "IO_BOUNDED", "OPAQUE_FOREIGN"))
def test_effectful_reference_vector_requires_explicit_runtime_admission(
    tmp_path,
    effect,
):
    record = _record(tmp_path, side_effect_class=effect)
    vector = record["reference_vectors"][0]
    plan = interpret_library_call(record, "affine", vector["inputs"])
    assert validate_interpreter_plan(plan, record)["ok"]
    assert plan["reference_vector_exact_match"] is True
    assert plan["status"] == "EXPLICIT_RUNTIME_ADMISSION_REQUIRED"
    assert plan["runtime_adapter_required"] is True
    assert tuple(plan["outputs"]) == ()


def test_equivalence_witness_is_exact_but_does_not_overclaim(tmp_path):
    record = _record(tmp_path)
    witness = constructor_equivalence_witness(record, "affine")
    assert witness["reference_vector_count"] == 4
    assert witness["all_replayable_reference_outputs_exact"] is True
    assert witness["external_input_contract_exact"] is True
    assert witness["external_output_contract_exact"] is True
    assert witness["codec_membrane_exact"] is True
    assert witness["generalized_constructor_equivalence_proven"] is False
    assert witness["unseen_input_execution_requires_native_constructor"] is True


def test_registry_is_deterministic_for_same_i047_record(tmp_path):
    record = _record(tmp_path)
    first = build_constructor_registry((record,))
    second = build_constructor_registry((record,))
    assert first == second
    assert first["binding_count"] == 1
    assert first["external_contracts_preserved"] is True
    assert first["generalized_execution_authorized"] is False


def test_input_type_drift_rejected_before_interpretation(tmp_path):
    record = _record(tmp_path)
    bad = dict(record["reference_vectors"][0]["inputs"][0])
    bad["data_type"] = "u64"
    with pytest.raises(
        Pass220I048InterpreterError,
        match="external type/encoding drift",
    ):
        interpret_library_call(
            record,
            "affine",
            [bad, record["reference_vectors"][0]["inputs"][1]],
        )


def test_tampered_binding_rejected(tmp_path):
    record = _record(tmp_path)
    binding = build_native_constructor_binding(record, "affine")
    tampered = dict(binding, abi="WRONG_ABI")
    with pytest.raises(
        Pass220I048InterpreterError,
        match="constructor binding identity mismatch",
    ):
        validate_native_constructor_binding(tampered, record)
