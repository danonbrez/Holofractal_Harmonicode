"""Pass 219 I159 Harmonicode modular-pivot phase binding.

This module implements the missing typed execution adapter for the two
P^2(MOD)(pq) joins carried unresolved through I157/I158.

The adapter is derived from inherited repository rules:
- Pass157 parses P^2(MOD)(pq) as HHS_MODULAR_NORMALIZATION with
  authority=P^2 and state=pq.
- Pass157 modular phase lanes retain both quotient and residue.
- Appendix E distinguishes ClosureResidue from RenewedUnit and permits a
  profile-scoped closure relation without asserting ordinary scalar 0=1.
- I157 permits typed constraint joins without untyped scalar identity.

No VM81 mutation, Hash72 mint, Hash216 persistence, or Pass169 terminal proof
authority is created here.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from hhs_runtime.pass219.typed_domain_join_executor import (
    TypedDomainExecutionError,
    execute_typed_domain_joins,
)
from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    PROVENANCE_SCHEMA,
    produce_candidate_bound_value_graph,
)
from native_projects.hhs_pass157_ppf_mptc.python.hhs_pass157.model import (
    phase_decompose,
)
from native_projects.hhs_pass157_ppf_mptc.python.hhs_pass157.parser import (
    compile_membrane,
)

PASS = 219
ITERATION = "I159"
SCHEMA = "HHS_PASS219_I159_HARMONICODE_MODULAR_PIVOT_PHASE_BINDING_V1"
PROFILE_SCHEMA = "HHS_PASS219_I159_MODULAR_NORMALIZATION_PROFILE_V1"
PHASE_LANE_SCHEMA = "HHS_PASS219_I159_EXACT_PHASE_LANE_V1"
PIVOT_WITNESS_SCHEMA = "HHS_PASS219_I159_TYPED_MODULAR_PIVOT_WITNESS_V1"

PASS157_CONTRACT_PATH = Path(
    "native_projects/hhs_pass157_ppf_mptc/specs/"
    "HHS_PASS_157_PPF_MPTC_CONTRACT_v1.1.0.md"
)
PASS157_PARSER_PATH = Path(
    "native_projects/hhs_pass157_ppf_mptc/python/hhs_pass157/parser.py"
)
APPENDIX_E_PATH = Path(
    "docs/pass219/APPENDIX_E_TYPED_ZERO_PIVOT_AND_PHASE_CLOSURE.md"
)

MODULAR_SOURCE = "P^2(MOD)(pq)"


class HarmonicodeModularPivotError(RuntimeError):
    pass


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]


def _reject_ieee(value: Any) -> None:
    if isinstance(value, float):
        raise HarmonicodeModularPivotError("FLOAT_CANONICAL_INPUT_FORBIDDEN")
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


def _hex64(value: Any, name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise HarmonicodeModularPivotError(f"{name}_SHA256_REQUIRED")
    return value


def _exact_integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise HarmonicodeModularPivotError(f"{name}_EXACT_INTEGER_REQUIRED")
    return value


def _fraction_from_node(node: Mapping[str, Any], name: str) -> Fraction:
    if (
        node.get("domain") != "EXACT_RATIONAL"
        or node.get("value_status") != "RESOLVED_EXACT"
        or node.get("exact") is not True
    ):
        raise HarmonicodeModularPivotError(f"{name}_EXACT_RATIONAL_NODE_REQUIRED")
    payload = node.get("payload")
    if not isinstance(payload, Mapping):
        raise HarmonicodeModularPivotError(f"{name}_PAYLOAD_REQUIRED")
    value = payload.get("value")
    if not isinstance(value, Mapping):
        raise HarmonicodeModularPivotError(f"{name}_VALUE_REQUIRED")
    numerator = _exact_integer(value.get("numerator"), f"{name}_NUMERATOR")
    denominator = _exact_integer(value.get("denominator"), f"{name}_DENOMINATOR")
    if denominator <= 0:
        raise HarmonicodeModularPivotError(f"{name}_DENOMINATOR_POSITIVE_REQUIRED")
    return Fraction(numerator, denominator)


def verify_pass157_modular_normalization_profile(
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Bind the I159 adapter to the inherited Pass157 typed-node semantics."""

    repo = _repo_root(root)
    contract = repo / PASS157_CONTRACT_PATH
    parser_path = repo / PASS157_PARSER_PATH
    appendix = repo / APPENDIX_E_PATH

    contract_text = contract.read_text(encoding="utf-8")
    parser_text = parser_path.read_text(encoding="utf-8")
    appendix_text = appendix.read_text(encoding="utf-8")

    compiled = compile_membrane(MODULAR_SOURCE, "CHECK_MEMBRANE")
    nodes = [
        row
        for row in compiled.get("typed_ast", [])
        if row.get("node") == "HHS_MODULAR_NORMALIZATION"
        and row.get("authority") == "P^2"
        and row.get("state") == "pq"
    ]

    checks = {
        "typed_membrane_schema": compiled.get("schema") == "HHS_PASS_157_TYPED_MEMBRANE_V2",
        "global_simultaneous_constraint": compiled.get("global_simultaneous_constraint") is True,
        "modular_normalization_node_exactly_bound": len(nodes) == 1,
        "parser_source_contains_same_node": (
            '"node": "HHS_MODULAR_NORMALIZATION"' in parser_text
            and '"authority": "P^2"' in parser_text
            and '"state": "pq"' in parser_text
        ),
        "pass157_full_phase_identity": (
            "n=qM+r" in contract_text.replace("\\", "")
            or "n=qM+r" in contract_text.replace(" ", "")
        ),
        "pass157_quotient_and_residue_retained": (
            "Each lane retains its quotient and residue." in contract_text
            and "Residues alone are never authoritative." in contract_text
        ),
        "typed_closure_residue_defined": "ClosureResidue(period)" in appendix_text,
        "typed_renewed_unit_defined": "RenewedUnit(period)" in appendix_text,
        "scalar_zero_one_noncollapse": "0_scalar != 1_scalar." in appendix_text,
    }
    if not all(checks.values()):
        raise HarmonicodeModularPivotError(
            "INHERITED_MODULAR_PROFILE_DRIFT:"
            + ",".join(name for name, ok in checks.items() if not ok)
        )

    core = {
        "schema": PROFILE_SCHEMA,
        "source": MODULAR_SOURCE,
        "typed_node": {
            "node": "HHS_MODULAR_NORMALIZATION",
            "authority": "P^2",
            "state": "pq",
        },
        "phase_identity": "n=q*M+r; 0<=r<M",
        "quotient_retained": True,
        "residue_retained": True,
        "residue_only_authority": False,
        "closure_relation_scope": "I159_LOCAL_MODULUS_TYPED_PROFILE",
        "ordinary_scalar_equality_claimed": False,
        "repository_sources": {
            "pass157_contract": {
                "path": str(PASS157_CONTRACT_PATH),
                "sha256": _file_sha256(contract),
            },
            "pass157_parser": {
                "path": str(PASS157_PARSER_PATH),
                "sha256": _file_sha256(parser_path),
            },
            "appendix_e": {
                "path": str(APPENDIX_E_PATH),
                "sha256": _file_sha256(appendix),
            },
        },
        "checks": checks,
        "floating_point_authority": False,
        "vm81_mutation_authority": False,
        "hash72_mint_authority": False,
        "hash216_persistence_authority": False,
    }
    core["profile_sha256"] = _sha256(core)
    return core


