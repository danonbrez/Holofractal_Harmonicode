"""Exact, read-only ERS analog-qutrit netlist V2 projection witnesses.

Candidate-only: does not evaluate native equality gates, hydrate Lane 5, or
authorize VM81/Hash72/Hash216 mutation. Exact scalar projections are deliberately
separate from cell-resident ordered tensor roles.
"""
from fractions import Fraction

SCHEMA = "HHS_ANALOG_QUTRIT_TENSOR_NETLIST_V2"
CIRCUITS = (
    "CC1_GENESIS_CARRIER", "CC2_BC_TENSOR", "CC3_METRIC_AND_DELTA",
    "CC4_BILATERAL_DELTA_E", "CC5_POLYNOMIAL_BANK",
    "CC6_ORDERED_PHASE_QUOTIENT", "CC7_FOUR_BRANCH_ROOT_POWER",
    "CC8_PHASE_ROOT_MATRIX", "CC9_EULER_PYTHAGOREAN_CIRCUIT",
    "CC10_TERMINAL_ZERO_MODE",
)
STAGES = (
    "LOOP_01_CARRIER_PLL", "LOOP_02_3X3_TRANSCONDUCTANCE_CORE",
    "LOOP_03_PAYLOAD_AND_DELTA_E_NULL", "LOOP_04_11_CHANNEL_PISO_FILTER",
    "LOOP_05_72_PHASOR_LUT_AND_QUARTIC_BRIDGE",
    "LOOP_06_MASTER_TORUS_RESET",
)
# Descending-order sparse coefficients. Keep all eleven original source cells.
POLYNOMIAL_CELLS = (
    {2: 1, 1: -1, 0: -1},
    {3: 1, 1: -1, 0: -1},
    {4: 1, 3: -1, 0: -1},
    {5: 1, 4: -1, 3: -1, 2: -1, 0: -1},
    {3: 1, 2: -1, 0: -1},
    {6: 1, 5: -1, 4: -1, 2: 1, 0: -1},
    {5: 1, 3: -1, 2: -1, 1: -1, 0: -1},
    {7: 1, 6: -1, 5: -1, 2: 1, 0: -1},
    {6: 1, 5: -2, 4: 1, 2: -1, 0: -1},
    {5: 1, 4: -1, 2: -1, 0: -1},
    {8: 1, 7: -1, 6: -1, 2: 1, 0: -1},
)
F_EXPECTED = {8: 1, 5: -1, 4: -1, 3: -1, 2: -1, 1: -3, 0: -11}
G_EXPECTED = {8: 1, 5: -1, 4: -1, 3: -1, 2: -1, 1: -3}
X3 = ((0, 0, 1), (1, 0, 0), (0, 1, 0))
PI_COLLAPSE = ((1, 0, 0), (0, 0, 0), (0, 0, 0))


def sum_polynomials(cells=POLYNOMIAL_CELLS):
    result = {}
    for cell in cells:
        for degree, coefficient in cell.items():
            result[degree] = result.get(degree, 0) + coefficient
    return {degree: value for degree, value in result.items() if value}


def evaluate(poly, x):
    return sum(coefficient * x ** degree for degree, coefficient in poly.items())


def unit_orbit(P):
    """Scalar projection only; does not collapse cell-address or AB/BA identities."""
    p, q = P - 1, P + 1
    return {"p": p, "q": q, "pq": p * q, "Delta": P * P - p * q,
            "q_minus_p": q - p, "p_plus_q": p + q}


def unit_orbit_nonzero_guards(P):
    """Relevant scalar nonzero checks; native gate admission is external."""
    orbit = unit_orbit(P)
    return {"P": P != 0, "p": orbit["p"] != 0,
            "q": orbit["q"] != 0, "pq": orbit["pq"] != 0,
            "p_plus_q": orbit["p_plus_q"] != 0}


def branch_audit():
    n = Fraction(1001, 1000)
    a = n * n
    a_squared = a * a
    b_squared = Fraction(2)
    c_squared = a_squared + b_squared
    tail = (c_squared - a_squared) ** 2 / b_squared - 2 * a_squared
    return {"n": n, "a": a, "a_squared": a_squared,
            "b_squared": b_squared, "c_squared": c_squared,
            "pythagorean_tail": tail, "tail_closed": tail == 0}


def phase_root_address(k):
    """Exact C72 address, not a floating-point complex phase."""
    if not 0 <= k < 72:
        raise ValueError("phase address must be in [0,71]")
    return {"k": k, "chromatic": k % 12, "sector": k // 12,
            "u72": (72 * k) % 72, "u36": (36 * k) % 72,
            "reciprocal_u_minus_180": (-180 * k) % 72}


def primitive_phase_audit():
    root = phase_root_address(1)
    return {"u36_is_minus_one": root["u36"] == 36,
            "u_minus_180_is_one": root["reciprocal_u_minus_180"] == 0,
            "u_minus_180_equals_u_minus_36": (
                root["reciprocal_u_minus_180"] == (-36) % 72),
            "u36_is_one": root["u36"] == 0}


def matrix_multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))


def qutrit_projection_witness():
    return {"x3_cubed_identity":
            matrix_multiply(matrix_multiply(X3, X3), X3)
            == ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            "projector_idempotent":
            matrix_multiply(PI_COLLAPSE, PI_COLLAPSE) == PI_COLLAPSE}


def witness_packet():
    """Reproducible read-only exact probes; NEVER an admission receipt."""
    return {"schema": SCHEMA, "class": "candidate_scalar_projection",
            "closed_circuit_count": len(CIRCUITS), "analog_stage_count": len(STAGES),
            "polynomial_cell_count": len(POLYNOMIAL_CELLS),
            "polynomial_bank_exact": sum_polynomials() == F_EXPECTED,
            "F_equals_G_minus_11": all(
                F_EXPECTED.get(degree, 0) - G_EXPECTED.get(degree, 0)
                == (-11 if degree == 0 else 0)
                for degree in set(F_EXPECTED) | set(G_EXPECTED)),
            "current_grounding": branch_audit(), "primitive_phase": primitive_phase_audit(),
            "qutrit_projection": qutrit_projection_witness(),
            "vm81_admitted": False, "hash72_minted": False,
            "hash216_committed": False, "lane5_hydrated": False}
