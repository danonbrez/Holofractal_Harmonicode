"""Pass 215 Iteration 4: exact Q4_0 linear-operator execution benchmark.

This benchmark executes the seven quantized linear weight tensors of one real
transformer block.  It deliberately stops before RMSNorm, attention softmax,
SiLU, residual composition, or any claim of a complete transformer forward.
Binary16 scale storage is decoded with integer bit operations into exact
rationals; Python float values are forbidden from canonical evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_backend.runtime.hhs_pass215_iteration1_transformer_ingestion_v1 import (
    FROZEN_PROFILE_GIT_BLOB_SHA1,
    PASS213_GATE_PRESERVATION_ROOT_HASH216,
    PASS214_AUTHORITY_ROOT_HASH216,
    PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    _exact_fraction,
)
from hhs_backend.runtime.hhs_pass215_iteration2_open_transformer_container_v1 import (
    ContainerTensor,
    ParsedContainer,
    parse_gguf,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest

CONTRACT = "HHS-P215-I4-EXACT-Q4-0-LINEAR-OPERATOR-EXECUTION-TRANSITION-COMPLEXITY"
PASS_NUMBER = 215
ITERATION = 4
CONTRACT_VERSION = "1.0.0-iteration4"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_4_EXACT_LINEAR_OPERATOR_EXECUTION"
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_4_LINEAR_EXECUTION_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_4_LINEAR_EXECUTION_VALIDATION_V1"

ITERATION2_EVIDENCE_ROOT_HASH216 = "0c18a5055b01bee0401d9ad0b3caba9c5d214d80a6dd809b190e106681b22e70"
ITERATION2_CANONICAL_BYTES = 18_335_232
ITERATION3_EVIDENCE_ROOT_HASH216 = "61e301f728e426b46dbdd7c435c06b7c7f0065b177d62313152494467ed7d021"
ITERATION3_RECEIPT_HASH72 = "+XV/)UKf1oM2)Y>uURQQ?KG(KURR<*5vl2zFqc6Gj6)xNFx/yzsyd!R!HIBJ4dVkCMEAYui)"
ITERATION3_SELECTED_GAIN_BYTES = 6_648_948
ITERATION3_TRANSFORMER_LAYER_GAIN_BYTES = 0
REAL_MODEL_SHA256 = "6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04"

Q4_0_BLOCK_ELEMENTS = 32
Q4_0_BLOCK_BYTES = 18

TARGET_OPERATORS: Mapping[str, tuple[int, int]] = {
    "blk.0.attn_q.weight": (288, 288),
    "blk.0.attn_k.weight": (288, 288),
    "blk.0.attn_v.weight": (288, 288),
    "blk.0.attn_output.weight": (288, 288),
    "blk.0.ffn_gate.weight": (288, 768),
    "blk.0.ffn_up.weight": (288, 768),
    "blk.0.ffn_down.weight": (768, 288),
}

FROZEN_COMPARISONS = (
    "dense_reference",
    "exact_integer_reference",
    "pass213_compiled_rom_only",
    "compiled_rom_plus_cache_layers",
    "compiled_rom_plus_continuation_delta",
    "compiled_rom_plus_multimodal_ml",
    "complete_inherited_hhs_stack",
    "complete_stack_with_ablations",
)
FROZEN_MODES = (
    "cold",
    "warm",
    "exact_repetition",
    "shared_structure",
    "single_region_mutation",
    "multi_region_mutation",
    "novel_content",
    "contradictory_content",
    "no_reuse_control",
    "interruption_recovery",
    "cross_process_replay",
)
PASS214_STAGES = tuple(f"A{index}" for index in range(10))
FROZEN_OPTIMIZATION_CLASSES = (
    "dense_reference",
    "exact_integer_reference",
    "semantic_composition_cache",
    "conformance_decision_cache",
    "predictive_continuation_cache",
    "reusable_pattern_cache",
    "vector_shortlist",
    "exact_compatibility_filtering",
    "exact_delta_cost_reranking",
    "content_addressed_source_reuse",
    "incremental_tokenization",
    "sparse_5184_projection",
    "dependency_complete_frontier",
    "residual_only_processing",
    "parametric_admission",
    "compiled_rom_reuse",
    "generator_exception_compression",
    "physical_recovery",
    "receipt_vector_indexing",
    "sql_context_graph",
    "encrypted_vector_store",
    "snapshot_reuse",
    "multimodal_cross_alignment",
    "bounded_learning_replay",
    "moving_tensor_routing",
    "native_dispatch",
    "accelerator_batching",
    "interruption_recovery",
    "gpu_execution",
)

WORK_COUNTER_KEYS = (
    "source_tensor_bytes",
    "source_quantization_blocks",
    "logical_weights",
    "block_decodes",
    "quant_integer_products",
    "quant_integer_additions",
    "exact_rational_scale_multiplications",
    "exact_rational_accumulation_additions",
    "compiled_descriptor_builds",
    "compiled_descriptor_hits",
    "exact_output_cache_hits",
    "exact_output_cache_misses",
    "changed_input_coordinates",
    "delta_weight_products",
    "delta_output_accumulations",
    "full_output_rows_recomputed",
    "continuation_output_rows_updated",
    "semantic_compare_count",
    "checkpoint_bytes",
    "recovery_work_units",
)


class Pass215Iteration4Error(RuntimeError):
    pass


class Pass215Iteration4ValidationError(Pass215Iteration4Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration4ValidationError(f"PASS215_I4_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _sha256(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _normal_rational(numerator: int, denominator: int) -> tuple[int, int]:
    numerator = int(numerator)
    denominator = int(denominator)
    if denominator <= 0:
        raise Pass215Iteration4ValidationError("PASS215_I4_RATIONAL_DENOMINATOR_INVALID")
    if numerator == 0:
        return (0, 1)
    divisor = gcd(abs(numerator), denominator)
    return (numerator // divisor, denominator // divisor)


def _rat_add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    ln, ld = left
    rn, rd = right
    common = gcd(ld, rd)
    return _normal_rational(ln * (rd // common) + rn * (ld // common), ld * (rd // common))


def _rat_to_dict(value: tuple[int, int]) -> Mapping[str, int]:
    return {"numerator": int(value[0]), "denominator": int(value[1])}


def decode_binary16_exact(raw: bytes) -> tuple[int, int]:
    """Decode IEEE binary16 bytes to an exact rational using integer bits only."""
    if len(raw) != 2:
        raise Pass215Iteration4ValidationError("PASS215_I4_BINARY16_LENGTH_INVALID")
    bits = int.from_bytes(raw, "little")
    sign = -1 if (bits >> 15) & 1 else 1
    exponent_field = (bits >> 10) & 0x1F
    fraction = bits & 0x03FF
    if exponent_field == 0x1F:
        raise Pass215Iteration4ValidationError("PASS215_I4_BINARY16_NAN_OR_INFINITY_SCALE")
    if exponent_field == 0:
        if fraction == 0:
            return (0, 1)
        significand = fraction
        binary_exponent = -24
    else:
        significand = 1024 + fraction
        binary_exponent = exponent_field - 25
    numerator = sign * significand
    denominator = 1
    if binary_exponent >= 0:
        numerator <<= binary_exponent
    else:
        denominator <<= -binary_exponent
    return _normal_rational(numerator, denominator)


def decode_q4_0_codes(raw: bytes) -> tuple[int, ...]:
    if len(raw) != 16:
        raise Pass215Iteration4ValidationError("PASS215_I4_Q4_0_CODE_LENGTH_INVALID")
    low = tuple((byte & 0x0F) - 8 for byte in raw)
    high = tuple(((byte >> 4) & 0x0F) - 8 for byte in raw)
    return low + high


def deterministic_vector(width: int, variant: str = "baseline") -> tuple[int, ...]:
    if width <= 0:
        raise Pass215Iteration4ValidationError("PASS215_I4_VECTOR_WIDTH_INVALID")
    if variant == "baseline":
        return tuple(((17 * index + 23) % 37) - 18 for index in range(width))
    if variant == "novel_content":
        return tuple(((29 * index + 11) % 53) - 26 for index in range(width))
    if variant == "contradictory_content":
        return tuple((1 + index % 13) if index % 2 == 0 else -(1 + index % 13) for index in range(width))
    raise Pass215Iteration4ValidationError(f"PASS215_I4_VECTOR_VARIANT_INVALID:{variant}")


def mutated_vector(parent: Sequence[int], variant: str) -> tuple[int, ...]:
    output = list(int(value) for value in parent)
    width = len(output)
    if variant == "single_region_mutation":
        output[width // 3] += 7
    elif variant == "multi_region_mutation":
        indexes = (0, width // 4, width // 2, width - 1)
        deltas = (3, -5, 7, -11)
        for index, delta in zip(indexes, deltas):
            output[index] += delta
    else:
        raise Pass215Iteration4ValidationError(f"PASS215_I4_MUTATION_VARIANT_INVALID:{variant}")
    return tuple(output)


def _new_work() -> dict[str, int]:
    return {key: 0 for key in WORK_COUNTER_KEYS}


def _add_work(*records: Mapping[str, int]) -> dict[str, int]:
    result = _new_work()
    for record in records:
        for key in WORK_COUNTER_KEYS:
            result[key] += int(record.get(key, 0))
    return result


def _executed_work_units(record: Mapping[str, int]) -> int:
    excluded = {"source_tensor_bytes", "checkpoint_bytes"}
    return sum(int(value) for key, value in record.items() if key not in excluded)


def _work_record(record: Mapping[str, int]) -> Mapping[str, Any]:
    normalized = {key: int(record.get(key, 0)) for key in WORK_COUNTER_KEYS}
    normalized["executed_work_units_total"] = _executed_work_units(normalized)
    return normalized


@dataclass(frozen=True)
class CompiledBlock:
    scale_numerator: int
    scale_denominator: int
    quant_integers: tuple[int, ...]


@dataclass(frozen=True)
class CompiledTensor:
    name: str
    ne0: int
    ne1: int
    source_sha256: str
    source_bytes: int
    blocks_per_row: int
    rows: tuple[tuple[CompiledBlock, ...], ...]
    descriptor_root_hash216: str

    @property
    def block_count(self) -> int:
        return self.ne1 * self.blocks_per_row


def _validate_q4_tensor_binding(tensor: ContainerTensor, payload: bytes, expected_shape: tuple[int, int]) -> None:
    if tensor.storage_type != "Q4_0" or tensor.block_elements != Q4_0_BLOCK_ELEMENTS or tensor.block_bytes != Q4_0_BLOCK_BYTES:
        raise Pass215Iteration4ValidationError(f"PASS215_I4_TARGET_TENSOR_TYPE_INVALID:{tensor.name}")
    if tuple(tensor.shape) != tuple(expected_shape):
        raise Pass215Iteration4ValidationError(f"PASS215_I4_TARGET_TENSOR_GEOMETRY_MISMATCH:{tensor.name}")
    ne0, ne1 = expected_shape
    expected_bytes = (ne0 // Q4_0_BLOCK_ELEMENTS) * ne1 * Q4_0_BLOCK_BYTES
    if ne0 % Q4_0_BLOCK_ELEMENTS or len(payload) != expected_bytes or tensor.data_size != expected_bytes:
        raise Pass215Iteration4ValidationError(f"PASS215_I4_TARGET_TENSOR_BYTE_GEOMETRY_INVALID:{tensor.name}")
    if _sha256(payload) != tensor.source_sha256:
        raise Pass215Iteration4ValidationError(f"PASS215_I4_TARGET_TENSOR_SOURCE_SHA_MISMATCH:{tensor.name}")


def compile_q4_tensor(tensor: ContainerTensor, payload: bytes, expected_shape: tuple[int, int]) -> tuple[CompiledTensor, Mapping[str, Any]]:
    _validate_q4_tensor_binding(tensor, payload, expected_shape)
    ne0, ne1 = expected_shape
    blocks_per_row = ne0 // Q4_0_BLOCK_ELEMENTS
    rows: list[tuple[CompiledBlock, ...]] = []
    cursor = 0
    for _row_index in range(ne1):
        row: list[CompiledBlock] = []
        for _block_index in range(blocks_per_row):
            block_raw = payload[cursor : cursor + Q4_0_BLOCK_BYTES]
            cursor += Q4_0_BLOCK_BYTES
            if len(block_raw) != Q4_0_BLOCK_BYTES:
                raise Pass215Iteration4ValidationError("PASS215_I4_Q4_0_BLOCK_LENGTH_INVALID")
            scale = decode_binary16_exact(block_raw[:2])
            quants = decode_q4_0_codes(block_raw[2:])
            row.append(CompiledBlock(scale[0], scale[1], quants))
        rows.append(tuple(row))
    if cursor != len(payload):
        raise Pass215Iteration4ValidationError("PASS215_I4_Q4_0_BLOCK_CURSOR_MISMATCH")
    descriptor_payload = {
        "name": tensor.name,
        "shape": [ne0, ne1],
        "storage_type": "Q4_0",
        "source_sha256": tensor.source_sha256,
        "source_bytes": len(payload),
        "block_count": ne1 * blocks_per_row,
        "decoder": "PASS215_I4_Q4_0_EXACT_BINARY16_RATIONAL_V1",
    }
    descriptor_root = hash216("pass215-i4-compiled-block-descriptor", canonical_bytes(descriptor_payload))
    compiled = CompiledTensor(
        name=tensor.name,
        ne0=ne0,
        ne1=ne1,
        source_sha256=tensor.source_sha256,
        source_bytes=len(payload),
        blocks_per_row=blocks_per_row,
        rows=tuple(rows),
        descriptor_root_hash216=descriptor_root,
    )
    work = _new_work()
    work["source_tensor_bytes"] = len(payload)
    work["source_quantization_blocks"] = compiled.block_count
    work["logical_weights"] = ne0 * ne1
    work["block_decodes"] = compiled.block_count
    work["compiled_descriptor_builds"] = compiled.block_count
    return compiled, {
        "descriptor_root_hash216": descriptor_root,
        "source_sha256": tensor.source_sha256,
        "shape": [ne0, ne1],
        "block_count": compiled.block_count,
        "work": _work_record(work),
    }


def _canonical_output(values: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    return tuple(_normal_rational(value[0], value[1]) for value in values)


def output_root(name: str, input_vector: Sequence[int], values: Sequence[tuple[int, int]]) -> str:
    payload = {
        "tensor": name,
        "input": [int(value) for value in input_vector],
        "output": [_rat_to_dict(value) for value in _canonical_output(values)],
    }
    return hash216("pass215-i4-exact-linear-output", canonical_bytes(payload))


def _row_scale_denominator(blocks: Sequence[CompiledBlock]) -> int:
    maximum = max(block.scale_denominator for block in blocks)
    for block in blocks:
        if maximum % block.scale_denominator:
            raise Pass215Iteration4ValidationError("PASS215_I4_SCALE_DENOMINATOR_NOT_POWER_COMPATIBLE")
    return maximum


def execute_dense_reference(compiled: CompiledTensor, input_vector: Sequence[int]) -> tuple[tuple[tuple[int, int], ...], Mapping[str, Any]]:
    if len(input_vector) != compiled.ne0:
        raise Pass215Iteration4ValidationError(f"PASS215_I4_INPUT_WIDTH_MISMATCH:{compiled.name}")
    outputs: list[tuple[int, int]] = []
    work = _new_work()
    work["source_tensor_bytes"] = compiled.source_bytes
    work["source_quantization_blocks"] = compiled.block_count
    work["logical_weights"] = compiled.ne0 * compiled.ne1
    work["block_decodes"] = compiled.block_count
    work["quant_integer_products"] = compiled.ne0 * compiled.ne1
    work["exact_rational_scale_multiplications"] = compiled.ne0 * compiled.ne1
    work["exact_rational_accumulation_additions"] = compiled.ne1 * (compiled.ne0 - 1)
    work["full_output_rows_recomputed"] = compiled.ne1
    for row in compiled.rows:
        common_denominator = _row_scale_denominator(row)
        numerator = 0
        for block_index, block in enumerate(row):
            base = block_index * Q4_0_BLOCK_ELEMENTS
            scale_factor = common_denominator // block.scale_denominator
            for local_index, quant in enumerate(block.quant_integers):
                numerator += (
                    int(quant)
                    * int(input_vector[base + local_index])
                    * block.scale_numerator
                    * scale_factor
                )
        outputs.append(_normal_rational(numerator, common_denominator))
    return _canonical_output(outputs), _work_record(work)


def execute_factored(compiled: CompiledTensor, input_vector: Sequence[int], *, descriptors_are_reused: bool) -> tuple[tuple[tuple[int, int], ...], Mapping[str, Any]]:
    if len(input_vector) != compiled.ne0:
        raise Pass215Iteration4ValidationError(f"PASS215_I4_INPUT_WIDTH_MISMATCH:{compiled.name}")
    outputs: list[tuple[int, int]] = []
    work = _new_work()
    work["source_tensor_bytes"] = compiled.source_bytes
    work["source_quantization_blocks"] = compiled.block_count
    work["logical_weights"] = compiled.ne0 * compiled.ne1
    work["quant_integer_products"] = compiled.ne0 * compiled.ne1
    work["quant_integer_additions"] = compiled.block_count * (Q4_0_BLOCK_ELEMENTS - 1)
    work["exact_rational_scale_multiplications"] = compiled.block_count
    work["exact_rational_accumulation_additions"] = compiled.ne1 * (compiled.blocks_per_row - 1)
    work["full_output_rows_recomputed"] = compiled.ne1
    if descriptors_are_reused:
        work["compiled_descriptor_hits"] = compiled.block_count
    else:
        work["block_decodes"] = compiled.block_count
    for row in compiled.rows:
        common_denominator = _row_scale_denominator(row)
        numerator = 0
        for block_index, block in enumerate(row):
            base = block_index * Q4_0_BLOCK_ELEMENTS
            integer_dot = 0
            for local_index, quant in enumerate(block.quant_integers):
                integer_dot += int(quant) * int(input_vector[base + local_index])
            numerator += integer_dot * block.scale_numerator * (common_denominator // block.scale_denominator)
        outputs.append(_normal_rational(numerator, common_denominator))
    return _canonical_output(outputs), _work_record(work)


def execute_continuation_delta(
    compiled: CompiledTensor,
    parent_input: Sequence[int],
    parent_output: Sequence[tuple[int, int]],
    child_input: Sequence[int],
) -> tuple[tuple[tuple[int, int], ...], Mapping[str, Any]]:
    if len(parent_input) != compiled.ne0 or len(child_input) != compiled.ne0 or len(parent_output) != compiled.ne1:
        raise Pass215Iteration4ValidationError("PASS215_I4_CONTINUATION_GEOMETRY_INVALID")
    changed = [index for index, (left, right) in enumerate(zip(parent_input, child_input)) if int(left) != int(right)]
    if not changed:
        raise Pass215Iteration4ValidationError("PASS215_I4_CONTINUATION_DELTA_EMPTY")
    changed_by_block: dict[int, list[int]] = {}
    for index in changed:
        changed_by_block.setdefault(index // Q4_0_BLOCK_ELEMENTS, []).append(index)
    outputs: list[tuple[int, int]] = []
    work = _new_work()
    work["source_tensor_bytes"] = compiled.source_bytes
    work["source_quantization_blocks"] = compiled.block_count
    work["logical_weights"] = compiled.ne0 * compiled.ne1
    work["compiled_descriptor_hits"] = compiled.ne1 * len(changed_by_block)
    work["changed_input_coordinates"] = len(changed)
    work["delta_weight_products"] = compiled.ne1 * len(changed)
    work["quant_integer_products"] = compiled.ne1 * len(changed)
    work["quant_integer_additions"] = compiled.ne1 * sum(max(0, len(values) - 1) for values in changed_by_block.values())
    work["exact_rational_scale_multiplications"] = compiled.ne1 * len(changed_by_block)
    work["exact_rational_accumulation_additions"] = compiled.ne1 * max(0, len(changed_by_block) - 1)
    work["delta_output_accumulations"] = compiled.ne1
    work["continuation_output_rows_updated"] = compiled.ne1
    for row_index, row in enumerate(compiled.rows):
        delta_value = (0, 1)
        for block_index in sorted(changed_by_block):
            block = row[block_index]
            integer_dot = 0
            for coordinate in changed_by_block[block_index]:
                local_index = coordinate % Q4_0_BLOCK_ELEMENTS
                delta = int(child_input[coordinate]) - int(parent_input[coordinate])
                integer_dot += int(block.quant_integers[local_index]) * delta
            contribution = _normal_rational(integer_dot * block.scale_numerator, block.scale_denominator)
            delta_value = _rat_add(delta_value, contribution)
        outputs.append(_rat_add(parent_output[row_index], delta_value))
    return _canonical_output(outputs), _work_record(work)


def _compare_outputs(left: Sequence[tuple[int, int]], right: Sequence[tuple[int, int]], context: str) -> None:
    if _canonical_output(left) != _canonical_output(right):
        raise Pass215Iteration4ValidationError(f"PASS215_I4_EXACT_OUTPUT_MISMATCH:{context}")


def _cache_key(compiled: CompiledTensor, input_vector: Sequence[int]) -> str:
    return hash216(
        "pass215-i4-exact-output-cache-key",
        canonical_bytes({
            "descriptor_root_hash216": compiled.descriptor_root_hash216,
            "source_sha256": compiled.source_sha256,
            "input": [int(value) for value in input_vector],
        }),
    )


def _aggregate_work(records: Iterable[Mapping[str, int]]) -> Mapping[str, Any]:
    return _work_record(_add_work(*list(records)))


def _optimization_dispositions() -> Mapping[str, str]:
    dispositions = {
        "dense_reference": "EXECUTED",
        "exact_integer_reference": "EXECUTED_AS_Q4_0_INTEGER_INNER_DOT_WITH_EXACT_RATIONAL_SCALE",
        "semantic_composition_cache": "EXECUTED_AS_EXACT_INPUT_OUTPUT_CACHE_FOR_FIXED_LINEAR_OPERATOR",
        "conformance_decision_cache": "DEFERRED_TO_LATER_PASS215_GOVERNANCE_ITERATION",
        "predictive_continuation_cache": "EXECUTED_AS_EXACT_SPARSE_LINEAR_CONTINUATION_DELTA",
        "reusable_pattern_cache": "EXECUTED_AS_IMMUTABLE_COMPILED_BLOCK_DESCRIPTOR_REUSE",
        "vector_shortlist": "NOT_APPLICABLE_TO_FIXED_SINGLE_OPERATOR_INPUT_WITH_NO_RETRIEVAL_SEARCH",
        "exact_compatibility_filtering": "EXECUTED_AS_CONTRACTED_TENSOR_NAME_TYPE_SHAPE_AND_SOURCE_BINDING",
        "exact_delta_cost_reranking": "NOT_APPLICABLE_WITH_SINGLE_PREDECLARED_DELTA_PATH_NO_CANDIDATE_RANKING",
        "content_addressed_source_reuse": "EXECUTED_WITH_SOURCE_SHA256_DESCRIPTOR_ROOT_AND_INPUT_CACHE_KEY",
        "incremental_tokenization": "NOT_APPLICABLE_TO_PRETOKENIZED_NUMERIC_LINEAR_OPERATOR_VECTOR",
        "sparse_5184_projection": "DEFERRED_TO_LATER_PASS215_NATIVE_LATTICE_PROJECTION_ITERATION",
        "dependency_complete_frontier": "EXECUTED_AS_CHANGED_COORDINATE_TO_AFFECTED_Q4_BLOCK_FRONTIER",
        "residual_only_processing": "EXECUTED_AS_SPARSE_W_TIMES_INPUT_DELTA",
        "parametric_admission": "DEFERRED_RUNTIME_MUTATION_AUTHORITY_REMAINS_FALSE",
        "compiled_rom_reuse": "EXECUTED_AS_BENCHMARK_ONLY_IMMUTABLE_DESCRIPTOR_ANALOG_NOT_PASS213_RUNTIME_MUTATION",
        "generator_exception_compression": "CONTROL_ONLY_ITERATION2_AND_DECOMPOSED_ITERATION3_PASS212_ADMISSION_REMAINS_ZERO",
        "physical_recovery": "EXECUTED_AS_SERIALIZED_SOURCE_BOUND_CHECKPOINT_VALIDATION_AND_REPLAY",
        "receipt_vector_indexing": "DEFERRED_EVIDENCE_RECEIPT_IS_MINTED_BUT_NOT_MUTATED_INTO_RUNTIME_INDEX",
        "sql_context_graph": "NOT_APPLICABLE_TO_STATELESS_SINGLE_LAYER_NUMERIC_OPERATOR_BENCHMARK",
        "encrypted_vector_store": "NOT_APPLICABLE_TO_EPHEMERAL_BENCHMARK_CACHE_NO_PERSISTENT_SECRET_DATA",
        "snapshot_reuse": "EXECUTED_AS_EXACT_PARENT_OUTPUT_CACHE_AND_RECOVERY_CHECKPOINT",
        "multimodal_cross_alignment": "NOT_APPLICABLE_TO_SINGLE_TEXT_TRANSFORMER_LINEAR_OPERATOR_SLICE",
        "bounded_learning_replay": "NOT_APPLICABLE_NO_LEARNING_OR_PARAMETER_UPDATE_OCCURS",
        "moving_tensor_routing": "DEFERRED_PASS213_OPERATIONAL_RUNTIME_AUTHORITY_NOT_PROMOTED",
        "native_dispatch": "DEFERRED_PASS213_OPERATIONAL_RUNTIME_AUTHORITY_NOT_PROMOTED",
        "accelerator_batching": "OPTIONAL_NOT_EXERCISED_CPU_REFERENCE_SCOPE",
        "interruption_recovery": "EXECUTED",
        "gpu_execution": "EXPERIMENTAL_NOT_EXERCISED_CPU_REFERENCE_SCOPE",
    }
    if set(dispositions) != set(FROZEN_OPTIMIZATION_CLASSES):
        raise Pass215Iteration4ValidationError("PASS215_I4_OPTIMIZATION_DISPOSITION_SET_INVALID")
    return dispositions


def _stage_dispositions() -> Mapping[str, str]:
    result = {
        "A0": "EXECUTED_DENSE_EXACT_RATIONAL_REFERENCE",
        "A1": "EXECUTED_ISOLATED_Q4_0_FACTORED_KERNEL",
        "A2": "EXECUTED_FACTORED_PLUS_IMMUTABLE_DESCRIPTOR_AND_EXACT_OUTPUT_CACHE",
        "A3": "EXECUTED_SINGLE_AND_MULTI_COORDINATE_CONTINUATION_DELTA",
        "A4": "PARTIAL_ITERATION4_EXECUTION_SUBSET_REMAINING_FROZEN_CLASSES_EXPLICITLY_DEFERRED_OR_NOT_APPLICABLE",
        "A5": "EXECUTED_ABLATIONS_NO_REUSE_DESCRIPTOR_REUSE_OUTPUT_CACHE_AND_CONTINUATION",
        "A6": "EXECUTED_NO_REUSE_AND_ALTERNATING_SIGN_ADVERSE_CONTROL",
        "A7": "EXECUTED_SERIALIZED_CHECKPOINT_VALIDATE_RESTORE_REPLAY",
        "A8": "READY_FOR_REQUIRED_EXTERNAL_CROSS_PROCESS_CI_REPLAY",
        "A9": "NOT_APPLICABLE_OPTIONAL_ACCELERATOR_NOT_USED_IN_ITERATION4_CPU_REFERENCE_SCOPE",
    }
    if tuple(result) != PASS214_STAGES:
        raise Pass215Iteration4ValidationError("PASS215_I4_STAGE_DISPOSITION_SET_INVALID")
    return result


def _comparison_dispositions(mode_aggregate: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any]:
    result: dict[str, Any] = {
        "dense_reference": {"status": "EXECUTED", "mode": "cold", "semantic_exactness": True},
        "exact_integer_reference": {"status": "EXECUTED", "mode": "no_reuse_control", "semantic_exactness": True},
        "pass213_compiled_rom_only": {"status": "EXECUTED_BENCHMARK_ANALOG_ONLY", "mode": "warm", "runtime_authority": False, "semantic_exactness": True},
        "compiled_rom_plus_cache_layers": {"status": "EXECUTED_BENCHMARK_ANALOG_ONLY", "mode": "exact_repetition", "runtime_authority": False, "semantic_exactness": True},
        "compiled_rom_plus_continuation_delta": {"status": "EXECUTED_BENCHMARK_ANALOG_ONLY", "mode": "single_region_mutation", "runtime_authority": False, "semantic_exactness": True},
        "compiled_rom_plus_multimodal_ml": {"status": "NOT_APPLICABLE", "reason": "SINGLE_TEXT_TRANSFORMER_LINEAR_OPERATOR_SLICE_NO_MULTIMODAL_INPUT_OR_LEARNING"},
        "complete_inherited_hhs_stack": {"status": "PARTIAL_ITERATION4_SUBSET_ONLY", "reason": "PASS215_TERMINAL_COMPLETE_STACK_NOT_YET_CLAIMED"},
        "complete_stack_with_ablations": {"status": "EXECUTED_ITERATION4_SUBSET_ABLATIONS", "modes": ["no_reuse_control", "warm", "exact_repetition", "single_region_mutation", "multi_region_mutation"]},
    }
    if tuple(result) != FROZEN_COMPARISONS:
        raise Pass215Iteration4ValidationError("PASS215_I4_COMPARISON_DISPOSITION_SET_INVALID")
    for name in ("dense_reference", "exact_integer_reference", "pass213_compiled_rom_only", "compiled_rom_plus_cache_layers", "compiled_rom_plus_continuation_delta"):
        mode = str(result[name]["mode"])
        result[name]["executed_work_units_total"] = int(mode_aggregate[mode]["work"]["executed_work_units_total"])
    return result


def _operator_record(tensor: ContainerTensor, payload: bytes, expected_shape: tuple[int, int]) -> tuple[Mapping[str, Any], CompiledTensor, tuple[tuple[int, int], ...], tuple[int, ...]]:
    compiled, build_record = compile_q4_tensor(tensor, payload, expected_shape)
    baseline = deterministic_vector(compiled.ne0, "baseline")
    dense_output, dense_work = execute_dense_reference(compiled, baseline)
    factored_output, factored_work = execute_factored(compiled, baseline, descriptors_are_reused=False)
    _compare_outputs(dense_output, factored_output, f"{tensor.name}:dense-vs-factored")
    warm_output, warm_work = execute_factored(compiled, baseline, descriptors_are_reused=True)
    _compare_outputs(dense_output, warm_output, f"{tensor.name}:dense-vs-warm")

    baseline_key = _cache_key(compiled, baseline)
    baseline_root = output_root(compiled.name, baseline, dense_output)
    cache = {baseline_key: (dense_output, baseline_root)}
    cache_miss_work = _new_work()
    cache_miss_work["exact_output_cache_misses"] = 1
    cache_hit_work = _new_work()
    cache_hit_work["exact_output_cache_hits"] = 1
    cached_output, cached_root = cache[baseline_key]
    if cached_root != baseline_root:
        raise Pass215Iteration4ValidationError("PASS215_I4_OUTPUT_CACHE_ROOT_TAMPERING")
    _compare_outputs(dense_output, cached_output, f"{tensor.name}:cache-replay")

    novel = deterministic_vector(compiled.ne0, "novel_content")
    novel_output, novel_work = execute_factored(compiled, novel, descriptors_are_reused=True)
    adverse = deterministic_vector(compiled.ne0, "contradictory_content")
    adverse_output, adverse_work = execute_factored(compiled, adverse, descriptors_are_reused=False)

    single = mutated_vector(baseline, "single_region_mutation")
    single_delta_output, single_delta_work = execute_continuation_delta(compiled, baseline, dense_output, single)
    single_full_output, single_full_work = execute_factored(compiled, single, descriptors_are_reused=True)
    _compare_outputs(single_delta_output, single_full_output, f"{tensor.name}:single-delta")

    multi = mutated_vector(baseline, "multi_region_mutation")
    multi_delta_output, multi_delta_work = execute_continuation_delta(compiled, baseline, dense_output, multi)
    multi_full_output, multi_full_work = execute_factored(compiled, multi, descriptors_are_reused=True)
    _compare_outputs(multi_delta_output, multi_full_output, f"{tensor.name}:multi-delta")

    factored_rational_mults = int(factored_work["exact_rational_scale_multiplications"])
    dense_rational_mults = int(dense_work["exact_rational_scale_multiplications"])
    record = {
        "name": compiled.name,
        "shape": [compiled.ne0, compiled.ne1],
        "source_bytes": compiled.source_bytes,
        "source_sha256": compiled.source_sha256,
        "block_count": compiled.block_count,
        "logical_weights": compiled.ne0 * compiled.ne1,
        "input_roots_hash216": {
            "baseline": hash216("pass215-i4-input", canonical_bytes(list(baseline))),
            "novel_content": hash216("pass215-i4-input", canonical_bytes(list(novel))),
            "contradictory_content": hash216("pass215-i4-input", canonical_bytes(list(adverse))),
            "single_region_mutation": hash216("pass215-i4-input", canonical_bytes(list(single))),
            "multi_region_mutation": hash216("pass215-i4-input", canonical_bytes(list(multi))),
        },
        "descriptor": build_record,
        "dense_reference": {
            "output_root_hash216": baseline_root,
            "work": dense_work,
        },
        "factored_reference": {
            "output_root_hash216": output_root(compiled.name, baseline, factored_output),
            "work": factored_work,
            "exact_rational_scale_multiplication_reduction": dense_rational_mults - factored_rational_mults,
            "dense_to_factored_rational_scale_multiplication_ratio_exact": _exact_fraction(dense_rational_mults, factored_rational_mults),
        },
        "warm_descriptor_reuse": {
            "output_root_hash216": output_root(compiled.name, baseline, warm_output),
            "work": warm_work,
        },
        "exact_repetition_cache": {
            "cache_key_hash216": baseline_key,
            "output_root_hash216": cached_root,
            "work": _work_record(cache_hit_work),
        },
        "novel_content": {
            "output_root_hash216": output_root(compiled.name, novel, novel_output),
            "work": novel_work,
        },
        "contradictory_content": {
            "output_root_hash216": output_root(compiled.name, adverse, adverse_output),
            "work": adverse_work,
        },
        "single_region_mutation": {
            "changed_coordinates": sum(1 for left, right in zip(baseline, single) if left != right),
            "continuation_output_root_hash216": output_root(compiled.name, single, single_delta_output),
            "full_recompute_output_root_hash216": output_root(compiled.name, single, single_full_output),
            "continuation_work": single_delta_work,
            "full_recompute_control_work": single_full_work,
            "semantic_exactness": True,
        },
        "multi_region_mutation": {
            "changed_coordinates": sum(1 for left, right in zip(baseline, multi) if left != right),
            "continuation_output_root_hash216": output_root(compiled.name, multi, multi_delta_output),
            "full_recompute_output_root_hash216": output_root(compiled.name, multi, multi_full_output),
            "continuation_work": multi_delta_work,
            "full_recompute_control_work": multi_full_work,
            "semantic_exactness": True,
        },
        "semantic_exactness": True,
    }
    _reject_floats(record)
    return record, compiled, dense_output, baseline


def _checkpoint_record(
    source_sha256: str,
    operators: Sequence[Mapping[str, Any]],
    compiled_tensors: Sequence[CompiledTensor],
    baseline_outputs: Sequence[Sequence[tuple[int, int]]],
    baseline_inputs: Sequence[Sequence[int]],
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    entries = []
    for operator, compiled, output, input_vector in zip(operators, compiled_tensors, baseline_outputs, baseline_inputs):
        entries.append({
            "name": compiled.name,
            "descriptor_root_hash216": compiled.descriptor_root_hash216,
            "source_sha256": compiled.source_sha256,
            "cache_key_hash216": _cache_key(compiled, input_vector),
            "input": [int(value) for value in input_vector],
            "output": [_rat_to_dict(value) for value in output],
            "output_root_hash216": operator["dense_reference"]["output_root_hash216"],
        })
    payload = {
        "schema": "HHS_PASS_215_ITERATION_4_EXECUTION_CHECKPOINT_V1",
        "source_sha256": source_sha256,
        "iteration3_control_root_hash216": ITERATION3_EVIDENCE_ROOT_HASH216,
        "entries": entries,
    }
    encoded = canonical_bytes(payload)
    checkpoint_sha = _sha256(encoded)
    restored = json.loads(encoded.decode("utf-8"))
    if canonical_bytes(restored) != encoded or _sha256(canonical_bytes(restored)) != checkpoint_sha:
        raise Pass215Iteration4ValidationError("PASS215_I4_CHECKPOINT_TAMPERING")
    work = _new_work()
    work["checkpoint_bytes"] = len(encoded)
    work["recovery_work_units"] = len(entries)
    work["semantic_compare_count"] = len(entries)
    work["exact_output_cache_hits"] = len(entries)
    for entry, compiled in zip(restored["entries"], compiled_tensors):
        if entry["descriptor_root_hash216"] != compiled.descriptor_root_hash216 or entry["source_sha256"] != compiled.source_sha256:
            raise Pass215Iteration4ValidationError("PASS215_I4_CHECKPOINT_DESCRIPTOR_BINDING_MISMATCH")
        input_vector = tuple(int(value) for value in entry["input"])
        output = tuple((int(value["numerator"]), int(value["denominator"])) for value in entry["output"])
        if _cache_key(compiled, input_vector) != entry["cache_key_hash216"]:
            raise Pass215Iteration4ValidationError("PASS215_I4_CHECKPOINT_CACHE_KEY_MISMATCH")
        if output_root(compiled.name, input_vector, output) != entry["output_root_hash216"]:
            raise Pass215Iteration4ValidationError("PASS215_I4_CHECKPOINT_OUTPUT_ROOT_MISMATCH")
    return {
        "checkpoint_sha256": checkpoint_sha,
        "checkpoint_root_hash216": hash216("pass215-i4-checkpoint", encoded),
        "checkpoint_bytes": len(encoded),
        "restored_entry_count": len(entries),
        "semantic_exactness": True,
    }, _work_record(work)


def build_execution_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
    frozen_profile_blob_sha1: str = FROZEN_PROFILE_GIT_BLOB_SHA1,
) -> Mapping[str, Any]:
    if frozen_profile_blob_sha1 != FROZEN_PROFILE_GIT_BLOB_SHA1:
        raise Pass215Iteration4ValidationError("PASS215_I4_FROZEN_PROFILE_BLOB_MISMATCH")
    _reject_floats(source)
    actual_sha = _sha256(raw)
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration4ValidationError("PASS215_I4_SOURCE_SHA256_MISMATCH")
    parsed: ParsedContainer = parse_gguf(raw)
    if parsed.file_sha256 != actual_sha:
        raise Pass215Iteration4ValidationError("PASS215_I4_CONTAINER_SHA256_INTERNAL_MISMATCH")
    real_open = source.get("kind") == "public_open_transformer"
    if real_open and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration4ValidationError("PASS215_I4_AUTHENTICATED_REAL_MODEL_IDENTITY_MISMATCH")

    by_name = {tensor.name: tensor for tensor in parsed.tensors}
    if set(TARGET_OPERATORS) - set(by_name):
        missing = sorted(set(TARGET_OPERATORS) - set(by_name))
        raise Pass215Iteration4ValidationError(f"PASS215_I4_TARGET_TENSOR_MISSING:{','.join(missing)}")

    operator_records: list[Mapping[str, Any]] = []
    compiled_tensors: list[CompiledTensor] = []
    baseline_outputs: list[tuple[tuple[int, int], ...]] = []
    baseline_inputs: list[tuple[int, ...]] = []
    for name, expected_shape in TARGET_OPERATORS.items():
        tensor = by_name[name]
        payload = raw[tensor.data_offset : tensor.data_offset + tensor.data_size]
        record, compiled, baseline_output, baseline_input = _operator_record(tensor, payload, expected_shape)
        operator_records.append(record)
        compiled_tensors.append(compiled)
        baseline_outputs.append(baseline_output)
        baseline_inputs.append(baseline_input)

    checkpoint, checkpoint_work = _checkpoint_record(
        actual_sha,
        operator_records,
        compiled_tensors,
        baseline_outputs,
        baseline_inputs,
    )

    mode_work: dict[str, Mapping[str, Any]] = {}
    mode_work["cold"] = _aggregate_work(
        _add_work(record["descriptor"]["work"], record["warm_descriptor_reuse"]["work"])
        for record in operator_records
    )
    mode_work["warm"] = _aggregate_work(record["warm_descriptor_reuse"]["work"] for record in operator_records)
    mode_work["exact_repetition"] = _aggregate_work(record["exact_repetition_cache"]["work"] for record in operator_records)
    mode_work["shared_structure"] = _aggregate_work(record["novel_content"]["work"] for record in operator_records)
    mode_work["single_region_mutation"] = _aggregate_work(record["single_region_mutation"]["continuation_work"] for record in operator_records)
    mode_work["multi_region_mutation"] = _aggregate_work(record["multi_region_mutation"]["continuation_work"] for record in operator_records)
    mode_work["novel_content"] = _aggregate_work(record["novel_content"]["work"] for record in operator_records)
    mode_work["contradictory_content"] = _aggregate_work(record["contradictory_content"]["work"] for record in operator_records)
    mode_work["no_reuse_control"] = _aggregate_work(record["factored_reference"]["work"] for record in operator_records)
    mode_work["interruption_recovery"] = checkpoint_work
    cross_process_work = _new_work()
    cross_process_work["semantic_compare_count"] = 1
    mode_work["cross_process_replay"] = _work_record(cross_process_work)
    mode_records = {
        mode: {
            "status": "READY_FOR_EXTERNAL_CROSS_PROCESS_REPLAY" if mode == "cross_process_replay" else "EXECUTED",
            "work": mode_work[mode],
            "semantic_exactness": True,
        }
        for mode in FROZEN_MODES
    }

    dense_total = _aggregate_work(record["dense_reference"]["work"] for record in operator_records)
    factored_total = _aggregate_work(record["factored_reference"]["work"] for record in operator_records)
    single_delta_total = _aggregate_work(record["single_region_mutation"]["continuation_work"] for record in operator_records)
    single_full_total = _aggregate_work(record["single_region_mutation"]["full_recompute_control_work"] for record in operator_records)
    multi_delta_total = _aggregate_work(record["multi_region_mutation"]["continuation_work"] for record in operator_records)
    multi_full_total = _aggregate_work(record["multi_region_mutation"]["full_recompute_control_work"] for record in operator_records)

    dense_scale_mults = int(dense_total["exact_rational_scale_multiplications"])
    factored_scale_mults = int(factored_total["exact_rational_scale_multiplications"])
    source_record = dict(source)
    source_record.update({
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or expected_sha256 == actual_sha,
    })

    suite_output_root = hash216(
        "pass215-i4-linear-suite-output",
        canonical_bytes([
            {
                "name": record["name"],
                "baseline_output_root_hash216": record["dense_reference"]["output_root_hash216"],
                "single_delta_output_root_hash216": record["single_region_mutation"]["continuation_output_root_hash216"],
                "multi_delta_output_root_hash216": record["multi_region_mutation"]["continuation_output_root_hash216"],
                "novel_output_root_hash216": record["novel_content"]["output_root_hash216"],
                "adverse_output_root_hash216": record["contradictory_content"]["output_root_hash216"],
            }
            for record in operator_records
        ]),
    )

    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "authority": {
            "pass214_authority_root_hash216": PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
            "pass213_gate_preservation_root_hash216": PASS213_GATE_PRESERVATION_ROOT_HASH216,
            "frozen_profile_git_blob_sha1": FROZEN_PROFILE_GIT_BLOB_SHA1,
            "benchmark_authority_promoted": True,
            "pass215_authorized": True,
            "pass213_gates_preserved": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "source": source_record,
        "controls": {
            "iteration2": {
                "evidence_root_hash216": ITERATION2_EVIDENCE_ROOT_HASH216,
                "canonical_tensor_bytes": ITERATION2_CANONICAL_BYTES,
                "raw_canonical_incidence_fraction_exact": {"numerator": 0, "denominator": 1},
            },
            "iteration3": {
                "evidence_root_hash216": ITERATION3_EVIDENCE_ROOT_HASH216,
                "selected_gain_bytes": ITERATION3_SELECTED_GAIN_BYTES,
                "transformer_layer_dictionary_gain_bytes": ITERATION3_TRANSFORMER_LAYER_GAIN_BYTES,
                "embedding_output_storage_gain_excluded_from_execution_gain": True,
            },
        },
        "container": {
            "format": parsed.format,
            "version": parsed.version,
            "architecture": parsed.architecture,
            "tensor_count": len(parsed.tensors),
        },
        "q4_0_semantics": {
            "block_elements": Q4_0_BLOCK_ELEMENTS,
            "block_bytes": Q4_0_BLOCK_BYTES,
            "binary16_scale_exact_rational_integer_bit_decode": True,
            "low_nibble_elements": [0, 15],
            "high_nibble_elements": [16, 31],
            "quant_integer_offset": -8,
            "canonical_float_interpretation_performed": False,
        },
        "operator_suite": operator_records,
        "suite_output_root_hash216": suite_output_root,
        "aggregate_execution": {
            "operator_count": len(operator_records),
            "source_tensor_bytes": sum(int(record["source_bytes"]) for record in operator_records),
            "quantization_blocks": sum(int(record["block_count"]) for record in operator_records),
            "logical_weights": sum(int(record["logical_weights"]) for record in operator_records),
            "dense_reference_work": dense_total,
            "factored_reference_work": factored_total,
            "dense_to_factored_rational_scale_multiplication_ratio_exact": _exact_fraction(dense_scale_mults, factored_scale_mults),
            "rational_scale_multiplications_avoided_by_factoring": dense_scale_mults - factored_scale_mults,
            "single_region_continuation_work": single_delta_total,
            "single_region_full_recompute_control_work": single_full_total,
            "single_region_executed_work_ratio_exact": _exact_fraction(int(single_full_total["executed_work_units_total"]), int(single_delta_total["executed_work_units_total"])),
            "multi_region_continuation_work": multi_delta_total,
            "multi_region_full_recompute_control_work": multi_full_total,
            "multi_region_executed_work_ratio_exact": _exact_fraction(int(multi_full_total["executed_work_units_total"]), int(multi_delta_total["executed_work_units_total"])),
            "semantic_exactness": True,
        },
        "frozen_workload_modes": mode_records,
        "frozen_profile_comparisons": _comparison_dispositions(mode_records),
        "optimization_class_dispositions": _optimization_dispositions(),
        "pass214_stage_dispositions": _stage_dispositions(),
        "interruption_recovery": {
            **checkpoint,
            "work": checkpoint_work,
        },
        "cross_process_replay": {
            "required": True,
            "local_canonical_suite_root_hash216": suite_output_root,
            "external_validation_status": "READY_FOR_SEPARATE_PROCESS_COMPARISON",
        },
        "claims": {
            "authenticated_real_open_transformer_execution_measured": bool(real_open and actual_sha == REAL_MODEL_SHA256),
            "seven_blk0_linear_operators_executed": True,
            "dense_exact_rational_reference_executed": True,
            "q4_0_factored_exact_kernel_executed": True,
            "dense_factored_semantic_exactness": True,
            "linear_continuation_delta_executed": True,
            "exact_output_cache_replay_executed": True,
            "interruption_recovery_executed": True,
            "embedding_output_dictionary_gain_counted_as_execution_gain": False,
            "full_transformer_layer_forward_executed": False,
            "rmsnorm_execution_claimed": False,
            "attention_softmax_execution_claimed": False,
            "silu_execution_claimed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "exact_nonlinear_transformer_operators_implemented": False,
            "pass213_compiled_rom_runtime_mutation_performed": False,
            "fifty_billion_desktop_feasibility_claimed": False,
            "arbitrary_compression_claimed": False,
        },
    }
    _reject_floats(evidence)
    evidence_root = hash216("pass215-i4-execution-evidence", canonical_bytes(evidence))
    receipt = hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION4_EXACT_LINEAR_EXECUTION"},
        {
            "sequence": 4,
            "parent_hash72": ITERATION3_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_output_root_hash216": suite_output_root,
        },
    )
    return {**evidence, "evidence_root_hash216": evidence_root, "receipt_hash72": receipt}


def validate_execution_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration4ValidationError("PASS215_I4_EVIDENCE_SCHEMA_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping):
        raise Pass215Iteration4ValidationError("PASS215_I4_AUTHORITY_MISSING")
    if authority.get("pass214_authority_root_hash216") != PASS214_AUTHORITY_ROOT_HASH216 or authority.get("pass215_benchmark_profile_root_hash216") != PASS215_BENCHMARK_PROFILE_ROOT_HASH216 or authority.get("pass213_gate_preservation_root_hash216") != PASS213_GATE_PRESERVATION_ROOT_HASH216:
        raise Pass215Iteration4ValidationError("PASS215_I4_AUTHORITY_ROOT_MISMATCH")
    if authority.get("frozen_profile_git_blob_sha1") != FROZEN_PROFILE_GIT_BLOB_SHA1:
        raise Pass215Iteration4ValidationError("PASS215_I4_FROZEN_PROFILE_BINDING_INVALID")
    for forbidden in ("runtime_mutation_authority_promoted", "canonical_mutation_authorized", "migration_active"):
        if authority.get(forbidden) is not False:
            raise Pass215Iteration4ValidationError(f"PASS215_I4_FORBIDDEN_AUTHORITY:{forbidden}")
    controls = evidence.get("controls")
    if not isinstance(controls, Mapping) or controls.get("iteration2", {}).get("evidence_root_hash216") != ITERATION2_EVIDENCE_ROOT_HASH216 or controls.get("iteration3", {}).get("evidence_root_hash216") != ITERATION3_EVIDENCE_ROOT_HASH216:
        raise Pass215Iteration4ValidationError("PASS215_I4_CONTROL_ROOT_MISMATCH")
    if controls["iteration2"].get("raw_canonical_incidence_fraction_exact") != {"numerator": 0, "denominator": 1}:
        raise Pass215Iteration4ValidationError("PASS215_I4_ITERATION2_ZERO_INCIDENCE_CONTROL_VIOLATED")
    if int(controls["iteration3"].get("transformer_layer_dictionary_gain_bytes", -1)) != 0 or controls["iteration3"].get("embedding_output_storage_gain_excluded_from_execution_gain") is not True:
        raise Pass215Iteration4ValidationError("PASS215_I4_ITERATION3_EXECUTION_CONTROL_VIOLATED")
    modes = evidence.get("frozen_workload_modes")
    comparisons = evidence.get("frozen_profile_comparisons")
    optimizations = evidence.get("optimization_class_dispositions")
    stages = evidence.get("pass214_stage_dispositions")
    if not isinstance(modes, Mapping) or tuple(modes) != FROZEN_MODES:
        raise Pass215Iteration4ValidationError("PASS215_I4_FROZEN_MODE_SET_INVALID")
    if not isinstance(comparisons, Mapping) or tuple(comparisons) != FROZEN_COMPARISONS:
        raise Pass215Iteration4ValidationError("PASS215_I4_FROZEN_COMPARISON_SET_INVALID")
    if not isinstance(optimizations, Mapping) or set(optimizations) != set(FROZEN_OPTIMIZATION_CLASSES):
        raise Pass215Iteration4ValidationError("PASS215_I4_FROZEN_OPTIMIZATION_SET_INVALID")
    if not isinstance(stages, Mapping) or tuple(stages) != PASS214_STAGES:
        raise Pass215Iteration4ValidationError("PASS215_I4_PASS214_STAGE_SET_INVALID")
    claims = evidence.get("claims")
    if not isinstance(claims, Mapping):
        raise Pass215Iteration4ValidationError("PASS215_I4_CLAIMS_MISSING")
    for false_claim in (
        "embedding_output_dictionary_gain_counted_as_execution_gain",
        "full_transformer_layer_forward_executed",
        "rmsnorm_execution_claimed",
        "attention_softmax_execution_claimed",
        "silu_execution_claimed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "exact_nonlinear_transformer_operators_implemented",
        "pass213_compiled_rom_runtime_mutation_performed",
        "fifty_billion_desktop_feasibility_claimed",
        "arbitrary_compression_claimed",
    ):
        if claims.get(false_claim) is not False:
            raise Pass215Iteration4ValidationError(f"PASS215_I4_CLAIM_BOUNDARY_VIOLATED:{false_claim}")
    operators = evidence.get("operator_suite")
    if not isinstance(operators, list) or [item.get("name") for item in operators] != list(TARGET_OPERATORS):
        raise Pass215Iteration4ValidationError("PASS215_I4_OPERATOR_SUITE_INVALID")
    if not all(item.get("semantic_exactness") is True for item in operators):
        raise Pass215Iteration4ValidationError("PASS215_I4_OPERATOR_SEMANTIC_EXACTNESS_INVALID")
    payload = dict(evidence)
    root = payload.pop("evidence_root_hash216", None)
    receipt = payload.pop("receipt_hash72", None)
    expected_root = hash216("pass215-i4-execution-evidence", canonical_bytes(payload))
    if root != expected_root:
        raise Pass215Iteration4ValidationError("PASS215_I4_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION4_EXACT_LINEAR_EXECUTION"},
        {
            "sequence": 4,
            "parent_hash72": ITERATION3_RECEIPT_HASH72,
            "evidence_root_hash216": expected_root,
            "suite_output_root_hash216": evidence["suite_output_root_hash216"],
        },
    )
    if receipt != expected_receipt:
        raise Pass215Iteration4ValidationError("PASS215_I4_RECEIPT_MISMATCH")


def build_execution_evidence_from_path(
    path: Path,
    *,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
    frozen_profile_blob_sha1: str = FROZEN_PROFILE_GIT_BLOB_SHA1,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_execution_evidence(
        target.read_bytes(),
        filename=target.name,
        source=source,
        expected_sha256=expected_sha256,
        frozen_profile_blob_sha1=frozen_profile_blob_sha1,
    )


__all__ = [
    "CONTRACT",
    "EVIDENCE_SCHEMA",
    "REAL_MODEL_SHA256",
    "TARGET_OPERATORS",
    "FROZEN_COMPARISONS",
    "FROZEN_MODES",
    "PASS214_STAGES",
    "FROZEN_OPTIMIZATION_CLASSES",
    "Pass215Iteration4Error",
    "Pass215Iteration4ValidationError",
    "CompiledBlock",
    "CompiledTensor",
    "decode_binary16_exact",
    "decode_q4_0_codes",
    "deterministic_vector",
    "mutated_vector",
    "compile_q4_tensor",
    "execute_dense_reference",
    "execute_factored",
    "execute_continuation_delta",
    "output_root",
    "build_execution_evidence",
    "build_execution_evidence_from_path",
    "validate_execution_evidence",
]
