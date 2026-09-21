"""Pass 220 I020: exact RNA-triplet/operation64, C4 dyadic, and G41 radical proof.

This proof layer closes the three constructive correspondences left explicit by
I019:

1. ordered Digital-DNA triplets over {x,y,z,w} form 4^3 = 64 states and map
   bijectively, without loss of symbol order, onto the inherited operation64
   address pair (left_basis8,right_basis8) with operation64=8*left+right;
2. the I011 quarter-phase carrier gives the typed dyadic projection
   x_D=u^18, y_D=u^54=x_D^-1, hence x_D^3=y_D and x_D^4=1_D;
3. the exact Genesis tensor differential
   sqrt(4^3*3^4 - 4^3/3^4) = 32*sqrt(410)/9
   exposes the prime factor 41, and the 41 canonical I014 reciprocal classes
   map constructively and bijectively to Z_41.

The module is read-only proof infrastructure. It does not widen VM81, Hash72,
Hash216, persistence, receipt, or floating-point authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_g41_sudoku_fingerprint_algebra_v1 import (
    enumerate_fingerprint_classes,
)
from hhs_runtime.hhs_pass220_mobius_quarter_phase_v1 import (
    PHASE_MODULUS,
    PHASE_POSITIONS,
    QUARTER_PHASE,
    mobius_matrix_power4,
)
from hhs_runtime.hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1 import (
    coordinate_phase_lock_witness,
    palindromic_precision_lanes,
)

SCHEMA = "HHS_PASS_220_RNA_OPERATION64_C4_G41_RADICAL_PROOF_V1"
VERSION = "1.0.0-checkpoint.20"
PROFILE = "PASS220-I020-RNA-OP64-C4-G41-RADICAL-PROOF-v1"

DNA_ALPHABET: Tuple[str, ...] = ("x", "y", "z", "w")
DNA_CODE: Dict[str, int] = {symbol: index for index, symbol in enumerate(DNA_ALPHABET)}
G41_MODULUS = 41
LO_SHU_RECIPROCAL_CONSTANT = 10
RADICAL_COEFFICIENT = 32
RADICAL_DENOMINATOR = 9
RADICAL_SQUAREFREE = 410


class Pass220I020ProofError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I020ProofError(f"{name} must be an exact integer")
    return value


def encode_rna_triplet_operation64(
    triplet: Sequence[str],
) -> Dict[str, Any]:
    """Encode one ordered x/y/z/w triplet into the inherited 8x8 operation64.

    Three base-4 symbols are six exact bits. Splitting those six bits 3|3 gives
    the inherited left_basis8/right_basis8 address without losing triplet
    order. This is an address/identity codec; it does not commute or scalarize
    ordered phase products.
    """
    values = tuple(triplet)
    if len(values) != 3 or any(symbol not in DNA_CODE for symbol in values):
        raise Pass220I020ProofError(
            "RNA triplet must contain exactly three x/y/z/w symbols"
        )
    digits = tuple(DNA_CODE[symbol] for symbol in values)
    operation64 = 16 * digits[0] + 4 * digits[1] + digits[2]
    left_basis8, right_basis8 = divmod(operation64, 8)
    if 8 * left_basis8 + right_basis8 != operation64:
        raise AssertionError("operation64 split identity failed")
    return {
        "triplet": values,
        "base4_digits": digits,
        "operation64": operation64,
        "left_basis8": left_basis8,
        "right_basis8": right_basis8,
        "binary6": format(operation64, "06b"),
        "split_3_3": (
            format(left_basis8, "03b"),
            format(right_basis8, "03b"),
        ),
    }


def decode_operation64_rna_triplet(operation64: int) -> Tuple[str, str, str]:
    n = _exact_int(operation64, name="operation64")
    if not 0 <= n < 64:
        raise Pass220I020ProofError("operation64 must lie in 0..63")
    d0, remainder = divmod(n, 16)
    d1, d2 = divmod(remainder, 4)
    return DNA_ALPHABET[d0], DNA_ALPHABET[d1], DNA_ALPHABET[d2]


def rna_operation64_bijection_witness() -> Dict[str, Any]:
    records = []
    addresses = set()
    pairs = set()
    for left in DNA_ALPHABET:
        for middle in DNA_ALPHABET:
            for right in DNA_ALPHABET:
                triplet = (left, middle, right)
                encoded = encode_rna_triplet_operation64(triplet)
                if decode_operation64_rna_triplet(encoded["operation64"]) != triplet:
                    raise Pass220I020ProofError(
                        "RNA triplet/operation64 inverse failed"
                    )
                records.append(encoded)
                addresses.add(encoded["operation64"])
                pairs.add((encoded["left_basis8"], encoded["right_basis8"]))

    expected_addresses = set(range(64))
    expected_pairs = {(left, right) for left in range(8) for right in range(8)}
    if addresses != expected_addresses or pairs != expected_pairs:
        raise Pass220I020ProofError("4^3 <-> 8^2 operation64 bijection failed")

    return _receipt({
        "schema": f"{SCHEMA}_RNA_OPERATION64_BIJECTION",
        "dna_alphabet": DNA_ALPHABET,
        "triplet_cardinality": len(records),
        "four_cubed": 4**3,
        "eight_squared": 8**2,
        "operation64_cardinality": len(addresses),
        "all_operation64_addresses": tuple(sorted(addresses)),
        "all_basis8_pairs_count": len(pairs),
        "roundtrip_all_64": True,
        "ordered_triplet_identity_preserved": True,
        "operation64_formula": "8*left_basis8+right_basis8",
        "base4_formula": "16*d0+4*d1+d2",
        "six_bit_split": "2+2+2 bits -> 3+3 bits",
        "ordered_products_collapsed": False,
        "records": tuple(records),
        "floating_point_authority": False,
    })


def dyadic_c4_cubic_conjugate_witness() -> Dict[str, Any]:
    """Prove x_D^3=y_D on the already-established 72-position C4 projection."""
    if PHASE_MODULUS != 72 or QUARTER_PHASE != 18:
        raise Pass220I020ProofError("inherited I011 quarter-phase geometry drift")
    if tuple(PHASE_POSITIONS) != (0, 18, 36, 54, 72):
        raise Pass220I020ProofError("inherited I011 phase positions drift")

    x_d = QUARTER_PHASE
    y_d = (-QUARTER_PHASE) % PHASE_MODULUS
    x_d_cubed = (3 * x_d) % PHASE_MODULUS
    x_d_fourth = (4 * x_d) % PHASE_MODULUS
    inverse_closure = (x_d + y_d) % PHASE_MODULUS
    matrix = mobius_matrix_power4()

    checks = {
        "x_D_is_u18": x_d == 18,
        "y_D_is_u54": y_d == 54,
        "x_D_cubed_equals_y_D": x_d_cubed == y_d,
        "x_D_fourth_equals_1_D": x_d_fourth == 0,
        "x_D_times_y_D_equals_1_D": inverse_closure == 0,
        "mobius_projective_C4": bool(matrix["projective_identity"]),
    }
    if not all(checks.values()):
        raise Pass220I020ProofError("dyadic C4 cubic conjugate proof failed")

    return _receipt({
        "schema": f"{SCHEMA}_DYADIC_C4_CUBIC_CONJUGATE",
        "phase_modulus": PHASE_MODULUS,
        "quarter_phase": QUARTER_PHASE,
        "x_D": {"symbol": "u^18", "phase_index": x_d},
        "y_D": {"symbol": "u^54", "phase_index": y_d},
        "x_D_cubed": {"symbol": "(u^18)^3=u^54", "phase_index": x_d_cubed},
        "x_D_fourth": {"symbol": "(u^18)^4=u^72=1_D", "phase_index": x_d_fourth},
        "inverse_closure": {"symbol": "u^18*u^54=u^72=1_D", "phase_index": inverse_closure},
        "checks": checks,
        "projection_law": "x_D:=u^18; y_D:=x_D^-1=u^54",
        "braid_surface_replaced": False,
        "braid_surface_required_for_this_projection": False,
        "floating_point_authority": False,
    })


def genesis_radical_witness(
    *,
    a2: int = 1,
    b2: int = 2,
    c2: int = 3,
    p2: int = 3,
    p4: int = 9,
    q_minus_p: int = 2,
) -> Dict[str, Any]:
    values = {
        "a2": _exact_int(a2, name="a2"),
        "b2": _exact_int(b2, name="b2"),
        "c2": _exact_int(c2, name="c2"),
        "p2": _exact_int(p2, name="p2"),
        "p4": _exact_int(p4, name="p4"),
        "q_minus_p": _exact_int(q_minus_p, name="q_minus_p"),
    }
    if values != {
        "a2": 1,
        "b2": 2,
        "c2": 3,
        "p2": 3,
        "p4": 9,
        "q_minus_p": 2,
    }:
        raise Pass220I020ProofError(
            "I020 radical proof is the canonical Genesis projection only"
        )

    exponent_macro_4 = values["p4"] // values["c2"]
    exponent_macro_3 = values["b2"] * values["q_minus_p"]
    exponent_micro_4 = (values["c2"] ** 2) // values["p2"]
    exponent_micro_3 = values["b2"] + values["c2"] - values["a2"]

    macro = (
        (values["b2"] ** 2) ** exponent_macro_4
        * (values["a2"] + values["b2"]) ** exponent_macro_3
    )
    micro = Fraction(
        (values["c2"] + values["a2"]) ** exponent_micro_4,
        (values["a2"] + values["b2"]) ** exponent_micro_3,
    )
    differential = Fraction(macro, 1) - micro
    radical_square = Fraction(
        RADICAL_COEFFICIENT**2 * RADICAL_SQUAREFREE,
        RADICAL_DENOMINATOR**2,
    )

    checks = {
        "macro_is_4_cubed_times_3_fourth": macro == 4**3 * 3**4 == 5184,
        "micro_is_4_cubed_over_3_fourth": micro == Fraction(4**3, 3**4),
        "differential_exact": differential == Fraction(419840, 81),
        "radical_square_exact": radical_square == differential,
        "radicand_is_10_times_41": RADICAL_SQUAREFREE == 10 * 41,
        "coefficient_is_64_over_2": RADICAL_COEFFICIENT == 64 // 2,
        "denominator_is_lo_shu_boundary": RADICAL_DENOMINATOR == 9,
    }
    if not all(checks.values()):
        raise Pass220I020ProofError("Genesis radical identity failed")

    return _receipt({
        "schema": f"{SCHEMA}_GENESIS_RADICAL",
        "genesis": values,
        "macro": macro,
        "micro": (micro.numerator, micro.denominator),
        "differential": (differential.numerator, differential.denominator),
        "radical_normal_form": "32*sqrt(410)/9",
        "radical_coefficient": RADICAL_COEFFICIENT,
        "radical_squarefree": RADICAL_SQUAREFREE,
        "radical_denominator": RADICAL_DENOMINATOR,
        "squarefree_factorization": ((2, 1), (5, 1), (41, 1)),
        "lo_shu_reciprocal_constant": LO_SHU_RECIPROCAL_CONSTANT,
        "g41_factor": G41_MODULUS,
        "checks": checks,
        "floating_point_authority": False,
    })


def g41_radical_class_bridge_witness() -> Dict[str, Any]:
    classes = enumerate_fingerprint_classes()
    if len(classes) != G41_MODULUS:
        raise Pass220I020ProofError("I014 no longer exposes exactly 41 classes")

    mappings = []
    residues = set()
    canonical_keys = set()
    for record in classes:
        class_id = int(record["class_id"])
        residue = class_id % G41_MODULUS
        recovered_class_id = G41_MODULUS if residue == 0 else residue
        if recovered_class_id != class_id:
            raise Pass220I020ProofError("G41 class/residue inverse failed")
        key = tuple(record["canonical_key"])
        if key in canonical_keys:
            raise Pass220I020ProofError("I014 canonical class key duplicated")
        canonical_keys.add(key)
        residues.add(residue)
        mappings.append({
            "class_id": class_id,
            "g41_residue": residue,
            "recovered_class_id": recovered_class_id,
            "fixed_center": bool(record["fixed_center"]),
            "canonical_key": key,
        })

    if residues != set(range(G41_MODULUS)):
        raise Pass220I020ProofError("I014 classes do not bijectively cover Z_41")

    radical = genesis_radical_witness()
    checks = {
        "class_count_41": len(classes) == 41,
        "residue_bijection_Z41": len(residues) == 41,
        "center_class_maps_to_zero": mappings[-1]["class_id"] == 41 and mappings[-1]["g41_residue"] == 0,
        "radical_contains_prime41": (41, 1) in radical["squarefree_factorization"],
        "radicand_equals_10_times_class_count": (
            radical["radical_squarefree"]
            == LO_SHU_RECIPROCAL_CONSTANT * len(classes)
        ),
    }
    if not all(checks.values()):
        raise Pass220I020ProofError("G41 radical class bridge failed")

    return _receipt({
        "schema": f"{SCHEMA}_G41_RADICAL_CLASS_BRIDGE",
        "class_count": len(classes),
        "g41_modulus": G41_MODULUS,
        "lo_shu_reciprocal_constant": LO_SHU_RECIPROCAL_CONSTANT,
        "radical_squarefree": RADICAL_SQUAREFREE,
        "constructive_map": "class_id -> class_id mod 41; residue 0 -> class 41",
        "mappings": tuple(mappings),
        "checks": checks,
        "floating_point_authority": False,
    })


def joint_i020_proof_witness() -> Dict[str, Any]:
    codec = rna_operation64_bijection_witness()
    c4 = dyadic_c4_cubic_conjugate_witness()
    radical = genesis_radical_witness()
    g41 = g41_radical_class_bridge_witness()
    i019_coordinates = coordinate_phase_lock_witness()
    i019_precision = palindromic_precision_lanes()

    checks = {
        "rna64_exact": codec["roundtrip_all_64"],
        "operation64_exact": codec["operation64_cardinality"] == 64,
        "c4_cubic_conjugate": c4["checks"]["x_D_cubed_equals_y_D"],
        "radical_exact": radical["checks"]["radical_square_exact"],
        "g41_constructive_bijection": g41["checks"]["residue_bijection_Z41"],
        "i019_5184_coordinate_lock": i019_coordinates["all_coordinate_systems_bijective"],
        "i019_three_precision_lanes": len(i019_precision) == 3,
    }
    if not all(checks.values()):
        raise Pass220I020ProofError("joint I020 theorem failed")

    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "checks": checks,
        "rna_operation64": codec,
        "dyadic_c4": c4,
        "genesis_radical": radical,
        "g41_radical_bridge": g41,
        "i019_coordinate_lock": i019_coordinates,
        "i019_precision_lanes": i019_precision,
        "theorem": (
            "4^3 RNA triplet identity <-> 8^2 operation64 address; "
            "x_D^3=y_D on the I011 C4 projection; "
            "I014 reciprocal classes <-> Z_41 <-> prime-41 radical coordinate"
        ),
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    })


def validate_i020_proof() -> Dict[str, Any]:
    witness = joint_i020_proof_witness()
    return _receipt({
        "schema": f"{SCHEMA}_VALIDATION",
        "version": VERSION,
        "ok": all(witness["checks"].values()),
        "witness_receipt_sha256": witness["receipt_sha256"],
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "floating_point_authority": False,
    })


def i020_self_test() -> Dict[str, Any]:
    return validate_i020_proof()
