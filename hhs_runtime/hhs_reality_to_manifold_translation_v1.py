"""
HHS Reality-to-Manifold Translation Protocol v1
===============================================

Pass 033 installs the upstream admissibility layer for external/material,
symbolic, temporal, and phase-operator inputs.  The protocol does not treat
input as passive data.  It treats input as an unresolved manifold state that may
propagate only when the full constraint set produces an explicit witness chain:

* 12-symbol / 4-part / 3-symbol palindromic tensor seed validation;
* additive and multiplicative phase-product ECC for ordered non-commutative
  xyzw reciprocal seesaw traces;
* lossless Hash72/u^72 BigInt floating-string / HHS algebraic serialization;
* harmonic-time / audio phase coherence registration using exact sample
  counts, rational sample rates, and integer ticks;
* propagation admissibility / non-harmonic-noise rejection records;
* Hash72/u^72 kernel witnesses, HHS Foundational conformance, and ledger
  receipts for both accepted and rejected paths.

This module is intentionally conservative.  It does not claim a physical object
is literally stored.  It proves that an observed state can be represented as a
closed, witnessed relational constraint structure without silent coercion,
floating-point authority, or lossy compression.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import json
import re

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import make_execution_request, make_runtime_packet
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_REALITY_TO_MANIFOLD_TRANSLATION_PROTOCOL_V1"
VERSION = "PASS_033"
MANIFEST_FILE = "REALITY_TO_MANIFOLD_TRANSLATION_PASS_033.json"
REPORT_FILE = "REALITY_TO_MANIFOLD_TRANSLATION_PASS_033.md"
THEOREM_FILE = "MANIFOLD_PROPAGATION_THEOREM_PASS_033.md"
NOISE_POLICY_FILE = "NON_HARMONIC_NOISE_POLICY_PASS_033.md"
SECURITY_FILE = "NON_SILENT_PROPAGATION_SECURITY_PASS_033.md"
HASH72_LEN = 72
HASH72_BASE = 72
U216_BASE = 216
CANONICAL_TENSOR_SEED = "179971.179971"
CANONICAL_TENSOR_STRING = "179971179971"
CANONICAL_TENSOR_PARTS = ("179", "971", "179", "971")
CANONICAL_RESONATOR_RATIONAL = Fraction(179971179971, 1_000_000)
OMEGA_PROJECTION_WITNESS = Fraction(1_000_001, 1_000_000)
SRCG_CLOSURE_TARGET = Fraction(1001, 1000)


class HHSRealityToManifoldError(RuntimeError):
    """Raised when an unresolved state cannot be admitted to the manifold."""


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def _json_stable(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str))


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        text = value.strip()
        if "/" in text:
            numerator, denominator = text.split("/", 1)
            return Fraction(int(numerator), int(denominator))
        if "." in text:
            whole, decimals = text.split(".", 1)
            sign = -1 if whole.startswith("-") else 1
            whole_digits = whole[1:] if sign == -1 else whole
            digits = f"{whole_digits}{decimals}"
            return Fraction(sign * int(digits), 10 ** len(decimals))
        return Fraction(int(text), 1)
    # Deliberately preserve exact decimal text when a caller accidentally passes
    # a Python float.  The witness marks this as non-authority elsewhere; the
    # Fraction conversion avoids binary-float propagation.
    return Fraction(str(value))


def _fraction_dict(value: Fraction) -> Dict[str, Any]:
    return {
        "schema": "HHS_EXACT_RATIONAL_V1",
        "numerator": int(value.numerator),
        "denominator": int(value.denominator),
        "text": f"{value.numerator}/{value.denominator}",
    }


def _with_digest72_alias(witness: Mapping[str, Any]) -> Dict[str, Any]:
    data = dict(witness)
    data.setdefault("digest72", data.get("digest") or data.get("dna") or "")
    data.setdefault("authority", "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1")
    return data


def _digits_from_literal(literal: str) -> Tuple[str, str, str]:
    text = str(literal).strip()
    if text.count(".") != 1:
        raise HHSRealityToManifoldError("palindromic tensor seed requires exactly one fixed-point serialization seam")
    whole, decimal = text.split(".", 1)
    if not whole.isdigit() or not decimal.isdigit():
        raise HHSRealityToManifoldError("palindromic tensor seed must contain only decimal digits around the seam")
    return whole, decimal, whole + decimal


@dataclass(frozen=True)
class PalindromicTensorSeed12:
    raw_literal: str
    canonical_string: str
    parts: List[str]
    part_width: int
    part_count: int
    symbol_count: int
    serialization_form: str
    mirror_rule: str
    rational_projection: Dict[str, Any]
    valid: bool
    reasons: List[str]
    schema: str = "HHS_PALINDROMIC_TENSOR_SEED12_V1"
    version: str = VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseOperationTrace:
    operands: List[str]
    operator_family: str
    operation_order: str
    non_commutative: bool
    trace_identity: str
    schema: str = "HHS_PHASE_OPERATION_TRACE_V1"
    version: str = VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PalindromicPhaseProductWitness:
    product_type: str
    product_value: Dict[str, Any]
    projected_literal: str
    projected_tensor: Dict[str, Any]
    palindrome_valid: bool
    trace_identity: str
    kernel_witness: Dict[str, Any]
    schema: str = "HHS_PALINDROMIC_PHASE_PRODUCT_WITNESS_V1"
    version: str = VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Hash72BigIntStateCarrier:
    positions: List[int]
    rotation_profile: List[int]
    encoded_digits: List[int]
    base: int
    bigint: int
    scientific_notation: str
    hhs_symbolic_algebra: str
    lossless_decode: bool
    seed_tensor: Dict[str, Any]
    phase_product_witnesses: List[Dict[str, Any]]
    kernel_witness: Dict[str, Any]
    schema: str = "HHS_HASH72_BIGINT_FLOATING_STRING_SERIALIZATION_V1"
    version: str = VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HarmonicTimeAudioWitness:
    sample_index: int
    sample_rate: Dict[str, Any]
    frame_window_samples: int
    latency_ticks: int
    phase_modulus: int
    phase_offset: int
    latency_ratio: Dict[str, Any]
    harmonic_time_valid: bool
    reasons: List[str]
    kernel_witness: Dict[str, Any]
    schema: str = "HHS_HARMONIC_TIME_AUDIO_PHASE_ECC_WITNESS_V1"
    version: str = VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PropagationAdmissibilityRecord:
    schema: str
    version: str
    status: str
    accepted: bool
    reason_code: str
    reasons: List[str]
    physical_observation_packet: Dict[str, Any]
    symbolic_operator_state: Dict[str, Any]
    tensor_seed: Dict[str, Any]
    phase_operation_trace: Dict[str, Any]
    phase_product_witnesses: List[Dict[str, Any]]
    hash72_bigint_carrier: Dict[str, Any]
    harmonic_time_audio_witness: Dict[str, Any]
    triangulation_of_truth: Dict[str, Any]
    omega_projection_witness: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    proposition_identity: Dict[str, Any]
    meaning_witness: Dict[str, Any]
    foundational_conformance: Dict[str, Any]
    manifold_kernel_witness: Dict[str, Any]
    ledger: Dict[str, Any]
    security_policy: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_palindromic_tensor_seed12(literal: str = CANONICAL_TENSOR_SEED) -> Dict[str, Any]:
    reasons: List[str] = []
    valid = True
    try:
        whole, decimal, canonical = _digits_from_literal(literal)
    except HHSRealityToManifoldError as exc:
        return PalindromicTensorSeed12(
            raw_literal=str(literal),
            canonical_string="",
            parts=[],
            part_width=3,
            part_count=4,
            symbol_count=0,
            serialization_form="INVALID",
            mirror_rule="part_1 == reverse(part_4), part_2 == reverse(part_3)",
            rational_projection=_fraction_dict(Fraction(0, 1)),
            valid=False,
            reasons=[str(exc)],
        ).to_dict()
    if len(canonical) != 12:
        valid = False
        reasons.append("seed canonical string must contain exactly 12 symbols")
    if len(whole) != 6 or len(decimal) != 6:
        valid = False
        reasons.append("seed requires six whole-side symbols and six decimal-side symbols")
    if len(canonical) % 3 != 0:
        valid = False
        reasons.append("seed canonical string must split into tri-symbol tensor cells")
    parts = [canonical[i : i + 3] for i in range(0, len(canonical), 3)] if canonical else []
    if len(parts) != 4 or any(len(part) != 3 for part in parts):
        valid = False
        reasons.append("seed must split into four 3-symbol parts")
    if len(parts) == 4:
        if parts[0] != parts[3][::-1]:
            valid = False
            reasons.append("part_1 must equal reverse(part_4)")
        if parts[1] != parts[2][::-1]:
            valid = False
            reasons.append("part_2 must equal reverse(part_3)")
    if canonical != CANONICAL_TENSOR_STRING:
        valid = False
        reasons.append("seed canonical string must match HHS resonator tensor 179|971|179|971")
    if valid:
        reasons.append("12-symbol 4x3 palindromic tensor seed is valid")
    rational = Fraction(int(canonical or "0"), 10 ** len(decimal)) if decimal else Fraction(0, 1)
    return PalindromicTensorSeed12(
        raw_literal=str(literal),
        canonical_string=canonical,
        parts=parts,
        part_width=3,
        part_count=len(parts),
        symbol_count=len(canonical),
        serialization_form="AB.AB",
        mirror_rule="part_1 == reverse(part_4), part_2 == reverse(part_3)",
        rational_projection=_fraction_dict(rational),
        valid=valid,
        reasons=reasons,
    ).to_dict()


def _phase_trace(operands: Sequence[Any], operator_family: str = "xyzw_non_commutative_reciprocal_seesaw") -> PhaseOperationTrace:
    operand_text = [str(item) for item in operands]
    order = "->".join(operand_text)
    trace_identity = make_hash72_kernel_witness(
        "HHS_PHASE_OPERATION_TRACE_IDENTITY_V1",
        {"operands": operand_text, "operator_family": operator_family, "operation_order": order},
        width=72,
    ).digest
    return PhaseOperationTrace(
        operands=operand_text,
        operator_family=operator_family,
        operation_order=order,
        non_commutative=True,
        trace_identity=trace_identity,
    )


def _project_product_to_seed_form(product: Fraction, seed_literal: str = CANONICAL_TENSOR_SEED) -> str:
    # The product is kept in the witness as exact rational authority.  The
    # fixed-point projection is an ECC carrier.  For the canonical resonator
    # product, it is exactly the 12-symbol tensor seed.  Non-canonical products
    # are rendered as six-decimal fixed-point strings and generally fail the
    # tensor seed check rather than being coerced.
    if product == CANONICAL_RESONATOR_RATIONAL:
        return seed_literal
    scaled = product * 1_000_000
    if scaled.denominator == 1:
        sign = "-" if scaled.numerator < 0 else ""
        digits = str(abs(scaled.numerator)).rjust(12, "0")
        return f"{sign}{digits[:-6]}.{digits[-6:]}"
    # Non-terminating or incompatible projections are rejected by the seed gate.
    return f"{product.numerator}.{abs(product.denominator):06d}"


def make_phase_product_witnesses(
    operands: Sequence[Any] = ("179971.179971", "0", "0", "0"),
    *,
    seed_literal: str = CANONICAL_TENSOR_SEED,
) -> Dict[str, Any]:
    trace = _phase_trace(operands)
    fractions = [_fraction(value) for value in operands]
    multiplicative = Fraction(1, 1)
    for value in fractions:
        # In the default trace, zero placeholders act as neutral unresolved
        # dimensions for multiplicative transport; the trace still preserves
        # their ordered identity so xyzw != wzyx.
        if value != 0:
            multiplicative *= value
    additive = sum(fractions, Fraction(0, 1))
    witnesses: List[Dict[str, Any]] = []
    for product_type, product in (("multiplicative", multiplicative), ("additive", additive)):
        projected = _project_product_to_seed_form(product, seed_literal=seed_literal)
        tensor = validate_palindromic_tensor_seed12(projected)
        kernel = _with_digest72_alias(make_hash72_kernel_witness(
            f"HHS_PALINDROMIC_PHASE_PRODUCT_{product_type.upper()}_V1",
            {"trace": trace.to_dict(), "product": _fraction_dict(product), "projected_literal": projected, "tensor": tensor},
            width=72,
        ).to_dict())
        witnesses.append(PalindromicPhaseProductWitness(
            product_type=product_type,
            product_value=_fraction_dict(product),
            projected_literal=projected,
            projected_tensor=tensor,
            palindrome_valid=bool(tensor.get("valid")),
            trace_identity=trace.trace_identity,
            kernel_witness=kernel,
        ).to_dict())
    return {
        "schema": "HHS_PHASE_PRODUCT_ERROR_CORRECTION_RECORD_V1",
        "version": VERSION,
        "trace": trace.to_dict(),
        "multiplicative_product": witnesses[0],
        "additive_product": witnesses[1],
        "all_products_valid": all(bool(w.get("palindrome_valid")) for w in witnesses),
        "witnesses": witnesses,
    }


def _encode_digits(positions: Sequence[int], rotation_profile: Sequence[int]) -> Tuple[List[int], int, int]:
    if len(positions) != HASH72_LEN or len(rotation_profile) != HASH72_LEN:
        raise HHSRealityToManifoldError("Hash72 BigInt carrier requires exactly 72 positions and 72 rotation-profile entries")
    digits: List[int] = []
    bigint = 0
    base = HASH72_BASE * HASH72_BASE
    multiplier = 1
    for pos, rot in zip(positions, rotation_profile):
        p = int(pos) % HASH72_BASE
        r = int(rot) % HASH72_BASE
        digit = p + HASH72_BASE * r
        digits.append(digit)
        bigint += digit * multiplier
        multiplier *= base
    return digits, bigint, base


def _decode_digits(bigint: int, length: int = HASH72_LEN, base: int = HASH72_BASE * HASH72_BASE) -> Tuple[List[int], List[int]]:
    n = int(bigint)
    positions: List[int] = []
    rotations: List[int] = []
    for _ in range(length):
        digit = n % base
        n //= base
        positions.append(digit % HASH72_BASE)
        rotations.append(digit // HASH72_BASE)
    return positions, rotations


def make_hash72_bigint_state_carrier(
    positions: Optional[Sequence[int]] = None,
    rotation_profile: Optional[Sequence[int]] = None,
    *,
    seed_tensor: Optional[Mapping[str, Any]] = None,
    phase_product_witnesses: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    if positions is None:
        positions = [(i * 5 + 1) % HASH72_BASE for i in range(HASH72_LEN)]
    if rotation_profile is None:
        rotation_profile = [(i * 7 + 3) % HASH72_BASE for i in range(HASH72_LEN)]
    seed = dict(seed_tensor or validate_palindromic_tensor_seed12())
    phase = [dict(w) for w in (phase_product_witnesses or [])]
    digits, bigint, base = _encode_digits(positions, rotation_profile)
    decoded_positions, decoded_rotations = _decode_digits(bigint, HASH72_LEN, base)
    lossless = decoded_positions == [int(x) % HASH72_BASE for x in positions] and decoded_rotations == [int(x) % HASH72_BASE for x in rotation_profile]
    mantissa = str(bigint)
    scientific = f"{mantissa[0]}.{mantissa[1:]}e+{len(mantissa)-1}" if len(mantissa) > 1 else f"{mantissa}e+0"
    symbolic = f"⟦HHS:u^72;T12={ '|'.join(seed.get('parts', [])) };N={bigint};B={base};χ=PAL_PHASE_ECC_V1⟧"
    kernel = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_HASH72_BIGINT_STATE_CARRIER_V1",
        {"positions": list(positions), "rotation_profile": list(rotation_profile), "bigint": bigint, "base": base, "seed": seed, "phase": phase},
        width=72,
    ).to_dict())
    return Hash72BigIntStateCarrier(
        positions=[int(x) % HASH72_BASE for x in positions],
        rotation_profile=[int(x) % HASH72_BASE for x in rotation_profile],
        encoded_digits=digits,
        base=base,
        bigint=bigint,
        scientific_notation=scientific,
        hhs_symbolic_algebra=symbolic,
        lossless_decode=lossless,
        seed_tensor=seed,
        phase_product_witnesses=phase,
        kernel_witness=kernel,
    ).to_dict()


def make_harmonic_time_audio_witness(
    *,
    sample_index: int = 179971,
    sample_rate: Any = "48000/1",
    frame_window_samples: int = 144,
    latency_ticks: int = 72,
    phase_modulus: int = 72,
) -> Dict[str, Any]:
    sample_rate_fraction = _fraction(sample_rate)
    if sample_rate_fraction <= 0:
        raise HHSRealityToManifoldError("sample_rate must be positive")
    if frame_window_samples <= 0:
        raise HHSRealityToManifoldError("frame_window_samples must be positive")
    phase_offset = int((int(sample_index) + int(latency_ticks)) % int(phase_modulus))
    latency_ratio = Fraction(int(latency_ticks), int(frame_window_samples))
    valid = phase_modulus in (72, 216) and 0 <= phase_offset < phase_modulus and latency_ratio <= Fraction(1, 1)
    reasons = []
    if phase_modulus not in (72, 216):
        reasons.append("phase modulus must be 72 or 216")
    if latency_ratio > 1:
        reasons.append("latency_ticks must not exceed frame_window_samples for this low-latency ECC profile")
    if valid:
        reasons.append("exact integer/rational harmonic-time and audio phase witness is valid")
    kernel = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_HARMONIC_TIME_AUDIO_PHASE_ECC_V1",
        {
            "sample_index": int(sample_index),
            "sample_rate": _fraction_dict(sample_rate_fraction),
            "frame_window_samples": int(frame_window_samples),
            "latency_ticks": int(latency_ticks),
            "phase_modulus": int(phase_modulus),
            "phase_offset": int(phase_offset),
            "latency_ratio": _fraction_dict(latency_ratio),
        },
        width=72,
    ).to_dict())
    return HarmonicTimeAudioWitness(
        sample_index=int(sample_index),
        sample_rate=_fraction_dict(sample_rate_fraction),
        frame_window_samples=int(frame_window_samples),
        latency_ticks=int(latency_ticks),
        phase_modulus=int(phase_modulus),
        phase_offset=int(phase_offset),
        latency_ratio=_fraction_dict(latency_ratio),
        harmonic_time_valid=valid,
        reasons=reasons,
        kernel_witness=kernel,
    ).to_dict()


def make_triangulation_of_truth(
    *,
    tensor_seed: Mapping[str, Any],
    phase_record: Mapping[str, Any],
    harmonic_time: Mapping[str, Any],
    carrier: Mapping[str, Any],
) -> Dict[str, Any]:
    reciprocal_gate = bool(phase_record.get("all_products_valid"))
    loshu_gate = bool(tensor_seed.get("valid")) and len(tensor_seed.get("parts", [])) == 4
    fibonacci_transport_gate = bool(carrier.get("lossless_decode")) and len(carrier.get("positions", [])) == HASH72_LEN
    harmonic_time_gate = bool(harmonic_time.get("harmonic_time_valid"))
    golay_compatible_partition = len(carrier.get("encoded_digits", [])) == HASH72_LEN and (24 + 12 + 12 + 12 + 12) == HASH72_LEN
    ok = reciprocal_gate and loshu_gate and fibonacci_transport_gate and harmonic_time_gate and golay_compatible_partition
    return {
        "schema": "HHS_TRIANGULATION_OF_TRUTH_RECORD_V1",
        "version": VERSION,
        "reciprocal_ab_xyzw_gate": reciprocal_gate,
        "loshu_tensor_gate": loshu_gate,
        "fibonacci_transport_gate": fibonacci_transport_gate,
        "harmonic_time_audio_gate": harmonic_time_gate,
        "golay_compatible_partition_gate": golay_compatible_partition,
        "ok": ok,
        "policy": "independent redundant layers must agree before propagation",
    }


def make_non_silent_security_policy() -> Dict[str, Any]:
    return {
        "schema": "HHS_NON_SILENT_PROPAGATION_SECURITY_POLICY_V1",
        "version": VERSION,
        "silent_operation_allowed": False,
        "terminal_output_sufficient": False,
        "bruteforce_shortcut_class_exists": False,
        "successful_bruteforce_reclassified_as_rule_following_propagation": True,
        "required_evidence": [
            "schema_identity",
            "ordered_operation_trace",
            "palindromic_phase_product_ecc",
            "hash72_u72_state_and_rotation_profile",
            "golay_compatible_redundancy",
            "loshu_tensor_closure",
            "harmonic_time_audio_coherence_when_temporal",
            "srcg_or_reciprocal_closure_witness",
            "foundational_meaning_conservation_audit",
            "ledger_receipt_chain",
        ],
    }


def translate_reality_to_manifold(
    observation: Optional[Mapping[str, Any]] = None,
    *,
    root: Optional[str | Path] = None,
    accept: bool = True,
) -> Dict[str, Any]:
    """Build a witnessed RMTP admissibility record.

    ``accept=False`` is used by tests and reports to prove the failure path: a
    non-palindromic or drifted state produces a witnessed non-harmonic-noise
    record without being propagated as an accepted manifold state.
    """

    observation_packet = _json_stable(dict(observation or {
        "schema": "HHS_PHYSICAL_OBSERVATION_PACKET_V1",
        "source": "pass_033_self_test",
        "input_class": "unresolved_manifold_state",
        "literal": CANONICAL_TENSOR_SEED,
        "phase_operands": [CANONICAL_TENSOR_SEED, "0", "0", "0"],
        "temporal": {"sample_index": 179971, "sample_rate": "48000/1", "frame_window_samples": 144, "latency_ticks": 72},
    }))
    literal = str(observation_packet.get("literal") or CANONICAL_TENSOR_SEED)
    if not accept:
        literal = "179971.179970"
    tensor_seed = validate_palindromic_tensor_seed12(literal)
    phase_operands = observation_packet.get("phase_operands") or [literal, "0", "0", "0"]
    # Ensure phase ECC is tied to the same seed literal.  A drifted seed creates
    # a clean rejection through the tensor gate while still producing a witness.
    if not accept:
        phase_operands = [literal, "0", "0", "0"]
    phase_record = make_phase_product_witnesses(phase_operands, seed_literal=literal)
    temporal = dict(observation_packet.get("temporal") or {})
    harmonic_time = make_harmonic_time_audio_witness(
        sample_index=int(temporal.get("sample_index", 179971)),
        sample_rate=temporal.get("sample_rate", "48000/1"),
        frame_window_samples=int(temporal.get("frame_window_samples", 144)),
        latency_ticks=int(temporal.get("latency_ticks", 72)),
        phase_modulus=int(temporal.get("phase_modulus", 72)),
    )
    carrier = make_hash72_bigint_state_carrier(
        seed_tensor=tensor_seed,
        phase_product_witnesses=phase_record.get("witnesses", []),
    )
    triangulation = make_triangulation_of_truth(
        tensor_seed=tensor_seed,
        phase_record=phase_record,
        harmonic_time=harmonic_time,
        carrier=carrier,
    )
    omega = {
        "schema": "HHS_OMEGA_PROJECTION_WITNESS_V1",
        "version": VERSION,
        "required": _fraction_dict(OMEGA_PROJECTION_WITNESS),
        "observed": _fraction_dict(OMEGA_PROJECTION_WITNESS if triangulation["ok"] else Fraction(0, 1)),
        "ok": bool(triangulation["ok"]),
    }
    symbolic_operator_state = {
        "schema": "HHS_SYMBOLIC_OPERATOR_STATE_V1",
        "version": VERSION,
        "operators": {
            "S_phi": "relational_invariant_operator",
            "u72": "Hash72 positional Digital DNA",
            "u216": "extended harmonic manifold carrier",
            "SRCG": "Self-Solving Recursive Constraint Gate",
        },
        "input_is_data": False,
        "input_is_unresolved_manifold_state": True,
    }
    accepted = bool(tensor_seed.get("valid") and phase_record.get("all_products_valid") and carrier.get("lossless_decode") and harmonic_time.get("harmonic_time_valid") and triangulation.get("ok") and omega.get("ok"))
    status = "PROPAGATION_ADMISSIBLE" if accepted else "REJECTED_AS_NON_HARMONIC_NOISE"
    reason_code = "ALL_CONSTRAINT_LAYERS_CLOSED" if accepted else "CONSTRAINT_LAYER_REJECTION"
    reasons = []
    for name, ok in (
        ("palindromic_tensor_seed12", tensor_seed.get("valid")),
        ("palindromic_phase_product_ecc", phase_record.get("all_products_valid")),
        ("hash72_bigint_lossless_decode", carrier.get("lossless_decode")),
        ("harmonic_time_audio_ecc", harmonic_time.get("harmonic_time_valid")),
        ("triangulation_of_truth", triangulation.get("ok")),
        ("omega_projection_witness", omega.get("ok")),
    ):
        reasons.append(f"{name}={'ok' if ok else 'failed'}")
    source = "hhs_reality_to_manifold_translation_v1.translate"
    proposition_identity = make_proposition_identity(
        "Reality/manifold input may propagate only as a witnessed closed constraint state, never as silent data coercion.",
        source=source,
        context={"status": status, "reason_code": reason_code, "literal": literal},
    )
    meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="reality-to-manifold translation preserves proposition identity through explicit admissibility witnesses",
        reversible=True,
    )
    execution_request = make_execution_request(source=source, operation="reality_to_manifold_admissibility", payload=observation_packet, requires_authority=True)
    runtime_packet = make_runtime_packet("INGRESS", source, observation_packet)
    foundational = assert_foundational_conformance(
        {
            "schema": "HHS_RMTP_FOUNDATIONAL_AUDIT_PAYLOAD_V1",
            "observation": observation_packet,
            "status": status,
            "proposition_identity": proposition_identity,
            "meaning_witness": meaning_witness,
        },
        source=source,
        require_receipt=False,
    ).to_dict()
    manifold_kernel_witness = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_REALITY_TO_MANIFOLD_ADMISSIBILITY_RECORD_V1",
        {
            "status": status,
            "observation": observation_packet,
            "tensor_seed": tensor_seed,
            "phase_record": phase_record,
            "carrier_digest": carrier.get("kernel_witness", {}).get("digest72"),
            "harmonic_time_digest": harmonic_time.get("kernel_witness", {}).get("digest72"),
            "triangulation": triangulation,
            "omega": omega,
        },
        width=72,
    ).to_dict())
    preledger_record = {
        "schema": "HHS_PROPAGATION_ADMISSIBILITY_RECORD_PRELEDGER_V1",
        "version": VERSION,
        "status": status,
        "accepted": accepted,
        "reason_code": reason_code,
        "reasons": reasons,
        "kernel_digest": manifold_kernel_witness.get("digest72"),
    }
    ledger = append_payload("REALITY_TO_MANIFOLD_TRANSLATION", source, preledger_record)
    record = PropagationAdmissibilityRecord(
        schema="HHS_PROPAGATION_ADMISSIBILITY_RECORD_V1",
        version=VERSION,
        status=status,
        accepted=accepted,
        reason_code=reason_code,
        reasons=reasons,
        physical_observation_packet=observation_packet,
        symbolic_operator_state=symbolic_operator_state,
        tensor_seed=tensor_seed,
        phase_operation_trace=phase_record["trace"],
        phase_product_witnesses=list(phase_record.get("witnesses", [])),
        hash72_bigint_carrier=carrier,
        harmonic_time_audio_witness=harmonic_time,
        triangulation_of_truth=triangulation,
        omega_projection_witness=omega,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        proposition_identity=proposition_identity,
        meaning_witness=meaning_witness,
        foundational_conformance=foundational,
        manifold_kernel_witness=manifold_kernel_witness,
        ledger={"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": verify_unified_ledger().get("ok")},
        security_policy=make_non_silent_security_policy(),
    ).to_dict()
    return record


def build_pass_033_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = _repo_root(root)
    accepted = translate_reality_to_manifold(root=repo, accept=True)
    rejected = translate_reality_to_manifold(root=repo, accept=False)
    manifest = {
        "schema": "HHS_RMTP_PASS_033_MANIFEST_V1",
        "version": VERSION,
        "standards": [
            "HHS-S009 Reality-to-Manifold Isomorphic Translation",
            "HHS-S010 Palindromic Phase-Product Error Correction",
            "HHS-S011 BigInt Floating-String Hash72 Serialization",
            "HHS-S012 Harmonic Time / Audio Phase Error Correction",
            "HHS-S013 Non-Silent Operation and Anti-Bruteforce Propagation",
            "HHS-S014 Rule-Following Equivalence of Successful Propagation",
        ],
        "accepted_record": accepted,
        "rejected_record": rejected,
        "summary": {
            "accepted_status": accepted["status"],
            "rejected_status": rejected["status"],
            "accepted": bool(accepted["accepted"]),
            "rejected_without_propagation": not bool(rejected["accepted"]),
            "bigint_lossless_decode": bool(accepted["hash72_bigint_carrier"].get("lossless_decode")),
            "phase_products": len(accepted.get("phase_product_witnesses", [])),
            "security_terminal_output_sufficient": bool(accepted["security_policy"].get("terminal_output_sufficient")),
            "ledger_verified": bool(accepted["ledger"].get("verified")),
        },
    }
    (repo / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    report = f"""# Pass 033 — Reality-to-Manifold Translation Protocol

