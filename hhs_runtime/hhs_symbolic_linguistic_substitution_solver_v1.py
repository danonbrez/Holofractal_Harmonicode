"""
HHS Symbolic Linguistic Substitution Solver v1
==============================================

Extra solving layer for difficult or novel linguistic strings.

The solver does not replace grammar, WordNet, or the linguistic training loop.
It projects tokens into algebraic roles and proposes bounded substitutions:
- noun/pronoun/article -> STATE
- verb/auxiliary -> OPERATOR
- adjective/adverb -> MODIFIER
- preposition/conjunction -> RELATION
- unknown/novel -> NOVEL_SYMBOL

It then emits candidate rewrites and feedback records for the existing loop.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry, tokenize_words

ROLE_BY_POS = {
    "noun": "STATE",
    "pronoun": "STATE",
    "article": "STATE_BINDER",
    "determiner": "STATE_BINDER",
    "verb": "OPERATOR",
    "adjective": "MODIFIER",
    "adverb": "MODIFIER",
    "preposition": "RELATION",
    "conjunction": "RELATION",
}

ROLE_PHASE = {
    "STATE": 5,
    "STATE_BINDER": 9,
    "OPERATOR": 17,
    "MODIFIER": 29,
    "RELATION": 41,
    "NOVEL_SYMBOL": 57,
}


@dataclass(frozen=True)
class SymbolicSubstitutionToken:
    token: str
    role: str
    pos: List[str]
    phase_index: int
    substitution: str
    token_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SymbolicSubstitutionCandidate:
    candidate_text: str
    roles: List[str]
    projected_phases: List[int]
    score: int
    reason: str
    candidate_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SymbolicSubstitutionReceipt:
    source_text: str
    tokens: List[SymbolicSubstitutionToken]
    candidates: List[SymbolicSubstitutionCandidate]
    feedback_records: List[Dict[str, Any]]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_text": self.source_text,
            "tokens": [t.to_dict() for t in self.tokens],
            "candidates": [c.to_dict() for c in self.candidates],
            "feedback_records": self.feedback_records,
            "receipt_hash72": self.receipt_hash72,
        }


def _role_from_pos(pos: List[str]) -> str:
    for item in pos:
        role = ROLE_BY_POS.get(str(item).lower())
        if role:
            return role
    return "NOVEL_SYMBOL"


def _phase_for(token: str, role: str, index: int) -> int:
    base = ROLE_PHASE.get(role, 57)
    acc = sum(ord(c) for c in token)
    return (base + acc + index * 7) % 72


def _root_form(token: str) -> str:
    root = re.sub(r"[aeiouAEIOU]", "", token.lower())
    return root or token.lower()


def _substitution_for(token: str, role: str) -> str:
    root = _root_form(token)
    if role == "STATE":
        return f"STATE({root})"
    if role == "STATE_BINDER":
        return f"BIND({root})"
    if role == "OPERATOR":
        return f"OP({root})"
    if role == "MODIFIER":
        return f"MOD({root})"
    if role == "RELATION":
        return f"REL({root})"
    return f"NOVEL({root})"


def solve_symbolic_linguistic_substitutions(text: str, relation_db: Dict[str, WordRelationEntry] | None = None) -> SymbolicSubstitutionReceipt:
    words = tokenize_words(text)
    tokens: List[SymbolicSubstitutionToken] = []
    for idx, word in enumerate(words):
        entry = relation_db.get(word) if relation_db else None
        pos = entry.pos if entry else []
        role = _role_from_pos(pos)
        phase = _phase_for(word, role, idx)
        subst = _substitution_for(word, role)
        h = hash72_digest(("hhs_symbolic_substitution_token_v1", word, role, pos, phase, subst), width=18)
        tokens.append(SymbolicSubstitutionToken(word, role, pos, phase, subst, h))

    symbolic_text = " ".join(t.substitution for t in tokens)
    role_chain = "→".join(t.role for t in tokens)
    phases = [t.phase_index for t in tokens]
    unknown = sum(1 for t in tokens if t.role == "NOVEL_SYMBOL")
    operator_count = sum(1 for t in tokens if t.role == "OPERATOR")
    state_count = sum(1 for t in tokens if t.role in {"STATE", "STATE_BINDER"})
    base_score = 100 - unknown * 12
    if operator_count == 0 and len(tokens) > 2:
        base_score -= 15
    if state_count == 0 and len(tokens) > 1:
        base_score -= 10
    score = max(0, min(100, base_score))

    candidates: List[SymbolicSubstitutionCandidate] = []
    h1 = hash72_digest(("hhs_symbolic_substitution_candidate_v1", symbolic_text, role_chain, phases, score), width=24)
    candidates.append(SymbolicSubstitutionCandidate(symbolic_text, [t.role for t in tokens], phases, score, "direct_role_projection", h1))

    compressed = " ⊗ ".join([t.substitution for t in tokens if t.role != "STATE_BINDER"])
    h2 = hash72_digest(("hhs_symbolic_substitution_candidate_v1", compressed, role_chain, phases, score - 3), width=24)
    candidates.append(SymbolicSubstitutionCandidate(compressed, [t.role for t in tokens if t.role != "STATE_BINDER"], phases, max(0, score - 3), "binder_compressed_projection", h2))

    feedback_records = [
        {
            "summary_hash72": c.candidate_hash72,
            "phases": c.projected_phases,
            "carrier": "xy" if c.score >= 85 else "y" if c.score >= 65 else "yx",
            "status": "STAGED" if c.score >= 65 else "HELD",
            "score": c.score,
            "operator_kind": "SYMBOLIC_LINGUISTIC_SUBSTITUTION",
            "candidate_text": c.candidate_text,
            "reason": c.reason,
        }
        for c in candidates
    ]
    receipt_hash = hash72_digest(("hhs_symbolic_linguistic_substitution_receipt_v1", text, [t.to_dict() for t in tokens], [c.to_dict() for c in candidates], feedback_records), width=24)
    return SymbolicSubstitutionReceipt(text, tokens, candidates, feedback_records, receipt_hash)


def main() -> None:
    import json
    receipt = solve_symbolic_linguistic_substitutions("The symbolic system preserves valid meaning")
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
