# HHS PASS 190 ITERATION 4 — DISTRIBUTED SINGLETON FENCED AUTHORITY

## 1. Metadata

| Field | Value |
|---|---|
| Contract | `HHS-P190-I4-DSFA-LEASE-FENCE-VM81-H72-H216` |
| Parent contract | `HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216` |
| Iteration | `4` |
| Baseline | `main @ a38f38f3a8036a76353b7b65453a84a54703460c` |
| Classification | `HHS_PASS_190_ITERATION_4_DISTRIBUTED_SINGLETON_FENCED_AUTHORITY_VERIFIED` |
| Full Pass 190 completion | Not claimed |

## 2. Purpose

Iterations 1–3 established the operation registry, persistent receipts and events, native ABI/compiler projection, signed remote capabilities, and fail-closed database validation. They still allowed two operating-system processes to construct candidates from separate in-memory snapshots.

Iteration 4 makes the singleton VM81 admission membrane durable across processes:

```text
process candidate
→ acquire durable SQLite lease
→ receive monotonic fencing token
→ begin exclusive admission transaction
→ refresh exact durable state
→ resolve operation through inherited registry/compiler
→ validate predecessor, index, state, and token
→ commit receipt + event + fence witness atomically
→ release lease
```

No process-local snapshot may commit merely because it was valid when that process started.

## 3. Durable singleton lease

The canonical lease identity is:

```text
pass190.singleton.vm81
```

The `authority_lease` table stores:

- holder identity;
- monotonically increasing fencing token;
- exact integer acquisition time;
- exact integer expiration time;
- exact integer release time.

Lease acquisition uses `BEGIN IMMEDIATE` so acquisition is serialized by SQLite before a candidate is admitted. The lease is committed before operation execution. Therefore a process crash leaves a bounded durable lease rather than an ambiguous private lock. Another process may take over only after expiration or explicit release.

Lease acquisition has bounded wait behavior and returns a typed `LeaseBusyError` when another live holder remains authoritative.

## 4. Fencing authority

Each granted admission receives:

```text
F_n ∈ ℕ,  F_{n+1} > F_n
```

A candidate must prove immediately before commit that:

```text
holder_db = holder_candidate
∧ fence_db = fence_candidate
∧ lease_expiry > commit_time
∧ released = false
```

A superseded or expired candidate raises `StaleFenceError` and cannot write a receipt, event, state root, or idempotency record.

Failed acquisitions may consume fencing tokens. Therefore committed tokens are strictly increasing but need not be contiguous.

## 5. Transactional refresh and stale-candidate rejection

After acquiring the lease, every invocation begins a second `BEGIN IMMEDIATE` admission transaction and reloads:

- all verified receipts;
- durable chain head;
- current state and state root;
- idempotency bindings;
- event topology;
- fencing witnesses.

Only then is the inherited `HHSAuthorityContext` invoked.

Before commit, the candidate must satisfy:

```text
candidate.predecessor_hash72 = durable.last_hash72
candidate.receipt_index = durable.receipt_count + 1
candidate.state_before = refreshed durable state root
```

This prevents a stale process from appending a locally valid but globally divergent receipt.

Expected-state preconditions are evaluated after distributed refresh, not against the process startup snapshot.

## 6. Fence witnesses

Every committed receipt has exactly one row in `authority_fences` containing:

- receipt Hash72;
- receipt index;
- holder identity;
- fencing token;
- acquisition, commit, and expiration times;
- predecessor Hash72;
- state-before and state-after roots;
- migration classification;
- fence Hash72.

The canonical witness is:

```text
H_fence = Hash72(
  receipt_hash72,
  receipt_index,
  holder_id,
  fencing_token,
  acquired_ns,
  committed_ns,
  expires_ns,
  predecessor_hash72,
  state_before,
  state_after,
  migration_class
)
```

Integrity validation requires:

```text
number of fences = number of receipts
strictly increasing committed fencing tokens
receipt/fence index equality
receipt/fence predecessor equality
receipt/fence state topology equality
valid fence Hash72
```

## 7. Iteration 3 migration

Existing Iteration 3 receipts remain authoritative. On first Iteration 4 opening, each historical receipt receives a deterministic migration fence:

```text
holder_id = iteration3-migration
fencing_token = receipt_index
legacy_migration = true
```

No receipt payload or existing Hash72/Hash216 identity is rewritten. The new witness is an additive outer authority record.

## 8. Replay and idempotency

Replay event writes are also fenced and serialized. Replay does not create a new operation receipt, but its event is admitted under a live fencing token.

Idempotency lookup occurs after distributed refresh. Reusing a valid idempotency key returns the existing receipt without creating another receipt or fence. Reusing the key with a different request remains rejected.

## 9. HTTP, OpenAPI, SDK, and GUI projection

Iteration 4 preserves every Iteration 3 route and adds:

```text
GET /api/pass190/arbitration
```

The response exposes:

- singleton key;
- active/released lease state;
- active holder when present;
- latest fencing token;
- expiration time when active;
- fence count;
- highest committed fence.

OpenAPI now reports Iteration 4 and the arbitration route. Python and TypeScript SDKs expose `arbitration()`.

The visual authority displays receipt count, event count, fence count, highest committed fence, active lease state, current holder, metadata integrity, event integrity, distributed-singleton verification, chain head, state root, and fencing tokens carried by live events.

## 10. Deployment

The production systemd unit starts:

```text
server/hhs_pass190_iteration4_server.py
```

against the inherited database:

```text
/var/lib/hhs/pass190-authority.sqlite3
```

Deployment verification requires:

- health receipt admission;
- complete persistent integrity;
- distributed-singleton verification;
- released lease after request completion;
- one fence witness per receipt;
- inherited native ABI manifest;
- inherited compiler routes;
- Iteration 4 OpenAPI identity.

## 11. Validation

The Iteration 4 gate adds eight tests covering:

1. two independent contexts refreshing before admission;
2. bounded lease contention;
3. expired-lease takeover and stale-fence rejection;
4. deterministic Iteration 3 fence migration;
5. fence-witness tamper rejection;
6. expected-state validation after distributed refresh;
7. two separate Python processes sharing one receipt/state chain;
8. live Iteration 4 server arbitration and OpenAPI projection.

All inherited native ABI, Iterations 1–3, authentication, persistence, replay, SDK, GUI, deployment, no-private-evaluation, and no-float checks remain binding.

## 12. Remaining Pass 190 work

Iteration 4 closes single-host multi-process mutation arbitration. It does not claim a distributed database consensus protocol across independent hosts.

Still open:

- repository-wide hydration of every public operation;
- complete Python built-in and standard-library compatibility;
- broader native ABI value profiles;
- migration of all legacy API routes, GUI actions, and workflows;
- complete compiler lowering across inherited surfaces;
- complete job, workspace, artifact, provider, and capability registries;
- multi-host consensus when the authoritative database is no longer single-host;
- live DigitalOcean installation and production acceptance;
- final Pass 190 completion classification.
