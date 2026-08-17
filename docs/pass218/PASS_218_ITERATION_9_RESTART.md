# Pass 218 Full Implementation — Iteration 9 Restart State

## Authority

- Pass: 218 — native corpus / relational curriculum / narrative hydration.
- Iteration: 9 — multi-process canonical ownership and fencing.
- Base validated Iteration-8 head: `af81e25d73d9ed68ee0e63b0741ff35c1c83dd5f`.
- Branch: `agent/pass218-full-iteration9-multiprocess-canonical-ownership`.
- Merge target: `main`.
- Main observed during Iteration 9: `b0656a92ab29507f81eae760e070f74e49db83f4`.
- Validated implementation/evidence head before this restart record: `7d6bc3dd521c8c98b00e48342402baca0d09608c`.
- Pass 218 remains **IN DEVELOPMENT**; this record freezes Iteration 9 only.

## Implemented surface

Iteration 9 replaces the Iteration-8 single-process writer assumption with a process-shared canonical ownership membrane for workers that share one lock-coherent POSIX filesystem.

Canonical ownership sequence:

```text
Runtime-OS process starts
        ↓
Pass-218 ingestion CLOSED
        ↓
try POSIX exclusive flock on ownership.lock
        ↓
  ┌──── acquired ────────────────┐
  │                              │
advance durable fencing epoch    lock busy
Hash72-seal ownership.json       ↓
  │                         OWNERSHIP_STANDBY
  ↓                              ↓
validate current fence           ingestion CLOSED
  ↓                              diagnostics only
I8 startup/restore
  ↓
I7 durable target validation
  ↓
PRIMARY + ingestion OPEN
  ↓
I5 authorization → I6 commit → I7 checkpoint
  ↓
clean shutdown/checkpoint
  ↓
release kernel flock
  ↓
next process may acquire → fence epoch + 1 → restore exact durable target
```

The kernel lock is the live ownership lease. The durable integer `fence_epoch` is the takeover/CAS witness. No wall-clock lease expiry and no floating-point time participate in canonical authority.

A process can perform Pass-218 canonical activity only while both conditions hold:

1. it still owns the kernel-held exclusive flock; and
2. its locally retained owner/fence/hash tuple exactly matches the current Hash72-sealed `ownership.json` record.

A process that does not own the fence remains `OWNERSHIP_STANDBY`; it can expose diagnostics but cannot open ingestion, construct the canonical commit boundary, or checkpoint canonical state.

## Ownership record

New durable record: `ownership.json`.

Schema:

`HHS-P218-I9-CANONICAL-OWNERSHIP-RECORD-V1`

It records:

- current integer fence epoch;
- current owner identity;
- immediately previous owner identity;
- immediately previous fence epoch;
- lock strategy `POSIX_FLOCK_EXCLUSIVE`;
- authority scope `LOCK_COHERENT_POSIX_FILESYSTEM`;
- Hash72 seal over the complete canonical ownership payload;
- explicit false flags for learning, truth, action, source retention, and Pass-165 source-retaining activity.

The first owner obtains epoch 1. Every successful later takeover obtains exactly previous epoch + 1. A stale unlocked record is therefore not treated as a live lease; acquiring the kernel lock advances the fence before canonical restore begins.

## Process-death recovery

Iteration-9 tests use a separate spawned process to acquire and hold the real flock. A concurrent process cannot acquire writer authority while that process is alive. After the holder process is forcibly terminated, the kernel releases the flock and a replacement process acquires epoch 2.

This proves crash recovery without a timeout heuristic or wall-clock expiry. The new process still must validate the durable ownership chain and Iteration-7 canonical generation before ingestion opens.

## Runtime-OS integration

`hhs_backend/runtime_os_pass218_lifecycle.py` now installs `Pass218MultiprocessRuntimeLifecycle` while preserving the same Runtime-OS app-state owner and diagnostic route introduced in Iteration 8.

The service lifecycle still wraps the inherited FastAPI lifespan rather than replacing it. The ownership membrane is therefore upstream of the Iteration-8 restore/ingestion lifecycle but downstream of the already established Runtime-OS application composition.

The diagnostic endpoint remains:

`GET` / `HEAD /api/runtime/pass218/lifecycle/status`

It now includes ownership state, lock-held state, owner identity, fence epoch, ownership Hash72, ownership scope, and `split_brain_writer_permitted=false`.

No public canonical mutation endpoint is introduced.

## Changed files

- `hhs_runtime/pass218/ownership.py`
- `hhs_runtime/pass218/lifecycle_i9.py`
- `hhs_runtime/pass218/__init__.py`
- `hhs_backend/runtime_os_pass218_lifecycle.py`
- `tests/pass218/test_pass218_iteration9_multiprocess_canonical_ownership.py`
- `tools/pass218_iteration9_evidence.py`
- `.github/workflows/pass218-full-iteration9.yml`
- `docs/pass218/PASS_218_ITERATION_9_RESTART.md`

## Iteration-9 tests

The dedicated Iteration-9 suite contains 15 tests covering:

