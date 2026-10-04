"""Pass 220 I073 — palindromic RNA / Fibonacci symbolic tensor generator.

I073 extends the compact I072 theory constructor through already-implemented
repository surfaces:

  I072 theory constructor
  -> I038 exact decimal + raw IEEE binary64/dyadic palindromic ingress
  -> I019 5184-character rational-scientific BigInt + bidirectional RNA binding
  -> Pass 192 nested modular Fibonacci compression witness
  -> Pass 118 exact HARMONICODE tensor-program execution/replay
  -> ordered Hash216 candidate
  -> I065 on-demand hydration/recompression

The candidate persists compact generator/proof roots. It does not persist the
full 5184-character carrier, 45 duplicated Fibonacci schedules, or the
3 x 5184 Hash216 expansion. All are deterministically reconstructible and are
validated before their compact roots are emitted.

IEEE binary64 is a boundary representation only; canonical arithmetic remains
exact integer/rational/symbolic arithmetic.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass118_symbolic_harmonicode_runtime_v1 import (
    HarmonicodeRuntimeEngine,
    PROGRAM_SCHEMA,
)
from hhs_runtime.hhs_pass219_fibonacci_compression_reference_v1 import (
    MAGNITUDES,
    OUTER_HYDRATION_MODULUS,
    build_witness as build_fibonacci_witness,
    expanded_cell_magnitude_schedules,
    fibonacci_prefix,
    reference_invariants as fibonacci_reference_invariants,
    source_membrane_depth,
)
from hhs_runtime.hhs_pass220_desi_lane5_parallel_exact_egress_v1 import (
    build_parallel_observation_carrier,
    validate_parallel_observation_carrier,
)
from hhs_runtime.hhs_pass220_g3_ouroboros_opcode_registry_v1 import (
    build_lane5_g3_pipeline_contract,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i072_theory_constructor_hash216_hydration_v1 import (
    build_theory_constructor,
    validate_theory_constructor,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    CELL_TOKEN_CHARACTERS,
    LO_SHU_FLAT,
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    bigint_to_offsets,
    deserialize_offsets_5184,
    offsets_to_bigint,
    serialize_offsets_5184,
)
from hhs_runtime.hhs_pass220_palindromic_ordered_phase_v1 import (
    palindromic_ordered_phase_witness,
)
from hhs_runtime.hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1 import (
    phase_locked_state_witness,
    validate_phase_locked_state,
)
from hhs_runtime.pass192.runtime import source_invariants as pass192_source_invariants

SCHEMA = "HHS_PASS_220_I073_PALINDROMIC_RNA_FIBONACCI_SYMBOLIC_TENSOR_V1"
PROFILE = "PASS220-I073-PALINDROMIC-RNA-FIBONACCI-SYMBOLIC-TENSOR-v1"
VERSION = "1.0.0"
DEFAULT_DECIMAL_SOURCE = "179971.179971"
DEFAULT_FIBONACCI_DEPTH = 10
RNA_WINDOW_CHARACTERS = 3
RNA_WINDOWS_TOTAL = SERIALIZED_CHARACTERS // RNA_WINDOW_CHARACTERS
HASH72_WIDTH = 72
HASH216_WIDTH = 216
FULL_HASH216_COMPONENTS = 3 * SERIALIZED_CHARACTERS
TENSOR_ROWS = len(MAGNITUDES)
TENSOR_COLUMNS = len(LO_SHU_FLAT)
TENSOR_ELEMENTS = TENSOR_ROWS * TENSOR_COLUMNS

SOURCE_BUNDLE = (
    {
        "role": "I072_THEORY_CONSTRUCTOR",
        "path": "hhs_runtime/hhs_pass220_i072_theory_constructor_hash216_hydration_v1.py",
        "git_blob_sha": "11e16f1f6ae6827cc0501fb78ebe7463b3e6b817",
    },
    {
        "role": "PALINDROMIC_IEEE_INGRESS",
        "path": "hhs_runtime/hhs_pass220_desi_lane5_parallel_exact_egress_v1.py",
        "git_blob_sha": "4479e11c9e9a87dc6aaaf583a3331aff4066b18a",
    },
    {
        "role": "G3_OUROBOROS_INGRESS_PIPELINE",
        "path": "hhs_runtime/hhs_pass220_g3_ouroboros_opcode_registry_v1.py",
        "git_blob_sha": "f312bff95d950589093a79d385ac26551f6d375e",
    },
    {
        "role": "RNA_BIGINT_PHASE_LOCK",
        "path": "hhs_runtime/hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1.py",
        "git_blob_sha": "84cb85e5c8b2f136a367dd4490ef2b3d800e1a9e",
    },
    {
        "role": "BIGINT_SCIENTIFIC_SERIALIZER",
        "path": "hhs_runtime/hhs_pass220_lo_shu_normalization_v1.py",
        "git_blob_sha": "cb18ec3f1d35017cb6c7b2b40848b398930270bc",
    },
    {
        "role": "NESTED_FIBONACCI_COMPRESSION",
        "path": "hhs_runtime/pass219_fibonacci_compression_reference_v1.py",
        "git_blob_sha": "bda83c1a8791dd4bd9e807a88e0a419848d1d140",
    },
    {
        "role": "PASS192_TENSOR_RUNTIME",
        "path": "hhs_runtime/pass192/runtime.py",
        "git_blob_sha": "279495e7b88adbd01e56eb6b8897c4d2f88bb948",
    },
    {
        "role": "HARMONICODE_SYMBOLIC_TENSOR_RUNTIME",
        "path": "hhs_runtime/hhs_pass118_symbolic_harmonicode_runtime_v1.py",
        "git_blob_sha": "823c4a09b239437ba060c2248ee0ac73becc34f5",
    },
    {
        "role": "HARMONICODE_LANGUAGE_SPEC",
        "path": "docs/HARMONICODE_SPEC_v1.md",
        "git_blob_sha": "25097da958792de4b5a9a3c2df9ea2ef283c3885",
    },
    {
        "role": "PALINDROMIC_ORDERED_PHASE_ALGEBRA",
        "path": "hhs_runtime/hhs_pass220_palindromic_ordered_phase_v1.py",
        "git_blob_sha": "535375bf8cd043a5c84f7d4cc9325fdf469a399e",
    },
)

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "ieee_binary64_boundary_only": True,
    "host_float_arithmetic_authority": False,
    "exact_decimal_source_preserved": True,
    "exact_ieee_dyadic_preserved": True,
    "bigint_serialization_lossless": True,
    "rna_transcription_read_only": True,
    "fibonacci_compression_reconstructible": True,
    "symbolic_tensor_runtime_exact": True,
    "expanded_5184_serialization_persisted": False,
    "expanded_45_fibonacci_schedules_persisted": False,
    "expanded_3x5184_hash216_geometry_persisted": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "external_egress_authority": False,
}


class Pass220I073GeneratorError(ValueError):
    """Raised when an I073 generator invariant fails."""


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I073GeneratorError(
            f"floating-point value forbidden in canonical payload at {path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _exact_int(value: Any, name: str, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I073GeneratorError(f"{name} must be an exact integer")
    if not lower <= value <= upper:
        raise Pass220I073GeneratorError(
            f"{name} must satisfy {lower} <= {name} <= {upper}"
        )
    return value


def _hash72_word(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH72_WIDTH:
        raise Pass220I073GeneratorError(
            f"{name} must be a 72-character Hash72 word"
        )
    return value


def _hash216_word(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH216_WIDTH:
        raise Pass220I073GeneratorError(
            f"{name} must be a 216-character Hash216 word"
        )
    return value


def _fraction_record(value: Fraction) -> dict[str, int]:
    q = Fraction(value)
    return {"numerator": q.numerator, "denominator": q.denominator}


def source_bundle_witness() -> dict[str, Any]:
    body = {
        "schema": f"{SCHEMA}_SOURCE_BUNDLE_V1",
        "sources": [dict(row) for row in SOURCE_BUNDLE],
        "source_count": len(SOURCE_BUNDLE),
        "roles_unique": len({r["role"] for r in SOURCE_BUNDLE}) == len(SOURCE_BUNDLE),
        "paths_unique": len({r["path"] for r in SOURCE_BUNDLE}) == len(SOURCE_BUNDLE),
    }
    body["source_bundle_root_sha256"] = _sha256(body)
    return body


def _scientific_serialization_descriptor(serialized: str) -> dict[str, Any]:
    offsets = deserialize_offsets_5184(serialized)
    scalar_bigint = offsets_to_bigint(offsets)
    recovered_offsets = bigint_to_offsets(
        scalar_bigint,
        length=VM81_CELLS,
    )
    recovered = serialize_offsets_5184(recovered_offsets)
    if recovered != serialized:
        raise Pass220I073GeneratorError(
            "BigInt/scientific serialization failed exact roundtrip"
        )

    tokens = tuple(
        serialized[start : start + CELL_TOKEN_CHARACTERS]
        for start in range(0, SERIALIZED_CHARACTERS, CELL_TOKEN_CHARACTERS)
    )
    dictionary: list[str] = []
    token_ids: list[int] = []
    positions: dict[str, int] = {}
    for token in tokens:
        if token not in positions:
            positions[token] = len(dictionary)
            dictionary.append(token)
        token_ids.append(positions[token])

    dictionary_tuple = tuple(dictionary)
    token_id_tuple = tuple(token_ids)
    reconstructed = "".join(dictionary_tuple[index] for index in token_id_tuple)
    if reconstructed != serialized:
        raise Pass220I073GeneratorError(
            "scientific-token dictionary reconstruction failed"
        )
    if len(dictionary_tuple) > 9:
        raise Pass220I073GeneratorError(
            "normalization scientific-token dictionary exceeds 0..8 alphabet"
        )

    return {
        "schema": f"{SCHEMA}_SCIENTIFIC_SERIALIZATION_DESCRIPTOR_V1",
        "serialized_characters": SERIALIZED_CHARACTERS,
        "cell_token_characters": CELL_TOKEN_CHARACTERS,
        "token_count": VM81_CELLS,
        "unique_token_count": len(dictionary_tuple),
        "scientific_token_dictionary": dictionary_tuple,
        "token_ids": token_id_tuple,
        "scalar_bigint": scalar_bigint,
        "serialized_sha256": sha256(serialized.encode("utf-8")).hexdigest(),
        "dictionary_root_sha256": _sha256(dictionary_tuple),
        "token_id_root_sha256": _sha256(token_id_tuple),
        "bigint_roundtrip_exact": recovered_offsets == offsets,
        "scientific_dictionary_roundtrip_exact": reconstructed == serialized,
        "canonical_serialized_5184_persisted_by_i073": False,
    }


def _build_palindromic_rna_ingress(
    *,
    decimal_text: str,
    offsets: Sequence[int],
) -> dict[str, Any]:
    offset_tuple = tuple(offsets)
    if len(offset_tuple) != VM81_CELLS:
        raise Pass220I073GeneratorError("ingress requires exactly 81 offsets")
    if any(
        isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 8
        for value in offset_tuple
    ):
        raise Pass220I073GeneratorError("ingress offsets must be exact integers in 0..8")

    carrier = build_parallel_observation_carrier(
        observable="I073_GENERATOR_INGRESS",
        decimal_text=decimal_text,
        offsets=offset_tuple,
        source_release_id="HHS_PASS_220_I073_GENERATOR_INGRESS",
    )
    validation = validate_parallel_observation_carrier(carrier)
    if validation.get("ok") is not True:
        raise Pass220I073GeneratorError("I038 ingress carrier did not validate")

    views = carrier["multirepresentational_constructor"]["representation_views"]
    serialized = views["bigint_5184"]
    if len(serialized) != SERIALIZED_CHARACTERS:
        raise Pass220I073GeneratorError("I038 BigInt view lost fixed 5184 width")

    scientific = _scientific_serialization_descriptor(serialized)
    rna = phase_locked_state_witness(serialized)
    rna_validation = validate_phase_locked_state(serialized)
    if rna_validation.get("ok") is not True or rna.get("phase_locked") is not True:
        raise Pass220I073GeneratorError("I019 RNA phase lock failed")

    palindrome = palindromic_ordered_phase_witness()
    if palindrome.get("phase_path_palindrome") is not True:
        raise Pass220I073GeneratorError("I015 palindromic phase witness failed")
    if palindrome.get("floating_point_authority") is not False:
        raise Pass220I073GeneratorError("I015 float authority widened")

    pipeline = build_lane5_g3_pipeline_contract()
    required_stages = (
        "PALINDROMIC_IEEE_EXACT_DYADIC_FRAME",
        "ORDERED_XYZW_RNA_5184_TRANSCRIPTION",
        "PASS219_CPP_RNA_CELL_WALL",
    )
    if not all(stage in tuple(pipeline["stages"]) for stage in required_stages):
        raise Pass220I073GeneratorError("G3 palindromic/RNA pipeline stage missing")

    return {
        "schema": f"{SCHEMA}_PALINDROMIC_RNA_INGRESS_V1",
        "decimal_source_text": decimal_text,
        "carrier_receipt_sha256": carrier["receipt_sha256"],
        "exact_decimal_rational": carrier["exact_decimal_rational"],
        "binary64_bits_hex": carrier["binary64_bits_hex"],
        "exact_ieee_dyadic": carrier["exact_ieee_dyadic"],
        "decimal_minus_ieee_exact_residue": carrier[
            "decimal_minus_ieee_exact_residue"
        ],
        "decimal_and_ieee_are_co_resident": carrier[
            "decimal_and_ieee_are_co_resident"
        ],
        "ieee_raw_bits_roundtrip": carrier["multirepresentational_validation"][
            "ieee_reciprocal_roundtrip"
        ],
        "symbol_reciprocal_roundtrip": carrier[
            "multirepresentational_validation"
        ]["symbol_reciprocal_roundtrip"],
        "scientific_serialization": scientific,
        "rna_state_root_sha256": rna["state_root_sha256"],
        "rna_witness_receipt_sha256": rna["receipt_sha256"],
        "rna_validation_receipt_sha256": rna_validation["receipt_sha256"],
        "rna_windows_total": rna["rna"]["rna_windows_total"],
        "rna_double_reverse_exact": rna["rna"]["double_reverse_exact"],
        "ordered_xyzw_products": rna["digital_dna"][
            "q_minus_one_ordered_products"
        ],
        "palindromic_phase_receipt_sha256": palindrome["receipt_sha256"],
        "g3_pipeline_root_hash72": _hash72_word(
            pipeline["pipeline_root_hash72"],
            "g3_pipeline_root_hash72",
        ),
        "g3_constructor_graph_root_hash72": _hash72_word(
            pipeline["mandatory_constructor_graph_root_hash72"],
            "g3_constructor_graph_root_hash72",
        ),
        "ieee_binary64_boundary_only": True,
        "host_float_arithmetic_authority": False,
        "canonical_mutation_authority": False,
    }


def _fibonacci_compression_descriptor(
    *,
    depth: int,
    parent_constructor_root_sha256: str,
) -> dict[str, Any]:
    d = _exact_int(depth, "fibonacci_depth", 0, 4096)
    witness = build_fibonacci_witness(d)
    if not witness.valid():
        raise Pass220I073GeneratorError("Pass 192 Fibonacci witness invalid")
    if not all(pass192_source_invariants().values()):
        raise Pass220I073GeneratorError("Pass 192 source invariants failed")

    schedule = fibonacci_prefix(d)
    expanded = expanded_cell_magnitude_schedules(d)
    if len(expanded) != TENSOR_ELEMENTS:
        raise Pass220I073GeneratorError("Pass 192 expanded schedule count drift")
    if any(item[2] != schedule for item in expanded):
        raise Pass220I073GeneratorError("Fibonacci shared-schedule dedup invalid")

    reference = fibonacci_reference_invariants()
    reference_default_closed = (
        all(reference.values()) if d == source_membrane_depth() else None
    )
    return {
        "schema": f"{SCHEMA}_FIBONACCI_COMPRESSION_V1",
        "depth": d,
        "f_depth": witness.f_depth,
        "f_next": witness.f_next,
        "transition": _fraction_record(witness.transition),
        "cumulative_scale": _fraction_record(witness.cumulative_scale),
        "membrane_modulus": witness.membrane_modulus,
        "membrane_residue": witness.membrane_residue,
        "magnitude_rows": tuple(witness.magnitude_rows),
        "lo_shu_cell_count": witness.lo_shu_cell_count,
        "shared_schedule_count": witness.shared_schedule_count,
        "expanded_schedule_count": witness.expanded_schedule_count,
        "outer_hydration_modulus": witness.outer_modulus,
        "schedule": schedule,
        "schedule_root_sha256": _sha256(schedule),
        "expanded_schedule_root_sha256": _sha256(expanded),
        "parent_constructor_root_sha256": parent_constructor_root_sha256,
        "reference_default_depth": source_membrane_depth(),
        "reference_default_closed": reference_default_closed,
        "expanded_45_schedules_persisted": False,
        "reconstructible_from_shared_schedule_and_labels": True,
    }


def _literal_integer(value: int) -> dict[str, Any]:
    return {"node": "literal", "kind": "INTEGER", "value": int(value)}


def _symbolic_tensor_program(
    *,
    authority_root_hash72: str,
) -> dict[str, Any]:
    authority = _hash72_word(authority_root_hash72, "authority_root_hash72")
    magnitude_tensor = {
        "node": "tensor",
        "shape": [TENSOR_ROWS],
        "values": [_literal_integer(value) for value in MAGNITUDES],
    }
    lo_shu_tensor = {
        "node": "tensor",
        "shape": [TENSOR_COLUMNS],
        "values": [_literal_integer(value) for value in LO_SHU_FLAT],
    }
    expression = {
        "node": "call",
        "op": "tensor_product",
        "args": [magnitude_tensor, lo_shu_tensor],
    }
    program = {
        "schema": PROGRAM_SCHEMA,
        "program_id": "pass220:i073:fibonacci-lo-shu-tensor",
        "scope": "pass220-i073-candidate",
        "symbols": [],
        "operations": [
            {
                "kind": "bind",
                "name": "fibonacci_lo_shu_tensor",
                "expression": expression,
            }
        ],
    }
    runtime = HarmonicodeRuntimeEngine()
    executed = runtime.execute_program(
        program,
        authority_root_hash72=authority,
    )
    equivalence = runtime.validate_runtime_equivalence(
        program,
        authority_root_hash72=authority,
    )
    output = executed["outputs"][0]
    if output.get("type") != "TENSOR":
        raise Pass220I073GeneratorError("HARMONICODE tensor result type drift")
    value = output["value"]
    if value.get("shape") != [TENSOR_ROWS, TENSOR_COLUMNS]:
        raise Pass220I073GeneratorError("HARMONICODE tensor shape drift")

    expected = [
        magnitude * lo_shu
        for magnitude in MAGNITUDES
        for lo_shu in LO_SHU_FLAT
    ]
    actual = []
    for item in value["values"]:
        if not isinstance(item, Mapping) or item.get("kind") != "RATIONAL":
            raise Pass220I073GeneratorError("tensor result lost exact rational type")
        q = Fraction(item["numerator"], item["denominator"])
        if q.denominator != 1:
            raise Pass220I073GeneratorError("tensor result is not exact integer")
        actual.append(q.numerator)
    if actual != expected:
        raise Pass220I073GeneratorError("HARMONICODE tensor result mismatch")
    if equivalence.get("equivalence_status") != (
        "SYMBOLIC_RUNTIME_EQUIVALENCE_VALIDATED"
    ):
        raise Pass220I073GeneratorError("HARMONICODE replay equivalence failed")

    return {
        "schema": f"{SCHEMA}_HARMONICODE_SYMBOLIC_TENSOR_V1",
        "program_id": program["program_id"],
        "program_root_hash72": _hash72_word(
            executed["receipt"]["program_root_hash72"],
            "program_root_hash72",
        ),
        "execution_receipt_root_hash72": _hash72_word(
            executed["receipt"]["execution_receipt_root_hash72"],
            "execution_receipt_root_hash72",
        ),
        "terminal_state_root_hash72": _hash72_word(
            executed["receipt"]["terminal_state_root_hash72"],
            "terminal_state_root_hash72",
        ),
        "equivalence_root_hash72": _hash72_word(
            equivalence["equivalence_root_hash72"],
            "equivalence_root_hash72",
        ),
        "equivalence_status": equivalence["equivalence_status"],
        "tensor_shape": (TENSOR_ROWS, TENSOR_COLUMNS),
        "tensor_elements": TENSOR_ELEMENTS,
        "tensor_values": tuple(actual),
        "tensor_values_root_sha256": _sha256(tuple(actual)),
        "ordered_tensor_operation": "tensor_product",
        "source_language": "HARMONICODE_TYPED_JSON_IR",
        "host_eval_used": False,
        "float_canonical_authority": False,
        "canonical_mutation_authority": False,
    }


def build_generator(
    *,
    decimal_text: str = DEFAULT_DECIMAL_SOURCE,
    offsets: Sequence[int] | None = None,
    fibonacci_depth: int | None = None,
    nucleus_index: int = 0,
    nesting_depth: int = 0,
) -> dict[str, Any]:
    if not isinstance(decimal_text, str) or not decimal_text:
        raise Pass220I073GeneratorError("decimal_text must be a non-empty string")
    offset_tuple = tuple(
        (0,) * VM81_CELLS if offsets is None else offsets
    )
    depth = (
        source_membrane_depth()
        if fibonacci_depth is None
        else _exact_int(fibonacci_depth, "fibonacci_depth", 0, 4096)
    )

    parent = build_theory_constructor(
        nucleus_index=nucleus_index,
        nesting_depth=nesting_depth,
    )
    if not validate_theory_constructor(parent):
        raise Pass220I073GeneratorError("I072 parent constructor invalid")

    sources = source_bundle_witness()
    ingress = _build_palindromic_rna_ingress(
        decimal_text=decimal_text,
        offsets=offset_tuple,
    )
    fib = _fibonacci_compression_descriptor(
        depth=depth,
        parent_constructor_root_sha256=parent[
            "theory_constructor_root_sha256"
        ],
    )
    symbolic = _symbolic_tensor_program(
        authority_root_hash72=parent["binding_hash72"],
    )

    previous = hash72(
        {
            "schema": f"{SCHEMA}_PREVIOUS_V1",
            "parent_theory_constructor_root_sha256": parent[
                "theory_constructor_root_sha256"
            ],
            "parent_theory_hash216": parent["theory_hash216"],
            "source_bundle_root_sha256": sources["source_bundle_root_sha256"],
        }
    )
    change = hash72(
        {
            "schema": f"{SCHEMA}_CHANGE_V1",
            "ingress": {
                "carrier_receipt_sha256": ingress["carrier_receipt_sha256"],
                "binary64_bits_hex": ingress["binary64_bits_hex"],
                "rna_witness_receipt_sha256": ingress[
                    "rna_witness_receipt_sha256"
                ],
                "scientific_serialization": {
                    "scalar_bigint": ingress["scientific_serialization"][
                        "scalar_bigint"
                    ],
                    "serialized_sha256": ingress["scientific_serialization"][
                        "serialized_sha256"
                    ],
                    "dictionary_root_sha256": ingress[
                        "scientific_serialization"
                    ]["dictionary_root_sha256"],
                },
            },
            "fibonacci": {
                "depth": fib["depth"],
                "schedule_root_sha256": fib["schedule_root_sha256"],
                "expanded_schedule_root_sha256": fib[
                    "expanded_schedule_root_sha256"
                ],
                "transition": fib["transition"],
                "cumulative_scale": fib["cumulative_scale"],
            },
            "symbolic": {
                "program_root_hash72": symbolic["program_root_hash72"],
                "equivalence_root_hash72": symbolic[
                    "equivalence_root_hash72"
                ],
                "tensor_values_root_sha256": symbolic[
                    "tensor_values_root_sha256"
                ],
            },
        }
    )
    receipt = hash72(
        {
            "schema": f"{SCHEMA}_RECEIPT_V1",
            "bigint_roundtrip_exact": ingress["scientific_serialization"][
                "bigint_roundtrip_exact"
            ],
            "scientific_dictionary_roundtrip_exact": ingress[
                "scientific_serialization"
            ]["scientific_dictionary_roundtrip_exact"],
            "rna_double_reverse_exact": ingress["rna_double_reverse_exact"],
            "fibonacci_reconstructible": fib[
                "reconstructible_from_shared_schedule_and_labels"
            ],
            "symbolic_runtime_equivalence": symbolic["equivalence_status"],
            "authority": AUTHORITY_BOUNDARY,
        }
    )
    generator_hash216 = _hash216_word(
        previous + change + receipt,
        "generator_hash216",
    )
    hydrated = hydrate_hash216_geometry(generator_hash216)
    if hydrated.get("roundtrip_exact") is not True:
        raise Pass220I073GeneratorError(
            "I073 Hash216 failed I065 exact hydration/recompression"
        )
    if hydrated.get("full_attached_components") != FULL_HASH216_COMPONENTS:
        raise Pass220I073GeneratorError("I073 hydrated component count drift")

    plane_roots = tuple(
        {
            "role": plane["role"],
            "generator_hash72": plane["generator_hash72"],
            "expanded_vertices": plane["expanded_vertices"],
            "expanded_geometry_sha256": plane["expanded_geometry_sha256"],
            "roundtrip_exact": plane["roundtrip_exact"],
        }
        for plane in hydrated["planes"]
    )

    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "parent_i072": {
            "theory_constructor_root_sha256": parent[
                "theory_constructor_root_sha256"
            ],
            "binding_hash72": parent["binding_hash72"],
            "theory_hash216": parent["theory_hash216"],
        },
        "source_bundle": sources,
        "palindromic_rna_ingress": ingress,
        "fibonacci_compression": fib,
        "symbolic_tensor_program": symbolic,
        "generator_hash216": generator_hash216,
        "plane_roots": plane_roots,
        "storage_optimization": {
            "persist_parent_constructor_root": True,
            "persist_hash216_generator": True,
            "persist_ieee_raw_bits": True,
            "persist_exact_decimal_dyadic_residue": True,
            "persist_scalar_bigint": True,
            "persist_scientific_token_dictionary": True,
            "persist_shared_fibonacci_schedule": True,
            "persist_symbolic_tensor_root": True,
            "persist_full_5184_serialization": False,
            "persist_45_fibonacci_schedule_copies": False,
            "persist_3x5184_hash216_expansion": False,
            "on_demand_exact_reconstruction": True,
        },
        "authority": dict(AUTHORITY_BOUNDARY),
    }
    result["generator_root_sha256"] = _sha256(result)
    result["binding_hash72"] = hash72(
        {
            "schema": SCHEMA,
            "generator_root_sha256": result["generator_root_sha256"],
            "generator_hash216": generator_hash216,
            "parent_binding_hash72": parent["binding_hash72"],
            "serialized_sha256": ingress["scientific_serialization"][
                "serialized_sha256"
            ],
            "fibonacci_schedule_root_sha256": fib["schedule_root_sha256"],
            "symbolic_equivalence_root_hash72": symbolic[
                "equivalence_root_hash72"
            ],
            "plane_roots": plane_roots,
        }
    )
    return result


def reconstruct_serialized_state(generator: Mapping[str, Any]) -> str:
    validate_generator(generator)
    descriptor = generator["palindromic_rna_ingress"][
        "scientific_serialization"
    ]
    offsets = bigint_to_offsets(
        descriptor["scalar_bigint"],
        length=VM81_CELLS,
    )
    serialized = serialize_offsets_5184(offsets)
    if sha256(serialized.encode("utf-8")).hexdigest() != descriptor[
        "serialized_sha256"
    ]:
        raise Pass220I073GeneratorError("reconstructed 5184 state root mismatch")
    return serialized


def validate_generator(generator: Mapping[str, Any]) -> bool:
    if not isinstance(generator, Mapping):
        raise Pass220I073GeneratorError("generator must be a mapping")
    if generator.get("schema") != SCHEMA:
        raise Pass220I073GeneratorError("generator schema mismatch")

    ingress = generator.get("palindromic_rna_ingress")
    fib = generator.get("fibonacci_compression")
    parent = generator.get("parent_i072")
    if not all(isinstance(value, Mapping) for value in (ingress, fib, parent)):
        raise Pass220I073GeneratorError("generator bindings missing")

    serialized_descriptor = ingress["scientific_serialization"]
    offsets = bigint_to_offsets(
        serialized_descriptor["scalar_bigint"],
        length=VM81_CELLS,
    )
    canonical = build_generator(
        decimal_text=ingress["decimal_source_text"],
        offsets=offsets,
        fibonacci_depth=fib["depth"],
        nucleus_index=generator["parent_i072"].get("nucleus_index", 0)
        if "nucleus_index" in generator["parent_i072"] else 0,
        nesting_depth=generator["parent_i072"].get("nesting_depth", 0)
        if "nesting_depth" in generator["parent_i072"] else 0,
    )

    # Parent identity is included explicitly in every derived root. If a caller
    # supplied a generator produced for another parent geometry, exact object
    # equality rejects it even if the compact payload is otherwise well-formed.
    for key in (
        "parent_i072",
        "source_bundle",
        "palindromic_rna_ingress",
        "fibonacci_compression",
        "symbolic_tensor_program",
        "generator_hash216",
        "plane_roots",
        "storage_optimization",
        "authority",
        "generator_root_sha256",
        "binding_hash72",
    ):
        if generator.get(key) != canonical[key]:
            raise Pass220I073GeneratorError(f"generator diverges at {key}")
    return True


def self_test() -> dict[str, Any]:
    offsets = tuple(index % 9 for index in range(VM81_CELLS))
    generator = build_generator(
        decimal_text=DEFAULT_DECIMAL_SOURCE,
        offsets=offsets,
        fibonacci_depth=DEFAULT_FIBONACCI_DEPTH,
        nucleus_index=0,
        nesting_depth=0,
    )
    serialized = reconstruct_serialized_state(generator)
    ingress = generator["palindromic_rna_ingress"]
    fib = generator["fibonacci_compression"]
    symbolic = generator["symbolic_tensor_program"]
    checks = {
        "generator_valid": validate_generator(generator),
        "binary64_boundary_bits_64": len(ingress["binary64_bits_hex"]) == 16,
        "decimal_ieee_co_resident": ingress["decimal_and_ieee_are_co_resident"],
        "bigint_5184_reconstructed": len(serialized) == SERIALIZED_CHARACTERS,
        "bigint_roundtrip_exact": ingress["scientific_serialization"][
            "bigint_roundtrip_exact"
        ],
        "scientific_dictionary_roundtrip_exact": ingress[
            "scientific_serialization"
        ]["scientific_dictionary_roundtrip_exact"],
        "rna_windows_1728": ingress["rna_windows_total"] == RNA_WINDOWS_TOTAL,
        "rna_double_reverse_exact": ingress["rna_double_reverse_exact"],
        "fibonacci_depth10_144_233": (
            fib["depth"] == 10
            and fib["f_depth"] == 144
            and fib["f_next"] == 233
        ),
        "fibonacci_cumulative_1_144": fib["cumulative_scale"]
        == {"numerator": 1, "denominator": 144},
        "fibonacci_shared_schedule": (
            fib["shared_schedule_count"] == 1
            and fib["expanded_schedule_count"] == 45
        ),
        "symbolic_tensor_5x9": symbolic["tensor_shape"] == (5, 9),
        "symbolic_tensor_45": symbolic["tensor_elements"] == 45,
        "symbolic_runtime_equivalence": symbolic["equivalence_status"]
        == "SYMBOLIC_RUNTIME_EQUIVALENCE_VALIDATED",
        "hash216_width_216": len(generator["generator_hash216"]) == 216,
        "three_plane_roots": len(generator["plane_roots"]) == 3,
        "no_expanded_state_persisted": (
            generator["storage_optimization"]["persist_full_5184_serialization"]
            is False
            and generator["storage_optimization"][
                "persist_45_fibonacci_schedule_copies"
            ]
            is False
            and generator["storage_optimization"][
                "persist_3x5184_hash216_expansion"
            ]
            is False
        ),
        "candidate_only": generator["authority"]["candidate_only"] is True,
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [name for name, passed in checks.items() if not passed],
        "checks": checks,
        "generator_root_sha256": generator["generator_root_sha256"],
        "binding_hash72": generator["binding_hash72"],
        "generator_hash216": generator["generator_hash216"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "DEFAULT_DECIMAL_SOURCE",
    "DEFAULT_FIBONACCI_DEPTH",
    "Pass220I073GeneratorError",
    "SCHEMA",
    "SOURCE_BUNDLE",
    "build_generator",
    "reconstruct_serialized_state",
    "self_test",
    "source_bundle_witness",
    "validate_generator",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
