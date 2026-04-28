"""
HHS Consonant-Only Phonemic Tokenizer v1
=======================================

Transforms text into consonant-root tokens (UPC-style skeleton) and produces
training packets that can be paired with audio phase transport data.

Rules
-----
- Lowercase normalization
- Strip vowels: a e i o u (optionally y as semi-vowel)
- Preserve consonant clusters as tokens
- Map each token to a stable id + Hash72
- Provide sequence suitable for LM training loop
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest

VOWELS = set("aeiou")


def _is_consonant(ch: str) -> bool:
    return ch.isalpha() and ch not in VOWELS


@dataclass(frozen=True)
class ConsonantToken:
    text: str
    root: str
    position: int
    token_hash72: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ConsonantSequence:
    original: str
    tokens: List[ConsonantToken]
    sequence_hash72: str

    def to_dict(self) -> Dict[str, any]:
        return {
            "original": self.original,
            "tokens": [t.to_dict() for t in self.tokens],
            "sequence_hash72": self.sequence_hash72,
        }


def consonant_skeleton(text: str) -> str:
    return "".join([c for c in text.lower() if _is_consonant(c)])


def tokenize_consonant_roots(text: str) -> ConsonantSequence:
    words = text.split()
    tokens: List[ConsonantToken] = []
    idx = 0
    for w in words:
        root = consonant_skeleton(w)
        if not root:
            continue
        h = hash72_digest(("hhs_consonant_token_v1", w, root, idx), width=16)
        tokens.append(ConsonantToken(text=w, root=root, position=idx, token_hash72=h))
        idx += 1
    seq_hash = hash72_digest(("hhs_consonant_sequence_v1", text, [t.to_dict() for t in tokens]), width=24)
    return ConsonantSequence(original=text, tokens=tokens, sequence_hash72=seq_hash)


def main() -> None:
    s = tokenize_consonant_roots("Harmonicode phase transport closure")
    import json
    print(json.dumps(s.to_dict(), indent=2))


if __name__ == "__main__":
    main()