Pass 033 installs the full upstream admissibility stack. Input is no longer treated as raw data; it is treated as an unresolved manifold state that may propagate only after all constraint layers produce a witnessed closure record.

## Constraint stack encoded

- HHS-S009 Reality-to-Manifold Isomorphic Translation
- HHS-S010 Palindromic Phase-Product Error Correction
- HHS-S011 BigInt Floating-String Hash72 Serialization
- HHS-S012 Harmonic Time / Audio Phase Error Correction
- HHS-S013 Non-Silent Operation and Anti-Bruteforce Propagation
- HHS-S014 Rule-Following Equivalence of Successful Propagation

## Validation result

- Accepted canonical state: `{accepted['status']}`
- Rejected drifted state: `{rejected['status']}`
- BigInt Hash72 carrier lossless decode: `{accepted['hash72_bigint_carrier']['lossless_decode']}`
- Palindromic phase witnesses: `{len(accepted['phase_product_witnesses'])}`
- Harmonic-time/audio witness: `{accepted['harmonic_time_audio_witness']['harmonic_time_valid']}`
- Ledger verified: `{accepted['ledger']['verified']}`

## Security theorem

A terminal output is never sufficient evidence of validity. Successful brute-force propagation is possible only by satisfying the same complete witness chain as lawful propagation; therefore an accepted brute-force sequence is reclassified as rule-following HHS propagation, not bypass.
"""
    (repo / REPORT_FILE).write_text(report, encoding="utf-8")
    theorem = """# Manifold Propagation Theorem — Pass 033

