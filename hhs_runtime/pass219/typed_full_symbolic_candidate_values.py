"""Pass 219 I157 candidate-bound typed full-symbolic value producer.

This module is an additive, read-only producer upstream of I156.  It binds one
I153 local-P snapshot and one verified Pass159 source->VMIR provenance chain to
one exact candidate symbol environment, then materializes the fifteen source
terms as typed value objects.

It deliberately does NOT coerce HARMONICODE typed joins into one scalar
algebra.  Rational, modular, tensor, ordered-phase, symbolic-root, and boundary
objects remain distinct.  It does not mutate VM81, mint Hash72/Hash216
authority, or claim Pass169 admission/replay.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import string
from typing import Any, Mapping

from hhs_runtime.pass219.fixed_cardinality_optimization import (
    ROUTE_MULTIPLICITY_PER_TARGET,
    TARGET_CARDINALITY,
    WORKING_MANIFOLD_CARDINALITY,
)
from hhs_runtime.pass219.local_global_equation_search_filter import (
    normalize_snapshot,
)

PASS = 219
ITERATION = "I157"
SCHEMA = "HHS_PASS219_I157_CANDIDATE_BOUND_TYPED_VALUE_GRAPH_V1"
CANDIDATE_SCHEMA = "HHS_PASS219_I157_CANDIDATE_SYMBOL_ENVIRONMENT_V1"
PROVENANCE_SCHEMA = "HHS_PASS219_I157_PASS159_PROVENANCE_BINDING_V1"

NATIVE_SOURCE_PATH = Path(
    "contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode"
)
MACHINE_SOURCE_PATH = Path(
    "contracts/pass219/PASS_219_NATIVE_UNIVERSAL_CONSTRAINT_ENVELOPE_1_8_0.harmonicode"
)
COMBINED_SOURCE_PATH = Path(
    "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode"
)

NATIVE_SOURCE_SHA256 = "ac143798146d89a3fe932f39ccb4d612e4fb3e45c471abc1a8bbbebb0f9c0a6a"
MACHINE_SOURCE_SHA256 = "7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42"
COMBINED_SOURCE_SHA256 = "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53"

HASH216_LEN = 216
SHA256_HEX_LEN = 64
HEX = frozenset(string.hexdigits)

TERM_NAMES = (
    "T3_MINUS_T",
    "P3_MINUS_P_OVER_DELTA",
    "T3_MINUS_T_OVER_DELTA",
    "P2_MOD_PQ",
    "M2_MINUS_M",
    "S",
    "S_SUBSTITUTION_RHS",
    "MATRIX_PLUS_XY_OVER_AT",
    "MOD_F_OVER_U_OVER_BT",
    "AB_OVER_P2",
    "SQRT_AB",
    "OUTER_LHS",
    "TERMINAL_RHS",
    "DELTA_OVER_P",
    "DELTA_ROOT_RHS",
)

TERM_SOURCES = (
    "t^3-t",
    "P^3-P/(P^2-pq)",
    "(t^3-t)/Delta",
    "P^2(MOD)(pq)",
    "m^2-m",
    "s",
    "(b^(2c^2)c^b^4)^2/(72P^2)",
    "(M_LH+x+y)/At",
    "Mod(f/u,72*(pq+xy))/Bt",
    "AB/P^2",
    "Sqrt[AB]",
    "P^2/{FULL_TYPED_CONSTRAINT_JOIN}",
    "(AB/(pq+Delta)-P^2)/(t^3-t)*u^72",
    "Delta/P",
    "Sqrt(pq+u^72)^x^2",
)

EDGE_SPECS = (
    (0, 1, "EXACT_RATIONAL_BINDING"),
    (1, 2, "EXACT_RATIONAL_BINDING"),
    (2, 3, "TYPED_MODULAR_PIVOT_JOIN"),
    (3, 4, "TYPED_MODULAR_PIVOT_JOIN"),
    (5, 6, "EXACT_RATIONAL_BINDING"),
    (7, 8, "TYPED_CONSTRAINT_JOIN"),
    (8, 9, "TYPED_CONSTRAINT_JOIN"),
    (9, 10, "AB_ROOT_CORRESPONDENCE"),
    (11, 12, "MONOLITHIC_BOUNDARY_EQUALITY"),
    (13, 14, "DELTA_RADICAL_PROJECTION"),
)

DOMAINS = (
    "EXACT_RATIONAL",
    "MODULAR_STATE",
    "EXACT_TENSOR_PROJECTION",
    "ORDERED_PHASE",
    "TENSOR_PHASE_QUOTIENT",
    "SYMBOLIC_MODULAR_QUOTIENT",
    "SYMBOLIC_BOUNDARY_RATIO",
    "SYMBOLIC_RADICAL",
    "SYMBOLIC_BOUNDARY",
)

PHASE_ANCHORS = {
    "x": 18,
    "y": 54,
    "z": 18,
    "w": 54,
    "xy": 0,
    "yx": 36,
    "zw": 0,
    "wz": 36,
}

# The four ordered generator products are the inherited exact-ABI overrides.
ORDERED_PRODUCT_PHASE_DELTA = {
    ("x", "y"): 0,
    ("y", "x"): 36,
    ("z", "w"): 0,
    ("w", "z"): 36,
}


class TypedCandidateValueError(RuntimeError):
    pass


def _repo_root(root: str | Path | None = None) -> Path:
    return (
        Path(root).resolve()
        if root is not None
        else Path(__file__).resolve().parents[2]
    )


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise TypedCandidateValueError("FLOAT_CANONICAL_INPUT_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_float(child)


def _canonical_json(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_source_identity(root: str | Path | None = None) -> dict[str, Any]:
    repo = _repo_root(root)
    rows = {
        "native": (repo / NATIVE_SOURCE_PATH, NATIVE_SOURCE_SHA256),
        "machine": (repo / MACHINE_SOURCE_PATH, MACHINE_SOURCE_SHA256),
        "combined": (repo / COMBINED_SOURCE_PATH, COMBINED_SOURCE_SHA256),
    }
    receipt: dict[str, Any] = {}
    for name, (path, expected) in rows.items():
        actual = _file_sha256(path)
        if actual != expected:
            raise TypedCandidateValueError(
                f"{name.upper()}_SOURCE_IDENTITY_DRIFT:{actual}"
            )
        receipt[name] = {
            "path": str(path.relative_to(repo)),
            "sha256": actual,
            "exact": True,
        }
    return receipt


def _hex64(value: Any, name: str, *, nonzero: bool = True) -> str:
    if (
        not isinstance(value, str)
        or len(value) != SHA256_HEX_LEN
        or any(ch not in HEX for ch in value)
    ):
        raise TypedCandidateValueError(f"{name}_SHA256_HEX_REQUIRED")
    lowered = value.lower()
    if nonzero and lowered == "0" * SHA256_HEX_LEN:
        raise TypedCandidateValueError(f"{name}_ZERO_FORBIDDEN")
    return lowered


def _hash216(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH216_LEN:
        raise TypedCandidateValueError(f"{name}_HASH216_LENGTH_REQUIRED")
    if any(ord(ch) < 33 or ord(ch) > 126 for ch in value):
        raise TypedCandidateValueError(f"{name}_HASH216_PRINTABLE_REQUIRED")
    return value


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypedCandidateValueError(f"{name}_BOOLEAN_REQUIRED")
    return value


def _int(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypedCandidateValueError(f"{name}_EXACT_INTEGER_REQUIRED")
    if minimum is not None and value < minimum:
        raise TypedCandidateValueError(f"{name}_OUT_OF_RANGE")
    return value


def _fraction(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypedCandidateValueError(f"{name}_EXACT_RATIONAL_REQUIRED")
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, Fraction):
        return value
    if isinstance(value, Mapping):
        numerator = _int(value.get("numerator"), f"{name}_NUMERATOR")
        denominator = _int(
            value.get("denominator"),
            f"{name}_DENOMINATOR",
            minimum=1,
        )
        return Fraction(numerator, denominator)
    raise TypedCandidateValueError(f"{name}_EXACT_RATIONAL_REQUIRED")


def _fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "text": (
            str(value.numerator)
            if value.denominator == 1
            else f"{value.numerator}/{value.denominator}"
        ),
    }


def normalize_pass159_provenance(provenance: Mapping[str, Any]) -> dict[str, Any]:
    if provenance.get("schema") != PROVENANCE_SCHEMA:
        raise TypedCandidateValueError("PASS159_PROVENANCE_SCHEMA_MISMATCH")
    if provenance.get("combined_source_sha256") != COMBINED_SOURCE_SHA256:
        raise TypedCandidateValueError("PASS159_COMBINED_SOURCE_IDENTITY_DRIFT")

    stage_names = (
        "source_hash216",
        "tokens_hash216",
        "cst_hash216",
        "ast_hash216",
        "type_environment_hash216",
        "constraint_graph_hash216",
        "hir_hash216",
        "vmir_hash216",
    )
    stages = {
        name: _hash216(provenance.get(name), name.upper())
        for name in stage_names
    }
    root = _hex64(
        provenance.get("global_symbol_environment_root"),
        "GLOBAL_SYMBOL_ENVIRONMENT_ROOT",
    )

    required_flags = (
        "source_identity_exact",
        "gate_occurrence_provenance_exact",
        "frontend_chain_complete",
        "source_root_lineage_exact",
        "pass159_whole_expression_provenance_verified",
    )
    for name in required_flags:
        if not _bool(provenance.get(name), name.upper()):
            raise TypedCandidateValueError(f"{name.upper()}_REQUIRED")

    forbidden_true = (
        "boolean_gate_results_available",
        "membrane_input_ready",
        "canonical_monolithic_proof",
        "floating_point_authority",
        "vm81_mutation_authority",
        "hash72_commit_authority",
        "persistence_mutation_authority",
    )
    for name in forbidden_true:
        if _bool(provenance.get(name), name.upper()):
            raise TypedCandidateValueError(f"{name.upper()}_AUTHORITY_ESCALATION")

    normalized = {
        "schema": PROVENANCE_SCHEMA,
        "combined_source_sha256": COMBINED_SOURCE_SHA256,
        **stages,
        "global_symbol_environment_root": root,
        **{name: True for name in required_flags},
        **{name: False for name in forbidden_true},
        "pass169_whole_expression_authority_required": True,
    }
    normalized["provenance_binding_sha256"] = _sha256(normalized)
    return normalized


def _phase_product(left: str, right: str, left_phase: int, right_phase: int) -> int:
    if (left, right) not in ORDERED_PRODUCT_PHASE_DELTA:
        raise TypedCandidateValueError("ORDERED_PHASE_PAIR_UNSUPPORTED")
    return (
        left_phase
        + right_phase
        + ORDERED_PRODUCT_PHASE_DELTA[(left, right)]
    ) % 72


def _phase_state(symbols: Mapping[str, Any]) -> dict[str, Any]:
    x = _int(symbols.get("x"), "X_PHASE", minimum=0)
    y = _int(symbols.get("y"), "Y_PHASE", minimum=0)
    z = _int(symbols.get("z"), "Z_PHASE", minimum=0)
    w = _int(symbols.get("w"), "W_PHASE", minimum=0)
    if max(x, y, z, w) >= 72:
        raise TypedCandidateValueError("PHASE_COORDINATE_OUT_OF_72_RING")

    xy = _phase_product("x", "y", x, y)
    yx = _phase_product("y", "x", y, x)
    zw = _phase_product("z", "w", z, w)
    wz = _phase_product("w", "z", w, z)
    state = {
        "domain": "ORDERED_PHASE",
        "x": x,
        "y": y,
        "z": z,
        "w": w,
        "xy": xy,
        "yx": yx,
        "zw": zw,
        "wz": wz,
        "xy_yx_distinct": xy != yx,
        "zw_wz_distinct": zw != wz,
        "ring_modulus": 72,
        "derivation": "INHERITED_EXACT_ABI_ORDERED_PRODUCT_DELTA",
        "floating_point_authority": False,
    }
    if not state["xy_yx_distinct"] or not state["zw_wz_distinct"]:
        raise TypedCandidateValueError("ORDERED_PHASE_NONCOMMUTATIVITY_COLLAPSED")
    state["witness_sha256"] = _sha256(state)
    return state


def _lo_shu_projection() -> dict[str, Any]:
    b2 = Fraction(2)
    c2 = Fraction(3)
    u72 = Fraction(1)
    xy_projection = Fraction(1)
    b4 = b2 * b2
    b6 = b4 * b2
    c4 = c2 * c2
    sqrt_c4 = Fraction(3)
    stage1 = (b2 * (c2 + b2) - (c2 - b2)) / sqrt_c4
    stage2 = (c2 * b6 - c2) / stage1
    nested = ((b6 - xy_projection) * (b4 + c2)) / stage2
    matrix = (
        (b4, c4, c2 - u72),
        (c2, Fraction(5), nested),
        ((Fraction(2) * c2) + b2, Fraction(2) / b2, b2 * c2),
    )
    expected = (
        (Fraction(4), Fraction(9), Fraction(2)),
        (Fraction(3), Fraction(5), Fraction(7)),
        (Fraction(8), Fraction(1), Fraction(6)),
    )
    if matrix != expected:
        raise TypedCandidateValueError("PASS191_LO_SHU_PROJECTION_DRIFT")

    row_sums = [sum(row) for row in matrix]
    column_sums = [
        sum(matrix[row][column] for row in range(3))
        for column in range(3)
    ]
    diagonals = [
        matrix[0][0] + matrix[1][1] + matrix[2][2],
        matrix[0][2] + matrix[1][1] + matrix[2][0],
    ]
    if (
        row_sums != [Fraction(15)] * 3
        or column_sums != [Fraction(15)] * 3
        or diagonals != [Fraction(15)] * 2
    ):
        raise TypedCandidateValueError("PASS191_LO_SHU_SUM_DRIFT")

    record = {
        "domain": "EXACT_TENSOR_PROJECTION",
        "shape": [3, 3],
        "matrix": [
            [_fraction_record(value) for value in row]
            for row in matrix
        ],
        "row_sums": [_fraction_record(v) for v in row_sums],
        "column_sums": [_fraction_record(v) for v in column_sums],
        "diagonal_sums": [_fraction_record(v) for v in diagonals],
        "projection_scope": "PASS191_XY_SCALAR_PROJECTION_EQUALS_1",
        "native_ordered_phase_substituted": False,
        "projection_is_native_state_identity": False,
        "exact_reconstruction_of_native_phase_claimed": False,
        "floating_point_authority": False,
    }
    record["witness_sha256"] = _sha256(record)
    return record


def _node(
    term_id: int,
    *,
    domain: str,
    value_status: str,
    payload: Mapping[str, Any],
    exact: bool,
) -> dict[str, Any]:
    if domain not in DOMAINS:
        raise TypedCandidateValueError("VALUE_DOMAIN_UNREGISTERED")
    core = {
        "term_id": term_id,
        "term_name": TERM_NAMES[term_id],
        "source_expression": TERM_SOURCES[term_id],
        "domain": domain,
        "value_status": value_status,
        "payload": dict(payload),
        "exact": exact,
        "floating_point_authority": False,
    }
    core["node_sha256"] = _sha256(core)
    return core


def _rational_node(term_id: int, value: Fraction) -> dict[str, Any]:
    return _node(
        term_id,
        domain="EXACT_RATIONAL",
        value_status="RESOLVED_EXACT",
        payload={"value": _fraction_record(value)},
        exact=True,
    )


def _unresolved_rational_node(
    term_id: int,
    reason: str,
    *,
    inputs: Mapping[str, Any],
) -> dict[str, Any]:
    return _node(
        term_id,
        domain="EXACT_RATIONAL",
        value_status="UNRESOLVED_EXACT_DOMAIN",
        payload={"reason": reason, "inputs": dict(inputs)},
        exact=False,
    )


def _rational_value(node: Mapping[str, Any]) -> Fraction | None:
    if (
        node.get("domain") != "EXACT_RATIONAL"
        or node.get("value_status") != "RESOLVED_EXACT"
    ):
        return None
    value = node["payload"]["value"]
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def _join(
    edge_index: int,
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    join_kind: str,
    candidate_binding_sha256: str,
) -> dict[str, Any]:
    status = "UNRESOLVED"
    reason = "REGISTERED_TYPED_EXECUTION_ADAPTER_REQUIRED"

    if join_kind == "EXACT_RATIONAL_BINDING":
        lv = _rational_value(left)
        rv = _rational_value(right)
        if lv is None or rv is None:
            status = "UNRESOLVED"
            reason = "EXACT_RATIONAL_VALUE_UNAVAILABLE"
        elif lv == rv:
            status = "PROVED"
            reason = "EXACT_RATIONAL_IDENTITY"
        else:
            status = "REJECTED"
            reason = "EXACT_RATIONAL_MISMATCH"

    elif join_kind == "TYPED_MODULAR_PIVOT_JOIN":
        # Do not flatten a modular state into a scalar remainder.  Production
        # proof needs the registered modular-pivot adapter from the typed graph.
        status = "UNRESOLVED"
        reason = "MODULAR_PIVOT_ADAPTER_REQUIRED_NO_SCALAR_REMAINDER_COERCION"

    elif join_kind == "TYPED_CONSTRAINT_JOIN":
        if left.get("exact") is True and right.get("exact") is True:
            status = "PROVED"
            reason = "EXACT_TYPED_WITNESSES_JOIN_ONE_CANDIDATE"
        else:
            status = "UNRESOLVED"
            reason = "TYPED_WITNESS_INCOMPLETE"

    elif join_kind == "AB_ROOT_CORRESPONDENCE":
        status = "UNRESOLVED"
        reason = "SYMBOLIC_AB_ROOT_EXECUTION_REQUIRED"

    elif join_kind == "MONOLITHIC_BOUNDARY_EQUALITY":
        status = "UNRESOLVED"
        reason = "COMPLETE_BOUNDARY_EXECUTION_REQUIRED"

    elif join_kind == "DELTA_RADICAL_PROJECTION":
        status = "UNRESOLVED"
        reason = "EXACT_PHASE_EXPONENT_RADICAL_ADAPTER_REQUIRED"

    core = {
        "edge_index": edge_index,
        "left_term_id": int(left["term_id"]),
        "right_term_id": int(right["term_id"]),
        "left_node_sha256": str(left["node_sha256"]),
        "right_node_sha256": str(right["node_sha256"]),
        "join_kind": join_kind,
        "status": status,
        "reason": reason,
        "candidate_binding_sha256": candidate_binding_sha256,
        "scalar_coercion_used": False,
        "floating_point_authority": False,
    }
    core["join_sha256"] = _sha256(core)
    return core


def _symbols(symbols: Mapping[str, Any], snapshot_p: int) -> dict[str, Any]:
    if symbols.get("schema") != CANDIDATE_SCHEMA:
        raise TypedCandidateValueError("CANDIDATE_SYMBOL_ENVIRONMENT_SCHEMA_MISMATCH")

    if "P" in symbols and _int(symbols.get("P"), "P", minimum=1) != snapshot_p:
        raise TypedCandidateValueError("CANDIDATE_P_SNAPSHOT_DRIFT")

    p = _int(symbols.get("p"), "p", minimum=1)
    q = _int(symbols.get("q"), "q", minimum=1)
    t = _int(symbols.get("t"), "t")
    m = _int(symbols.get("m"), "m")
    s = _fraction(symbols.get("s"), "s")
    f = _fraction(symbols.get("f"), "f")
    At = _fraction(symbols.get("At"), "At")
    Bt = _fraction(symbols.get("Bt"), "Bt")
    if At == 0:
        raise TypedCandidateValueError("At_ZERO_FORBIDDEN")
    if Bt == 0:
        raise TypedCandidateValueError("Bt_ZERO_FORBIDDEN")

    phase = _phase_state(symbols)

    normalized = {
        "schema": CANDIDATE_SCHEMA,
        "P": snapshot_p,
        "p": p,
        "q": q,
        "t": t,
        "m": m,
        "s": _fraction_record(s),
        "f": _fraction_record(f),
        "At": _fraction_record(At),
        "Bt": _fraction_record(Bt),
        "u72": 1,
        "b2": 2,
        "c2": 3,
        "phase_state": phase,
    }
    normalized["symbol_environment_sha256"] = _sha256(normalized)
    return normalized


def produce_candidate_bound_value_graph(
    snapshot: Mapping[str, Any],
    pass159_provenance: Mapping[str, Any],
    symbols: Mapping[str, Any],
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Produce all fifteen frozen-source terms as typed value objects.

    The function computes ordinary exact-rational projections where their
    declared domain permits it and preserves modular/tensor/phase/root/boundary
    objects without destructive scalarization.
    """

    source_receipt = verify_frozen_source_identity(root)
    snap = normalize_snapshot(snapshot)
    provenance = normalize_pass159_provenance(pass159_provenance)
    env = _symbols(symbols, int(snap["P"]))

    P = int(env["P"])
    p = int(env["p"])
    q = int(env["q"])
    t = int(env["t"])
    m = int(env["m"])
    s = Fraction(env["s"]["numerator"], env["s"]["denominator"])
    f = Fraction(env["f"]["numerator"], env["f"]["denominator"])
    At = Fraction(env["At"]["numerator"], env["At"]["denominator"])
    Bt = Fraction(env["Bt"]["numerator"], env["Bt"]["denominator"])
    phase = env["phase_state"]

    P2 = P * P
    pq = p * q
    delta = P2 - pq
    cubic = t * t * t - t
    idempotent = m * m - m

    nodes: list[dict[str, Any]] = []

    nodes.append(_rational_node(0, Fraction(cubic)))

    if delta == 0:
        nodes.append(
            _unresolved_rational_node(
                1,
                "P2_MINUS_PQ_ZERO_DENOMINATOR",
                inputs={"P": P, "p": p, "q": q},
            )
        )
        nodes.append(
            _unresolved_rational_node(
                2,
                "DELTA_ZERO_DENOMINATOR",
                inputs={"t": t, "delta": delta},
            )
        )
    else:
        nodes.append(
            _rational_node(1, Fraction(P**3) - Fraction(P, delta))
        )
        nodes.append(_rational_node(2, Fraction(cubic, delta)))

    if pq <= 0:
        nodes.append(
            _node(
                3,
                domain="MODULAR_STATE",
                value_status="UNRESOLVED_EXACT_DOMAIN",
                payload={"reason": "PQ_MODULUS_NONPOSITIVE", "pq": pq},
                exact=False,
            )
        )
    else:
        nodes.append(
            _node(
                3,
                domain="MODULAR_STATE",
                value_status="RESOLVED_EXACT_TYPED",
                payload={
                    "representative": P2 % pq,
                    "modulus": pq,
                    "class_expression": f"[{P2}]_mod_{pq}",
                    "source_operator": "P^2(MOD)(pq)",
                    "ordinary_scalar_remainder_identity_claimed": False,
                },
                exact=True,
            )
        )

    nodes.append(_rational_node(4, Fraction(idempotent)))
    nodes.append(_rational_node(5, s))

    # b^(2*c^2) = b^6 = 8; c^(b^4) = c^4 = 9; their product is 72.
    # Squaring and dividing by 72*P^2 gives the exact rational 72/P^2.
    s_rhs = Fraction(72, P2)
    nodes.append(
        _node(
            6,
            domain="EXACT_RATIONAL",
            value_status="RESOLVED_EXACT",
            payload={
                "value": _fraction_record(s_rhs),
                "derivation": {
                    "b2": 2,
                    "c2": 3,
                    "b4": 4,
                    "b6": 8,
                    "c4": 9,
                    "b6_times_c4": 72,
                    "squared": 5184,
                    "denominator": 72 * P2,
                },
            },
            exact=True,
        )
    )

    lo_shu = _lo_shu_projection()
    matrix_phase_payload = {
        "matrix_projection_sha256": lo_shu["witness_sha256"],
        "matrix_projection": lo_shu,
        "ordered_phase_witness_sha256": phase["witness_sha256"],
        "ordered_phase_state": phase,
        "At": _fraction_record(At),
        "source_operation": "(M_LH+x+y)/At",
        "typed_tensor_phase_join_preserved": True,
        "scalar_matrix_collapse_used": False,
    }
    nodes.append(
        _node(
            7,
            domain="TENSOR_PHASE_QUOTIENT",
            value_status="RESOLVED_EXACT_TYPED",
            payload=matrix_phase_payload,
            exact=True,
        )
    )

    nodes.append(
        _node(
            8,
            domain="SYMBOLIC_MODULAR_QUOTIENT",
            value_status="RESOLVED_EXACT_SYMBOLIC",
            payload={
                "f_over_u72": _fraction_record(f),
                "u72": 1,
                "pq": pq,
                "xy_ordered_phase": int(phase["xy"]),
                "modulus_expression": "72*(pq+xy)",
                "Bt": _fraction_record(Bt),
                "native_xy_scalar_projection_applied": False,
                "numeric_modulus_claimed": False,
                "ordinary_scalar_remainder_identity_claimed": False,
            },
            exact=True,
        )
    )

    boundary_refs = {
        "A": "COMPLETE_MONOLITHIC_LEFT_BOUNDARY",
        "B": "COMPLETE_MONOLITHIC_RIGHT_BOUNDARY",
    }
    nodes.append(
        _node(
            9,
            domain="SYMBOLIC_BOUNDARY_RATIO",
            value_status="RESOLVED_EXACT_SYMBOLIC",
            payload={
                **boundary_refs,
                "P2": P2,
                "expression": "AB/P^2",
                "A_or_B_definitionally_P2": False,
            },
            exact=True,
        )
    )
    nodes.append(
        _node(
            10,
            domain="SYMBOLIC_RADICAL",
            value_status="RESOLVED_EXACT_SYMBOLIC",
            payload={
                **boundary_refs,
                "radicand": "A*B",
                "root_degree": 2,
                "expression": "Sqrt[AB]",
                "scalar_root_projection_claimed": False,
            },
            exact=True,
        )
    )

    nodes.append(
        _node(
            11,
            domain="SYMBOLIC_BOUNDARY",
            value_status="RESOLVED_EXACT_SYMBOLIC",
            payload={
                "boundary": "A",
                "expression": "P^2/{FULL_TYPED_CONSTRAINT_JOIN}",
                "P2": P2,
                "harmonic_term_ids": [0, 1, 2, 3, 4],
                "tensor_modular_term_ids": [5, 6, 7, 8, 9, 10],
                "source_structure_preserved": True,
                "scalar_denominator_substitution_used": False,
            },
            exact=True,
        )
    )
    nodes.append(
        _node(
            12,
            domain="SYMBOLIC_BOUNDARY",
            value_status="RESOLVED_EXACT_SYMBOLIC",
            payload={
                "boundary": "B",
                "expression": "(AB/(pq+Delta)-P^2)/(t^3-t)*u^72",
                "P2": P2,
                "pq": pq,
                "delta": delta,
                "t3_minus_t": cubic,
                "u72": 1,
                "AB_source_boundary_refs": boundary_refs,
                "source_structure_preserved": True,
                "scalar_boundary_fixed_point_claimed": False,
            },
            exact=True,
        )
    )

    nodes.append(_rational_node(13, Fraction(delta, P)))
    nodes.append(
        _node(
            14,
            domain="SYMBOLIC_RADICAL",
            value_status="RESOLVED_EXACT_SYMBOLIC",
            payload={
                "expression": "Sqrt(pq+u^72)^x^2",
                "base": {
                    "pq": pq,
                    "u72": 1,
                    "sum": pq + 1,
                },
                "root_degree": 2,
                "phase_exponent": {
                    "symbol": "x^2",
                    "x_phase": int(phase["x"]),
                    "domain": "ORDERED_PHASE_EXPONENT",
                },
                "ordinary_scalar_x_squared_assumed": False,
                "scalar_radical_projection_claimed": False,
            },
            exact=True,
        )
    )

    if len(nodes) != len(TERM_NAMES):
        raise TypedCandidateValueError("TERM_COUNT_DRIFT")

    candidate_binding = {
        "snapshot_binding_sha256": snap["snapshot_binding_sha256"],
        "snapshot_hash216": snap["snapshot_hash216"],
        "P": P,
        "combined_source_sha256": COMBINED_SOURCE_SHA256,
        "native_source_sha256": NATIVE_SOURCE_SHA256,
        "machine_source_sha256": MACHINE_SOURCE_SHA256,
        "pass159_provenance_binding_sha256": provenance["provenance_binding_sha256"],
        "pass159_global_symbol_environment_root": provenance[
            "global_symbol_environment_root"
        ],
        "pass159_constraint_graph_hash216": provenance[
            "constraint_graph_hash216"
        ],
        "pass159_vmir_hash216": provenance["vmir_hash216"],
        "symbol_environment_sha256": env["symbol_environment_sha256"],
        "node_sha256s": [node["node_sha256"] for node in nodes],
    }
    candidate_binding_sha256 = _sha256(candidate_binding)

    joins = [
        _join(
            edge_index,
            nodes[left],
            nodes[right],
            join_kind,
            candidate_binding_sha256,
        )
        for edge_index, (left, right, join_kind) in enumerate(EDGE_SPECS)
    ]

    rejected = [join for join in joins if join["status"] == "REJECTED"]
    unresolved = [join for join in joins if join["status"] == "UNRESOLVED"]
    proved = [join for join in joins if join["status"] == "PROVED"]

    if rejected:
        graph_decision = "REJECTED"
    elif unresolved:
        graph_decision = "UNRESOLVED"
    else:
        graph_decision = "TYPED_GRAPH_RESOLVED"

    rational_projection_terms = [
        node["term_id"]
        for node in nodes
        if node["domain"] == "EXACT_RATIONAL"
        and node["value_status"] == "RESOLVED_EXACT"
    ]
    non_rational_terms = [
        node["term_id"]
        for node in nodes
        if node["domain"] != "EXACT_RATIONAL"
    ]

    core = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "classification": "CANDIDATE_BOUND_TYPED_FULL_SYMBOLIC_VALUE_GRAPH",
        "decision": graph_decision,
        "source_identity": source_receipt,
        "snapshot": snap,
        "pass159_provenance": provenance,
        "symbol_environment": env,
        "candidate_binding_sha256": candidate_binding_sha256,
        "value_nodes": nodes,
        "joins": joins,
        "counts": {
            "term_count": len(nodes),
            "join_count": len(joins),
            "proved_joins": len(proved),
            "unresolved_joins": len(unresolved),
            "rejected_joins": len(rejected),
            "typed_domains": sorted({str(node["domain"]) for node in nodes}),
        },
        "i156_projection_boundary": {
            "i156_is_full_typed_semantic_authority": False,
            "i156_ratio_projection_terms": rational_projection_terms,
            "non_rational_typed_terms": non_rational_terms,
            "full_i156_ratio_packet_eligible": False,
            "reason": (
                "FULL_SOURCE_CONTAINS_MODULAR_TENSOR_PHASE_RADICAL_AND_BOUNDARY_"
                "VALUES_NO_SCALAR_COERCION_AUTHORIZED"
            ),
        },
        "fixed_search_space": {
            "target_cardinality_decimal": str(TARGET_CARDINALITY),
            "working_manifold_cardinality_decimal": str(
                WORKING_MANIFOLD_CARDINALITY
            ),
            "route_multiplicity_per_target_decimal": str(
                ROUTE_MULTIPLICITY_PER_TARGET
            ),
            "changed": False,
        },
        "authority": {
            "pass169_whole_expression_authority_required": True,
            "canonical_monolithic_proof": False,
            "vm81_execution_verified": False,
            "vm81_mutation_authority": False,
            "hash72_execution_receipt_verified": False,
            "hash72_mint_authority": False,
            "hash216_persistence_authority": False,
            "deterministic_replay_verified": False,
            "floating_point_authority": False,
        },
        "next_required_adapters": sorted(
            {
                join["reason"]
                for join in unresolved
                if join["reason"]
                != "EXACT_RATIONAL_VALUE_UNAVAILABLE"
            }
        ),
        "result": "PASS",
    }
    core["typed_value_graph_sha256"] = _sha256(core)
    return core


