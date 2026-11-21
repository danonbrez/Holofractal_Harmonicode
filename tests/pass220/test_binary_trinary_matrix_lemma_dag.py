"""Address-bound exact lemma DAG over Pass 220 scalar projection witness charts.

The graph is a test-only constraint witness subdomain. It does not assign
native VM81 tensor semantics to these scalar chart cells, nor convert raw
binary egress to Delta, nor promote symbolic registration to proof.
All calculations read the matrix addresses supplied by the candidate,
not a parallel constructor's parameters or a precomputed PASS flag.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

import pytest

from test_binary_trinary_projection_family_constraints import projection

Address = tuple[int, int]
Matrix = tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]


@dataclass(frozen=True)
class Lemma:
    name: str
    cells: tuple[Address, ...]
    parents: tuple[str, ...]


# Ordered parent edges must be acyclic, and all named cells remain
# externally visible even if a branch is invalidated.
LEMMAS = (
    Lemma("P_GT_ONE", ((0, 1),), ()),
    Lemma("SUCCESSOR", ((0, 0), (0, 1), (0, 2)), ("P_GT_ONE",)),
    Lemma("DELTA_UNIT", ((1, 1),), ()),
    Lemma("P_SQUARE_CELL", ((0, 1), (2, 1)), ("P_GT_ONE",)),
    Lemma("P2_PQ_DELTA", ((2, 1), (2, 0), (1, 1)),
          ("SUCCESSOR", "DELTA_UNIT", "P_SQUARE_CELL")),
    Lemma("A_EQUALS_P2", ((1, 0), (2, 1)), ("P_SQUARE_CELL",)),
    Lemma("B_EQUALS_P2", ((1, 2), (2, 1)), ("P_SQUARE_CELL",)),
    Lemma("AB_PRODUCT", ((1, 0), (1, 2), (2, 2)),
          ("A_EQUALS_P2", "B_EQUALS_P2")),
    Lemma("AB_EQUALS_P4", ((0, 1), (2, 2)),
          ("AB_PRODUCT", "P_SQUARE_CELL")),
)


def evaluate(matrix: Matrix) -> dict:
    if (
        not isinstance(matrix, tuple) or len(matrix) != 3
        or any(not isinstance(row, tuple) or len(row) != 3 for row in matrix)
        or any(type(value) is not int for row in matrix for value in row)
    ):
        raise TypeError("EXACT_3X3_SCALAR_MATRIX_REQUIRED")
    p, P, q = matrix[0]
    A, d, B = matrix[1]
    pq, P2, AB = matrix[2]
    conditions = {
        "P_GT_ONE": P > 1,
        "SUCCESSOR": p == P - 1 and q == P + 1,
        "DELTA_UNIT": d == 1,
        "P_SQUARE_CELL": P2 == P * P,
        "P2_PQ_DELTA": P2 == pq + d and pq == p * q,
        "A_EQUALS_P2": A == P2,
        "B_EQUALS_P2": B == P2,
        "AB_PRODUCT": AB == A * B,
        "AB_EQUALS_P4": AB == P**4,
    }
    witness = []
    already_seen: set[str] = set()
    for lemma in LEMMAS:
        assert all(parent in already_seen for parent in lemma.parents)
        values = tuple(matrix[r][c] for r, c in lemma.cells)
        local = conditions[lemma.name]
        parent_acceptance = all(
            row["accepted"] for row in witness if row["name"] in lemma.parents
        )
        witness.append({
            "name": lemma.name,
            "addresses": [[r, c] for r, c in lemma.cells],
            "values": list(values),
            "parents": list(lemma.parents),
            "local": local,
            "accepted": local and parent_acceptance,
        })
        already_seen.add(lemma.name)
    core = {
        "schema": "PASS220_SCALAR_MATRIX_LEMMA_DAG_WITNESS_V1",
        "matrix": [list(row) for row in matrix],
        "branches": witness,
        "all_accepted": all(node["accepted"] for node in witness),
        "full_global_typed_closure": False,
        "native_delta_reinjection": False,
    }
    core["witness_sha256"] = sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":"), allow_nan=False)
        .encode("utf-8")
    ).hexdigest()
    return core


@pytest.mark.parametrize("P", [2, 3, 4, 9, 30, 72, 251])
def test_distinct_matrices_share_complete_addressed_subdomain_dag(P: int) -> None:
    receipt = evaluate(projection(P).matrix())
    assert receipt["all_accepted"]
    assert len(receipt["branches"]) == len(LEMMAS)
    assert all(branch["local"] for branch in receipt["branches"])
    assert all(branch["accepted"] for branch in receipt["branches"])
    assert not receipt["full_global_typed_closure"]
    assert not receipt["native_delta_reinjection"]


@pytest.mark.parametrize("address,modifier,broken", [
    ((0, 0), 1, "SUCCESSOR"),
    ((0, 2), 1, "SUCCESSOR"),
    ((1, 1), 1, "DELTA_UNIT"),
    ((2, 0), 1, "P2_PQ_DELTA"),
    ((2, 1), 1, "P_SQUARE_CELL"),
    ((1, 0), 1, "A_EQUALS_P2"),
    ((1, 2), 1, "B_EQUALS_P2"),
    ((2, 2), 1, "AB_PRODUCT"),
])
def test_address_mutation_identifies_failed_branch_and_descendants(
    address: Address, modifier: int, broken: str
) -> None:
    candidate = [list(row) for row in projection(9).matrix()]
    r, c = address
    candidate[r][c] += modifier
    witness = evaluate(tuple(tuple(row) for row in candidate))
    assert not witness["all_accepted"]
    by_name = {node["name"]: node for node in witness["branches"]}
    assert by_name[broken]["local"] is False
    assert by_name[broken]["accepted"] is False
    for branch in witness["branches"]:
        if broken in branch["parents"]:
            assert branch["accepted"] is False
    assert witness["matrix"][r][c] == candidate[r][c]


def test_lemma_receipt_changes_for_matrix_change_without_erasing_provenance() -> None:
    first = evaluate(projection(4).matrix())
    second = evaluate(projection(9).matrix())
    assert first["witness_sha256"] != second["witness_sha256"]
    assert [x["name"] for x in first["branches"]] == [
        x["name"] for x in second["branches"]
    ]
    assert [x["addresses"] for x in first["branches"]] == [
        x["addresses"] for x in second["branches"]
    ]


def test_rejects_non_exact_and_incomplete_matrix() -> None:
    with pytest.raises(TypeError, match="EXACT_3X3"):
        evaluate(((1, 2, 3),))
    with pytest.raises(TypeError, match="EXACT_3X3"):
        evaluate(((1, 2, 3), (4, True, 6), (7, 8, 9)))
    with pytest.raises(TypeError, match="EXACT_3X3"):
        evaluate(((1, 2, 3), (4, 5, 6), (7, 8, 9.0)))
