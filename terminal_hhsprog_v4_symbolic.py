"""Exact symbolic parser compatibility surface required by terminal V5.

The parser is deliberately syntax-preserving: it classifies and hashes symbolic
forms but does not claim that an equality is numerically true merely because it
is well formed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re


SYMBOLIC_FORMAT = "TERMINAL_HHSPROG_V4_SYMBOLIC"
_FLOAT_LITERAL_RE = re.compile(r"(?<![A-Za-z0-9_])(?:\d+\.\d*|\d*\.\d+)(?![A-Za-z0-9_])")
_TOKEN_RE = re.compile(
    r"==|:=|<=|>=|!=|->|[A-Za-z_Α-ω][A-Za-z0-9_Α-ω]*|\d+/\d+|\d+|\S",
    re.UNICODE,
)


class HHSSymbolicParseError(ValueError):
    pass


def _balanced(source: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for char in source:
        if char in "([{":
            stack.append(char)
        elif char in ")]}":
            if not stack or stack.pop() != pairs[char]:
                return False
    return not stack


def _normalize(source: str) -> str:
    source = source.strip()
    source = re.sub(r"\s+", " ", source)
    source = re.sub(r"\s*(==|:=|<=|>=|!=|->)\s*", r"\1", source)
    source = re.sub(r"\s*,\s*", ",", source)
    return source


def _form(source: str) -> str:
    upper = source.upper()
    if ":=" in source:
        return "DEFINITION"
    if "==" in source:
        return "EQUALITY_CHAIN"
    if upper.startswith("LIST("):
        return "LIST"
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)", source, re.DOTALL):
        return "CALL"
    return "SYMBOLIC_EXPRESSION"


@dataclass(frozen=True)
class HHSSymbolicParserV1:
    authority: Any

    def parse(self, source: str) -> dict[str, Any]:
        if not isinstance(source, str):
            raise TypeError("symbolic source must be str")
        if not source.strip():
            raise HHSSymbolicParseError("symbolic source is empty")
        if "\x00" in source:
            raise HHSSymbolicParseError("symbolic source contains NUL")
        if not _balanced(source):
            raise HHSSymbolicParseError("unbalanced symbolic delimiters")

        normalized = _normalize(source)
        tokens = _TOKEN_RE.findall(normalized)
        structure = {
            "form": _form(normalized),
            "token_count": len(tokens),
            "tokens": tokens,
            "equality_count": normalized.count("=="),
            "definition_count": normalized.count(":="),
            "parentheses_balanced": True,
            "contains_float_literal": bool(_FLOAT_LITERAL_RE.search(normalized)),
            "truth_evaluated": False,
            "semantic_policy": "SYNTAX_PRESERVING_NO_IMPLICIT_TRUTH",
        }
        source_hash72 = self.authority.commit(
            {"format": SYMBOLIC_FORMAT, "source": source},
            domain="HHS_SYMBOLIC_SOURCE",
        )
        symbolic_hash72 = self.authority.commit(
            {"format": SYMBOLIC_FORMAT, "normalized_source": normalized, "structure": structure},
            domain="HHS_SYMBOLIC_FORM",
        )
        return {
            "format": SYMBOLIC_FORMAT,
            "source": source,
            "normalized_source": normalized,
            "source_hash72": source_hash72,
            "symbolic_hash72": symbolic_hash72,
            "structure": structure,
        }
