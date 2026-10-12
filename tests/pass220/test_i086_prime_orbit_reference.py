"""Dependency-scoped reference tests; native VM81 admission tested separately."""
from benchmarks.pass220.benchmark_i086_prime_orbit_reference import life, primes81, run

def test_prime_coordinates():
    primes = primes81()
    assert len(primes) == len(set(primes)) == 81
    assert primes[0] == 2 and primes[-1] == 419
    assert all(a < b for a, b in zip(primes, primes[1:]))

def test_dead_fixed_point():
    assert life(0) == 0

def test_toroidal_blinker_period_two():
    initial = sum(1 << (4 * 9 + c) for c in (3, 4, 5))
    next_state = life(initial)
    assert next_state != initial
    assert life(next_state) == initial

def test_bounded_recurrence_and_receipt():
    receipt = run(256)
    assert receipt["steps_executed"] > 0
    assert receipt["native_lane5_executed"] is False
    assert receipt["native_vm81_admitted"] is False
    assert len(receipt["state_sha256"]) == 64
