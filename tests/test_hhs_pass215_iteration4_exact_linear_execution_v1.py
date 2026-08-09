from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import struct

import pytest

from hhs_backend.runtime.hhs_pass215_iteration2_open_transformer_container_v1 import (
    STORAGE_QUANTIZED,
    ContainerTensor,
)
from hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v1 import (
    FROZEN_COMPARISONS,
    FROZEN_MODES,
    FROZEN_OPTIMIZATION_CLASSES,
    PASS214_STAGES,
    TARGET_OPERATORS,
    Pass215Iteration4ValidationError,
    build_execution_evidence,
    compile_q4_tensor,
    decode_binary16_exact,
    decode_q4_0_codes,
    deterministic_vector,
    execute_continuation_delta,
    execute_dense_reference,
    execute_factored,
    mutated_vector,
)
from hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v2 import (
    validate_execution_evidence,
)


def _q4_block(seed: int = 0) -> bytes:
    scale_one = bytes.fromhex("003c")
    codes = bytes(((seed * 17 + index * 13 + 5) & 0xFF) for index in range(16))
    return scale_one + codes


def _tensor(name: str, ne0: int, ne1: int, payload: bytes) -> ContainerTensor:
    return ContainerTensor(
        name=name,
        shape=(ne0, ne1),
        storage_type="Q4_0",
        storage_type_code=2,
        storage_class=STORAGE_QUANTIZED,
        data_offset=0,
        data_size=len(payload),
        source_sha256=sha256(payload).hexdigest(),
        block_elements=32,
        block_bytes=18,
        header_index=0,
    )


