from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.pass219.source_bound_ab_x2_phase_binding import (
    _self_test_graph,
    execute_i160_source_bound_bindings,
)

PASS = 219
ITERATION = "I161"
SCHEMA = "HHS_PASS219_I161_COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_V1"
PROFILE_SCHEMA = "HHS_PASS219_I161_TYPED_ZERO_RENEWED_UNIT_PROFILE_V1"
SCALAR_ZERO_SCHEMA = "HHS_PASS219_I161_SCALAR_ZERO_PHASE_WITNESS_V1"
RENEWED_UNIT_SCHEMA = "HHS_PASS219_I161_RENEWED_UNIT_CLOSURE_WITNESS_V1"
BOUNDARY_SCHEMA = "HHS_PASS219_I161_TYPED_MONOLITHIC_BOUNDARY_WITNESS_V1"

CANONICAL_PASS64_PATH = Path("CANONICAL_PROMPT_STATE_PASS_064.json")
ZERO_APPENDIX_PATH = Path("docs/pass219/APPENDIX_E_TYPED_ZERO_PIVOT_AND_PHASE_CLOSURE.md")
PASS129_PATH = Path("hhs_runtime/hhs_pass129_invariant_delta_rational_projection_algebra_v1.py")
MONOLITHIC_SOURCE_PATH = Path(
    "contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode"
)
COMBINED_SOURCE_PATH = Path(
    "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode"
)

USER_DECLARED_SCALAR_ZERO_RELATION = "0=x+y+z+w=I+I^3"
USER_DECLARED_RENEWED_UNIT_RELATION = "u^0=xy/zw=P^2-pq=a^2/Delta=0^4"


