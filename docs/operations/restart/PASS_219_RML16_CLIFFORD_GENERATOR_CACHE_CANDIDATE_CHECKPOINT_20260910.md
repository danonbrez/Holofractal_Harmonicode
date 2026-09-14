# Pass 219 RML16 Clifford Generator Cache Candidate Restart Checkpoint — 2026-09-10

## Restart identity

- Canonical RML16 parent branch: `agent/pass219-recursive-manifold-learning-20260909`
- Parent RML16 profiler head: `3749a602b676cf6bcdf86c16eb8f12c5ee7a3565`
- RML16 child branch: `agent/pass219-rml16-cold-route-profile-20260910`
- Validated whole-route cache checkpoint: `5dd174448453aec5955d77ba836ac108341c6d3a`
- Cold-route workflow implementation: `ec522d8ad6bc2ab3ae16fe6186dfd5173327743f`
- Candidate benchmark implementation: `18da51091a56cc26b0186f3779361ed17384d749`
- Candidate workflow implementation/test head: `9894af4b225519f35e6ed484f7d52211a9d52250`

## Frozen RML16 cold-route result

Dedicated workflow:

- run: `34496709714`
- job: `102936894109`
- conclusion: success
- artifact: `10160136318`
- artifact ZIP SHA256: `370e283093b4afccae7c7a0fc4c574bafb28f16c417084d4eeee1d799d7509f2`

The 16-state cold profile deliberately changed source identity while preserving the route shape so the exact-request RML16 route cache could not hit by construction.

Median ranking:

| Surface | Median ns | Samples |
|---|---:|---:|
| RML12 full shortest + complementary bundle | 214,692,847 | 16 |
| RML12 shortest plan | 111,583,064 | 16 |
| RML12 coupled edge | 26,986,667 | 64 |
| RML11 Clifford classifier | 21,523,743 | 64 |
| RML11 Clifford lift | 20,750,971 | 64 |
| RML7 Hopf classifier | 3,982,859 | 64 |
| RML5 reference path | 2,632,237 | 16 |
| RML12 reverse proof | 1,923,242 | 16 |
| S7 embedding | 853,843 | 64 |
| advance gyroscope | 482,426 | 64 |
| S4 Hopf projection only | 169,445 | 64 |

Derived integer diagnostics:

- RML11 Clifford classifier / RML12 edge: `7975 bp` (~79.75%).
- RML11 Clifford lift / RML12 edge: `7689 bp` (~76.89%).
- RML7 Hopf classifier / RML12 edge: `1475 bp`.
- advance gyroscope / RML12 edge: `178 bp`.

All cold-profile semantic-before-timing gates passed. The impacted production route regression set completed 36 tests successfully. Timing remains observational and non-canonical.

## Causal implementation finding

`hhs_runtime/pass219/phase_clifford_intertwiner.py` already memoizes invariant channel-action matrices and chirality, but its transport lift still invokes RML10 `build_cl08_generators()` for each lift. RML10 `build_cl08_generators()` rebuilds the exact eight-generator 16x16 tuple graph through exact Kronecker products on every call.

This matches the measured RML11 lift dominance and is the current RML16 optimization target.

## Candidate implementation

New candidate-only benchmark:

- `benchmarks/pass219/pass219_rml16_clifford_generator_cache_candidate.py`

New dedicated workflow:

- `.github/workflows/pass219-rml16-clifford-generator-cache-candidate.yml`

The candidate does **not** modify the RML10, RML11, or RML12 production source. It temporarily substitutes an `lru_cache(maxsize=1)` wrapper around the pure immutable RML10 generator constructor only inside the benchmark process.

Acceptance requires exact Python-object equality before timing acceptance for:

- 32 RML11 Clifford lifts;
- 32 RML11 Clifford classifications;
- 32 RML12 coupled edges;
- 8 RML12 shortest plans;
- 8 RML12 full reciprocal-route bundles.

The candidate also requires the cached generator result to be an immutable tuple graph exactly equal to an independently rebuilt uncached generator tuple.

## Candidate validation state

Dedicated workflow:

- workflow: `Pass 219 RML16 Clifford Generator Cache Candidate`
- run: `34497417758`
- job: `102939302172`
- tested head: `9894af4b225519f35e6ed484f7d52211a9d52250`

At checkpoint creation:

- checkout: success;
- Python setup: success;
- bounded dependency install: success;
- inherited RML15 native route validation: running;
- RML10/RML11/RML12 reference semantic tests: pending;
- candidate benchmark: pending;
- semantic identity gate: pending;
- impacted production route regression: pending;
- artifact upload: pending.

Do not accept or integrate the generator-cache optimization until this dedicated run produces a `PASS` candidate receipt.

## Authority invariants

Neither the profiler nor candidate may introduce:

- canonical VM81 mutation authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- floating-point canonical authority;
- scalar-projection substitution authority;
- timing authority.

No public RML10, RML11, or RML12 ABI change is authorized by this candidate benchmark.

## Exact next action

1. Resolve dedicated run `34497417758`, job `102939302172`.
2. Ignore unrelated legacy branch-wide failures unless they touch an RML16 dependency surface.
3. If the dedicated run fails, repair only its first causal RML16 failure.
4. If it passes, record the artifact ID/digest plus reference/candidate medians and exact equality counts.
5. Before integrating, search current repository validation for any frozen source-blob identity that protects `hhs_runtime/pass219/real_clifford_morita_witness.py` or `phase_clifford_intertwiner.py`.
6. If direct RML10 memoization would violate a frozen source identity, implement the optimization as an additive RML16 successor surface rather than rewriting frozen history.
7. If no frozen identity blocks it, integrate the smallest immutable one-entry generator cache, then run dependency-scoped RML10/RML11/RML12, route-cache, cold-profile, full hydration, and production-route semantic validation.
8. Accept latency gains only after exact semantic identity equality.
9. Commit and create the next repository-visible restart checkpoint before moving to another subsystem.
