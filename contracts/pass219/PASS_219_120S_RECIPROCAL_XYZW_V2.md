# Pass 219 — 120-Second Reciprocal x,y,z,w Architecture Benchmark v2

**Date:** 2026-09-16  
**Status:** normative reciprocal benchmark contract  
**Depends on:** `PASS_219_120S_INFINITE_STREAM_THROUGHPUT_V1`

## 1. Objective

Measure the same exact deterministic workload on two opposite exact architectures with a reciprocal four-pass protocol:

```text
A / x = HHS maximum capacity in 120 seconds -> Dataset X
B / y = optimized conventional maximum capacity in 120 seconds -> Dataset Y
C / z = optimized conventional architecture completes Dataset X exactly
D / w = HHS completes Dataset Y exactly
```

A and B are bounded capacity measurements. C and D are completion-time measurements and are not assigned a 120-second limit.

This creates two datasets, each consumed exactly twice:

```text
Dataset X: A produces, C consumes.
Dataset Y: B produces, D consumes.
```

Dataset X is selected exactly once, by A's clock-bounded capacity pass. Dataset Y is selected exactly once, by B's clock-bounded capacity pass. The reciprocal consumer is not permitted to choose, truncate, reorder, regenerate with a different seed, or extend its dataset.

## 2. Workload generator

The workload remains the deterministic lazy sequence:

```text
Q_0, Q_1, Q_2, ...
Q_i = (x_i, k_i)
F(x) = a*x + b (mod m)
compute F^k_i(x_i) exactly
```

with:

```text
m = 2305843009213693951
k_i in [1,000,000, 1,000,999,999]
fixed stream seed = 0x2191205a72c0ffee
```

A and B each begin at `Q_0`. Their 120-second capacity can produce different prefix lengths; that is intentional. Those two prefix lengths freeze X and Y respectively.

A dataset identity is:

```text
(stream seed,
 prefix query count,
 exact represented transition sum,
 exact descriptor-bit sum,
 ordered descriptor digest,
 ordered endpoint digest)
```

The descriptor digest proves ordered input identity. The endpoint digest proves ordered exact result identity.

## 3. Timing and runner protocol

All four benchmarks execute sequentially on the same GitHub Actions runner with one active benchmark thread:

```text
A capacity window = 120,000,000,000 ns
B capacity window = 120,000,000,000 ns
C = run until every query in X is complete
D = run until every query in Y is complete
```

A and B are allowed only a bounded final-query overrun. The analyzer rejects either capacity pass if it stops before the declared window or exceeds it by more than `max(1 second, 1%)`.

C and D are not rate extrapolations. They execute every frozen query in their reciprocal dataset and report actual wall-clock completion time.

## 4. HHS architecture — A and D

For each query HHS SHALL:

1. compute the exact affine jump by binary affine-map composition;
2. independently recompute through exact 2x2 homogeneous matrix exponentiation;
3. require exact endpoint equality;
4. pass the endpoint through the production Lane 5 candidate validator;
5. preserve:
   - `materialized_intermediate_states = 0`;
   - candidate-only authority;
   - zero canonical VM81 mutation authority;
   - zero canonical Hash72 authority;
   - zero canonical Hash216 authority;
   - signed environmental VM81 admission requirement.

A uses this architecture for the 120-second capacity pass. D uses the identical architecture to complete exactly the dataset frozen by B.

## 5. Optimized conventional architecture — B and C

The optimized exact conventional architecture uses 2x2 homogeneous matrix exponentiation by squaring:

```text
[a b] ^ k
[0 1]
```

over the same exact modular integer arithmetic.

It SHALL NOT use the HHS Lane 5 admission membrane or HHS candidate authority. It is intentionally an optimized skip-ahead conventional comparator, not the literal repeated-step comparator from v1.

B uses this architecture for the 120-second capacity pass. C uses the identical architecture to complete exactly the dataset frozen by A.

The v1 literal-step result remains preserved separately. v2 does not rewrite or erase that evidence.

## 6. Reciprocal x,y,z,w measurement

The primary measured surface is:

```text
x = elapsed(A): HHS capacity interval
y = elapsed(B): conventional capacity interval
z = elapsed(C): conventional time to complete exact Dataset X
w = elapsed(D): HHS time to complete exact Dataset Y
```

The two same-work comparisons are therefore:

```text
Dataset X:
  A(HHS) and C(conventional) perform the identical ordered query set.

Dataset Y:
  B(conventional) and D(HHS) perform the identical ordered query set.
```

Derived same-work speed ratios are observational:

```text
HHS/conventional speed on X = z / x
HHS/conventional speed on Y = y / w
```

No ratio is allowed to substitute for execution. C and D must both complete.

## 7. Dataset non-divergence rule

The benchmark passes only when:

```text
A.query_count == C.query_count
A.represented_transitions == C.represented_transitions
A.descriptor_bits == C.descriptor_bits
A.descriptor_digest == C.descriptor_digest
A.endpoint_digest == C.endpoint_digest

B.query_count == D.query_count
B.represented_transitions == D.represented_transitions
B.descriptor_bits == D.descriptor_bits
B.descriptor_digest == D.descriptor_digest
B.endpoint_digest == D.endpoint_digest
```

This enforces the rule that neither architecture can receive a different dataset in more than its single capacity-selection pass.

## 8. Required output

Raw records SHALL include, as applicable:

```text
benchmark id A/B/C/D
axis x/y/z/w
architecture
dataset X/Y
mode capacity_120s or reciprocal_completion
elapsed_ns
completed_queries
represented_transitions
descriptor_bits
ordered descriptor digest
ordered endpoint digest
HHS affine composition count
matrix multiplication count
Lane 5 admission count
materialized intermediate state count
```

The analyzer SHALL preserve raw integer evidence before computing rates.

## 9. Acceptance

A run passes only if:

```text
A and B both satisfy the 120-second capacity contract
A/B/C/D all complete successfully
A and D use the HHS path and admit every endpoint through Lane 5
B and C use the optimized exact conventional matrix path
Dataset X input/result identity matches exactly between A and C
Dataset Y input/result identity matches exactly between B and D
no HHS represented intermediate state is materialized
all four benchmarks run sequentially on the same runner
```

## 10. Claim scope

This protocol compares two declared exact architectures on the same deterministic affine-orbit workload and provides reciprocal same-work completion times.

It does not claim universal computing supremacy. The v1 literal-step benchmark remains a separate measure of represented-path compression versus sequential transition execution; v2 instead isolates architecture overhead against an optimized exact conventional skip-ahead implementation.
