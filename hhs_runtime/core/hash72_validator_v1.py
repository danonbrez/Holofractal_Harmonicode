"""Canonical Hash72 format and 72-phase-ring validation.

This module intentionally separates structural validation from digest
construction. The prior implementation tested ``sum(range(72)) % 72 == 0``;
that expression is permanently false because the sum is 2556. Closure is a
property of traversing the complete 72-phase ring, not of the arithmetic sum
of phase labels.
"""
from __future__ import annotations

PHASE_MOD = 72
HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
HASH72_SYMBOL_COUNT = 72


def u(k: int) -> int:
    if not isinstance(k, int):
        raise TypeError("phase index must be an integer")
    return k % PHASE_MOD


def validate_phase_ring() -> bool:
    return u(PHASE_MOD) == u(0)


def validate_full_population(symbols: object) -> bool:
    return (
        isinstance(symbols, str)
        and len(symbols) == HASH72_SYMBOL_COUNT
        and all(symbol in HASH72_ALPHABET for symbol in symbols)
    )


def validate_closure(symbols: object) -> bool:
    """Validate one exact, ordered traversal of the 72-position phase ring."""
    if not validate_full_population(symbols):
        return False
    phases = tuple(u(index) for index in range(HASH72_SYMBOL_COUNT + 1))
    return (
        phases[0] == phases[-1]
        and all(
            phases[index + 1] == u(phases[index] + 1)
            for index in range(HASH72_SYMBOL_COUNT)
        )
    )


def validate_hash72(symbols: object) -> bool:
    return (
        validate_phase_ring()
        and validate_full_population(symbols)
        and validate_closure(symbols)
    )
