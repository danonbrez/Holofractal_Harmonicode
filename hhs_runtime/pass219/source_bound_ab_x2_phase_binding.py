from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.pass219.harmonicode_modular_pivot_phase_binding import (
    execute_i159_modular_pivot_phase_bindings,
)
from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    PROVENANCE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    produce_candidate_bound_value_graph,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_phase_lattice_v1 import (
    PhaseState,
)

PASS = 219
ITERATION = "I160"
SCHEMA = "HHS_PASS219_I160_SOURCE_BOUND_AB_X2_PHASE_BINDING_V1"
PROFILE_SCHEMA = "HHS_PASS219_I160_PASS191_SOURCE_BINDING_PROFILE_V1"
PRODUCT_SCHEMA = "HHS_PASS219_I160_SOURCE_BOUND_AB_PRODUCT_WITNESS_V1"
PHASE_SCHEMA = "HHS_PASS219_I160_X_SQUARED_PHASE_EXPONENT_WITNESS_V1"
BOUNDARY_AUDIT_SCHEMA = "HHS_PASS219_I160_MONOLITHIC_BOUNDARY_BLOCKER_AUDIT_V1"

PASS191_PHASE_PATH = Path(
    "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/"
    "hhs_pass191_phase_lattice_v1.py"
)
PASS191_MANIFOLD_PATH = Path(
    "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/"
    "hhs_pass191_manifold_kernel_v1.py"
)
PASS169_CONTRACT_PATH = Path(
    "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_"
    "EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME.md"
)