def _gguf_string(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack("<Q", len(raw)) + raw


def _align(value: int, alignment: int = 32) -> int:
    return (value + alignment - 1) // alignment * alignment


def _build_full_target_fixture() -> bytes:
    metadata = bytearray()
    metadata += _gguf_string("general.architecture")
    metadata += struct.pack("<I", 8)
    metadata += _gguf_string("llama")
    metadata += _gguf_string("general.alignment")
    metadata += struct.pack("<I", 4)
    metadata += struct.pack("<I", 32)

    payloads: list[tuple[str, tuple[int, int], int, bytes]] = []
    cursor = 0
    for operator_index, (name, shape) in enumerate(TARGET_OPERATORS.items()):
        ne0, ne1 = shape
        block_count = ne1 * (ne0 // 32)
        payload = b"".join(_q4_block((operator_index + block_index) % 251) for block_index in range(block_count))
        cursor = _align(cursor)
        payloads.append((name, shape, cursor, payload))
        cursor += len(payload)

    infos = bytearray()
    for name, shape, relative_offset, _payload in payloads:
        infos += _gguf_string(name)
        infos += struct.pack("<I", 2)
        infos += struct.pack("<QQ", shape[0], shape[1])
        infos += struct.pack("<I", 2)
        infos += struct.pack("<Q", relative_offset)

    prefix = b"GGUF" + struct.pack("<IQQ", 3, len(payloads), 2) + bytes(metadata) + bytes(infos)
    data_start = _align(len(prefix))
    data = bytearray(b"\x00" * cursor)
    for _name, _shape, relative_offset, payload in payloads:
        data[relative_offset : relative_offset + len(payload)] = payload
    return prefix + b"\x00" * (data_start - len(prefix)) + bytes(data)


def test_binary16_exact_integer_decode_and_special_rejection() -> None:
    assert decode_binary16_exact(bytes.fromhex("003c")) == (1, 1)
    assert decode_binary16_exact(bytes.fromhex("00c0")) == (-2, 1)
    assert decode_binary16_exact(bytes.fromhex("0100")) == (1, 1 << 24)
    assert decode_binary16_exact(bytes.fromhex("0000")) == (0, 1)
    assert decode_binary16_exact(bytes.fromhex("0080")) == (0, 1)
    with pytest.raises(Pass215Iteration4ValidationError, match="NAN_OR_INFINITY"):
        decode_binary16_exact(bytes.fromhex("007c"))
    with pytest.raises(Pass215Iteration4ValidationError, match="NAN_OR_INFINITY"):
        decode_binary16_exact(bytes.fromhex("007e"))


def test_q4_0_nibble_mapping_is_low_half_then_high_half() -> None:
    raw = bytes(range(16))
    decoded = decode_q4_0_codes(raw)
    assert decoded[:16] == tuple((value & 0x0F) - 8 for value in raw)
    assert decoded[16:] == tuple(((value >> 4) & 0x0F) - 8 for value in raw)
    assert len(decoded) == 32


def test_dense_and_factored_exact_execution_match_with_32x_scale_factor_reduction() -> None:
    payload = _q4_block(1) + _q4_block(2)
    tensor = _tensor("fixture.weight", 32, 2, payload)
    compiled, build = compile_q4_tensor(tensor, payload, (32, 2))
    vector = deterministic_vector(32)
    dense, dense_work = execute_dense_reference(compiled, vector)
    factored, factored_work = execute_factored(compiled, vector, descriptors_are_reused=False)
    assert dense == factored
    assert build["work"]["compiled_descriptor_builds"] == 2
    assert dense_work["exact_rational_scale_multiplications"] == 64
    assert factored_work["exact_rational_scale_multiplications"] == 2
    assert dense_work["exact_rational_scale_multiplications"] // factored_work["exact_rational_scale_multiplications"] == 32


def test_single_and_multi_coordinate_continuation_match_full_recomputation() -> None:
    payload = b"".join(_q4_block(index) for index in range(8))
    tensor = _tensor("fixture.weight", 128, 2, payload)
    compiled, _ = compile_q4_tensor(tensor, payload, (128, 2))
    baseline = deterministic_vector(128)
    parent_output, _ = execute_factored(compiled, baseline, descriptors_are_reused=True)
    for variant, expected_changed in (("single_region_mutation", 1), ("multi_region_mutation", 4)):
        child = mutated_vector(baseline, variant)
        delta_output, delta_work = execute_continuation_delta(compiled, baseline, parent_output, child)
        full_output, full_work = execute_factored(compiled, child, descriptors_are_reused=True)
        assert delta_output == full_output
        assert delta_work["changed_input_coordinates"] == expected_changed
        assert delta_work["quant_integer_products"] < full_work["quant_integer_products"]
        assert delta_work["full_output_rows_recomputed"] == 0
        assert delta_work["continuation_output_rows_updated"] == 2


def test_deterministic_vector_and_mutations_have_contract_width_and_counts() -> None:
    baseline = deterministic_vector(288, "baseline")
    assert baseline == deterministic_vector(288, "baseline")
    assert baseline != deterministic_vector(288, "novel_content")
    assert baseline != deterministic_vector(288, "contradictory_content")
    single = mutated_vector(baseline, "single_region_mutation")
    multi = mutated_vector(baseline, "multi_region_mutation")
    assert sum(1 for left, right in zip(baseline, single) if left != right) == 1
    assert sum(1 for left, right in zip(baseline, multi) if left != right) == 4


@pytest.fixture(scope="module")
def full_evidence():
    return build_execution_evidence(
        _build_full_target_fixture(),
        filename="pass215-i4-fixture.gguf",
        source={"kind": "repository_generated_fixture", "repo_id": None, "revision": None},
    )


def test_full_fixture_exercises_all_contract_modes_and_validates_sorted_json(full_evidence) -> None:
    validate_execution_evidence(full_evidence)
    serialized = json.dumps(full_evidence, sort_keys=True, separators=(",", ":"), allow_nan=False)
    reloaded = json.loads(serialized)
    validate_execution_evidence(reloaded)
    assert set(full_evidence["frozen_workload_modes"]) == set(FROZEN_MODES)
    assert set(full_evidence["frozen_profile_comparisons"]) == set(FROZEN_COMPARISONS)
    assert set(full_evidence["optimization_class_dispositions"]) == set(FROZEN_OPTIMIZATION_CLASSES)
    assert set(full_evidence["pass214_stage_dispositions"]) == set(PASS214_STAGES)
    assert len(full_evidence["operator_suite"]) == 7
    assert full_evidence["aggregate_execution"]["semantic_exactness"] is True
    assert full_evidence["claims"]["full_transformer_layer_forward_executed"] is False
    assert full_evidence["claims"]["canonical_float_interpretation_performed"] is False
    assert full_evidence["claims"]["embedding_output_dictionary_gain_counted_as_execution_gain"] is False


def test_evidence_fails_closed_on_control_and_authority_tampering(full_evidence) -> None:
    changed = deepcopy(full_evidence)
    changed["controls"]["iteration3"]["transformer_layer_dictionary_gain_bytes"] = 1
    with pytest.raises(Pass215Iteration4ValidationError, match="ITERATION3_EXECUTION_CONTROL"):
        validate_execution_evidence(changed)
    changed = deepcopy(full_evidence)
    changed["authority"]["canonical_mutation_authorized"] = True
    with pytest.raises(Pass215Iteration4ValidationError, match="FORBIDDEN_AUTHORITY"):
        validate_execution_evidence(changed)


def test_evidence_contains_no_json_float_numbers(full_evidence) -> None:
    def walk(value):
        assert not isinstance(value, float)
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(full_evidence)
