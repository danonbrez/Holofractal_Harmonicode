# Pass 219B Iteration 3 — Fused Depth-2 Phase Scaling

## Status

Experimental benchmark-only continuation of frozen Pass 219B I2.

Frozen parent:

```text
df4a6cdd61052eb27efb342e8c21c45909462d8b
```

No VM81 mutation, Hash72 emission, persistence, canonical admission, or generating-tensor semantics are changed by this iteration.

## Purpose

Pass 219B I1 established exact selective 81-origin phase hydration. I2 measured an exact 81x deterministic work/capacity reduction and large wall-clock improvements for vector shortlisting, cache locality, selective materialization, and Pass 208 CPU-reference branch expansion. An Android Adreno-8xx WebGPU depth-1 run then measured physical GPU timing with selected-output equality and found an exact affine series for the tested kernel:

```text
T_1(s) = 32,768 ns * (s + 1)
S_1(s) = 82 / (s + 1)
```

I3 tests whether a second fused 81-origin phase dimension scales with the number of materialized phase combinations rather than the total potential combinations.

## Exact depth-2 geometry

For two phase layers:

```text
q1 = q2 = 81
Q = q1*q2 = 6,561 potential phase combinations
branch families = 2
lanes per branch = 5,184
```

Dense benchmark cardinality:

```text
6,561 * 2 = 13,122 branch identities
13,122 * 5,184 = 68,024,448 logical lane dispatches
```

For a selected slice with `s1` active origins in layer 1 and `s2` active origins in layer 2:

```text
M = s1*s2
R_ideal = Q/M = 6,561/(s1*s2)
```

The benchmark sweep is:

```text
(1,1)   -> M=1     -> 6,561x ideal work reduction
(1,3)   -> M=3     -> 2,187x
(3,3)   -> M=9     -> 729x
(3,9)   -> M=27    -> 243x
(9,9)   -> M=81    -> 81x
(27,27) -> M=729   -> 9x
(81,81) -> M=6,561 -> 1x
```

## General multiplicative scaling law

For depth `d`, with phase cardinality `q_l` and active materialized origins `s_l` at layer `l`:

```text
Q_d = product(q_l)
M_d = product(s_l)
R_d = Q_d / M_d = product(q_l/s_l)
```

For repeated VM81 phase quantization where every `q_l=81`:

```text
Q_d = 81^d
R_d = 81^d / product(s_l)
```

If exactly one phase origin is known before expansion at every layer:

```text
R_d = 81^d
```

This is a work/address-space law. It does not by itself guarantee equal wall-clock speedup; hardware launch, synchronization, occupancy, memory, and cache overhead remain empirical.

## Depth-2 hardware hypothesis

I3 does not assume that the depth-1 affine constant survives fusion. It measures a general affine model:

```text
T_2(M) = a + b*M
```

and derives the equivalent fixed-overhead phase-combination count:

```text
c = a/b
```

which gives the fitted speedup model:

```text
S_2(M) ~= (Q + c)/(M + c)
```

The earlier `3,281x` single-combination figure corresponds only to the special unproven case `c=1`:

```text
(6,561 + 1)/(1 + 1) = 3,281
```

I3 exists to measure `c` rather than assume it.

## Original branch identity

The fused branch identity is stable and independent of local selected-list ordinal:

```text
combination = origin1*81 + origin2
original_branch_id = combination*2 + family
```

The Android harness carries this original identity through every selected slice. This prevents the Pass-208/I2 branch-ordinal renumbering issue from being reproduced in the experimental route.

## Android WebGPU benchmark

Repository harness:

```text
benchmarks/pass219b/pass219b_android_webgpu_depth2.html
```

It uses an integer-only WGSL compute kernel and, when available, WebGPU `timestamp-query` plus wall timing.

The dense timing dispatch performs all 68,024,448 logical lane computations. To avoid requiring a ~272 MB full output buffer on mobile hardware, it retains eight deterministic lane samples per branch for dense/selected equality checks. Therefore:

```text
original branch identity preserved = YES
selected sampled-lane equality measured = YES
full 5,184-lane output equality measured in this HTML harness = NO
repository Pass 208 kernel measured = NO
canonical state mutated = NO
```

The repository C++ reference independently validates exact cardinalities, selected-set identity uniqueness, bounds, and deterministic selected/dense lane-word equivalence for fixed witness lanes.

## Analyzer

Hardware JSON can be analyzed with:

```text
python benchmarks/pass219b/analyze_pass219b_depth2_android.py RESULT.json
```

The analyzer uses exact rational arithmetic for the affine least-squares coefficients and reports:

- `a` fixed GPU time,
- `b` time per materialized phase combination,
- `c=a/b` fixed-overhead equivalent combinations,
- exact rational and decimal R-squared,
- observed versus fitted speedup for every sweep point.

## Wiring boundary

I3 is observational only. No phase-local depth-2 route may become a canonical vector/cache/GPU dispatch path solely because this benchmark is fast. Production wiring remains a later explicit iteration requiring the inherited exact route, complete identity preservation, and exact semantic equality at the production boundary.
