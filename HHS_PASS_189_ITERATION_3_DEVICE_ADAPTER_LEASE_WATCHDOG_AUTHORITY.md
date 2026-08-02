# HHS PASS 189 — ITERATION 3 DEVICE ADAPTER, LEASE, ANTI-REPLAY, AND WATCHDOG AUTHORITY

## Exact command envelopes, bounded operator leases, fail-closed test adapters, deterministic software traces, emergency revocation, checkpoint recovery, and DigitalOcean durable service

## 1. Normative metadata

| Field | Value |
|---|---|
| Parent contract | `HHS-P189-HQLH-LS41-XNOR-P1-H72-H216-UPA` |
| Iteration identifier | `HHS-P189-HQLH-ITERATION-3-DEVICE-ADAPTER-LEASE-WATCHDOG` |
| Pass number | `189`, Iteration 3 |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative baseline | `main @ 5178787599dc02c477cc8160eee0e39047437660` |
| Iteration 2 merge | `c3cc477cd1b573eb5a318c7f38a1197e428d7014` |
| Deployment authority | Existing DigitalOcean Ubuntu host, systemd, nginx, durable `/var/lib/hhs-pass189` state |
| Vercel | Non-authoritative and excluded from acceptance |
| Arithmetic authority | Exact integers and rational numerator/denominator pairs; floats rejected from canonical ingress |
| Honest classification | `HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS` |

## 2. Purpose

Iteration 2 can admit a bounded physical candidate but intentionally emits `CANDIDATE_ONLY_NO_DEVICE_DRIVER`. Iteration 3 closes the next software boundary by defining adapter identity, lease authority, canonical command envelopes, anti-replay sequencing, watchdog expiry, emergency revocation, software execution traces, and durable recovery.

This iteration does **not** implement uncontrolled physical output. Only these test drivers execute:

```text
LOOPBACK
FILE_SINK
```

The following driver classes remain forbidden:

```text
GPIO
SERIAL
USB
NETWORK_DEVICE
ACTUATOR
```

## 3. Adapter authority

Every adapter records adapter and device identity, driver kind, unit, exact minimum and maximum, allowed operations, watchdog timeout, maximum commands per lease, software attestation, enabled state, sandboxed sink directory, created-nanosecond witness, and adapter Hash72.

Adapter identity is canonical-payload-sensitive. Re-registering the same identity with different content is rejected.

## 4. Operator lease authority

A lease records adapter identity, issue and expiry witnesses, bounded command count, allowed operation subset, operator-arm Hash72, status, and lease Hash72.

Lease duration is bounded to twenty-four hours. Command count cannot exceed the adapter limit. Revocation invalidates every prepared command under the lease.

## 5. Command envelope and anti-replay

A command envelope retains command, adapter, and lease identities; adapter-local sequence; operation; exact rational value; unit; issue time; watchdog deadline; Iteration 2 candidate identity; profile identity; candidate receipt index; and command Hash72.

A command requires an Iteration 2 candidate with:

```text
physical_output_authorized = true
dispatch_class = CANDIDATE_ONLY_NO_DEVICE_DRIVER.
```

`command_id` is globally unique and `(adapter_id, sequence)` is unique. Replays and reordered duplicates are rejected.

## 6. Watchdog and fail-closed execution

Prepared commands must execute before their watchdog deadline and lease expiry. Expired commands are persistently classified `EXPIRED` and receive a Hash72 event. Disabled adapters, revoked leases, exhausted budgets, unit mismatches, range violations, and arm-token mismatches cannot execute.

Emergency adapter disable also revokes active leases and prepared commands.

## 7. Software trace authority

`LOOPBACK` returns the requested exact rational value. `FILE_SINK` writes one atomic JSON trace per command inside the configured state directory. Both produce:

```text
SOFTWARE_LOOPBACK_TRACE
hardware_measurement = false
physical_claim = false
dispatch_status = SOFTWARE_TEST_DRIVER_ONLY.
```

Software traces cannot be promoted to `MEASURED_HARDWARE` evidence.

## 8. Persistence and replay

The SQLite ledger uses WAL, full synchronous commits, foreign-key enforcement, bounded busy timeout, bounded retries, a process lock, and `BEGIN IMMEDIATE` singleton mutation.

Every adapter, lease, command, trace, revocation, expiry, and checkpoint transition appends one ordered Hash72 event. Event-chain verification recomputes sequence, predecessor, and successor identity.

## 9. Checkpoint recovery

Iteration 3 checkpoints use SQLite backup, SHA-256 file integrity, captured sequence, and captured root Hash72. Recovery is allowed only to a distinct nonexistent destination after verification.

## 10. Callable surfaces

```text
GET  /api/pass189/i3/status
GET  /api/pass189/i3/adapter
GET  /api/pass189/i3/command
POST /api/pass189/i3/adapter/register
POST /api/pass189/i3/adapter/enable
POST /api/pass189/i3/lease/issue
POST /api/pass189/i3/lease/revoke
POST /api/pass189/i3/command/prepare
POST /api/pass189/i3/command/execute
POST /api/pass189/i3/watchdog/sweep
POST /api/pass189/i3/checkpoint
POST /api/pass189/i3/checkpoint/verify
POST /api/pass189/i3/chain/verify
GET  /api/pass189/i3/events
GET  /ws/pass189/i3
GET  /pass189/i3/.
```

## 11. DigitalOcean authority

The services remain separated:

```text
Iteration 1 hydration       127.0.0.1:8189
Iteration 2 calibration     127.0.0.1:8190
Iteration 3 adapters        127.0.0.1:8191
```

Iteration 3 persists at `/var/lib/hhs-pass189/iteration3.sqlite3` and `/var/lib/hhs-pass189/iteration3/`. Specific Iteration 3 nginx routes precede Iteration 2 and general Pass 189 routes.

## 12. Validation

Validation includes inherited strict C11 and 51,648,192-context authority, inherited no-float disassembly scanning, Iterations 1 and 2 tests and surfaces, eleven Iteration 3 unit tests, forbidden-driver and float-ingress rejection, adapter payload sensitivity, bounded leases, operator-arm validation, candidate-gate validation, anti-replay concurrency, watchdog persistence, revoke/disable handling, loopback and sandboxed file traces, event-chain verification, checkpoint recovery, HTTP/visual/SSE/WebSocket smoke tests, deployment shell syntax, and Python bytecode compilation.

## 13. Honest status

Iteration 3 proves the fail-closed software adapter authority. It does not claim real hardware calibration, real sensor return traces, GPIO/serial/USB/network/actuator dispatch, live operating-envelope acceptance, or `HHS_PASS_189_HQLH_UNIFIED_PHYSICS_VERIFIED`.

The classification remains `HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS`.

## 14. Closure

Pass 189 now carries exact hydration, persistent calibration, atomic causal batches, and a bounded device-command membrane. The remaining path to measured unified-physics verification requires device-specific drivers, real instrument traces, hardware safety interlocks, and measured operating-envelope evidence—not Vercel work.
