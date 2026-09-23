"""Pass 220 I043 Lane 5 alignment/math/physics authority closure.

This module does not replace, reinterpret, weaken, or independently reimplement
the repository's existing ethical alignment logic, exact mathematics, or exact
physics surfaces.  It composes their already-authoritative results into one
fail-closed pre-admission witness.

Authority order:
    existing narrative/ethical membrane
    AND existing exact mathematical closure
    AND existing exact physics closure
    AND existing I042 shared-root fabric
    -> inherited Pass 219 VM81 admission bridge

The module itself has no VM81, Hash72, Hash216, learning, model-weight, or
persistence authority.  A non-PASS ethical invariant, unresolved ethical
invariant, scope failure, mathematical witness drift, physics witness drift,
or shared-root ancestry split makes the joint state non-admissible.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Optional, Tuple

from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalDecision,
    INVARIANT_ORDER,
    InvariantState,
    all_pass_invariants,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    EpistemicAdequacyTrace,
    EthicalNarrativeEvaluationV2,
    evaluate_action_v2,
)
from hhs_runtime.hhs_pass220_holofractal_relativistic_game_engine_v1 import (
    holofractal_relativistic_game_engine_witness,
)
from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    lane5_multimodal_shared_root_witness,
    shared_multimodal_root_payload,
    shared_multimodal_root_sha256,
)
from hhs_runtime.hhs_pass220_quantum_geometric_unification_closure_v1 import (
    quantum_geometric_unification_witness,
)

SCHEMA = "HHS_PASS_220_I043_LANE5_ALIGNMENT_PHYSICS_AUTHORITY_CLOSURE_V1"
VERSION = "1.0.0-checkpoint.43"
PROFILE = "PASS220-I043-LANE5-ALIGNMENT-PHYSICS-AUTHORITY-CLOSURE-v1"
WITNESS_SCHEMA = "HHS_PASS_220_I043_JOINT_AUTHORITY_WITNESS_V1"

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "CURRENT_REPOSITORY_ALIGNMENT_LOGIC_IS_HIGHEST_AUTHORITY",
    "CURRENT_REPOSITORY_MATH_IS_HIGHEST_AUTHORITY",
    "CURRENT_REPOSITORY_PHYSICS_IS_HIGHEST_AUTHORITY",
    "NO_ALIGNMENT_REIMPLEMENTATION_OR_RECLASSIFICATION",
    "NO_MATH_REIMPLEMENTATION_OR_APPROXIMATION",
    "NO_PHYSICS_REIMPLEMENTATION_OR_APPROXIMATION",
    "ALL_ETHICAL_INVARIANTS_MUST_PASS",
    "ETHICAL_SCOPE_PREFLIGHT_MUST_CLOSE",
    "I039_EXACT_MATH_CLOSURE_REQUIRED",
    "I041_EXACT_PHYSICS_CYCLE_REQUIRED",
    "I042_SHARED_ROOT_FABRIC_REQUIRED",
    "I039_I041_I042_ANCESTRY_MUST_BIND",
    "MISALIGNED_OR_UNRESOLVED_STATE_HAS_NO_CANONICAL_TRANSITION",
    "JOINT_AUTHORITY_WITNESS_REQUIRED_BEFORE_VM81_ADMISSION",
    "NO_NEW_VM81_HASH_OR_PERSISTENCE_AUTHORITY",
)


class Pass220I043AuthorityError(RuntimeError):
    """Fail-closed I043 joint-authority error."""


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
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


@lru_cache(maxsize=1)
def _canonical_math_witness() -> Dict[str, Any]:
    return quantum_geometric_unification_witness()


@lru_cache(maxsize=1)
def _canonical_physics_witness() -> Dict[str, Any]:
    return holofractal_relativistic_game_engine_witness()


@lru_cache(maxsize=1)
def _canonical_fabric_witness() -> Dict[str, Any]:
    return lane5_multimodal_shared_root_witness()


@lru_cache(maxsize=1)
def _canonical_shared_root_payload() -> Dict[str, Any]:
    return shared_multimodal_root_payload()


def _exact_witness(
    *,
    name: str,
    provided: Optional[Mapping[str, Any]],
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    if provided is None:
        return dict(expected)
    candidate = dict(provided)
    if candidate != dict(expected):
        raise Pass220I043AuthorityError(f"{name} witness drift")
    return candidate


def _validate_authority_surfaces(
    *,
    math_witness: Optional[Mapping[str, Any]] = None,
    physics_witness: Optional[Mapping[str, Any]] = None,
    fabric_witness: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    math = _exact_witness(
        name="math",
        provided=math_witness,
        expected=_canonical_math_witness(),
    )
    physics = _exact_witness(
        name="physics",
        provided=physics_witness,
        expected=_canonical_physics_witness(),
    )
    fabric = _exact_witness(
        name="fabric",
        provided=fabric_witness,
        expected=_canonical_fabric_witness(),
    )
    payload = _canonical_shared_root_payload()

    if math.get("ok") is not True:
        raise Pass220I043AuthorityError("I039 exact math witness is not closed")
    if physics.get("ok") is not True:
        raise Pass220I043AuthorityError("I041 exact physics witness is not closed")
    if fabric.get("ok") is not True:
        raise Pass220I043AuthorityError("I042 shared-root fabric is not closed")

    math_result = math.get("result")
    physics_result = physics.get("result")
    fabric_result = fabric.get("result")
    if not isinstance(math_result, Mapping):
        raise Pass220I043AuthorityError("I039 result missing")
    if not isinstance(physics_result, Mapping):
        raise Pass220I043AuthorityError("I041 result missing")
    if not isinstance(fabric_result, Mapping):
        raise Pass220I043AuthorityError("I042 result missing")

    if math_result.get("simultaneous_projection_closure") is not True:
        raise Pass220I043AuthorityError("I039 simultaneous projection closure open")
    if physics_result.get("exact_cycle_closed") is not True:
        raise Pass220I043AuthorityError("I041 exact physics cycle open")
    if fabric_result.get("exact_multimodal_fabric_closed") is not True:
        raise Pass220I043AuthorityError("I042 exact multimodal fabric open")

    for name, witness in (
        ("I039", math),
        ("I041", physics),
        ("I042", fabric),
    ):
        if witness.get("canonical_admission_authority") is not False:
            raise Pass220I043AuthorityError(
                f"{name} reference surface escalated canonical admission authority"
            )

    math_root = math.get("shared_state_root_sha256")
    physics_i039_root = physics_result.get("shared_i039_root_sha256")
    payload_i039_root = payload.get("i041_i039_shared_root_sha256")
    if not math_root or not (
        math_root == physics_i039_root == payload_i039_root
    ):
        raise Pass220I043AuthorityError("I039/I041/I042 ancestry root split")

    physics_root = physics_result.get("shared_relativistic_projection_root_sha256")
    if payload.get("i041_relativistic_projection_root_sha256") != physics_root:
        raise Pass220I043AuthorityError("I041/I042 physics projection root split")

    fabric_root = fabric.get("shared_multimodal_root_sha256")
    if fabric_root != shared_multimodal_root_sha256():
        raise Pass220I043AuthorityError("I042 shared multimodal root drift")

    return {
        "math_witness": math,
        "physics_witness": physics,
        "fabric_witness": fabric,
        "math_shared_state_root_sha256": math_root,
        "physics_projection_root_sha256": physics_root,
        "fabric_shared_root_sha256": fabric_root,
        "ancestry_root_shared": True,
        "math_authority_closed": True,
        "physics_authority_closed": True,
        "fabric_authority_closed": True,
    }


def _ethical_projection(
    refined: EthicalNarrativeEvaluationV2,
) -> Dict[str, Any]:
    ethical = refined.evaluation
    results = tuple(ethical.invariant_results)
    ordered_ids = tuple(item.invariant_id for item in results)
    if ordered_ids != tuple(INVARIANT_ORDER):
        raise Pass220I043AuthorityError("ethical invariant order drift")

    state_to_trinary = {
        InvariantState.PASS: 1,
        InvariantState.UNRESOLVED: 0,
        InvariantState.FAIL: -1,
    }
    trinary = tuple(
        {
            "invariant_id": item.invariant_id,
            "state": item.state.value,
            "trinary": state_to_trinary[item.state],
        }
        for item in results
    )
    all_pass = all(item.state is InvariantState.PASS for item in results)
    alignment_closed = all((
        ethical.decision is EthicalDecision.EXECUTE_LOCAL_PROVISIONAL,
        ethical.prospective_alignment is True,
        ethical.scope.decision is None,
        not ethical.failed_invariants,
        not ethical.unresolved_invariants,
        all_pass,
    ))
    return {
        "alignment_engine_version": refined.to_dict()["version"],
        "alignment_engine_authority": refined.to_dict()["authority"],
        "ethical_decision_preserved_verbatim": ethical.decision.value,
        "ethical_reference_receipt_hash72": ethical.reference_receipt_hash72,
        "ethical_trace_receipt_hash72": refined.trace_receipt_hash72,
        "ordered_invariant_projection": trinary,
        "all_ethics_invariants_pass": all_pass,
        "scope_preflight_closed": ethical.scope.decision is None,
        "alignment_authority_closed": alignment_closed,
        "alignment_decision_reimplemented": False,
        "alignment_invariant_reclassification_performed": False,
    }


def build_lane5_alignment_physics_authority_witness(
    refined: EthicalNarrativeEvaluationV2,
    *,
    math_witness: Optional[Mapping[str, Any]] = None,
    physics_witness: Optional[Mapping[str, Any]] = None,
    fabric_witness: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Bind existing alignment, math, physics, and fabric authority surfaces."""

    if not isinstance(refined, EthicalNarrativeEvaluationV2):
        raise Pass220I043AuthorityError(
            "existing EthicalNarrativeEvaluationV2 trace required"
        )

    ethical = _ethical_projection(refined)
    surfaces = _validate_authority_surfaces(
        math_witness=math_witness,
        physics_witness=physics_witness,
        fabric_witness=fabric_witness,
    )
    joint_closed = all((
        ethical["alignment_authority_closed"],
        surfaces["math_authority_closed"],
        surfaces["physics_authority_closed"],
        surfaces["fabric_authority_closed"],
        surfaces["ancestry_root_shared"],
    ))

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "local_constraints": LOCAL_CONSTRAINTS,
        "ethical_authority": ethical,
        "math_shared_state_root_sha256": surfaces[
            "math_shared_state_root_sha256"
        ],
        "physics_projection_root_sha256": surfaces[
            "physics_projection_root_sha256"
        ],
        "fabric_shared_root_sha256": surfaces[
            "fabric_shared_root_sha256"
        ],
        "math_authority_closed": surfaces["math_authority_closed"],
        "physics_authority_closed": surfaces["physics_authority_closed"],
        "fabric_authority_closed": surfaces["fabric_authority_closed"],
        "ancestry_root_shared": surfaces["ancestry_root_shared"],
        "joint_authority_closed": joint_closed,
        "misaligned_state_canonical_transition": False,
        "unresolved_state_canonical_transition": False,
        "current_repository_alignment_logic_preserved": True,
        "current_repository_math_preserved": True,
        "current_repository_physics_preserved": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_learning_commit_authority": False,
        "model_weight_update_authority": False,
        "direct_canonical_persistence_authority": False,
        "host_float_arithmetic_used_by_i043": False,
        "probability_used_for_i043_admission": False,
    })


