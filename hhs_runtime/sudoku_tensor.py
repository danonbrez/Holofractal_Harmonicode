"""Diagonal Sudoku, Lo Shu traversal, and exact factoradic topology encoding."""
from __future__ import annotations

from hashlib import shake_256
from math import factorial
from typing import Iterable, Sequence

from .hash72_checkpoint import validate_diagonal_sudoku_native, native_loshu_vm81_order

LOSHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)
LOSHU0 = tuple(v - 1 for v in LOSHU)
S9 = factorial(9)

BASE_DIAGONAL_SUDOKU = (
    (0,1,2,3,4,5,6,7,8),
    (3,4,5,6,7,8,0,1,2),
    (6,7,8,0,1,2,3,4,5),
    (8,2,4,1,3,0,7,5,6),
    (5,0,6,4,2,7,1,8,3),
    (7,3,1,5,8,6,4,2,0),
    (1,8,7,2,0,3,5,6,4),
    (2,6,0,7,5,4,8,3,1),
    (4,5,3,8,6,1,2,0,7),
)


def _shuffle9(seed: bytes, domain: str) -> list[int]:
    out = list(range(9))
    stream = shake_256(domain.encode("utf-8") + b"\x1f" + seed).digest(64)
    cursor = 0
    for i in range(8, 0, -1):
        j = int.from_bytes(stream[cursor:cursor+4], "big") % (i + 1)
        cursor += 4
        out[i], out[j] = out[j], out[i]
    return out


def _symmetry(grid: list[list[int]], selector: int) -> list[list[int]]:
    g = [row[:] for row in grid]
    for _ in range(selector % 4):
        g = [list(row) for row in zip(*g[::-1])]
    if selector >= 4:
        g = [row[::-1] for row in g]
    return g


def derive_diagonal_sudoku(seed: bytes, domain: str = "HHS-P133-SUDOKU-TOPOLOGY-V1") -> list[list[int]]:
    perm = _shuffle9(seed, domain + ":symbols")
    selector = shake_256(domain.encode() + b":symmetry:" + seed).digest(1)[0] % 8
    base = _symmetry([list(row) for row in BASE_DIAGONAL_SUDOKU], selector)
    grid = [[perm[v] for v in row] for row in base]
    validation = validate_sudoku(grid)
    if not validation["ok"]:
        raise RuntimeError(f"derived diagonal Sudoku failed closure: {validation}")
    return grid


def units(grid: Sequence[Sequence[int]]) -> dict[str, list[list[int]]]:
    rows = [list(row) for row in grid]
    cols = [[grid[r][c] for r in range(9)] for c in range(9)]
    blocks = [
        [grid[br*3+dr][bc*3+dc] for dr in range(3) for dc in range(3)]
        for br in range(3) for bc in range(3)
    ]
    diags = [[grid[i][i] for i in range(9)], [grid[i][8-i] for i in range(9)]]
    return {"rows": rows, "columns": cols, "blocks": blocks, "diagonals": diags}


def validate_sudoku(grid: Sequence[Sequence[int]]) -> dict[str, object]:
    shape_ok = len(grid) == 9 and all(len(row) == 9 for row in grid)
    if not shape_ok:
        return {"ok": False, "shape_ok": False, "native_ok": False}
    expected = set(range(9))
    us = units(grid)
    checks = {kind: [set(unit) == expected and len(unit) == 9 for unit in group] for kind, group in us.items()}
    native_ok = validate_diagonal_sudoku_native([list(row) for row in grid])
    return {
        "ok": native_ok and all(all(v) for v in checks.values()),
        "shape_ok": True,
        "native_ok": native_ok,
        "checks": checks,
    }


def rank_permutation(perm: Sequence[int]) -> int:
    if sorted(perm) != list(range(9)):
        raise ValueError("row is not a permutation of 0..8")
    available = list(range(9))
    rank = 0
    for i, value in enumerate(perm):
        idx = available.index(value)
        rank += idx * factorial(8 - i)
        available.pop(idx)
    return rank


def unrank_permutation(rank: int) -> list[int]:
    if not 0 <= rank < S9:
        raise ValueError("factoradic rank outside [0, 9!-1]")
    available = list(range(9))
    out: list[int] = []
    for i in range(9):
        f = factorial(8 - i)
        idx, rank = divmod(rank, f)
        out.append(available.pop(idx))
    return out


def pack_topology(grid: Sequence[Sequence[int]]) -> tuple[int, list[int]]:
    if not validate_sudoku(grid)["ok"]:
        raise ValueError("invalid diagonal Sudoku")
    ranks = [rank_permutation([grid[r][c] for c in LOSHU0]) for r in range(9)]
    packed = sum(ranks[LOSHU0[k]] * (S9 ** k) for k in range(9))
    if packed >= S9 ** 9:
        raise AssertionError("topology bound violated")
    return packed, ranks


def unpack_topology(packed: int) -> list[list[int]]:
    if not 0 <= packed < S9 ** 9:
        raise ValueError("packed topology outside bound")
    ranks = [0] * 9
    residue = packed
    for k in range(9):
        digit, residue = residue % S9, residue // S9
        ranks[LOSHU0[k]] = digit
    grid = [[0] * 9 for _ in range(9)]
    for r in range(9):
        traversal_row = unrank_permutation(ranks[r])
        for idx, c in enumerate(LOSHU0):
            grid[r][c] = traversal_row[idx]
    if not validate_sudoku(grid)["ok"]:
        raise ValueError("decoded topology fails Sudoku closure")
    return grid


def vm81_loshu_order() -> list[int]:
    py = [9*r+c for r in LOSHU0 for c in LOSHU0]
    native = native_loshu_vm81_order()
    if py != native:
        raise RuntimeError("native/Python Lo Shu VM81 order mismatch")
    return py