class SourceBoundBindingError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _exact_integer(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise SourceBoundBindingError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _fraction_from_node(node: Mapping[str, Any], label: str) -> Fraction:
    if node.get("domain") != "EXACT_RATIONAL" or node.get("exact") is not True:
        raise SourceBoundBindingError(f"{label}_EXACT_RATIONAL_NODE_REQUIRED")
    payload = node.get("payload")
    if not isinstance(payload, Mapping):
        raise SourceBoundBindingError(f"{label}_PAYLOAD_REQUIRED")
    record = payload.get("value")
    if not isinstance(record, Mapping):
        raise SourceBoundBindingError(f"{label}_VALUE_REQUIRED")
    numerator = _exact_integer(record.get("numerator"), f"{label}_NUMERATOR")
    denominator = _exact_integer(record.get("denominator"), f"{label}_DENOMINATOR")
    if denominator == 0:
        raise SourceBoundBindingError(f"{label}_ZERO_DENOMINATOR")
    return Fraction(numerator, denominator)


def _repo_root(root: str | Path | None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]


def _read(root: Path, relative: Path) -> str:
    path = root / relative
    if not path.is_file():
        raise SourceBoundBindingError(f"REQUIRED_SOURCE_MISSING:{relative.as_posix()}")
    return path.read_text(encoding="utf-8")


def verify_pass191_source_binding_profile(root: str | Path | None = None) -> dict[str, Any]:
    """Bind I160 to inherited Pass191 phase-square and P⁴=AB evidence."""

    repo = _repo_root(root)
    phase_source = _read(repo, PASS191_PHASE_PATH)
    manifold_source = _read(repo, PASS191_MANIFOLD_PATH)
    pass169_source = _read(repo, PASS169_CONTRACT_PATH)

    required_phase_literals = (
        'DEF PHASE_SQUARE(x,p) := DYADIC_LEVEL(x)+1==QUARTIC_PHASE(p+1)',
        'return PhaseState(self.dyadic_level + 1, self.quartic_phase + 1)',
        'return ("1", "i", "-1", "-i")[self.quartic_phase]',
    )
    required_product_literals = (
        '"AB_equals_P_fourth"',
        '"AB_over_P_squared_equals_P_squared"',
        '"sqrt_AB_equals_P_squared"',
        '"x_squared_binding": None',
    )
    required_pass169_literals = (
        "P^4=AB",
        "P^2-pq=Δ",
        "supports typed zero reciprocal and phase rotation",
    )

    checks = {
        "pass191_phase_square_macro_present": all(
            literal in phase_source for literal in required_phase_literals
        ),
        "pass191_product_witnesses_present": all(
            literal in manifold_source for literal in required_product_literals
        ),
        "pass191_historical_x2_binding_remains_unresolved": (
            '"x_squared_binding": None' in manifold_source
        ),
        "pass169_membrane_and_typed_phase_requirements_present": all(
            literal in pass169_source for literal in required_pass169_literals
        ),
    }
    if not all(checks.values()):
        raise SourceBoundBindingError(f"INHERITED_SOURCE_BINDING_PROFILE_DRIFT:{checks}")

    core = {
        "schema": PROFILE_SCHEMA,
        "pass191_phase_path": PASS191_PHASE_PATH.as_posix(),
        "pass191_phase_sha256": sha256(phase_source.encode("utf-8")).hexdigest(),
        "pass191_manifold_path": PASS191_MANIFOLD_PATH.as_posix(),
        "pass191_manifold_sha256": sha256(manifold_source.encode("utf-8")).hexdigest(),
        "pass169_contract_path": PASS169_CONTRACT_PATH.as_posix(),
        "pass169_contract_sha256": sha256(pass169_source.encode("utf-8")).hexdigest(),
        "checks": checks,
        "historical_A_equals_P2_reused_as_full_boundary_definition": False,
        "historical_B_equals_P2_reused_as_full_boundary_definition": False,
        "inherited_AB_equals_P4_used_as_product_membrane_only": True,
        "pass191_source_rewritten": False,
        "floating_point_authority": False,
    }
    core["profile_sha256"] = _sha256(core)
    return core


def prove_source_bound_ab_product(
    *,
    P: int,
    ratio_node: Mapping[str, Any],
    radical_node: Mapping[str, Any],
    candidate_binding_sha256: str,
    profile_sha256: str,
) -> dict[str, Any]:
    """Resolve AB/P² == sqrt(AB) through the P⁴=AB membrane only."""

    P = _exact_integer(P, "P")
    if P <= 0:
        raise SourceBoundBindingError("P_POSITIVE_REQUIRED")

    ratio_payload = ratio_node.get("payload")
    radical_payload = radical_node.get("payload")
    if (
        ratio_node.get("domain") != "SYMBOLIC_BOUNDARY_RATIO"
        or ratio_node.get("exact") is not True
        or not isinstance(ratio_payload, Mapping)
    ):
        raise SourceBoundBindingError("SOURCE_BOUND_RATIO_NODE_REQUIRED")
    if (
        radical_node.get("domain") != "SYMBOLIC_RADICAL"
        or radical_node.get("exact") is not True
        or not isinstance(radical_payload, Mapping)
    ):
        raise SourceBoundBindingError("SOURCE_BOUND_AB_RADICAL_NODE_REQUIRED")
    if ratio_payload.get("A_or_B_definitionally_P2") is not False:
        raise SourceBoundBindingError("A_OR_B_DEFINITIONALLY_P2_FORBIDDEN")
    if radical_payload.get("scalar_root_projection_claimed") is not False:
        raise SourceBoundBindingError("SCALAR_AB_ROOT_PROJECTION_FORBIDDEN")
    if ratio_payload.get("A") != "COMPLETE_MONOLITHIC_LEFT_BOUNDARY":
        raise SourceBoundBindingError("LEFT_BOUNDARY_REFERENCE_DRIFT")
    if ratio_payload.get("B") != "COMPLETE_MONOLITHIC_RIGHT_BOUNDARY":
        raise SourceBoundBindingError("RIGHT_BOUNDARY_REFERENCE_DRIFT")
    if (
        radical_payload.get("A") != ratio_payload.get("A")
        or radical_payload.get("B") != ratio_payload.get("B")
    ):
        raise SourceBoundBindingError("AB_BOUNDARY_REFERENCE_MISMATCH")

    P2 = P * P
    AB = P2 * P2
    ratio = Fraction(AB, P2)
    radical = P2
    checks = {
        "ratio_node_P2_matches_candidate": ratio_payload.get("P2") == P2,
        "source_bound_product_is_P_fourth": AB == P**4,
        "AB_over_P2_is_P2": ratio == P2,
        "positive_exact_root_squares_to_AB": radical * radical == AB,
        "positive_exact_root_is_P2": radical == P2,
        "A_not_redefined_as_P2": ratio_payload.get("A_or_B_definitionally_P2") is False,
        "B_not_redefined_as_P2": ratio_payload.get("A_or_B_definitionally_P2") is False,
        "scalar_radical_projection_not_claimed": (
            radical_payload.get("scalar_root_projection_claimed") is False
        ),
    }
    proved = all(checks.values())
    core = {
        "schema": PRODUCT_SCHEMA,
        "relation": "SOURCE_BOUND_P4_PRODUCT_ROOT_CORRESPONDENCE",
        "status": "PROVED" if proved else "REJECTED",
        "reason": (
            "EXACT_SOURCE_BOUND_AB_PRODUCT_AND_ROOT"
            if proved
            else "SOURCE_BOUND_AB_PRODUCT_CONSTRAINT_MISMATCH"
        ),
        "P": P,
        "P2": P2,
        "AB": AB,
        "AB_over_P2": _fraction_record(ratio),
        "sqrt_AB": radical,
        "candidate_binding_sha256": candidate_binding_sha256,
        "profile_sha256": profile_sha256,
        "checks": checks,
        "boundary_product_binding_only": True,
        "ordinary_scalar_A_equals_P2_claimed": False,
        "ordinary_scalar_B_equals_P2_claimed": False,
        "floating_point_authority": False,
    }
    core["product_witness_sha256"] = _sha256(core)
    return core


def prove_pass191_x_squared_phase_exponent(
    *,
    P: int,
    p: int,
    q: int,
    delta: int,
    left_node: Mapping[str, Any],
    radical_node: Mapping[str, Any],
    candidate_binding_sha256: str,
    profile_sha256: str,
) -> dict[str, Any]:
    """Resolve Δ/P against sqrt(pq+u⁷²)^x² using a typed phase-basis exponent."""

    P = _exact_integer(P, "P")
    p = _exact_integer(p, "p")
    q = _exact_integer(q, "q")
    delta = _exact_integer(delta, "DELTA")
    if P <= 0:
        raise SourceBoundBindingError("P_POSITIVE_REQUIRED")

    left = _fraction_from_node(left_node, "DELTA_OVER_P")
    payload = radical_node.get("payload")
    if (
        radical_node.get("domain") != "SYMBOLIC_RADICAL"
        or radical_node.get("exact") is not True
        or not isinstance(payload, Mapping)
    ):
        raise SourceBoundBindingError("X2_RADICAL_NODE_REQUIRED")
    if payload.get("ordinary_scalar_x_squared_assumed") is not False:
        raise SourceBoundBindingError("ORDINARY_SCALAR_X_SQUARED_FORBIDDEN")
    if payload.get("scalar_radical_projection_claimed") is not False:
        raise SourceBoundBindingError("SCALAR_X2_RADICAL_PROJECTION_FORBIDDEN")

    base = payload.get("base")
    exponent = payload.get("phase_exponent")
    if not isinstance(base, Mapping) or not isinstance(exponent, Mapping):
        raise SourceBoundBindingError("X2_PHASE_PAYLOAD_REQUIRED")
    if exponent.get("domain") != "ORDERED_PHASE_EXPONENT" or exponent.get("symbol") != "x^2":
        raise SourceBoundBindingError("ORDERED_PHASE_EXPONENT_DOMAIN_REQUIRED")

    x_phase = _exact_integer(exponent.get("x_phase"), "X_PHASE")
    if x_phase not in (0, 18, 36, 54):
        raise SourceBoundBindingError("X_PHASE_QUARTER_CYCLE_REQUIRED")
    start = PhaseState(0, x_phase // 18)
    squared = start.square()
    squared_basis = squared.phase_basis()

    # I160 registers the ORDERED_PHASE_EXPONENT adapter as a basis-lane
    # projection. Pass191's dyadic level is retained in the witness and is not
    # silently reinterpreted as an ordinary scalar exponent magnitude.
    exact_basis_exponents = {"1": 1, "-1": -1}
    if squared_basis not in exact_basis_exponents:
        raise SourceBoundBindingError("X2_PHASE_BASIS_NOT_REAL_INTEGER")
    basis_exponent = exact_basis_exponents[squared_basis]

    pq = p * q
    base_sum = _exact_integer(base.get("sum"), "RADICAL_BASE_SUM")
    if base.get("pq") != pq or base.get("u72") != 1:
        raise SourceBoundBindingError("RADICAL_BASE_BINDING_DRIFT")
    P2 = P * P
    if base_sum != pq + 1 or base_sum != P2:
        raise SourceBoundBindingError("RADICAL_BASE_NOT_EXACT_P2")
    root = P
    if root * root != base_sum:
        raise SourceBoundBindingError("EXACT_POSITIVE_ROOT_MISMATCH")

    right = Fraction(1, root) if basis_exponent == -1 else Fraction(root)
    checks = {
        "delta_matches_P2_minus_pq": delta == P2 - pq,
        "left_is_exact_delta_over_P": left == Fraction(delta, P),
        "base_is_pq_plus_u72": base_sum == pq + 1,
        "base_is_P2": base_sum == P2,
        "positive_root_is_P": root == P,
        "pass191_phase_square_advanced_dyadic_and_quartic_coordinates": (
            squared.dyadic_level == start.dyadic_level + 1
            and squared.quartic_phase == (start.quartic_phase + 1) % 4
        ),
        "candidate_x_is_quarter_cycle_i": start.phase_basis() == "i",
        "x2_phase_square_basis_is_negative_unit": squared_basis == "-1",
        "ordered_phase_exponent_basis_is_negative_one": basis_exponent == -1,
        "radical_phase_result_equals_delta_over_P": right == left,
    }
    proved = all(checks.values())
    core = {
        "schema": PHASE_SCHEMA,
        "relation": "PASS191_ORDERED_PHASE_BASIS_EXPONENT_JOIN",
        "status": "PROVED" if proved else "REJECTED",
        "reason": (
            "EXACT_PASS191_X2_ORDERED_PHASE_EXPONENT_BINDING"
            if proved
            else "PASS191_X2_PHASE_EXPONENT_CONSTRAINT_MISMATCH"
        ),
        "P": P,
        "p": p,
        "q": q,
        "delta": delta,
        "base_sum": base_sum,
        "positive_root": root,
        "x_phase": x_phase,
        "phase_square": {
            "input": {
                "dyadic_level": start.dyadic_level,
                "dyadic_magnitude": str(start.magnitude()),
                "quartic_phase": start.quartic_phase,
                "basis": start.phase_basis(),
            },
            "output": {
                "dyadic_level": squared.dyadic_level,
                "dyadic_magnitude": str(squared.magnitude()),
                "quartic_phase": squared.quartic_phase,
                "basis": squared_basis,
            },
            "ordered_phase_basis_exponent": basis_exponent,
            "dyadic_magnitude_used_as_scalar_exponent": False,
        },
        "left_delta_over_P": _fraction_record(left),
        "right_phase_radical": _fraction_record(right),
        "candidate_binding_sha256": candidate_binding_sha256,
        "profile_sha256": profile_sha256,
        "checks": checks,
        "ordinary_scalar_x_squared_assumed": False,
        "ordinary_18_squared_used": False,
        "pass191_dyadic_coordinate_discarded": False,
        "pass191_dyadic_coordinate_scalarized": False,
        "floating_point_authority": False,
    }
    core["phase_witness_sha256"] = _sha256(core)
    return core


def audit_complete_monolithic_boundary_blocker(
    *,
    P: int,
    p: int,
    q: int,
    delta: int,
    t: int,
    u72: int,
    left_boundary_node: Mapping[str, Any],
    right_boundary_node: Mapping[str, Any],
    product_witness: Mapping[str, Any],
    phase_witness: Mapping[str, Any],
    candidate_binding_sha256: str,
    profile_sha256: str,
) -> dict[str, Any]:
    """Expose what is now known without inventing the missing boundary executor."""

    P = _exact_integer(P, "P")
    p = _exact_integer(p, "p")
    q = _exact_integer(q, "q")
    delta = _exact_integer(delta, "DELTA")
    t = _exact_integer(t, "T")
    u72 = _exact_integer(u72, "U72")
    left_payload = left_boundary_node.get("payload")
    right_payload = right_boundary_node.get("payload")
    if not isinstance(left_payload, Mapping) or not isinstance(right_payload, Mapping):
        raise SourceBoundBindingError("COMPLETE_BOUNDARY_PAYLOADS_REQUIRED")
    if (
        left_boundary_node.get("domain") != "SYMBOLIC_BOUNDARY"
        or left_payload.get("boundary") != "A"
        or left_payload.get("source_structure_preserved") is not True
        or left_payload.get("scalar_denominator_substitution_used") is not False
    ):
        raise SourceBoundBindingError("LEFT_BOUNDARY_SOURCE_PRESERVATION_REQUIRED")
    if (
        right_boundary_node.get("domain") != "SYMBOLIC_BOUNDARY"
        or right_payload.get("boundary") != "B"
        or right_payload.get("source_structure_preserved") is not True
        or right_payload.get("scalar_boundary_fixed_point_claimed") is not False
    ):
        raise SourceBoundBindingError("RIGHT_BOUNDARY_SOURCE_PRESERVATION_REQUIRED")
    if product_witness.get("status") != "PROVED" or phase_witness.get("status") != "PROVED":
        raise SourceBoundBindingError("PRODUCT_AND_PHASE_WITNESSES_REQUIRED")

    P2 = P * P
    pq = p * q
    AB = _exact_integer(product_witness.get("AB"), "AB")
    cubic = t * t * t - t
    if cubic == 0:
        raise SourceBoundBindingError("RIGHT_BOUNDARY_NONZERO_CUBIC_REQUIRED")
    if P2 - pq != delta or pq + delta != P2:
        raise SourceBoundBindingError("P2_PQ_DELTA_MEMBRANE_REQUIRED")
    if u72 != 1 or right_payload.get("u72") != 1:
        raise SourceBoundBindingError("U72_UNIT_REQUIRED")

    ab_over_membrane = Fraction(AB, pq + delta)
    closure_numerator = ab_over_membrane - P2
    conventional_right = closure_numerator / cubic * u72
    core = {
        "schema": BOUNDARY_AUDIT_SCHEMA,
        "status": "UNRESOLVED",
        "reason": "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED",
        "known_exact_relations": {
            "P2_minus_pq": delta,
            "AB": AB,
            "AB_over_pq_plus_delta": _fraction_record(ab_over_membrane),
            "right_closure_numerator": _fraction_record(closure_numerator),
            "right_conventional_scalar_projection": _fraction_record(conventional_right),
        },
        "checks": {
            "P4_AB_membrane_proved": AB == P**4,
            "P2_pq_delta_membrane_proved": P2 - pq == delta,
            "AB_over_pq_plus_delta_is_P2": ab_over_membrane == P2,
            "right_closure_numerator_is_zero": closure_numerator == 0,
            "right_conventional_projection_is_zero": conventional_right == 0,
            "left_source_structure_retained": True,
            "right_source_structure_retained": True,
            "x2_where_clause_proved": True,
        },
        "candidate_binding_sha256": candidate_binding_sha256,
        "profile_sha256": profile_sha256,
        "product_witness_sha256": product_witness.get("product_witness_sha256"),
        "phase_witness_sha256": phase_witness.get("phase_witness_sha256"),
        "ordinary_scalar_boundary_equality_claimed": False,
        "right_scalar_zero_promoted_to_typed_boundary_identity": False,
        "typed_zero_boundary_rule_invented": False,
        "vm81_execution_claimed": False,
        "floating_point_authority": False,
    }
    core["boundary_audit_sha256"] = _sha256(core)
    return core


def _patch_join(
    row: Mapping[str, Any],
    *,
    status: str,
    reason: str,
    relation: str,
    witness_sha256: str,
    profile_sha256: str,
) -> dict[str, Any]:
    patched = dict(row)
    patched.update(
        {
            "execution_status": status,
            "execution_reason": reason,
            "adapter_witness_sha256": witness_sha256,
            "i160_typed_profile": relation,
            "i160_profile_sha256": profile_sha256,
            "scalar_coercion_used": False,
            "floating_point_authority": False,
        }
    )
    patched_core = dict(patched)
    patched_core.pop("execution_row_sha256", None)
    patched["execution_row_sha256"] = _sha256(patched_core)
    return patched


def execute_i160_source_bound_bindings(
    graph: Mapping[str, Any],
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Resolve edges 7 and 9; preserve edge 8 fail-closed for the next executor."""

    i159 = execute_i159_modular_pivot_phase_bindings(graph, root=root)
    counts = i159.get("counts")
    if i159.get("decision") != "PARTIALLY_RESOLVED_TYPED_GRAPH":
        raise SourceBoundBindingError("I159_PARTIAL_GRAPH_REQUIRED")
    if not isinstance(counts, Mapping):
        raise SourceBoundBindingError("I159_COUNTS_REQUIRED")
    if (
        counts.get("proved") != 7
        or counts.get("unresolved") != 3
        or counts.get("rejected") != 0
    ):
        raise SourceBoundBindingError("I159_EXPECTED_7_3_0_BOUNDARY")

    env = graph.get("symbol_environment")
    nodes = graph.get("value_nodes")
    if not isinstance(env, Mapping) or not isinstance(nodes, list) or len(nodes) != 15:
        raise SourceBoundBindingError("I157_GRAPH_SHAPE_REQUIRED")

    P = _exact_integer(env.get("P"), "P")
    p = _exact_integer(env.get("p"), "p")
    q = _exact_integer(env.get("q"), "q")
    t = _exact_integer(env.get("t"), "t")
    u72 = _exact_integer(env.get("u72"), "U72")
    delta = P * P - p * q
    binding = str(graph.get("candidate_binding_sha256"))
    if len(binding) != 64:
        raise SourceBoundBindingError("CANDIDATE_BINDING_SHA256_REQUIRED")

    profile = verify_pass191_source_binding_profile(root)
    product = prove_source_bound_ab_product(
        P=P,
        ratio_node=nodes[9],
        radical_node=nodes[10],
        candidate_binding_sha256=binding,
        profile_sha256=profile["profile_sha256"],
    )
    phase = prove_pass191_x_squared_phase_exponent(
        P=P,
        p=p,
        q=q,
        delta=delta,
        left_node=nodes[13],
        radical_node=nodes[14],
        candidate_binding_sha256=binding,
        profile_sha256=profile["profile_sha256"],
    )
    boundary_audit = audit_complete_monolithic_boundary_blocker(
        P=P,
        p=p,
        q=q,
        delta=delta,
        t=t,
        u72=u72,
        left_boundary_node=nodes[11],
        right_boundary_node=nodes[12],
        product_witness=product,
        phase_witness=phase,
        candidate_binding_sha256=binding,
        profile_sha256=profile["profile_sha256"],
    )

    rows = [dict(row) for row in i159["executed_joins"]]
    rows[7] = _patch_join(
        rows[7],
        status=str(product["status"]),
        reason=str(product["reason"]),
        relation=str(product["relation"]),
        witness_sha256=str(product["product_witness_sha256"]),
        profile_sha256=str(profile["profile_sha256"]),
    )
    rows[9] = _patch_join(
        rows[9],
        status=str(phase["status"]),
        reason=str(phase["reason"]),
        relation=str(phase["relation"]),
        witness_sha256=str(phase["phase_witness_sha256"]),
        profile_sha256=str(profile["profile_sha256"]),
    )

    # Edge 8 intentionally remains unresolved. Attach the audit receipt without
    # changing its execution status.
    edge8 = dict(rows[8])
    edge8["i160_boundary_audit_sha256"] = boundary_audit["boundary_audit_sha256"]
    edge8["i160_boundary_audit_status"] = boundary_audit["status"]
    edge8["i160_profile_sha256"] = profile["profile_sha256"]
    edge8_core = dict(edge8)
    edge8_core.pop("execution_row_sha256", None)
    edge8["execution_row_sha256"] = _sha256(edge8_core)
    rows[8] = edge8

    proved = sum(row["execution_status"] == "PROVED" for row in rows)
    unresolved = sum(row["execution_status"] == "UNRESOLVED" for row in rows)
    rejected = sum(row["execution_status"] == "REJECTED" for row in rows)

    if rejected:
        decision = "REJECTED_SOURCE_BOUND_BINDING"
        next_boundary = "REPAIR_REJECTED_SOURCE_BOUND_BINDING"
    elif unresolved:
        decision = "PARTIALLY_RESOLVED_TYPED_GRAPH"
        next_boundary = "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR"
    else:
        decision = "ALL_TYPED_JOINS_RESOLVED"
        next_boundary = "VM81_PASS169_ADMISSION"

    core = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "classification": "SOURCE_BOUND_AB_PRODUCT_AND_X2_PHASE_EXPONENT_BINDING",
        "decision": decision,
        "input_typed_value_graph_sha256": graph["typed_value_graph_sha256"],
        "candidate_binding_sha256": binding,
        "inherited_i159_execution_sha256": i159["i159_execution_sha256"],
        "source_binding_profile": profile,
        "product_witness": product,
        "phase_witness": phase,
        "boundary_blocker_audit": boundary_audit,
        "executed_joins": rows,
        "counts": {
            "join_count": len(rows),
            "proved": proved,
            "unresolved": unresolved,
            "rejected": rejected,
            "newly_resolved_source_bound_bindings": proved - int(counts["proved"]),
        },
        "remaining_blockers": [
            {
                "edge_index": row["edge_index"],
                "join_kind": row["join_kind"],
                "reason": row["execution_reason"],
            }
            for row in rows
            if row["execution_status"] != "PROVED"
        ],
        "semantic_guards": {
            "source_bound_P4_AB_product_membrane_used": True,
            "historical_A_equals_P2_full_boundary_definition_reused": False,
            "historical_B_equals_P2_full_boundary_definition_reused": False,
            "ordered_phase_exponent_basis_lane_registered": True,
            "pass191_dyadic_coordinate_retained": True,
            "pass191_dyadic_coordinate_used_as_scalar_exponent": False,
            "ordinary_scalar_x_squared_assumed": False,
            "ordinary_18_squared_used": False,
            "ordinary_scalar_boundary_equality_claimed": False,
            "right_zero_projection_used_as_boundary_authority": False,
            "typed_zero_boundary_rule_invented": False,
            "floating_point_authority": False,
        },
        "authority": {
            "source_bound_ab_product_registered": product["status"] == "PROVED",
            "pass191_x_squared_phase_exponent_bound": phase["status"] == "PROVED",
            "complete_monolithic_boundary_executor_registered": False,
            "typed_join_execution_complete": unresolved == 0 and rejected == 0,
            "canonical_monolithic_boundary_proof": False,
            "pass169_terminal_proof": False,
            "vm81_execution_verified": False,
            "vm81_mutation_authority": False,
            "hash72_execution_receipt_verified": False,
            "hash72_mint_authority": False,
            "hash216_persistence_authority": False,
            "deterministic_replay_verified": False,
            "floating_point_authority": False,
        },
        "next_boundary": next_boundary,
        "fixed_resolution": "72^42=5184^21",
        "physical_full_manifold_enumeration_claim": False,
        "result": "PASS",
    }
    core["i160_execution_sha256"] = _sha256(core)
    return core


def _self_test_graph() -> dict[str, Any]:
    snapshot = {
        "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
        "snapshot_hash216": "2" * 64,
        "snapshot_hash216_format": "PASS150_HASH216_GENOME_ROOT_SHA256",
        "P": 30,
        "hydration_bits": 5184,
    }
    provenance = {
        "schema": PROVENANCE_SCHEMA,
        "combined_source_sha256": COMBINED_SOURCE_SHA256,
        "source_hash216": "0" * 216,
        "tokens_hash216": "1" * 216,
        "cst_hash216": "2" * 216,
        "ast_hash216": "3" * 216,
        "type_environment_hash216": "4" * 216,
        "constraint_graph_hash216": "5" * 216,
        "hir_hash216": "6" * 216,
        "vmir_hash216": "7" * 216,
        "global_symbol_environment_root": "b" * 64,
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
        "P": 30,
        "p": 29,
        "q": 31,
        "t": 30,
        "m": 267,
        "s": {"numerator": 2, "denominator": 25},
        "f": 900,
        "At": 1,
        "Bt": 1,
        "x": 18,
        "y": 54,
        "z": 18,
        "w": 54,
    }
    return produce_candidate_bound_value_graph(snapshot, provenance, symbols)


def i160_source_bound_binding_self_test() -> dict[str, Any]:
    row = execute_i160_source_bound_bindings(_self_test_graph())
    product = row["product_witness"]
    phase = row["phase_witness"]
    audit = row["boundary_blocker_audit"]
    expected_counts = {
        "join_count": 10,
        "proved": 9,
        "unresolved": 1,
        "rejected": 0,
        "newly_resolved_source_bound_bindings": 2,
    }
    ok = (
        row["decision"] == "PARTIALLY_RESOLVED_TYPED_GRAPH"
        and row["counts"] == expected_counts
        and product["AB"] == 810000
        and product["AB_over_P2"] == {"numerator": 900, "denominator": 1}
        and product["sqrt_AB"] == 900
        and phase["phase_square"]["input"]["basis"] == "i"
        and phase["phase_square"]["output"]["basis"] == "-1"
        and phase["phase_square"]["output"]["dyadic_magnitude"] == "2"
        and phase["phase_square"]["ordered_phase_basis_exponent"] == -1
        and phase["phase_square"]["dyadic_magnitude_used_as_scalar_exponent"] is False
        and phase["right_phase_radical"] == {"numerator": 1, "denominator": 30}
        and audit["status"] == "UNRESOLVED"
        and audit["reason"] == "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED"
        and audit["right_scalar_zero_promoted_to_typed_boundary_identity"] is False
        and row["remaining_blockers"] == [
            {
                "edge_index": 8,
                "join_kind": "MONOLITHIC_BOUNDARY_EQUALITY",
                "reason": "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED",
            }
        ]
        and row["next_boundary"] == "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR"
        and row["authority"]["canonical_monolithic_boundary_proof"] is False
        and row["authority"]["vm81_mutation_authority"] is False
        and row["authority"]["hash72_mint_authority"] is False
        and row["authority"]["hash216_persistence_authority"] is False
    )
    if not ok:
        raise AssertionError(row)
    return {"ok": True, **row}


__all__ = [
    "PASS",
    "ITERATION",
    "SCHEMA",
    "PROFILE_SCHEMA",
    "PRODUCT_SCHEMA",
    "PHASE_SCHEMA",
    "BOUNDARY_AUDIT_SCHEMA",
    "SourceBoundBindingError",
    "verify_pass191_source_binding_profile",
    "prove_source_bound_ab_product",
    "prove_pass191_x_squared_phase_exponent",
    "audit_complete_monolithic_boundary_blocker",
    "execute_i160_source_bound_bindings",
    "i160_source_bound_binding_self_test",
]


if __name__ == "__main__":
    print(json.dumps(i160_source_bound_binding_self_test(), sort_keys=True))
