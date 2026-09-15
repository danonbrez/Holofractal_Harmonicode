from __future__ import annotations

from copy import deepcopy
from fractions import Fraction


HASH72_RADIX = 72
VM81_CELLS = 81
LANE64 = 64
BLOCK5184 = HASH72_RADIX * HASH72_RADIX
LEVELS = 36
HASH72_MODULUS = HASH72_RADIX**HASH72_RADIX
GENESIS_K = 179_971_179_971
GENESIS_Q = 1_000_000
LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)


def split_5184(value: int, *, levels: int = LEVELS) -> tuple[int, ...]:
    assert 0 <= value < BLOCK5184**levels
    digits = []
    rest = value
    for _ in range(levels):
        rest, digit = divmod(rest, BLOCK5184)
        digits.append(digit)
    assert rest == 0
    return tuple(digits)


def join_5184(digits: tuple[int, ...]) -> int:
    value = 0
    for digit in reversed(digits):
        assert 0 <= digit < BLOCK5184
        value = value * BLOCK5184 + digit
    return value


def hash72_pair(local: int) -> tuple[int, int]:
    assert 0 <= local < BLOCK5184
    return divmod(local, HASH72_RADIX)


def vm81_lane(local: int) -> tuple[int, int]:
    assert 0 <= local < BLOCK5184
    return divmod(local, LANE64)


def pq_window(P: int) -> tuple[int, int, int]:
    return P - 1, P, P + 1


def loshu_gain(n: int) -> Fraction:
    assert 1 <= n <= 9
    return Fraction(n, 10 - n)


def mass_D(t: int, x: int, y: int) -> int:
    return -t * x * y + t**4 + t**3 - t**2


def mass_N_expanded(t: int, x: int, y: int) -> int:
    return (
        -8 * t * x * y**3
        + t**2 * x**2 * y**2
        + 8 * t**4 * y**2
        + 8 * t**3 * y**2
        - 8 * t**2 * y**2
        + 8 * t * x**3 * y
        - 2 * t**5 * x * y
        - 2 * t**4 * x * y
        + 2 * t**3 * x * y
        - 8 * t**4 * x**2
        - 8 * t**3 * x**2
        + 8 * t**2 * x**2
        + t**8
        + 2 * t**7
        - t**6
        - 2 * t**5
        + t**4
    )


def mass_N_factored(t: int, x: int, y: int) -> int:
    D = mass_D(t, x, y)
    A = x * x - y * y
    return D * (D - 8 * A)