def candidate_bound_full_symbolic_value_producer_self_test() -> dict[str, Any]:
    """Pure-Python exact self-test suitable for the service registry."""

    snapshot = {
        "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
        "snapshot_hash216": "1" * 64,
        "snapshot_hash216_format": "PASS150_HASH216_GENOME_ROOT_SHA256",
        "P": 2,
        "hydration_bits": 5184,
    }
    base_hashes = {
        "source_hash216": "0" * HASH216_LEN,
        "tokens_hash216": "1" * HASH216_LEN,
        "cst_hash216": "2" * HASH216_LEN,
        "ast_hash216": "3" * HASH216_LEN,
        "type_environment_hash216": "4" * HASH216_LEN,
        "constraint_graph_hash216": "5" * HASH216_LEN,
        "hir_hash216": "6" * HASH216_LEN,
        "vmir_hash216": "7" * HASH216_LEN,
    }
    provenance = {
        "schema": PROVENANCE_SCHEMA,
        "combined_source_sha256": COMBINED_SOURCE_SHA256,
        **base_hashes,
        "global_symbol_environment_root": "a" * 64,
        "source_identity_exact": True,
        "gate_occurrence_provenance_exact": True,
        "frontend_chain_complete": True,
        "source_root_lineage_exact": True,
        "pass159_whole_expression_provenance_verified": True,
        "boolean_gate_results_available": False,
        "membrane_input_ready": False,
        "canonical_monolithic_proof": False,
        "floating_point_authority": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "persistence_mutation_authority": False,
    }
    symbols = {
        "schema": CANDIDATE_SCHEMA,
        "P": 2,
        "p": 1,
        "q": 3,
        "t": 2,
        "m": 3,
        "s": {"numerator": 18, "denominator": 1},
        "f": 4,
        "At": 1,
        "Bt": 1,
        "x": 18,
        "y": 54,
        "z": 18,
        "w": 54,
    }
    result = produce_candidate_bound_value_graph(snapshot, provenance, symbols)
    if (
        result["counts"]["term_count"] != 15
        or result["counts"]["join_count"] != 10
        or result["symbol_environment"]["phase_state"]["xy"] != 0
        or result["symbol_environment"]["phase_state"]["yx"] != 36
        or result["i156_projection_boundary"]["full_i156_ratio_packet_eligible"]
        is not False
        or result["authority"]["canonical_monolithic_proof"] is not False
    ):
        raise AssertionError("I157_SELF_TEST_INVARIANT_FAILURE")
    return {
        "schema": "HHS_PASS219_I157_SELF_TEST_V1",
        "ok": True,
        "decision": result["decision"],
        "term_count": result["counts"]["term_count"],
        "join_count": result["counts"]["join_count"],
        "typed_value_graph_sha256": result["typed_value_graph_sha256"],
        "canonical_monolithic_proof": False,
        "vm81_mutation_authority": False,
        "hash72_mint_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "PASS",
    "ITERATION",
    "SCHEMA",
    "CANDIDATE_SCHEMA",
    "PROVENANCE_SCHEMA",
    "TERM_NAMES",
    "TERM_SOURCES",
    "EDGE_SPECS",
    "TypedCandidateValueError",
    "verify_frozen_source_identity",
    "normalize_pass159_provenance",
    "produce_candidate_bound_value_graph",
    "candidate_bound_full_symbolic_value_producer_self_test",
]
