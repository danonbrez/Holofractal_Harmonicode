# Pass 219 — Global VM81 Latency Policy 25/3 Benchmark Results

**Classification:** `GLOBAL_LATENCY_POLICY_PROMOTION_SUPPORTED`  
**Benchmark base:** `main @ e8ecb02cc2fc823d0ffb49fa2e6d765a2cc73191`  
**Benchmark head:** `1a0ab12b4c2e66969a8fb8176f3ee0b66a45fa27`  
**Workflow:** `33536893755`

## 1. Exact policy

The tested latency quantum is:

```text
a^2 = 1
b^2 = 2
c^2 = 3
d^2 = 5

d^4/c^2 = 5^2/3 = 25/3
(b^2+c^2)^2/(a^2+b^2) = (2+3)^2/(1+2) = 25/3
```

For latency classification:

```text
U = 25/3 ms = 1/120 s
```

and:

| Tier | Exact budget | FPS |
|---|---:|---:|
| 1 | `25/3 ms` | 120 |
| 2 | `50/3 ms` | 60 |
| 3 | `100/3 ms` | 30 |

The repeated-window policy is:

```text
mean <= Tier 1
p95  <= Tier 2
max  <= Tier 3
```

All tier classification in the exact C ABI uses integer nanoseconds and exact
cross multiplication. No `float` or `double` participates in policy
authority.

## 2. Physical Fold7 result

The committed physical WebGPU evidence for the Galaxy Z Fold7 / Snapdragon 8
Elite / Adreno 8xx reports:

```text
dense:
  host total median = 13,400,000 ns
  GPU median        = 11,534,336 ns
  lane dispatches   = 68,024,448
  policy tier       = Tier 2

largest measured Tier-1 exact-selected slice:
  M                 = 729
  host total median = 1,368,750 ns
  GPU median        = 1,282,048 ns
  lane dispatches   = 7,558,272
  policy tier       = Tier 1
```

The exact lane-work ratio is:

```text
68,024,448 / 7,558,272 = 9
```

The observational host timing ratio is approximately:

```text
13,400,000 / 1,368,750 = 9.789x
```

The observational GPU timing ratio is approximately:

```text
11,534,336 / 1,282,048 = 8.996x
```

The M=729 host measurement uses only about one sixth of the Tier-1 budget,
giving approximately `6.088x` Tier-1 headroom.

The physical result therefore demonstrates the requested policy effect on an
already-measured GPU workload: exact phase-local work moves the workload from
the 60-FPS tier into the 120-FPS tier.

## 3. Fresh CPU semantic control

A fresh Pass 208 CPU-reference benchmark was executed in the same validation
run.

```text
dense branch path:
  median           = 771,246,619 ns
  logical lanes    = 839,808
  policy tier      = over Tier 3

phase-local path:
  median           = 10,101,389 ns
  logical lanes    = 10,368
  policy tier      = Tier 2

exact work ratio   = 81x
wall ratio         = 76.350x observational
```

The selected VM81 child-state words, child projections, and objective distance
were exactly equal to the corresponding selected branches of the dense
reference.

This CPU result is the semantic control for the physical selected-route timing
evidence. It prevents physical timing from becoming its own correctness proof.

## 4. Fresh phase-locality results

### Vector shortlist

```text
dense median       = 12,855,569 ns  -> Tier 2
phase median       =    122,972 ns  -> Tier 1
exact work ratio   = 81x
wall ratio         = 104.540x observational
result equality    = exact
```

### Exact cache lookup

```text
hash-map median    = 740,611 ns -> Tier 1
phase-address      = 203,172 ns -> Tier 1
wall ratio         = 3.645x observational
result equality    = exact
```

### Selective materialization

```text
full median        = 7,108,362 ns -> Tier 1
selected median    =    98,357 ns -> Tier 1
capacity ratio     = 81x
wall ratio         = 72.271x observational
selected equality  = exact
```

These results show that the tier policy is useful even when both paths already
meet Tier 1: it still distinguishes available headroom and retains the
lower-work exact route.

## 5. Policy overhead

The integer-only policy implementation was benchmarked independently.

Approximate per-call medians derived from batched measurements:

```text
classify one latency       ~ 2.375 ns
select one route           ~ 8.812 ns
evaluate one 20-sample window ~ 45.317 ns
```

A conservative epoch containing one of each costs approximately:

```text
56.504 ns
```

Relative to the Tier-1 budget:

```text
~6 ppm
```

Relative to the `12,031,250 ns` saved in the Fold7 dense-versus-M729
comparison:

```text
~4 ppm
```

The measured policy cost is therefore materially below the observed benefit in
the validated workload.

## 6. Fail-closed behavior

The exact policy tests prove:

- a route without exact semantic equality is not eligible;
- a sparse/optimized route without an exact selector is not eligible;
- a complete exact fallback must remain available;
- if no eligible route meets the requested tier, the correct exact route is
  preserved and the result is `LATENCY_BUDGET_UNMET`;
- a candidate route requesting canonical authority is rejected;
- timing cannot create VM81, persistence, Hash72, or Hash216 authority.

The policy therefore optimizes route selection without changing the inherited
semantic or authority model.

## 7. Claim boundary

The benchmark supports **policy promotion**, not a universal hardware
performance guarantee.

It establishes:

```text
exact tier law
+ low-overhead deterministic classification
+ measured physical tier improvement on Fold7
+ fresh exact CPU semantic equality
+ fresh exact phase-locality equality
+ preserved singleton authority
```

It does not assert:

- that every device will run every workload at 120 FPS;
- that GitHub CI measured a physical GPU;
- that the Fold7 artifact compared every dense lane for equality;
- that timing defines canonical state identity.

The Fold7 artifact measured selected-sample equality. Exact selected
child-state/projection equality is independently revalidated on the CPU
reference path.

## 8. Promotion decision

All defined promotion gates passed.

The global policy is therefore:

```text
PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0
= VALIDATED_GLOBAL_CANONICAL_DEFAULT
```

for compatible latency-sensitive VM81 runtime, data-processing, and
machine-learning surfaces.

The mandatory enforcement rule is:

```text
exact semantic route set
-> apply 25/3 tier classification
-> prefer exact route satisfying requested tier
-> preserve complete exact route when budget is unmet
-> singleton VM81 admission remains authoritative
```

Existing compatible surfaces that omit the policy are repair-forward targets;
future compatible surfaces must register the global latency guard.


## Compression debt is not elapsed-time credit

The global `25/3 ms` policy and the compression-debt ledger are coupled but distinct.

```text
physical elapsed time: monotonic
compression debt: conserved computational obligation
```

A layer that cannot continue immediate work inside the `25/3 ms` tier does not receive time back. Its unresolved work must instead be retained in compressed typed form or transferred through the native 5184/Hash216 debt membrane.

The reciprocal bookkeeping normalization is:

```text
debt      3/25
capacity 25/3
```

and is exact rational accounting only.

Operationally:

```text
within 25/3 ms -> local immediate execution may continue
over 25/3 ms   -> transfer or recompress unresolved debt
```

Timing remains noncanonical for semantic identity, and the complete correct route remains preserved.
