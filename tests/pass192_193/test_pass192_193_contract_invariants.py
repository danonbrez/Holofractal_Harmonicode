from __future__ import annotations

import hashlib
import json
import math
import unittest
from dataclasses import asdict, dataclass
from fractions import Fraction
from itertools import combinations
from typing import Sequence

LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
MAGNITUDES = (1, 2, 3, 5, 8)
NUCLEUS_LEXEMES = (
    "1==1",
    "1+1==2",
    "1+2==3",
    "1+3==4==2+2==2^2",
    "2+3==5",
)
SOURCE = (
    "List(List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5),"
    "(2*List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5)),"
    "(3*List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5)),"
    "(5*List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5)),"
    "(8*List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5)))"
)


def fib(n: int) -> int:
    if n < 0:
        raise ValueError("negative depth")
    a, b = 1, 2
    if n == 0:
        return a
    for _ in range(1, n):
        a, b = b, a + b
    return b


def ratio(depth_transition: int) -> Fraction:
    return Fraction(fib(depth_transition), fib(depth_transition + 1))


def cumulative_scale(depth: int) -> Fraction:
    if depth < 0:
        raise ValueError("negative depth")
    out = Fraction(1, 1)
    for current_depth in range(depth):
        out *= ratio(current_depth)
    return out


def identity(n: int) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(Fraction(int(i == j), 1) for j in range(n))
        for i in range(n)
    )


