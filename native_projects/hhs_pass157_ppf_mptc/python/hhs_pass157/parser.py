from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
import hashlib
import re
import unicodedata
from typing import Any

HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
MASK64 = (1 << 64) - 1


def _mix64(x: int) -> int:
    x &= MASK64
    x ^= x >> 33
    x = (x * 0xFF51AFD7ED558CCD) & MASK64
    x ^= x >> 33
    x = (x * 0xC4CEB9FE1A85EC53) & MASK64
    x ^= x >> 33
    return x & MASK64


def hash216(data: bytes) -> str:
    state = 0x179971179971
    for i, value in enumerate(data):
        state ^= value << ((i % 8) * 8)
        state = _mix64(state + i + 1)
    chars: list[str] = []
    for i in range(216):
        state = _mix64(state + 0x517CC1B727220A95 * (i + 1))
        chars.append(HASH72_ALPHABET[state % 72])
    return "".join(chars)


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    start: int
    end: int
    depth: int


@dataclass(frozen=True)
class ParseProduct:
    original_text: str
    normalized_unicode_view: str
    source_sha256: str
    source_hash216: str
    tokens: tuple[Token, ...]
    trivia: tuple[Token, ...]
    equality_lanes: tuple[str, ...]
    scope_edges: tuple[tuple[int, int, str], ...]
    boundary_carriers: tuple[str, ...]
    symbolic_radicals: tuple[str, ...]
    matrix_tensor_markers: tuple[str, ...]
    exact_numbers: tuple[str, ...]
    ambiguities: tuple[str, ...]
    diagnostics: tuple[str, ...]
    outcome: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["tokens"] = [asdict(token) for token in self.tokens]
        result["trivia"] = [asdict(token) for token in self.trivia]
        return result


_MULTI = ("==", "!=", "<=", ">=", "::", "->", "=>")
_SINGLE = set("+-*/^%=<>()[]{}:,;") | {"×", "·", "÷", "√", "≠", "≤", "≥", "∆", "Δ", "π"}
_OPEN = {"(": ")", "[": "]", "{": "}"}
_CLOSE = {value: key for key, value in _OPEN.items()}
_NUMBER = re.compile(r"(?:\d+/\d+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)")
_IDENT = re.compile(r"[A-Za-z_\u0370-\u03ff][A-Za-z0-9_\u0370-\u03ff]*")


def _exact_number(text: str) -> Fraction:
    if "/" in text and "e" not in text.lower() and "." not in text:
        numerator, denominator = text.split("/", 1)
        if int(denominator) == 0:
            raise ZeroDivisionError("zero denominator")
        return Fraction(int(numerator), int(denominator))
    if "e" in text.lower():
        mantissa, exponent_text = re.split("[eE]", text)
        exponent = int(exponent_text)
        base = _exact_number(mantissa)
        return base * (10 ** exponent) if exponent >= 0 else base / (10 ** (-exponent))
    if "." in text:
        whole, fractional = text.split(".", 1)
        sign = -1 if whole.startswith("-") else 1
        whole_abs = whole[1:] if whole.startswith("-") else whole
        numerator = int(whole_abs or "0") * (10 ** len(fractional)) + int(fractional or "0")
        return Fraction(sign * numerator, 10 ** len(fractional))
    return Fraction(int(text), 1)


