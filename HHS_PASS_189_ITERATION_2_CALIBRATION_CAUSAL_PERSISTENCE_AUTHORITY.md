# HHS PASS 189 — ITERATION 2 CALIBRATION, CAUSAL BATCH, AND PERSISTENCE AUTHORITY

## Exact measured-binding ledger, bounded physical-output admission, receipt-locked multi-object worldlines, atomic checkpoints, deterministic recovery, and DigitalOcean durable state

## 1. Normative metadata

| Field | Value |
|---|---|
| Parent contract | `HHS-P189-HQLH-LS41-XNOR-P1-H72-H216-UPA` |
| Iteration identifier | `HHS-P189-HQLH-ITERATION-2-CALIBRATION-CAUSAL-PERSISTENCE` |
| Pass number | `189`, Iteration 2 |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative baseline | `main @ 992b4e92a54d4656d66af4edfab7e03922addca6` |
| Inherited Iteration 1 merge | `a1a55a4f621ff3678f5af81119439e9558cf9db4` |
| Deployment authority | Existing DigitalOcean Ubuntu host, systemd, nginx, durable `/var/lib/hhs-pass189` state |
| Vercel | Non-authoritative and excluded from acceptance |
| Arithmetic authority | Exact integers and rational numerator/denominator pairs; floats rejected from canonical ingress |
| Honest classification | `HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS` |

## 2. Purpose

Iteration 1 established exact contextual addressing, typed membranes, Lo Shu/XNOR/ternary hydration, V72, Hash72/Hash216 receipts, replay, and shared software equation projections. Four material gaps remained:

1. calibration existed only as unvalidated metadata;
2. all breadboard output was unconditionally blocked rather than admitted through a bounded evidence gate;
3. worldline output was a label rather than an atomic multi-object resolver;
4. runtime authority was memory-only and lacked durable checkpoint/recovery.

Iteration 2 closes those software gaps without claiming that real laboratory measurements have occurred.

## 3. Exact calibration profile

A calibration profile records device identity, canonical variable, unit and dimension, exact scale and offset, raw and canonical ranges, resolution and residual tolerance, required sample count, evidence class, calibration source, device attestation state, operator-arm Hash72, created-nanosecond witness, and profile Hash72.

All numeric calibration fields are exact rational pairs. Binary floating-point values are rejected from canonical profile, sample, output, and worldline ingress.

Supported evidence classes are `SYNTHETIC` and `MEASURED_HARDWARE`. Synthetic evidence may validate software behavior but cannot authorize a physical candidate.

## 4. Sample and residual authority

For exact raw value `r`, scale `s`, offset `o`, and expected canonical value `e`:

```text
computed = r*s + o
residual = computed - e.
```

A sample is accepted only when:

```text
raw_min <= r <= raw_max
canonical_min <= computed <= canonical_max
abs(residual) <= tolerance.
```

A profile becomes `VALIDATED` only after the required number of samples exists and every recorded sample is accepted. Sample identity, source, measurement-nanosecond witness, computed value, residual, and receipt are preserved.

## 5. Bounded output admission

Output admission supports `SIMULATION` and `PHYSICAL` modes. Simulation admission requires canonical range validity and emits a `SIMULATION_ONLY` receipt.

Physical candidate admission additionally requires a validated profile, `MEASURED_HARDWARE` evidence, device attestation, matching operator-arm token hash, and canonical range validity.

Even after these gates pass, this implementation emits only `CANDIDATE_ONLY_NO_DEVICE_DRIVER`. Actual GPIO, serial, USB, network-device, or actuator dispatch remains outside this iteration and must be bound by a later device-specific authority.

## 6. Persistent Hash72 event chain

The SQLite ledger uses WAL journaling, full synchronous commits, foreign-key enforcement, bounded busy timeout, bounded retry count, a reciprocal process lock, and `BEGIN IMMEDIATE` singleton mutation transactions.

Every admitted event includes an ordered predecessor Hash72, sequence number, event type, canonical payload, and successor Hash72. The event chain covers profile registration, sample recording, output admission, worldline admission, and checkpoint creation.

## 7. Atomic receipt-locked worldlines

A worldline batch contains one or more objects with exact four-position and four-delta coordinates. Every object must reference the same current global receipt index.

For delta `(dt, dx, dy, dz)` and configured causal rate `c`:

```text
dx^2 + dy^2 + dz^2 <= (c*dt)^2
and dt >= 0.
```

All candidates are validated before mutation. Duplicate object identities, receipt drift, causal-rate violations, or rejected target collisions abort the complete batch with no event append.

An admitted batch receives one global Hash72 and one receipt index shared by every object. Proper-time-squared witnesses are retained as exact rational values.

## 8. Projection lock

The projection-lock validator requires every projection of one equation state to carry exactly one common equation Hash72 and receipt index. Any disagreement is projection drift and is rejected.

## 9. Checkpoint and recovery

A checkpoint captures metadata, event chain, calibration profiles, calibration samples, captured receipt index, and captured root Hash72 before appending its own checkpoint event.

The checkpoint digest is recomputed during verification. Recovery is permitted only into a distinct, nonexistent database path. Recovered event count and root Hash72 must exactly match the captured values before recovery succeeds.

## 10. Callable surfaces

Iteration 2 adds:

```text
GET  /api/pass189/i2/status
GET  /api/pass189/i2/profile
POST /api/pass189/i2/calibration/profile
POST /api/pass189/i2/calibration/sample
POST /api/pass189/i2/calibration/admit
POST /api/pass189/i2/worldline/resolve
POST /api/pass189/i2/checkpoint
POST /api/pass189/i2/checkpoint/verify
GET  /api/pass189/i2/events
GET  /ws/pass189/i2
GET  /pass189/i2/.
```

The HHS Pass 189 runtime window also displays Iteration 2 receipt, calibration, worldline, and checkpoint state.

## 11. DigitalOcean authority

The existing hydration service remains on `127.0.0.1:8189`. Iteration 2 runs as a separate constrained systemd unit on `127.0.0.1:8190` and stores SQLite authority at `/var/lib/hhs-pass189/iteration2.sqlite3`.

The nginx include routes the more specific Iteration 2 paths before the general Pass 189 paths. Installation validates the full project before enabling either service. No Vercel workflow, environment variable, route, deployment, or acceptance result participates in this authority.

## 12. Validation

Dependency-scoped validation includes inherited strict C11 and 51,648,192-context validation, inherited no-float disassembly scanning, inherited hydration tests and transport smoke test, eleven Iteration 2 unit tests, float-ingress rejection, exact residual tests, profile idempotence, synthetic-versus-measured gate separation, bounded concurrent mutation, atomic causal and collision rejection, joint worldline receipt locking, projection identity locking, checkpoint verification and recovery, Iteration 2 HTTP/visual/SSE/WebSocket smoke testing, deployment shell syntax, and Python bytecode compilation.

## 13. Honest status

Iteration 2 implements the software calibration and persistence authority, but repository validation uses fixtures. It does not claim real breadboard calibration, real sensor trace acquisition, real actuator dispatch, measured physical operating-envelope closure, or `HHS_PASS_189_HQLH_UNIFIED_PHYSICS_VERIFIED`.

The valid classification remains `HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS`.

## 14. Closure

Pass 189 now supports durable exact calibration evidence, range and residual admission, bounded physical-candidate gating, atomic receipt-locked worldline resolution, persistent Hash72 sequencing, and verified checkpoint recovery on the self-hosted DigitalOcean deployment path. The remaining step toward measured unified-physics verification is real device-specific calibration and operating-envelope evidence, not additional Vercel work.
