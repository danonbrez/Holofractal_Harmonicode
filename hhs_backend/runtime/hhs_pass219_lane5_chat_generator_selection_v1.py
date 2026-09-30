"""Pass 219 / Lane 5 chatbot generator selection.

This module adapts already-visible, already-ready TEXT_GENERATION members into
the inherited Pass 124 parallel deterministic generalization selector.  It does
not execute providers, grant authority, or treat probability as admission.

Selection is therefore:

    typed visible candidates
      -> three deterministic invariant witness lanes
      -> invariant isolation
      -> exact Fraction weighting
      -> replay-validated Pass 124 selection
      -> provider invocation remains separately governed

Local provider order is evidence only.  It is never composition authority.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_runtime.hhs_pass124_parallel_deterministic_generalization_v1 import (
    ParallelDeterministicGeneralizationEngine,
)

SCHEMA = "HHS_PASS219_LANE5_CHAT_GENERATOR_SELECTION_V1"


def _normalized_capabilities(member: Mapping[str, Any]) -> set[str]:
    return {
        str(value).strip().upper().replace("-", "_")
        for value in (member.get("capabilities") or ())
        if str(value).strip()
    }


def _eligible(
    member: Mapping[str, Any],
    failed_member_ids: set[str],
) -> bool:
    member_id = str(member.get("member_id") or "")
    return bool(
        member_id
        and member_id not in failed_member_ids
        and member.get("visible_to_lane5", True) is not False
        and member.get("callable_from_unified_chat") is True
        and member.get("ready") is True
        and "TEXT_GENERATION" in _normalized_capabilities(member)
        and member.get("semantic_fallback_is_text_generation") is not False
        if str(member.get("role") or "") == "SEMANTIC_CONTEXT_CONTRIBUTOR"
        else (
            member_id
            and member_id not in failed_member_ids
            and member.get("visible_to_lane5", True) is not False
            and member.get("callable_from_unified_chat") is True
            and member.get("ready") is True
            and "TEXT_GENERATION" in _normalized_capabilities(member)
        )
    )


def _utility(member: Mapping[str, Any]) -> Fraction:
    """Exact evidence weight; configuration can inform search, never authorize it."""
    value = 1
    if member.get("declared_primary") is True:
        value += 2
    if member.get("configured_primary") is True:
        value += 1
    if member.get("loaded") is True:
        value += 1
    if member.get("configured") is True:
        value += 1
    return Fraction(value, 1)


def _validator(lane_id: str):
    def validate(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
        evidence = dict(candidate.get("selection_evidence") or {})
        claims = dict(candidate.get("invariant_claims") or {})
        admitted = bool(
            evidence.get("visible_to_lane5")
            and evidence.get("callable")
            and evidence.get("ready")
            and evidence.get("text_generation")
            and evidence.get("provider_output_canonical_authority") is False
            and evidence.get("probability_may_authorize_state") is False
        )
        return {
            "admitted": admitted,
            "validated_invariants": claims,
            "reason_codes": [
                f"{lane_id}_VISIBLE_TYPED_READY_GENERATOR"
                if admitted
                else f"{lane_id}_REJECTED_GENERATOR_EVIDENCE"
            ],
        }
    return validate


def select_lane5_chat_generator(
    *,
    fabric: Mapping[str, Any],
    thread_id: str,
    content: str,
    failed_member_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Select one admissible generator with inherited Pass 124 consensus/weighting."""
    failed = {str(value) for value in failed_member_ids}
    members = [
        dict(member)
        for member in (fabric.get("members") or ())
        if isinstance(member, Mapping) and _eligible(member, failed)
    ]
    if not members:
        return {
            "schema": SCHEMA,
            "ok": False,
            "status": "NO_ADMISSIBLE_VISIBLE_TEXT_GENERATOR",
            "selected_member_id": None,
            "candidate_count": 0,
            "failed_member_ids": sorted(failed),
            "candidate_only": True,
            "probability_created_authority": False,
            "canonical_vm81_mutation_authority": False,
        }

    request_root = hash72(
        "HHS_PASS219_LANE5_CHAT_SELECTION_REQUEST_V1",
        {
            "thread_id": str(thread_id),
            "content": str(content),
            "failed_member_ids": sorted(failed),
            "fabric_root_hash72": fabric.get("fabric_root_hash72"),
        },
    )
    fabric_root = str(
        fabric.get("fabric_root_hash72")
        or hash72("HHS_PASS219_LANE5_CHAT_FABRIC_FALLBACK_V1", dict(fabric))
    )

    engine = ParallelDeterministicGeneralizationEngine()
    candidates: list[dict[str, Any]] = []
    member_by_candidate_root: dict[str, str] = {}
    candidate_evidence: dict[str, dict[str, Any]] = {}

    for member in sorted(members, key=lambda item: str(item.get("member_id"))):
        member_id = str(member["member_id"])
        member_root = hash72(
            "HHS_PASS219_LANE5_CHAT_MEMBER_V1",
            member,
        )
        claims = {
            "visible_to_lane5": True,
            "callable_from_unified_chat": True,
            "runtime_ready": True,
            "text_generation": True,
            "provider_output_canonical_authority": False,
            "probability_may_authorize_state": False,
        }
        candidate = engine.make_candidate(
            candidate_id=member_id,
            semantic_root_hash72=member_root,
            invariant_claims=claims,
            evidence_roots=[fabric_root, member_root, request_root],
            utility=_utility(member),
            cost=Fraction(1, 1),
        )
        evidence = {
            "visible_to_lane5": member.get("visible_to_lane5", True) is not False,
            "callable": member.get("callable_from_unified_chat") is True,
            "ready": member.get("ready") is True,
            "text_generation": "TEXT_GENERATION" in _normalized_capabilities(member),
            "provider_output_canonical_authority": False,
            "probability_may_authorize_state": False,
        }
        candidate["selection_evidence"] = evidence
        # selection_evidence is validation input, not part of the Pass 124
        # candidate identity. Keep a side table so the inherited root remains exact.
        candidate_evidence[candidate["candidate_root_hash72"]] = evidence
        member_by_candidate_root[candidate["candidate_root_hash72"]] = member_id
        candidates.append(candidate)

    # Pass 124 verifies its own candidate root, so strip the side-channel evidence
    # before evaluation and restore it only inside deterministic validators.
    pure_candidates = []
    for candidate in candidates:
        pure = dict(candidate)
        pure.pop("selection_evidence", None)
        pure_candidates.append(pure)

    evidence_by_candidate_id = {
        candidate["candidate_id"]: candidate_evidence[candidate["candidate_root_hash72"]]
        for candidate in pure_candidates
    }

    def lane(lane_id: str):
        base = _validator(lane_id)

        def validate(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
            enriched = dict(candidate)
            enriched["selection_evidence"] = evidence_by_candidate_id[
                str(candidate["candidate_id"])
            ]
            return base(enriched)

        return validate

    lanes = [
        ("lane5_capability", lane("LANE5_CAPABILITY")),
        ("runtime_readiness", lane("RUNTIME_READINESS")),
        ("authority_membrane", lane("AUTHORITY_MEMBRANE")),
    ]
    parallel = engine.evaluate_parallel(pure_candidates, lane_validators=lanes)
    selection = engine.select(
        parallel,
        entropy_seed_root_hash72=request_root,
    )
    replay = engine.replay(parallel, request_root, selection)

    selected_root = str(selection["selected_candidate_root_hash72"])
    selected_member_id = member_by_candidate_root[selected_root]
    result = {
        "schema": SCHEMA,
        "ok": True,
        "status": "PASS219_LANE5_GENERATOR_SELECTED",
        "selected_member_id": selected_member_id,
        "candidate_count": len(pure_candidates),
        "candidate_member_ids": sorted(
            str(candidate["candidate_id"]) for candidate in pure_candidates
        ),
        "failed_member_ids": sorted(failed),
        "request_root_hash72": request_root,
        "parallel_root_hash72": parallel["parallel_root_hash72"],
        "selection": selection,
        "replay": replay,
        "selection_uses_pass124_parallel_consensus": True,
        "probability_created_authority": False,
        "provider_invocation_still_requires_governed_membrane": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }
    result["selection_receipt_hash72"] = hash72(SCHEMA, result)
    return result


__all__ = [
    "SCHEMA",
    "select_lane5_chat_generator",
]
