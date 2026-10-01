"""Pass 220 I065 lossless emergent compression and Hash216 hydration.

I065 formalizes the fixed-geometry representation discussed by the Pass 220
Lane 5 stack.  It is deliberately scoped to HHS-admitted fixed geometry:
a Hash72 word is a 72-position generator over the canonical 72 x 72 = 5184
vertex lattice.  Hydration reconstructs that lattice deterministically and
compression recovers the original Hash72 word exactly.

This is not a claim that arbitrary unconstrained 5184-symbol payloads compress
72:1.  The gain exists only where the omitted structure is fixed by inherited
HHS geometry and can therefore be reconstructed from the generator plus the
shared pipeline.

I065 is candidate/read-only infrastructure.  It grants no VM81 mutation,
Hash72 commit, Hash216 persistence, GPU canonical-state, or float authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    HASH72_ALPHABET,
    HASH72_LEN,
    HASH216_LEN,
    LANE_ORDER,
    VM5184,
    coordinate_5184,
    split_hash216,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    CELL_TOKEN_CHARACTERS,
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    deserialize_offsets_5184,
    serialize_offsets_5184,
)

SCHEMA = "HHS_PASS_220_I065_LOSSLESS_EMERGENT_COMPRESSION_HYDRATION_V1"
VERSION = "1.0.0"
BASE_MAIN = "c7c984dfb0b635974c2cf4531786d3ff7b2ec7cb"

HASH72_BASE = len(HASH72_ALPHABET)
HASH72_POSITIONS = HASH72_LEN
EXPANDED_VERTICES = HASH72_BASE * HASH72_POSITIONS
VM81_FACTOR = VM81_CELLS * CELL_TOKEN_CHARACTERS
HASH216_PLANES = len(LANE_ORDER)
HASH216_FLAT_POSITIONS = HASH216_PLANES * HASH72_POSITIONS
FULL_HASH216_COMPONENTS = HASH216_PLANES * EXPANDED_VERTICES
STRUCTURAL_COMPRESSION = Fraction(HASH72_POSITIONS, EXPANDED_VERTICES)

if HASH72_BASE != 72:
    raise AssertionError("Hash72 alphabet cardinality drift")
if EXPANDED_VERTICES != VM5184 or EXPANDED_VERTICES != 5184:
    raise AssertionError("72x72 != VM5184")
if VM81_FACTOR != VM5184:
    raise AssertionError("81x64 != VM5184")
if HASH216_FLAT_POSITIONS != HASH216_LEN or HASH216_LEN != 216:
    raise AssertionError("3x72 != Hash216 width")
if STRUCTURAL_COMPRESSION != Fraction(1, 72):
    raise AssertionError("Hash72 structural ratio drift")


class I065HydrationError(ValueError):
    """Fail-closed I065 validation error."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _root(value: Any) -> str:
    return sha256(value.encode("utf-8") if isinstance(value, str) else _canonical(value)).hexdigest()


def _require_exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise I065HydrationError(f"{name} must be an exact integer")
    return value


def _validate_hash72_word(value: Any, *, name: str = "Hash72") -> str:
    if not isinstance(value, str) or len(value) != HASH72_POSITIONS:
        raise I065HydrationError(f"{name} must contain exactly 72 symbols")
    alphabet = set(HASH72_ALPHABET)
    bad = next((char for char in value if char not in alphabet), None)
    if bad is not None:
        raise I065HydrationError(f"{name} contains non-HARMONICODE symbol {bad!r}")
    return value


def sha256_alphabet72() -> tuple[tuple[str, str], ...]:
    """Return the fixed 72-symbol -> SHA-256 codeword translation table."""
    table = tuple(
        (symbol, sha256(symbol.encode("utf-8")).hexdigest())
        for symbol in HASH72_ALPHABET
    )
    if len(table) != 72 or len({symbol for symbol, _ in table}) != 72:
        raise AssertionError("Hash72 alphabet is not a 72-symbol set")
    if len({codeword for _, codeword in table}) != 72:
        raise I065HydrationError("SHA-256 alphabet codeword collision detected")
    return table


