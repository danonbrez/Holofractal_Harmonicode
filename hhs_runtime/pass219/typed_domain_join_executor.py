"""Pass 219 I158 typed-domain join execution membrane.

Consumes one exact I157 typed candidate graph and executes only domain adapters
whose semantics are already registered and independently checkable.

I158 closes the two modular-pivot joins through an explicit rational->modular
projection witness.  It deliberately does not claim the still-missing
AB-boundary product evaluator, complete monolithic A/B executor, or Pass191
x^2 phase-exponent binding.

No VM81 mutation, Hash72 mint, Hash216 persistence, or Pass169 terminal proof
authority is created here.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    EDGE_SPECS,
    SCHEMA as I157_SCHEMA,
    TERM_NAMES,
)

PASS = 219
ITERATION = "I158"
SCHEMA = "HHS_PASS219_I158_TYPED_DOMAIN_JOIN_EXECUTION_V1"
MODULAR_WITNESS_SCHEMA = "HHS_PASS219_I158_RATIONAL_TO_MODULAR_PROJECTION_V1"

PASS191_KERNEL_PATH = Path(
    "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/"
    "hhs_pass191_manifold_kernel_v1.py"
)
PASS169_CONTRACT_PATH = Path(
    "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_"
    "EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME.md"
)

MODULAR_EDGE_IDS = (2, 3)
BLOCKED_EDGE_IDS = (7, 8, 9)

EXPECTED_BLOCKERS = {
    7: "BOUNDARY_PRODUCT_BINDING_REQUIRED",
    8: "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED",
    9: "PASS191_X_SQUARED_PHASE_BINDING_REQUIRED",
}


class TypedDomainExecutionError(RuntimeError):
    pass


def _repo_root(root: str | Path | None = None) -> Path:
    return (
        Path(root).resolve()
        if root is not None
        else Path(__file__).resolve().parents[2]
    )


def _reject_ieee(value: Any) -> None:
    if isinstance(value, float):
        raise TypedDomainExecutionError("FLOAT_CANONICAL_INPUT_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_ieee(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_ieee(child)


def _canonical_json(value: Any) -> bytes:
    _reject_ieee(value)
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


def _fraction_from_node(node: Mapping[str, Any]) -> Fraction:
    if (
        node.get("domain") != "EXACT_RATIONAL"
        or node.get("value_status") != "RESOLVED_EXACT"
    ):
        raise TypedDomainExecutionError("EXACT_RATIONAL_NODE_REQUIRED")
    payload = node.get("payload")
    if not isinstance(payload, Mapping):
        raise TypedDomainExecutionError("EXACT_RATIONAL_PAYLOAD_REQUIRED")
    value = payload.get("value")
    if not isinstance(value, Mapping):
        raise TypedDomainExecutionError("EXACT_RATIONAL_VALUE_REQUIRED")
    numerator = value.get("numerator")
    denominator = value.get("denominator")
    if (
        isinstance(numerator, bool)
        or not isinstance(numerator, int)
        or isinstance(denominator, bool)
        or not isinstance(denominator, int)
        or denominator <= 0
    ):
        raise TypedDomainExecutionError("EXACT_RATIONAL_ENCODING_INVALID")
    return Fraction(numerator, denominator)


def _validate_i157_graph(graph: Mapping[str, Any]) -> dict[str, Any]:
    _reject_ieee(graph)
    if graph.get("schema") != I157_SCHEMA:
        raise TypedDomainExecutionError("I157_GRAPH_SCHEMA_MISMATCH")
    if graph.get("result") != "PASS":
        raise TypedDomainExecutionError("I157_GRAPH_RESULT_NOT_PASS")

    nodes = graph.get("value_nodes")
    joins = graph.get("joins")
    if not isinstance(nodes, list) or len(nodes) != len(TERM_NAMES):
        raise TypedDomainExecutionError("I157_TERM_COUNT_DRIFT")
    if not isinstance(joins, list) or len(joins) != len(EDGE_SPECS):
        raise TypedDomainExecutionError("I157_JOIN_COUNT_DRIFT")

    for index, node in enumerate(nodes):
        if not isinstance(node, Mapping) or node.get("term_id") != index:
            raise TypedDomainExecutionError("I157_TERM_ORDER_DRIFT")
        if node.get("term_name") != TERM_NAMES[index]:
            raise TypedDomainExecutionError("I157_TERM_NAME_DRIFT")

    for index, row in enumerate(joins):
        if not isinstance(row, Mapping) or row.get("edge_index") != index:
            raise TypedDomainExecutionError("I157_JOIN_ORDER_DRIFT")
        left, right, kind = EDGE_SPECS[index]
        if (
            row.get("left_term_id") != left
            or row.get("right_term_id") != right
            or row.get("join_kind") != kind
        ):
            raise TypedDomainExecutionError("I157_JOIN_TOPOLOGY_DRIFT")
        if row.get("scalar_coercion_used") is not False:
            raise TypedDomainExecutionError("I157_SCALAR_COERCION_DRIFT")

    stored = graph.get("typed_value_graph_sha256")
    if not isinstance(stored, str) or not re.fullmatch(r"[0-9a-f]{64}", stored):
        raise TypedDomainExecutionError("I157_GRAPH_SHA256_INVALID")
    core = dict(graph)
    core.pop("typed_value_graph_sha256", None)
    actual = _sha256(core)
    if actual != stored:
        raise TypedDomainExecutionError("I157_GRAPH_SHA256_MISMATCH")

    authority = graph.get("authority")
    if not isinstance(authority, Mapping):
        raise TypedDomainExecutionError("I157_AUTHORITY_BLOCK_REQUIRED")
    for forbidden in (
        "canonical_monolithic_proof",
        "vm81_execution_verified",
        "vm81_mutation_authority",
        "hash72_execution_receipt_verified",
        "hash72_mint_authority",
        "hash216_persistence_authority",
        "deterministic_replay_verified",
        "floating_point_authority",
    ):
        if authority.get(forbidden) is not False:
            raise TypedDomainExecutionError(
                f"I157_UPSTREAM_AUTHORITY_ESCALATION:{forbidden}"
            )

    binding = graph.get("candidate_binding_sha256")
    if not isinstance(binding, str) or not re.fullmatch(r"[0-9a-f]{64}", binding):
        raise TypedDomainExecutionError("I157_CANDIDATE_BINDING_INVALID")

    return {
        "typed_value_graph_sha256": stored,
        "candidate_binding_sha256": binding,
        "node_count": len(nodes),
        "join_count": len(joins),
    }


def _modular_node(node: Mapping[str, Any]) -> tuple[int, int]:
    if (
        node.get("domain") != "MODULAR_STATE"
        or node.get("value_status") != "RESOLVED_EXACT_TYPED"
        or node.get("exact") is not True
    ):
        raise TypedDomainExecutionError("MODULAR_STATE_NODE_REQUIRED")
    payload = node.get("payload")
    if not isinstance(payload, Mapping):
        raise TypedDomainExecutionError("MODULAR_STATE_PAYLOAD_REQUIRED")
    representative = payload.get("representative")
    modulus = payload.get("modulus")
    if (
        isinstance(representative, bool)
        or not isinstance(representative, int)
        or isinstance(modulus, bool)
        or not isinstance(modulus, int)
        or modulus <= 0
        or representative < 0
        or representative >= modulus
    ):
        raise TypedDomainExecutionError("MODULAR_STATE_ENCODING_INVALID")
    if payload.get("ordinary_scalar_remainder_identity_claimed") is not False:
        raise TypedDomainExecutionError("MODULAR_SCALARIZATION_FORBIDDEN")
    return representative, modulus


def project_rational_to_modular(
    scalar_node: Mapping[str, Any],
    modular_node: Mapping[str, Any],
    *,
    scalar_term_id: int,
    modular_term_id: int,
    candidate_binding_sha256: str,
) -> dict[str, Any]:
    """Project an exact rational into a declared modular class.

    This is a typed projection, not reverse inference and not an assertion that
    the modular state is identical to an ordinary scalar remainder.
    """

    value = _fraction_from_node(scalar_node)
    representative, modulus = _modular_node(modular_node)
    denominator_mod = value.denominator % modulus
    if gcd(denominator_mod, modulus) != 1:
        return {
            "schema": MODULAR_WITNESS_SCHEMA,
            "status": "UNRESOLVED",
            "reason": "RATIONAL_DENOMINATOR_NOT_INVERTIBLE_IN_MODULAR_DOMAIN",
            "scalar_term_id": scalar_term_id,
            "modular_term_id": modular_term_id,
            "modulus": modulus,
            "candidate_binding_sha256": candidate_binding_sha256,
            "scalar_coercion_used": False,
            "reverse_inference_authorized": False,
            "floating_point_authority": False,
        }

    inverse = pow(denominator_mod, -1, modulus)
    projected = (value.numerator % modulus) * inverse % modulus
    equal = projected == representative

    projection_audit = {
        "source_type": "EXACT_RATIONAL",
        "target_type": "MODULAR_STATE",
        "domain": f"Z/{modulus}Z",
        "forward_rule": "num*inv(den) mod modulus",
        "reverse_rule": None,
        "preserved_invariants": [
            "candidate_binding",
            "declared_modulus",
            "congruence_class",
            "exact_rational_numerator_denominator",
        ],
        "lost_information": [
            "integer_quotient",
            "unique_scalar_preimage",
        ],
        "injective": False,
        "reverse_inference_authorized": False,
        "validation_oracle": "EXACT_INTEGER_MODULAR_INVERSE_AND_CLASS_COMPARE",
    }

    core = {
        "schema": MODULAR_WITNESS_SCHEMA,
        "status": "PROVED" if equal else "REJECTED",
        "reason": (
            "EXACT_TYPED_MODULAR_CLASS_MATCH"
            if equal
            else "EXACT_TYPED_MODULAR_CLASS_MISMATCH"
        ),
        "scalar_term_id": scalar_term_id,
        "scalar_term_name": TERM_NAMES[scalar_term_id],
        "modular_term_id": modular_term_id,
        "modular_term_name": TERM_NAMES[modular_term_id],
        "rational": {
            "numerator": value.numerator,
            "denominator": value.denominator,
        },
        "modulus": modulus,
        "denominator_modulus": denominator_mod,
        "denominator_inverse": inverse,
        "projected_representative": projected,
        "modular_representative": representative,
        "projection_audit": projection_audit,
        "candidate_binding_sha256": candidate_binding_sha256,
        "ordinary_scalar_remainder_identity_claimed": False,
        "scalar_coercion_used": False,
        "reverse_inference_authorized": False,
        "floating_point_authority": False,
    }
    core["projection_witness_sha256"] = _sha256(core)
    return core


def _repository_blocker_evidence(root: str | Path | None = None) -> dict[str, Any]:
    repo = _repo_root(root)
    pass191 = repo / PASS191_KERNEL_PATH
    pass169 = repo / PASS169_CONTRACT_PATH
    pass191_text = pass191.read_text(encoding="utf-8")
    pass169_text = pass169.read_text(encoding="utf-8")

    x_binding_unresolved = '"x_squared_binding": None' in pass191_text
    pass169_requires_symbolic_radical = (
        "construct symbolic radical" in pass169_text
        and "exact algebraic-number equality" in pass169_text
    )
    pass169_requires_vm81 = (
        "execute only through VM81" in pass169_text
        and "emit Hash72 receipt" in pass169_text
    )
    if not x_binding_unresolved:
        raise TypedDomainExecutionError(
            "PASS191_X_SQUARED_BINDING_CHANGED_REAUDIT_REQUIRED"
        )
    if not pass169_requires_symbolic_radical or not pass169_requires_vm81:
        raise TypedDomainExecutionError(
            "PASS169_REQUIRED_EXECUTION_CONTRACT_DRIFT"
        )

    return {
        "pass191_kernel": {
            "path": str(PASS191_KERNEL_PATH),
            "sha256": _file_sha256(pass191),
            "x_squared_binding_unresolved": True,
        },
        "pass169_contract": {
            "path": str(PASS169_CONTRACT_PATH),
            "sha256": _file_sha256(pass169),
            "symbolic_radical_runtime_required": True,
            "exact_algebraic_equality_required": True,
            "vm81_execution_required_for_canonical_commit": True,
            "hash72_receipt_required_for_canonical_commit": True,
        },
    }


def execute_typed_domain_joins(
    graph: Mapping[str, Any],
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    validated = _validate_i157_graph(graph)
    nodes = graph["value_nodes"]
    original_joins = graph["joins"]
    candidate_binding = validated["candidate_binding_sha256"]

    executed: list[dict[str, Any]] = []
    modular_witnesses: list[dict[str, Any]] = []

    for edge_index, row in enumerate(original_joins):
        status = row["status"]
        reason = row["reason"]
        witness_sha256: str | None = None

        if edge_index == 2:
            witness = project_rational_to_modular(
                nodes[2],
                nodes[3],
                scalar_term_id=2,
                modular_term_id=3,
                candidate_binding_sha256=candidate_binding,
            )
            modular_witnesses.append(witness)
            status = witness["status"]
            reason = witness["reason"]
            witness_sha256 = witness.get("projection_witness_sha256")

        elif edge_index == 3:
            witness = project_rational_to_modular(
                nodes[4],
                nodes[3],
                scalar_term_id=4,
                modular_term_id=3,
                candidate_binding_sha256=candidate_binding,
            )
            modular_witnesses.append(witness)
            status = witness["status"]
            reason = witness["reason"]
            witness_sha256 = witness.get("projection_witness_sha256")

        elif edge_index in BLOCKED_EDGE_IDS:
            status = "UNRESOLVED"
            reason = EXPECTED_BLOCKERS[edge_index]

        core = {
            "edge_index": edge_index,
            "left_term_id": row["left_term_id"],
            "right_term_id": row["right_term_id"],
            "join_kind": row["join_kind"],
            "input_status": row["status"],
            "execution_status": status,
            "execution_reason": reason,
            "candidate_binding_sha256": candidate_binding,
            "adapter_witness_sha256": witness_sha256,
            "scalar_coercion_used": False,
            "floating_point_authority": False,
        }
        core["execution_row_sha256"] = _sha256(core)
        executed.append(core)

    blockers = _repository_blocker_evidence(root)

    rejected = [row for row in executed if row["execution_status"] == "REJECTED"]
    unresolved = [
        row for row in executed if row["execution_status"] == "UNRESOLVED"
    ]
    proved = [row for row in executed if row["execution_status"] == "PROVED"]

    if rejected:
        decision = "REJECTED"
    elif unresolved:
        decision = "PARTIALLY_RESOLVED"
    else:
        decision = "ALL_TYPED_JOINS_RESOLVED"

    core = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "classification": "EXACT_TYPED_DOMAIN_JOIN_EXECUTION_MEMBRANE",
        "decision": decision,
        "input_graph": validated,
        "executed_joins": executed,
        "modular_projection_witnesses": modular_witnesses,
        "counts": {
            "join_count": len(executed),
            "proved": len(proved),
            "unresolved": len(unresolved),
            "rejected": len(rejected),
            "newly_resolved_modular_pivots": sum(
                1
                for row in executed
                if row["edge_index"] in MODULAR_EDGE_IDS
                and row["execution_status"] == "PROVED"
            ),
        },
        "repository_blocker_evidence": blockers,
        "remaining_blockers": [
            {
                "edge_index": row["edge_index"],
                "join_kind": row["join_kind"],
                "reason": row["execution_reason"],
            }
            for row in unresolved
        ],
        "authority": {
            "typed_join_execution_complete": len(unresolved) == 0
            and len(rejected) == 0,
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
        "next_boundary": (
            "BOUNDARY_VALUE_EVALUATOR_AND_PHASE_EXPONENT_BINDING"
            if unresolved and not rejected
            else (
                "REPAIR_REJECTED_TYPED_JOIN"
                if rejected
                else "VM81_PASS169_ADMISSION"
            )
        ),
        "result": "PASS",
    }
    core["execution_membrane_sha256"] = _sha256(core)
    return core


def typed_domain_join_executor_self_test() -> dict[str, Any]:
    from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
        CANDIDATE_SCHEMA,
        COMBINED_SOURCE_SHA256,
        PROVENANCE_SCHEMA,
        produce_candidate_bound_value_graph,
    )

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
    graph = produce_candidate_bound_value_graph(
        snapshot, provenance, symbols
    )
    result = execute_typed_domain_joins(graph)

    if (
        result["counts"]["join_count"] != 10
        or result["counts"]["proved"] != 7
        or result["counts"]["unresolved"] != 3
        or result["counts"]["rejected"] != 0
        or result["counts"]["newly_resolved_modular_pivots"] != 2
        or result["decision"] != "PARTIALLY_RESOLVED"
    ):
        raise AssertionError("I158_SELF_TEST_COUNT_DRIFT")

    return {
        "schema": "HHS_PASS219_I158_SELF_TEST_V1",
        "ok": True,
        "decision": result["decision"],
        "proved": result["counts"]["proved"],
        "unresolved": result["counts"]["unresolved"],
        "rejected": result["counts"]["rejected"],
        "newly_resolved_modular_pivots": result["counts"][
            "newly_resolved_modular_pivots"
        ],
        "execution_membrane_sha256": result["execution_membrane_sha256"],
        "canonical_monolithic_boundary_proof": False,
        "vm81_mutation_authority": False,
        "hash72_mint_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "PASS",
    "ITERATION",
    "SCHEMA",
    "MODULAR_WITNESS_SCHEMA",
    "TypedDomainExecutionError",
    "project_rational_to_modular",
    "execute_typed_domain_joins",
    "typed_domain_join_executor_self_test",
]
