"""Pass 220: exact source-bound lowering of the four ordered 72-shell gates.

No host scalar equality is permitted to substitute for native HHS ==.
This parser never admits, commits, or fabricates a VM81/Hash72/Hash216 receipt.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from math import factorial
from typing import Tuple

SOURCE = "(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2"
SOURCE_SHA256 = "cd6309c3a6ad1d71a08258322b95df127e6aab7428904a5ff903449864859bb2"
SOURCE_GATE_OFFSETS = (74, 89, 92, 112)
ROOT_SEED = "179971.179971"
N = "1.001"
PHASE_EXPONENT = Fraction(2752680919, 10000000000)
INNER_GRAMMAR = (
    "x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)",
    "(x^2+1)^2/x^3",
    "b",
    "1/b^3",
)
OUTER_GRAMMAR = ("^2/(c^2-a^2)", "a^4/b^2")


class SourceBindingError(ValueError):
    """Invalid source or unsupported typed grammar: fail closed."""


@dataclass(frozen=True)
class TypedNode:
    kind: str
    source: str
    byte_start: int
    byte_end: int
    children: Tuple["TypedNode", ...] = ()


@dataclass(frozen=True)
class Lowering:
    source_sha256: str
    source_length: int
    gate_offsets: Tuple[int, ...]
    root: TypedNode
    rational_residue: Fraction
    rational_phase_exponent: Fraction
    native_proof_admitted: bool = False
    vm81_admitted: bool = False


def lower_exact_source(source: str) -> Lowering:
    if not isinstance(source, str):
        raise SourceBindingError("source must be text")
    data = source.encode("utf-8")
    digest = sha256(data).hexdigest()
    if digest != SOURCE_SHA256 or source != SOURCE or len(data) != 121:
        raise SourceBindingError("source identity mismatch")
    offsets = tuple(i for i in range(len(data) - 1) if data[i:i+2] == b"==")
    if offsets != SOURCE_GATE_OFFSETS:
        raise SourceBindingError("ordered equality gate offsets mismatch")
    # Offset 0 is the opening parenthesis, enclosing exactly the inner chain.
    close = source.index(")^2/(c^2-a^2)")
    if close != 99 or source[close + 1:] != OUTER_GRAMMAR[0] + "==" + OUTER_GRAMMAR[1]:
        raise SourceBindingError("outer typed square/division grammar mismatch")
    inner = source[1:close]
    operands = tuple(inner.split("=="))
    if operands != INNER_GRAMMAR:
        raise SourceBindingError("four native operands changed or reordered")
    cursor = 1
    nodes = []
    for i, item in enumerate(operands):
        if source[cursor:cursor + len(item)] != item:
            raise SourceBindingError("operand byte boundary mismatch")
        nodes.append(TypedNode("HHS_OPAQUE_OPERAND", item, cursor, cursor+len(item)))
        cursor += len(item)
        if i < 3:
            if source[cursor:cursor+2] != "==":
                raise SourceBindingError("inner gate mismatch")
            cursor += 2
    if cursor != close:
        raise SourceBindingError("inner boundary mismatch")
    chain = TypedNode("HHS_ORDERED_CHAIN_3_GATES", inner, 1, close, tuple(nodes))
    left = TypedNode("HHS_SQUARED_CHAIN_OVER_CANONICAL_DIFFERENCE",
                     source[:SOURCE_GATE_OFFSETS[-1]], 0, SOURCE_GATE_OFFSETS[-1],
                     (chain,))
    right_start = SOURCE_GATE_OFFSETS[-1] + 2
    right = TypedNode("HHS_CANONICAL_RIGHT_BOUNDARY",
                      source[right_start:], right_start, len(source))
    root = TypedNode("HHS_ORDERED_OUTER_EQUALITY",
                     source, 0, len(source), (left, right))
    f = factorial(72)
    residue = Fraction(pow(72, 72, f), f)
    if residue <= 0 or residue >= 1:
        raise SourceBindingError("72-shell residue outside admitted rational domain")
    return Lowering(digest, len(data), offsets, root, residue, PHASE_EXPONENT)


def admission_disposition(lowering: Lowering) -> str:
    # Structural lowering alone is never native proof or runtime admission.
    return "UNSUPPORTED_DOMAIN_NATIVE_PROOF_REQUIRED"