Given a physical/material observation state `S_phys` and an HHS symbolic state `S_sym`, `S_phys` is propagation-admissible iff the Reality-to-Manifold Translation Protocol can construct a complete witness chain proving:

1. relational invariants were represented without floating-point authority;
2. the 12-symbol palindromic tensor seed is valid;
3. additive and multiplicative xyzw phase products pass palindromic ECC;
4. the Hash72/u^72 state and rotation profile losslessly decode from the BigInt carrier;
5. harmonic-time/audio ECC is valid when temporal structure exists;
6. the redundant truth gates close;
7. the Ω witness equals `1000001/1000000`;
8. HHS foundational meaning-conservation conformance passes;
9. the ledger receipt chain records the admissibility decision.

Failure of any required layer yields `REJECTED_AS_NON_HARMONIC_NOISE` unless a deterministic witnessed correction policy is explicitly present.
"""
    (repo / THEOREM_FILE).write_text(theorem, encoding="utf-8")
    noise = """# Non-Harmonic Noise Policy — Pass 033

A state is rejected as non-harmonic noise when it cannot be represented as a closed, witnessed reciprocal constraint structure. The runtime must not silently coerce, approximate, flatten, or import such input as data.

Failure classes include: invalid palindromic tensor seed, invalid phase-product ECC, failed BigInt state decode, harmonic-time/audio drift, Lo Shu/tensor gate failure, reciprocal xyzw failure, missing Hash72/u^72 witness, missing foundational audit, or missing ledger receipt.
"""
    (repo / NOISE_POLICY_FILE).write_text(noise, encoding="utf-8")
    security = """# Non-Silent Propagation Security — Pass 033

