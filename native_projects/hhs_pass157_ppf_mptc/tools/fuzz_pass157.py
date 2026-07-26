from __future__ import annotations

import json
import random
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project / "python"))

from hhs_pass157.model import construct_exact, phase_decompose, pythagorean  # noqa: E402
from hhs_pass157.parser import parse_source  # noqa: E402

rng = random.Random(157)
checks = 0
for _ in range(500):
    n = rng.randrange(-(10**80), 10**80)
    modulus = rng.randrange(1, 10**12)
    q, r = phase_decompose(n, modulus)
    assert q * modulus + r == n and 0 <= r < modulus
    checks += 1
for _ in range(200):
    m = rng.randrange(2, 10**6)
    n = rng.randrange(1, m)
    a, b, c = pythagorean(m, n)
    assert a * a + b * b == c * c
    checks += 1
samples = [
    "A=xy==P^2==yx=B",
    "x=√(5)+ComplexInfinity",
    "M=[[1,2],[3,4]]",
    "72P+3t==Mod(f/u,72)",
    "O!=π; Δ!=∆",
]
for _ in range(300):
    parsed = parse_source(rng.choice(samples))
    assert parsed.source_hash216 and parsed.original_text
    checks += 1
result = {"schema": "HHS_PASS_157_FUZZ_REPORT_V1", "seed": 157, "checks": checks, "status": "PASS"}
(project / "dist" / "fuzz-report.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
