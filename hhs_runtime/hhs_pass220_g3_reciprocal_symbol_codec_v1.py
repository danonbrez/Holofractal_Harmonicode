"""Pass 220 I030: G^3 reciprocal symbol-string codec.

Read-only exact reference implementation for the constructor-level reversible
symbol-string surface discussed in the Pass 220 G^3/Ouroboros lineage.

The implementation deliberately does not parse source strings as numbers.
Binary text, IEEE spellings, BigInt/scientific notation, equations, and other
UTF-8 symbol strings remain exact strings. Ordered x/y/z/w phase expressions
are tagged constructors so Python cannot commute, cancel, or scalarize them.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Tuple, Union

SCHEMA = "HHS_PASS_220_I030_G3_RECIPROCAL_SYMBOL_CODEC_V1"
VERSION = "1.0.1-checkpoint.30-expanded-ingress"
PROFILE = "PASS220-I030-G3-RECIPROCAL-SYMBOL-CODEC-v1"
CARRIER_SCHEMA = "HHS_PASS_220_I030_G3_SYMBOL_CARRIER_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I030_G3_RECIPROCAL_SYMBOL_WITNESS_V1"

PROOF_CELL_TOKEN = "123321.111"
PHASE_NAMES = ("x", "y", "z", "w")
PHASE_RECIPROCAL = {"x": "y", "y": "x", "z": "w", "w": "z"}
RECIPROCAL_RELATIONS = ("y=1/x", "x=1/y", "w=1/z", "z=1/w")

EXPANDED_INGRESS_PROBES = (
    "(123,321,123,321/(999999,1000000,1000001))=X",
    "((123,321,123,321÷999,999)×(123,321,123,321÷1,000,001))×((123,321,123,321÷999,999)×(123,321,123,321÷1,000,001))^(−x²yx,y²-xy,z²=wz,w²=-zw)",
    "1000.0001=(1,0,0,0,0,0,0,0,1)=(-4,-3,-2,-1,0,+1,+2,+3,+4)=(4,9,2,35,7,8,1,6)=123321.111+111.123321=246642.246642=369963.369963",
)


class Pass220G3ReciprocalCodecError(ValueError):
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


def _phase(name: str) -> Tuple[str, str]:
    if name not in PHASE_RECIPROCAL:
        raise Pass220G3ReciprocalCodecError(f"invalid phase: {name!r}")
    return ("phase", name)


def _proof_cell() -> Tuple[str, str]:
    return ("proof_cell", PROOF_CELL_TOKEN)


def _oprod(*terms: Any) -> Tuple[Any, ...]:
    return ("oprod",) + tuple(terms)


def _osum(*terms: Any) -> Tuple[Any, ...]:
    return ("osum",) + tuple(terms)


def _oneg(term: Any) -> Tuple[str, Any]:
    return ("oneg", term)


def _odiff(left: Any, right: Any) -> Tuple[str, Any, Any]:
    return ("odiff", left, right)


def _odiv(numerator: Any, denominator: Any) -> Tuple[str, Any, Any]:
    return ("odiv", numerator, denominator)


FORWARD_ZERO = _odiv(
    _oprod(_phase("x"), _phase("y"), _proof_cell()),
    _phase("x"),
)


def reciprocal_phase_expr(value: Any) -> Any:
    """Swap only tagged phase carriers; source symbol payloads are untouched."""
    if (
        isinstance(value, tuple)
        and len(value) == 2
        and value[0] == "phase"
    ):
        return _phase(PHASE_RECIPROCAL[value[1]])
    if isinstance(value, tuple):
        return tuple(reciprocal_phase_expr(item) for item in value)
    if isinstance(value, list):
        return [reciprocal_phase_expr(item) for item in value]
    if isinstance(value, dict):
        return {
            key: reciprocal_phase_expr(item)
            for key, item in value.items()
        }
    return value


RETURN_ZERO = reciprocal_phase_expr(FORWARD_ZERO)

G3_PROOF_TENSOR = (
    (
        _oprod(_phase("x"), _phase("y")),
        _osum(_phase("x"), _phase("y")),
        _oprod(_phase("y"), _phase("x")),
    ),
    (
        _odiff(
            _oprod(_phase("x"), _phase("y")),
            _oprod(_phase("z"), _phase("w")),
        ),
        _osum(
            _phase("x"),
            _phase("y"),
            _oneg(_phase("z")),
            _oneg(_phase("w")),
            _oprod(_phase("x"), _phase("y")),
            _oprod(_phase("y"), _phase("x")),
            _oneg(_oprod(_phase("z"), _phase("w"))),
            _oneg(_oprod(_phase("w"), _phase("z"))),
        ),
        _odiff(
            _oprod(_phase("w"), _phase("z")),
            _oprod(_phase("y"), _phase("x")),
        ),
    ),
    (
        _oprod(_phase("w"), _phase("z")),
        _osum(_phase("z"), _phase("w")),
        _oprod(_phase("z"), _phase("w")),
    ),
)


def digit_cell(symbol: str, position: int) -> Dict[str, Any]:
    """Lift one Arabic numeral without parsing the enclosing source string."""
    if not isinstance(position, int) or isinstance(position, bool) or position < 0:
        raise Pass220G3ReciprocalCodecError("position must be a nonnegative integer")
    if symbol == "0":
        return {
            "kind": "phase_zero",
            "position": position,
            "symbol_utf8_hex": "30",
            "forward_zero": FORWARD_ZERO,
            "return_zero": RETURN_ZERO,
            "proof_cell": PROOF_CELL_TOKEN,
        }
    if symbol in "123456789":
        return {
            "kind": "scaled_proof_cell",
            "position": position,
            "symbol_utf8_hex": symbol.encode("utf-8").hex(),
            "scale": ord(symbol) - ord("0"),
            "proof_cell": PROOF_CELL_TOKEN,
        }
    raise Pass220G3ReciprocalCodecError("digit_cell accepts only one Arabic numeral")


def _symbol_cell(symbol: str, position: int) -> Dict[str, Any]:
    if symbol in "0123456789":
        return digit_cell(symbol, position)
    encoded = symbol.encode("utf-8")
    return {
        "kind": "opaque_symbol",
        "position": position,
        "symbol_utf8_hex": encoded.hex(),
        "codepoint": ord(symbol),
    }


def _symbol_cells(text: str) -> Tuple[Dict[str, Any], ...]:
    return tuple(_symbol_cell(symbol, index) for index, symbol in enumerate(text))


def encode_symbol_string(text: str) -> Dict[str, Any]:
    """Construct the reciprocal carrier for one exact UTF-8 symbol string."""
    if not isinstance(text, str):
        raise Pass220G3ReciprocalCodecError("source must be a string")
    try:
        payload = text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise Pass220G3ReciprocalCodecError(
            "source must be a valid UTF-8 encodable Unicode string"
        ) from exc

    return _receipt({
        "schema": CARRIER_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "encoding": "UTF-8",
        "forward_hex": payload.hex(),
        "return_hex": payload[::-1].hex(),
        "payload_sha256": sha256(payload).hexdigest(),
        "symbol_count": len(text),
        "byte_length": len(payload),
        "ingress_phase": "x",
        "return_phase": "y",
        "reciprocal_rule": "y=1/x",
        "reciprocal_relations": RECIPROCAL_RELATIONS,
        "proof_cell": PROOF_CELL_TOKEN,
        "forward_zero": FORWARD_ZERO,
        "return_zero": RETURN_ZERO,
        "symbol_cells": _symbol_cells(text),
        "numeric_parse_performed": False,
        "floating_point_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def _receipt_matches(carrier: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in carrier:
        return False
    body = dict(carrier)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def _payload_candidates(carrier: Mapping[str, Any]) -> Tuple[Tuple[str, bytes], ...]:
    expected = carrier.get("payload_sha256")
    if not isinstance(expected, str):
        raise Pass220G3ReciprocalCodecError("missing payload digest")

    candidates = []
    for label, field, reverse in (
        ("forward", "forward_hex", False),
        ("return", "return_hex", True),
    ):
        encoded = carrier.get(field)
        if not isinstance(encoded, str):
            continue
        try:
            payload = bytes.fromhex(encoded)
        except ValueError:
            continue
        if reverse:
            payload = payload[::-1]
        if sha256(payload).hexdigest() == expected:
            candidates.append((label, payload))
    return tuple(candidates)


def _decode_verified_payload(payload: bytes) -> str:
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Pass220G3ReciprocalCodecError(
            "verified payload is not valid UTF-8"
        ) from exc


def validate_symbol_carrier(carrier: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(carrier, Mapping):
        raise Pass220G3ReciprocalCodecError("carrier must be a mapping")
    if carrier.get("schema") != CARRIER_SCHEMA:
        raise Pass220G3ReciprocalCodecError("carrier schema mismatch")
    if carrier.get("proof_cell") != PROOF_CELL_TOKEN:
        raise Pass220G3ReciprocalCodecError("proof cell mismatch")
    if carrier.get("ingress_phase") != "x" or carrier.get("return_phase") != "y":
        raise Pass220G3ReciprocalCodecError("reciprocal phase orientation mismatch")
    if carrier.get("reciprocal_rule") != "y=1/x":
        raise Pass220G3ReciprocalCodecError("reciprocal rule mismatch")
    if carrier.get("forward_zero") != FORWARD_ZERO:
        raise Pass220G3ReciprocalCodecError("forward zero lock mismatch")
    if carrier.get("return_zero") != RETURN_ZERO:
        raise Pass220G3ReciprocalCodecError("return zero lock mismatch")
    if reciprocal_phase_expr(carrier["forward_zero"]) != carrier["return_zero"]:
        raise Pass220G3ReciprocalCodecError("zero locks are not reciprocal")
    if not _receipt_matches(carrier):
        raise Pass220G3ReciprocalCodecError("carrier receipt mismatch")

    candidates = _payload_candidates(carrier)
    if len(candidates) != 2 or candidates[0][1] != candidates[1][1]:
        raise Pass220G3ReciprocalCodecError(
            "both reciprocal paths must validate and reconstruct the same payload"
        )
    payload = candidates[0][1]
    text = _decode_verified_payload(payload)

    if carrier.get("byte_length") != len(payload):
        raise Pass220G3ReciprocalCodecError("byte length mismatch")
    if carrier.get("symbol_count") != len(text):
        raise Pass220G3ReciprocalCodecError("symbol count mismatch")
    if tuple(carrier.get("symbol_cells", ())) != _symbol_cells(text):
        raise Pass220G3ReciprocalCodecError("symbol-cell provenance mismatch")
    if carrier.get("numeric_parse_performed") is not False:
        raise Pass220G3ReciprocalCodecError("numeric parsing is forbidden")

    return {
        "ok": True,
        "text": text,
        "valid_paths": ("forward", "return"),
        "receipt_valid": True,
        "phase_involution": (
            reciprocal_phase_expr(reciprocal_phase_expr(FORWARD_ZERO))
            == FORWARD_ZERO
        ),
    }


def repair_single_path_and_decode(carrier: Mapping[str, Any]) -> Dict[str, Any]:
    """Recover when exactly one redundant byte path still matches the digest.

    This is bounded path-level repair, not a claim of arbitrary error
    correction. Immutable constructor metadata and the original payload digest
    must remain intact.
    """
    if not isinstance(carrier, Mapping):
        raise Pass220G3ReciprocalCodecError("carrier must be a mapping")
    if carrier.get("schema") != CARRIER_SCHEMA:
        raise Pass220G3ReciprocalCodecError("carrier schema mismatch")
    if carrier.get("proof_cell") != PROOF_CELL_TOKEN:
        raise Pass220G3ReciprocalCodecError("proof cell mismatch")
    if carrier.get("forward_zero") != FORWARD_ZERO:
        raise Pass220G3ReciprocalCodecError("forward zero lock mismatch")
    if carrier.get("return_zero") != RETURN_ZERO:
        raise Pass220G3ReciprocalCodecError("return zero lock mismatch")

    candidates = _payload_candidates(carrier)
    if not candidates:
        raise Pass220G3ReciprocalCodecError(
            "neither redundant path matches the payload digest"
        )
    payloads = {payload for _, payload in candidates}
    if len(payloads) != 1:
        raise Pass220G3ReciprocalCodecError(
            "reciprocal paths disagree after digest validation"
        )

    text = _decode_verified_payload(next(iter(payloads)))
    if tuple(carrier.get("symbol_cells", ())) != _symbol_cells(text):
        raise Pass220G3ReciprocalCodecError("symbol-cell provenance mismatch")
    return {
        "ok": True,
        "text": text,
        "valid_paths": tuple(label for label, _ in candidates),
        "repaired_single_path": len(candidates) == 1,
        "strict_receipt_valid": _receipt_matches(carrier),
    }


ReciprocalValue = Union[str, Mapping[str, Any]]


def g3_reciprocal_transform(value: ReciprocalValue) -> Union[str, Dict[str, Any]]:
    """Apply the one public reciprocal operation.

    On a source string it constructs the x-oriented carrier with its y=1/x
    return path. On a valid carrier the same callable consumes the reciprocal
    path and returns the exact source string. Therefore T(T(s)) == s on the
    admitted UTF-8 string domain.
    """
    if isinstance(value, str):
        return encode_symbol_string(value)
    if isinstance(value, Mapping):
        return validate_symbol_carrier(value)["text"]
    raise Pass220G3ReciprocalCodecError(
        "transform accepts an exact symbol string or a reciprocal carrier"
    )


def reciprocal_symbol_codec_witness() -> Dict[str, Any]:
    probes = (
        "123321.111",
        "0001.0",
        "0011111111110000000000000000000000000000000000000000000000000000",
        "-0.0",
        "1.00e+000",
        "x+y=0; y=1/x; 0=Φ; Ω",
        *EXPANDED_INGRESS_PROBES,
    )
    round_trips = tuple(
        g3_reciprocal_transform(g3_reciprocal_transform(text)) == text
        for text in probes
    )
    digit_cells = tuple(digit_cell(str(digit), digit) for digit in range(10))
    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "proof_cell": PROOF_CELL_TOKEN,
        "forward_zero": FORWARD_ZERO,
        "return_zero": RETURN_ZERO,
        "phase_reciprocal": PHASE_RECIPROCAL,
        "reciprocal_relations": RECIPROCAL_RELATIONS,
        "g3_tensor": G3_PROOF_TENSOR,
        "g3_tensor_phase_involution": (
            reciprocal_phase_expr(reciprocal_phase_expr(G3_PROOF_TENSOR))
            == G3_PROOF_TENSOR
        ),
        "zero_phase_involution": (
            reciprocal_phase_expr(reciprocal_phase_expr(FORWARD_ZERO))
            == FORWARD_ZERO
        ),
        "digit_cells": digit_cells,
        "all_probe_round_trips": all(round_trips),
        "probe_round_trips": round_trips,
        "expanded_ingress_probes": EXPANDED_INGRESS_PROBES,
        "expanded_ingress_probe_count": len(EXPANDED_INGRESS_PROBES),
        "expanded_ingress_probe_round_trips": round_trips[-len(EXPANDED_INGRESS_PROBES):],
        "one_operation_both_directions": True,
        "return_phase_constraint": "y=1/x",
        "source_strings_parsed_as_numbers": False,
        "bounded_error_repair": "ONE_REDUNDANT_BYTE_PATH_WITH_INTACT_DIGEST_AND_SYMBOL_PROVENANCE",
        "floating_point_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def validate_reciprocal_symbol_codec() -> Dict[str, Any]:
    witness = reciprocal_symbol_codec_witness()
    zero = witness["digit_cells"][0]
    nonzero = witness["digit_cells"][1:]
    ok = all((
        witness["g3_tensor_phase_involution"],
        witness["zero_phase_involution"],
        witness["all_probe_round_trips"],
        zero["kind"] == "phase_zero",
        zero["forward_zero"] == FORWARD_ZERO,
        zero["return_zero"] == RETURN_ZERO,
        all(cell["kind"] == "scaled_proof_cell" for cell in nonzero),
        all(cell["proof_cell"] == PROOF_CELL_TOKEN for cell in nonzero),
        all(cell["scale"] == index for index, cell in enumerate(nonzero, start=1)),
        witness["source_strings_parsed_as_numbers"] is False,
        witness["floating_point_authority"] is False,
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
        "mutation_policy": "READ_ONLY_RECIPROCAL_SYMBOL_PROOF_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def reciprocal_symbol_codec_self_test() -> Dict[str, Any]:
    return validate_reciprocal_symbol_codec()
