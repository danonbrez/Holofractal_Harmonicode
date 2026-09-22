"""Pass 220 I032: G^3 full-phase IEEE transport.

I031 proved exact IEEE scalar-state return.  I032 binds that invariant to the
complete ordered x/y/z/w G^3 tensor so x/y identify the external reciprocal
boundary while all four phase carriers drive the internal nine-slot logic.

The IEEE payload remains immutable throughout the internal phase trace.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from hhs_runtime.hhs_pass220_g3_reciprocal_symbol_codec_v1 import (
    FORWARD_ZERO,
    G3_PROOF_TENSOR,
    PHASE_RECIPROCAL,
    PROOF_CELL_TOKEN,
    RETURN_ZERO,
    reciprocal_phase_expr,
)
from hhs_runtime.hhs_pass220_g3_ieee_scalar_involution_v1 import (
    CARRIER_SCHEMA as IEEE_CARRIER_SCHEMA,
    IEEE_BINARY_FORMATS,
    Pass220IEEEExactError,
    encode_ieee_scalar,
    g3_ieee_scalar_transform,
    validate_ieee_scalar_carrier,
)

SCHEMA = "HHS_PASS_220_I032_G3_FULL_PHASE_IEEE_TRANSPORT_V1"
VERSION = "1.0.0-checkpoint.32"
PROFILE = "PASS220-I032-G3-FULL-PHASE-IEEE-TRANSPORT-v1"
CARRIER_SCHEMA = "HHS_PASS_220_I032_G3_FULL_PHASE_IEEE_CARRIER_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I032_G3_FULL_PHASE_IEEE_WITNESS_V1"

PHASES = ("x", "y", "z", "w")
ORDERED_CHANNELS = (("x", "y"), ("y", "x"), ("z", "w"), ("w", "z"))
RECIPROCAL_RULES = ("y=1/x", "x=1/y", "w=1/z", "z=1/w")


class Pass220FullPhaseTransportError(ValueError):
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


def _receipt_matches(carrier: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in carrier:
        return False
    body = dict(carrier)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, tuple):
        for item in value:
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)


def phase_names_in_tensor(tensor: Any = G3_PROOF_TENSOR) -> Tuple[str, ...]:
    found = []
    for node in _walk(tensor):
        if (
            isinstance(node, tuple)
            and len(node) == 2
            and node[0] == "phase"
            and node[1] in PHASES
            and node[1] not in found
        ):
            found.append(node[1])
    return tuple(found)


def ordered_channels_in_tensor(
    tensor: Any = G3_PROOF_TENSOR,
) -> Tuple[Tuple[str, str], ...]:
    found = []
    for node in _walk(tensor):
        if not (isinstance(node, tuple) and len(node) >= 3 and node[0] == "oprod"):
            continue
        left, right = node[1], node[2]
        if (
            isinstance(left, tuple)
            and len(left) == 2
            and left[0] == "phase"
            and isinstance(right, tuple)
            and len(right) == 2
            and right[0] == "phase"
        ):
            pair = (left[1], right[1])
            if pair not in found:
                found.append(pair)
    return tuple(found)


def _flatten_g3(tensor: Any = G3_PROOF_TENSOR) -> Tuple[Any, ...]:
    if not (
        isinstance(tensor, tuple)
        and len(tensor) == 3
        and all(isinstance(row, tuple) and len(row) == 3 for row in tensor)
    ):
        raise Pass220FullPhaseTransportError("G3 tensor must be exactly 3x3")
    return tuple(cell for row in tensor for cell in row)


def build_full_phase_trace(raw_hex: str) -> Tuple[Dict[str, Any], ...]:
    if not isinstance(raw_hex, str):
        raise Pass220FullPhaseTransportError("raw hex must be a string")
    cells = _flatten_g3()
    trace = []
    for index, forward_expr in enumerate(cells):
        row, column = divmod(index, 3)
        trace.append({
            "slot": index,
            "row": row,
            "column": column,
            "scalar_bits_hex": raw_hex,
            "forward_expr": forward_expr,
            "return_expr": reciprocal_phase_expr(forward_expr),
            "scalar_immutable": True,
        })
    return tuple(trace)


def _validate_full_phase_trace(
    trace: Any,
    raw_hex: str,
) -> Tuple[Dict[str, Any], ...]:
    if not isinstance(trace, (tuple, list)) or len(trace) != 9:
        raise Pass220FullPhaseTransportError("full phase trace must have 9 cells")
    expected = build_full_phase_trace(raw_hex)
    for index, (actual, wanted) in enumerate(zip(trace, expected)):
        if not isinstance(actual, Mapping):
            raise Pass220FullPhaseTransportError(
                f"phase trace slot {index} must be a mapping"
            )
        if dict(actual) != wanted:
            raise Pass220FullPhaseTransportError(
                f"phase trace slot {index} mismatch"
            )
        if actual["scalar_bits_hex"] != raw_hex:
            raise Pass220FullPhaseTransportError(
                f"scalar changed at phase trace slot {index}"
            )
        if reciprocal_phase_expr(actual["forward_expr"]) != actual["return_expr"]:
            raise Pass220FullPhaseTransportError(
                f"reciprocal phase mismatch at slot {index}"
            )
    return tuple(dict(item) for item in trace)


def encode_full_phase_ieee(
    raw: bytes,
    format_name: str,
    *,
    byteorder: str = "big",
) -> Dict[str, Any]:
    try:
        scalar_carrier = encode_ieee_scalar(
            raw,
            format_name,
            byteorder=byteorder,
        )
    except Pass220IEEEExactError as exc:
        raise Pass220FullPhaseTransportError(str(exc)) from exc

    raw_hex = scalar_carrier["raw_hex"]
    forward_tensor = G3_PROOF_TENSOR
    return_tensor = reciprocal_phase_expr(forward_tensor)
    trace = build_full_phase_trace(raw_hex)

    return _receipt({
        "schema": CARRIER_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "scalar_carrier_schema": IEEE_CARRIER_SCHEMA,
        "scalar_carrier": scalar_carrier,
        "boundary_ingress_phase": "x",
        "boundary_egress_phase": "y",
        "boundary_reciprocal_rule": "y=1/x",
        "internal_phase_carriers": PHASES,
        "internal_reciprocal_rules": RECIPROCAL_RULES,
        "ordered_channels": ORDERED_CHANNELS,
        "forward_tensor": forward_tensor,
        "return_tensor": return_tensor,
        "internal_logic_trace": trace,
        "proof_cell": PROOF_CELL_TOKEN,
        "forward_zero": FORWARD_ZERO,
        "return_zero": RETURN_ZERO,
        "scalar_bits_hex": raw_hex,
        "scalar_immutable_through_internal_logic": True,
        "full_phase_tensor_drives_internal_logic": True,
        "same_operation_both_directions": True,
        "host_float_arithmetic_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "floating_point_authority": False,
    })


def validate_full_phase_ieee_carrier(
    carrier: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(carrier, Mapping):
        raise Pass220FullPhaseTransportError("carrier must be a mapping")
    if carrier.get("schema") != CARRIER_SCHEMA:
        raise Pass220FullPhaseTransportError("carrier schema mismatch")
    if not _receipt_matches(carrier):
        raise Pass220FullPhaseTransportError("carrier receipt mismatch")
    if carrier.get("scalar_carrier_schema") != IEEE_CARRIER_SCHEMA:
        raise Pass220FullPhaseTransportError("nested IEEE carrier schema mismatch")

    scalar_carrier = carrier.get("scalar_carrier")
    if not isinstance(scalar_carrier, Mapping):
        raise Pass220FullPhaseTransportError("missing nested IEEE scalar carrier")
    try:
        scalar_result = validate_ieee_scalar_carrier(scalar_carrier)
    except Pass220IEEEExactError as exc:
        raise Pass220FullPhaseTransportError(str(exc)) from exc

    raw = scalar_result["raw"]
    raw_hex = raw.hex()
    if carrier.get("scalar_bits_hex") != raw_hex:
        raise Pass220FullPhaseTransportError("top-level scalar bits mismatch")

    if carrier.get("boundary_ingress_phase") != "x":
        raise Pass220FullPhaseTransportError("ingress boundary must be x")
    if carrier.get("boundary_egress_phase") != "y":
        raise Pass220FullPhaseTransportError("egress boundary must be y")
    if carrier.get("boundary_reciprocal_rule") != "y=1/x":
        raise Pass220FullPhaseTransportError("boundary reciprocal rule mismatch")

    if tuple(carrier.get("internal_phase_carriers", ())) != PHASES:
        raise Pass220FullPhaseTransportError("full x/y/z/w phase set missing")
    if tuple(tuple(item) for item in carrier.get("ordered_channels", ())) != ORDERED_CHANNELS:
        raise Pass220FullPhaseTransportError("ordered phase channels mismatch")

    forward_tensor = carrier.get("forward_tensor")
    return_tensor = carrier.get("return_tensor")
    if forward_tensor != G3_PROOF_TENSOR:
        raise Pass220FullPhaseTransportError("forward G3 tensor mismatch")
    if return_tensor != reciprocal_phase_expr(G3_PROOF_TENSOR):
        raise Pass220FullPhaseTransportError("return G3 tensor mismatch")
    if reciprocal_phase_expr(return_tensor) != G3_PROOF_TENSOR:
        raise Pass220FullPhaseTransportError("G3 reciprocal involution failed")

    names = phase_names_in_tensor(forward_tensor)
    if set(names) != set(PHASES):
        raise Pass220FullPhaseTransportError("not all four phases drive internal tensor")
    channels = ordered_channels_in_tensor(forward_tensor)
    if not all(channel in channels for channel in ORDERED_CHANNELS):
        raise Pass220FullPhaseTransportError("ordered phase channel coverage incomplete")

    trace = _validate_full_phase_trace(
        carrier.get("internal_logic_trace"),
        raw_hex,
    )

    if carrier.get("proof_cell") != PROOF_CELL_TOKEN:
        raise Pass220FullPhaseTransportError("proof cell mismatch")
    if carrier.get("forward_zero") != FORWARD_ZERO:
        raise Pass220FullPhaseTransportError("forward zero lock mismatch")
    if carrier.get("return_zero") != RETURN_ZERO:
        raise Pass220FullPhaseTransportError("return zero lock mismatch")
    if reciprocal_phase_expr(FORWARD_ZERO) != RETURN_ZERO:
        raise Pass220FullPhaseTransportError("zero phase reciprocity mismatch")

    for flag in (
        "scalar_immutable_through_internal_logic",
        "full_phase_tensor_drives_internal_logic",
        "same_operation_both_directions",
    ):
        if carrier.get(flag) is not True:
            raise Pass220FullPhaseTransportError(f"{flag} must be true")
    if carrier.get("host_float_arithmetic_used") is not False:
        raise Pass220FullPhaseTransportError("host floating arithmetic forbidden")

    return {
        "ok": True,
        "raw": raw,
        "format": scalar_result["format"],
        "classification": scalar_result["classification"],
        "bit_identity": scalar_result["bit_identity"],
        "phase_scalar_invariant": scalar_result["phase_scalar_invariant"],
        "phase_names": names,
        "ordered_channels": channels,
        "logic_slots": len(trace),
        "full_phase_tensor_reciprocal_involution": (
            reciprocal_phase_expr(reciprocal_phase_expr(G3_PROOF_TENSOR))
            == G3_PROOF_TENSOR
        ),
        "all_logic_slots_scalar_immutable": all(
            item["scalar_bits_hex"] == raw_hex and item["scalar_immutable"]
            for item in trace
        ),
    }


FullPhaseValue = Any


def g3_full_phase_ieee_transform(
    value: FullPhaseValue,
    format_name: Optional[str] = None,
    *,
    byteorder: str = "big",
) -> Any:
    """One operation for exact IEEE ingress and reciprocal full-phase return."""
    if isinstance(value, (bytes, bytearray)):
        if format_name is None:
            raise Pass220FullPhaseTransportError(
                "format name required for raw IEEE ingress"
            )
        return encode_full_phase_ieee(
            bytes(value),
            format_name,
            byteorder=byteorder,
        )
    if isinstance(value, Mapping):
        if format_name is not None:
            raise Pass220FullPhaseTransportError(
                "format name is carried by encoded state"
            )
        return validate_full_phase_ieee_carrier(value)["raw"]
    raise Pass220FullPhaseTransportError(
        "transform accepts raw IEEE bytes or a full-phase carrier"
    )


def _edge_patterns(format_name: str) -> Tuple[int, ...]:
    spec = IEEE_BINARY_FORMATS[format_name]
    emax = (1 << spec.exponent_bits) - 1
    fmask = (1 << spec.fraction_bits) - 1
    sign = 1 << (spec.total_bits - 1)
    return (
        0,
        sign,
        1,
        fmask,
        1 << spec.fraction_bits,
        ((emax - 1) << spec.fraction_bits) | fmask,
        emax << spec.fraction_bits,
        sign | (emax << spec.fraction_bits),
        (emax << spec.fraction_bits) | 1,
        (emax << spec.fraction_bits) | (1 << max(spec.fraction_bits - 1, 0)) | 1,
        (1 << spec.total_bits) - 1,
    )


def full_phase_ieee_witness() -> Dict[str, Any]:
    format_results: Dict[str, Any] = {}
    for name, spec in IEEE_BINARY_FORMATS.items():
        patterns = _edge_patterns(name)
        passed = True
        for bits in patterns:
            raw = bits.to_bytes(spec.byte_width, "big")
            carrier = g3_full_phase_ieee_transform(raw, name)
            returned = g3_full_phase_ieee_transform(carrier)
            if returned != raw:
                passed = False
                break
            validation = validate_full_phase_ieee_carrier(carrier)
            if (
                validation["logic_slots"] != 9
                or not validation["all_logic_slots_scalar_immutable"]
                or set(validation["phase_names"]) != set(PHASES)
            ):
                passed = False
                break
        format_results[name] = {
            "edge_patterns": len(patterns),
            "all_round_trips": passed,
        }

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "proof_cell": PROOF_CELL_TOKEN,
        "phases": PHASES,
        "ordered_channels": ORDERED_CHANNELS,
        "reciprocal_rules": RECIPROCAL_RULES,
        "g3_dimensions": (3, 3),
        "logic_slots": 9,
        "phase_names_in_g3": phase_names_in_tensor(),
        "ordered_channels_in_g3": ordered_channels_in_tensor(),
        "g3_reciprocal_involution": (
            reciprocal_phase_expr(reciprocal_phase_expr(G3_PROOF_TENSOR))
            == G3_PROOF_TENSOR
        ),
        "format_results": format_results,
        "all_formats_round_trip": all(
            item["all_round_trips"] for item in format_results.values()
        ),
        "x_is_ingress_boundary": True,
        "y_is_egress_boundary": True,
        "full_xyzw_drives_internal_logic": True,
        "scalar_bits_are_invariant": True,
        "host_float_arithmetic_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def validate_full_phase_ieee_transport() -> Dict[str, Any]:
    witness = full_phase_ieee_witness()
    ok = all((
        set(witness["phase_names_in_g3"]) == set(PHASES),
        all(channel in witness["ordered_channels_in_g3"] for channel in ORDERED_CHANNELS),
        witness["g3_reciprocal_involution"],
        witness["all_formats_round_trip"],
        witness["x_is_ingress_boundary"],
        witness["y_is_egress_boundary"],
        witness["full_xyzw_drives_internal_logic"],
        witness["scalar_bits_are_invariant"],
        witness["host_float_arithmetic_used"] is False,
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
        "mutation_policy": "READ_ONLY_FULL_PHASE_IEEE_PROOF_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def full_phase_ieee_transport_self_test() -> Dict[str, Any]:
    return validate_full_phase_ieee_transport()
