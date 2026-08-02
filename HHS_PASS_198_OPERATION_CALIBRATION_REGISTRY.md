# HHS PASS 198 — OPERATION CALIBRATION REGISTRY AND PROOF-CARRYING SIMPLIFICATION AUTHORITY

Contract identifier: `HHS-P198-OCR-PROOF-SIMPLIFICATION-VM81-H72`

Classification: `HHS_PASS_198_GENERIC_CALIBRATION_REGISTRY_FOUNDATION_VERIFIED`

## 1. Purpose

Pass 198 generalizes the exact Pass 197 A/B workload into a persistent registry of calibratable integrated operations.

A registered operation defines:

- canonical input schema;
- exact parameter axes;
- domain constraints;
- reference branch A;
- candidate branch B;
- required invariants;
- retained coordinate and lane witnesses;
- cost model;
- negative mutations;
- replay policy;
- immutable operation identity.

The Pass 197 reciprocal matrix gate is the first executable adapter. Future operations must enter through a separately hashed specification and executable adapter rather than being silently inserted into the existing workload.

## 2. Persistent registry

The registry uses SQLite with:

- WAL journaling;
- full synchronous commits;
- foreign-key enforcement;
- immutable operation identities;
- append-only Hash72 events;
- persistent calibration runs;
- persistent simplification proofs;
- explicit run-to-proof relationships;
- deterministic event-chain verification.

The frontend, API, worker, SQLite database, and proof list do not independently grant canonical mutation authority.

## 3. Deterministic parameter trees

For each operation, the registry constructs a canonical tree from its registered axes or exact caller overrides.

The first operation retains the Pass 197 axes:

```text
x,y ∈ {-3,-2,-1,-1/2,0,1/2,1,2,3}
xy ∈ {-2,-1,0,1,2}
```

Every state records:

- deterministic ordinal;
- exact rational `x` and `y`;
- lexical `xy` exponent;
- domain classification;
- sign class.

The tree receives a Hash72 identity before execution. Zero reciprocal states remain explicit rejected branches.

## 4. Executable adapter

Adapter `hhs.pass197.reciprocal_matrix_gate.v1` executes the registered tree through the Pass 197 exact runtime.

A recorded run binds:

- operation specification Hash72;
- parameter-tree Hash72;
- Pass 197 configuration Hash72;
- report Hash72;
- exact state-root Hash72;
- VM81 authorized-tick receipt when invoked through the API;
- replay result;
- exact calibration summary;
- ordered registry event.

Unsupported adapters fail closed. Registering a specification does not make it executable.

## 5. Proof-carrying simplifications

Every closed calibration run produces proof records for each admitted simplification.

A proof carries:

- source operation identity;
- candidate operation identity;
- tested parameter-envelope Hash72;
- exact equivalence root;
- counterexample and singular-state results;
- registered negative mutations;
- retained witnesses;
- before/after/saved exact operation cost;
- replay receipt;
- contributing run identities;
- revocation conditions;
- proof Hash72.

The first registered proof set covers:

1. original numerator to compact numerator;
2. reciprocal denominator factorization;
3. VM81 lane-preserving broadcast;
4. exact matrix-power caching by lexical `xy`.

## 6. Promotion membrane

Simplification state progresses only one stage at a time:

```text
OBSERVED
→ ENVELOPE_VERIFIED
→ CROSS_WORKLOAD_VERIFIED
→ COMPILER_CANDIDATE
→ RUNTIME_ADMITTED
→ FROZEN_CONSTRAINT
```

Minimum distinct verified-run requirements are:

- `CROSS_WORKLOAD_VERIFIED`: 2;
- `COMPILER_CANDIDATE`: 2;
- `RUNTIME_ADMITTED`: 3;
- `FROZEN_CONSTRAINT`: 4.

Promotion rejects unknown run identities, skipped stages, insufficient evidence, and revoked records. Automatic compiler promotion and automatic runtime admission are disabled.

## 7. Revocation

Any counterexample, replay mismatch, retained-witness loss, operation-identity change, or unverified domain expansion is grounds for revocation.

Revocation is persistent, receipt-bearing, and fail-closed. A revoked record cannot be promoted.

## 8. VM81/API authority

Mutating HTTP surfaces require `runtime_controller.authorized_tick(...)` before registry mutation:

- operation registration;
- calibration execution;
- simplification promotion;
- simplification revocation.

Read-only parameter-tree construction and registry queries do not grant mutation authority.

Routes:

- `GET /api/runtime/calibration-registry/status`
- `GET /api/runtime/calibration-registry/operations`
- `GET /api/runtime/calibration-registry/operations/{operation_id}`
- `POST /api/runtime/calibration-registry/operations`
- `POST /api/runtime/calibration-registry/parameter-tree`
- `POST /api/runtime/calibration-registry/run`
- `GET /api/runtime/calibration-registry/runs`
- `GET /api/runtime/calibration-registry/simplifications`
- `POST /api/runtime/calibration-registry/simplifications/promote`
- `POST /api/runtime/calibration-registry/simplifications/revoke`
- tool registry and invocation surfaces.

## 9. Visual interface

The Holofractal Harmonizer gains a Pass 198 panel showing:

- registered operations;
- recorded runs;
- envelope-verified simplifications;
- compiler candidates;
- event-chain status;
- parameter-tree generation;
- registered-envelope execution;
- proof-record inspection.

The panel deliberately does not expose casual one-click compiler or runtime promotion.

## 10. Current-tree integration scan

The dedicated workflow runs the Pass 196 observer against the exact PR tree and emits a concise artifact containing:

- manifest Hash72 and Hash216;
- file and byte counts;
- maximum discovered pass;
- pass-state counts;
- mandatory surface status;
- unresolved pass-layer list;
- Pass 198 classification;
- explicit authority boundary.

The scan is observational. It does not claim full repository integration closure, persist encrypted vectors, mutate DigitalOcean, or grant runtime authority.

## 11. Acceptance criteria

Pass 198 foundation is verified when:

- the built-in Pass 197 operation is registered idempotently;
- the default tree contains 405 states, 320 eligible and 85 rejected;
- exact registered runs persist and replay;
- four simplification proofs are created;
- a second distinct run updates proof evidence;
- one-stage promotion succeeds only with sufficient known evidence;
- skipped or under-evidenced promotion fails;
- revocation persists;
- float ingress fails;
- database reopen preserves operations, runs, proofs, and event chain;
- Python and JavaScript compile;
- API and visual wiring validate;
- current-tree Pass 196 scan discovers Pass 198 and emits evidence.

## 12. Claim boundary

This pass provides the generic registry and first executable adapter. It does not yet provide arbitrary expression execution, automatic operation-code loading, automatic compiler mutation, runtime admission without staged evidence, Pass 190 distributed job submission, physical hardware evidence, live DigitalOcean acceptance, or universal parameter-space exhaustion.
