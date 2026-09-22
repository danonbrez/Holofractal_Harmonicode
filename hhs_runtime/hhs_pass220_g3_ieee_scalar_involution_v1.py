"""Pass 220 I031: exact IEEE binary scalar reciprocal involution.

This module strengthens I030 from exact source-string round trips to exact IEEE
binary scalar-state round trips.  The authoritative identity is the complete
IEEE storage bit pattern, not a decimal rendering and not host floating-point
arithmetic.

The reciprocal phase operation changes only the x/y (or z/w) phase coordinate.
The IEEE scalar coordinate is immutable.  All field extraction, exact dyadic
decoding, and reconstruction use integers only.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import gcd
from typing import Any, Dict, Mapping, Optional, Tuple

from hhs_runtime.hhs_pass220_g3_reciprocal_symbol_codec_v1 import (
    FORWARD_ZERO,
    PROOF_CELL_TOKEN,
    RETURN_ZERO,
    reciprocal_phase_expr,
)

SCHEMA = "HHS_PASS_220_I031_G3_IEEE_SCALAR_INVOLUTION_V1"
VERSION = "1.0.0-checkpoint.31"
PROFILE = "PASS220-I031-G3-IEEE-SCALAR-INVOLUTION-v1"
CARRIER_SCHEMA = "HHS_PASS_220_I031_IEEE_SCALAR_CARRIER_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I031_IEEE_SCALAR_INVOLUTION_WITNESS_V1"


class Pass220IEEEExactError(ValueError):
    pass


@dataclass(frozen=True)
class IEEEBinaryFormat:
    name: str
    total_bits: int
    exponent_bits: int
    fraction_bits: int
    bias: int

    @property
    def exponent_max(self) -> int:
        return (1 << self.exponent_bits) - 1

    @property
    def byte_width(self) -> int:
        return self.total_bits // 8


IEEE_BINARY_FORMATS: Dict[str, IEEEBinaryFormat] = {
    "binary16": IEEEBinaryFormat("binary16", 16, 5, 10, 15),
    "binary32": IEEEBinaryFormat("binary32", 32, 8, 23, 127),
    "binary64": IEEEBinaryFormat("binary64", 64, 11, 52, 1023),
    "binary128": IEEEBinaryFormat("binary128", 128, 15, 112, 16383),
}


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


def _format(name: str) -> IEEEBinaryFormat:
    try:
        return IEEE_BINARY_FORMATS[name]
    except KeyError as exc:
        raise Pass220IEEEExactError(f"unsupported IEEE binary format: {name}") from exc


def _validate_byteorder(byteorder: str) -> None:
    if byteorder not in {"big", "little"}:
        raise Pass220IEEEExactError("byteorder must be 'big' or 'little'")


def raw_to_bits(raw: bytes, format_name: str, *, byteorder: str = "big") -> int:
    spec = _format(format_name)
    _validate_byteorder(byteorder)
    if not isinstance(raw, (bytes, bytearray)):
        raise Pass220IEEEExactError("raw IEEE storage must be bytes")
    raw = bytes(raw)
    if len(raw) != spec.byte_width:
        raise Pass220IEEEExactError(
            f"{format_name} requires exactly {spec.byte_width} bytes"
        )
    return int.from_bytes(raw, byteorder=byteorder, signed=False)


def bits_to_raw(bits: int, format_name: str, *, byteorder: str = "big") -> bytes:
    spec = _format(format_name)
    _validate_byteorder(byteorder)
    if isinstance(bits, bool) or not isinstance(bits, int):
        raise Pass220IEEEExactError("bits must be an integer")
    if not 0 <= bits < (1 << spec.total_bits):
        raise Pass220IEEEExactError("bit pattern outside format width")
    return bits.to_bytes(spec.byte_width, byteorder=byteorder, signed=False)


def split_fields(bits: int, format_name: str) -> Dict[str, int]:
    spec = _format(format_name)
    if isinstance(bits, bool) or not isinstance(bits, int):
        raise Pass220IEEEExactError("bits must be an integer")
    if not 0 <= bits < (1 << spec.total_bits):
        raise Pass220IEEEExactError("bit pattern outside format width")

    sign_shift = spec.exponent_bits + spec.fraction_bits
    sign = bits >> sign_shift
    exponent_mask = (1 << spec.exponent_bits) - 1
    fraction_mask = (1 << spec.fraction_bits) - 1
    exponent = (bits >> spec.fraction_bits) & exponent_mask
    fraction = bits & fraction_mask
    return {
        "sign": sign,
        "exponent": exponent,
        "fraction": fraction,
    }


def rebuild_bits(
    format_name: str,
    *,
    sign: int,
    exponent: int,
    fraction: int,
) -> int:
    spec = _format(format_name)
    if sign not in (0, 1):
        raise Pass220IEEEExactError("sign bit must be 0 or 1")
    if not 0 <= exponent <= spec.exponent_max:
        raise Pass220IEEEExactError("exponent field outside range")
    if not 0 <= fraction < (1 << spec.fraction_bits):
        raise Pass220IEEEExactError("fraction field outside range")
    return (
        (sign << (spec.exponent_bits + spec.fraction_bits))
        | (exponent << spec.fraction_bits)
        | fraction
    )


def classify_fields(fields: Mapping[str, int], format_name: str) -> str:
    spec = _format(format_name)
    exponent = int(fields["exponent"])
    fraction = int(fields["fraction"])
    if exponent == 0:
        return "zero" if fraction == 0 else "subnormal"
    if exponent == spec.exponent_max:
        return "infinity" if fraction == 0 else "nan"
    return "normal"


def exact_dyadic(
    fields: Mapping[str, int],
    format_name: str,
) -> Optional[Tuple[int, int]]:
    """Return the exact finite value as a reduced integer rational.

    Signed zero retains its sign in the independent sign field.  NaN and
    infinity have no finite rational projection and return None; their complete
    raw bit patterns remain authoritative carrier state.
    """
    spec = _format(format_name)
    sign_bit = int(fields["sign"])
    exponent_field = int(fields["exponent"])
    fraction = int(fields["fraction"])
    value_class = classify_fields(fields, format_name)
    if value_class in {"nan", "infinity"}:
        return None
    if value_class == "zero":
        return (0, 1)

    sign = -1 if sign_bit else 1
    if exponent_field == 0:
        significand = fraction
        binary_exponent = 1 - spec.bias - spec.fraction_bits
    else:
        significand = (1 << spec.fraction_bits) + fraction
        binary_exponent = exponent_field - spec.bias - spec.fraction_bits

    numerator = sign * significand
    denominator = 1
    if binary_exponent >= 0:
        numerator <<= binary_exponent
    else:
        denominator <<= -binary_exponent

    common = gcd(abs(numerator), denominator)
    return (numerator // common, denominator // common)


def _dyadic_record(
    dyadic: Optional[Tuple[int, int]],
) -> Optional[Dict[str, Any]]:
    """Serialize an exact dyadic without forcing huge powers of two to decimal.

    IEEE binary rationals always have a power-of-two denominator after
    reduction.  binary128 subnormals can require a denominator whose decimal
    spelling exceeds Python's guarded integer-string limit, so the canonical
    record carries the power-of-two exponent.  A direct denominator integer is
    included only when its decimal serialization is safely bounded.
    """
    if dyadic is None:
        return None
    numerator, denominator = dyadic
    if denominator <= 0 or denominator & (denominator - 1):
        raise Pass220IEEEExactError("dyadic denominator is not a power of two")
    denominator_power2 = denominator.bit_length() - 1
    return {
        "numerator": numerator,
        "denominator_power2": denominator_power2,
        "denominator": denominator if denominator_power2 <= 4096 else None,
    }


def _phase_state(raw_hex: str, phase: str) -> Dict[str, Any]:
    return {
        "raw_bits_hex": raw_hex,
        "phase": phase,
        "proof_cell": PROOF_CELL_TOKEN,
    }


def encode_ieee_scalar(
    raw: bytes,
    format_name: str,
    *,
    byteorder: str = "big",
) -> Dict[str, Any]:
    spec = _format(format_name)
    _validate_byteorder(byteorder)
    raw = bytes(raw)
    bits = raw_to_bits(raw, format_name, byteorder=byteorder)
    fields = split_fields(bits, format_name)
    rebuilt = rebuild_bits(format_name, **fields)
    if rebuilt != bits:
        raise Pass220IEEEExactError("field reconstruction failed")
    dyadic = exact_dyadic(fields, format_name)
    raw_hex = raw.hex()

    return _receipt({
        "schema": CARRIER_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "format": spec.name,
        "total_bits": spec.total_bits,
        "exponent_bits": spec.exponent_bits,
        "fraction_bits": spec.fraction_bits,
        "bias": spec.bias,
        "byteorder": byteorder,
        "raw_hex": raw_hex,
        "raw_integer": bits,
        "fields": fields,
        "classification": classify_fields(fields, format_name),
        "exact_dyadic": _dyadic_record(dyadic),
        "field_rebuild_integer": rebuilt,
        "field_rebuild_hex": bits_to_raw(
            rebuilt, format_name, byteorder=byteorder
        ).hex(),
        "forward_state": _phase_state(raw_hex, "x"),
        "return_state": _phase_state(raw_hex, "y"),
        "reciprocal_rule": "y=1/x",
        "phase_scalar_invariant": True,
        "forward_zero": FORWARD_ZERO,
        "return_zero": RETURN_ZERO,
        "proof_cell": PROOF_CELL_TOKEN,
        "host_float_arithmetic_used": False,
        "numeric_decimal_roundtrip_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "floating_point_authority": False,
    })


def _receipt_matches(carrier: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in carrier:
        return False
    body = dict(carrier)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def validate_ieee_scalar_carrier(carrier: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(carrier, Mapping):
        raise Pass220IEEEExactError("carrier must be a mapping")
    if carrier.get("schema") != CARRIER_SCHEMA:
        raise Pass220IEEEExactError("carrier schema mismatch")
    if not _receipt_matches(carrier):
        raise Pass220IEEEExactError("carrier receipt mismatch")

    format_name = str(carrier.get("format"))
    spec = _format(format_name)
    byteorder = str(carrier.get("byteorder"))
    _validate_byteorder(byteorder)
    raw_hex = carrier.get("raw_hex")
    if not isinstance(raw_hex, str):
        raise Pass220IEEEExactError("raw hex missing")
    try:
        raw = bytes.fromhex(raw_hex)
    except ValueError as exc:
        raise Pass220IEEEExactError("raw hex invalid") from exc
    if len(raw) != spec.byte_width:
        raise Pass220IEEEExactError("raw width mismatch")

    bits = raw_to_bits(raw, format_name, byteorder=byteorder)
    fields = split_fields(bits, format_name)
    rebuilt = rebuild_bits(format_name, **fields)
    if carrier.get("raw_integer") != bits:
        raise Pass220IEEEExactError("raw integer mismatch")
    if carrier.get("fields") != fields:
        raise Pass220IEEEExactError("field decomposition mismatch")
    if carrier.get("field_rebuild_integer") != rebuilt or rebuilt != bits:
        raise Pass220IEEEExactError("field reconstruction mismatch")
    if carrier.get("field_rebuild_hex") != raw_hex:
        raise Pass220IEEEExactError("field reconstruction bytes mismatch")
    if carrier.get("classification") != classify_fields(fields, format_name):
        raise Pass220IEEEExactError("classification mismatch")

    dyadic = exact_dyadic(fields, format_name)
    expected_dyadic = _dyadic_record(dyadic)
    if carrier.get("exact_dyadic") != expected_dyadic:
        raise Pass220IEEEExactError("exact dyadic mismatch")

    forward = carrier.get("forward_state")
    return_state = carrier.get("return_state")
    if forward != _phase_state(raw_hex, "x"):
        raise Pass220IEEEExactError("forward scalar/phase state mismatch")
    if return_state != _phase_state(raw_hex, "y"):
        raise Pass220IEEEExactError("return scalar/phase state mismatch")
    if forward["raw_bits_hex"] != return_state["raw_bits_hex"]:
        raise Pass220IEEEExactError("scalar bits changed across reciprocal phase")
    if carrier.get("reciprocal_rule") != "y=1/x":
        raise Pass220IEEEExactError("reciprocal phase rule mismatch")
    if carrier.get("forward_zero") != FORWARD_ZERO:
        raise Pass220IEEEExactError("forward zero lock mismatch")
    if carrier.get("return_zero") != RETURN_ZERO:
        raise Pass220IEEEExactError("return zero lock mismatch")
    if reciprocal_phase_expr(FORWARD_ZERO) != RETURN_ZERO:
        raise Pass220IEEEExactError("inherited phase lock no longer reciprocal")
    if carrier.get("host_float_arithmetic_used") is not False:
        raise Pass220IEEEExactError("host floating arithmetic is forbidden")
    if carrier.get("numeric_decimal_roundtrip_used") is not False:
        raise Pass220IEEEExactError("decimal float roundtrip is forbidden")

    return {
        "ok": True,
        "raw": raw,
        "bits": bits,
        "format": format_name,
        "classification": classify_fields(fields, format_name),
        "exact_dyadic": expected_dyadic,
        "bit_identity": rebuilt == bits,
        "phase_scalar_invariant": (
            forward["raw_bits_hex"] == return_state["raw_bits_hex"]
        ),
    }


def g3_ieee_scalar_transform(
    value: Any,
    format_name: Optional[str] = None,
    *,
    byteorder: str = "big",
) -> Any:
    """One reciprocal operation for IEEE scalar ingress and return.

    bytes -> carrier at x with y=1/x return state
    carrier -> identical original bytes

    Thus T(T(raw)) == raw for every admitted bit pattern, including signed
    zero, subnormals, infinities, and every NaN payload.
    """
    if isinstance(value, (bytes, bytearray)):
        if format_name is None:
            raise Pass220IEEEExactError("format name required for raw ingress")
        return encode_ieee_scalar(bytes(value), format_name, byteorder=byteorder)
    if isinstance(value, Mapping):
        if format_name is not None:
            raise Pass220IEEEExactError("format name is carried by encoded state")
        return validate_ieee_scalar_carrier(value)["raw"]
    raise Pass220IEEEExactError(
        "transform accepts raw IEEE bytes or an exact IEEE scalar carrier"
    )


def exhaustive_binary16_roundtrip_witness() -> Dict[str, Any]:
    """Exhaust all 65,536 binary16 storage states."""
    class_counts = {
        "zero": 0,
        "subnormal": 0,
        "normal": 0,
        "infinity": 0,
        "nan": 0,
    }
    for bits in range(1 << 16):
        raw = bits.to_bytes(2, "big")
        fields = split_fields(bits, "binary16")
        class_counts[classify_fields(fields, "binary16")] += 1
        if rebuild_bits("binary16", **fields) != bits:
            raise Pass220IEEEExactError(
                f"binary16 field roundtrip failed at 0x{bits:04x}"
            )
        carrier = encode_ieee_scalar(raw, "binary16")
        if g3_ieee_scalar_transform(carrier) != raw:
            raise Pass220IEEEExactError(
                f"binary16 reciprocal roundtrip failed at 0x{bits:04x}"
            )
    return {
        "states": 1 << 16,
        "class_counts": class_counts,
        "all_field_round_trips": True,
        "all_reciprocal_round_trips": True,
    }


def _deterministic_patterns(total_bits: int, count: int) -> Tuple[int, ...]:
    mask = (1 << total_bits) - 1
    state = (0x9E3779B97F4A7C15 ^ total_bits) & mask
    out = []
    for _ in range(count):
        state = (
            state * 6364136223846793005
            + 1442695040888963407
        ) & mask
        out.append(state)
    return tuple(out)


def sampled_wide_roundtrip_witness(count: int = 4096) -> Dict[str, Any]:
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise Pass220IEEEExactError("sample count must be positive")
    result: Dict[str, Any] = {}
    for name in ("binary32", "binary64", "binary128"):
        spec = _format(name)
        edge = (
            0,
            1,
            (1 << spec.fraction_bits) - 1,
            1 << spec.fraction_bits,
            (spec.exponent_max - 1) << spec.fraction_bits,
            (spec.exponent_max << spec.fraction_bits),
            (spec.exponent_max << spec.fraction_bits) | 1,
            (1 << spec.total_bits) - 1,
            1 << (spec.total_bits - 1),
        )
        patterns = edge + _deterministic_patterns(spec.total_bits, count)
        for bits in patterns:
            fields = split_fields(bits, name)
            if rebuild_bits(name, **fields) != bits:
                raise Pass220IEEEExactError(
                    f"{name} field roundtrip failed at {bits}"
                )
            raw = bits_to_raw(bits, name)
            if g3_ieee_scalar_transform(
                g3_ieee_scalar_transform(raw, name)
            ) != raw:
                raise Pass220IEEEExactError(
                    f"{name} reciprocal roundtrip failed at {bits}"
                )
        result[name] = {
            "patterns": len(patterns),
            "edge_patterns": len(edge),
            "deterministic_patterns": count,
            "all_field_round_trips": True,
            "all_reciprocal_round_trips": True,
        }
    return result


def ieee_scalar_involution_witness() -> Dict[str, Any]:
    # Known IEEE binary64 encoding of the machine scalar commonly printed 0.1.
    one_tenth_bits = 0x3FB999999999999A
    one_tenth_fields = split_fields(one_tenth_bits, "binary64")
    one_tenth_dyadic = exact_dyadic(one_tenth_fields, "binary64")

    signed_zero = (
        split_fields(0x0000000000000000, "binary64"),
        split_fields(0x8000000000000000, "binary64"),
    )
    nan_payload = 0x7FF8000000000042
    nan_raw = bits_to_raw(nan_payload, "binary64")
    nan_roundtrip = g3_ieee_scalar_transform(
        g3_ieee_scalar_transform(nan_raw, "binary64")
    )

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "formats": {
            name: {
                "total_bits": spec.total_bits,
                "exponent_bits": spec.exponent_bits,
                "fraction_bits": spec.fraction_bits,
                "bias": spec.bias,
            }
            for name, spec in IEEE_BINARY_FORMATS.items()
        },
        "binary16_exhaustive": exhaustive_binary16_roundtrip_witness(),
        "wide_samples": sampled_wide_roundtrip_witness(),
        "binary64_0p1_bits": f"{one_tenth_bits:016x}",
        "binary64_0p1_exact_dyadic": {
            "numerator": one_tenth_dyadic[0],
            "denominator": one_tenth_dyadic[1],
        },
        "signed_zero_fields_distinct": signed_zero[0] != signed_zero[1],
        "signed_zero_numeric_projection_equal": (
            exact_dyadic(signed_zero[0], "binary64")
            == exact_dyadic(signed_zero[1], "binary64")
            == (0, 1)
        ),
        "nan_payload_bits": f"{nan_payload:016x}",
        "nan_payload_roundtrip_exact": nan_roundtrip == nan_raw,
        "same_operation_both_directions": True,
        "reciprocal_rule": "y=1/x",
        "phase_changes_scalar_does_not": True,
        "proof_cell": PROOF_CELL_TOKEN,
        "forward_zero": FORWARD_ZERO,
        "return_zero": RETURN_ZERO,
        "host_float_arithmetic_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "floating_point_authority": False,
    })


def validate_ieee_scalar_involution() -> Dict[str, Any]:
    witness = ieee_scalar_involution_witness()
    binary16 = witness["binary16_exhaustive"]
    wide = witness["wide_samples"]
    expected_counts = {
        "zero": 2,
        "subnormal": 2046,
        "normal": 61440,
        "infinity": 2,
        "nan": 2046,
    }
    ok = all((
        binary16["states"] == 65536,
        binary16["class_counts"] == expected_counts,
        binary16["all_field_round_trips"],
        binary16["all_reciprocal_round_trips"],
        all(item["all_field_round_trips"] for item in wide.values()),
        all(item["all_reciprocal_round_trips"] for item in wide.values()),
        witness["binary64_0p1_exact_dyadic"] == {
            "numerator": 3602879701896397,
            "denominator": 36028797018963968,
        },
        witness["signed_zero_fields_distinct"],
        witness["signed_zero_numeric_projection_equal"],
        witness["nan_payload_roundtrip_exact"],
        witness["same_operation_both_directions"],
        witness["phase_changes_scalar_does_not"],
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
        "mutation_policy": "READ_ONLY_IEEE_SCALAR_PROOF_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def ieee_scalar_involution_self_test() -> Dict[str, Any]:
    return validate_ieee_scalar_involution()
