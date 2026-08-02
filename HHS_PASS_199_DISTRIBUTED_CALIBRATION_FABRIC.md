# HHS PASS 199 — DURABLE DISTRIBUTED CALIBRATION FABRIC

Contract identifier: `HHS-P199-P198-P190-DCT-WORKER-SLOTS64-VM81-H72`

Classification target: `HHS_PASS_199_DURABLE_DISTRIBUTED_CALIBRATION_FABRIC_VERIFIED`

## Purpose

Pass 199 connects the Pass 198 operation-calibration registry to the verified Pass 190 Iteration 7 durable worker, scheduler, cancellation, retry, lease-recovery, and receipt authority.

It executes registered A/B parameter trees as durable branch jobs while preserving the singular VM81 mutation authority and one canonical Hash72 tree-commit operation.

## Authority split

Candidate workers may:

- claim one durable branch job per worker slot;
- read immutable exact arguments;
- evaluate branch A or branch B outside the VM81 authority lock;
- return immutable candidates with exact cell and lane witnesses.

Candidate workers may not:

- alter canonical VM81 state;
- write the final parameter-state result;
- promote a simplification;
- mutate the Pass 198 operation specification;
- commit the completed tree;
- create a second Hash72 authority stream.

Candidate completion re-enters Pass 190 only to validate the claim token, candidate binding, candidate Hash72, lease, capability, and worker ownership before storing durable candidate evidence.

## Durable branch jobs

Each Pass 198 parameter state creates two deterministic jobs:

```text
ordinal n, branch A → calibration.evaluate_branch
ordinal n, branch B → calibration.evaluate_branch
```

Default Pass 197 calibration produces 405 states and 810 individual durable branch jobs.

The job identity binds:

- Pass 199 run identity;
- Pass 198 operation identity and specification Hash72;
- parameter-tree Hash72;
- canonical ordinal;
- exact rational `x` and `y`;
- lexical integer `xy` exponent;
- branch identity.

## Bounded authority batching

Individual durable jobs are retained, but repeated whole-state mutation is bounded through governed batch operations:

```text
calibration.submit_tree
  → one atomic mutation creates all durable branch jobs

calibration.ensure_workers
  → one atomic mutation creates or refreshes up to 64 one-job worker slots

calibration.claim_batch
  → one atomic mutation assigns at most one job to each available slot

candidate computation
  → exact work occurs concurrently outside authority

calibration.complete_batch
  → one atomic mutation validates and completes the claimed slot set
```

For the default 810-job tree, 64 durable slots require no more than 13 claim batches and 13 completion batches. The compute-worker count is independently bounded from 1 to 64; the verified default is eight compute workers over 64 durable slots.

This batching changes transport cost, not job identity, worker ownership, candidate semantics, or canonical admission.

## Exact candidate witness

Every admitted branch candidate retains:

- 81 exact cell-value Hash72 witnesses;
- the complete 5,184-address codec witness root;
- cell root;
- address root;
- exact parameter coordinate;
- branch identity;
- operation and tree identity;
- candidate Hash72;
- Pass 190 execution request and durable completion identity.

The address witness uses

```text
c = 27*i + 9*j + 3*k + l
s = 64*c + o
```

for all `c ∈ [0,80]` and `o ∈ [0,63]`.

No floating-point value participates in candidate identity, equality, admission, state, proof, receipt, or replay.

## Out-of-lock candidate computation

Pass 190 invocation remains the serialized mutation authority. Pass 199 deliberately separates candidate computation from candidate admission:

```text
batch claim under Pass 190 authority
  → release authority
  → compute immutable exact candidates concurrently
  → validate and persist the batch under Pass 190 authority
```

This permits concurrent candidate computation without concurrent canonical mutation.

## Canonical ordinal serialization

When every branch job is complete, `calibration.commit_tree` performs exactly one canonical admission operation.

The singleton operation:

1. discovers all jobs belonging to the run;
2. requires exactly two completed candidates per ordinal;
3. rejects duplicate or missing branches;
4. validates every candidate against its durable request;
5. compares A and B exact-equivalence roots;
6. serializes states strictly by ordinal `0..N-1`;
7. derives the ordered state root;
8. records the closed or rejected tree in canonical Pass 190 state;
9. emits one canonical tree-commit receipt.

Submission, worker-slot, claim, and completion receipts are durable transport evidence. They are not canonical tree admissions.