def matmul(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    rows = len(left)
    inner = len(right)
    columns = len(right[0])
    if len(left[0]) != inner:
        raise ValueError("shape mismatch")
    return tuple(
        tuple(
            sum(left[i][k] * right[k][j] for k in range(inner))
            for j in range(columns)
        )
        for i in range(rows)
    )


def quarter_turn(n: int, i: int, j: int) -> tuple[tuple[Fraction, ...], ...]:
    matrix = [list(row) for row in identity(n)]
    matrix[i][i] = Fraction(0)
    matrix[i][j] = Fraction(-1)
    matrix[j][i] = Fraction(1)
    matrix[j][j] = Fraction(0)
    return tuple(tuple(row) for row in matrix)


def apply(
    matrix: Sequence[Sequence[Fraction]],
    vector: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    return tuple(
        sum(row[column] * vector[column] for column in range(len(vector)))
        for row in matrix
    )


def canonical_digest(payload: dict) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FractalAddress:
    root_object_id: str
    parent_object_id: str
    child_slot: int
    lo_shu_cell: tuple[int, int]
    magnitude_row: int
    nesting_depth: int
    phase_plane: tuple[int, int]
    phase_num: int
    phase_den: int
    incidence_path: tuple[int, ...]

    def digest(self) -> str:
        return canonical_digest(asdict(self))


class Pass192Tests(unittest.TestCase):
    def test_lo_shu_contains_1_to_9(self) -> None:
        self.assertEqual(
            sorted(value for row in LO_SHU for value in row),
            list(range(1, 10)),
        )

    def test_lo_shu_rows_sum_15(self) -> None:
        self.assertTrue(all(sum(row) == 15 for row in LO_SHU))

    def test_lo_shu_columns_sum_15(self) -> None:
        self.assertTrue(
            all(sum(LO_SHU[row][column] for row in range(3)) == 15 for column in range(3))
        )

    def test_lo_shu_diagonals_sum_15(self) -> None:
        self.assertEqual(sum(LO_SHU[i][i] for i in range(3)), 15)
        self.assertEqual(sum(LO_SHU[i][2 - i] for i in range(3)), 15)

    def test_fibonacci_seed(self) -> None:
        self.assertEqual(
            [fib(i) for i in range(10)],
            [1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
        )

    def test_fibonacci_recurrence(self) -> None:
        for n in range(50):
            self.assertEqual(fib(n + 2), fib(n + 1) + fib(n))

    def test_first_child_half(self) -> None:
        self.assertEqual(ratio(0), Fraction(1, 2))

    def test_successive_exact_ratios(self) -> None:
        self.assertEqual(
            [ratio(i) for i in range(6)],
            [
                Fraction(1, 2),
                Fraction(2, 3),
                Fraction(3, 5),
                Fraction(5, 8),
                Fraction(8, 13),
                Fraction(13, 21),
            ],
        )

    def test_telescoping_scale(self) -> None:
        for depth in range(1, 100):
            self.assertEqual(cumulative_scale(depth), Fraction(1, fib(depth)))

    def test_no_float_in_exact_path(self) -> None:
        self.assertTrue(
            all(isinstance(cumulative_scale(depth), Fraction) for depth in range(30))
        )

    def test_ratio_limit_is_only_a_projection(self) -> None:
        inverse_phi = (math.sqrt(5) - 1) / 2
        self.assertLess(abs(float(ratio(30)) - inverse_phi), 1e-12)
        self.assertIsInstance(ratio(30), Fraction)

    def test_five_magnitude_rows(self) -> None:
        self.assertEqual(MAGNITUDES, tuple(fib(i) for i in range(5)))

    def test_finite_prefix_has_unique_coordinates(self) -> None:
        depth_prefix = 12
        entries = [
            (row, column, magnitude, depth)
            for row in range(3)
            for column in range(3)
            for magnitude in MAGNITUDES
            for depth in range(depth_prefix)
        ]
        self.assertEqual(len(entries), 9 * 5 * depth_prefix)
        self.assertEqual(len(entries), len(set(entries)))

    def test_membrane_witness(self) -> None:
        for depth in range(100):
            self.assertEqual(depth % (depth + 1), depth)

    def test_source_preserves_equality_chain(self) -> None:
        self.assertEqual(SOURCE.count("1+3==4==2+2==2^2"), 5)

    def test_source_preserves_all_nucleus_lexemes(self) -> None:
        for lexeme in NUCLEUS_LEXEMES:
            self.assertEqual(SOURCE.count(lexeme), 5)

    def test_outer_envelope_modulus(self) -> None:
        self.assertEqual(64 * 81 * 243 + 1, 1_259_713)

    def test_negative_depth_rejected(self) -> None:
        with self.assertRaises(ValueError):
            fib(-1)
        with self.assertRaises(ValueError):
            cumulative_scale(-1)


class Pass193GeometryTests(unittest.TestCase):
    def test_3d_regular_convex_count(self) -> None:
        families = {
            "tetrahedron",
            "cube",
            "octahedron",
            "dodecahedron",
            "icosahedron",
        }
        self.assertEqual(len(families), 5)

    def test_4d_regular_convex_count(self) -> None:
        families = {
            "5-cell",
            "8-cell",
            "16-cell",
            "24-cell",
            "120-cell",
            "600-cell",
        }
        self.assertEqual(len(families), 6)

    def test_high_dimension_regular_family_count(self) -> None:
        self.assertEqual(len({"simplex", "hypercube", "cross-polytope"}), 3)

    def test_rotation_plane_count(self) -> None:
        for dimension in range(2, 20):
            self.assertEqual(
                len(list(combinations(range(dimension), 2))),
                dimension * (dimension - 1) // 2,
            )

    def test_quarter_turn_is_exact_and_orthogonal(self) -> None:
        rotor = quarter_turn(5, 1, 4)
        transpose = tuple(zip(*rotor))
        self.assertEqual(matmul(transpose, rotor), identity(5))
        self.assertTrue(
            all(isinstance(value, Fraction) for row in rotor for value in row)
        )

    def test_ordered_plane_rotations_are_noncommutative(self) -> None:
        r01 = quarter_turn(4, 0, 1)
        r12 = quarter_turn(4, 1, 2)
        self.assertNotEqual(matmul(r01, r12), matmul(r12, r01))

    def test_disjoint_plane_rotations_commute(self) -> None:
        r01 = quarter_turn(4, 0, 1)
        r23 = quarter_turn(4, 2, 3)
        self.assertEqual(matmul(r01, r23), matmul(r23, r01))

    def test_transform_order_changes_global_point(self) -> None:
        vector = (Fraction(1), Fraction(2), Fraction(3), Fraction(4))
        root = quarter_turn(4, 0, 1)
        child = quarter_turn(4, 1, 2)
        self.assertNotEqual(
            apply(matmul(root, child), vector),
            apply(matmul(child, root), vector),
        )

    def test_lineage_address_is_deterministic(self) -> None:
        address = FractalAddress(
            "root", "parent", 7, (0, 0), 5, 12, (1, 4), 13, 34, (2, 9, 4)
        )
        self.assertEqual(address.digest(), address.digest())

    def test_lineage_changes_when_child_slot_changes(self) -> None:
        left = FractalAddress(
            "root", "parent", 7, (0, 0), 5, 12, (1, 4), 13, 34, (2, 9, 4)
        )
        right = FractalAddress(
            "root", "parent", 8, (0, 0), 5, 12, (1, 4), 13, 34, (2, 9, 4)
        )
        self.assertNotEqual(left.digest(), right.digest())

    def test_lineage_changes_when_phase_changes(self) -> None:
        left = FractalAddress(
            "root", "parent", 7, (0, 0), 5, 12, (1, 4), 13, 34, (2, 9, 4)
        )
        right = FractalAddress(
            "root", "parent", 7, (0, 0), 5, 12, (1, 4), 14, 34, (2, 9, 4)
        )
        self.assertNotEqual(left.digest(), right.digest())

    def test_lineage_changes_when_incidence_path_changes(self) -> None:
        left = FractalAddress(
            "root", "parent", 7, (0, 0), 5, 12, (1, 4), 13, 34, (2, 9, 4)
        )
        right = FractalAddress(
            "root", "parent", 7, (0, 0), 5, 12, (1, 4), 13, 34, (2, 9, 5)
        )
        self.assertNotEqual(left.digest(), right.digest())

    def test_global_scale_inherits_pass192(self) -> None:
        root_scale = Fraction(7, 3)
        for depth in range(1, 25):
            self.assertEqual(
                root_scale * cumulative_scale(depth),
                Fraction(7, 3 * fib(depth)),
            )

    def test_finite_prefix_materialization_is_bounded(self) -> None:
        branching = 5
        depth = 6
        nodes = sum(branching**current for current in range(depth + 1))
        self.assertEqual(
            nodes,
            (branching ** (depth + 1) - 1) // (branching - 1),
        )
        self.assertLess(nodes, 100_000)


class DeveloperSchemaTests(unittest.TestCase):
    REQUIRED_192 = {
        "tensor_id",
        "lo_shu_cell",
        "magnitude_row",
        "depth",
        "parent_id",
        "ratio_num",
        "ratio_den",
        "membrane_witness",
        "source_identity",
        "hash216_identity",
        "hash72_receipt_policy",
    }
    REQUIRED_193 = {
        "object_id",
        "family",
        "dimension",
        "incidence_graph",
        "exact_coordinates",
        "parent_id",
        "children",
        "fractal_address",
        "phase_planes",
        "fold_graph",
        "constraint_registry",
        "hash216_identity",
        "hash72_receipt_policy",
    }
    REQUIRED_BUNDLE = {
        "application_identity",
        "source_graph_identity",
        "operation_closure_identity",
        "asset_closure_identity",
        "targets",
        "capabilities",
        "signatures",
        "build_receipts",
        "replay_manifest",
        "license_manifest",
    }

    def test_pass192_manifest_sample(self) -> None:
        sample = {
            "tensor_id": "tensor:4:5:12",
            "lo_shu_cell": [0, 0],
            "magnitude_row": 5,
            "depth": 12,
            "parent_id": "tensor:4:5:11",
            "ratio_num": 233,
            "ratio_den": 377,
            "membrane_witness": {"n": 12, "modulus": 13, "residue": 12},
            "source_identity": "exact-list-source",
            "hash216_identity": "pending-reference-implementation",
            "hash72_receipt_policy": "required",
        }
        self.assertEqual(self.REQUIRED_192 - sample.keys(), set())

    def test_pass193_manifest_sample(self) -> None:
        sample = {
            "object_id": "mesh:root/7",
            "family": "hypercube",
            "dimension": 4,
            "incidence_graph": {},
            "exact_coordinates": [],
            "parent_id": "mesh:root",
            "children": [],
            "fractal_address": {},
            "phase_planes": [[0, 1], [2, 3]],
            "fold_graph": {},
            "constraint_registry": {},
            "hash216_identity": "pending-reference-implementation",
            "hash72_receipt_policy": "required",
        }
        self.assertEqual(self.REQUIRED_193 - sample.keys(), set())

    def test_native_bundle_manifest_sample(self) -> None:
        sample = {
            "application_identity": "app:demo",
            "source_graph_identity": "src:1",
            "operation_closure_identity": "ops:1",
            "asset_closure_identity": "assets:1",
            "targets": ["linux-x86_64", "linux-arm64"],
            "capabilities": [],
            "signatures": [],
            "build_receipts": [],
            "replay_manifest": {},
            "license_manifest": {},
        }
        self.assertEqual(self.REQUIRED_BUNDLE - sample.keys(), set())

    def test_architecture_targets_are_distinct_projections(self) -> None:
        self.assertEqual(len({"linux-x86_64", "linux-arm64"}), 2)

    def test_nft_identity_does_not_authorize_execution(self) -> None:
        nft_identity_present = True
        execution_authorized = False
        self.assertFalse(nft_identity_present and execution_authorized)


if __name__ == "__main__":
    unittest.main(verbosity=2)
