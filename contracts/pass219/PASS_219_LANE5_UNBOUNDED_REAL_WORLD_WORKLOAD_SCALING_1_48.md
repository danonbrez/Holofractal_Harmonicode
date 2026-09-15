# Pass 219 Lane 5 — Unbounded Real-World Workload Scaling 1.48

## Scope

This successor contract removes the fixed-batch and `uint64_t represented_span` limits from Lane 5 candidate optimization while preserving all inherited canonical authority boundaries.

The supported workload domain is every finite workload that has an exact ordered byte serialization. Workload media/class is deliberately absent from the native ABI: text, source code, JSON, databases, binary objects, images, audio, video, archives, model/tensor bytes, executable payloads, and streamed device/application data all enter through the same exact source digest and provenance binding.

Lane 5 remains candidate-only. This contract does not grant VM81 mutation, Hash72, Hash216, persistence, PQC-key, or receipt-clock authority. A selected candidate still requires the inherited signed environmental VM81 admission path before canonical commitment.

## Full-manifold coordinate closure

The earlier 1.46 surface exposed BigInt-addressing intent but retained a `uint64_t represented_span`. That field cannot encode the complete `72^72` coordinate domain.

1.48 uses the inherited `HHSExactBigUIntView` and the Pass 219 1.36 full-manifold modulus validator for every previous/current/goal/candidate coordinate.

```text
0 <= address < 72^72
72^72 = 5184^36
bit_length(72^72 - 1) = 445
canonical full-manifold storage width = 56 bytes
```

The coordinate `72^72 - 1` MUST be admitted when canonically encoded. The modulus `72^72` itself MUST be rejected as out of range. Noncanonical leading-zero encodings MUST be rejected.

## Workload binding

Each candidate binds:

- exact previous state coordinate;
- exact current state coordinate;
- exact goal/candidate coordinate;
- workload SHA-256;
- provenance SHA-256;
- contradiction/forbidden-boundary SHA-256;
- reciprocal-phase witness SHA-256;
- route witness SHA-256;
- workload byte count;
- evidence and contradiction-check counts;
- exact quarter-cycle phase plus reciprocal inverse;
- balanced trinary collapse;
- binary collapse and nested-zero continuation;
- replay, goal, contradiction, and source-digest verification flags.

The workload digest is content binding, not canonical state authority. The provenance and forbidden-boundary digests are part of the immutable candidate descriptor.

## Streaming candidate reduction

The optimizer MUST NOT require an in-memory array of all candidate routes.

Candidate ingress is one route at a time:

```text
stream_init
  -> consider(candidate_0)
  -> consider(candidate_1)
  -> ...
  -> consider(candidate_n)
  -> stream_finalize(best)
```

The stream state is fixed-size. Candidate count therefore changes runtime, not optimizer memory footprint.

Candidate counters are observational/accounting fields. If a counter reaches `UINT64_MAX`, it saturates and sets `count_saturated=1`; candidate consideration MUST continue. The counter is not an admission bound.

The stream binds the complete workload identity from its first admissible route. Subsequent candidates with different previous/current/goal coordinates, workload digest, provenance digest, forbidden-boundary digest, or workload byte count MUST be rejected from that stream without aborting the remaining candidate search.

## Deterministic ordering

Among admissible candidates for one bound workload, selection is deterministic:

1. lower exact integer route cost;
2. lexicographically lower 32-byte route witness;
3. lower phase slot;
4. lower balanced-trinary collapse value;
5. lower binary collapse value.

No floating-point timing measurement participates in canonical selection.

## Intermediate-state rule

For every admitted 1.48 route:

```text
materialized_intermediate_states == 0
```

Lane 5 needs the previous state, current state, exact replay/provenance witness, goal, and contradiction boundary. It does not gain permission to materialize a path merely because a represented path could be long.

## Python/runtime bridge

`hhs_python/runtime/hhs_pass219_lane5_unbounded_workload_scaling_bridge.py` supplies the workload-facing adapter.

It:

- hashes arbitrary byte streams incrementally;
- supports file streaming without loading the entire source into memory;
- preserves Python BigInt state coordinates exactly and rejects coordinates outside `0 <= n < 72^72` before the native call;
- passes candidates to the native stream one at a time;
- returns only candidate receipts with canonical mutation/Hash216 authority disabled.

The per-envelope byte-count field is an unsigned 64-bit exact integer, allowing up to `2^64-1` serialized bytes in a single workload envelope. This payload-accounting width is independent of the 445-bit manifold coordinate width.

## Required validation

The dependency-scoped gate MUST prove:

1. exact `72^72 - 1` coordinate admission;
2. `72^72` rejection;
3. noncanonical BigInt rejection;
4. zero intermediate materialization;
5. fixed-size stream state while processing at least 1,000,000 candidates;
6. continued candidate processing after accounting-counter saturation;
7. fail-closed rejection of mixed-workload streams;
8. fail-closed rejection of invalid phase, contradiction, authority, and candidate/goal mismatches;
9. workload-class agnosticism across text, structured data, source, generic binary, image-like, audio-like, video-like, tensor/model-like, compressed, and empty payloads;
10. chunk-partition-independent workload identity;
11. deterministic replay;
12. inherited Lane 5 1.37-1.47, full hydration, raw5184, and signed VM81 authority boundaries remain green.