def build_phase_lane(value: int, modulus: int) -> dict[str, Any]:
    """Return the full inherited Pass157 quotient/residue phase lane."""

    value = _exact_integer(value, "PHASE_VALUE")
    modulus = _exact_integer(modulus, "PHASE_MODULUS")
    if modulus <= 0:
        raise HarmonicodeModularPivotError("PHASE_MODULUS_POSITIVE_REQUIRED")

    quotient, residue = phase_decompose(value, modulus)
    if value != quotient * modulus + residue or not 0 <= residue < modulus:
        raise HarmonicodeModularPivotError("PASS157_PHASE_DECOMPOSITION_MISMATCH")

    if residue == 0:
        phase_class = "CLOSURE_RESIDUE"
    elif residue == 1 and quotient >= 1:
        phase_class = "RENEWED_UNIT"
    elif residue == 1:
        phase_class = "UNIT_BEFORE_CLOSURE"
    else:
        phase_class = "PHASE_HELD"

    core = {
        "schema": PHASE_LANE_SCHEMA,
        "value": value,
        "modulus": modulus,
        "quotient": quotient,
        "residue": residue,
        "reconstruction": quotient * modulus + residue,
        "reconstruction_exact": True,
        "phase_class": phase_class,
        "quotient_retained": True,
        "residue_retained": True,
        "residue_only_authority": False,
        "floating_point_authority": False,
    }
    core["phase_lane_sha256"] = _sha256(core)
    return core


