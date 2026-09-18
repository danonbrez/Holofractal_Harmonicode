# Pass 220 I003 — Four-Phase A:B:C Max-Hardware Query Calibration

Status: IMPLEMENTED CHECKPOINT / BENCHMARK-PENDING-CI / CANDIDATE-ONLY

## 1. Purpose

I003 integrates the Pass 220 I002 holographic query metadata packet with the inherited Pass 219 Lane 5 Hash216 ranking path and subjects the resulting search stack to the repository's four-phase, time-bounded A:B:C calibration discipline.

The calibration is observational. It never changes canonical arithmetic, VM81 admission, Hash72 state, Hash216 state, or persistence authority.

## 2. Reused four reciprocal gates

The benchmark preserves the sealed reciprocal phase geometry:

- xy: 0 -> 36
- yx: 36 -> 0
- zw: 18 -> 54
- wz: 54 -> 18

No global commutativity rule is introduced.

## 3. Same-dataset A:B:C arms

For each phase and candidate-count coordinate, one deterministic query/candidate dataset is generated and reused across all timed arms.

### A — holographic composition

A evaluates the I002 exact hierarchical ranker over pre-hydrated candidate metadata:

- Hash216 agreement;
- multi-prime residue agreement;
- Fibonacci scale agreement;
- q=-1 phase signature agreement;
- modality-perspective root agreement;
- deterministic exact weighted sampling.

### B — inherited Lane 5 control

B evaluates the existing Pass 219 1.37 Hash216 optimizer on exactly the same Hash216 query/candidate identities. Its native ranking surface remains the three ordered Hash72 lanes and Pass 207 exact cyclic 72-symbol vector distance.

### C — raw exact control

C performs only the direct cyclic HARMONICODE-symbol distance over the same 216-symbol query/candidate words and stable ordering. It does not evaluate I002 metadata and does not call the Lane 5 phase-routing service.

The raw distance matches the Pass 207 kernel metric per symbol:

d(a,b) = min(|a-b|, 72-|a-b|).

## 4. Run-order normalization

Timed arm order rotates:

ABC
BCA
CAB

so one arm is not permanently first or last with respect to cache/order effects.

## 5. Time-bounded max-hardware calibration

The inherited candidate-count ladder begins at:

8,16,32,64,128,256,512,1024,2048.

The I003 benchmark can continue exact doubling after 2048 until the configured MAX_CANDIDATES ceiling, provided all three arms continue to complete the configured repeat count inside the common per-arm deadline.

For each phase:

max_hardware_closed_n(phase)

is the largest candidate count for which A, B, and C all close inside the same time membrane on that runner.

The all-phase value is:

global_max_hardware_closed_n = min_phase max_hardware_closed_n(phase).

This is an observational runner calibration, not a canonical system limit.

## 6. Fixed-size query identity

All three arms operate over the same Hash216 identities. A additionally consumes pre-generated holographic metadata attached to those candidate IDs.

This intentionally benchmarks query-time composition and ranking, not modality-ingestion cost. Translation metadata is presumed generated during hydration as formalized in I002.

## 7. Exact performance analysis

Timing is integer nanoseconds. Throughput is analyzed as an exact rational:

R_X = completed_X * 1,000,000,000 / elapsed_ns_X.

A:B, A:C, and B:C ratios are retained as exact Fraction numerator/denominator pairs.

Decimal timing summaries, if produced by later reports, are presentation-only.

## 8. Bridge into Lane 5

The new bridge:

hhs_backend/runtime/hhs_pass220_holographic_hash216_lane5_bridge_v1.py

composes the I002 ranker and existing Pass 219 Lane 5 optimizer without replacing either surface.

It verifies:

- one identical query Hash216;
- one identical candidate identity set;
- preserved reciprocal phase slots;
- candidate-only semantics;
- no Hash72 commit authority;
- no Hash216 commit authority;
- no VM81 mutation authority;
- exact CPU/VM81 replay remains required.

## 9. Runner workflow

The dedicated workflow first executes the inherited sealed Pass 219 raw-runner A:B:C calibration in the same job as a hardware/time-membrane preflight.

Only after that preflight passes does it:

1. build the cumulative exact ABI;
2. build the Pass 207 CPU-reference vector driver;
3. run dependency-scoped I001-I003 tests;
4. execute I003 A:B:C max-hardware calibration;
5. analyze exact ratios and per-phase maxima;
6. upload both inherited preflight and I003 evidence.

This preserves comparability with the already established runner-normalization methodology.

## 10. Default dedicated-workflow calibration envelope

The workflow currently supplies:

- per-leg budget: 120,000,000 ns;
- global budget: 12,000,000,000 ns;
- max candidate ceiling: 16,384;
- repeats per arm/sample: 3;
- backend: CPU_REFERENCE.

These are benchmark parameters, not canonical constants.

## 11. Authority membrane

I003 requires:

candidate_only = true
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
timing_observational_only = true

The sampler may choose where to spend search effort. It may not authorize a canonical state.

## 12. Evidence state at checkpoint

Implementation files and the dedicated workflow are repository-visible. The workflow is allowed to continue asynchronously after this restartable checkpoint.

No performance number is claimed by this document until the dedicated I003 workflow completes and its exact analyzer artifact is sealed.
