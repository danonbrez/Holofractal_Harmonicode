from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_191_FORMAL_OUTCOME_LEDGER_V1"
CLASSIFICATION = "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_FORMAL_DECISION_VERIFIED"
SCOPE = "CURRENT_REGISTERED_RULE_GRAPH"

PROVED = "PROVED"
FALSIFIED = "FALSIFIED"
OBSTRUCTED = "OBSTRUCTED"
VALID_STATUSES = frozenset((PROVED, FALSIFIED, OBSTRUCTED))

OBLIGATION_ORDER = (
    "DQPL-UNIT",
    "DQPL-QUARTIC",
    "DQPL-RESONANCE-LITERAL",
    "DQPL-CRITICAL-AXIS-LITERAL",
    "DQPL-FIBONACCI-RECURRENCE",
    "DQPL-FIBONACCI-PRODUCT",
    "DQPL-PLASTIC-CLOSURE",
    "DQPL-COLLATZ-GLOBAL",
    "DQPL-RH-TRANSFER",
    "DQPL-QUADRATIC-RECIPROCITY-TRANSFER",
)


def _outcome(
    obligation_id: str,
    proposition: str,
    status: str,
    certificate: Mapping[str, Any],
    dependencies: tuple[str, ...] = (),
) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid formal status: {status}")
    core = {
        "obligation_id": obligation_id,
        "proposition": proposition,
        "status": status,
        "scope": SCOPE,
        "dependencies": list(dependencies),
        "certificate": dict(certificate),
    }
    return {
        **core,
        "outcome_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-FORMAL-OUTCOME-V1", "obligation_id": obligation_id},
            core,
        ),
    }