def prove_p_fold_closure_to_renewed_unit(
    *,
    P: int,
    modulus: int,
    left_value: int,
    authority_value: int,
    candidate_binding_sha256: str,
    profile_sha256: str,
) -> dict[str, Any]:
    """Prove the left modular pivot with complete quotient/residue provenance."""

    P = _exact_integer(P, "P")
    modulus = _exact_integer(modulus, "MODULUS")
    left_value = _exact_integer(left_value, "LEFT_VALUE")
    authority_value = _exact_integer(authority_value, "AUTHORITY_VALUE")
    candidate_binding_sha256 = _hex64(candidate_binding_sha256, "CANDIDATE_BINDING")
    profile_sha256 = _hex64(profile_sha256, "PROFILE")

    left_lane = build_phase_lane(left_value, modulus)
    authority_lane = build_phase_lane(authority_value, modulus)

    checks = {
        "positive_P": P > 0,
        "cellular_modulus_is_P2_minus_1": modulus == P * P - 1,
        "left_exactly_P_full_periods": left_value == P * modulus,
        "left_quotient_is_P": left_lane["quotient"] == P,
        "left_is_closure_residue": (
            left_lane["residue"] == 0
            and left_lane["phase_class"] == "CLOSURE_RESIDUE"
        ),
        "authority_is_P2": authority_value == P * P,
        "authority_is_one_period_plus_unit": authority_value == modulus + 1,
        "authority_quotient_is_one": authority_lane["quotient"] == 1,
        "authority_is_renewed_unit": (
            authority_lane["residue"] == 1
            and authority_lane["phase_class"] == "RENEWED_UNIT"
        ),
        "quotients_retained": (
            left_lane["quotient_retained"] is True
            and authority_lane["quotient_retained"] is True
        ),
        "no_residue_only_authority": (
            left_lane["residue_only_authority"] is False
            and authority_lane["residue_only_authority"] is False
        ),
    }
    proved = all(checks.values())

    core = {
        "schema": PIVOT_WITNESS_SCHEMA,
        "edge_role": "LEFT_OF_P2_MOD_PQ",
        "relation": "P_FOLD_CLOSURE_TO_RENEWED_UNIT",
        "status": "PROVED" if proved else "REJECTED",
        "reason": (
            "EXACT_TYPED_CLOSURE_RESIDUE_TO_RENEWED_UNIT_PIVOT"
            if proved
            else "P_FOLD_CLOSURE_TO_RENEWED_UNIT_CONSTRAINT_MISMATCH"
        ),
        "P": P,
        "modulus": modulus,
        "left_lane": left_lane,
        "authority_lane": authority_lane,
        "candidate_binding_sha256": candidate_binding_sha256,
        "profile_sha256": profile_sha256,
        "checks": checks,
        "ordinary_scalar_identity_claimed": False,
        "ordinary_scalar_zero_equals_one_claimed": False,
        "full_phase_lane_identity_claimed": False,
        "typed_relation_only": True,
        "floating_point_authority": False,
    }
    core["pivot_witness_sha256"] = _sha256(core)
    return core