def parse_source(source: str) -> ParseProduct:
    if not isinstance(source, str):
        raise TypeError("source must be str")
    raw = source.encode("utf-8")
    normalized = unicodedata.normalize("NFKC", source)
    tokens: list[Token] = []
    trivia: list[Token] = []
    diagnostics: list[str] = []
    ambiguities: list[str] = []
    exact_numbers: list[str] = []
    boundary: list[str] = []
    radicals: list[str] = []
    matrix_markers: list[str] = []
    scopes: list[tuple[int, int, str]] = []
    stack: list[tuple[str, int]] = []
    i = 0
    depth = 0
    while i < len(source):
        ch = source[i]
        if ch.isspace():
            start = i
            while i < len(source) and source[i].isspace():
                i += 1
            trivia.append(Token("TRIVIA", source[start:i], start, i, depth))
            continue
        if source.startswith("//", i) or source.startswith("#", i):
            start = i
            while i < len(source) and source[i] != "\n":
                i += 1
            trivia.append(Token("COMMENT", source[start:i], start, i, depth))
            continue
        matched = next((operator for operator in _MULTI if source.startswith(operator, i)), None)
        if matched:
            tokens.append(Token("RELATION" if matched in {"==", "!=", "<=", ">="} else "OPERATOR", matched, i, i + len(matched), depth))
            i += len(matched)
            continue
        number_match = _NUMBER.match(source, i)
        if number_match:
            text = number_match.group(0)
            try:
                value = _exact_number(text)
                exact_numbers.append(f"{value.numerator}/{value.denominator}")
                tokens.append(Token("NUMBER", text, i, number_match.end(), depth))
            except ZeroDivisionError:
                diagnostics.append(f"ZERO_DENOMINATOR@{i}")
                tokens.append(Token("INVALID_NUMBER", text, i, number_match.end(), depth))
            i = number_match.end()
            continue
        ident_match = _IDENT.match(source, i)
        if ident_match:
            text = ident_match.group(0)
            kind = "BOUNDARY_CARRIER" if text == "ComplexInfinity" else "IDENTIFIER"
            if kind == "BOUNDARY_CARRIER":
                boundary.append(text)
            tokens.append(Token(kind, text, i, ident_match.end(), depth))
            i = ident_match.end()
            continue
        if ch in _OPEN:
            if ch in {"[", "{"}:
                matrix_markers.append(ch)
            tokens.append(Token("OPEN", ch, i, i + 1, depth))
            stack.append((ch, i))
            depth += 1
            i += 1
            continue
        if ch in _CLOSE:
            depth = max(0, depth - 1)
            tokens.append(Token("CLOSE", ch, i, i + 1, depth))
            if not stack or stack[-1][0] != _CLOSE[ch]:
                diagnostics.append(f"UNMATCHED_CLOSE_{ch}@{i}")
            else:
                opening, start = stack.pop()
                scopes.append((start, i, opening + ch))
            i += 1
            continue
        if ch in _SINGLE:
            if ch == "√":
                radicals.append(ch)
            kind = "RELATION" if ch in {"=", "<", ">", "≠", "≤", "≥"} else "OPERATOR"
            tokens.append(Token(kind, ch, i, i + 1, depth))
            i += 1
            continue
        tokens.append(Token("UNRESOLVED", ch, i, i + 1, depth))
        diagnostics.append(f"UNRESOLVED_CODEPOINT_U+{ord(ch):04X}@{i}")
        i += 1
    for opening, start in stack:
        diagnostics.append(f"UNCLOSED_{opening}@{start}")

    significant = tokens
    for left, right in zip(significant, significant[1:]):
        if left.end == right.start and (
            left.kind in {"NUMBER", "IDENTIFIER", "BOUNDARY_CARRIER", "CLOSE"}
            and right.kind in {"IDENTIFIER", "BOUNDARY_CARRIER", "OPEN"}
        ):
            ambiguities.append(f"IMPLICIT_ADJACENCY:{left.text}|{right.text}@{left.end}")

    lanes: list[str] = []
    start = 0
    for token in significant:
        if token.depth == 0 and token.text in {"==", "="}:
            lanes.append(source[start:token.start].strip())
            start = token.end
    if lanes:
        lanes.append(source[start:].strip())
    else:
        lanes.append(source.strip())

    if any(token.kind == "UNRESOLVED" for token in tokens):
        outcome = "PARSE_PARTIAL"
    elif diagnostics:
        outcome = "PARSE_RECOVERED"
    elif ambiguities:
        outcome = "PARSE_VALID_WITH_AMBIGUITY"
    else:
        outcome = "PARSE_VALID"
    return ParseProduct(
        original_text=source,
        normalized_unicode_view=normalized,
        source_sha256=hashlib.sha256(raw).hexdigest(),
        source_hash216=hash216(raw),
        tokens=tuple(tokens),
        trivia=tuple(trivia),
        equality_lanes=tuple(lanes),
        scope_edges=tuple(sorted(scopes)),
        boundary_carriers=tuple(boundary),
        symbolic_radicals=tuple(radicals),
        matrix_tensor_markers=tuple(matrix_markers),
        exact_numbers=tuple(exact_numbers),
        ambiguities=tuple(ambiguities),
        diagnostics=tuple(diagnostics),
        outcome=outcome,
    )


def compile_membrane(source: str, mode: str = "COMPILE_ONLY") -> dict[str, Any]:
    allowed = {
        "SOLVE_TARGET_EXPLICIT",
        "SOLVE_TARGET_SET_EXPLICIT",
        "ENUMERATE_ADMISSIBLE_TARGETS",
        "COMPILE_ONLY",
        "CHECK_MEMBRANE",
        "PROJECT_REQUESTED_VALUE",
    }
    if mode not in allowed:
        raise ValueError("unsupported solve mode")
    parsed = parse_source(source)
    lane_hashes = [hash216(lane.encode("utf-8")) for lane in parsed.equality_lanes]
    payload = "|".join(lane_hashes + [mode, parsed.outcome]).encode("utf-8")
    typed_ast = [
        {"node": token.kind, "value": token.text, "depth": token.depth}
        for token in parsed.tokens
        if token.kind != "TRIVIA"
    ]
    return {
        "schema": "HHS_PASS_156_MEMBRANE_V1",
        "mode": mode,
        "parse": parsed.to_dict(),
        "typed_ast": typed_ast,
        "typed_ast_hash216": hash216(str(typed_ast).encode("utf-8")),
        "lane_count": len(parsed.equality_lanes),
        "lane_hash216": lane_hashes,
        "membrane_hash216": hash216(payload),
        "global_simultaneous_constraint": True,
        "arbitrary_solve_target": False,
        "symbols_distinct": {"O_ne_pi": True, "Delta_variants_preserved": True},
    }
