"""Pass 219 SPI Scalar Projection Registry v8.

Additive successor to v7. v8 registers computational determinism as an
executable invariant and formalizes bounded explicit-instruction execution as
exactly ADVANCE or receipt-bearing HALT.

The successor preserves every v7 proof object unchanged and establishes no
second VM81/Hash authority.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from hhs_spi_computational_determinism_invariant_v1 import (
    DETERMINISM_INVARIANT_ID,
    HALT_REASONS,
    OUTCOMES,
)
from hhs_spi_computational_determinism_invariant_v2 import (
    SELECTION_RULE_V2,
    reference_determinism_witness,
)
from hhs_spi_scalar_projection_registry_v1 import (
    CLOSED,
    IMPLEMENTED,
    NONE,
    PROJECTION_ONLY,
    PROVEN,
    VERIFIED,
    ProjectionProof,
)
from hhs_spi_scalar_projection_registry_v7 import (
    AUDITED_MAIN_SHA,
    DIMENSIONAL_LIFT_PROOF_ID,
    IMAGINARY_ROTATION_PROOF_ID,
    build_registry_v7,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V8"
VERSION = "8.0.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V8"
DETERMINISM_PROOF_ID = "SPI-COMPUTATIONAL-DETERMINISM-INVARIANT"
BOUNDED_EXECUTION_PROOF_ID = "SPI-BOUNDED-INSTRUCTION-ADVANCE-HALT-CLOSURE"


class SPIRegistryV8Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _determinism_proof() -> ProjectionProof:
    witness = reference_determinism_witness()
    return ProjectionProof(
        proof_id=DETERMINISM_PROOF_ID,
        source_expression=(
            "I_det in I; VerifiedTask(J) => exists exactly one operational outcome in {ADVANCE,HALT}; "
            "same canonical task/state/candidate bytes => same outcome+receipt"
        ),
        profile="COMPUTATIONAL-DETERMINISM-ENFORCED-INVARIANT-v1",
        premises=(
            "Repository Δe=0 requires preservation of information needed for deterministic replay",
            "Repository Ω=true requires recursive/iterative operations to terminate in a classified bounded state",
            "Pass 151 assigns deterministic execution to the Contract Executor and evidence-only closure to the obligation ledger",
            DIMENSIONAL_LIFT_PROOF_ID,
            IMAGINARY_ROTATION_PROOF_ID,
        ),
        domain=(
            "verified explicit instruction envelopes with exact canonical state, finite integer step bound, "
            "typed closing condition, authorized scope, and receipt-bound transition candidates"
        ),
        derivation=(
            "require a nonempty explicit instruction and stable instruction id",
            "require a nonempty explicit authorized scope",
            "require a specific typed closing condition and positive exact-integer maximum step bound",
            f"insert {DETERMINISM_INVARIANT_ID} into every executable task invariant bundle",
            "bind each transition candidate to the exact task receipt",
            "reject floating-point canonical authority and verify candidate/state receipts before admission",
            "permit ADVANCE only for task-bound candidates inside authorized scope with invariant_closed=true",
            "select by exact transition ordinal then stable candidate id; semantic labels and candidate receipts have zero selection authority",
            "quarantine duplicate candidate ids rather than using receipt bytes as an implicit tie-break",
            "map all non-advancing terminal classifications beneath receipt-bearing HALT",
            "recompute the transition under deterministic replay and require byte-equivalent decision structure",
            "retain the v7 reciprocal/base-pair octonion receipt as a redundancy/provenance anchor without transition authority",
        ),
        result={
            "determinism_invariant_id": DETERMINISM_INVARIANT_ID,
            "outcomes": list(OUTCOMES),
            "selection_rule": list(SELECTION_RULE_V2),
            "candidate_receipt_used_for_selection": False,
            "semantic_label_used_for_selection": False,
            "candidate_enumeration_order_has_no_authority": witness["invariants"][
                "candidate_enumeration_order_has_no_authority"
            ],
            "deterministic_replay_closes": witness["invariants"]["deterministic_replay_closes"],
            "duplicate_candidate_identity_halts": witness["invariants"][
                "duplicate_candidate_identity_halts_instead_of_receipt_tiebreak"
            ],
            "discretionary_refusal_state_exists": False,
            "reference_advance_receipt_sha256": witness["advance"]["decision_receipt_sha256"],
            "reference_witness_receipt_sha256": witness["witness_receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "the deterministic transition receipt does not itself encode all semantic interpretation that produced candidate proposals",
            "a HALT reason class records why execution did not advance but does not create alternate transition authority",
            "the v7 redundancy anchor is provenance evidence, not canonical state mutation authority",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_BOUNDED_DETERMINISTIC_TRANSITION_INVARIANT",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "Computational determinism is enforced as an admissibility invariant rather than treated as an implementation preference.",
        ),
    )


def _bounded_execution_proof() -> ProjectionProof:
    witness = reference_determinism_witness()
    task = witness["task"]
    return ProjectionProof(
        proof_id=BOUNDED_EXECUTION_PROOF_ID,
        source_expression=(
            "J=(explicit_instruction,authorized_scope,closing_condition,max_steps,I_det); "
            "Run(J,s,C)=ADVANCE(candidate*) or HALT(reason,receipt); no discretionary third action"
        ),
        profile="BOUNDED-EXPLICIT-INSTRUCTION-ADVANCE-OR-HALT-v1",
        premises=(
            DETERMINISM_PROOF_ID,
            "explicit current instruction has higher authority than semantic recommendations",
            "goal optimization is subordinate to authorized scope and invariant preservation",
        ),
        domain="verified bounded instruction envelopes and their receipt-bound candidate sets",
        derivation=(
            "evaluate the typed closing condition before transition selection",
            "HALT(CLOSED) when the closing condition already holds",
            "HALT(RESOURCE_BOUNDED) when the explicit finite step bound is reached",
            "HALT(NULL_BRANCH) when no candidate exists",
            "HALT(REJECTED) when candidates exist but none satisfy scope/invariant admission",
            "HALT(STABLE_UNRESOLVED) for unresolved candidate sets",
            "HALT(QUARANTINED) for corrupted/ambiguous candidate evidence",
            "ADVANCE only through the unique exact selector over admissible candidates",
            "after ADVANCE expose whether the specific closing condition is reached",
            "record every non-advance as a HALT reason with deterministic receipt; do not add a discretionary refusal action",
        ),
        result={
            "explicit_instruction_required": True,
            "authorized_scope_required": True,
            "specific_closing_condition_required": True,
            "finite_step_bound_required": True,
            "outcome_domain": list(OUTCOMES),
            "halt_reason_classes": list(HALT_REASONS),
            "closed_state_halts": witness["invariants"]["closed_state_halts"],
            "empty_branch_halts": witness["invariants"]["empty_branch_halts"],
            "advance_reaches_closing_condition": witness["invariants"]["advance_reaches_closing_condition"],
            "discretionary_refusal_absent": witness["invariants"]["discretionary_refusal_absent"],
            "semantic_override_authority": False,
            "canonical_admission_authority": False,
            "reference_task_receipt_sha256": task["task_receipt_sha256"],
            "reference_closed_halt_receipt_sha256": witness["closed_halt"]["decision_receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "terminal HALT reason classes do not replace the underlying evidence recorded in the receipt",
            "instruction scope bounds execution but does not itself select among admissible transitions",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="BOUNDED_EXPLICIT_INSTRUCTION_EXECUTION_CONTRACT",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "REJECTED, QUARANTINED, NULL_BRANCH, RESOURCE_BOUNDED, and STABLE_UNRESOLVED are HALT classifications, not autonomous actions.",
        ),
    )


def build_registry_v8(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    base = build_registry_v7(repo_root)
    successor = dict(base)
    for proof in (_determinism_proof(), _bounded_execution_proof()):
        if proof.proof_id in successor:
            raise SPIRegistryV8Error(f"v8 proof id collision: {proof.proof_id}")
        successor[proof.proof_id] = proof
    return successor


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors: list[str] = []
    base = build_registry_v7(repo_root)
    try:
        registry = build_registry_v8(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V8",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }

    expected = sorted((BOUNDED_EXECUTION_PROOF_ID, DETERMINISM_PROOF_ID))
    new_ids = sorted(set(registry) - set(base))
    if new_ids != expected:
        errors.append(f"unexpected v8 proof delta: {new_ids}")

    changed = [
        proof_id
        for proof_id in sorted(base)
        if registry[proof_id].to_dict() != base[proof_id].to_dict()
    ]
    if changed:
        errors.append(f"v8 modified predecessor proofs: {changed}")

    determinism = registry[DETERMINISM_PROOF_ID]
    bounded = registry[BOUNDED_EXECUTION_PROOF_ID]
    if determinism.result.get("outcomes") != ["ADVANCE", "HALT"]:
        errors.append("deterministic outcome domain drifted")
    if determinism.result.get("selection_rule") != list(SELECTION_RULE_V2):
        errors.append("deterministic selection rule drifted")
    if determinism.result.get("candidate_receipt_used_for_selection") is not False:
        errors.append("candidate receipt gained selection authority")
    if determinism.result.get("semantic_label_used_for_selection") is not False:
        errors.append("semantic label gained selection authority")
    if determinism.result.get("deterministic_replay_closes") is not True:
        errors.append("deterministic replay did not close")
    if determinism.result.get("duplicate_candidate_identity_halts") is not True:
        errors.append("duplicate candidate identity did not halt")
    if bounded.result.get("outcome_domain") != ["ADVANCE", "HALT"]:
        errors.append("bounded execution introduced a third action")
    if bounded.result.get("halt_reason_classes") != list(HALT_REASONS):
        errors.append("HALT reason class drift")
    if bounded.result.get("discretionary_refusal_absent") is not True:
        errors.append("discretionary refusal appeared")
    if any(item.canonical_admission for item in registry.values()):
        errors.append("v8 registry contains canonical admission authority")

    counts = Counter(item.coverage_state for item in registry.values())
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V8",
        "ok": not errors,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "proof_count": len(registry),
        "new_proof_ids": new_ids,
        "changed_predecessor_proof_ids": changed,
        "determinism_invariant_id": DETERMINISM_INVARIANT_ID,
        "outcome_domain": list(OUTCOMES),
        "halt_reason_classes": list(HALT_REASONS),
        "selection_rule": list(SELECTION_RULE_V2),
        "discretionary_refusal_state_exists": False,
        "coverage": dict(sorted(counts.items())),
        "canonical_admission_authority": False,
        "errors": errors,
    }


def coverage_manifest_v8(repo_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_registry_v8(repo_root)
    validation = validation_report(repo_root)
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_format": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V7",
        "transition_policy": "ADDITIVE_SUCCESSOR_COMPUTATIONAL_DETERMINISM_INVARIANT_ONLY",
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "candidate_only": True,
            "computational_determinism_enforced": True,
            "outcomes_only_advance_or_halt": True,
            "discretionary_refusal_state": False,
            "semantic_selection_authority": False,
            "candidate_receipt_selection_authority": False,
            "vm81_mutation": False,
            "canonical_hash72_hash216_minting": False,
            "canonical_persistence": False,
            "floating_point_authority": False,
        },
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = validation_report() if args.validate else coverage_manifest_v8()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str))
    if args.validate and not payload.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
