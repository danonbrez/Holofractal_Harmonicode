"""Pass 220 I038: DESI public-data Lane 5 parallel exact observational egress.

I038 implements the T_COSMO-07 numerical-egress boundary as a read-only,
multi-representational constructor.  Public DESI decimal measurements enter as
exact rationals and are carried in parallel through:

1. exact decimal/rational source state;
2. integer-only nearest-even IEEE binary64 storage construction;
3. the inherited palindromic symbolic/full-phase IEEE path (I031/I032/I033);
4. the inherited fixed-width 5,184-character BigInt serialization;
5. the I037 mandatory 24D equation/proof bundle identity; and
6. Lane 5 validated-constructor composition metadata.

No host float participates in the conversion or comparison.  The exact decimal
measurement remains the observational source; the IEEE state is a co-resident
transport/calculator view whose exact dyadic discrepancy is retained as a
rational residue rather than rounded away.

Measurement uncertainty components are preserved as exact observational
boundary metadata.  They are not combined into a probability, likelihood, MCMC
weight, or fit objective by this constructor.

The initial public fixture is the DESI DR2 Ly-alpha BAO result at z_eff=2.33,
published with D_H/r_d=8.632 and D_M/r_d=38.99 and separate statistical and
systematic uncertainty components.  These public decimal strings are retained
verbatim and parsed exactly.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
import re
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_24d_mandatory_constraint_spacetime_v1 import (
    constructor_bundle_root,
    twentyfour_d_constraint_spacetime_witness,
)
from hhs_runtime.hhs_pass220_g3_4711_symbolic_numeric_constructor_v1 import (
    build_solver_constructor,
    validate_solver_constructor,
)
from hhs_runtime.hhs_pass220_g3_ieee_scalar_involution_v1 import (
    bits_to_raw,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    deserialize_offsets_5184,
)

SCHEMA = "HHS_PASS_220_I038_DESI_LANE5_PARALLEL_EXACT_EGRESS_V1"
VERSION = "1.0.0-checkpoint.38"
PROFILE = "PASS220-I038-DESI-LANE5-PARALLEL-EXACT-EGRESS-v1"
CARRIER_SCHEMA = "HHS_PASS_220_I038_PARALLEL_OBSERVATION_CARRIER_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I038_DESI_PUBLIC_RELEASE_WITNESS_V1"

DESI_DR2_LYA_PUBLIC_FIXTURE: Mapping[str, str] = {
    "release_id": "DESI_DR2_RESULTS_I_LYA_BAO_2025",
    "official_results_url": (
        "https://www.desi.lbl.gov/2025/03/19/desi-dr2-results-march-19-guide/"
    ),
    "official_data_index_url": "https://data.desi.lbl.gov/doc/papers/dr2/",
    "paper_url": "https://arxiv.org/abs/2503.14739",
    "z_eff": "2.33",
    "D_H_over_r_d": "8.632",
    "D_H_stat_sigma": "0.098",
    "D_H_sys_sigma": "0.026",
    "D_M_over_r_d": "38.99",
    "D_M_stat_sigma": "0.52",
    "D_M_sys_sigma": "0.12",
}

DESI_NUMERIC_FIELDS: Tuple[str, ...] = (
    "z_eff",
    "D_H_over_r_d",
    "D_H_stat_sigma",
    "D_H_sys_sigma",
    "D_M_over_r_d",
    "D_M_stat_sigma",
    "D_M_sys_sigma",
)

DECIMAL_PATTERN = re.compile(
    r"^(?P<sign>[+-]?)(?P<int>\d*)(?:\.(?P<frac>\d*))?"
    r"(?:[eE](?P<exp>[+-]?\d+))?$"
)


class Pass220I038DESIError(ValueError):
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


def _fraction_record(value: Fraction) -> Dict[str, int]:
    q = Fraction(value)
    return {
        "numerator": q.numerator,
        "denominator": q.denominator,
    }


def _fraction_from_record(record: Mapping[str, Any]) -> Fraction:
    try:
        numerator = record["numerator"]
        denominator = record["denominator"]
    except Exception as exc:
        raise Pass220I038DESIError("fraction record missing fields") from exc
    if (
        isinstance(numerator, bool)
        or not isinstance(numerator, int)
        or isinstance(denominator, bool)
        or not isinstance(denominator, int)
        or denominator <= 0
    ):
        raise Pass220I038DESIError("invalid exact fraction record")
    return Fraction(numerator, denominator)


def parse_exact_decimal(text: str) -> Fraction:
    """Parse a finite decimal/scientific spelling without float or Decimal."""
    if not isinstance(text, str) or not text:
        raise Pass220I038DESIError("decimal source must be a non-empty string")
    match = DECIMAL_PATTERN.fullmatch(text)
    if match is None:
        raise Pass220I038DESIError("invalid exact decimal spelling")

    integer_digits = match.group("int") or ""
    fractional_digits = match.group("frac")
    if not integer_digits and (fractional_digits is None or fractional_digits == ""):
        raise Pass220I038DESIError("decimal spelling contains no digits")
    if fractional_digits is None:
        fractional_digits = ""

    sign = -1 if match.group("sign") == "-" else 1
    exponent10 = int(match.group("exp") or "0")
    digits = (integer_digits or "0") + fractional_digits
    coefficient = int(digits or "0")
    scale10 = len(fractional_digits) - exponent10

    if scale10 >= 0:
        value = Fraction(sign * coefficient, 10**scale10)
    else:
        value = Fraction(sign * coefficient * (10 ** (-scale10)), 1)
    return value


def _round_ratio_nearest_even(numerator: int, denominator: int) -> int:
    if (
        isinstance(numerator, bool)
        or not isinstance(numerator, int)
        or numerator < 0
        or isinstance(denominator, bool)
        or not isinstance(denominator, int)
        or denominator <= 0
    ):
        raise Pass220I038DESIError("nearest-even ratio requires nonnegative exact integers")
    quotient, remainder = divmod(numerator, denominator)
    twice = remainder * 2
    if twice < denominator:
        return quotient
    if twice > denominator:
        return quotient + 1
    return quotient if quotient % 2 == 0 else quotient + 1


def _floor_log2_positive_fraction(numerator: int, denominator: int) -> int:
    if numerator <= 0 or denominator <= 0:
        raise Pass220I038DESIError("log2 helper requires positive fraction")
    exponent = numerator.bit_length() - denominator.bit_length()
    if exponent >= 0:
        if numerator < (denominator << exponent):
            exponent -= 1
    else:
        if (numerator << (-exponent)) < denominator:
            exponent -= 1
    return exponent


def fraction_to_binary64_bits(value: Fraction) -> int:
    """Round an exact rational to IEEE binary64 using integer nearest-even logic."""
    q = Fraction(value)
    sign_bit = 1 if q < 0 else 0
    magnitude = abs(q)
    if magnitude == 0:
        return sign_bit << 63

    numerator = magnitude.numerator
    denominator = magnitude.denominator
    exponent = _floor_log2_positive_fraction(numerator, denominator)

    # Overflow to infinity if the exact magnitude lies above binary64 range
    # after nearest-even rounding.
    if exponent > 1023:
        return (sign_bit << 63) | (0x7FF << 52)

    if exponent >= -1022:
        shift = 52 - exponent
        if shift >= 0:
            scaled_num = numerator << shift
            scaled_den = denominator
        else:
            scaled_num = numerator
            scaled_den = denominator << (-shift)
        significand = _round_ratio_nearest_even(scaled_num, scaled_den)

        if significand >= (1 << 53):
            significand >>= 1
            exponent += 1
            if exponent > 1023:
                return (sign_bit << 63) | (0x7FF << 52)

        if significand < (1 << 52):
            # A boundary value can round down into subnormal representation.
            subnormal = _round_ratio_nearest_even(
                numerator << 1074,
                denominator,
            )
            if subnormal >= (1 << 52):
                return (sign_bit << 63) | (1 << 52)
            return (sign_bit << 63) | subnormal

        exponent_field = exponent + 1023
        fraction_field = significand - (1 << 52)
        return (
            (sign_bit << 63)
            | (exponent_field << 52)
            | fraction_field
        )

    # Subnormal / underflow path: value = fraction_field * 2^-1074.
    subnormal = _round_ratio_nearest_even(
        numerator << 1074,
        denominator,
    )
    if subnormal == 0:
        return sign_bit << 63
    if subnormal >= (1 << 52):
        # Rounded to the smallest normal value.
        return (sign_bit << 63) | (1 << 52)
    return (sign_bit << 63) | subnormal


def decimal_to_binary64_raw(text: str) -> bytes:
    bits = fraction_to_binary64_bits(parse_exact_decimal(text))
    return bits_to_raw(bits, "binary64", byteorder="big")


def _dyadic_fraction_from_multirep(
    multirep: Mapping[str, Any],
) -> Fraction:
    try:
        dyadic = multirep["representation_views"]["exact_dyadic_projection"]
    except Exception as exc:
        raise Pass220I038DESIError("missing exact IEEE dyadic projection") from exc
    if not isinstance(dyadic, Mapping):
        raise Pass220I038DESIError("IEEE dyadic projection must be finite")
    numerator = dyadic.get("numerator")
    denominator = dyadic.get("denominator")
    if (
        isinstance(numerator, bool)
        or not isinstance(numerator, int)
        or isinstance(denominator, bool)
        or not isinstance(denominator, int)
        or denominator <= 0
    ):
        raise Pass220I038DESIError("finite binary64 dyadic is not materialized")
    return Fraction(numerator, denominator)


def build_parallel_observation_carrier(
    *,
    observable: str,
    decimal_text: str,
    offsets: Sequence[int] | None = None,
    source_release_id: str = DESI_DR2_LYA_PUBLIC_FIXTURE["release_id"],
) -> Dict[str, Any]:
    if not isinstance(observable, str) or not observable:
        raise Pass220I038DESIError("observable must be a non-empty string")
    if not isinstance(source_release_id, str) or not source_release_id:
        raise Pass220I038DESIError("source release id must be a non-empty string")

    exact_decimal = parse_exact_decimal(decimal_text)
    raw = decimal_to_binary64_raw(decimal_text)
    offset_tuple = tuple((0,) * VM81_CELLS if offsets is None else offsets)
    if len(offset_tuple) != VM81_CELLS:
        raise Pass220I038DESIError("parallel carrier requires exactly 81 offsets")

    source_text = (
        f"{source_release_id}:{observable}={decimal_text}"
    )
    try:
        multirep = build_solver_constructor(
            source_text,
            raw,
            "binary64",
            offset_tuple,
            byteorder="big",
        )
        validated = validate_solver_constructor(multirep)
    except Exception as exc:
        raise Pass220I038DESIError(str(exc)) from exc

    ieee_dyadic = _dyadic_fraction_from_multirep(multirep)
    residue = exact_decimal - ieee_dyadic
    bigint_5184 = multirep["representation_views"]["bigint_5184"]
    if (
        not isinstance(bigint_5184, str)
        or len(bigint_5184) != SERIALIZED_CHARACTERS
    ):
        raise Pass220I038DESIError("5,184-character BigInt carrier missing")
    if deserialize_offsets_5184(bigint_5184) != offset_tuple:
        raise Pass220I038DESIError("BigInt carrier roundtrip mismatch")

    phase_root = constructor_bundle_root()
    return _receipt({
        "schema": CARRIER_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "source_release_id": source_release_id,
        "observable": observable,
        "decimal_source_text": decimal_text,
        "exact_decimal_rational": _fraction_record(exact_decimal),
        "binary64_bits_hex": raw.hex(),
        "exact_ieee_dyadic": _fraction_record(ieee_dyadic),
        "decimal_minus_ieee_exact_residue": _fraction_record(residue),
        "decimal_and_ieee_are_co_resident": True,
        "decimal_source_replaced_by_ieee": False,
        "ieee_transport_replaced_by_decimal": False,
        "multirepresentational_constructor": multirep,
        "multirepresentational_validation": {
            "ok": validated["ok"],
            "bigint_5184_roundtrip": validated["bigint_5184_roundtrip"],
            "scalar_bigint_roundtrip": validated["scalar_bigint_roundtrip"],
            "symbol_reciprocal_roundtrip": validated["symbol_reciprocal_roundtrip"],
            "ieee_reciprocal_roundtrip": validated["ieee_reciprocal_roundtrip"],
            "co_resident_views_preserved": validated["co_resident_views_preserved"],
        },
        "bigint_5184_characters": len(bigint_5184),
        "bigint_offsets": offset_tuple,
        "i037_mandatory_constructor_bundle_root_sha256": phase_root,
        "parallel_lanes": (
            "EXACT_DECIMAL_RATIONAL",
            "PALINDROMIC_SYMBOLIC_IEEE_BINARY64",
            "EXACT_IEEE_DYADIC_RESIDUE",
            "BIGINT_5184",
            "I037_24D_EQUATION_PROOF_BUNDLE",
            "LANE5_VALIDATED_CONSTRUCTOR_COMPOSITION",
        ),
        "lane5_parallel_execution": True,
        "probability_used_in_equation_solve": False,
        "likelihood_used_in_equation_solve": False,
        "mcmc_used_in_equation_solve": False,
        "host_float_arithmetic_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "direct_canonical_persistence_authority": False,
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
    })


def validate_parallel_observation_carrier(
    carrier: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(carrier, Mapping):
        raise Pass220I038DESIError("carrier must be a mapping")
    if carrier.get("schema") != CARRIER_SCHEMA:
        raise Pass220I038DESIError("carrier schema mismatch")
    if not _receipt_matches(carrier):
        raise Pass220I038DESIError("carrier receipt mismatch")

    observable = carrier.get("observable")
    decimal_text = carrier.get("decimal_source_text")
    release_id = carrier.get("source_release_id")
    offsets = tuple(carrier.get("bigint_offsets", ()))
    expected = build_parallel_observation_carrier(
        observable=observable,
        decimal_text=decimal_text,
        offsets=offsets,
        source_release_id=release_id,
    )
    if carrier != expected:
        raise Pass220I038DESIError("parallel observation carrier drift")

    exact_decimal = _fraction_from_record(carrier["exact_decimal_rational"])
    ieee_dyadic = _fraction_from_record(carrier["exact_ieee_dyadic"])
    residue = _fraction_from_record(
        carrier["decimal_minus_ieee_exact_residue"]
    )
    if exact_decimal - ieee_dyadic != residue:
        raise Pass220I038DESIError("exact decimal/IEEE residue mismatch")

    for field in (
        "probability_used_in_equation_solve",
        "likelihood_used_in_equation_solve",
        "mcmc_used_in_equation_solve",
        "host_float_arithmetic_used",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "direct_canonical_persistence_authority",
    ):
        if carrier.get(field) is not False:
            raise Pass220I038DESIError(f"forbidden authority or solver path: {field}")

    return {
        "ok": True,
        "observable": observable,
        "exact_decimal": _fraction_record(exact_decimal),
        "binary64_bits_hex": carrier["binary64_bits_hex"],
        "exact_ieee_dyadic": _fraction_record(ieee_dyadic),
        "exact_residue": _fraction_record(residue),
        "bigint_5184_characters": carrier["bigint_5184_characters"],
        "parallel_lane_count": len(carrier["parallel_lanes"]),
    }


def build_desi_dr2_lya_public_release_witness(
    *,
    offsets: Sequence[int] | None = None,
) -> Dict[str, Any]:
    offset_tuple = tuple((0,) * VM81_CELLS if offsets is None else offsets)
    carriers = {
        field: build_parallel_observation_carrier(
            observable=field,
            decimal_text=DESI_DR2_LYA_PUBLIC_FIXTURE[field],
            offsets=offset_tuple,
        )
        for field in DESI_NUMERIC_FIELDS
    }
    validations = {
        field: validate_parallel_observation_carrier(carrier)
        for field, carrier in carriers.items()
    }
    i037 = twentyfour_d_constraint_spacetime_witness()
    if i037.get("ok") is not True:
        raise Pass220I038DESIError("I037 mandatory 24D bundle did not validate")

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "public_release": dict(DESI_DR2_LYA_PUBLIC_FIXTURE),
        "numeric_field_order": DESI_NUMERIC_FIELDS,
        "parallel_observation_carriers": carriers,
        "parallel_observation_validations": validations,
        "i037_witness_receipt_sha256": i037["receipt_sha256"],
        "i037_mandatory_constructor_bundle_root_sha256": constructor_bundle_root(),
        "measurement_policy": {
            "released_decimal_strings_are_exact_source": True,
            "ieee_lane_is_parallel_transport_calculator": True,
            "bigint_5184_lane_is_parallel_geometry_serialization": True,
            "epsilon_and_phase_provenance_not_erased": True,
            "uncertainty_components_kept_separate": True,
            "uncertainty_probability_combination_used": False,
            "parameter_refit_performed": False,
            "likelihood_evaluation_performed": False,
            "mcmc_performed": False,
        },
        "solve_boundary": (
            "OBSERVATION_RECEIPT_READY_FOR_EXPLICIT_DESI_TO_HHS_VARIABLE_BINDING"
        ),
        "implicit_desi_to_hhs_variable_mapping": False,
        "host_float_arithmetic_used": False,
        "canonical_admission_authority": False,
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
    })


def validate_desi_dr2_lya_public_release_witness(
    witness: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(witness, Mapping):
        raise Pass220I038DESIError("DESI witness must be a mapping")
    if witness.get("schema") != WITNESS_SCHEMA:
        raise Pass220I038DESIError("DESI witness schema mismatch")
    if not _receipt_matches(witness):
        raise Pass220I038DESIError("DESI witness receipt mismatch")
    if witness.get("public_release") != dict(DESI_DR2_LYA_PUBLIC_FIXTURE):
        raise Pass220I038DESIError("DESI public fixture drift")
    if tuple(witness.get("numeric_field_order", ())) != DESI_NUMERIC_FIELDS:
        raise Pass220I038DESIError("DESI numeric field order drift")

    carriers = witness.get("parallel_observation_carriers")
    validations = witness.get("parallel_observation_validations")
    if not isinstance(carriers, Mapping) or not isinstance(validations, Mapping):
        raise Pass220I038DESIError("DESI carrier set missing")
    if set(carriers) != set(DESI_NUMERIC_FIELDS):
        raise Pass220I038DESIError("DESI carrier field coverage mismatch")

    for field in DESI_NUMERIC_FIELDS:
        result = validate_parallel_observation_carrier(carriers[field])
        if result != validations[field]:
            raise Pass220I038DESIError(f"{field} validation drift")

    policy = witness.get("measurement_policy")
    if not isinstance(policy, Mapping):
        raise Pass220I038DESIError("measurement policy missing")
    required_true = (
        "released_decimal_strings_are_exact_source",
        "ieee_lane_is_parallel_transport_calculator",
        "bigint_5184_lane_is_parallel_geometry_serialization",
        "epsilon_and_phase_provenance_not_erased",
        "uncertainty_components_kept_separate",
    )
    if not all(policy.get(key) is True for key in required_true):
        raise Pass220I038DESIError("parallel exact measurement policy lost")
    required_false = (
        "uncertainty_probability_combination_used",
        "parameter_refit_performed",
        "likelihood_evaluation_performed",
        "mcmc_performed",
    )
    if not all(policy.get(key) is False for key in required_false):
        raise Pass220I038DESIError("probabilistic/refit path entered I038")

    if witness.get("implicit_desi_to_hhs_variable_mapping") is not False:
        raise Pass220I038DESIError("implicit DESI-to-HHS mapping forbidden")
    if witness.get("host_float_arithmetic_used") is not False:
        raise Pass220I038DESIError("host float arithmetic forbidden")
    if witness.get("canonical_admission_authority") is not False:
        raise Pass220I038DESIError("I038 cannot admit canonical state")

    return {
        "ok": True,
        "release_id": DESI_DR2_LYA_PUBLIC_FIXTURE["release_id"],
        "carrier_count": len(carriers),
        "z_eff": _fraction_record(parse_exact_decimal(
            DESI_DR2_LYA_PUBLIC_FIXTURE["z_eff"]
        )),
        "D_H_over_r_d": _fraction_record(parse_exact_decimal(
            DESI_DR2_LYA_PUBLIC_FIXTURE["D_H_over_r_d"]
        )),
        "D_M_over_r_d": _fraction_record(parse_exact_decimal(
            DESI_DR2_LYA_PUBLIC_FIXTURE["D_M_over_r_d"]
        )),
        "parallel_exact_paths": True,
        "probability_free_equation_solve_boundary": True,
        "explicit_variable_binding_still_required": True,
    }


def desi_lane5_parallel_exact_egress_self_test() -> Dict[str, Any]:
    witness = build_desi_dr2_lya_public_release_witness()
    result = validate_desi_dr2_lya_public_release_witness(witness)
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": result["ok"],
        "result": result,
        "witness_receipt_sha256": witness["receipt_sha256"],
        "public_release_id": DESI_DR2_LYA_PUBLIC_FIXTURE["release_id"],
        "host_float_arithmetic_used": False,
        "probability_used_in_equation_solve": False,
        "canonical_admission_authority": False,
    })