def require_lane5_alignment_physics_authority(
    refined: EthicalNarrativeEvaluationV2,
) -> Dict[str, Any]:
    witness = build_lane5_alignment_physics_authority_witness(refined)
    if witness.get("joint_authority_closed") is not True:
        raise Pass220I043AuthorityError(
            "joint alignment/math/physics authority did not close"
        )
    return witness


def lane5_alignment_physics_authority_self_test() -> Dict[str, Any]:
    action = ActionCandidate(
        action_id="PASS220-I043-SELF-TEST",
        intent="prove joint alignment/math/physics pre-admission closure",
        requested_scope=("self.test",),
        minimum_necessary_scope=("self.test",),
        granted_scope=("self.test",),
        reversible=True,
        authority_source_ids=("PASS220-I043",),
    )
    epistemic = EpistemicAdequacyTrace(
        observation_integrity=InvariantState.PASS,
        causal_attribution_integrity=InvariantState.PASS,
        action_relevance_sufficiency=InvariantState.PASS,
    )
    refined = evaluate_action_v2(
        action,
        all_pass_invariants(rationale="I043 self-test inherited PASS"),
        epistemic,
    )
    witness = require_lane5_alignment_physics_authority(refined)
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": True,
        "result": {
            "joint_authority_closed": witness["joint_authority_closed"],
            "alignment_authority_closed": witness["ethical_authority"][
                "alignment_authority_closed"
            ],
            "math_authority_closed": witness["math_authority_closed"],
            "physics_authority_closed": witness["physics_authority_closed"],
            "fabric_authority_closed": witness["fabric_authority_closed"],
            "ancestry_root_shared": witness["ancestry_root_shared"],
            "misaligned_state_canonical_transition": witness[
                "misaligned_state_canonical_transition"
            ],
            "current_repository_alignment_logic_preserved": witness[
                "current_repository_alignment_logic_preserved"
            ],
            "canonical_vm81_mutation_authority": witness[
                "canonical_vm81_mutation_authority"
            ],
        },
        "joint_authority_receipt_sha256": witness["receipt_sha256"],
    })


__all__ = [
    "SCHEMA",
    "VERSION",
    "PROFILE",
    "WITNESS_SCHEMA",
    "LOCAL_CONSTRAINTS",
    "Pass220I043AuthorityError",
    "build_lane5_alignment_physics_authority_witness",
    "require_lane5_alignment_physics_authority",
    "lane5_alignment_physics_authority_self_test",
]
