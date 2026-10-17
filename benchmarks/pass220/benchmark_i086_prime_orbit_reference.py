"""I086 exact reference benchmark: NOT a native Lane 5 throughput claim."""
from __future__ import annotations
import argparse
import hashlib
import json
import time

def primes81():
    out = []
    n = 2
    while len(out) < 81:
        if all(n % d for d in range(2, __import__('math').isqrt(n) + 1)):
            out.append(n)
        n += 1
    return tuple(out)

def life(state):
    result = 0
    for r in range(9):
        for c in range(9):
            i = r * 9 + c
            count = sum((state >> (((r+dr)%9)*9+(c+dc)%9)) & 1
                        for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                        if dr or dc)
            live = (state >> i) & 1
            if count == 3 or (live and count == 2):
                result |= 1 << i
    return result

def run(steps):
    prime = primes81()
    assert len(prime) == len(set(prime)) == 81
    state = sum(1 << i for i in (21, 22, 23, 32, 41))
    seen = {}
    start = time.perf_counter_ns()
    closure = None
    for t in range(steps):
        # State identity is exact 81-bit occupancy, not a digest alone.
        if state in seen:
            closure = {"preperiod": seen[state], "period": t - seen[state]}
            break
        seen[state] = t
        state = life(state)
    elapsed = time.perf_counter_ns() - start
    return {"schema": "I086_REFERENCE_ONLY", "steps_executed": len(seen),
            "elapsed_ns": elapsed, "closure": closure,
            "prime_first_last": [prime[0], prime[-1]],
            "state_sha256": hashlib.sha256(state.to_bytes(11, "big")).hexdigest(),
            "native_lane5_executed": False,
            "native_vm81_admitted": False,
            "native_hash216_verified": False,
            "gpu_benchmarked": False}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=256)
    args = p.parse_args()
    if args.steps < 1:
        p.error("--steps must be positive")
    print(json.dumps(run(args.steps), sort_keys=True))