def mirror_index(index: int) -> int:
    """Return the fixed 5184-position palindromic address partner."""
    i = _require_exact_int(index, name="index")
    if not 0 <= i < EXPANDED_VERTICES:
        raise I065HydrationError("mirror index must lie in [0, 5183]")
    return EXPANDED_VERTICES - 1 - i


def mirror_geometry_witness() -> dict[str, Any]:
    """Exhaustively prove the even-width 5184 mirror-address involution."""
    pairs = tuple((i, mirror_index(i)) for i in range(EXPANDED_VERTICES))
    involutive = all(mirror_index(partner) == i for i, partner in pairs)
    fixed_points = tuple(i for i, partner in pairs if i == partner)
    center_pair = (EXPANDED_VERTICES // 2 - 1, EXPANDED_VERTICES // 2)
    if not involutive or fixed_points:
        raise I065HydrationError("5184 mirror geometry failed involution")
    if (mirror_index(center_pair[0]), mirror_index(center_pair[1])) != (
        center_pair[1],
        center_pair[0],
    ):
        raise I065HydrationError("5184 center mirror pair drift")
    return {
        "positions": EXPANDED_VERTICES,
        "rule": "mirror(i)=5183-i",
        "involutive": True,
        "fixed_points": 0,
        "center_pair_zero_based": center_pair,
        "center_pair_one_based": (center_pair[0] + 1, center_pair[1] + 1),
    }


def structural_ratio(depth: int = 1) -> dict[str, Any]:
    """Return the exact fixed-geometry structural representation ratio."""
    d = _require_exact_int(depth, name="depth")
    if d < 0:
        raise I065HydrationError("depth must be nonnegative")
    ratio = STRUCTURAL_COMPRESSION ** d
    expansion = HASH72_BASE ** d
    return {
        "depth": d,
        "single_layer_numerator": STRUCTURAL_COMPRESSION.numerator,
        "single_layer_denominator": STRUCTURAL_COMPRESSION.denominator,
        "ratio_numerator": ratio.numerator,
        "ratio_denominator": ratio.denominator,
        "expansion_factor": expansion,
        "identity": "(72/5184)^n=(1/72)^n",
        "scope": "HHS_ADMITTED_FIXED_GEOMETRY",
        "generic_unconstrained_payload_compression_claimed": False,
    }


def hash72_vertex_geometry(word: str) -> tuple[dict[str, Any], ...]:
    """Hydrate one Hash72 word into its exact 72x72=5184 vertex geometry.

    Row i is bound to the source symbol at Hash72 position i.  Column j is the
    fixed coupled Hash72 alphabet position j.  Therefore character identity,
    source position, coupled character/position, linear5184 address, VM81
    address, and mirror partner are all explicit in every hydrated vertex.
    """
    source = _validate_hash72_word(word)
    vertices: list[dict[str, Any]] = []
    for source_position, source_symbol in enumerate(source):
        for coupled_position, coupled_symbol in enumerate(HASH72_ALPHABET):
            linear = HASH72_BASE * source_position + coupled_position
            coordinate = coordinate_5184(linear)
            vertices.append({
                "linear5184": linear,
                "source_position72": source_position,
                "source_symbol": source_symbol,
                "coupled_position72": coupled_position,
                "coupled_symbol": coupled_symbol,
                "hash72_row": coordinate["hash72_row"],
                "hash72_column": coordinate["hash72_column"],
                "vm81_cell": coordinate["vm81_cell"],
                "local64": coordinate["local64"],
                "mirror5184": mirror_index(linear),
            })
    if len(vertices) != EXPANDED_VERTICES:
        raise AssertionError("Hash72 hydration did not materialize 5184 vertices")
    return tuple(vertices)


def compress_hash72_vertex_geometry(vertices: Sequence[Mapping[str, Any]]) -> str:
    """Recover the Hash72 generator from a fully admitted 5184 geometry."""
    rows = tuple(vertices)
    if len(rows) != EXPANDED_VERTICES:
        raise I065HydrationError("expanded geometry must contain exactly 5184 vertices")

    recovered: list[str] = []
    seen_linear: set[int] = set()
    for source_position in range(HASH72_POSITIONS):
        row_start = source_position * HASH72_BASE
        source_symbol: str | None = None
        for coupled_position in range(HASH72_BASE):
            expected_linear = row_start + coupled_position
            raw = rows[expected_linear]
            if not isinstance(raw, Mapping):
                raise I065HydrationError("expanded vertex must be a mapping")
            if raw.get("linear5184") != expected_linear:
                raise I065HydrationError("linear5184 position drift")
            if expected_linear in seen_linear:
                raise I065HydrationError("duplicate linear5184 address")
            seen_linear.add(expected_linear)
            if raw.get("source_position72") != source_position:
                raise I065HydrationError("source Hash72 position drift")
            if raw.get("coupled_position72") != coupled_position:
                raise I065HydrationError("coupled Hash72 position drift")
            if raw.get("coupled_symbol") != HASH72_ALPHABET[coupled_position]:
                raise I065HydrationError("coupled Hash72 character-position drift")
            current_source = raw.get("source_symbol")
            if (
                not isinstance(current_source, str)
                or len(current_source) != 1
                or current_source not in HASH72_ALPHABET
            ):
                raise I065HydrationError("source symbol is not a Hash72 alphabet member")
            if source_symbol is None:
                source_symbol = current_source
            elif current_source != source_symbol:
                raise I065HydrationError("source symbol changed within one hydrated row")
            coordinate = coordinate_5184(expected_linear)
            if raw.get("hash72_row") != coordinate["hash72_row"]:
                raise I065HydrationError("Hash72 row coordinate drift")
            if raw.get("hash72_column") != coordinate["hash72_column"]:
                raise I065HydrationError("Hash72 column coordinate drift")
            if raw.get("vm81_cell") != coordinate["vm81_cell"]:
                raise I065HydrationError("VM81 cell coordinate drift")
            if raw.get("local64") != coordinate["local64"]:
                raise I065HydrationError("VM81 local64 coordinate drift")
            if raw.get("mirror5184") != mirror_index(expected_linear):
                raise I065HydrationError("palindromic mirror-address drift")
        assert source_symbol is not None
        recovered.append(source_symbol)

    if len(seen_linear) != EXPANDED_VERTICES:
        raise I065HydrationError("expanded geometry does not cover all 5184 addresses")
    return _validate_hash72_word("".join(recovered), name="recovered Hash72")


def hash216_vertex72_geometry(hash216: str) -> tuple[dict[str, Any], ...]:
    """Express Hash216 as one ordered three-component geometry on 72 vertices."""
    previous, change, receipt = split_hash216(hash216)
    codewords = dict(sha256_alphabet72())
    lanes = (previous, change, receipt)
    result = []
    for position in range(HASH72_POSITIONS):
        symbols = tuple(lane[position] for lane in lanes)
        result.append({
            "vertex72": position,
            "lane_order": LANE_ORDER,
            "symbols": symbols,
            "sha256_codewords": tuple(codewords[symbol] for symbol in symbols),
        })
    if len(result) != HASH72_POSITIONS:
        raise AssertionError("Hash216 vertex geometry must contain 72 vertices")
    return tuple(result)


def hydrate_hash216_geometry(hash216: str) -> dict[str, Any]:
    """Hydrate all three Hash72 planes and prove exact recompression."""
    lanes = split_hash216(hash216)
    plane_roots = []
    for role, lane in zip(LANE_ORDER, lanes):
        expanded = hash72_vertex_geometry(lane)
        recovered = compress_hash72_vertex_geometry(expanded)
        if recovered != lane:
            raise I065HydrationError(f"{role} Hash72 hydration roundtrip failed")
        plane_roots.append({
            "role": role,
            "expanded_vertices": len(expanded),
            "generator_hash72": lane,
            "expanded_geometry_sha256": _root(expanded),
            "roundtrip_exact": True,
        })
    recomposed = "".join(lanes)
    if recomposed != hash216:
        raise I065HydrationError("Hash216 three-plane recomposition failed")
    return {
        "schema": f"{SCHEMA}_HASH216_GEOMETRY_V1",
        "hash216_positions": HASH216_FLAT_POSITIONS,
        "three_dimensional_vertex_count": HASH72_POSITIONS,
        "components_per_vertex": HASH216_PLANES,
        "full_attached_components": FULL_HASH216_COMPONENTS,
        "vertex72_geometry": hash216_vertex72_geometry(hash216),
        "planes": tuple(plane_roots),
        "roundtrip_exact": True,
    }


def validate_binary5184(binary: str) -> str:
    if not isinstance(binary, str) or len(binary) != EXPANDED_VERTICES:
        raise I065HydrationError("binary pipeline state must contain exactly 5184 bits")
    if any(bit not in "01" for bit in binary):
        raise I065HydrationError("binary pipeline state must contain only 0/1")
    if binary != binary[::-1]:
        raise I065HydrationError("binary pipeline state must satisfy 5184 mirror palindrome")
    return binary


def validate_serialized5184(serialized: str) -> tuple[int, ...]:
    """Validate the inherited fixed-width zero-padded rational-scientific ABI."""
    if not isinstance(serialized, str) or len(serialized) != SERIALIZED_CHARACTERS:
        raise I065HydrationError("BigInt carrier must contain exactly 5184 characters")
    try:
        offsets = deserialize_offsets_5184(serialized)
    except Exception as exc:
        raise I065HydrationError("BigInt carrier is not canonical 5184 serialization") from exc
    if serialize_offsets_5184(offsets) != serialized:
        raise I065HydrationError("BigInt carrier failed exact canonical roundtrip")
    return offsets


def bind_binary_serialized_pipeline(binary: str, serialized: str) -> dict[str, Any]:
    """Bind both 5184-wide modalities to the same coordinate/mirror geometry."""
    bits = validate_binary5184(binary)
    offsets = validate_serialized5184(serialized)
    records = []
    for index, (bit, character) in enumerate(zip(bits, serialized)):
        coordinate = coordinate_5184(index)
        records.append((
            index,
            bit,
            character,
            coordinate["hash72_row"],
            coordinate["hash72_column"],
            coordinate["vm81_cell"],
            coordinate["local64"],
            mirror_index(index),
        ))
    return {
        "schema": f"{SCHEMA}_PIPELINE_BINDING_V1",
        "binary_width": len(bits),
        "serialized_width": len(serialized),
        "offset_count": len(offsets),
        "binary_palindrome_exact": bits == bits[::-1],
        "serialized_zero_padding_inherited": True,
        "serialized_palindromic_address_geometry": mirror_geometry_witness(),
        "binary_sha256": _root(bits),
        "serialized_sha256": _root(serialized),
        "position_binding_sha256": _root(records),
        "same_5184_geometry": len(records) == EXPANDED_VERTICES,
    }


def hydrate_cycle(
    *,
    hash216: str,
    binary5184: str,
    serialized5184: str,
    depth: int = 1,
    exceptions: Sequence[Any] = (),
) -> dict[str, Any]:
    """Execute one deterministic read-only I065 hydration/verification cycle."""
    ratio = structural_ratio(depth)
    pipeline = bind_binary_serialized_pipeline(binary5184, serialized5184)
    hydrated = hydrate_hash216_geometry(hash216)
    exception_tuple = tuple(exceptions)

    receipt = {
        "schema": SCHEMA,
        "version": VERSION,
        "base_main": BASE_MAIN,
        "cycle": (
            "VALIDATE_PIPELINE",
            "SPLIT_HASH216_3x72",
            "HYDRATE_3x5184",
            "BIND_SHA256_ALPHABET",
            "BIND_BINARY_AND_SERIALIZATION",
            "RECOMPRESS_3xHASH72",
            "RECOMPOSE_HASH216",
            "EMIT_CANDIDATE_RECEIPT",
        ),
        "ratio": ratio,
        "pipeline": pipeline,
        "hash216": {
            "input_sha256": _root(hash216),
            "vertex72_root_sha256": _root(hydrated["vertex72_geometry"]),
            "plane_roots": tuple(
                (plane["role"], plane["expanded_geometry_sha256"])
                for plane in hydrated["planes"]
            ),
            "three_dimensional_vertex_count": hydrated[
                "three_dimensional_vertex_count"
            ],
            "components_per_vertex": hydrated["components_per_vertex"],
            "full_attached_components": hydrated["full_attached_components"],
            "roundtrip_exact": hydrated["roundtrip_exact"],
        },
        "exceptions": {
            "count": len(exception_tuple),
            "root_sha256": _root(exception_tuple),
        },
        "storage_floor_model": (
            "PIPELINE_BINARY",
            "HASH216_HYDRATION",
            "NOVEL_EXCEPTIONS",
        ),
        "shared_pipeline_amortizable": True,
        "materialized_5184_geometry_is_reconstructible": True,
        "lossless_condition": "COMPRESS(HYDRATE(HASH72))=HASH72",
        "candidate_only": True,
        "generic_unconstrained_payload_compression_claimed": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
        "gpu_canonical_state_authority": False,
        "floating_point_authority": False,
    }
    receipt["receipt_sha256"] = _root(receipt)
    return receipt


def lane5_optimization_witness(depth: int = 1) -> dict[str, Any]:
    """Return the Lane 5 optimization constraints without widening authority."""
    ratio = structural_ratio(depth)
    return {
        "schema": f"{SCHEMA}_LANE5_OPTIMIZATION_V1",
        "fixed_geometry_reused": True,
        "hash72_generator_positions": HASH72_POSITIONS,
        "expanded_vertices": EXPANDED_VERTICES,
        "structural_ratio": (
            ratio["ratio_numerator"],
            ratio["ratio_denominator"],
        ),
        "stream_generator_then_hydrate_on_demand": True,
        "expanded_vertex_materialization_required_for_search": False,
        "roots_may_replace_repeated_materialization_in_candidate_metadata": True,
        "canonical_state_commit_requires_inherited_vm81_path": True,
        "candidate_search_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }


def i065_self_test() -> dict[str, Any]:
    previous = HASH72_ALPHABET
    change = HASH72_ALPHABET[::-1]
    receipt = HASH72_ALPHABET[1:] + HASH72_ALPHABET[:1]
    hash216 = previous + change + receipt
    half = "01" * (EXPANDED_VERTICES // 4)
    binary = half + half[::-1]
    offsets = tuple(index % 9 for index in range(VM81_CELLS))
    serialized = serialize_offsets_5184(offsets)
    cycle = hydrate_cycle(
        hash216=hash216,
        binary5184=binary,
        serialized5184=serialized,
        depth=3,
    )
    return {
        "schema": f"{SCHEMA}_SELF_TEST_V1",
        "ok": (
            cycle["hash216"]["roundtrip_exact"]
            and cycle["pipeline"]["same_5184_geometry"]
            and cycle["ratio"]["ratio_denominator"] == 72**3
            and cycle["generic_unconstrained_payload_compression_claimed"] is False
        ),
        "receipt_sha256": cycle["receipt_sha256"],
        "lane5": lane5_optimization_witness(3),
    }


__all__ = [
    "BASE_MAIN",
    "EXPANDED_VERTICES",
    "FULL_HASH216_COMPONENTS",
    "HASH216_FLAT_POSITIONS",
    "HASH216_PLANES",
    "HASH72_BASE",
    "HASH72_POSITIONS",
    "I065HydrationError",
    "SCHEMA",
    "STRUCTURAL_COMPRESSION",
    "VERSION",
    "bind_binary_serialized_pipeline",
    "compress_hash72_vertex_geometry",
    "hash216_vertex72_geometry",
    "hash72_vertex_geometry",
    "hydrate_cycle",
    "hydrate_hash216_geometry",
    "i065_self_test",
    "lane5_optimization_witness",
    "mirror_geometry_witness",
    "mirror_index",
    "sha256_alphabet72",
    "structural_ratio",
    "validate_binary5184",
    "validate_serialized5184",
]
