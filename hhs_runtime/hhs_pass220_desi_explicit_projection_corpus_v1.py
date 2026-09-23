"""Pass 220 I040: explicit DESI observation projection and fail-closed corpus.

I040 closes the boundary intentionally left open by I038 and I039.

Public DESI observables are not implicitly renamed into A/B/p/q/etc. Instead the
projection is explicit and typed against the already implemented I023
relativistic output surfaces:

    z_eff
        -> redshift target z
        -> one_plus_z = 1 + z

    D_H/r_d
        -> hubble_distance_over_sound_horizon
        -> (H * r_d / c0) = 1 / (D_H/r_d)

    D_M/r_d
        -> transverse_comoving_distance_over_sound_horizon
        -> D_M/D_H = (D_M/r_d)/(D_H/r_d)

and the exact isotropic BAO identity is retained as

    (D_V/r_d)^3
        = z * (D_M/r_d)^2 * (D_H/r_d).

All released decimal source values continue through the I038 exact decimal,
palindromic IEEE, exact dyadic-residue, 5,184-character BigInt and I037 bundle
paths. The resulting observation projection is then bound to the I039 shared
quantum-geometric root.

The three -,0,+ 24D copies receive the same complete observation projection and
the same exact carrier receipts. No copy is a partial slice.

Corpus execution is fail-closed. Every row returns either CLOSE or REJECT with
a deterministic rejection code. Rows are never averaged together to hide a
constraint failure. No likelihood, MCMC, probability weighting, floating
arithmetic, or parameter refit is used.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_24d_mandatory_constraint_spacetime_v1 import (
    TRINARY_LABELS,
    constructor_bundle_root,
)
from hhs_runtime.hhs_pass220_desi_lane5_parallel_exact_egress_v1 import (
    DESI_DR2_LYA_PUBLIC_FIXTURE,
    DESI_NUMERIC_FIELDS,
    build_parallel_observation_carrier,
    parse_exact_decimal,
    validate_parallel_observation_carrier,
)
from hhs_runtime.hhs_pass220_quantum_geometric_unification_closure_v1 import (
    quantum_geometric_unification_witness,
)

SCHEMA = "HHS_PASS_220_I040_DESI_EXPLICIT_PROJECTION_CORPUS_V1"
VERSION = "1.0.0-checkpoint.40"
PROFILE = "PASS220-I040-DESI-EXPLICIT-PROJECTION-CORPUS-v1"
PROJECTION_SCHEMA = "HHS_PASS_220_I040_DESI_EXPLICIT_PROJECTION_V1"
CORPUS_SCHEMA = "HHS_PASS_220_I040_DESI_FAIL_CLOSED_CORPUS_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I040_DESI_PROJECTION_WITNESS_V1"

PUBLIC_ROW_ID = "DESI_DR2_LYA_BAO_Z2P33"

OBSERVATION_MAP_RULES: Tuple[str, ...] = (
    "z_eff -> I023.redshift_target",
    "one_plus_z = 1 + z_eff",
    "D_H_over_r_d -> I023.hubble_distance_over_sound_horizon",
    "H_times_r_d_over_c0 = 1 / (D_H_over_r_d)",
    "D_M_over_r_d -> I023.transverse_comoving_distance_over_sound_horizon",
    "D_M_over_D_H = (D_M_over_r_d) / (D_H_over_r_d)",
    "(D_V_over_r_d)^3 = z_eff * (D_M_over_r_d)^2 * (D_H_over_r_d)",
)

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "DESI_TO_HHS_OBSERVATION_MAP_IS_EXPLICIT",
    "NO_IMPLICIT_A_B_P_P_Q_BINDING",
    "RELEASED_DECIMALS_REMAIN_EXACT_RATIONAL_SOURCES",
    "I038_PARALLEL_IEEE_BIGINT_CARRIERS_PRESERVED",
    "I039_SHARED_UNIFICATION_ROOT_BOUND",
    "I037_MANDATORY_EQUATION_PROOF_ROOT_BOUND",
    "THREE_COMPLETE_24D_PHASE_COPIES_RECEIVE_IDENTICAL_OBSERVATION_STATE",
    "EXACT_HUBBLE_DISTANCE_RECIPROCAL_SOLVE",
    "EXACT_ALCOCK_PACZYNSKI_RATIO_SOLVE",
    "EXACT_ISOTROPIC_BAO_CUBE_RELATION",
    "UNCERTAINTY_COMPONENTS_REMAIN_SEPARATE",
    "ROW_FAILURE_IS_NOT_AVERAGED_AWAY",
    "CORPUS_IS_FAIL_CLOSED",
    "BIGINT_WIDTH_5184_PRESERVED",
    "NO_HOST_FLOAT_ARITHMETIC",
    "NO_PROBABILITY_WEIGHTING",
    "NO_LIKELIHOOD_SOLVE",
    "NO_MCMC_SOLVE",
    "NO_PARAMETER_REFIT",
    "NO_COMMUTATIVE_REORDERING_AUTHORIZED",
)


class Pass220I040ProjectionError(ValueError):
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
        raise Pass220I040ProjectionError("fraction record missing fields") from exc
    if (
        isinstance(numerator, bool)
        or not isinstance(numerator, int)
        or isinstance(denominator, bool)
        or not isinstance(denominator, int)
        or denominator <= 0
    ):
        raise Pass220I040ProjectionError("invalid exact fraction record")
    return Fraction(numerator, denominator)


def public_desi_dr2_lya_row() -> Dict[str, str]:
    return {
        "row_id": PUBLIC_ROW_ID,
        **dict(DESI_DR2_LYA_PUBLIC_FIXTURE),
    }


def _require_row(row: Mapping[str, Any]) -> Dict[str, str]:
    if not isinstance(row, Mapping):
        raise Pass220I040ProjectionError("observation row must be a mapping")
    required = (
        "row_id",
        "release_id",
        "official_results_url",
        "official_data_index_url",
        "paper_url",
        *DESI_NUMERIC_FIELDS,
    )
    normalized: Dict[str, str] = {}
    for key in required:
        value = row.get(key)
        if not isinstance(value, str) or not value:
            raise Pass220I040ProjectionError(
                f"observation row missing non-empty string field: {key}"
            )
        normalized[key] = value
    return normalized


def _build_numeric_carriers(row: Mapping[str, str]) -> Dict[str, Dict[str, Any]]:
    return {
        field: build_parallel_observation_carrier(
            observable=field,
            decimal_text=row[field],
            source_release_id=row["release_id"],
        )
        for field in DESI_NUMERIC_FIELDS
    }


def _validate_numeric_carriers(
    carriers: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    if set(carriers) != set(DESI_NUMERIC_FIELDS):
        raise Pass220I040ProjectionError("numeric carrier coverage mismatch")
    return {
        field: validate_parallel_observation_carrier(carriers[field])
        for field in DESI_NUMERIC_FIELDS
    }


def exact_observation_solve(row: Mapping[str, Any]) -> Dict[str, Any]:
    """Solve only declared DESI observational definitions with exact rationals."""
    normalized = _require_row(row)

    z = parse_exact_decimal(normalized["z_eff"])
    dh_over_rd = parse_exact_decimal(normalized["D_H_over_r_d"])
    dm_over_rd = parse_exact_decimal(normalized["D_M_over_r_d"])

    if z < 0:
        raise Pass220I040ProjectionError("z_eff must be nonnegative")
    if dh_over_rd <= 0:
        raise Pass220I040ProjectionError("D_H/r_d must be positive")
    if dm_over_rd <= 0:
        raise Pass220I040ProjectionError("D_M/r_d must be positive")

    one_plus_z = Fraction(1) + z
    h_times_rd_over_c0 = Fraction(1) / dh_over_rd
    dm_over_dh = dm_over_rd / dh_over_rd
    dv_over_rd_cubed = z * dm_over_rd * dm_over_rd * dh_over_rd

    return _receipt({
        "schema": "HHS_PASS_220_I040_EXACT_OBSERVATION_SOLVE_V1",
        "row_id": normalized["row_id"],
        "mapping_rules": OBSERVATION_MAP_RULES,
        "z_eff": _fraction_record(z),
        "one_plus_z": _fraction_record(one_plus_z),
        "D_H_over_r_d": _fraction_record(dh_over_rd),
        "D_M_over_r_d": _fraction_record(dm_over_rd),
        "H_times_r_d_over_c0": _fraction_record(h_times_rd_over_c0),
        "D_M_over_D_H": _fraction_record(dm_over_dh),
        "D_V_over_r_d_cubed": _fraction_record(dv_over_rd_cubed),
        "I023_target_surfaces": {
            "redshift_target": _fraction_record(z),
            "one_plus_z_target": _fraction_record(one_plus_z),
            "hubble_distance_over_sound_horizon": _fraction_record(dh_over_rd),
            "transverse_comoving_distance_over_sound_horizon": _fraction_record(
                dm_over_rd
            ),
        },
        "definition_checks": {
            "one_plus_z": one_plus_z == Fraction(1) + z,
            "hubble_reciprocal": (
                h_times_rd_over_c0 * dh_over_rd == Fraction(1)
            ),
            "alcock_paczynski_ratio": (
                dm_over_dh * dh_over_rd == dm_over_rd
            ),
            "isotropic_bao_cube": (
                dv_over_rd_cubed
                == z * dm_over_rd * dm_over_rd * dh_over_rd
            ),
        },
        "host_float_arithmetic_used": False,
        "probability_used": False,
        "likelihood_used": False,
        "mcmc_used": False,
        "parameter_refit_performed": False,
    })


def _projection_root_payload(
    *,
    normalized_row: Mapping[str, str],
    exact_solve: Mapping[str, Any],
    carrier_receipts: Mapping[str, str],
    i039_root: str,
    i037_root: str,
) -> Dict[str, Any]:
    return {
        "row_id": normalized_row["row_id"],
        "release_id": normalized_row["release_id"],
        "exact_observation_solve_receipt_sha256": exact_solve["receipt_sha256"],
        "carrier_receipts": dict(carrier_receipts),
        "i039_shared_state_root_sha256": i039_root,
        "i037_mandatory_constructor_bundle_root_sha256": i037_root,
        "mapping_rules": OBSERVATION_MAP_RULES,
    }


def build_desi_explicit_projection(row: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = _require_row(row)
    carriers = _build_numeric_carriers(normalized)
    validations = _validate_numeric_carriers(carriers)
    exact_solve = exact_observation_solve(normalized)

    i039 = quantum_geometric_unification_witness()
    if i039.get("ok") is not True:
        raise Pass220I040ProjectionError("I039 unification substrate did not close")
    if i039["result"].get("simultaneous_projection_closure") is not True:
        raise Pass220I040ProjectionError("I039 simultaneous projection closure lost")

    i039_root = i039["shared_state_root_sha256"]
    i037_root = constructor_bundle_root()
    if i039["result"]["i037_bundle_root_sha256"] != i037_root:
        raise Pass220I040ProjectionError("I039/I037 constructor-root mismatch")

    carrier_receipts = {
        field: carriers[field]["receipt_sha256"]
        for field in DESI_NUMERIC_FIELDS
    }
    projection_root_payload = _projection_root_payload(
        normalized_row=normalized,
        exact_solve=exact_solve,
        carrier_receipts=carrier_receipts,
        i039_root=i039_root,
        i037_root=i037_root,
    )
    projection_root = sha256(
        _stable_json(projection_root_payload).encode("utf-8")
    ).hexdigest()

    ieee_residues = {
        field: carriers[field]["decimal_minus_ieee_exact_residue"]
        for field in DESI_NUMERIC_FIELDS
    }

    phase_copies = tuple(
        _receipt({
            "schema": "HHS_PASS_220_I040_PHASE_COPY_BINDING_V1",
            "trinary_phase": phase,
            "full_information_copy": True,
            "partial_information_slice": False,
            "projection_root_sha256": projection_root,
            "i039_shared_state_root_sha256": i039_root,
            "i037_mandatory_constructor_bundle_root_sha256": i037_root,
            "exact_observation_solve_receipt_sha256": exact_solve[
                "receipt_sha256"
            ],
            "observation_carrier_receipts": carrier_receipts,
            "exact_ieee_residues": ieee_residues,
            "bigint_5184_preserved_for_every_numeric_field": all(
                validations[field]["bigint_5184_characters"] == 5184
                for field in DESI_NUMERIC_FIELDS
            ),
            "normalization_erases_observation": False,
            "normalization_erases_ieee_residue": False,
            "normalization_erases_provenance": False,
        })
        for phase in TRINARY_LABELS
    )

    definition_checks = exact_solve["definition_checks"]
    uncertainty_components = {
        "D_H": {
            "stat": carriers["D_H_stat_sigma"]["exact_decimal_rational"],
            "sys": carriers["D_H_sys_sigma"]["exact_decimal_rational"],
        },
        "D_M": {
            "stat": carriers["D_M_stat_sigma"]["exact_decimal_rational"],
            "sys": carriers["D_M_sys_sigma"]["exact_decimal_rational"],
        },
    }

    close = all((
        all(definition_checks.values()),
        all(validation["ok"] for validation in validations.values()),
        all(
            validation["bigint_5184_characters"] == 5184
            for validation in validations.values()
        ),
        len(phase_copies) == 3,
        all(copy["full_information_copy"] for copy in phase_copies),
        len({copy["projection_root_sha256"] for copy in phase_copies}) == 1,
        len({
            copy["i039_shared_state_root_sha256"]
            for copy in phase_copies
        }) == 1,
        i039["result"]["delta_e"] == 0,
        i039["result"]["psi"] == 0,
        i039["result"]["omega"] is True,
        i039["palindromic_return_gate_closed"] is True,
    ))

    return _receipt({
        "schema": PROJECTION_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "row": normalized,
        "mapping_kind": "EXPLICIT_DESI_TO_I023_RELATIONAL_SURFACE",
        "mapping_rules": OBSERVATION_MAP_RULES,
        "implicit_A_B_P_p_q_binding": False,
        "exact_observation_solve": exact_solve,
        "numeric_carriers": carriers,
        "numeric_carrier_validations": validations,
        "uncertainty_components": uncertainty_components,
        "uncertainty_components_combined": False,
        "i039_unification_witness_receipt_sha256": i039["receipt_sha256"],
        "i039_shared_state_root_sha256": i039_root,
        "i037_mandatory_constructor_bundle_root_sha256": i037_root,
        "projection_root_payload": projection_root_payload,
        "projection_root_sha256": projection_root,
        "phase_copies": phase_copies,
        "u_data_predicate": {
            "i039_unification_substrate_closed": i039["ok"],
            "explicit_projection_definitions_closed": all(
                definition_checks.values()
            ),
            "all_parallel_carriers_valid": all(
                validation["ok"] for validation in validations.values()
            ),
            "all_bigint_widths_5184": all(
                validation["bigint_5184_characters"] == 5184
                for validation in validations.values()
            ),
            "all_three_phase_copies_full": all(
                copy["full_information_copy"] for copy in phase_copies
            ),
            "palindromic_return_gate_closed": i039[
                "palindromic_return_gate_closed"
            ],
            "delta_e_zero": i039["result"]["delta_e"] == 0,
            "psi_zero": i039["result"]["psi"] == 0,
            "omega_true": i039["result"]["omega"] is True,
            "close": close,
        },
        "status": "CLOSE" if close else "REJECT",
        "host_float_arithmetic_used": False,
        "probability_weighting_used": False,
        "likelihood_used": False,
        "mcmc_used": False,
        "parameter_refit_performed": False,
        "row_averaging_used": False,
        "commutative_reordering_authorized": False,
        "canonical_service": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "direct_canonical_persistence_authority": False,
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
    })


def validate_desi_explicit_projection(
    projection: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(projection, Mapping):
        raise Pass220I040ProjectionError("projection must be a mapping")
    if projection.get("schema") != PROJECTION_SCHEMA:
        raise Pass220I040ProjectionError("projection schema mismatch")
    if not _receipt_matches(projection):
        raise Pass220I040ProjectionError("projection receipt mismatch")

    expected = build_desi_explicit_projection(projection["row"])
    if projection != expected:
        raise Pass220I040ProjectionError("projection drift")

    exact_solve = projection["exact_observation_solve"]
    if not all(exact_solve["definition_checks"].values()):
        raise Pass220I040ProjectionError("exact observation definition failed")

    # Re-evaluate the core exact identities from serialized records.
    z = _fraction_from_record(exact_solve["z_eff"])
    one_plus_z = _fraction_from_record(exact_solve["one_plus_z"])
    dh = _fraction_from_record(exact_solve["D_H_over_r_d"])
    dm = _fraction_from_record(exact_solve["D_M_over_r_d"])
    hrd_over_c = _fraction_from_record(exact_solve["H_times_r_d_over_c0"])
    ap = _fraction_from_record(exact_solve["D_M_over_D_H"])
    dv3 = _fraction_from_record(exact_solve["D_V_over_r_d_cubed"])

    if one_plus_z != Fraction(1) + z:
        raise Pass220I040ProjectionError("one_plus_z closure failed")
    if hrd_over_c * dh != Fraction(1):
        raise Pass220I040ProjectionError("H*r_d/c reciprocal closure failed")
    if ap * dh != dm:
        raise Pass220I040ProjectionError("AP ratio closure failed")
    if dv3 != z * dm * dm * dh:
        raise Pass220I040ProjectionError("D_V cube closure failed")

    if tuple(projection.get("mapping_rules", ())) != OBSERVATION_MAP_RULES:
        raise Pass220I040ProjectionError("observation map rules drift")
    if projection.get("implicit_A_B_P_p_q_binding") is not False:
        raise Pass220I040ProjectionError("implicit native-variable mapping forbidden")
    if projection.get("status") != "CLOSE":
        raise Pass220I040ProjectionError("projection did not close")
    if projection["u_data_predicate"].get("close") is not True:
        raise Pass220I040ProjectionError("U_data predicate did not close")

    phase_copies = tuple(projection.get("phase_copies", ()))
    if tuple(copy["trinary_phase"] for copy in phase_copies) != TRINARY_LABELS:
        raise Pass220I040ProjectionError("trinary phase-copy order mismatch")
    if len({
        copy["projection_root_sha256"]
        for copy in phase_copies
    }) != 1:
        raise Pass220I040ProjectionError("phase copies do not share projection root")
    if not all(
        copy["bigint_5184_preserved_for_every_numeric_field"]
        and copy["normalization_erases_observation"] is False
        and copy["normalization_erases_ieee_residue"] is False
        and copy["normalization_erases_provenance"] is False
        for copy in phase_copies
    ):
        raise Pass220I040ProjectionError("phase-copy information loss")

    for field in (
        "host_float_arithmetic_used",
        "probability_weighting_used",
        "likelihood_used",
        "mcmc_used",
        "parameter_refit_performed",
        "row_averaging_used",
        "commutative_reordering_authorized",
        "canonical_service",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "direct_canonical_persistence_authority",
    ):
        if projection.get(field) is not False:
            raise Pass220I040ProjectionError(f"forbidden path/escalation: {field}")

    return {
        "ok": True,
        "status": "CLOSE",
        "row_id": projection["row"]["row_id"],
        "projection_root_sha256": projection["projection_root_sha256"],
        "i039_shared_state_root_sha256": projection[
            "i039_shared_state_root_sha256"
        ],
        "z_eff": exact_solve["z_eff"],
        "one_plus_z": exact_solve["one_plus_z"],
        "D_H_over_r_d": exact_solve["D_H_over_r_d"],
        "D_M_over_r_d": exact_solve["D_M_over_r_d"],
        "H_times_r_d_over_c0": exact_solve["H_times_r_d_over_c0"],
        "D_M_over_D_H": exact_solve["D_M_over_D_H"],
        "D_V_over_r_d_cubed": exact_solve["D_V_over_r_d_cubed"],
        "phase_copy_count": len(phase_copies),
        "numeric_carrier_count": len(DESI_NUMERIC_FIELDS),
        "bigint_5184_preserved": True,
        "u_data_close": True,
    }


def run_fail_closed_desi_corpus(
    rows: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise Pass220I040ProjectionError("rows must be a non-string sequence")
    if not rows:
        raise Pass220I040ProjectionError("corpus must contain at least one row")

    row_results = []
    for index, row in enumerate(rows):
        row_id = None
        if isinstance(row, Mapping):
            raw_row_id = row.get("row_id")
            if isinstance(raw_row_id, str) and raw_row_id:
                row_id = raw_row_id
        if row_id is None:
            row_id = f"ROW_{index:06d}"

        try:
            projection = build_desi_explicit_projection(row)
            validation = validate_desi_explicit_projection(projection)
            row_results.append(_receipt({
                "schema": "HHS_PASS_220_I040_CORPUS_ROW_RESULT_V1",
                "index": index,
                "row_id": row_id,
                "status": "CLOSE",
                "rejection_code": None,
                "projection_receipt_sha256": projection["receipt_sha256"],
                "projection_root_sha256": projection["projection_root_sha256"],
                "validation": validation,
            }))
        except Exception as exc:
            row_results.append(_receipt({
                "schema": "HHS_PASS_220_I040_CORPUS_ROW_RESULT_V1",
                "index": index,
                "row_id": row_id,
                "status": "REJECT",
                "rejection_code": "REJECT_I040_EXPLICIT_PROJECTION_CLOSURE",
                "projection_receipt_sha256": None,
                "projection_root_sha256": None,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }))

    close_count = sum(result["status"] == "CLOSE" for result in row_results)
    reject_count = len(row_results) - close_count
    corpus_close = reject_count == 0

    return _receipt({
        "schema": CORPUS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "row_count": len(row_results),
        "close_count": close_count,
        "reject_count": reject_count,
        "row_results": tuple(row_results),
        "status": "CLOSE" if corpus_close else "REJECT",
        "corpus_close": corpus_close,
        "row_failure_is_averaged_away": False,
        "row_failure_invalidates_corpus": True,
        "host_float_arithmetic_used": False,
        "probability_weighting_used": False,
        "likelihood_used": False,
        "mcmc_used": False,
        "parameter_refit_performed": False,
        "canonical_admission_authority": False,
    })


def build_public_desi_projection_witness() -> Dict[str, Any]:
    row = public_desi_dr2_lya_row()
    projection = build_desi_explicit_projection(row)
    validation = validate_desi_explicit_projection(projection)
    corpus = run_fail_closed_desi_corpus((row,))

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": (
            validation["ok"]
            and corpus["corpus_close"]
            and corpus["row_count"] == 1
        ),
        "projection_receipt_sha256": projection["receipt_sha256"],
        "projection_root_sha256": projection["projection_root_sha256"],
        "i039_shared_state_root_sha256": projection[
            "i039_shared_state_root_sha256"
        ],
        "validation": validation,
        "corpus_receipt_sha256": corpus["receipt_sha256"],
        "corpus_status": corpus["status"],
        "mapping_rules": OBSERVATION_MAP_RULES,
        "canonical_admission_authority": False,
    })


def desi_explicit_projection_corpus_self_test() -> Dict[str, Any]:
    return build_public_desi_projection_witness()
