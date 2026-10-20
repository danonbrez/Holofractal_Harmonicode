"""Exact bounded Module 29 traversal regression; no candidate mint."""
from pathlib import Path

from hhs_runtime.pass148.parser import tokenize

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "evidence/pass220/course_m29_siamese_torus_source_20261020.md"


def test_siamese_81_visit_and_72_plus_8_ledger():
    n = 9
    cells = [[0] * n for _ in range(n)]
    row, col = 0, 4
    visited = []
    regular, breaks = 0, []
    for k in range(1, 82):
        assert cells[row][col] == 0
        cells[row][col] = k
        visited.append((row, col))
        if k == 81:
            break
        nr, nc = (row - 1) % n, (col + 1) % n
        if cells[nr][nc] != 0:
            nr, nc = (row + 1) % n, col
            breaks.append(k)
        else:
            regular += 1
        row, col = nr, nc
    assert len(set(visited)) == 81
    assert sorted(v for line in cells for v in line) == list(range(1, 82))
    assert regular == 72
    assert breaks == list(range(9, 81, 9))
    assert all(sum(line) == 369 for line in cells)
    assert all(sum(cells[r][c] for r in range(9)) == 369 for c in range(9))
    assert sum(cells[i][i] for i in range(9)) == 369
    assert sum(cells[i][8-i] for i in range(9)) == 369


def test_module29_ordered_matrix_source_is_preserved():
    doc = SOURCE.read_text(encoding="utf-8")
    source = doc.split("## Source expression (verbatim)\n\n```\n", 1)[1].split("\n```", 1)[0]
    assert source.startswith("List(NcalcMatrixPower(")
    assert "(-1)),I^List(" in source
    assert "List(4,9,2),List(3,5,7),List(8,1,6)" in source
    tokens = tokenize(source)
    assert all(t.kind != "UNKNOWN" for t in tokens)
    assert "".join(source[t.start:t.end] for t in tokens if t.kind != "EOF") == source
