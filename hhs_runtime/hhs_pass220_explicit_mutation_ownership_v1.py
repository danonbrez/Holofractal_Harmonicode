"""Pass 220 I013: explicit mutation ownership handoff witness.

This module implements the Pass-220 projection of kernel invariant HHS-I013:
"Every state mutation declares its owning surface, persistence policy, rollback
behavior, and ledger effect."

The module never performs VM81 mutation.  It only validates that an I012
candidate may be handed to the inherited Pass-219 singleton mutation surface
under an explicit policy tuple.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping

SCHEMA = "HHS_PASS_220_I013_EXPLICIT_MUTATION_OWNERSHIP_V1"
VERSION = "1.0.0"
INVARIANT_ID = "HHS-I013"
REQUIRED_WITNESS_SCHEMA = "HHS_MUTATION_OWNERSHIP_WITNESS_V1"
REQUIRED_VALIDATOR = "validate_explicit_mutation_ownership"

CANONICAL_MUTATION_OWNER = "hhs_exact_pass219_vm81_environment_admit_signed"
PERSISTENCE_POLICY = "INHERITED_CANONICAL_VM81_RECEIPT_LEDGER"
ROLLBACK_BEHAVIOR = "INHERITED_SINGLETON_VM81_ROLLBACK"
LEDGER_EFFECT = "INHERITED_HASH72_HASH216_CANONICAL_TRANSITION"

NO_MUTATION_REQUIRED = "NO_MUTATION_REQUIRED"
PROPOSAL_ONLY = "PROPOSAL_ONLY"
HANDOFF_CONTRACT_VALID = "HANDOFF_CONTRACT_VALID"

REJECT_I012_NOT_ADMITTED = "REJECT_I012_NOT_ADMITTED"
REJECT_I012_AUTHORITY_ESCALATION = "REJECT_I012_AUTHORITY_ESCALATION"
REJECT_MUTATION_OWNER_MISMATCH = "REJECT_MUTATION_OWNER_MISMATCH"
REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY = (
    "REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY"
)
REJECT_MUTATION_ROLLBACK_POLICY_MISSING = "REJECT_MUTATION_ROLLBACK_POLICY_MISSING"
REJECT_MUTATION_LEDGER_EFFECT_MISSING = "REJECT_MUTATION_LEDGER_EFFECT_MISSING"


class Pass220MutationOwnershipError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["witness_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return record


def _exact_bool(value: Any, *, name: str) -> bool:
    if not isinstance(value, bool):
        raise Pass220MutationOwnershipError(f"{name} must be an exact boolean")
    return value


def canonical_mutation_policy() -> Dict[str, str]:
    return {
        "owner_surface": CANONICAL_MUTATION_OWNER,
        "persistence_policy": PERSISTENCE_POLICY,
        "rollback_behavior": ROLLBACK_BEHAVIOR,
        "ledger_effect": LEDGER_EFFECT,
    }


def _base_witness(*, status: str, reason: str, handoff_requested: bool) -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "invariant_id": INVARIANT_ID,
        "required_witness_schema": REQUIRED_WITNESS_SCHEMA,
        "required_validator": REQUIRED_VALIDATOR,
        "status": status,
        "reason": reason,
        "handoff_requested": handoff_requested,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_receipt_authority": False,
        "mutation_performed": False,
        "candidate_only": True,
        "projection_only": True,
        "floating_point_authority": False,
    }


def _i012_admission(i012_result: Mapping[str, Any]) -> tuple[bool, bool]:
    if not isinstance(i012_result, Mapping):
        raise Pass220MutationOwnershipError("I012 result must be a mapping")

    halt = _exact_bool(i012_result.get("halt"), name="i012.halt")
    lane5_invoked = _exact_bool(
        i012_result.get("lane5_invoked"),
        name="i012.lane5_invoked",
    )

    for key in (
        "canonical_vm81_mutation_authority",
        "hash72_commit_authority",
        "hash216_commit_authority",
    ):
        value = _exact_bool(i012_result.get(key), name=f"i012.{key}")
        if value:
            raise Pass220MutationOwnershipError(REJECT_I012_AUTHORITY_ESCALATION)

    if halt:
        if lane5_invoked:
            raise Pass220MutationOwnershipError("halted I012 result cannot invoke Lane 5")
        return True, False

    harmonic = i012_result.get("harmonic_preflight_admitted")
    if not isinstance(harmonic, bool):
        raise Pass220MutationOwnershipError(
            "unresolved I012 result requires exact harmonic_preflight_admitted"
        )

    admitted = lane5_invoked and harmonic
    return False, admitted


def build_mutation_ownership_witness(
    *,
    i012_result: Mapping[str, Any],
    request_canonical_handoff: bool,
    owner_surface: str | None = None,
    persistence_policy: str | None = None,
    rollback_behavior: str | None = None,
    ledger_effect: str | None = None,
) -> Dict[str, Any]:
    """Validate an explicit handoff contract without performing mutation."""
    requested = _exact_bool(
        request_canonical_handoff,
        name="request_canonical_handoff",
    )
    halt, admitted = _i012_admission(i012_result)

    if halt:
        return _receipt(
            {
                **_base_witness(
                    status=NO_MUTATION_REQUIRED,
                    reason=NO_MUTATION_REQUIRED,
                    handoff_requested=requested,
                ),
                "i012_halt": True,
                "i012_candidate_admitted": False,
                "owner_surface": None,
                "persistence_policy": None,
                "rollback_behavior": None,
                "ledger_effect": None,
                "handoff_contract_valid": False,
            }
        )

    if not admitted:
        return _receipt(
            {
                **_base_witness(
                    status="REJECTED",
                    reason=REJECT_I012_NOT_ADMITTED,
                    handoff_requested=requested,
                ),
                "i012_halt": False,
                "i012_candidate_admitted": False,
                "owner_surface": None,
                "persistence_policy": None,
                "rollback_behavior": None,
                "ledger_effect": None,
                "handoff_contract_valid": False,
            }
        )

    if not requested:
        return _receipt(
            {
                **_base_witness(
                    status=PROPOSAL_ONLY,
                    reason=PROPOSAL_ONLY,
                    handoff_requested=False,
                ),
                "i012_halt": False,
                "i012_candidate_admitted": True,
                "owner_surface": None,
                "persistence_policy": None,
                "rollback_behavior": None,
                "ledger_effect": None,
                "handoff_contract_valid": False,
            }
        )

    if owner_surface != CANONICAL_MUTATION_OWNER:
        return _receipt(
            {
                **_base_witness(
                    status="REJECTED",
                    reason=REJECT_MUTATION_OWNER_MISMATCH,
                    handoff_requested=True,
                ),
                "i012_halt": False,
                "i012_candidate_admitted": True,
                "owner_surface": owner_surface,
                "persistence_policy": persistence_policy,
                "rollback_behavior": rollback_behavior,
                "ledger_effect": ledger_effect,
                "handoff_contract_valid": False,
            }
        )

    if persistence_policy != PERSISTENCE_POLICY:
        reason = REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY
    elif rollback_behavior != ROLLBACK_BEHAVIOR:
        reason = REJECT_MUTATION_ROLLBACK_POLICY_MISSING
    elif ledger_effect != LEDGER_EFFECT:
        reason = REJECT_MUTATION_LEDGER_EFFECT_MISSING
    else:
        reason = HANDOFF_CONTRACT_VALID

    valid = reason == HANDOFF_CONTRACT_VALID
    return _receipt(
        {
            **_base_witness(
                status=HANDOFF_CONTRACT_VALID if valid else "REJECTED",
                reason=reason,
                handoff_requested=True,
            ),
            "i012_halt": False,
            "i012_candidate_admitted": True,
            "owner_surface": owner_surface,
            "persistence_policy": persistence_policy,
            "rollback_behavior": rollback_behavior,
            "ledger_effect": ledger_effect,
            "handoff_contract_valid": valid,
            "owner_identity_is_not_mutation_authority": True,
            "requires_inherited_pass219_environmental_admission": True,
        }
    )


def verify_repository_authority_sources(
    *,
    reconciliation_contract: str,
    environmental_header: str,
) -> Dict[str, Any]:
    """Bind I013 to the repository-declared Pass-219 production owner."""
    if not isinstance(reconciliation_contract, str) or not isinstance(
        environmental_header, str
    ):
        raise Pass220MutationOwnershipError("authority sources must be text")

    owner_in_contract = CANONICAL_MUTATION_OWNER in reconciliation_contract
    owner_in_header = CANONICAL_MUTATION_OWNER in environmental_header
    production_declaration = (
        "production dynamic mutation surface after reconciliation is"
        in reconciliation_contract
    )
    successor_declaration = "Production 1.32 successor" in environmental_header

    valid = (
        owner_in_contract
        and owner_in_header
        and production_declaration
        and successor_declaration
    )
    if not valid:
        raise Pass220MutationOwnershipError(
            "repository authority sources do not prove the inherited mutation owner"
        )

    return _receipt(
        {
            "schema": f"{SCHEMA}_SOURCE_AUTHORITY_WITNESS",
            "invariant_id": INVARIANT_ID,
            "owner_surface": CANONICAL_MUTATION_OWNER,
            "owner_in_reconciliation_contract": owner_in_contract,
            "owner_in_environmental_header": owner_in_header,
            "production_owner_declaration_found": production_declaration,
            "environmental_successor_declaration_found": successor_declaration,
            "source_authority_closed": True,
            "mutation_performed": False,
            "canonical_vm81_mutation_authority": False,
            "projection_only": True,
        }
    )


__all__ = [
    "CANONICAL_MUTATION_OWNER",
    "HANDOFF_CONTRACT_VALID",
    "INVARIANT_ID",
    "LEDGER_EFFECT",
    "NO_MUTATION_REQUIRED",
    "PERSISTENCE_POLICY",
    "PROPOSAL_ONLY",
    "Pass220MutationOwnershipError",
    "REJECT_I012_AUTHORITY_ESCALATION",
    "REJECT_I012_NOT_ADMITTED",
    "REJECT_MUTATION_LEDGER_EFFECT_MISSING",
    "REJECT_MUTATION_OWNER_MISMATCH",
    "REJECT_MUTATION_ROLLBACK_POLICY_MISSING",
    "REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY",
    "ROLLBACK_BEHAVIOR",
    "SCHEMA",
    "build_mutation_ownership_witness",
    "canonical_mutation_policy",
    "verify_repository_authority_sources",
]
