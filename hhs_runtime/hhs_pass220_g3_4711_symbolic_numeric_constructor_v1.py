"""Pass 220 I033: G^3 4/7/11 multirepresentational solver constructor.

This cycle composes already-validated Pass 220 surfaces into one candidate-only
constructor.  It preserves symbolic text, exact IEEE storage state, exact
dyadic projection, full ordered x/y/z/w G^3 phase state, fixed-width 5,184
BigInt normalization serialization, scalar BigInt projection, and reciprocal
return provenance as co-resident views.

The constructor contains local constraints.  It does not create or enforce
canonical HARMONICODE constraints and owns no VM81, Hash72, or Hash216
canonical authority. Repository OS hydration may cache/compile a validated
constructor after the normal pull-request data-flow pipeline accepts it.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_g3_reciprocal_symbol_codec_v1 import (
    PROOF_CELL_TOKEN,
    Pass220G3ReciprocalCodecError,
    encode_symbol_string,
    g3_reciprocal_transform,
    validate_symbol_carrier,
)
from hhs_runtime.hhs_pass220_g3_full_phase_ieee_transport_v1 import (
    Pass220FullPhaseTransportError,
    encode_full_phase_ieee,
    g3_full_phase_ieee_transform,
    validate_full_phase_ieee_carrier,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    VM81_CELLS,
    Pass220NormalizationError,
    bigint_to_offsets,
    deserialize_offsets_5184,
    offsets_to_bigint,
    serialize_offsets_5184,
)

SCHEMA = "HHS_PASS_220_I033_G3_4711_SYMBOLIC_NUMERIC_SOLVER_CONSTRUCTOR_V1"
VERSION = "1.0.0-checkpoint.33"
PROFILE = "PASS220-I033-G3-4711-SYMBOLIC-NUMERIC-SOLVER-CONSTRUCTOR-v1"
CONSTRUCTOR_SCHEMA = "HHS_PASS_220_I033_G3_4711_MULTI_VIEW_CONSTRUCTOR_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I033_G3_4711_MULTI_VIEW_WITNESS_V1"

G3_BASE_SCALE: Tuple[int, int, int] = (1, 2, 3)
G3_LIFTED_SCALE: Tuple[int, int, int] = (4, 7, 11)

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "G3_BASE_U_PLUS_V_EQUALS_W",
    "G3_4711_U_PLUS_V_EQUALS_W",
    "G3_4711_NOT_UNIFORM_SCALAR_MULTIPLICATION",
    "SYMBOL_TEXT_RECIPROCAL_RETURN_EXACT",
    "IEEE_STORAGE_BITS_RECIPROCAL_RETURN_EXACT",
    "FULL_XYZW_ORDERED_PHASE_STATE_RETAINED",
    "BIGINT_5184_SERIALIZATION_ROUNDTRIP_EXACT",
    "SCALAR_BIGINT_PROJECTION_ROUNDTRIP_EXACT",
    "DISTINCT_INFORMATION_VIEWS_CO_RESIDENT",
)

REPRESENTATION_VIEW_NAMES: Tuple[str, ...] = (
    "source_symbol_state",
    "ieee_storage_state",
    "exact_dyadic_projection",
    "full_g3_phase_tensor",
    "bigint_5184",
    "scalar_bigint_projection",
    "ordered_reciprocal_provenance",
)


class Pass220I033ConstructorError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


def _receipt_matches(record: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in record:
        return False
    body = dict(record)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def g3_4711_scaling_witness() -> Dict[str, Any]:
    base = G3_BASE_SCALE
    lifted = G3_LIFTED_SCALE
    base_closure = base[0] + base[1] == base[2]
    lifted_closure = lifted[0] + lifted[1] == lifted[2]
    uniform_scalar_multiplier = all(
        lifted[0] * base[index] == lifted[index] * base[0]
        for index in range(1, len(base))
    )
    return _receipt({
        "schema": "HHS_PASS_220_I033_G3_4711_SCALING_WITNESS_V1",
        "base_scale": base,
        "lifted_scale": lifted,
        "base_relation": "u+v=w",
        "lifted_relation": "u+v=w",
        "base_closure": base_closure,
        "lifted_closure": lifted_closure,
        "same_relation_preserved": base_closure and lifted_closure,
        "uniform_scalar_multiplier": uniform_scalar_multiplier,
        "scaling_law_retained_as_constructor_relation": True,
        "scalar_reduction_used": False,
    })


def build_solver_constructor(
    source_text: str,
    raw_ieee: bytes,
    format_name: str,
    offsets: Sequence[int],
    *,
    byteorder: str = "big",
) -> Dict[str, Any]:
    """Build one lossless co-resident solver constructor.

    No representation replaces another.  The source text, IEEE state, exact
    dyadic projection, phase tensor, fixed-width BigInt object, scalar BigInt
    projection, and reciprocal provenance are retained together.
    """
    try:
        symbol_carrier = encode_symbol_string(source_text)
        ieee_carrier = encode_full_phase_ieee(
            raw_ieee,
            format_name,
            byteorder=byteorder,
        )
        offset_tuple = tuple(offsets)
        bigint_5184 = serialize_offsets_5184(offset_tuple)
        scalar_bigint = offsets_to_bigint(offset_tuple)
    except (
        Pass220G3ReciprocalCodecError,
        Pass220FullPhaseTransportError,
        Pass220NormalizationError,
        TypeError,
    ) as exc:
        raise Pass220I033ConstructorError(str(exc)) from exc

    if len(offset_tuple) != VM81_CELLS:
        raise Pass220I033ConstructorError("constructor requires exactly 81 offsets")

    scalar_carrier = ieee_carrier["scalar_carrier"]
    scaling = g3_4711_scaling_witness()

    representation_views = {
        "source_symbol_state": symbol_carrier,
        "ieee_storage_state": ieee_carrier,
        "exact_dyadic_projection": scalar_carrier["exact_dyadic"],
        "full_g3_phase_tensor": ieee_carrier["forward_tensor"],
        "bigint_5184": bigint_5184,
        "scalar_bigint_projection": scalar_bigint,
        "ordered_reciprocal_provenance": {
            "proof_cell": PROOF_CELL_TOKEN,
            "symbol_ingress_phase": symbol_carrier["ingress_phase"],
            "symbol_return_phase": symbol_carrier["return_phase"],
            "ieee_ingress_phase": ieee_carrier["boundary_ingress_phase"],
            "ieee_return_phase": ieee_carrier["boundary_egress_phase"],
            "reciprocal_rule": "y=1/x",
        },
    }

    return _receipt({
        "schema": CONSTRUCTOR_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "constructor_kind": "VALIDATED_OPERATION_CONSTRUCTOR",
        "contains_constraints": True,
        "local_constraints": LOCAL_CONSTRAINTS,
        "constraint_authority": "CONSTRUCTOR_LOCAL_ONLY",
        "canonical_service": False,
        "canonical_constraint_creation_authority": False,
        "canonical_constraint_enforcement_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "direct_canonical_persistence_authority": False,
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
        "g3_scaling": scaling,
        "representation_views": representation_views,
        "representation_view_names": REPRESENTATION_VIEW_NAMES,
        "co_resident_representation_count": len(REPRESENTATION_VIEW_NAMES),
        "reduction_policy": "NO_DISTINCT_INFORMATION_VIEW_DISCARDED",
        "symbolic_logic_view_present": True,
        "ieee_floating_state_view_present": True,
        "exact_numeric_view_present": True,
        "bigint_view_present": True,
        "phase_geometric_view_present": True,
        "palindromic_reciprocal_view_present": True,
        "host_float_arithmetic_used_by_constructor": False,
    })


def validate_solver_constructor(
    constructor: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(constructor, Mapping):
        raise Pass220I033ConstructorError("constructor must be a mapping")
    if constructor.get("schema") != CONSTRUCTOR_SCHEMA:
        raise Pass220I033ConstructorError("constructor schema mismatch")
    if not _receipt_matches(constructor):
        raise Pass220I033ConstructorError("constructor receipt mismatch")

    scaling = constructor.get("g3_scaling")
    expected_scaling = g3_4711_scaling_witness()
    if scaling != expected_scaling:
        raise Pass220I033ConstructorError("G3 4/7/11 scaling witness mismatch")
    if not (
        scaling["base_closure"]
        and scaling["lifted_closure"]
        and scaling["same_relation_preserved"]
        and scaling["uniform_scalar_multiplier"] is False
    ):
        raise Pass220I033ConstructorError("G3 4/7/11 scaling relation failed")

    views = constructor.get("representation_views")
    if not isinstance(views, Mapping):
        raise Pass220I033ConstructorError("representation views missing")
    if tuple(constructor.get("representation_view_names", ())) != REPRESENTATION_VIEW_NAMES:
        raise Pass220I033ConstructorError("representation view registry mismatch")
    if set(views) != set(REPRESENTATION_VIEW_NAMES):
        raise Pass220I033ConstructorError("co-resident representation set mismatch")

    try:
        symbol_result = validate_symbol_carrier(views["source_symbol_state"])
        ieee_result = validate_full_phase_ieee_carrier(views["ieee_storage_state"])
        decoded_offsets = deserialize_offsets_5184(views["bigint_5184"])
        scalar_offsets = bigint_to_offsets(
            views["scalar_bigint_projection"],
            length=VM81_CELLS,
        )
    except (
        Pass220G3ReciprocalCodecError,
        Pass220FullPhaseTransportError,
        Pass220NormalizationError,
    ) as exc:
        raise Pass220I033ConstructorError(str(exc)) from exc

    if decoded_offsets != scalar_offsets:
        raise Pass220I033ConstructorError(
            "5184 serialization and scalar BigInt projections disagree"
        )
    if g3_reciprocal_transform(views["source_symbol_state"]) != symbol_result["text"]:
        raise Pass220I033ConstructorError("symbol reciprocal return mismatch")
    if g3_full_phase_ieee_transform(views["ieee_storage_state"]) != ieee_result["raw"]:
        raise Pass220I033ConstructorError("IEEE reciprocal return mismatch")

    scalar_carrier = views["ieee_storage_state"]["scalar_carrier"]
    if views["exact_dyadic_projection"] != scalar_carrier["exact_dyadic"]:
        raise Pass220I033ConstructorError("exact dyadic co-resident view mismatch")
    if views["full_g3_phase_tensor"] != views["ieee_storage_state"]["forward_tensor"]:
        raise Pass220I033ConstructorError("G3 phase tensor co-resident view mismatch")

    if tuple(constructor.get("local_constraints", ())) != LOCAL_CONSTRAINTS:
        raise Pass220I033ConstructorError("local constructor constraints changed")
    if constructor.get("contains_constraints") is not True:
        raise Pass220I033ConstructorError("constructor constraints must be retained")
    for field in (
        "canonical_service",
        "canonical_constraint_creation_authority",
        "canonical_constraint_enforcement_authority",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "direct_canonical_persistence_authority",
    ):
        if constructor.get(field) is not False:
            raise Pass220I033ConstructorError(f"authority escalation: {field}")

    if constructor.get("reduction_policy") != "NO_DISTINCT_INFORMATION_VIEW_DISCARDED":
        raise Pass220I033ConstructorError("reduction policy mismatch")
    if constructor.get("co_resident_representation_count") != len(REPRESENTATION_VIEW_NAMES):
        raise Pass220I033ConstructorError("co-resident representation count mismatch")

    return {
        "ok": True,
        "source_text": symbol_result["text"],
        "raw_ieee": ieee_result["raw"],
        "format": ieee_result["format"],
        "classification": ieee_result["classification"],
        "exact_dyadic": ieee_result["exact_dyadic"],
        "offsets": decoded_offsets,
        "bigint_5184_roundtrip": True,
        "scalar_bigint_roundtrip": True,
        "symbol_reciprocal_roundtrip": True,
        "ieee_reciprocal_roundtrip": True,
        "g3_4711_relation_preserved": True,
        "co_resident_views_preserved": True,
    }


def recover_solver_constructor(
    constructor: Mapping[str, Any],
) -> Dict[str, Any]:
    result = validate_solver_constructor(constructor)
    return {
        "source_text": result["source_text"],
        "raw_ieee": result["raw_ieee"],
        "format": result["format"],
        "exact_dyadic": result["exact_dyadic"],
        "offsets": result["offsets"],
    }


def g3_4711_symbolic_numeric_constructor_witness() -> Dict[str, Any]:
    source = "A/B*B/A == P^4 == c^4 == TRUE"
    raw = bytes.fromhex("3fb999999999999a")
    offsets = tuple((index * 7 + 3) % 9 for index in range(VM81_CELLS))
    constructor = build_solver_constructor(
        source,
        raw,
        "binary64",
        offsets,
    )
    result = validate_solver_constructor(constructor)
    recovered = recover_solver_constructor(constructor)

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "proof_cell": PROOF_CELL_TOKEN,
        "g3_scaling": constructor["g3_scaling"],
        "constructor_receipt_sha256": constructor["receipt_sha256"],
        "representation_view_names": REPRESENTATION_VIEW_NAMES,
        "co_resident_representation_count": len(REPRESENTATION_VIEW_NAMES),
        "source_roundtrip_exact": recovered["source_text"] == source,
        "ieee_roundtrip_exact": recovered["raw_ieee"] == raw,
        "offset_roundtrip_exact": recovered["offsets"] == offsets,
        "exact_dyadic_retained": result["exact_dyadic"]
        == constructor["representation_views"]["exact_dyadic_projection"],
        "g3_4711_relation_preserved": result["g3_4711_relation_preserved"],
        "constructor_contains_constraints": True,
        "constructor_has_constraint_authority": False,
        "repository_os_hydration_is_downstream": True,
    })


def validate_g3_4711_symbolic_numeric_constructor() -> Dict[str, Any]:
    witness = g3_4711_symbolic_numeric_constructor_witness()
    scaling = witness["g3_scaling"]
    ok = all((
        scaling["base_scale"] == G3_BASE_SCALE,
        scaling["lifted_scale"] == G3_LIFTED_SCALE,
        scaling["base_closure"],
        scaling["lifted_closure"],
        scaling["same_relation_preserved"],
        scaling["uniform_scalar_multiplier"] is False,
        witness["source_roundtrip_exact"],
        witness["ieee_roundtrip_exact"],
        witness["offset_roundtrip_exact"],
        witness["exact_dyadic_retained"],
        witness["g3_4711_relation_preserved"],
        witness["constructor_contains_constraints"],
        witness["constructor_has_constraint_authority"] is False,
        witness["repository_os_hydration_is_downstream"],
    ))
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": ok,
        "witness": witness,
        "invariant_ids": (
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ),
        "mutation_policy": "READ_ONLY_VALIDATED_CONSTRUCTOR_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
        "canonical_service": False,
        "canonical_constraint_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def g3_4711_symbolic_numeric_constructor_self_test() -> Dict[str, Any]:
    return validate_g3_4711_symbolic_numeric_constructor()