def build_formal_outcome_ledger() -> dict[str, Any]:
    outcomes = [
        _outcome(
            "DQPL-UNIT",
            "PHASE_SQUARE(1,0) advances the dyadic magnitude projection from 1 to 2.",
            PROVED,
            {
                "proof_kind": "EXACT_STATE_TRANSITION",
                "initial_state": {"dyadic_level": 0, "quartic_phase": 0, "magnitude": "1"},
                "operator": "square",
                "result_state": {"dyadic_level": 1, "quartic_phase": 1, "magnitude": "2"},
                "equation": "2^(0+1)=2",
            },
        ),
        _outcome(
            "DQPL-QUARTIC",
            "Four phase advances return quartic phase to zero while advancing dyadic magnitude 1→2→4→8→16.",
            PROVED,
            {
                "proof_kind": "FINITE_EXACT_TRACE",
                "dyadic_levels": [0, 1, 2, 3, 4],
                "quartic_phases": [0, 1, 2, 3, 0],
                "magnitudes": ["1", "2", "4", "8", "16"],
                "closure_equation": "(0+4) mod 4 = 0",
            },
        ),
        _outcome(
            "DQPL-RESONANCE-LITERAL",
            "exp(i*pi*(1/2+i*t)) = -exp(-pi*t) for all real t.",
            FALSIFIED,
            {
                "proof_kind": "EXACT_COUNTEREXAMPLE",
                "counterexample": "t=0",
                "left": {"expression": "exp(i*pi/2)", "exact_value": "i"},
                "right": {"expression": "-exp(0)", "exact_value": "-1"},
                "equality": False,
                "derived_identity": "exp(i*pi*(1/2+i*t)) = i*exp(-pi*t)",
            },
        ),
        _outcome(
            "DQPL-CRITICAL-AXIS-LITERAL",
            "1/2 = i^2/2 = -1/2 under the equality relation.",
            FALSIFIED,
            {
                "proof_kind": "EXACT_COUNTEREXAMPLE",
                "identity": "i^2=-1",
                "middle_value": "-1/2",
                "left_value": "1/2",
                "difference": "1",
                "equality": False,
                "required_extension": "A separately defined phase-equivalence relation may be tested without identifying it with equality.",
            },
        ),
        _outcome(
            "DQPL-FIBONACCI-RECURRENCE",
            "F(n+2)=F(n+1)+F(n) for the recursively defined Fibonacci sequence.",
            PROVED,
            {
                "proof_kind": "DEFINITIONAL_INDUCTION",
                "base_cases": {"F(0)": 0, "F(1)": 1},
                "induction_rule": "F(n+2):=F(n+1)+F(n)",
                "witness_n_10": "F(12)=144=89+55",
            },
        ),
        _outcome(
            "DQPL-FIBONACCI-PRODUCT",
            "F(n+2)=phi^n*psi^n for all n, where phi and psi are the roots of x^2-x-1.",
            FALSIFIED,
            {
                "proof_kind": "EXACT_COUNTEREXAMPLE",
                "root_product": "phi*psi=-1",
                "counterexample": "n=1",
                "left": "F(3)=2",
                "right": "phi*psi=-1",
                "equality": False,
            },
        ),
        _outcome(
            "DQPL-PLASTIC-CLOSURE",
            "For nonzero rho satisfying rho^3=rho+1, rho^4/rho=rho+1.",
            PROVED,
            {
                "proof_kind": "EXACT_ALGEBRAIC_REDUCTION",
                "premises": ["rho^3=rho+1", "rho!=0"],
                "steps": ["rho^4/rho=rho^3", "rho^3=rho+1"],
                "conclusion": "rho^4/rho=rho+1",
            },
        ),
        _outcome(
            "DQPL-COLLATZ-GLOBAL",
            "Quartic phase closure entails convergence of every positive Collatz orbit.",
            OBSTRUCTED,
            {
                "proof_kind": "MISSING_RULE_GRAPH_PATH",
                "registered_local_rule": "T(n)=n/2 if even, else (3n+1)/2",
                "nonmonotone_witness": "7→11",
                "missing_lemmas": [
                    "COLLATZ_PHASE_MAP_TOTAL",
                    "COLLATZ_PHASE_TRANSITION_HOMOMORPHISM",
                    "WELL_FOUNDED_DESCENT_MEASURE",
                    "DESCENT_IMPLIES_EVENTUAL_ONE",
                ],
                "registered_derivation_path_exists": False,
            },
            dependencies=(
                "COLLATZ_PHASE_MAP_TOTAL",
                "COLLATZ_PHASE_TRANSITION_HOMOMORPHISM",
                "WELL_FOUNDED_DESCENT_MEASURE",
                "DESCENT_IMPLIES_EVENTUAL_ONE",
            ),
        ),
        _outcome(
            "DQPL-RH-TRANSFER",
            "Dyadic-quartic phase closure proves or falsifies that every nontrivial zeta zero has real part 1/2.",
            OBSTRUCTED,
            {
                "proof_kind": "MISSING_RULE_GRAPH_PATH",
                "registered_axis_fact": "Re(1/2+i*t)=1/2",
                "missing_lemmas": [
                    "ZETA_DOMAIN_AND_ANALYTIC_CONTINUATION_ENCODING",
                    "ZETA_ZERO_TO_PHASE_CLOSURE_EQUIVALENCE",
                    "PHASE_MAP_FAITHFULNESS",
                    "OFF_AXIS_ZERO_EXCLUSION_OR_COUNTEREXAMPLE_TRANSFER",
                ],
                "registered_derivation_path_exists": False,
                "decision_condition": "Add and verify every bridge lemma, or construct an exact off-axis zero certificate accepted by the same map.",
            },
            dependencies=(
                "ZETA_DOMAIN_AND_ANALYTIC_CONTINUATION_ENCODING",
                "ZETA_ZERO_TO_PHASE_CLOSURE_EQUIVALENCE",
                "PHASE_MAP_FAITHFULNESS",
                "OFF_AXIS_ZERO_EXCLUSION_OR_COUNTEREXAMPLE_TRANSFER",
            ),
        ),
        _outcome(
            "DQPL-QUADRATIC-RECIPROCITY-TRANSFER",
            "Quadratic reciprocity is equivalent to phase commutativity under modular phase halving.",
            OBSTRUCTED,
            {
                "proof_kind": "MISSING_RULE_GRAPH_PATH",
                "verified_component": "Bounded Legendre-symbol reciprocity checks are exact.",
                "missing_lemmas": [
                    "LEGENDRE_TO_PHASE_ALIGNMENT_MAP",
                    "MODULAR_PHASE_HALVING_COMPOSITION_LAW",
                    "RECIPROCITY_IF_AND_ONLY_IF_PHASE_COMMUTATIVITY",
                ],
                "registered_derivation_path_exists": False,
            },
            dependencies=(
                "LEGENDRE_TO_PHASE_ALIGNMENT_MAP",
                "MODULAR_PHASE_HALVING_COMPOSITION_LAW",
                "RECIPROCITY_IF_AND_ONLY_IF_PHASE_COMMUTATIVITY",
            ),
        ),
    ]

    if tuple(row["obligation_id"] for row in outcomes) != OBLIGATION_ORDER:
        raise AssertionError("formal obligation order mismatch")

    counts = Counter(row["status"] for row in outcomes)
    decisions = {
        "RIEMANN_HYPOTHESIS": {
            "status": OBSTRUCTED,
            "scope": SCOPE,
            "controlling_obligation": "DQPL-RH-TRANSFER",
            "next_admissible_operations": ["PROVE_BRIDGE_LEMMAS", "PRODUCE_EXACT_OFF_AXIS_ZERO_CERTIFICATE"],
        },
        "COLLATZ_CONJECTURE": {
            "status": OBSTRUCTED,
            "scope": SCOPE,
            "controlling_obligation": "DQPL-COLLATZ-GLOBAL",
            "next_admissible_operations": ["PROVE_WELL_FOUNDED_DESCENT", "PRODUCE_NONCONVERGENT_ORBIT_CERTIFICATE"],
        },
    }
    core = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "scope": SCOPE,
        "outcome_counts": {status: counts.get(status, 0) for status in (PROVED, FALSIFIED, OBSTRUCTED)},
        "hypothesis_decisions": decisions,
        "outcomes": outcomes,
    }
    return {
        **core,
        "formal_outcome_ledger_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-FORMAL-OUTCOME-LEDGER-V1"},
            core,
        ),
    }