def prove_renewed_unit_phase_class_join(
    *,
    modulus: int,
    authority_value: int,
    right_value: int,
    m: int,
    candidate_binding_sha256: str,
    profile_sha256: str,
) -> dict[str, Any]:
    """Prove the right modular pivot while retaining both fold quotients."""

    modulus = _exact_integer(modulus, "MODULUS")
    authority_value = _exact_integer(authority_value, "AUTHORITY_VALUE")
    right_value = _exact_integer(right_value, "RIGHT_VALUE")
    m = _exact_integer(m, "M")
    candidate_binding_sha256 = _hex64(candidate_binding_sha256, "CANDIDATE_BINDING")
    profile_sha256 = _hex64(profile_sha256, "PROFILE")

    authority_lane = build_phase_lane(authority_value, modulus)
    right_lane = build_phase_lane(right_value, modulus)

    checks = {
        "right_is_exact_m2_minus_m": right_value == m * m - m,
        "authority_is_one_period_plus_unit": authority_value == modulus + 1,
        "authority_quotient_is_one": authority_lane["quotient"] == 1,
        "authority_is_renewed_unit": (
            authority_lane["residue"] == 1
            and authority_lane["phase_class"] == "RENEWED_UNIT"
        ),
        "right_is_renewed_unit": (
            right_lane["residue"] == 1
            and right_lane["quotient"] >= 1
            and right_lane["phase_class"] == "RENEWED_UNIT"
        ),
        "right_reconstruction_uses_retained_quotient": (
            right_value
            == right_lane["quotient"] * modulus + right_lane["residue"]
        ),
        "quotients_retained": (
            authority_lane["quotient_retained"] is True
            and right_lane["quotient_retained"] is True
        ),
        "no_residue_only_authority": (
            authority_lane["residue_only_authority"] is False
            and right_lane["residue_only_authority"] is False
        ),
    }
    proved = all(checks.values())

    core = {
        "schema": PIVOT_WITNESS_SCHEMA,
        "edge_role": "RIGHT_OF_P2_MOD_PQ",
        "relation": "RENEWED_UNIT_PHASE_CLASS_JOIN",
        "status": "PROVED" if proved else "REJECTED",
        "reason": (
            "EXACT_TYPED_RENEWED_UNIT_PHASE_CLASS_JOIN"
            if proved
            else "RENEWED_UNIT_PHASE_CLASS_CONSTRAINT_MISMATCH"
        ),
        "modulus": modulus,
        "authority_lane": authority_lane,
        "right_lane": right_lane,
        "m": m,
        "candidate_binding_sha256": candidate_binding_sha256,
        "profile_sha256": profile_sha256,
        "checks": checks,
        "ordinary_scalar_identity_claimed": False,
        "full_phase_lane_identity_claimed": False,
        "same_residue_is_sufficient_authority": False,
        "typed_phase_class_relation_only": True,
        "floating_point_authority": False,
    }
    core["pivot_witness_sha256"] = _sha256(core)
    return core


