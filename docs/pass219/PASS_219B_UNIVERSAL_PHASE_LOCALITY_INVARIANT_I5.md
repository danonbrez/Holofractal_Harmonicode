# Pass 219B I5 — Universal Phase-Locality Invariant

## Purpose

Pass 219B I5 promotes the experimentally validated phase-locality behavior into an exact repository invariant for every HHS execution path that already possesses an exact pre-expansion phase selector.

This is not a claim that every arbitrary HHS operation is phase-local. It is a universal rule over the subset of candidate, lookup, cache, hydration, and accelerator operations whose phase dimensions and selected origins are known exactly before realization.

## Exact law

For phase dimensions `l = 1..d`:

```text
q_l = potential phase cardinality of dimension l
s_l = exactly selected phase cardinality of dimension l
1 <= s_l <= q_l
Q = product(q_l)
M = product(s_l)
R = Q / M
```

`Q` is potential phase volume. `M` is realized phase volume. The exact pruning law is multiplicative across dimensions.

For repeated VM81 phase cardinality `q_l = 81`:

```text
Q = 81^d
M = product(s_l)
```

The invariant does not infer that runtime speedup must equal `R`. Timing is observational. The exact invariant is the realized-work bound and equality/identity discipline.

## Mandatory routing

When an exact selector exists before expansion:

```text
exact selector + M < Q
        -> LOCAL
        -> realize base_units * M
        -> preserve original dense identity
        -> require exact selected-output equality
        -> only then continue toward inherited authority
```

Dense realization is forbidden in that case unless an explicit audit/ablation route is requested.

When no exact selector exists:

```text
selector unavailable
        -> DENSE_REQUIRED
        -> realize base_units * Q
```

This preserves correctness and prevents the optimization from fabricating locality.

## Authority boundary

The phase-local invariant has zero authority to:

- mutate canonical VM81 state;
- emit or advance Hash72;
- persist canonical state;
- replace inherited exact admission;
- convert a candidate or cache hit into canonical truth.

Exact selected-output equality and original identity preservation are prerequisites before any phase-local result can be passed downstream to inherited authoritative transition logic.

## Stable original identity

Local selections may not renumber the dense identity namespace. The public exact ABI therefore exposes a generic mixed-radix identity function.

For the validated depth-2 benchmark:

```text
original_branch_id = ((origin1 * 81 + origin2) * 2 + family)
```

This repairs the specific Pass 208 preselection hazard discovered in I2, where local ordinal rebasing would otherwise change `branch_candidate_root216` identity.

## Exact ABI

Public surfaces:

- `hhs_exact_pass219b_phase_locality_plan`
- `hhs_exact_pass219b_phase_locality_verify_realization`
- `hhs_exact_pass219b_phase_locality_original_identity`

The current ABI supports up to nine dimensions with exact `uint64_t` products and fails closed on overflow. A future wider exact product representation must be additive and may not weaken the invariant.

## Physical hardware evidence

The frozen I4 hardware result is recorded at:

`artifacts/pass219b/PASS_219B_I4_FOLD7_HARDWARE_RESULT.json`

Device:

```text
Samsung Galaxy Z Fold7
SM-F966U
Snapdragon 8 Elite for Galaxy
Qualcomm / adreno-8xx WebGPU adapter
```

Measured depth-2 dense reference:

```text
Q = 6,561 phase combinations
13,122 branches
68,024,448 logical lane dispatches
GPU median = 11,534,336 ns
```

Measured phase-local cases:

```text
M=1      3,584 ns      3,218.286x observed speedup
M=3      7,168 ns      1,609.143x
M=9     17,664 ns        652.986x
M=27    49,152 ns        234.667x
M=81   143,872 ns         80.171x
M=729 1,282,048 ns         8.997x
M=6561 11,534,336 ns       1.000x
```

Every selected sample in the hardware run preserved exact selected equality and original branch identity.

At fixed `M=81`, factorizations `(1,81)`, `(3,27)`, `(9,9)`, `(27,3)`, `(81,1)` measured 143,872–144,384 ns, a 512 ns total spread. This supports the hardware hypothesis that realized phase volume dominates factorization depth for this kernel/device, but that performance statement remains observational rather than canonical.

## Universal invariant versus empirical scaling model

Exact repository invariant:

```text
Q = product(q_l)
M = product(s_l)
exact selectors available => realize no more than the exact local plan
stable identity required
exact selected equality required
zero new authority
```

Empirical hardware model:

```text
T(M) = a + b*M
S(M) = (Q + c) / (M + c), c = a/b
```

The latter is benchmark evidence only and must be recalibrated by hardware/kernel combination.

## Integration requirement

All future phase-aware HHS candidate, vector shortlist, cache, hydration, and GPU/accelerator paths must use the exact phase-locality planner or prove an equivalent invariant before realizing phase-expanded work. New public phase-expansion APIs that bypass stable identity, exact selection equality, or the no-authority boundary are non-conforming.