- public ownership/version contract;
- first acquisition at fence epoch 1;
- concurrent contender rejected while primary owns the flock;
- takeover increments the fence and links the previous owner;
- stale unlocked ownership record recovery;
- tampered ownership record rejection;
- real separate-process kernel-lock release after forced process termination;
- Runtime-OS primary versus standby behavior;
- standby inability to construct canonical commit authority;
- takeover exact canonical root, VM81 snapshot, and consumed I6 receipt;
- released stale lifecycle unable to resume writes;
- non-owner checkpoint rejection;
- Runtime-OS installer binding the Iteration-9 lifecycle;
- status exclusion of learning/truth/action/source authority;
- no authoritative float literals in Iteration-9 authority surfaces.

## Validation completed before restart record

Dedicated `Pass 218 Full Iteration 9` run `31660063705` completed successfully on exact implementation/evidence head `7d6bc3dd521c8c98b00e48342402baca0d09608c`.

- cumulative Pass-218 + Runtime-OS compilation: PASS
- no-authoritative-float AST gate: PASS
- Iteration 1: 12 passed
- Iteration 2: 13 passed
- Iteration 3: 12 passed
- Iteration 4: 14 passed
- Iteration 5: 18 passed
- Iteration 6: 19 passed
- Iteration 7: 21 passed
- Iteration 8: 23 passed
- Iteration 9: 15 passed
- repository-native crawler: 14 passed
- Runtime-OS production-root acceptance: 6 passed
- repository-native Iteration-9 ownership evidence: PASS

The initial Iteration-9 evidence run failed only because the script queried `ownership.json` for the epoch-2 previous owner after the later epoch-3 contender had already advanced the record. The evidence was repaired to freeze the epoch-2 record immediately after takeover. No ownership or Runtime-OS implementation semantics changed in that repair.

## Repository-native evidence

Workload: `creative_writing/novels/THE_SMALLEST_PERMISSION.md`.

- source SHA-256: `42caa64e6d75aeeedb256f8e9c72b773ab9e5e230bcbc63e76bdff59fae37c03`
- structural narrative beats: 61
- transaction ID Hash72: `9ckHe3R(Hr<W0gU9MA5jYr/UdZCcHHXjY/LZyksp3D>OICUnbFAU<Q-Tw1r/piFmdaZb5D!+`
- candidate entry ID: `2cb8dffce47850123f6f6878ce8e4c107670e493c4d681963d1fde0051fa2eae`
- VM5184 projection SHA-256: `7496cdb5047f7609397ba06adbc0e9c303efd4d9240f9b6a6198164df70b2baa`
- checkpoint SHA-256: `adc749e9820621a6f6c962efc12006d0c180153e727dae96f666ef46487284db`
- canonical root Hash72: `+)XvAsp(/Q516-Tp-cl+3MAYmPYp4y7?CMoX8p8j4pF8)D>DU!zYC>lyAhuMR6uHq6zQONNu`
- primary startup state: `EMPTY_READY`
- primary ownership state: `PRIMARY`
- primary fence epoch: 1
- concurrent standby state: `OWNERSHIP_STANDBY`
- standby ingestion enabled: false
- standby writer authority: false
- standby canonical boundary blocked: true
- first takeover state: `RESTORED_READY`
- first takeover fence epoch: 2
- first takeover previous owner: `iteration9-primary`
- first takeover canonical root equality: true
- first takeover VM81 snapshot equality: true
- first takeover consumed I6 receipt equality: true
- takeover new authorization minted: false
- takeover new canonical mutation invoked: false
- third contender remains standby while epoch-2 owner is live: true
- second takeover state after epoch-2 owner releases: `RESTORED_READY`
- second takeover fence epoch: 3
- second takeover canonical root equality: true
- split-brain writer permitted: false
- source text present in persisted canonical/ownership authority: false
- Pass-165 source-retaining path invoked: false
- canonical learning commit invoked: false
- truth promotion: false
- action authority minted: false
- verbatim source retained: false

## Restart instructions

1. Verify branch head before editing.
2. Preserve Iteration-6 receipt bytes and the Iteration-7 compatibility membrane.
3. Do not bypass `Pass218MultiprocessRuntimeLifecycle` for process-shared Runtime-OS canonical activity.
4. Do not open Pass-218 ingestion in a standby/non-owner process.
5. Revalidate the live ownership fence before canonical boundary construction and durable checkpoint activity.
6. Preserve the Iteration-8 rule that a successful I6 mutation whose I7 checkpoint fails remains real while ingress stays closed until the same target becomes durable.
7. Preserve source purge and the explicit exclusion of Pass-165 source-retaining learning.
8. Rerun dependency-scoped Iteration-9 validation and the inherited merge-candidate integration gate after any change to ownership, lifecycle, persistence, or Runtime-OS composition.

## Scope limitation / next boundary

Iteration 9 proves **multi-process writer exclusion and takeover only for processes sharing one lock-coherent POSIX filesystem**. It does not claim that `fcntl.flock` is a distributed consensus protocol and does not infer cross-host safety from a shared path whose locking semantics are unknown.

A subsequent iteration may generalize the exact same fencing contract to horizontally replicated hosts by adding an explicit distributed lease/CAS authority with a consensus-backed monotonically increasing fence. That future layer must preserve the Iteration-9 owner/fence semantics while replacing only the live-lock transport; it must not weaken I3-I8 purge, authorization, atomic commit, durability, or restart invariants.