def verify_formal_outcome_ledger(ledger: Mapping[str, Any]) -> dict[str, Any]:
    if ledger.get("schema") != SCHEMA:
        raise AssertionError("formal outcome schema mismatch")
    if ledger.get("classification") != CLASSIFICATION:
        raise AssertionError("formal outcome classification mismatch")
    outcomes = list(ledger.get("outcomes", []))
    if tuple(row.get("obligation_id") for row in outcomes) != OBLIGATION_ORDER:
        raise AssertionError("formal outcome obligation set mismatch")

    for row in outcomes:
        core = {key: value for key, value in row.items() if key != "outcome_hash72"}
        expected = hash72_digest(
            {"domain": "HHS-PASS-191-FORMAL-OUTCOME-V1", "obligation_id": row["obligation_id"]},
            core,
        )
        if row.get("outcome_hash72") != expected:
            raise AssertionError(f"formal outcome Hash72 mismatch: {row['obligation_id']}")

    core = {key: value for key, value in ledger.items() if key != "formal_outcome_ledger_hash72"}
    expected_ledger_hash = hash72_digest(
        {"domain": "HHS-PASS-191-FORMAL-OUTCOME-LEDGER-V1"},
        core,
    )
    if ledger.get("formal_outcome_ledger_hash72") != expected_ledger_hash:
        raise AssertionError("formal outcome ledger Hash72 mismatch")

    observed_counts = Counter(row["status"] for row in outcomes)
    expected_counts = {status: observed_counts.get(status, 0) for status in (PROVED, FALSIFIED, OBSTRUCTED)}
    if ledger.get("outcome_counts") != expected_counts:
        raise AssertionError("formal outcome counts mismatch")

    return {
        "ok": True,
        "outcome_count": len(outcomes),
        "outcome_counts": expected_counts,
        "formal_outcome_ledger_hash72": expected_ledger_hash,
    }
