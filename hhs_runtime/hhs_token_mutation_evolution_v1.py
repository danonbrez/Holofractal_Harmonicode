"""
HHS Token Mutation / Evolution Engine v1
=======================================

Adaptive candidate-generation layer for the HHS goal attractor stack.

This engine mutates token sequences, runs every candidate through the existing
Goal State / Attractor Engine, accepts only replay-valid improvements, and
records all accepted/rejected branches with Hash72 receipts.

No branch may bypass:

    embedding -> attention -> PhaseTransportVM gates -> ledger append -> replay

Mutation is deterministic and exact.  It does not use random sampling.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from hhs_runtime.hhs_goal_attractor_engine_v1 import (
    AttractorRunReceipt,
    AttractorStatus,
    GoalState,
    run_attractor,
)
from hhs_runtime.hhs_loshu_phase_embedding_v1 import HASH72_ALPHABET, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger


class MutationKind(str, Enum):
    APPEND = "APPEND"
    PREPEND = "PREPEND"
    REPLACE = "REPLACE"
    ROTATE_LEFT = "ROTATE_LEFT"
    ROTATE_RIGHT = "ROTATE_RIGHT"
    REVERSE = "REVERSE"
    HASH72_SUFFIX = "HASH72_SUFFIX"


class BranchStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class MutationCandidate:
    """One deterministic token mutation candidate."""

    parent_tokens: Tuple[str, ...]
    mutated_tokens: Tuple[str, ...]
    mutation_kind: MutationKind
    mutation_index: int
    mutation_payload: str
    candidate_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["mutation_kind"] = self.mutation_kind.value
        data["parent_tokens"] = list(self.parent_tokens)
        data["mutated_tokens"] = list(self.mutated_tokens)
        return data


@dataclass(frozen=True)
class EvolutionBranchReceipt:
    """Receipt for one evaluated mutation branch."""

    candidate: MutationCandidate
    attractor_receipt_hash72: str
    replay_valid: bool
    score: Fraction
    baseline_score: Fraction
    status: BranchStatus
    reason: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "candidate": self.candidate.to_dict(),
            "attractor_receipt_hash72": self.attractor_receipt_hash72,
            "replay_valid": self.replay_valid,
            "score": f"{self.score.numerator}/{self.score.denominator}",
            "baseline_score": f"{self.baseline_score.numerator}/{self.baseline_score.denominator}",
            "status": self.status.value,
            "reason": self.reason,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class EvolutionGenerationReceipt:
    """Receipt for one generation of deterministic candidate evolution."""

    generation_index: int
    parent_tokens: Tuple[str, ...]
    baseline_score: Fraction
    branches: List[EvolutionBranchReceipt]
    selected_tokens: Tuple[str, ...]
    selected_score: Fraction
    status: BranchStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "generation_index": self.generation_index,
            "parent_tokens": list(self.parent_tokens),
            "baseline_score": f"{self.baseline_score.numerator}/{self.baseline_score.denominator}",
            "branches": [branch.to_dict() for branch in self.branches],
            "selected_tokens": list(self.selected_tokens),
            "selected_score": f"{self.selected_score.numerator}/{self.selected_score.denominator}",
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class EvolutionRunReceipt:
    """Full token mutation/evolution run receipt."""

    module: str
    goal: GoalState
    initial_tokens: Tuple[str, ...]
    final_tokens: Tuple[str, ...]
    generations: List[EvolutionGenerationReceipt]
    ledger_commit_receipt: Dict[str, object]
    replay_receipt: Dict[str, object]
    status: BranchStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "module": self.module,
            "goal": self.goal.to_dict(),
            "initial_tokens": list(self.initial_tokens),
            "final_tokens": list(self.final_tokens),
            "generations": [generation.to_dict() for generation in self.generations],
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


def _candidate_hash(parent: Sequence[str], mutated: Sequence[str], kind: MutationKind, index: int, payload: str) -> str:
    return hash72_digest(("mutation_candidate_v1", tuple(parent), tuple(mutated), kind.value, index, payload))


def _hash72_seed_token(tokens: Sequence[str], generation: int, index: int) -> str:
    seed = hash72_digest(("hash72_seed_token", tuple(tokens), generation, index), width=6)
    return f"H72_{seed}"


def generate_candidates(tokens: Sequence[str], generation: int, max_candidates: int = 16) -> List[MutationCandidate]:
    """
    Deterministically generate candidate token sequences.

    The generator uses structural mutations only: append/prepend goal-like seeds,
    replacement, rotations, reversal, and Hash72 suffix construction.  No random
    sampling is used.
    """

    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive")
    parent = tuple(tokens)
    if not parent:
        parent = ("HHS",)

    candidates: List[MutationCandidate] = []

    def add(kind: MutationKind, mutated: Sequence[str], index: int, payload: str) -> None:
        if len(candidates) >= max_candidates:
            return
        mutated_tuple = tuple(mutated)
        c_hash = _candidate_hash(parent, mutated_tuple, kind, index, payload)
        candidates.append(MutationCandidate(parent, mutated_tuple, kind, index, payload, c_hash))

    seed_tokens = [
        "Hash72",
        "LoShu",
        "xyzw",
        "u72",
        "Attractor",
        _hash72_seed_token(parent, generation, 0),
    ]

    for idx, token in enumerate(seed_tokens):
        add(MutationKind.APPEND, parent + (token,), idx, token)
        add(MutationKind.PREPEND, (token,) + parent, idx, token)

    for idx, token in enumerate(seed_tokens[:4]):
        replace_index = idx % len(parent)
        mutated = list(parent)
        mutated[replace_index] = token
        add(MutationKind.REPLACE, mutated, replace_index, token)

    if len(parent) > 1:
        add(MutationKind.ROTATE_LEFT, parent[1:] + parent[:1], 0, "rotL")
        add(MutationKind.ROTATE_RIGHT, parent[-1:] + parent[:-1], 0, "rotR")
        add(MutationKind.REVERSE, tuple(reversed(parent)), 0, "reverse")

    suffix = _hash72_seed_token(parent, generation, 1)
    add(MutationKind.HASH72_SUFFIX, parent + (suffix,), len(parent), suffix)
    return candidates[:max_candidates]


def _best_step_score(attractor: AttractorRunReceipt) -> Fraction:
    best = Fraction(0, 1)
    for step in attractor.steps:
        if step.selected_score and step.selected_score.total_score > best:
            best = step.selected_score.total_score
    return best


def _attractor_replay_valid(attractor: AttractorRunReceipt) -> bool:
    replay = attractor.replay_receipt
    return replay.get("invalid") == 0


def evaluate_candidate(
    candidate: MutationCandidate,
    goal: GoalState,
    baseline_score: Fraction,
    d_model: int,
    dimensions: int,
    top_k: int,
    max_steps: int,
    ledger_path: str | Path,
) -> EvolutionBranchReceipt:
    """Run one mutation candidate through the full attractor stack."""

    candidate_ledger = Path(str(ledger_path) + f".{candidate.candidate_hash72}.json")
    if candidate_ledger.exists():
        candidate_ledger.unlink()

    attractor = run_attractor(
        candidate.mutated_tokens,
        goal=goal,
        d_model=d_model,
        dimensions=dimensions,
        top_k=top_k,
        max_steps=max_steps,
        ledger_path=candidate_ledger,
    )
    score = _best_step_score(attractor)
    replay_valid = _attractor_replay_valid(attractor)

    if not replay_valid or attractor.status == AttractorStatus.QUARANTINED:
        status = BranchStatus.QUARANTINED
        reason = "candidate_failed_replay_or_quarantined"
    elif score > baseline_score:
        status = BranchStatus.ACCEPTED
        reason = "candidate_improved_goal_score"
    else:
        status = BranchStatus.REJECTED
        reason = "candidate_did_not_improve_goal_score"

    receipt = hash72_digest(
        (
            "evolution_branch_v1",
            candidate.to_dict(),
            attractor.receipt_hash72,
            replay_valid,
            score,
            baseline_score,
            status.value,
            reason,
        )
    )
    return EvolutionBranchReceipt(
        candidate=candidate,
        attractor_receipt_hash72=attractor.receipt_hash72,
        replay_valid=replay_valid,
        score=score,
        baseline_score=baseline_score,
        status=status,
        reason=reason,
        receipt_hash72=receipt,
    )


def evolve_generation(
    tokens: Sequence[str],
    goal: GoalState,
    generation_index: int,
    d_model: int = 72,
    dimensions: int = 4,
    top_k: int = 2,
    max_steps: int = 2,
    max_candidates: int = 12,
    ledger_path: str | Path = "demo_reports/hhs_token_evolution_v1.json",
) -> EvolutionGenerationReceipt:
    """Run one deterministic mutation/evaluation/selection generation."""

    baseline_ledger = Path(str(ledger_path) + f".baseline.{generation_index}.json")
    if baseline_ledger.exists():
        baseline_ledger.unlink()
    baseline_attractor = run_attractor(
        tokens,
        goal=goal,
        d_model=d_model,
        dimensions=dimensions,
        top_k=top_k,
        max_steps=max_steps,
        ledger_path=baseline_ledger,
    )
    baseline_score = _best_step_score(baseline_attractor)

    candidates = generate_candidates(tokens, generation_index, max_candidates=max_candidates)
    branches = [
        evaluate_candidate(
            candidate,
            goal=goal,
            baseline_score=baseline_score,
            d_model=d_model,
            dimensions=dimensions,
            top_k=top_k,
            max_steps=max_steps,
            ledger_path=ledger_path,
        )
        for candidate in candidates
    ]

    accepted = [branch for branch in branches if branch.status == BranchStatus.ACCEPTED]
    if accepted:
        accepted.sort(key=lambda branch: (branch.score, branch.receipt_hash72), reverse=True)
        selected = accepted[0]
        selected_tokens = selected.candidate.mutated_tokens
        selected_score = selected.score
        status = BranchStatus.ACCEPTED
    else:
        selected_tokens = tuple(tokens)
        selected_score = baseline_score
        status = BranchStatus.REJECTED

    receipt = hash72_digest(
        (
            "evolution_generation_v1",
            generation_index,
            tuple(tokens),
            baseline_score,
            [branch.receipt_hash72 for branch in branches],
            selected_tokens,
            selected_score,
            status.value,
        )
    )
    return EvolutionGenerationReceipt(
        generation_index=generation_index,
        parent_tokens=tuple(tokens),
        baseline_score=baseline_score,
        branches=branches,
        selected_tokens=selected_tokens,
        selected_score=selected_score,
        status=status,
        receipt_hash72=receipt,
    )


def run_evolution(
    tokens: Sequence[str],
    goal: GoalState,
    generations: int = 3,
    d_model: int = 72,
    dimensions: int = 4,
    top_k: int = 2,
    max_steps: int = 2,
    max_candidates: int = 12,
    ledger_path: str | Path = "demo_reports/hhs_token_evolution_v1.json",
) -> EvolutionRunReceipt:
    """Run deterministic token evolution toward a goal attractor."""

    if generations <= 0:
        raise ValueError("generations must be positive")

    path = Path(ledger_path)
    if path.exists():
        path.unlink()

    current = tuple(tokens) if tokens else ("HHS",)
    generation_receipts: List[EvolutionGenerationReceipt] = []
    final_status = BranchStatus.REJECTED

    for generation_index in range(generations):
        generation = evolve_generation(
            current,
            goal=goal,
            generation_index=generation_index,
            d_model=d_model,
            dimensions=dimensions,
            top_k=top_k,
            max_steps=max_steps,
            max_candidates=max_candidates,
            ledger_path=ledger_path,
        )
        generation_receipts.append(generation)
        final_status = generation.status
        current = generation.selected_tokens
        if generation.status != BranchStatus.ACCEPTED:
            break

    ledger = MemoryLedger(path)
    commit = ledger.append_payloads("token_evolution_generation_v1", [g.to_dict() for g in generation_receipts])
    replay = replay_ledger(path)
    run_hash = hash72_digest(
        (
            "token_evolution_run_v1",
            goal.to_dict(),
            tuple(tokens),
            current,
            [g.receipt_hash72 for g in generation_receipts],
            commit.receipt_hash72,
            replay.receipt_hash72,
            final_status.value,
        )
    )
    return EvolutionRunReceipt(
        module="hhs_token_mutation_evolution_v1",
        goal=goal,
        initial_tokens=tuple(tokens),
        final_tokens=current,
        generations=generation_receipts,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        status=final_status,
        receipt_hash72=run_hash,
    )


def demo() -> Dict[str, object]:
    goal = GoalState(
        name="Token evolution demo",
        target_token="Hash72",
        target_phase_index=36,
        target_lo_shu_cell=40,
        target_dna_prefix="x",
    )
    receipt = run_evolution(
        ["HHS", "LoShu"],
        goal=goal,
        generations=2,
        d_model=72,
        dimensions=3,
        top_k=2,
        max_steps=2,
        max_candidates=8,
        ledger_path="demo_reports/hhs_token_evolution_demo_v1.json",
    )
    return receipt.to_dict()


if __name__ == "__main__":
    import json

    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