def mul_i(value: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    real, imag = value
    return -imag, real


def mul_minus_i(value: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    real, imag = value
    return imag, -real


def make_claim(*, big_int: int, local: int, P: int, lo_shu_n: int, t: int, mx: int, my: int) -> dict[str, object]:
    p, _, q = pq_window(P)
    a72, b72 = hash72_pair(local)
    cell81, lane64 = vm81_lane(local)
    D = mass_D(t, mx, my)
    N = mass_N_factored(t, mx, my)
    return {
        "big_int": big_int,
        "digits": split_5184(big_int),
        "local": local,
        "hash72_pair": (a72, b72),
        "vm81_lane": (cell81, lane64),
        "P": P,
        "p": p,
        "q": q,
        "xy_plus_zw": 2,
        "u72_left": 1,
        "u72_right": 1,
        "lo_shu_n": lo_shu_n,
        "lo_shu_antipode": 10 - lo_shu_n,
        "lo_shu_gain": loshu_gain(lo_shu_n),
        "mass_t": t,
        "mass_x": mx,
        "mass_y": my,
        "mass_D": D,
        "mass_N": N,
    }


def validate_claim(claim: dict[str, object]) -> bool:
    try:
        big_int = int(claim["big_int"])
        local = int(claim["local"])
        P = int(claim["P"])
        p = int(claim["p"])
        q = int(claim["q"])
        lo_n = int(claim["lo_shu_n"])
        anti = int(claim["lo_shu_antipode"])
        t = int(claim["mass_t"])
        mx = int(claim["mass_x"])
        my = int(claim["mass_y"])

        if not 0 <= big_int < HASH72_MODULUS:
            return False
        digits = tuple(int(v) for v in claim["digits"])
        if len(digits) != LEVELS or join_5184(digits) != big_int:
            return False
        if digits[0] != local:
            return False

        if tuple(claim["hash72_pair"]) != hash72_pair(local):
            return False
        if tuple(claim["vm81_lane"]) != vm81_lane(local):
            return False

        if (p, P, q) != pq_window(P):
            return False
        if P * P - p * q != 1:
            return False
        if P == 0 or p + q == 0:
            return False
        left = int(claim["u72_left"]) * int(claim["u72_right"])
        middle = Fraction(int(claim["xy_plus_zw"]) * P, p + q)
        right = (P * P - p * q) ** 2
        if not left == middle == right:
            return False

        if anti != 10 - lo_n:
            return False
        gain = Fraction(claim["lo_shu_gain"])
        if gain != loshu_gain(lo_n):
            return False
        if gain * loshu_gain(anti) != 1:
            return False

        D = mass_D(t, mx, my)
        if int(claim["mass_D"]) != D:
            return False
        N = mass_N_expanded(t, mx, my)
        if N != mass_N_factored(t, mx, my):
            return False
        if int(claim["mass_N"]) != N:
            return False
    except (AssertionError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return False
    return True


def test_scaling_law_closes_hash72_modulus_into_5184_blocks() -> None:
    assert BLOCK5184 == 72**2 == 81 * 64
    assert HASH72_MODULUS == 72**72 == BLOCK5184**36
    assert HASH72_MODULUS // BLOCK5184 == 72**70


def test_bigint_5184_serialization_round_trips_at_boundaries_and_sparse_states() -> None:
    values = (
        0,
        1,
        71,
        72,
        5183,
        5184,
        5184**2 - 1,
        5184**17 + 72 * 31 + 7,
        HASH72_MODULUS - 2,
        HASH72_MODULUS - 1,
    )
    for value in values:
        digits = split_5184(value)
        assert len(digits) == 36
        assert join_5184(digits) == value
        for digit in digits:
            a72, b72 = hash72_pair(digit)
            c81, lane64 = vm81_lane(digit)
            assert 72 * a72 + b72 == digit
            assert 64 * c81 + lane64 == digit
            assert 0 <= a72 < 72 and 0 <= b72 < 72
            assert 0 <= c81 < 81 and 0 <= lane64 < 64


def test_all_5184_local_states_have_bijective_dual_coordinate_reads() -> None:
    seen72 = set()
    seen8164 = set()
    for local in range(BLOCK5184):
        seen72.add(hash72_pair(local))
        seen8164.add(vm81_lane(local))
    assert len(seen72) == BLOCK5184
    assert len(seen8164) == BLOCK5184
    assert len({a for a, _ in seen72}) == 72
    assert len({b for _, b in seen72}) == 72
    assert len({c for c, _ in seen8164}) == 81
    assert len({lane for _, lane in seen8164}) == 64


def test_p_pq_sliding_windows_overlap_and_preserve_unit_closure() -> None:
    for P in tuple(range(-32, 0)) + tuple(range(1, 33)):
        p, center, q = pq_window(P)
        assert center == P
        assert p + q == 2 * P
        assert p * q == P * P - 1
        assert P * P - p * q == 1
        assert pq_window(P)[1:] == pq_window(P + 1)[:2]


def test_fractal_qudit_constructor_three_way_equality_on_unit_branch() -> None:
    for P in (-97, -17, -2, -1, 1, 2, 17, 97):
        p, _, q = pq_window(P)
        # x=y=z=w=1 -> xy+zw=2.  u_L^72=u_R^72=1.
        left = 1 * 1
        middle = Fraction(2 * P, p + q)
        right = (P * P - p * q) ** 2
        assert left == middle == right == 1


def test_constructor_mutations_are_detected_as_self_description_mismatch() -> None:
    P = 13
    p, _, q = pq_window(P)
    assert Fraction(2 * P, p + q) == (P * P - p * q) ** 2 == 1
    assert Fraction(3 * P, p + q) != 1
    assert (P * P - p * (q + 1)) ** 2 != 1


def test_loshu_1_to_9_reciprocal_quantization_is_exact_and_zero_drift() -> None:
    assert set(LO_SHU) == set(range(1, 10))
    product = Fraction(1, 1)
    for n in range(1, 10):
        g = loshu_gain(n)
        product *= g
        assert g * loshu_gain(10 - n) == 1
        orientation = (n > 5) - (n < 5)
        assert orientation in (-1, 0, 1)
    assert loshu_gain(5) == 1
    assert product == 1


def test_mass_degree8_surface_equals_factored_anisotropy_constructor() -> None:
    for t in range(-4, 5):
        for x in range(-3, 4):
            for y in range(-3, 4):
                assert mass_N_expanded(t, x, y) == mass_N_factored(t, x, y)


def test_mass_quadratic_witness_on_isotropic_real_branches() -> None:
    t, x, y = 2, 1, 1
    D = mass_D(t, x, y)
    N = mass_N_factored(t, x, y)
    assert D == 18
    assert N == D * D
    for m in (Fraction(0, 1), Fraction(1, 1)):
        assert D * (m * m - m) == 2 * (y * y - x * x) == 0
        assert (2 * m - 1) ** 2 == Fraction(N, D * D)


def test_phase_lock_constant_and_i_direction_are_exact_reciprocals() -> None:
    assert GENESIS_K == 179_971 * 1_000_001
    assert GENESIS_K == 11 * 101 * 9_901 * 16_361
    assert GENESIS_Q == 2**6 * 5**6

    u = Fraction(3, 2)
    scalar = Fraction(GENESIS_K, GENESIS_Q) * u**73
    forward = mul_i((scalar, Fraction(0)))
    assert forward == (0, scalar)
    assert mul_minus_i(forward) == (scalar, 0)


def test_scope_bounded_claim_accepts_exact_state_and_rejects_each_lie() -> None:
    # local=73 is encoded into the low 5184 digit so every claimed projection can
    # be independently replayed from the same canonical BigInt state.
    claim = make_claim(
        big_int=5184**12 + 73,
        local=73,
        P=13,
        lo_shu_n=4,
        t=2,
        mx=1,
        my=1,
    )
    assert validate_claim(claim)

    mutations = (
        ("local", 74),
        ("hash72_pair", (1, 0)),
        ("vm81_lane", (0, 0)),
        ("q", int(claim["q"]) + 1),
        ("xy_plus_zw", 3),
        ("lo_shu_antipode", 5),
        ("lo_shu_gain", Fraction(3, 2)),
        ("mass_D", int(claim["mass_D"]) + 1),
        ("mass_N", int(claim["mass_N"]) + 1),
    )
    for key, bad_value in mutations:
        tampered = deepcopy(claim)
        tampered[key] = bad_value
        assert not validate_claim(tampered), key


def test_out_of_scope_hash72_modulus_state_is_rejected() -> None:
    claim = make_claim(
        big_int=73,
        local=73,
        P=7,
        lo_shu_n=5,
        t=2,
        mx=1,
        my=1,
    )
    assert validate_claim(claim)
    claim["big_int"] = HASH72_MODULUS
    assert not validate_claim(claim)
