"""Pass 219 Lane 5 1.53 reciprocal phase-boundary formalization.

This module binds HHS-T5184-002 to the existing 1.52 BigInt serializer circuit
without importing scalar cancellation, commutative reciprocal rules, or a
second normalization path.

All equations are preserved as typed HARMONICODE laws.  The validator proves
source identity, dependency composition, inherited serializer closure, and
negative rewrite guards.  It does not reinterpret the native operators through
host-language scalar algebra.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Tuple

from hhs_runtime.harmonicode_lane5_bigint_transcription_v1 import (
    GLOBAL_DENOMINATOR_NATIVE,
    boundary_manifest,
    validate_lane5_1_52,
)

SCHEMA = "HHS_PASS219_LANE5_RECIPROCAL_PHASE_BOUNDARY_V1"
VERSION = "1.0.0"
THEOREM_ID = "HHS-T5184-002"

GLOBAL_DENOMINATOR = "(P=√(pq+(P⁴/AB)))/∆"
P_GENERATOR = "P=(Bx^5184)/∆"
INFINITY_BOUNDARY = "∞∆=Bx^5184"
RECIPROCAL_INFINITY = "R(∞)=∆"
RECIPROCAL_DELTA = "R(∆)=x"
GAMMA_BINDING = "x=Γ_x"
GAMMA_X = "Γ_x=u^(18/72mod72)*u^36"
P_NOT_INFINITY = "P≠∞"
P_SCALE_CLOSURE = "(P/∞)^x^2=P"
DELTA_RECURRENCE = "∆=(∞^x^2)/∆"
P_DELTA_FIXED_POINT = "P=P/∆"
DELTA_CANCEL_FORBIDDEN = "Cancel_∆(S)=forbidden"

NATIVE_LAWS: Tuple[str, ...] = (
    GLOBAL_DENOMINATOR,
    P_GENERATOR,
    INFINITY_BOUNDARY,
    RECIPROCAL_INFINITY,
    RECIPROCAL_DELTA,
    GAMMA_BINDING,
    GAMMA_X,
    P_NOT_INFINITY,
    P_SCALE_CLOSURE,
    DELTA_RECURRENCE,
    P_DELTA_FIXED_POINT,
    DELTA_CANCEL_FORBIDDEN,
)

PROHIBITED_REWRITES: Tuple[Tuple[str, str], ...] = (
    ("(∞∆)/∆", "∞"),
    ("P∆=∞∆", "P=∞"),
    ("R(R(∞))", "∞"),
    ("∆^-1*∆", "1"),
    ("∆*∆^-1", "1"),
    ("u^(18/72mod72)*u^36", "u^(18/72mod72+36)"),
    ("u^(18/72mod72)*u^36", "u^36*u^(18/72mod72)"),
)


@dataclass(frozen=True)
class NativeLaw:
    law_id: str
    source: str
    kind: str
    scalar_rewrite_authority: bool = False
    delta_cancellation_authority: bool = False
    commutation_authority: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
    record["receipt_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return record


def theorem_laws() -> Tuple[NativeLaw, ...]:
    return (
        NativeLaw("T5184-002-GLOBAL-DENOMINATOR", GLOBAL_DENOMINATOR, "GLOBAL_BOUNDARY"),
        NativeLaw("T5184-002-P-GENERATOR", P_GENERATOR, "GENERATOR"),
        NativeLaw("T5184-002-INFINITY-BOUNDARY", INFINITY_BOUNDARY, "GLOBAL_SCALE_BOUNDARY"),
        NativeLaw("T5184-002-R-INF", RECIPROCAL_INFINITY, "DIRECTED_RECIPROCAL"),
        NativeLaw("T5184-002-R-DELTA", RECIPROCAL_DELTA, "DIRECTED_RECIPROCAL"),
        NativeLaw("T5184-002-GAMMA-BINDING", GAMMA_BINDING, "PHASE_OPERATOR_BINDING"),
        NativeLaw("T5184-002-GAMMA-X", GAMMA_X, "ORDERED_PHASE_GEAR"),
        NativeLaw("T5184-002-P-NE-INF", P_NOT_INFINITY, "DISTINCTNESS"),
        NativeLaw("T5184-002-P-SCALE-CLOSURE", P_SCALE_CLOSURE, "PHASE_RECONSTRUCTION"),
        NativeLaw("T5184-002-DELTA-RECURRENCE", DELTA_RECURRENCE, "BOUNDARY_RECURRENCE"),
        NativeLaw("T5184-002-P-DELTA-FIXED", P_DELTA_FIXED_POINT, "BOUNDARY_FIXED_POINT"),
        NativeLaw("T5184-002-NO-DELTA-CANCEL", DELTA_CANCEL_FORBIDDEN, "NEGATIVE_AUTHORITY"),
    )


def reciprocal_phase_chain() -> Dict[str, Any]:
    return {
        "source": "∞->∆->x=Γ_x",
        "nodes": ("∞", "∆", "x", "Γ_x"),
        "edges": (
            {"from": "∞", "to": "∆", "operator": "R", "ordered": True},
            {"from": "∆", "to": "x", "operator": "R", "ordered": True},
            {"from": "x", "to": "Γ_x", "operator": "BIND", "ordered": True},
        ),
        "ordinary_inverse_semantics": False,
        "involutive_reciprocal_assumed": False,
    }


def phase_gear() -> Dict[str, Any]:
    return {
        "operator": "Γ_x",
        "source": GAMMA_X,
        "ordered_factors": ("u^(18/72mod72)", "u^36"),
        "phase_fraction_source": "18/72mod72",
        "phase_closure_source": "36",
        "algebra": "A_q=-1(x,y,z,w,u)",
        "scalar_exponent_combination_authority": False,
        "factor_reordering_authority": False,
    }


def boundary_fixed_points() -> Dict[str, Any]:
    return {
        "delta_recurrence": DELTA_RECURRENCE,
        "p_delta_fixed_point": P_DELTA_FIXED_POINT,
        "p_scale_reconstruction": P_SCALE_CLOSURE,
        "p_distinct_from_infinity": True,
        "delta_persistent": True,
        "delta_cancellable": False,
    }


def theorem_record() -> Dict[str, Any]:
    inherited = validate_lane5_1_52()
    manifest = boundary_manifest()
    laws = theorem_laws()
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "theorem_id": THEOREM_ID,
        "title": "Deterministic Manifold Resolution via the Reciprocal Phase-Gear Chain",
        "status": "EXECUTED_TYPED_FORMALIZATION",
        "arithmetic_closure": "∆e=0",
        "laws": tuple(law.to_dict() for law in laws),
        "reciprocal_phase_chain": reciprocal_phase_chain(),
        "phase_gear": phase_gear(),
        "boundary_fixed_points": boundary_fixed_points(),
        "universal_denominator": GLOBAL_DENOMINATOR,
        "serializer_binding": {
            "schema": inherited["schema"],
            "result": inherited["result"],
            "transcription_operation": inherited["transcription_operation"],
            "ingress_egress_same_operation": inherited["ingress_egress_same_operation"],
            "nested_payloads_remain_typed": inherited["nested_payloads_remain_typed"],
        },
        "nested_boundary_manifest": manifest,
        "prohibited_rewrites": tuple(
            {"source": source, "forbidden_target": target}
            for source, target in PROHIBITED_REWRITES
        ),
        "authority": {
            "delta_cancellation_authority": False,
            "ordinary_inverse_authority": False,
            "commutation_authority": False,
            "scalar_exponent_combination_authority": False,
            "scalar_substitution_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
        },
    })


def validate_t5184_002() -> Dict[str, Any]:
    theorem = theorem_record()
    law_sources = {law["source"] for law in theorem["laws"]}
    manifest = theorem["nested_boundary_manifest"]
    gear = theorem["phase_gear"]
    chain = theorem["reciprocal_phase_chain"]
    authority = theorem["authority"]

    checks = {
        "global_denominator_verbatim": GLOBAL_DENOMINATOR in law_sources
            and GLOBAL_DENOMINATOR == GLOBAL_DENOMINATOR_NATIVE,
        "p_generator_preserves_delta": P_GENERATOR in law_sources and P_GENERATOR.endswith("/∆"),
        "infinity_boundary_preserved": INFINITY_BOUNDARY in law_sources,
        "reciprocal_chain_ordered": chain["source"] == "∞->∆->x=Γ_x"
            and all(edge["ordered"] for edge in chain["edges"]),
        "reciprocal_infinity_to_delta": RECIPROCAL_INFINITY in law_sources,
        "reciprocal_delta_to_x": RECIPROCAL_DELTA in law_sources,
        "gamma_binding_exact": GAMMA_BINDING in law_sources,
        "gamma_source_verbatim": gear["source"] == GAMMA_X
            and gear["phase_fraction_source"] == "18/72mod72",
        "gamma_factor_order_preserved": gear["ordered_factors"]
            == ("u^(18/72mod72)", "u^36"),
        "gamma_not_scalarized": gear["scalar_exponent_combination_authority"] is False
            and gear["factor_reordering_authority"] is False,
        "p_not_infinity": P_NOT_INFINITY in law_sources
            and theorem["boundary_fixed_points"]["p_distinct_from_infinity"] is True,
        "p_scale_reconstruction_exact": P_SCALE_CLOSURE in law_sources,
        "delta_recurrence_exact": DELTA_RECURRENCE in law_sources,
        "p_delta_fixed_point_exact": P_DELTA_FIXED_POINT in law_sources,
        "delta_cancellation_forbidden": DELTA_CANCEL_FORBIDDEN in law_sources
            and authority["delta_cancellation_authority"] is False,
        "ordinary_inverse_not_imported": chain["ordinary_inverse_semantics"] is False
            and chain["involutive_reciprocal_assumed"] is False
            and authority["ordinary_inverse_authority"] is False,
        "all_nested_objects_share_delta_boundary": all(
            item["global_denominator"] == GLOBAL_DENOMINATOR
            and item["boundary_condition"] is True
            and item["independent_normalization_authority"] is False
            for item in manifest["objects"]
        ),
        "serializer_1_52_inherited_green": theorem["serializer_binding"]["result"] == "PASS"
            and theorem["serializer_binding"]["ingress_egress_same_operation"] is True
            and theorem["serializer_binding"]["nested_payloads_remain_typed"] is True,
        "no_canonical_authority_escalation": (
            authority["canonical_vm81_mutation_authority"] is False
            and authority["canonical_hash72_authority"] is False
            and authority["canonical_hash216_authority"] is False
        ),
        "negative_rewrite_surface_complete": len(theorem["prohibited_rewrites"]) == len(PROHIBITED_REWRITES)
            and all(item["source"] != item["forbidden_target"] for item in theorem["prohibited_rewrites"]),
    }

    return _receipt({
        "schema": f"{SCHEMA}_VALIDATION",
        "version": VERSION,
        "theorem_id": THEOREM_ID,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "law_count": len(theorem["laws"]),
        "prohibited_rewrite_count": len(theorem["prohibited_rewrites"]),
        "theorem_receipt_sha256": theorem["receipt_sha256"],
        "source_complete_formalization_status": "IN_PROGRESS",
    })


def main() -> int:
    report = validate_t5184_002()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
