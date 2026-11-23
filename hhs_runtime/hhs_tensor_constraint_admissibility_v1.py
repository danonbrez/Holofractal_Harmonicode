"""General HHS tensor *eligibility routing* under inherited native constraints.

No reproof of HHS algebra. A fully verified, contradiction-free state with
exactly one fully resolved branch proceeds to the existing signed VM81 lane.
Unknown evidence is PENDING, not a mathematical contradiction or invalid state.

This pure classifier NEVER admits, persists, signs, or mints Hash72/Hash216.
Its constraint evidence MUST originate from the native authoritative registry;
caller-authored examples are suitable only for testing the routing policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping


class TensorEligibility(str, Enum):
    FORWARD_SIGNED_VM81 = "FORWARD_SIGNED_VM81"
    EVIDENCE_PENDING = "EVIDENCE_PENDING"
    CONTRADICTORY = "CONTRADICTORY"
    AMBIGUOUS_BRANCH = "AMBIGUOUS_BRANCH"
    INVALID_EVIDENCE = "INVALID_EVIDENCE"


@dataclass(frozen=True)
class TensorEligibilityRecord:
    classification: TensorEligibility
    required_constraints: tuple[str, ...]
    satisfied_constraints: tuple[str, ...]
    unresolved_constraints: tuple[str, ...]
    contradictory_constraints: tuple[str, ...]
    candidate_branches: tuple[str, ...] | None
    branches_exhaustively_resolved: bool
    eligible_for_inherited_signed_vm81: bool
    canonical_vm81_committed: bool = False
    canonical_hash72_hash216_minted: bool = False


def classify_tensor_state(
    *,
    required_constraints: Iterable[str],
    constraint_results: Mapping[str, bool | None],
    candidate_branches: Iterable[str] | None,
    branches_exhaustively_resolved: bool,
) -> TensorEligibilityRecord:
    """Logical admission rule; only the native runtime can authenticate inputs.

    True: enforced and satisfied; False: explicit native contradictory witness;
    None/missing: incomplete observation, not a contradiction.
    None branches: native branch solver not yet evaluated.
    Empty branches with complete enumeration: genuine empty admissible set.
    """
    required = tuple(required_constraints)
    branches = None if candidate_branches is None else tuple(candidate_branches)
    invalid = (
        not required or
        len(set(required)) != len(required) or
        any(not isinstance(x, str) or not x for x in required) or
        any(not isinstance(x, str) or not x for x in constraint_results) or
        any(type(v) not in (bool, type(None)) for v in constraint_results.values()) or
        any(x not in required for x in constraint_results) or
        type(branches_exhaustively_resolved) is not bool or
        (branches is not None and (
            any(not isinstance(x, str) or not x for x in branches) or
            len(set(branches)) != len(branches)
        ))
    )
    if invalid:
        return TensorEligibilityRecord(
            TensorEligibility.INVALID_EVIDENCE,
            required if all(isinstance(x, str) for x in required) else (),
            (), (), (), branches if not invalid else None,
            bool(branches_exhaustively_resolved), False,
        )
    satisfied = tuple(x for x in required if constraint_results.get(x) is True)
    contradictions = tuple(x for x in required if constraint_results.get(x) is False)
    pending = tuple(x for x in required if constraint_results.get(x) is not True and
                    constraint_results.get(x) is not False)
    if contradictions:
        state = TensorEligibility.CONTRADICTORY
    elif branches is not None and len(branches) > 1:
        state = TensorEligibility.AMBIGUOUS_BRANCH
    elif branches is not None and not branches and branches_exhaustively_resolved:
        state = TensorEligibility.CONTRADICTORY
    elif pending or not branches_exhaustively_resolved or branches is None or len(branches) != 1:
        state = TensorEligibility.EVIDENCE_PENDING
    else:
        state = TensorEligibility.FORWARD_SIGNED_VM81
    return TensorEligibilityRecord(
        classification=state,
        required_constraints=required,
        satisfied_constraints=satisfied,
        unresolved_constraints=pending,
        contradictory_constraints=contradictions,
        candidate_branches=branches,
        branches_exhaustively_resolved=branches_exhaustively_resolved,
        eligible_for_inherited_signed_vm81=state is TensorEligibility.FORWARD_SIGNED_VM81,
    )
