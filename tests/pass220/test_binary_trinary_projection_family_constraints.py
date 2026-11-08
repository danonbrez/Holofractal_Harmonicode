"""Pass 220 dependency-scoped multi-projection identity constraint witnesses.

This tests an exact, *declared integer-symmetric projection subdomain* of the
existing P/p/q/Delta/A/B identities, not a replacement for the global typed
HARMONICODE executor. In particular no arbitrary conversion from raw 648-byte
egress into Delta or 81 tensor cells is invented here.

Every branch retains its identity, premises, exact operands and individual
disposition. Aggregate admission requires *all* branch obligations. Different
accepted projections need not have identical scalar values.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3
from hhs_runtime.hhs_recursive_global_constraint_bundle_v1 import XY, YX, ZW, WZ


BRANCHES = (
    "P_GT_ONE", "ORDERED_SUCCESSOR_P_Q", "UNIT_DELTA",
    "P2_EQ_PQ_PLUS_DELTA", "A_EQ_P2", "B_EQ_P2", "AB_EQ_P4",
    "LO_SHU_ROWS", "LO_SHU_COLUMNS", "LO_SHU_DIAGONALS",
    "ORDERED_GENERATORS_DISTINCT",
)


@dataclass(frozen=True)
class ScalarMatrixProjection:
    P: int
    p: int
    q: int
    Delta: int
    A: int
    B: int

    def matrix(self) -> tuple[tuple[int, ...], ...]:
        """Ordered scalar witness chart, not native VM81 address replacement."""
        return (
            (self.p, self.P, self.q),
            (self.A, self.Delta, self.B),
            (self.p * self.q, self.P * self.P, self.A * self.B),
        )


def projection(P: int) -> ScalarMatrixProjection:
    if type(P) is not int or P <= 1:
        raise ValueError("P_GT_ONE")
    return ScalarMatrixProjection(P, P - 1, P + 1, 1, P * P, P * P)


def validate(value: ScalarMatrixProjection) -> dict[str, bool]:
    if not isinstance(value, ScalarMatrixProjection):
        raise TypeError("TYPED_PROJECTION_REQUIRED")
    if any(type(v) is not int for v in
           (value.P, value.p, value.q, value.Delta, value.A, value.B)):
        raise TypeError("EXACT_INTEGER_REQUIRED")
    P, p, q, d, A, B = (
        value.P, value.p, value.q, value.Delta, value.A, value.B
    )
    ls = LO_SHU_3X3
    return dict(zip(BRANCHES, (
        P > 1,
        p == P - 1 and q == P + 1,
        d == 1,
        P * P == p * q + d,
        A == P * P,
        B == P * P,
        A * B == P**4,
        all(sum(row) == 15 for row in ls),
        all(sum(ls[i][j] for i in range(3)) == 15 for j in range(3)),
        sum(ls[i][i] for i in range(3)) == 15
        and sum(ls[i][2 - i] for i in range(3)) == 15,
        XY != YX and ZW != WZ,
    )))


@pytest.mark.parametrize("P", [2, 3, 4, 9, 30, 72, 251])
def test_distinct_exact_scalar_matrices_share_constraint_geometry(P: int) -> None:
    witness = projection(P)
    conditions = validate(witness)
    assert tuple(conditions) == BRANCHES
    assert all(conditions.values()), conditions
    assert witness.matrix()[1] == (P * P, 1, P * P)
    assert witness.matrix()[2] == (P * P - 1, P * P, P**4)
    assert witness.Delta == 1


def test_many_distinct_projection_values_do_not_collapse_to_one_matrix() -> None:
    matrices = [projection(P).matrix() for P in (2, 3, 4, 9, 30, 72, 251)]
    assert len(matrices) == len(set(matrices))
    assert all(all(validate(projection(P)).values())
               for P in (2, 3, 4, 9, 30, 72, 251))


@pytest.mark.parametrize("field,replacement,broken", [
    ("p", 7, "ORDERED_SUCCESSOR_P_Q"),
    ("q", 11, "ORDERED_SUCCESSOR_P_Q"),
    ("Delta", 2, "UNIT_DELTA"),
    ("A", 80, "A_EQ_P2"),
    ("B", 82, "B_EQ_P2"),
])
def test_branch_violation_is_not_silently_normalized(
    field: str, replacement: int, broken: str
) -> None:
    from dataclasses import replace
    candidate = replace(projection(9), **{field: replacement})
    conditions = validate(candidate)
    assert conditions[broken] is False
    assert not all(conditions.values())
    assert tuple(conditions) == BRANCHES


def test_projection_has_no_undeclared_binary_ingress_or_scalar_coercion() -> None:
    with pytest.raises(TypeError, match="EXACT_INTEGER_REQUIRED"):
        validate(ScalarMatrixProjection(4, 3, 5, 1.0, 16, 16))
    with pytest.raises(ValueError, match="P_GT_ONE"):
        projection(1)
    with pytest.raises(ValueError, match="P_GT_ONE"):
        projection(0)
    with pytest.raises(ValueError, match="P_GT_ONE"):
        projection(-4)
    with pytest.raises(ValueError, match="P_GT_ONE"):
        projection(True)  # bool is not an integer projection constructor