## Cancellation, retry, and recovery

Pass 199 inherits and validates Pass 190 behavior for:

- queued-job cancellation;
- terminal-job retry within the exact attempt budget;
- deterministic retry scheduling;
- expired claim-lease recovery;
- stale worker release;
- process restart and database reopening;
- idempotent tree preparation;
- receipt-independent run identity.

Cancellation, retry, worker count, worker ordering, batching, and process restart must not alter the final ordered state root.

## Replay

After singleton admission, Pass 199 performs a complete independent replay of all 810 branch candidates for the default tree.

The replay must reproduce:

- all branch candidate roots;
- all state comparison results;
- canonical ordinal ordering;
- the final ordered state root.

Replay mismatch prevents closure and prevents Pass 198 simplification-proof recording.

## Pass 198 integration

A closed distributed run is recorded in the Pass 198 atomic event ledger with execution mode:

```text
PASS199_DURABLE_DISTRIBUTED
```

Proof-carrying simplification records receive the distributed run identity only after:

- zero A/B mismatches;
- zero admitted singular states;
- full replay equality;
- verified singleton commit receipt;
- retained cell and lane witnesses.

Pass 199 does not automatically promote any simplification. Compiler and runtime promotion remain governed by Pass 198 evidence thresholds and explicit VM81-authorized actions.

## Registered Pass 190 overlay operations

The authoritative Pass 199 V2 registry contains 49 operations: the inherited 42 Pass 190 Iteration 7 operations plus seven Pass 199 operations.

The Pass 199 operations are:

- `calibration.evaluate_branch` — pure immutable candidate operation;
- `calibration.complete_claimed` — single-candidate compatibility completion;
- `calibration.commit_tree` — singleton canonical tree admission;
- `calibration.submit_tree` — atomic durable-tree submission;
- `calibration.claim_batch` — atomic one-job-per-worker batch claim;
- `calibration.complete_batch` — atomic validated candidate-batch completion;
- `calibration.ensure_workers` — atomic durable worker-slot creation or refresh.

Every inherited Pass 190 operation remains unchanged.

## Runtime, API, and visual surfaces

Runtime:

- `hhs_backend/runtime/hhs_pass199_distributed_calibration_fabric_v1.py`
- `hhs_backend/runtime/hhs_pass199_distributed_calibration_runtime_v1.py`
- `hhs_backend/runtime/hhs_pass199_distributed_calibration_runtime_v2.py`

API:

- `GET /api/runtime/distributed-calibration/status`
- `POST /api/runtime/distributed-calibration/prepare`
- `POST /api/runtime/distributed-calibration/run`
- `GET /api/runtime/distributed-calibration/report`
- `GET /api/runtime/distributed-calibration/tools`
- `POST /api/runtime/distributed-calibration/tools/invoke`

Visual IDE:

- Pass 199 durable calibration panel;
- compute-worker selector;
- state, job, slot, batch, replay, and commit receipt projection;
- no frontend fabrication of canonical state.

## Verified workload requirements

The first Pass 199 workload is accepted only when:

- Pass 190 Iterations 1–7 inherited authority workflows remain passing;
- all Pass 199 lifecycle tests pass;
- context reopening preserves Pass 199 jobs;
- candidate tampering is rejected before completion;
- direct in-lock execution of a calibration branch is rejected;
- cancellation and retry preserve the state root;
- stale lease recovery preserves the state root;
- the default 405-state tree creates and completes 810 jobs;
- 320 states are admitted and 85 are explicit domain rejections;
- 1,658,880 VM5184 address comparisons close with zero mismatches;
- 64 durable slots complete the tree in no more than 13 claim/completion batches;
- candidate computation occurs outside the authority lock;
- complete 810-branch replay reproduces the ordered state root;
- exactly one canonical `calibration.commit_tree` receipt exists;
- four proof-carrying simplification records are bound into Pass 198;
- floating-point canonical operations remain absent;
- API and visual projections pass source and syntax validation.

## Claim boundary

Pass 199 does not claim multi-host distributed consensus, external provider execution, arbitrary registered adapters, automatic compiler mutation, automatic runtime admission, live DigitalOcean acceptance, or physical hardware calibration. The implementation is a single-host durable worker fabric with parallel immutable candidate computation, bounded authority batches, and one serialized VM81 tree-admission authority.