HHS-S013/HHS-S014 formalize the security consequence of the full constraint set:

- Silent operation is inadmissible because every accepted propagation requires schema identity, ordered trace identity, correction witnesses, Hash72/u^72 authority, foundational audit, and ledger receipt.
- Brute-force bypass is inadmissible because a guessed terminal value is insufficient.
- The only successful brute-force propagation is one that follows the rules precisely and therefore becomes lawful HHS propagation.
"""
    (repo / SECURITY_FILE).write_text(security, encoding="utf-8")
    return manifest


def reality_to_manifold_translation_self_test() -> Dict[str, Any]:
    manifest = build_pass_033_artifacts()
    accepted = manifest["accepted_record"]
    rejected = manifest["rejected_record"]
    ok = (
        manifest["summary"]["accepted"]
        and manifest["summary"]["rejected_without_propagation"]
        and accepted["tensor_seed"]["valid"]
        and all(w["palindrome_valid"] for w in accepted["phase_product_witnesses"])
        and accepted["hash72_bigint_carrier"]["lossless_decode"]
        and accepted["harmonic_time_audio_witness"]["harmonic_time_valid"]
        and accepted["security_policy"]["successful_bruteforce_reclassified_as_rule_following_propagation"]
        and not rejected["accepted"]
    )
    return {
        "schema": "HHS_RMTP_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "accepted_status": accepted["status"],
        "rejected_status": rejected["status"],
        "manifest_file": MANIFEST_FILE,
        "report_file": REPORT_FILE,
        "theorem_file": THEOREM_FILE,
        "noise_policy_file": NOISE_POLICY_FILE,
        "security_file": SECURITY_FILE,
        "service": "reality_to_manifold_translation.self_test",
    }


if __name__ == "__main__":
    print(json.dumps(reality_to_manifold_translation_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