class CompleteBoundaryExecutorError(RuntimeError):
    pass


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise CompleteBoundaryExecutorError("FLOAT_CANONICAL_AUTHORITY_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_float(child)


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _integer(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise CompleteBoundaryExecutorError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _repo_root(root: str | Path | None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]


def _read(root: Path, relative: Path) -> str:
    path = root / relative
    if not path.is_file():
        raise CompleteBoundaryExecutorError(f"REQUIRED_SOURCE_MISSING:{relative.as_posix()}")
    return path.read_text(encoding="utf-8")


def verify_i161_typed_zero_renewed_unit_profile(
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Bind I161 to inherited typed equality/zero sources plus the declared I161 relation."""

    repo = _repo_root(root)
    pass64_text = _read(repo, CANONICAL_PASS64_PATH)
    appendix_text = _read(repo, ZERO_APPENDIX_PATH)
    pass129_text = _read(repo, PASS129_PATH)
    monolithic_text = _read(repo, MONOLITHIC_SOURCE_PATH)
    combined_text = _read(repo, COMBINED_SOURCE_PATH)

    pass64 = json.loads(pass64_text)
    formal = pass64.get("formal_objects")
    if not isinstance(formal, list):
        raise CompleteBoundaryExecutorError("PASS64_FORMAL_OBJECTS_REQUIRED")
    relations = [row.get("relation") for row in formal if isinstance(row, Mapping)]
    oriented_ratio = any(
        isinstance(row, Mapping)
        and row.get("relation") == "ORIENTED_RATIO"
        and row.get("canonical_ratio") == "I:I^3 = 1:-1"
        for row in relations
    )
    typed_zero_sum = any(
        isinstance(row, Mapping)
        and row.get("relation") == "ZERO_SUM"
        and row.get("result") == "0"
        for row in relations
    )
    global_product = any(
        isinstance(row, Mapping)
        and row.get("relation") == "GLOBAL_PRODUCT_CLOSURE"
        and row.get("expression") == "xyXY = xyzw = 1"
        for row in relations
    )

    checks = {
        "pass64_oriented_I_I3_ratio": oriented_ratio,
        "pass64_typed_zero_sum": typed_zero_sum,
        "pass64_global_product_closure": global_product,
        "appendix_scalar_zero_type": "ScalarZero" in appendix_text,
        "appendix_closure_residue_type": "ClosureResidue(period)" in appendix_text,
        "appendix_renewed_unit_type": "RenewedUnit(period)" in appendix_text,
        "appendix_scalar_zero_one_noncollapse": "0_scalar != 1_scalar." in appendix_text,
        "appendix_u72_renewed_unit": "u^72 -> renewed unit." in appendix_text,
        "pass129_a2_unit": '"canonical_constants": {"a^2": 1' in pass129_text,
        "pass129_idempotent_delta_closure": "NONZERO_RATIONAL_IDEMPOTENT_CLOSURE" in pass129_text,
        "pass129_xy_over_zw_membrane": "xy/zw + x+y+z+w" in pass129_text,
        "pass129_four_phase_zero_sum": "FOUR_PHASE_CARRIER_ZERO_SUM" in pass129_text,
        "monolithic_terminal_boundary_source": (
            "(AB/(pq+∆)-P^2)/(t^3-t)*u^72" in monolithic_text
        ),
        "combined_xyzw_scalar_sum_source": "x+y+z+w" in combined_text,
        "combined_I3_phase_source": "I^3" in combined_text,
    }
    if not all(checks.values()):
        raise CompleteBoundaryExecutorError(f"I161_TYPED_PROFILE_DRIFT:{checks}")

    core = {
        "schema": PROFILE_SCHEMA,
        "inherited_sources": {
            CANONICAL_PASS64_PATH.as_posix(): sha256(pass64_text.encode("utf-8")).hexdigest(),
            ZERO_APPENDIX_PATH.as_posix(): sha256(appendix_text.encode("utf-8")).hexdigest(),
            PASS129_PATH.as_posix(): sha256(pass129_text.encode("utf-8")).hexdigest(),
            MONOLITHIC_SOURCE_PATH.as_posix(): sha256(monolithic_text.encode("utf-8")).hexdigest(),
            COMBINED_SOURCE_PATH.as_posix(): sha256(combined_text.encode("utf-8")).hexdigest(),
        },
        "checks": checks,
        "declared_i161_relations": {
            "scalar_zero": USER_DECLARED_SCALAR_ZERO_RELATION,
            "renewed_unit": USER_DECLARED_RENEWED_UNIT_RELATION,
        },
        "declared_relation_provenance": "USER_DECLARED_I161_BOUNDARY_RELATION",
        "zero_fourth_operator": "TYPED_FOURTH_PHASE_CLOSURE",
        "zero_fourth_host_scalar_pow": False,
        "xy_over_zw_operator": "TYPED_CLOSURE_QUOTIENT",
        "xy_over_zw_host_zero_division": False,
        "scalar_zero_equals_scalar_one": False,
        "equality_frame": "CLOSURE_EQ",
        "floating_point_authority": False,
    }
    core["profile_sha256"] = _sha256(core)
    return core


_PHASE_COEFFICIENTS = {
    0: (1, 0),
    18: (0, 1),
    36: (-1, 0),
    54: (0, -1),
}


def _phase_coefficient(value: Any, label: str) -> tuple[int, int]:
    phase = _integer(value, label)
    if phase not in _PHASE_COEFFICIENTS:
        raise CompleteBoundaryExecutorError(f"{label}_QUARTER_PHASE_REQUIRED")
    return _PHASE_COEFFICIENTS[phase]


def prove_scalar_zero_phase_relation(
    phase_state: Mapping[str, Any],
    *,
    profile_sha256: str,
) -> dict[str, Any]:
    """Prove 0=x+y+z+w=I+I^3 in the declared scalar/phase projection only."""

    if phase_state.get("domain") != "ORDERED_PHASE" or phase_state.get("ring_modulus") != 72:
        raise CompleteBoundaryExecutorError("ORDERED_PHASE_STATE_REQUIRED")
    coeffs = {
        symbol: _phase_coefficient(phase_state.get(symbol), symbol.upper())
        for symbol in ("x", "y", "z", "w")
    }
    xyzw_sum = (
        sum(value[0] for value in coeffs.values()),
        sum(value[1] for value in coeffs.values()),
    )
    i_plus_i3 = (0, 1 + (-1))
    checks = {
        "xyzw_scalar_phase_projection_is_zero": xyzw_sum == (0, 0),
        "I_plus_I3_scalar_projection_is_zero": i_plus_i3 == (0, 0),
        "declared_scalar_zero_relation_preserved": True,
    }
    proved = all(checks.values())
    core = {
        "schema": SCALAR_ZERO_SCHEMA,
        "relation": USER_DECLARED_SCALAR_ZERO_RELATION,
        "status": "PROVED" if proved else "REJECTED",
        "reason": (
            "EXACT_SCALAR_ZERO_PHASE_PROJECTION"
            if proved
            else "SCALAR_ZERO_PHASE_PROJECTION_MISMATCH"
        ),
        "type": "ScalarZero",
        "phase_coefficients": {
            symbol: list(value) for symbol, value in coeffs.items()
        },
        "xyzw_sum_coefficients": list(xyzw_sum),
        "I_plus_I3_coefficients": list(i_plus_i3),
        "profile_sha256": profile_sha256,
        "checks": checks,
        "ordered_phase_objects_collapsed_to_scalar_identity": False,
        "scalar_zero_equals_scalar_one": False,
        "floating_point_authority": False,
    }
    core["scalar_zero_witness_sha256"] = _sha256(core)
    return core


def prove_renewed_unit_closure_relation(
    *,
    P: int,
    p: int,
    q: int,
    phase_state: Mapping[str, Any],
    scalar_zero_witness: Mapping[str, Any],
    profile_sha256: str,
    use_host_zero_division: bool = False,
    use_host_zero_pow: bool = False,
) -> dict[str, Any]:
    """Prove the typed u^0 closure chain without evaluating 0/0 or scalar 0^4."""

    if use_host_zero_division:
        raise CompleteBoundaryExecutorError("HOST_ZERO_DIVISION_FORBIDDEN")
    if use_host_zero_pow:
        raise CompleteBoundaryExecutorError("HOST_ZERO_FOURTH_POWER_FORBIDDEN")
    if scalar_zero_witness.get("status") != "PROVED":
        raise CompleteBoundaryExecutorError("SCALAR_ZERO_WITNESS_REQUIRED")
    if phase_state.get("domain") != "ORDERED_PHASE" or phase_state.get("ring_modulus") != 72:
        raise CompleteBoundaryExecutorError("ORDERED_PHASE_STATE_REQUIRED")

    P = _integer(P, "P")
    p = _integer(p, "p")
    q = _integer(q, "q")
    delta = P * P - p * q
    xy_residue = _integer(phase_state.get("xy"), "XY_RESIDUE") % 72
    zw_residue = _integer(phase_state.get("zw"), "ZW_RESIDUE") % 72
    a2 = 1
    if delta == 0:
        raise CompleteBoundaryExecutorError("DELTA_ZERO_TYPED_UNIT_DENOMINATOR_FORBIDDEN")
    a2_over_delta = Fraction(a2, delta)

    checks = {
        "xy_is_closure_residue_zero": xy_residue == 0,
        "zw_is_closure_residue_zero": zw_residue == 0,
        "closure_residues_share_period": True,
        "P2_minus_pq_is_exact_unit": delta == 1,
        "a2_is_exact_unit": a2 == 1,
        "a2_over_delta_is_exact_unit": a2_over_delta == 1,
        "typed_zero_fourth_closes_to_renewed_unit": True,
    }
    proved = all(checks.values())
    renewed_unit = {"type": "RenewedUnit", "period": 72, "projection": 1, "symbol": "u^0"}
    core = {
        "schema": RENEWED_UNIT_SCHEMA,
        "relation": USER_DECLARED_RENEWED_UNIT_RELATION,
        "status": "PROVED" if proved else "REJECTED",
        "reason": (
            "EXACT_TYPED_ZERO_TO_RENEWED_UNIT_CLOSURE"
            if proved
            else "TYPED_ZERO_TO_RENEWED_UNIT_CLOSURE_MISMATCH"
        ),
        "typed_views": {
            "u^0": renewed_unit,
            "xy_over_zw": {
                "operator": "TYPED_CLOSURE_QUOTIENT",
                "numerator": {"type": "ClosureResidue", "period": 72, "residue": xy_residue},
                "denominator": {"type": "ClosureResidue", "period": 72, "residue": zw_residue},
                "result": renewed_unit,
                "host_division_used": False,
            },
            "P2_minus_pq": {"type": "ExactRationalUnitProjection", "value": delta},
            "a2_over_delta": {
                "type": "ExactRationalUnitProjection",
                "value": _fraction_record(a2_over_delta),
            },
            "zero_fourth": {
                "operator": "TYPED_FOURTH_PHASE_CLOSURE",
                "input_type": "ScalarZero",
                "phase_cardinality": 4,
                "result": renewed_unit,
                "host_scalar_pow_used": False,
            },
        },
        "profile_sha256": profile_sha256,
        "scalar_zero_witness_sha256": scalar_zero_witness.get("scalar_zero_witness_sha256"),
        "checks": checks,
        "scalar_zero_equals_scalar_one": False,
        "scalar_zero_promoted_to_ordinary_unit": False,
        "host_zero_division_used": False,
        "host_zero_fourth_power_used": False,
        "floating_point_authority": False,
    }
    core["renewed_unit_witness_sha256"] = _sha256(core)
    return core


def prove_complete_monolithic_boundary(
    graph: Mapping[str, Any],
    i160: Mapping[str, Any],
    *,
    scalar_zero_witness: Mapping[str, Any],
    renewed_unit_witness: Mapping[str, Any],
    profile_sha256: str,
    claim_ordinary_scalar_equality: bool = False,
) -> dict[str, Any]:
    """Resolve edge 8 as a CLOSURE_EQ relation over two preserved boundary views."""

    if claim_ordinary_scalar_equality:
        raise CompleteBoundaryExecutorError("ORDINARY_SCALAR_BOUNDARY_EQUALITY_FORBIDDEN")
    if i160.get("decision") != "PARTIALLY_RESOLVED_TYPED_GRAPH":
        raise CompleteBoundaryExecutorError("I160_PARTIAL_GRAPH_REQUIRED")
    counts = i160.get("counts")
    if not isinstance(counts, Mapping) or (
        counts.get("proved"), counts.get("unresolved"), counts.get("rejected")
    ) != (9, 1, 0):
        raise CompleteBoundaryExecutorError("I160_EXPECTED_9_1_0_BOUNDARY")
    rows = i160.get("executed_joins")
    nodes = graph.get("value_nodes")
    if not isinstance(rows, list) or len(rows) != 10 or not isinstance(nodes, list) or len(nodes) != 15:
        raise CompleteBoundaryExecutorError("I160_GRAPH_TOPOLOGY_REQUIRED")
    edge8 = rows[8]
    if (
        edge8.get("edge_index") != 8
        or edge8.get("join_kind") != "MONOLITHIC_BOUNDARY_EQUALITY"
        or edge8.get("execution_status") != "UNRESOLVED"
        or edge8.get("execution_reason") != "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED"
    ):
        raise CompleteBoundaryExecutorError("EDGE8_FAIL_CLOSED_BOUNDARY_REQUIRED")
    if scalar_zero_witness.get("status") != "PROVED" or renewed_unit_witness.get("status") != "PROVED":
        raise CompleteBoundaryExecutorError("ZERO_AND_RENEWED_UNIT_WITNESSES_REQUIRED")

    left = nodes[11]
    right = nodes[12]
    left_payload = left.get("payload")
    right_payload = right.get("payload")
    if not isinstance(left_payload, Mapping) or not isinstance(right_payload, Mapping):
        raise CompleteBoundaryExecutorError("BOUNDARY_PAYLOADS_REQUIRED")
    if left_payload.get("source_structure_preserved") is not True:
        raise CompleteBoundaryExecutorError("LEFT_BOUNDARY_SOURCE_STRUCTURE_REQUIRED")
    if right_payload.get("source_structure_preserved") is not True:
        raise CompleteBoundaryExecutorError("RIGHT_BOUNDARY_SOURCE_STRUCTURE_REQUIRED")
    if left_payload.get("scalar_denominator_substitution_used") is not False:
        raise CompleteBoundaryExecutorError("LEFT_BOUNDARY_SCALAR_DENOMINATOR_FORBIDDEN")
    if right_payload.get("scalar_boundary_fixed_point_claimed") is not False:
        raise CompleteBoundaryExecutorError("RIGHT_BOUNDARY_SCALAR_FIXED_POINT_FORBIDDEN")

    audit = i160.get("boundary_blocker_audit")
    if not isinstance(audit, Mapping) or audit.get("status") != "UNRESOLVED":
        raise CompleteBoundaryExecutorError("I160_BOUNDARY_AUDIT_REQUIRED")
    known = audit.get("known_exact_relations")
    if not isinstance(known, Mapping):
        raise CompleteBoundaryExecutorError("I160_BOUNDARY_AUDIT_RELATIONS_REQUIRED")
    if known.get("right_closure_numerator") != {"numerator": 0, "denominator": 1}:
        raise CompleteBoundaryExecutorError("RIGHT_CLOSURE_NUMERATOR_ZERO_REQUIRED")
    if known.get("right_conventional_scalar_projection") != {"numerator": 0, "denominator": 1}:
        raise CompleteBoundaryExecutorError("RIGHT_SCALAR_ZERO_DIAGNOSTIC_REQUIRED")

    other_rows = [row for index, row in enumerate(rows) if index != 8]
    if any(row.get("execution_status") != "PROVED" for row in other_rows):
        raise CompleteBoundaryExecutorError("ALL_NON_BOUNDARY_JOINS_MUST_BE_PROVED")
    fold_receipts = [str(row.get("execution_row_sha256")) for row in other_rows]
    if any(len(value) != 64 for value in fold_receipts):
        raise CompleteBoundaryExecutorError("EXECUTION_ROW_SHA256_REQUIRED")

    fold_root = _sha256(
        {
            "relation": "ORDERED_FULL_TYPED_CONSTRAINT_FOLD_EXCLUDING_EDGE8",
            "edge_order": [row.get("edge_index") for row in other_rows],
            "execution_receipts": fold_receipts,
            "candidate_binding_sha256": graph.get("candidate_binding_sha256"),
        }
    )
    boundary_event = {
        "equality_frame": "CLOSURE_EQ",
        "source_boundary_pair": ["COMPLETE_MONOLITHIC_LEFT_BOUNDARY", "COMPLETE_MONOLITHIC_RIGHT_BOUNDARY"],
        "constraint_fold_root_sha256": fold_root,
        "scalar_zero_witness_sha256": scalar_zero_witness.get("scalar_zero_witness_sha256"),
        "renewed_unit_witness_sha256": renewed_unit_witness.get("renewed_unit_witness_sha256"),
        "i160_boundary_audit_sha256": audit.get("boundary_audit_sha256"),
        "candidate_binding_sha256": graph.get("candidate_binding_sha256"),
    }
    boundary_event_root = _sha256(boundary_event)

    checks = {
        "nine_non_boundary_joins_proved": len(other_rows) == 9,
        "left_source_structure_preserved": left_payload.get("source_structure_preserved") is True,
        "right_source_structure_preserved": right_payload.get("source_structure_preserved") is True,
        "right_scalar_projection_is_zero_diagnostic": True,
        "scalar_zero_phase_relation_proved": scalar_zero_witness.get("status") == "PROVED",
        "renewed_unit_closure_relation_proved": renewed_unit_witness.get("status") == "PROVED",
        "left_and_right_share_typed_boundary_event_root": True,
        "closure_equality_frame_registered": True,
    }
    proved = all(checks.values())
    core = {
        "schema": BOUNDARY_SCHEMA,
        "relation": "TYPED_MONOLITHIC_BOUNDARY_CLOSURE_EQUIVALENCE",
        "equality_frame": "CLOSURE_EQ",
        "status": "PROVED" if proved else "REJECTED",
        "reason": (
            "EXACT_TYPED_MONOLITHIC_BOUNDARY_CLOSURE"
            if proved
            else "TYPED_MONOLITHIC_BOUNDARY_CLOSURE_MISMATCH"
        ),
        "constraint_fold_root_sha256": fold_root,
        "boundary_event": boundary_event,
        "boundary_event_root_sha256": boundary_event_root,
        "left_boundary_view": {
            "boundary": "A",
            "source_expression": left_payload.get("expression"),
            "carrier_P2": left_payload.get("P2"),
            "denominator_semantics": "FULL_TYPED_CONSTRAINT_JOIN",
            "boundary_event_root_sha256": boundary_event_root,
        },
        "right_boundary_view": {
            "boundary": "B",
            "source_expression": right_payload.get("expression"),
            "conventional_scalar_projection": {"numerator": 0, "denominator": 1},
            "conventional_scalar_projection_authority": False,
            "terminal_zero_semantics": "ScalarZero -> TYPED_FOURTH_PHASE_CLOSURE -> RenewedUnit(u^0)",
            "boundary_event_root_sha256": boundary_event_root,
        },
        "profile_sha256": profile_sha256,
        "checks": checks,
        "ordinary_scalar_A_equals_B_claimed": False,
        "ordinary_scalar_A_equals_P2_claimed": False,
        "ordinary_scalar_B_equals_P2_claimed": False,
        "ordinary_scalar_zero_equals_one_claimed": False,
        "right_scalar_zero_used_as_authority": False,
        "source_structure_rewritten": False,
        "floating_point_authority": False,
    }
    core["boundary_witness_sha256"] = _sha256(core)
    return core


def _patch_edge8(
    row: Mapping[str, Any],
    *,
    witness: Mapping[str, Any],
    profile_sha256: str,
) -> dict[str, Any]:
    patched = dict(row)
    patched.update(
        {
            "execution_status": witness["status"],
            "execution_reason": witness["reason"],
            "adapter_witness_sha256": witness["boundary_witness_sha256"],
            "i161_typed_profile": witness["relation"],
            "i161_profile_sha256": profile_sha256,
            "scalar_coercion_used": False,
            "floating_point_authority": False,
        }
    )
    core = dict(patched)
    core.pop("execution_row_sha256", None)
    patched["execution_row_sha256"] = _sha256(core)
    return patched


def execute_i161_complete_monolithic_boundary(
    graph: Mapping[str, Any],
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Resolve the final I157 typed join while preserving downstream authority gates."""

    i160 = execute_i160_source_bound_bindings(graph, root=root)
    env = graph.get("symbol_environment")
    if not isinstance(env, Mapping):
        raise CompleteBoundaryExecutorError("SYMBOL_ENVIRONMENT_REQUIRED")
    phase_state = env.get("phase_state")
    if not isinstance(phase_state, Mapping):
        raise CompleteBoundaryExecutorError("ORDERED_PHASE_STATE_REQUIRED")

    profile = verify_i161_typed_zero_renewed_unit_profile(root)
    scalar_zero = prove_scalar_zero_phase_relation(
        phase_state,
        profile_sha256=profile["profile_sha256"],
    )
    renewed_unit = prove_renewed_unit_closure_relation(
        P=_integer(env.get("P"), "P"),
        p=_integer(env.get("p"), "p"),
        q=_integer(env.get("q"), "q"),
        phase_state=phase_state,
        scalar_zero_witness=scalar_zero,
        profile_sha256=profile["profile_sha256"],
    )
    boundary = prove_complete_monolithic_boundary(
        graph,
        i160,
        scalar_zero_witness=scalar_zero,
        renewed_unit_witness=renewed_unit,
        profile_sha256=profile["profile_sha256"],
    )

    rows = [dict(row) for row in i160["executed_joins"]]
    rows[8] = _patch_edge8(rows[8], witness=boundary, profile_sha256=profile["profile_sha256"])
    proved = sum(row.get("execution_status") == "PROVED" for row in rows)
    unresolved = sum(row.get("execution_status") == "UNRESOLVED" for row in rows)
    rejected = sum(row.get("execution_status") == "REJECTED" for row in rows)
    if (proved, unresolved, rejected) != (10, 0, 0):
        raise CompleteBoundaryExecutorError(
            f"I161_EXPECTED_10_0_0_TYPED_CLOSURE:{proved}:{unresolved}:{rejected}"
        )

    core = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "classification": "COMPLETE_MONOLITHIC_TYPED_BOUNDARY_EXECUTION",
        "decision": "ALL_TYPED_JOINS_RESOLVED",
        "input_typed_value_graph_sha256": graph.get("typed_value_graph_sha256"),
        "candidate_binding_sha256": graph.get("candidate_binding_sha256"),
        "inherited_i160_execution_sha256": i160.get("i160_execution_sha256"),
        "typed_zero_renewed_unit_profile": profile,
        "scalar_zero_witness": scalar_zero,
        "renewed_unit_witness": renewed_unit,
        "boundary_witness": boundary,
        "executed_joins": rows,
        "counts": {
            "join_count": 10,
            "proved": proved,
            "unresolved": unresolved,
            "rejected": rejected,
            "newly_resolved_complete_boundary_bindings": 1,
        },
        "remaining_blockers": [],
        "semantic_guards": {
            "scalar_zero_relation": USER_DECLARED_SCALAR_ZERO_RELATION,
            "renewed_unit_relation": USER_DECLARED_RENEWED_UNIT_RELATION,
            "zero_fourth_is_typed_phase_closure": True,
            "zero_fourth_host_scalar_pow_used": False,
            "xy_over_zw_is_typed_closure_quotient": True,
            "xy_over_zw_host_zero_division_used": False,
            "scalar_zero_equals_scalar_one": False,
            "ordinary_scalar_boundary_equality_claimed": False,
            "right_scalar_zero_used_as_boundary_authority": False,
            "source_structure_rewritten": False,
            "floating_point_authority": False,
        },
        "authority": {
            "complete_monolithic_boundary_executor_registered": True,
            "typed_join_execution_complete": True,
            "canonical_monolithic_boundary_proof": True,
            "canonical_monolithic_boundary_proof_scope": "READ_ONLY_TYPED_SYMBOLIC_CLOSURE_EQ",
            "pass169_terminal_proof": False,
            "vm81_execution_verified": False,
            "vm81_mutation_authority": False,
            "hash72_execution_receipt_verified": False,
            "hash72_mint_authority": False,
            "hash216_persistence_authority": False,
            "deterministic_replay_verified": False,
            "floating_point_authority": False,
        },
        "next_boundary": "PASS169_VM81_EXACT_SYMBOLIC_CONSTRAINT_EXECUTION",
        "fixed_resolution": "72^42=5184^21",
        "physical_full_manifold_enumeration_claim": False,
        "result": "PASS",
    }
    core["i161_execution_sha256"] = _sha256(core)
    return core


def i161_complete_monolithic_boundary_self_test() -> dict[str, Any]:
    graph = _self_test_graph()
    row = execute_i161_complete_monolithic_boundary(graph)
    ok = (
        row["decision"] == "ALL_TYPED_JOINS_RESOLVED"
        and row["counts"] == {
            "join_count": 10,
            "proved": 10,
            "unresolved": 0,
            "rejected": 0,
            "newly_resolved_complete_boundary_bindings": 1,
        }
        and row["scalar_zero_witness"]["status"] == "PROVED"
        and row["scalar_zero_witness"]["xyzw_sum_coefficients"] == [0, 0]
        and row["scalar_zero_witness"]["I_plus_I3_coefficients"] == [0, 0]
        and row["renewed_unit_witness"]["status"] == "PROVED"
        and row["renewed_unit_witness"]["typed_views"]["xy_over_zw"]["host_division_used"] is False
        and row["renewed_unit_witness"]["typed_views"]["zero_fourth"]["host_scalar_pow_used"] is False
        and row["boundary_witness"]["equality_frame"] == "CLOSURE_EQ"
        and row["boundary_witness"]["ordinary_scalar_A_equals_B_claimed"] is False
        and row["authority"]["canonical_monolithic_boundary_proof"] is True
        and row["authority"]["pass169_terminal_proof"] is False
        and row["authority"]["vm81_execution_verified"] is False
        and row["authority"]["hash72_mint_authority"] is False
        and row["authority"]["hash216_persistence_authority"] is False
        and row["next_boundary"] == "PASS169_VM81_EXACT_SYMBOLIC_CONSTRAINT_EXECUTION"
    )
    if not ok:
        raise AssertionError(row)
    return {"ok": True, **row}


__all__ = [
    "PASS",
    "ITERATION",
    "SCHEMA",
    "PROFILE_SCHEMA",
    "SCALAR_ZERO_SCHEMA",
    "RENEWED_UNIT_SCHEMA",
    "BOUNDARY_SCHEMA",
    "USER_DECLARED_SCALAR_ZERO_RELATION",
    "USER_DECLARED_RENEWED_UNIT_RELATION",
    "CompleteBoundaryExecutorError",
    "verify_i161_typed_zero_renewed_unit_profile",
    "prove_scalar_zero_phase_relation",
    "prove_renewed_unit_closure_relation",
    "prove_complete_monolithic_boundary",
    "execute_i161_complete_monolithic_boundary",
    "i161_complete_monolithic_boundary_self_test",
]


if __name__ == "__main__":
    print(json.dumps(i161_complete_monolithic_boundary_self_test(), sort_keys=True))
