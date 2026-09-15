from __future__ import annotations

from fractions import Fraction


BLOCK5184 = 5184
VM81_CELLS = 81
LANE64 = 64
HASH72_RADIX = 72
HASH72_LEVELS = 36
HASH72_MODULUS = HASH72_RADIX**HASH72_RADIX

PHASE_SYMBOLS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz", "null")
CARRIER_FAMILIES = (
    ("x", "y"),
    ("z", "w"),
    ("xy", "yx"),
    ("zw", "wz"),
)
LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)

BINARY_NULL_POSITIVE = (0, 1)
BINARY_NULL_NEGATIVE = (0, -1)
BINARY_RECIPROCAL = (-1, 1)


def loshu_gain(n: int) -> Fraction:
    assert 1 <= n <= 9
    return Fraction(n, 10 - n)


def digit_at_depth(value: int, depth: int) -> int:
    assert value >= 0
    assert depth >= 0
    return (value // (BLOCK5184**depth)) % BLOCK5184


def decode_cell81(cell81: int) -> dict[str, object]:
    assert 0 <= cell81 < VM81_CELLS
    phase_slot, magnitude_slot = divmod(cell81, 9)
    symbol = PHASE_SYMBOLS[phase_slot]
    lo_shu_n = LO_SHU[magnitude_slot]
    result: dict[str, object] = {
        "cell81": cell81,
        "phase_slot": phase_slot,
        "symbol": symbol,
        "magnitude_slot": magnitude_slot,
        "lo_shu_n": lo_shu_n,
        "gain": loshu_gain(lo_shu_n),
        "active": phase_slot < 8,
    }
    if phase_slot < 8:
        family_index, orientation_bit = divmod(phase_slot, 2)
        result["carrier_family"] = CARRIER_FAMILIES[family_index]
        result["orientation_bit"] = orientation_bit
    else:
        result["carrier_family"] = None
        result["orientation_bit"] = None
    return result


def decode_local5184(local: int, *, depth: int) -> dict[str, object]:
    assert 0 <= local < BLOCK5184
    assert depth >= 0
    cell81, operation64 = divmod(local, LANE64)
    decoded = decode_cell81(cell81)
    decoded.update(
        {
            "depth": depth,
            "local5184": local,
            "operation64": operation64,
        }
    )
    return decoded


def decode_bigint(value: int, *, depth: int) -> dict[str, object]:
    return decode_local5184(digit_at_depth(value, depth), depth=depth)


def rotate_cw(matrix: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    size = len(matrix)
    return tuple(
        tuple(matrix[size - 1 - row][col] for row in range(size))
        for col in range(size)
    )


def negate(matrix: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(-value for value in row) for row in matrix)


def test_vm81_quantization_is_72_active_channels_plus_nine_null_channels() -> None:
    decoded = tuple(decode_cell81(cell) for cell in range(VM81_CELLS))
    active = tuple(item for item in decoded if item["active"])
    null = tuple(item for item in decoded if not item["active"])

    assert len(decoded) == 9 * 9 == 81
    assert len(active) == 8 * 9 == 72
    assert len(null) == 1 * 9 == 9
    assert {item["symbol"] for item in active} == set(PHASE_SYMBOLS[:-1])
    assert {item["symbol"] for item in null} == {"null"}
    assert {item["lo_shu_n"] for item in null} == set(range(1, 10))


def test_active_channels_factor_as_four_typed_binary_carriers_by_nine_magnitudes() -> None:
    keys = set()
    for cell81 in range(72):
        state = decode_cell81(cell81)
        assert state["carrier_family"] in CARRIER_FAMILIES
        assert state["orientation_bit"] in (0, 1)
        keys.add(
            (
                state["carrier_family"],
                state["orientation_bit"],
                state["lo_shu_n"],
            )
        )

    assert len(keys) == 4 * 2 * 9 == 72


def test_typed_binary_relations_compose_into_null_separated_trinary_groups() -> None:
    assert set(BINARY_NULL_POSITIVE) == {0, 1}
    assert set(BINARY_NULL_NEGATIVE) == {0, -1}
    assert set(BINARY_RECIPROCAL) == {-1, 1}
    assert set(BINARY_NULL_POSITIVE) | set(BINARY_NULL_NEGATIVE) == {-1, 0, 1}

    clockwise = (1, 0, -1)
    counterclockwise = (-1, 0, 1)
    assert clockwise[0:2] == (1, 0)
    assert clockwise[1:3] == (0, -1)
    assert counterclockwise[0:2] == (-1, 0)
    assert counterclockwise[1:3] == (0, 1)
    assert sum(clockwise) == sum(counterclockwise) == 0
    assert clockwise[::-1] == counterclockwise


def test_all_5184_states_have_collision_free_typed_quantization_and_control_keys() -> None:
    keys = set()
    active_count = 0
    null_count = 0
    for local in range(BLOCK5184):
        state = decode_local5184(local, depth=0)
        key = (
            state["phase_slot"],
            state["magnitude_slot"],
            state["operation64"],
        )
        assert key not in keys
        keys.add(key)
        if state["active"]:
            active_count += 1
        else:
            null_count += 1

    assert len(keys) == BLOCK5184 == 81 * 64 == 72 * 72
    assert active_count == 72 * 64
    assert null_count == 9 * 64


def test_bigint_location_and_depth_deterministically_recover_quantized_state() -> None:
    value = (
        17
        + 73 * BLOCK5184
        + 2625 * BLOCK5184**2
        + 5183 * BLOCK5184**17
        + 4097 * BLOCK5184**35
    )
    assert 0 <= value < HASH72_MODULUS

    expected_digits = {0: 17, 1: 73, 2: 2625, 17: 5183, 35: 4097}
    for depth in range(HASH72_LEVELS):
        state = decode_bigint(value, depth=depth)
        expected_local = expected_digits.get(depth, 0)
        assert state["local5184"] == expected_local
        assert state == decode_local5184(expected_local, depth=depth)
        assert 64 * int(state["cell81"]) + int(state["operation64"]) == expected_local


def test_same_local_digit_at_different_depths_has_same_local_type_but_distinct_position() -> None:
    local = 2625
    value = local * BLOCK5184**3 + local * BLOCK5184**29

    low = decode_bigint(value, depth=3)
    high = decode_bigint(value, depth=29)
    assert low["local5184"] == high["local5184"] == local
    assert low["phase_slot"] == high["phase_slot"]
    assert low["magnitude_slot"] == high["magnitude_slot"]
    assert low["operation64"] == high["operation64"]
    assert low["depth"] == 3
    assert high["depth"] == 29
    assert local * BLOCK5184**3 != local * BLOCK5184**29


def test_bigint_positional_decoder_extends_beyond_hash72_window_without_redefining_hash72() -> None:
    # The generic base-5184 location rule is arbitrary-depth BigInt arithmetic.
    # The 1.45 canonical Hash72 admission window remains exactly 36 digits.
    value = 71 * BLOCK5184**73 + 5183 * BLOCK5184**40 + 1
    assert value >= HASH72_MODULUS
    assert digit_at_depth(value, 0) == 1
    assert digit_at_depth(value, 40) == 5183
    assert digit_at_depth(value, 73) == 71
    assert digit_at_depth(value, 72) == 0


def test_loshu_rational_magnitude_gradient_is_exact_reciprocal_prime_exponent_data() -> None:
    gains = {n: loshu_gain(n) for n in range(1, 10)}
    assert gains == {
        1: Fraction(1, 9),
        2: Fraction(1, 4),
        3: Fraction(3, 7),
        4: Fraction(2, 3),
        5: Fraction(1, 1),
        6: Fraction(3, 2),
        7: Fraction(7, 3),
        8: Fraction(4, 1),
        9: Fraction(9, 1),
    }
    for n, gain in gains.items():
        assert gain * gains[10 - n] == 1

    def prime_support(value: int) -> set[int]:
        support = set()
        rest = value
        for prime in (2, 3, 7):
            while rest % prime == 0:
                support.add(prime)
                rest //= prime
        assert rest == 1
        return support

    for gain in gains.values():
        assert prime_support(gain.numerator) <= {2, 3, 7}
        assert prime_support(gain.denominator) <= {2, 3, 7}


def test_palindromic_null_kernel_reverses_phase_on_quarter_turn_and_closes_on_half_turn() -> None:
    kernel = (
        (1, 0, -1),
        (0, 0, 0),
        (-1, 0, 1),
    )
    quarter = rotate_cw(kernel)
    half = rotate_cw(quarter)

    assert quarter == negate(kernel)
    assert half == kernel
    assert tuple(reversed(tuple(reversed(row)) for row in kernel)) == kernel
    assert all(sum(row) == 0 for row in kernel)
    assert all(sum(kernel[row][col] for row in range(3)) == 0 for col in range(3))
