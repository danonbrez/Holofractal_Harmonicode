# HHS Pass 175 Pre-Contract Benchmark Report

## Scope

This benchmark evaluates a proposed **5,184-state noncommutative phase-gear
extension** using the repository's existing 8×8 octonion-DNA u72 table,
Pass 157 scalar closure `A=B=xy=yx=P²`, Pass 174 `64×81=5,184` phase/address
fabric, canonical Hash72 construction, three-lane Hash216 identity, and an
ordinary x86_64 egress workload.

It is executable pre-contract evidence. It is not yet a merged VM81 runtime
implementation and makes no physical quantum-computing claim.

## Measured result

| Test | Result |
|---|---:|
| Ordered u72 product cells | **64** |
| u72 closure cells (`phase 0` or `36`) | **32** |
| Phase distribution | **{0: 14, 18: 16, 36: 18, 54: 16}** |
| VM81 cells | **81** |
| Total extension states | **5,184** |
| Unique state IDs | **5,184** |
| Unique operation keys | **5,184** |
| Unique operation identities | **5,184** |
| Unique Hash216 index roots | **5,184** |
| Closed successor cycle | **PASS: 5,183 → 0** |
| `AB=P⁴` scalar-magnitude witnesses | **5,184 / 5,184 PASS** |
| Reciprocal `xy/yx` phase projection | **5,184 / 5,184 PASS** |
| Perturbed phase negative tests | **81 / 81 rejected** |
| `(x+y-z-w) mod 72` | **0** |
| Parenthesization identities preserved | **512 / 512 distinct** |
| Leading-zero source identity sensitivity | **PASS** |

## Hash216 cache benchmark

```text
Cold fill:       7.868741 s
Cold/state:      1,517,889.9 ns
Warm replay:     0.001210 s
Warm/state:      233.3 ns
Measured speedup:6505.22×
Mutated misses:  5,184 / 5,184
```

Roots:

```text
state_root = 3493b2f340db7931be54418e93a5c4e6d0ec5514eb8ccee83eb0be5a7a878882
cache_root = 40efa24d47d9da67686917a887bb25f7e16e53a3c83f89eaf12fb733c2147d56
egress_root = dfb1a249a58b48124683a3929ac7bb262d3ab71c607df6a4d621a28ee82a560b
```

## Native x86_64 benchmark

The generated C11/x86_64 benchmark performs the complete 5,184-state loop
20,000 times per run.

```text
Median throughput: 179,526,600 state transitions/second
Executable SHA-256: 461cb5947ad32cc2f3313c2d7ce41fc7d7dd6db4653228166615721f96bca1d3
```

## Algebraic interpretation tested

The extension preserves two simultaneous layers:

```text
A = xy = (magnitude P², ordered phase 0)
B = yx = (magnitude P², ordered phase 36)
```

The ordered lanes remain non-identical. Their reciprocal phase pairing projects
to scalar phase zero while their magnitudes produce:

```text
AB = P² × P² = P⁴
```

This reciprocal projection is a proposed Pass 175 rule. It must be implemented
as an explicit typed VM81 operation and must not be confused with ordinary
commutative multiplication or silent `xy=yx` substitution.

## Contract implications

The next pass must implement:

1. a permanent bijection between 81 VM81 cells, 64 ordered phase operations,
   and all 5,184 state identities;
2. an exact ordered phase-gear value type carrying magnitude, phase, source
   word, parenthesization, and Hash216 lineage;
3. explicit `A=xy`, `B=yx`, `AB=P⁴` reciprocal-pair projection;
4. one cold ingress–VM81–x86_64 egress traversal that admits 5,184 Hash216
   objects;
5. retrieval-first replay with stale-root, collision, mutation, and provenance
   rejection;
6. deterministic cycle closure `σ^5184(S₀)=S₀`;
7. native ABI/API/CLI/Visual-IDE surfaces and dependency-scoped evidence.
