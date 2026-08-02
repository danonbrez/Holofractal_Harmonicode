# HHS PASS 189 — ITERATION 4 DRIVER PROVENANCE, QUARANTINE, CONFORMANCE, PROMOTION, AND ROLLBACK AUTHORITY

## Authenticated package manifests, payload identity, capability confinement, evidence-class separation, dual approval, bounded admission tokens, emergency revocation, deterministic rollback, and DigitalOcean durable service

## 1. Normative metadata

| Field | Value |
|---|---|
| Parent contract | `HHS-P189-HQLH-LS41-XNOR-P1-H72-H216-UPA` |
| Iteration identifier | `HHS-P189-HQLH-ITERATION-4-DRIVER-PROVENANCE-QUARANTINE-PROMOTION` |
| Pass number | `189`, Iteration 4 |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative baseline | `main @ 1d3c7588a242e3a83304f5083c2ec5a974f19399` |
| Iteration 3 merge | `f3ceba745ce5b478ca850c14a543a18189cc7d6c` |
| Deployment authority | DigitalOcean Ubuntu, systemd, nginx, durable `/var/lib/hhs-pass189` state |
| Vercel | Non-authoritative and excluded from acceptance |
| Honest classification | `HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS` |

## 2. Purpose

Iteration 3 established a fail-closed command membrane for built-in `LOOPBACK` and sandboxed `FILE_SINK` test adapters. It intentionally prohibited external GPIO, serial, USB, network-device, and actuator drivers. Iteration 4 closes the driver-supply-chain boundary without authorizing uncontrolled hardware execution.

This iteration provides authenticated manifest ingestion, exact payload binding, quarantine, conformance evidence, dual approval, bounded admission tokens, trust-root and promotion revocation, active-package designation, and rollback.

## 3. Authentication authority

Operator keys are supplied at runtime and are never persisted. The authority stores only their SHA-256 identities. Driver manifests are authenticated with `HMAC-SHA256-OPERATOR-KEY` and rejected when the supplied verification key does not match the active trust root.

This is an operator-key authentication membrane, not a claim of public-key code signing or external certificate authority validation.

## 4. Manifest and payload identity

Every manifest carries driver identity, semantic version, driver class, confined relative entrypoint, signer identity, payload SHA-256, operations, capabilities, units, device identities, exact rational minimum and maximum, watchdog bound, interlock declarations, and creation witness.

Absolute paths and `..` traversal are rejected. The quarantined byte payload must exactly match the manifest SHA-256 before admission.

## 5. Quarantine

Every authenticated package enters `QUARANTINED`. Payload bytes are written through a unique atomic staging file into the configured quarantine directory. Package identity is sensitive to the complete canonical manifest, signature, and payload digest.

Concurrent duplicate ingestion is idempotent. Conflicting reuse of a package identity or driver-version pair is rejected.

## 6. Conformance evidence

Evidence classes are:

```text
SOFTWARE_FIXTURE
HARDWARE_IN_LOOP
```

Software evidence cannot claim a physical measurement. Hardware-in-loop evidence must explicitly identify a physical measurement and pass additional interlock, measured-return, and emergency-stop tests.

Required software tests include manifest identity, payload digest, path confinement, capability scope, range enforcement, watchdog fail-closed behavior, anti-replay, and rollback readiness.

Hardware-in-loop adds physical interlock, measured return trace, and emergency stop.

## 7. Promotion classes

Built-in software test drivers may receive:

```text
SOFTWARE_TEST_EXECUTABLE
```

Real driver classes may receive only:

```text
HARDWARE_CANDIDATE_NONEXECUTABLE
```

A hardware candidate token always retains:

```text
executable = false
real_hardware_dispatch_authorized = false
```

No package promoted by Iteration 4 can bypass Iteration 3 or load a physical driver.

## 8. Dual approval and bounded token

Promotion requires two distinct Hash72 approver identities, a conformant package, a required Hash72 issue witness, an expiry no greater than seven days, and an optional rollback package belonging to the same driver identity. Token validation checks the trust root, package state, active-driver designation, and validity window. Overdue promotions are persistently marked `EXPIRED`, removed from active designation, and recorded on the Hash72 event chain.

The admission token binds package, package Hash72, driver class, promotion class, approvals, issue witness, time window, rollback reference, and explicit hardware-dispatch denial.

## 9. Revocation and rollback

Revoking a trust root revokes every package signed by it, revokes related promotions, and removes those packages from active designation.

Promotion revocation removes the active designation and invalidates the token. Rollback atomically points the active driver identity to the declared predecessor package without loading either package.

## 10. Persistence

The SQLite authority uses WAL, full synchronous commits, foreign-key enforcement, bounded busy timeouts, bounded retries, reciprocal process locking, and `BEGIN IMMEDIATE` singleton mutation.

Trust roots, packages, conformance runs, promotions, expirations, revocations, rollbacks, and checkpoints append one ordered Hash72 event each.

## 11. Callable surfaces

```text
GET  /api/pass189/i4/status
GET  /api/pass189/i4/package
POST /api/pass189/i4/trust/register
POST /api/pass189/i4/trust/revoke
POST /api/pass189/i4/package/sign
POST /api/pass189/i4/package/ingest
POST /api/pass189/i4/conformance
POST /api/pass189/i4/promote
POST /api/pass189/i4/promotion/validate
POST /api/pass189/i4/promotion/sweep
POST /api/pass189/i4/promotion/revoke
POST /api/pass189/i4/rollback
POST /api/pass189/i4/chain/verify
POST /api/pass189/i4/checkpoint
POST /api/pass189/i4/checkpoint/verify
GET  /api/pass189/i4/events
GET  /ws/pass189/i4
GET  /pass189/i4/.
```

## 12. DigitalOcean authority

```text
Iteration 1 hydration        127.0.0.1:8189
Iteration 2 calibration      127.0.0.1:8190
Iteration 3 adapters         127.0.0.1:8191
Iteration 4 provenance       127.0.0.1:8192
```

Iteration 4 stores authority at `/var/lib/hhs-pass189/iteration4.sqlite3` and quarantine payloads under `/var/lib/hhs-pass189/iteration4-quarantine`. The authoritative systemd service runs the token-lifecycle overlay, which migrates existing Iteration 4 databases in place while preserving the pre-lifecycle package and event history.

## 13. Validation

Validation includes all inherited Pass 189 native and Python authority, sixteen Iteration 4 unit tests (twelve provenance tests plus four token-lifecycle tests), signature mismatch rejection, payload-digest binding, path traversal rejection, concurrent quarantine idempotence, evidence-class separation, dual approval, required issue-witness validation, bounded token validation and persistent expiry, hardware-candidate non-execution, trust-root cascade revocation, rollback, event-chain verification, checkpoint recovery, HTTP, visual, SSE, WebSocket, Python bytecode, and deployment shell syntax.

## 14. Honest boundary

Iteration 4 verifies the software provenance, quarantine, and promotion-token lifecycle membrane. Repository hardware-in-loop tests use explicit fixtures only where stated; no external laboratory run is asserted. No GPIO, serial, USB, network-device, actuator, kernel module, or userspace hardware driver is loaded or executed.

The classification remains `HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS`. `HHS_PASS_189_HQLH_UNIFIED_PHYSICS_VERIFIED` is not claimed.