def execute_i159_modular_pivot_phase_bindings(
    graph: Mapping[str, Any],
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Resolve exactly the two modular-pivot joins left open by I158."""

    _reject_ieee(graph)
    i158 = execute_typed_domain_joins(graph, root=root)
    if i158.get("decision") != "UNRESOLVED_TYPED_SEMANTICS":
        raise HarmonicodeModularPivotError("I158_EXPECTED_UNRESOLVED_TYPED_SEMANTICS")

    env = graph.get("symbol_environment")
    nodes = graph.get("value_nodes")
    if not isinstance(env, Mapping) or not isinstance(nodes, list) or len(nodes) != 15:
        raise HarmonicodeModularPivotError("I157_GRAPH_SHAPE_REQUIRED")

    P = _exact_integer(env.get("P"), "P")
    p = _exact_integer(env.get("p"), "p")
    q = _exact_integer(env.get("q"), "q")
    m = _exact_integer(env.get("m"), "m")
    modulus = p * q
    P2 = P * P
    delta = P2 - modulus

    modular_node = nodes[3]
    if (
        not isinstance(modular_node, Mapping)
        or modular_node.get("domain") != "MODULAR_STATE"
        or modular_node.get("value_status") != "RESOLVED_EXACT_TYPED"
        or modular_node.get("exact") is not True
    ):
        raise HarmonicodeModularPivotError("P2_MOD_PQ_EXACT_TYPED_NODE_REQUIRED")
    modular_payload = modular_node.get("payload")
    if not isinstance(modular_payload, Mapping):
        raise HarmonicodeModularPivotError("P2_MOD_PQ_PAYLOAD_REQUIRED")
    if modular_payload.get("source_operator") != MODULAR_SOURCE:
        raise HarmonicodeModularPivotError("P2_MOD_PQ_SOURCE_OPERATOR_DRIFT")
    if _exact_integer(modular_payload.get("modulus"), "P2_MOD_PQ_MODULUS") != modulus:
        raise HarmonicodeModularPivotError("P2_MOD_PQ_MODULUS_DRIFT")
    if modular_payload.get("ordinary_scalar_remainder_identity_claimed") is not False:
        raise HarmonicodeModularPivotError("P2_MOD_PQ_SCALARIZATION_FORBIDDEN")

    left_fraction = _fraction_from_node(nodes[2], "LEFT_MODULAR_PIVOT")
    right_fraction = _fraction_from_node(nodes[4], "RIGHT_MODULAR_PIVOT")
    if left_fraction.denominator != 1 or right_fraction.denominator != 1:
        raise HarmonicodeModularPivotError("MODULAR_PIVOT_INTEGER_PHASE_LANE_REQUIRED")

    profile = verify_pass157_modular_normalization_profile(root)
    binding = _hex64(graph.get("candidate_binding_sha256"), "CANDIDATE_BINDING")

    left_witness = prove_p_fold_closure_to_renewed_unit(
        P=P,
        modulus=modulus,
        left_value=left_fraction.numerator,
        authority_value=P2,
        candidate_binding_sha256=binding,
        profile_sha256=profile["profile_sha256"],
    )
    right_witness = prove_renewed_unit_phase_class_join(
        modulus=modulus,
        authority_value=P2,
        right_value=right_fraction.numerator,
        m=m,
        candidate_binding_sha256=binding,
        profile_sha256=profile["profile_sha256"],
    )

    executed: list[dict[str, Any]] = []
    witnesses = {2: left_witness, 3: right_witness}
    for row in i158["executed_joins"]:
        edge_index = int(row["edge_index"])
        if edge_index in witnesses:
            witness = witnesses[edge_index]
            patched = {
                **row,
                "execution_status": witness["status"],
                "execution_reason": witness["reason"],
                "adapter_witness_sha256": witness["pivot_witness_sha256"],
                "i159_typed_profile": witness["relation"],
                "ordinary_scalar_identity_claimed": False,
                "residue_only_authority": False,
            }
            patched_core = dict(patched)
            patched_core.pop("execution_row_sha256", None)
            patched["execution_row_sha256"] = _sha256(patched_core)
            executed.append(patched)
        else:
            executed.append(dict(row))

    rejected = [row for row in executed if row["execution_status"] == "REJECTED"]
    unresolved = [row for row in executed if row["execution_status"] == "UNRESOLVED"]
    proved = [row for row in executed if row["execution_status"] == "PROVED"]

    if rejected:
        decision = "REJECTED"
    elif unresolved:
        decision = "PARTIALLY_RESOLVED_TYPED_GRAPH"
    else:
        decision = "ALL_TYPED_JOINS_RESOLVED"

    core = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "classification": "HARMONICODE_TYPED_MODULAR_PIVOT_PHASE_BINDING",
        "decision": decision,
        "input_typed_value_graph_sha256": graph["typed_value_graph_sha256"],
        "candidate_binding_sha256": binding,
        "inherited_i158_execution_membrane_sha256": i158[
            "execution_membrane_sha256"
        ],
        "modular_normalization_profile": profile,
        "cellular_membrane": {
            "P": P,
            "p": p,
            "q": q,
            "m": m,
            "P2": P2,
            "pq": modulus,
            "Delta": delta,
            "delta_is_one": delta == 1,
        },
        "pivot_witnesses": {
            "edge_2": left_witness,
            "edge_3": right_witness,
        },
        "executed_joins": executed,
        "counts": {
            "join_count": len(executed),
            "proved": len(proved),
            "unresolved": len(unresolved),
            "rejected": len(rejected),
            "newly_resolved_modular_pivots": sum(
                1
                for edge in (2, 3)
                if executed[edge]["execution_status"] == "PROVED"
                and i158["executed_joins"][edge]["execution_status"]
                == "UNRESOLVED"
            ),
        },
        "remaining_blockers": [
            {
                "edge_index": row["edge_index"],
                "join_kind": row["join_kind"],
                "reason": row["execution_reason"],
            }
            for row in unresolved
        ],
        "semantic_guards": {
            "conventional_modular_projection_used_as_authority": False,
            "ordinary_scalar_equality_claimed": False,
            "ordinary_scalar_zero_equals_one_claimed": False,
            "residue_only_authority": False,
            "quotients_retained": True,
            "full_phase_lane_identity_claimed": False,
            "typed_phase_relation_only": True,
        },
        "authority": {
            "typed_modular_pivot_profile_registered": True,
            "typed_modular_pivots_resolved": (
                left_witness["status"] == "PROVED"
                and right_witness["status"] == "PROVED"
            ),
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
            "SOURCE_BOUND_AB_PRODUCT_AND_X2_PHASE_EXPONENT_BINDINGS"
            if not rejected and unresolved
            else (
                "REPAIR_REJECTED_MODULAR_PIVOT"
                if rejected
                else "VM81_PASS169_ADMISSION"
            )
        ),
        "result": "PASS",
    }
    core["i159_execution_sha256"] = _sha256(core)
    return core


def i159_modular_pivot_self_test() -> dict[str, Any]:
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
    graph = produce_candidate_bound_value_graph(snapshot, provenance, symbols)
    result = execute_i159_modular_pivot_phase_bindings(graph)
    if (
        result["decision"] != "PARTIALLY_RESOLVED_TYPED_GRAPH"
        or result["counts"] != {
            "join_count": 10,
            "proved": 7,
            "unresolved": 3,
            "rejected": 0,
            "newly_resolved_modular_pivots": 2,
        }
        or result["pivot_witnesses"]["edge_2"]["left_lane"]["quotient"] != 30
        or result["pivot_witnesses"]["edge_2"]["left_lane"]["residue"] != 0
        or result["pivot_witnesses"]["edge_2"]["authority_lane"]["quotient"] != 1
        or result["pivot_witnesses"]["edge_2"]["authority_lane"]["residue"] != 1
        or result["pivot_witnesses"]["edge_3"]["right_lane"]["quotient"] != 79
        or result["pivot_witnesses"]["edge_3"]["right_lane"]["residue"] != 1
    ):
        raise AssertionError("I159_SELF_TEST_INVARIANT_FAILURE")

    return {
        "schema": "HHS_PASS219_I159_SELF_TEST_V1",
        "ok": True,
        "decision": result["decision"],
        "proved": result["counts"]["proved"],
        "unresolved": result["counts"]["unresolved"],
        "rejected": result["counts"]["rejected"],
        "newly_resolved_modular_pivots": result["counts"][
            "newly_resolved_modular_pivots"
        ],
        "left_lane": result["pivot_witnesses"]["edge_2"]["left_lane"],
        "authority_lane": result["pivot_witnesses"]["edge_2"]["authority_lane"],
        "right_lane": result["pivot_witnesses"]["edge_3"]["right_lane"],
        "i159_execution_sha256": result["i159_execution_sha256"],
        "canonical_monolithic_boundary_proof": False,
        "vm81_mutation_authority": False,
        "hash72_mint_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "PASS",
    "ITERATION",
    "SCHEMA",
    "PROFILE_SCHEMA",
    "PHASE_LANE_SCHEMA",
    "PIVOT_WITNESS_SCHEMA",
    "HarmonicodeModularPivotError",
    "verify_pass157_modular_normalization_profile",
    "build_phase_lane",
    "prove_p_fold_closure_to_renewed_unit",
    "prove_renewed_unit_phase_class_join",
    "execute_i159_modular_pivot_phase_bindings",
    "i159_modular_pivot_self_test",
]
