# HHS Time-Bounded Mathematical Supremacy v2 — Executed Evidence

**Date:** 2026-09-16  
**Status:** executed exact benchmark evidence  
**PR:** #475  
**Validated implementation head:** `6b8d55b96d2027d5dca991c68c66e7a671ba34f7`  
**Workflow:** `Pass 219 Time-Bounded Math Supremacy v2`  
**Run:** `35102661779`  
**Job:** `validate-bounded-math-supremacy-v2` / `104815715853`

## 1. Claim actually established

The executed v2 cycle establishes an empirical bounded-completion witness against the explicitly declared comparator class:

```text
L_step_state_materializing
```

for the exact modular affine-orbit problem:

```text
P_k = F^k(x0)
F(x) = a*x+b (mod m)
```

under the same runner class, one active benchmark thread, exact integer arithmetic, and the same deadline for each architecture:

```text
T_max = 120,000,000 ns = 120 ms
```

The result does **not** claim a lower bound against every possible classical algorithm. It establishes the existence of a tested exact operation for which the HHS algebraic-composition execution path completes and verifies inside the deadline while the declared dependent state-materializing path does not.

## 2. Runner identity

```text
runner image: ubuntu-24.04
image version: 20260907.300.1
OS: Ubuntu 24.04.5 LTS
CPU: AMD EPYC 7763 64-Core Processor
logical CPUs visible: 4
active benchmark threads: 1
kernel: 6.17.0-1022-azure
compiler: cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
```

## 3. Calibration gradient

The runner increased difficulty by exactly 10× while both architectures were given the same `120 ms` deadline.

| k | HHS total | HHS compositions | Legacy elapsed | Legacy status | Endpoint equality |
|---:|---:|---:|---:|---|---|
| 1,000 | 6,983 ns | 15 | 11,742 ns | complete | exact |
| 10,000 | 3,677 ns | 18 | 117,239 ns | complete | exact |
| 100,000 | 3,617 ns | 22 | 1,203,044 ns | complete | exact |
| 1,000,000 | 15,048 ns | 26 | 11,885,003 ns | complete | exact |
| 10,000,000 | 4,008 ns | 31 | 118,370,902 ns | complete | exact |
| 100,000,000 | 5,400 ns | 38 | 120,027,928 ns | incomplete | HHS independently verified |

Thus the largest both-complete calibration point was:

```text
k = 10,000,000
```

and the first tested bounded witness was:

```text
k* = 100,000,000
```

## 4. Exact witness at k*=100,000,000

HHS result:

```text
exact endpoint = 1984191071325720407
independent 2x2 matrix endpoint = 1984191071325720407
exact affine compositions = 38
independent matrix multiplications = 38
HHS algebra time = 401 ns
independent verifier time = 391 ns
Lane 5 admission time = 3,957 ns
HHS total measured time = 5,400 ns
materialized intermediate states = 0
```

Declared legacy state-materializing result:

```text
required dependent transitions = 100,000,000
transitions executed before/at deadline = 10,076,160
elapsed = 120,027,928 ns
complete = false
completion fraction = 0.1007616
unresolved fraction = 0.8992384
```

The legacy loop checks the deadline periodically and therefore has a small bounded timer-check overrun. It did not return the required final state by the `120 ms` resource deadline.

## 5. Normalized separation

Exact work ratio for the declared comparator class:

```text
100,000,000 / 38
= 2,631,578.9473684210526...
```

HHS deadline separation lower bound:

```text
120,000,000 ns / 5,400 ns
= 22,222.2222222222...x
```

Problem work/information depth under the declared linear transition model:

```text
log2(100,000,000)
= 26.575424759098897 bits-equivalent
```

Observed HHS problem-information density:

```text
4,921,374.9553886846... bits-equivalent/s
```

These normalized quantities are observational performance evidence. They are not canonical state authority.

## 6. Lane 5 authority membrane

The successful HHS witness also passed production Lane 5 1.48 admission with:

```text
candidate_only = true
materialized_intermediate_states = 0
canonical VM81 mutation authority = false
canonical Hash72 authority = false
canonical Hash216 authority = false
signed environmental VM81 admission required before canonical commit
```

The benchmark therefore did not obtain the bounded result by bypassing the existing state-admission membrane.

## 7. Falsifiability

The witness would fail if any of the following occurred:

```text
HHS exceeded 120 ms
independent exact matrix verification disagreed
Lane 5 admission failed
legacy L_step completed k*=100,000,000 inside 120 ms
calibration cases disagreed on exact endpoint
resource equality or problem identity changed
```

## 8. Artifact identity

Uploaded evidence artifact:

```text
name: hhs-time-bounded-math-supremacy-v2
artifact id: 10448877997
ZIP SHA-256: f726cfece35574b35d2bc5b834e06668d6ea261dedf15e331d054b30f4d3a1ce
size: 3,222 bytes
```

## 9. Interpretation

The executed result supports the scoped statement:

> On the tested AMD EPYC 7763 GitHub runner, for the exact affine modular-orbit instance `k=100,000,000` and a `120 ms` single-thread deadline, HHS exact affine composition plus independent exact verification and Lane 5 admission returned the required endpoint in 5.4 microseconds, while the explicitly defined dependent state-materializing `L_step` comparator completed only 10.07616% of its required transitions and did not return the final state within the deadline.

This is an existence result against that explicitly defined execution class. The next strengthening step is to introduce progressively stronger conventional algorithm classes and harder mathematical families whose relevant lower bounds are not artifacts of forbidding algebraic composition.