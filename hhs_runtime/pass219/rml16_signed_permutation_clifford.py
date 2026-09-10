"""Pass 219 RML16 exact signed-permutation acceleration for RML11 Clifford products.

RML11's validated Cl_(0,8) channel actions are exact signed-permutation matrices.
The same class is closed under the products used by the RML11 transport lift, so
RML16 can compose those matrices by exact row permutation/sign multiplication
instead of repeatedly executing the general dense 16x16 integer product.

This module is a repair-forward RML16 successor surface.  It does not rewrite
the historical RML11 source or alter any RML11/RML12 public callable signature.
Matrices outside the exact signed-permutation class are delegated to the frozen
dense RML11 product unchanged.

The descriptor cache is bounded, process-local, non-persistent, and carries no
VM81 mutation, Hash72 mint, Hash216 persistence, floating-point, scalar
projection, or timing authority.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from hhs_runtime.pass219 import phase_clifford_intertwiner as _clifford
from hhs_runtime.pass219.real_clifford_morita_witness import Matrix

PASS = 219
ITERATION = "RML16_SIGNED_PERMUTATION_CLIFFORD_ACCELERATION"
SCHEMA = "HHS_PASS219_RML16_SIGNED_PERMUTATION_CLIFFORD_ACCELERATION_V1"
DESCRIPTOR_CACHE_CAPACITY = 512
RML11_FROZEN_SOURCE_COMMIT = "773fe9d3a083b76fc30bfbdaf42f624e6757310d"

_DENSE_RML11_MATMUL = _clifford._matmul


@lru_cache(maxsize=DESCRIPTOR_CACHE_CAPACITY)
def _signed_permutation_descriptor(
    matrix: Matrix,
) -> tuple[tuple[int, int], ...] | None:
    """Return (column, sign) per row only for an exact signed permutation."""
    order = len(matrix)
    if order <= 0 or any(len(row) != order for row in matrix):
        return None

    descriptor: list[tuple[int, int]] = []
    used_columns: set[int] = set()
    for row in matrix:
        nonzero = [(column, value) for column, value in enumerate(row) if value != 0]
        if len(nonzero) != 1:
            return None
        column, value = nonzero[0]
        if value not in (-1, 1) or column in used_columns:
            return None
        used_columns.add(column)
        descriptor.append((column, value))

    if len(used_columns) != order:
        return None
    return tuple(descriptor)


def signed_permutation_clifford_matmul(left: Matrix, right: Matrix) -> Matrix:
    """Exact RML16 fast path with the frozen RML11 dense product as fallback."""
    if not left or not right or len(left[0]) != len(right):
        return _DENSE_RML11_MATMUL(left, right)

    rows = len(left)
    inner = len(right)
    cols = len(right[0])
    if any(len(row) != inner for row in left) or any(len(row) != cols for row in right):
        return _DENSE_RML11_MATMUL(left, right)

    if rows == inner == cols:
        left_descriptor = _signed_permutation_descriptor(left)
        right_descriptor = _signed_permutation_descriptor(right)
        if left_descriptor is not None and right_descriptor is not None:
            result: list[tuple[int, ...]] = []
            for left_column, left_sign in left_descriptor:
                right_column, right_sign = right_descriptor[left_column]
                value = left_sign * right_sign
                result.append(
                    tuple(value if column == right_column else 0 for column in range(cols))
                )
            return tuple(result)

    return _DENSE_RML11_MATMUL(left, right)


def install_rml16_signed_permutation_clifford_acceleration() -> dict[str, Any]:
    """Install the exact private-product successor idempotently for RML16 use."""
    already_installed = _clifford._matmul is signed_permutation_clifford_matmul
    if not already_installed:
        if _clifford._matmul is not _DENSE_RML11_MATMUL:
            raise RuntimeError("RML16_CLIFFORD_MATMUL_PREEXISTING_SUCCESSOR_CONFLICT")
        _clifford._matmul = signed_permutation_clifford_matmul

    return {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "installed": True,
        "already_installed": already_installed,
        "rml11_frozen_source_commit": RML11_FROZEN_SOURCE_COMMIT,
        "descriptor_cache_capacity": DESCRIPTOR_CACHE_CAPACITY,
        "dense_exact_fallback_preserved": True,
        "rml11_public_abi_changed": False,
        "rml12_public_abi_changed": False,
        "process_local": True,
        "persistent_cache": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "scalar_projection_substitution_authority": False,
        "timing_canonical_authority": False,
    }


def rml16_signed_permutation_clifford_info() -> dict[str, Any]:
    cache = _signed_permutation_descriptor.cache_info()
    return {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "installed": _clifford._matmul is signed_permutation_clifford_matmul,
        "rml11_frozen_source_commit": RML11_FROZEN_SOURCE_COMMIT,
        "descriptor_cache": {
            "hits": cache.hits,
            "misses": cache.misses,
            "maxsize": cache.maxsize,
            "currsize": cache.currsize,
        },
        "dense_exact_fallback_preserved": True,
        "rml11_public_abi_changed": False,
        "rml12_public_abi_changed": False,
        "process_local": True,
        "persistent_cache": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "scalar_projection_substitution_authority": False,
        "timing_canonical_authority": False,
    }


__all__ = [
    "DESCRIPTOR_CACHE_CAPACITY",
    "RML11_FROZEN_SOURCE_COMMIT",
    "SCHEMA",
    "install_rml16_signed_permutation_clifford_acceleration",
    "rml16_signed_permutation_clifford_info",
    "signed_permutation_clifford_matmul",
]
