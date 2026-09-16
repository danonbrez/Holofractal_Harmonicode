# Pass 219 — 120-Second Infinite-Stream Throughput v1

**Date:** 2026-09-16  
**Status:** normative benchmark contract  
**Depends on:** `PASS_219_TIME_BOUNDED_MATH_SUPREMACY_V1`

## 1. Objective

Measure how much exact represented computation HHS/Lane 5 and the declared sequential classical baseline can process in real time when both consume the same deterministic, non-terminating workload stream for equal 120-second wall-clock epochs.

This cycle replaces the finite 50 ms crossover grid with a sustained streaming experiment.

## 2. Same infinite workload

The logical workload is the lazy sequence:

```text
Q_0, Q_1, Q_2, ...
```

No finite workload list is pre-materialized. A deterministic index-to-query generator produces each query only when requested. The implementation uses a fixed seed and fails if its 64-bit execution index wraps; the practical stream therefore has no terminal condition inside the experiment and is bounded only by the clock.

Every query has the form:

```text
Q_i = (x_i, k_i)
compute F^k_i(x_i) exactly
F(x) = a*x + b (mod m)
```

with fixed exact `a`, `b`, and `m`, and deterministic `x_i` and `k_i` from the stream seed. In v1:

```text
m = 2305843009213693951
k_i in [1,000,000, 1,000,999,999]
```

Both engines start from `Q_0` and consume queries in the same order.

## 3. Timing protocol

Each engine receives an independent epoch:

```text
T_window = 120,000,000,000 ns
active benchmark threads per epoch = 1
```

The epochs run sequentially on the same GitHub Actions runner. They MUST NOT run concurrently because shared-core/cache contention would make the comparison dependent on scheduling interference.

A small bounded overrun is permitted only to finish/check the current timing quantum. The evidence analyzer rejects an epoch that stops before the declared window or exceeds the window by more than max(1 s, 1%).

## 4. HHS/Lane 5 engine

For every query completed inside its epoch, HHS SHALL:

1. compute the exact affine jump by binary affine-map composition;
2. independently recompute the endpoint through exact 2x2 homogeneous matrix exponentiation;
3. require endpoint equality;
4. pass the endpoint through the production Lane 5 1.48 candidate validator;
5. preserve:

```text
materialized_intermediate_states = 0
candidate_only = 1
canonical VM81 mutation authority = 0
canonical Hash72 authority = 0
canonical Hash216 authority = 0
requires signed environmental VM81 admission = 1
```

The timed HHS result therefore includes mathematical composition, an independent verifier, and Lane 5 admission overhead.

## 5. Sequential classical engine

The classical comparator consumes the same `Q_i` stream, but computes each query by literal repeated transition application:

```text
x <- F(x)
```

exactly `k_i` times before advancing to `Q_(i+1)`.

It may keep the current state in constant memory but may not replace repeated stepping with affine composition, exponentiation, closed forms, jump tables, or equivalent skip-ahead logic. This is the same declared `C_step` class used by Stage 1.

If the 120-second boundary is reached partway through a query, the partial transition count is retained as executed work but the incomplete query is not counted as a completed endpoint.

## 6. Same-stream exactness

After both timed epochs, the entire prefix completed by the classical engine SHALL be replayed with the exact HHS affine-composition path outside the timed windows.

A deterministic endpoint fold/digest over that prefix MUST match exactly:

```text
Digest_classical_prefix == Digest_HHS_replay_prefix
```

This verifies that both engines were solving the same ordered workload and that the classical completed endpoints agree with the exact HHS route.

## 7. Required real-time measurements

The benchmark SHALL report raw integer counts first. Derived rates are observational and have no canonical state authority.

### HHS

```text
elapsed_ns
completed_queries
sum(k_i) for completed queries
sum(bit_length(k_i))
affine composition count
independent matrix multiplication count
Lane 5 admission count
materialized intermediate states
endpoint digest
```

### Classical

```text
elapsed_ns
completed_queries
sum(k_i) for completed queries
actual transition steps executed, including partial final query
sum(bit_length(k_i)) for completed queries
partial final-query progress
endpoint digest
```

## 8. Information processed

Because the word information can mean several different things, v1 SHALL report multiple explicit quantities.

### 8.1 Endpoint state-space information rate

For modulus `m`, one exact endpoint occupies a state space of size `m`:

```text
H_endpoint = log2(m) bits-equivalent
```

For completed-query rate `R_q`:

```text
Gamma_endpoint = R_q * log2(m)
```

This is a state-space-capacity normalization, not a Shannon entropy claim.

### 8.2 Exact descriptor-bit throughput

Each started query contains an exact `x_i` address width plus the exact integer bit length of `k_i`. The analyzer reports the corresponding descriptor bits processed per second. This is an exact representation-width metric, not semantic information entropy.

### 8.3 Represented path-resolution rate

For HHS:

```text
R_path,HHS = sum(k_i completed) / elapsed_seconds
```

For the classical comparator, the directly executed transition rate is:

```text
R_step,C = executed_transition_steps / elapsed_seconds
```

Their ratio measures how many represented path transitions HHS resolves per second relative to how many literal transition applications the comparator executes per second.

### 8.4 Counted HHS control work

The analyzer also reports:

```text
represented transitions /
(affine compositions + matrix verifier multiplications + Lane 5 admissions)
```

This ratio is a high-level representation/composition metric. The counted operations are heterogeneous and MUST NOT be described as equivalent CPU instructions.

## 9. Acceptance rules

The run passes only if:

```text
both epochs meet the 120-second timing contract
both engines complete at least one query
all HHS endpoints pass independent matrix verification
all HHS endpoints pass Lane 5 admission
HHS materialized_intermediate_states remains zero
classical executed steps >= its completed represented steps
classical partial progress is internally valid
full classical completed prefix replays to the identical HHS digest
```

## 10. Claim scope

This cycle answers a sustained-throughput question for the two declared execution methods under one runner envelope.

It does not claim universal classical-computing supremacy and does not compare HHS against optimized conventional skip-ahead affine exponentiation. That remains the stronger Stage-2 comparator class.
