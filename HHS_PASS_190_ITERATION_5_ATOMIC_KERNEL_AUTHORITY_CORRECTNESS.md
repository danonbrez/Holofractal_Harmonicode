# HHS PASS 190 ITERATION 5 — ATOMIC KERNEL-AUTHORITY CORRECTNESS

## 1. Metadata

| Field | Value |
|---|---|
| Contract | `HHS-P190-I5-AKAC-LEASE-RECEIPT-FENCE-VM81-H72-H216` |
| Parent | `HHS-P190-I4-DSFA-LEASE-FENCE-VM81-H72-H216` |
| Iteration | `5` |
| Baseline | `main @ 3e97fc0cabcbadd1c713fdaf79e27bb4841ea283` |
| Classification | `HHS_PASS_190_ITERATION_5_ATOMIC_KERNEL_AUTHORITY_CORRECTNESS_VERIFIED` |
| Full Pass 190 completion | Not claimed |

## 2. Purpose

Iteration 4 established single-host multi-process lease and fencing authority. Iteration 5 repairs correctness gaps that could still weaken that authority under lock contention, migration, observation, or deployment verification.

The authoritative path becomes:

```text
bounded SQLite lock acquisition
→ Hash72 lease ACQUIRED receipt
→ atomic durable snapshot validation
→ inherited registry/compiler evaluation
→ kernel-authority fence witness
→ operation receipt and event commit
→ Hash72 RELEASED / FAILED_RELEASED / EXPIRED receipt
→ refreshed arbitration projection
```

## 3. Bounded lock contention

SQLite's connection-level busy timeout must not silently exceed the Pass 190 lease-wait contract.

The production runtime uses short lock slices and retries until the declared monotonic deadline. A lock that clears within the wait is retried successfully. A lock that remains past the deadline returns typed `LeaseBusyError`, never a raw `sqlite3.OperationalError`.

```text
slice <= 25 ms
Σ slices <= configured lease wait + one bounded slice
```

## 4. Atomic restore validation

State restoration and validation now occur in one SQLite read transaction unless already inside the exclusive admission transaction.

The snapshot includes:

- receipts and their Hash72/Hash216 identities;
- authority metadata and state root;
- idempotency references;
- admitted and replayed events;
- lease-transition receipts;
- fence witnesses;
- kernel-authority bindings.

No concurrent commit may be observed halfway through restoration.

## 5. Validate before migration

Iteration 5 does not create migration fences for untrusted legacy data.

The order is binding:

```text
validate inherited receipt chain
→ validate metadata and state topology
→ validate inherited events
→ validate existing Iteration 4 fences
→ add missing migration witnesses
→ extend witnesses with kernel authority
```

A tampered Iteration 2, 3, or 4 database fails before any receipt receives a new authority witness.

## 6. Lease-transition receipt chain

Every observed lease transition has a canonical Hash72 receipt:

```text
MIGRATED
ACQUIRED
RELEASED
FAILED_RELEASED
EXPIRED
```

Each receipt contains:

- singleton key;
- transition type;
- holder identity;
- fencing token;
- observed, acquired, expiration, and release times;
- predecessor lease-receipt Hash72.

The chain requires continuous sequence numbers, exact predecessor continuity, valid Hash72 identity, and a valid per-token transition state machine.

A runtime token begins with `ACQUIRED` and has at most one terminal transition. Historical tokens may be represented by one deterministic `MIGRATED` receipt.

## 7. Expiration settlement

Expired unreleased leases are settled transactionally when arbitration is refreshed or a new holder attempts acquisition.

Settlement emits `EXPIRED`, marks the durable lease released, and prevents the old grant from passing kernel verification. A replacement token must be greater than every fence and lease-transition token already recorded.

## 8. Kernel-authority fence witness

Every operation fence now binds the operation receipt to the lease acquisition receipt that authorized it.

```text
H_kernel = Hash72(
  receipt Hash72,
  receipt index,
  fence Hash72,
  lease ACQUIRED receipt Hash72,
  holder identity,
  fencing token,
  predecessor Hash72,
  state-before root,
  state-after root
)
```

The fence ledger stores:

- `lease_acquire_hash72`;
- `kernel_authority_hash72`.

Validation requires the referenced lease receipt to exist and to carry the same holder and fencing token. Admitted events must carry the same fence, lease-acquisition, and kernel-authority identities.

Replay events receive a separate kernel event witness tied to their lease acquisition receipt.

## 9. Arbitration refresh

`GET /api/pass190/arbitration` refreshes expired state before returning a transactionally consistent report.

The report includes:

- `active`;
- `lease_state` (`absent`, `active`, or `released` after refresh);
- current holder when active;
- fencing token;
- fence count and highest committed fence;
- lease-transition count;
- last transition and its Hash72;
- lease-receipt-chain verification.

An active lease is a valid operating condition, not a deployment failure.

## 10. HTTP, SDK, and GUI

Iteration 5 adds:

```text
GET /api/pass190/lease-receipts?after=<sequence>&limit=<count>
```

Python exposes `lease_receipts()`. TypeScript exposes `leaseReceipts()`.

The GUI refreshes integrity and arbitration every two seconds and after live receipt events. It displays atomic snapshot status, transition count, last transition, lease state, lease-receipt verification, kernel-authority verification, and kernel Hash72 identities.

Custom Iteration 5 GET routes preserve structured errors:

```json
{
  "error": "persistent_authority_unavailable",
  "message": "..."
}
```

with HTTP `503` for persistence, locking, and operating-system authority failures.

## 11. Deployment verification

Production starts:

```text
server/hhs_pass190_iteration5_server.py
```

Deployment verification requires:

- inherited operation health;
- complete metadata and event validation;
- distributed singleton verification;
- atomic snapshot verification;
- lease-transition receipt verification;
- kernel-authority verification;
- one operation fence per operation receipt;
- Iteration 5 OpenAPI and lease-receipt routes;
- native ABI and compiler route preservation.

A live active lease is accepted when it has a holder, future expiry, and last transition `ACQUIRED`. An inactive authority must be `absent` or `released`.

## 12. Validation

Iteration 5 adds tests for:

1. ACQUIRED and RELEASED receipt production;
2. kernel fence and event witness equality;
3. FAILED_RELEASED after rejected candidates;
4. SQLite lock retry followed by successful admission;
5. typed bounded lock timeout;
6. receipt validation before migration;
7. additive Iteration 4 migration;
8. expiration receipt and stale-grant rejection;
9. atomic restoration transaction ordering;
10. valid active-lease arbitration;
11. structured `503` on custom routes;
12. live lease-receipt and OpenAPI projection;
13. production lock-slice deadline enforcement.

All inherited Iterations 1–4 tests, native C11 tests, SDK and binding parity, GUI/deployment verification, no-private-evaluation checks, and no-float authority checks remain binding.

## 13. Remaining Pass 190 work

Iteration 5 closes the identified single-host authority correctness defects. It does not claim multi-host consensus.

Still open:

- repository-wide operation hydration;
- complete Python built-in and standard-library compatibility;
- broader native ABI value profiles;
- migration of legacy routes, GUI actions, and workflows;
- full compiler lowering across inherited surfaces;
- complete job, workspace, artifact, provider, and capability registries;
- multi-host consensus if authority moves beyond one SQLite host;
- live DigitalOcean installation and production acceptance;
- final Pass 190 completion classification.
