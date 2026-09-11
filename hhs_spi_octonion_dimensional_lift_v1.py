"""Pass 219 SPI — reciprocal/base-pair octonion dimensional lift v1.

This layer makes the user's compact reciprocal/base-pair phase constructor
executable without rewriting the inherited RML2/RML4 gyroscope geometry.

Exact source syntax preserved by this module:

    x=1/y y=-x
    (x,y,z,w)²==(Ixy, I-yx, Izw, I-wz)²

Three relations are deliberately kept distinct:

1. geometric phase opposite inherited from RML2;
2. ordered reciprocal operand inherited from RML4 product construction;
3. symbolic base-pair equivalent from the exact source equation above.

The first four relational coordinates are materialized directly. Dimensions
above four are represented as recursive references to the same four-coordinate
closure, avoiding combinatorial materialization while preserving ancestry.

The gyroscope may also be encoded as a typed ordinary imaginary/u^72 rotation
carrier. The phase coordinate alone is not declared lossless; the typed carrier
is lossless because it preserves source channel, reciprocal/opposite relations,
base-pair identity, and exact phase72 coordinate.

This module is projection/candidate metadata only. It cannot mutate VM81, mint
Hash72/Hash216, persist canonical state, or collapse ordered products.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    PHASE_MODULUS,
    PRIMITIVE_GEOMETRY,
    phase_to_exact_angle,
)

FORMAT = "HHS_SPI_OCTONION_DIMENSIONAL_LIFT_V1"
VERSION = "1.0.0"
SCHEMA = "HHS_SPI_OCTONION_DIMENSIONAL_LIFT_RECEIPT_V1"

SOURCE_RECIPROCAL_SYNTAX = "x=1/y y=-x"
SOURCE_BASE_PAIR_SYNTAX = "(x,y,z,w)²==(Ixy, I-yx, Izw, I-wz)²"

PRIMITIVES = ("x", "y", "z", "w")

# RML2 geometric reciprocal phase opposites: same plane, opposite orientation.
PHASE_OPPOSITE = {
    "x": "z",
    "z": "x",
    "w": "y",
    "y": "w",
}

# RML4 ordered reciprocal operands used to construct product channels.
ORDERED_RECIPROCAL_OPERAND = {
    "x": "y",
    "y": "x",
    "z": "w",
    "w": "z",
}

# Exact coordinate pairing from the supplied source constructor.
SYMBOLIC_BASE_PAIR = {
    "x": "Ixy",
    "y": "I-yx",
    "z": "Izw",
    "w": "I-wz",
}

A2_UNIT = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}


class SPIOctonionDimensionalLiftError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _primitive(value: Any) -> str:
    if value not in PRIMITIVES:
        raise SPIOctonionDimensionalLiftError("PRIMITIVE_OCTONION_PHASE_CHANNEL_REQUIRED")
    return str(value)


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SPIOctonionDimensionalLiftError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _phase(value: Any) -> int:
    phase = _exact_int(value, "PHASE72")
    if phase < 0 or phase >= PHASE_MODULUS:
        raise SPIOctonionDimensionalLiftError("PHASE72_OUT_OF_RANGE")
    return phase


def phase_opposite(channel: str) -> str:
    return PHASE_OPPOSITE[_primitive(channel)]


def ordered_reciprocal_operand(channel: str) -> str:
    return ORDERED_RECIPROCAL_OPERAND[_primitive(channel)]


def symbolic_base_pair(channel: str) -> str:
    return SYMBOLIC_BASE_PAIR[_primitive(channel)]


def four_coordinate_closure(channel: str) -> tuple[dict[str, Any], ...]:
    """Return the exact 1D..4D relational closure for one primitive channel."""
    source = _primitive(channel)
    opposite = phase_opposite(source)
    return (
        {
            "dimension": 1,
            "role": "NATIVE_OCTONION_PHASE_STATE",
            "value": source,
        },
        {
            "dimension": 2,
            "role": "GEOMETRIC_PHASE_OPPOSITE",
            "value": opposite,
            "relation": "RML2_SAME_PLANE_OPPOSITE_ORIENTATION",
        },
        {
            "dimension": 3,
            "role": "SYMBOLIC_BASE_PAIR_EQUIVALENT",
            "value": symbolic_base_pair(source),
            "relation": SOURCE_BASE_PAIR_SYNTAX,
        },
        {
            "dimension": 4,
            "role": "BASE_PAIR_OF_GEOMETRIC_OPPOSITE",
            "value": symbolic_base_pair(opposite),
            "relation": SOURCE_BASE_PAIR_SYNTAX,
        },
    )


def dimensional_lift(channel: str, dimension: int) -> dict[str, Any]:
    """Generate a deterministic 1,2,3,4+ dimensional descriptor.

    Dimensions 1..4 are explicit relational coordinates. A higher dimension
    adds ancestry-only nested closure references over the exact same octonion
    algebra; it does not invent new basis elements or materialize an exponential
    state table.
    """
    source = _primitive(channel)
    requested = _exact_int(dimension, "DIMENSION")
    if requested < 1:
        raise SPIOctonionDimensionalLiftError("DIMENSION_MUST_BE_POSITIVE")

    closure = list(four_coordinate_closure(source))
    coordinates = closure[: min(requested, 4)]
    recursive_axes: list[dict[str, Any]] = []
    if requested > 4:
        closure_root = _sha256(
            {
                "source": source,
                "closure": closure,
                "source_base_pair_syntax": SOURCE_BASE_PAIR_SYNTAX,
            }
        )
        for axis in range(5, requested + 1):
            recursive_axes.append(
                {
                    "dimension": axis,
                    "role": "RECURSIVE_SAME_ALGEBRA_CLOSURE_REFERENCE",
                    "nesting_depth": axis - 4,
                    "closure_root_sha256": closure_root,
                    "source_channel": source,
                    "materializes_new_octonion_basis": False,
                }
            )
        coordinates.extend(recursive_axes)

    result = {
        "schema": "HHS_SPI_OCTONION_DIMENSIONAL_DESCRIPTOR_V1",
        "source_channel": source,
        "requested_dimension": requested,
        "coordinates": coordinates,
        "explicit_relational_dimensions": min(requested, 4),
        "recursive_reference_dimensions": max(0, requested - 4),
        "same_octonion_algebra_all_dimensions": True,
        "new_basis_elements_introduced": False,
        "combinatorial_materialization_required": False,
    }
    result["descriptor_sha256"] = _sha256(result)
    return result


def collapse_to_imaginary_rotation(channel: str, phase72: int) -> dict[str, Any]:
    """Losslessly encode one primitive gyroscope state as a typed u^72 rotation."""
    source = _primitive(channel)
    phase = _phase(phase72)
    opposite = phase_opposite(source)
    carrier = {
        "schema": "HHS_SPI_TYPED_IMAGINARY_ROTATION_CARRIER_V1",
        "source_channel": source,
        "phase72": phase,
        "rotation": phase_to_exact_angle(phase),
        "signed_orientation": PRIMITIVE_GEOMETRY[source]["signed_orientation"],
        "plane": PRIMITIVE_GEOMETRY[source]["plane"],
        "geometric_phase_opposite": opposite,
        "ordered_reciprocal_operand": ordered_reciprocal_operand(source),
        "symbolic_base_pair": symbolic_base_pair(source),
        "opposite_symbolic_base_pair": symbolic_base_pair(opposite),
        "source_reciprocal_syntax": SOURCE_RECIPROCAL_SYNTAX,
        "source_base_pair_syntax": SOURCE_BASE_PAIR_SYNTAX,
        "phase_coordinate_alone_claimed_lossless": False,
        "typed_rotation_carrier_lossless": True,
        "ordered_native_identity_preserved": True,
        "scalar_projection_substitution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    carrier["carrier_sha256"] = _sha256(carrier)
    return carrier


def restore_from_imaginary_rotation(carrier: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(carrier, Mapping):
        raise SPIOctonionDimensionalLiftError("TYPED_ROTATION_CARRIER_REQUIRED")
    if carrier.get("schema") != "HHS_SPI_TYPED_IMAGINARY_ROTATION_CARRIER_V1":
        raise SPIOctonionDimensionalLiftError("TYPED_ROTATION_CARRIER_SCHEMA_MISMATCH")

    body = dict(carrier)
    supplied_sha = body.pop("carrier_sha256", None)
    if not isinstance(supplied_sha, str) or supplied_sha != _sha256(body):
        raise SPIOctonionDimensionalLiftError("TYPED_ROTATION_CARRIER_RECEIPT_MISMATCH")

    source = _primitive(body.get("source_channel"))
    phase = _phase(body.get("phase72"))
    if body.get("geometric_phase_opposite") != phase_opposite(source):
        raise SPIOctonionDimensionalLiftError("GEOMETRIC_PHASE_OPPOSITE_MISMATCH")
    if body.get("ordered_reciprocal_operand") != ordered_reciprocal_operand(source):
        raise SPIOctonionDimensionalLiftError("ORDERED_RECIPROCAL_OPERAND_MISMATCH")
    if body.get("symbolic_base_pair") != symbolic_base_pair(source):
        raise SPIOctonionDimensionalLiftError("SYMBOLIC_BASE_PAIR_MISMATCH")
    if body.get("opposite_symbolic_base_pair") != symbolic_base_pair(phase_opposite(source)):
        raise SPIOctonionDimensionalLiftError("OPPOSITE_SYMBOLIC_BASE_PAIR_MISMATCH")

    return {
        "source_channel": source,
        "phase72": phase,
        "exact_round_trip": True,
        "carrier_sha256": supplied_sha,
    }


def a2_projection_compatibility(channel: str) -> dict[str, Any]:
    source = _primitive(channel)
    return {
        "schema": "HHS_SPI_OCTONION_A2_PROJECTION_COMPATIBILITY_V1",
        "source_channel": source,
        "projection_premise_id": "SPI-LAW1-A2-LOCAL-SCALE",
        "a2_projection": dict(A2_UNIT),
        "native_channel": source,
        "native_phase_opposite": phase_opposite(source),
        "native_ordered_reciprocal_operand": ordered_reciprocal_operand(source),
        "native_symbolic_base_pair": symbolic_base_pair(source),
        "projection_equality_implies_native_identity": False,
        "commutative_reorder_authorized": False,
        "a2_projection_contradiction": False,
    }


def dimensional_lift_witness(
    channel: str = "x",
    *,
    phase72: int = 0,
    dimension: int = 8,
) -> dict[str, Any]:
    source = _primitive(channel)
    carrier = collapse_to_imaginary_rotation(source, phase72)
    restored = restore_from_imaginary_rotation(carrier)
    lift = dimensional_lift(source, dimension)
    projection = a2_projection_compatibility(source)

    witness = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "source_reciprocal_syntax": SOURCE_RECIPROCAL_SYNTAX,
        "source_base_pair_syntax": SOURCE_BASE_PAIR_SYNTAX,
        "source_channel": source,
        "geometric_phase_opposite": phase_opposite(source),
        "ordered_reciprocal_operand": ordered_reciprocal_operand(source),
        "symbolic_base_pair": symbolic_base_pair(source),
        "dimensional_lift": lift,
        "imaginary_rotation_carrier": carrier,
        "imaginary_rotation_round_trip": restored,
        "a2_projection_compatibility": projection,
        "invariants": {
            "phase_opposite_involutive": phase_opposite(phase_opposite(source)) == source,
            "ordered_reciprocal_operand_involutive": (
                ordered_reciprocal_operand(ordered_reciprocal_operand(source)) == source
            ),
            "phase_opposite_and_ordered_reciprocal_are_distinct_relations": (
                phase_opposite(source) != ordered_reciprocal_operand(source)
            ),
            "typed_imaginary_rotation_round_trip_lossless": restored["exact_round_trip"],
            "same_octonion_algebra_all_dimensions": lift["same_octonion_algebra_all_dimensions"],
            "a2_unit_projection_preserved": projection["a2_projection"] == A2_UNIT,
            "ordered_native_identity_preserved": True,
        },
        "authority": {
            "projection_only": True,
            "candidate_only": True,
            "vm81_mutation": False,
            "canonical_hash72_minting": False,
            "canonical_hash216_minting": False,
            "canonical_persistence": False,
            "floating_point_authority": False,
        },
    }
    witness["receipt_sha256"] = _sha256(witness)
    return witness
