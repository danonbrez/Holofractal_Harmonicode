# Pass 219 RML16 Clifford Internal Profile Result — 2026-09-10

## Identity

- RML16 parent branch: `agent/pass219-recursive-manifold-learning-20260909`
- RML16 parent profiler head: `3749a602b676cf6bcdf86c16eb8f12c5ee7a3565`
- Active child branch: `agent/pass219-rml16-cold-route-profile-20260910`
- Internal profiler benchmark commit: `67d32d47bcb206ec0c5150141b7dacbe6a089ec8`
- Internal profiler workflow/tested head: `2860388b739bdfc1b26ecfbf27065a04016d4a93`
- Workflow run: `34497930227`
- Job: `102941035512`
- Conclusion: `success`
- Artifact ID: `10160612711`
- Artifact ZIP SHA256: `b4e5f0d72024e2127216740c8f6e4de5b1055888dbc6397087cb2a171eb9bd45`

## Validation

- Frozen RML10/RML11/RML12 reference semantics: 20 passed, 1 intentionally deselected expensive cross-tab.
- 32 profiled production lifts exactly equal their corresponding uninstrumented production lifts.
- Production source modified by profiler: false.
- Public RML10/RML11/RML12 ABI change: false.
- VM81 mutation authority: false.
- Hash72 mint authority: false.
- Hash216 persistence authority: false.
- Floating-point canonical authority: false.
- Scalar-projection substitution authority: false.
- Timing authority: false.

## Measured RML11 lift decomposition

Reference lift median: `26,495,978 ns`.
Profiled lift median: `26,843,784 ns`; profiler overhead remains observational.

Top exclusive helper costs across 32 lifts:

| Helper | Calls | Calls/lift | Exclusive ns total | Share |
|---|---:|---:|---:|---:|
| `_matmul` | 1,920 | 60 | 689,126,612 | 81.74% |
| `_canonical` | 352 | 11 | 97,533,456 | 11.56% |
| `build_cl08_generators` | 32 | 1 | 24,920,940 | 2.95% |
| `_identity` | 544 | 17 | 10,459,689 | 1.24% |
| `_require_state` | 32 | 1 | 7,244,175 | 0.85% |
| `_matrix_power_order4` exclusive | 512 | 16 | 2,865,565 | 0.33% |
| `_sha256` exclusive | 352 | 11 | 1,637,253 | 0.19% |
| `_matrix_hash` exclusive | 320 | 10 | 1,364,310 | 0.16% |

Median `_matmul` call: `355,019 ns`; p95: `369,727 ns`.

## Interpretation constrained to the measured surface

The cold residual is not primarily generator construction. The frozen RML11 algorithm performs 60 exact dense 16x16 matrix products per lift, and those products consume 81.74% of measured profiled time.

The matrices on the Cl(0,8) transport path are generated from exact Kronecker products of signed permutation 2x2 matrices. Identity, generators, their ordered products, powers, inverse factors, and chirality products remain in the exact signed-permutation class under multiplication. This makes a structure-preserving exact composition path a valid candidate to test; it does not authorize replacing the dense exact path for arbitrary matrices.

## Next candidate

Candidate benchmark:

- `benchmarks/pass219/pass219_rml16_signed_permutation_matmul_candidate.py`
- implementation commit: `860eb3c8865f59239164cc72c876060145f3c8aa`

Candidate workflow:

- `.github/workflows/pass219-rml16-signed-permutation-matmul-candidate.yml`
- workflow/test head: `519129682d0b514dfa0cf6db4bde6aa0ad868087`

The candidate:

1. detects exact square signed-permutation matrices;
2. represents each row by its unique nonzero column and sign;
3. composes those exact permutations/signs directly;
4. falls back to frozen dense `_matmul` for any matrix outside the class;
5. first proves 81 primitive action/identity products exactly equal the dense result;
6. then requires exact equality across 32 lifts, 32 classifiers, 32 RML12 edges, 8 shortest plans, and 8 full route bundles;
7. does not modify production RML10/RML11/RML12 source during the candidate run.

## Exact restart action

1. Resolve the dedicated signed-permutation candidate workflow for tested head `519129682d0b514dfa0cf6db4bde6aa0ad868087`.
2. If it fails semantic identity, reject the fast path and preserve dense multiplication.
3. If semantic identity passes but speed is weak, do not integrate; continue to `_canonical`/receipt profiling.
4. If semantic identity passes with a material RML11/RML12 latency reduction, record the artifact and benchmark ratios.
5. Check source-freeze assertions again before integration.
6. Integrate only as a repair-forward RML16 optimization surface consistent with frozen RML10/RML11 semantics; retain dense exact fallback for non-signed-permutation matrices.
7. Run dependency-scoped RML10-RML16 semantics, cold-route profile, route-cache profile, and full-hydration regression after integration.
8. Commit and checkpoint the resulting state before changing subsystem.
