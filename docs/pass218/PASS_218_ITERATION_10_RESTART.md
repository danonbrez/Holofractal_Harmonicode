# Pass 218 Iteration 10 Restart Record

## Identity

- Pass: 218
- Iteration: 10 — distributed / cross-host canonical ownership
- Branch: `agent/pass218-full-iteration10-distributed-canonical-ownership`
- Base / inherited Iteration-9 validated head: `42cc8ec4b4806221dd271c9429a16a0dd8650b57`
- Merge target: `main`
- Status at this checkpoint: implementation present; Iteration-10 validation pending

## Inherited authority

Iteration 10 is append-only over the validated Iteration-9 boundary:

1. Iterations 1–3 preserve Genesis/curriculum, grammar/narrative hydration, source transaction closure, and source purge.
2. Iterations 4–6 preserve candidate staging, explicit promotion authority, and the atomic Pass-217/VM81 canonical commit boundary.
3. Iteration 7 preserves sealed durable I7 canonical checkpoints and exact restart reconstruction.
4. Iteration 8 preserves Runtime-OS lifecycle gating and restart behavior.
5. Iteration 9 remains the per-host process exclusion layer: one writer on one lock-coherent POSIX filesystem using a kernel-held `flock` and monotonically increasing local Hash72-sealed fence.

Iteration 10 does not reinterpret or replace those layers. A distributed writer must hold both the local Iteration-9 fence and the Iteration-10 distributed fence.

## Implemented Iteration-10 surfaces

- `hhs_runtime/pass218/distributed_ownership.py`
  - production etcd v3 JSON-gateway client
  - lease-bound ephemeral owner key
  - durable globally monotonic integer fence
  - durable last-owner witness
  - Hash72-sealed distributed ownership record
  - exact owner/fence linearizable compare-and-swap validation
  - lease renewal and explicit stale-owner rejection
  - Hash72-sealed distributed canonical checkpoint containing the validated I7 checkpoint
  - exact distributed checkpoint predecessor CAS
  - cross-host target reconstruction from the distributed I7 checkpoint
  - deterministic in-memory consensus harness for injected unit tests only
  - fail-closed unconfigured authority
- `hhs_runtime/pass218/lifecycle_i10.py`
  - local-I9 + distributed-I10 dual-fence Runtime-OS lifecycle
  - distributed standby / primary / lease-loss states
  - cross-host restore into an unrelated local I7 store
  - local I9 state bootstrap into distributed authority only when no distributed checkpoint exists
  - distributed checkpoint publication after inherited I6/I7 commit
  - rollback to the last distributed checkpoint if global publication fails
  - source/learning/truth/action authority exclusion
- `hhs_runtime/pass218/__init__.py`
  - lazy public exports for Iteration 10
- `hhs_runtime/pass218/lifecycle_i9.py`
  - compatibility repair so Iteration-10 status narrowing cannot make a healthy Iteration-9 local restore appear failed during composed startup
- `hhs_backend/runtime_os_pass218_lifecycle.py`
  - existing single-host deployment remains on I9 when distributed mode is not configured
  - `HHS_PASS218_ETCD_ENDPOINT` mounts I10
  - `HHS_PASS218_DISTRIBUTED_REQUIRED=1` requires I10 and fails closed if no valid backend exists
  - distributed configuration errors never silently fall back to local-only writer authority
  - Runtime-OS lifespan keepalive for active I10 lease
- `tests/pass218/test_pass218_iteration10_distributed_canonical_ownership.py`
  - deterministic dual-host, partition, lease-loss, stale-owner, rollback, retry, tamper, bootstrap, source-exclusion, Runtime-OS selection, and real-etcd tests
- `tools/pass218_iteration10_evidence.py`
  - repository-native real-etcd cross-host evidence using `creative_writing/novels/THE_SMALLEST_PERMISSION.md`
- `.github/workflows/pass218-full-iteration10.yml`
  - real etcd v3 service gate plus cumulative I1–I10 validation

## Distributed authority contract

Production consensus backend: `ETCD_V3`.

Authority scope: `ETCD_V3_LINEARIZABLE_LEASE_CAS`.

The authoritative etcd namespace contains:

- `owner` — lease-bound ephemeral exact ownership record
- `fence` — durable globally monotonic positive integer fencing epoch
- `last-owner` — durable exact predecessor ownership record
- `checkpoint` — durable Hash72-sealed wrapper around the validated I7 canonical checkpoint

Acquisition is a single etcd transaction comparing:

- no live `owner`,
- the exact prior `fence`, and
- the exact prior `last-owner`,

then writing the next fence, last-owner witness, and lease-bound owner record atomically.

Canonical publication is a separate etcd transaction comparing:

- the exact current lease-bound owner record,
- the exact current global fence, and
- the exact prior distributed checkpoint value/version,

then replacing the distributed checkpoint atomically.

A transport failure, quorum-unavailable response, lease expiry, owner mismatch, fence mismatch, or checkpoint CAS mismatch removes effective writer authority. There is no wall-clock lease-expiry judgment inside HHS; the consensus backend decides lease validity.

## Cross-host recovery contract

A replacement host may have an unrelated/empty local filesystem. After acquiring:

1. its local I9 process fence,
2. the next distributed I10 fence,

it validates the distributed checkpoint, reconstructs the exact Pass-217/VM81 target using the inherited I7 restore path, then writes that validated state to its own local I7 store before reopening ingestion.

Restart reconstruction does not mint a new I5 authorization and does not invoke a new I6 canonical mutation.

## Failed-publication repair

If local I6/I7 commit succeeds but distributed checkpoint CAS publication fails:

1. ingress is closed,
2. the local target is restored to the last distributed checkpoint,
3. the local I7 replica is repaired to that distributed state,
4. if the distributed state was empty, the local manifest for the unpublished mutation is removed,
5. distributed writer authority is released/lost,
6. the prepared I5 authorization remains retryable because authoritative consumption is represented by the target's I6 receipt, which disappears with rollback.

The failed local mutation is therefore never admitted as distributed canonical state.

## Source and authority exclusions

Iteration 10 must preserve:

- no verbatim source text in ownership/checkpoint authority,
- no Pass-165 source-retaining path,
- no canonical learning commit,
- no truth promotion,
- no action authority minting,
- no authoritative float literals.

## Validation plan

The Iteration-10 workflow must validate, on one exact branch head:

- compilation of cumulative Pass-218 and Runtime-OS surfaces,
- AST no-authoritative-float gate,
- I1: 12 tests,
- I2: 13 tests,
- I3: 12 tests,
- I4: 14 tests,
- I5: 18 tests,
- I6: 19 tests,
- I7: 21 tests,
- I8: 23 tests,
- I9: 15 tests,
- all I10 deterministic and real-etcd tests,
- inherited repository-native crawler: 14 tests,
- Runtime-OS production-root: 6 tests,
- repository-native real-etcd Iteration-10 evidence.

No validation result is claimed in this restart record until the corresponding GitHub Actions run completes successfully.

## Environment

Required for the production distributed mode:

- a reachable etcd v3 linearizable cluster,
- `HHS_PASS218_ETCD_ENDPOINT`,
- optional namespace, authorization, CA, timeout, and lease-TTL configuration.

CI provisions an actual etcd v3 service so the production HTTP lease/CAS implementation is exercised in addition to deterministic injected tests.

Existing single-host deployments without distributed configuration intentionally remain on the validated Iteration-9 ownership boundary.

## Remaining work

1. Run and repair the full Iteration-10 GitHub Actions authority gate.
2. Freeze actual real-etcd evidence identities in an evidence summary after the run is green.
3. Re-run the full gate on the documentation-complete exact head.
4. Open a draft PR against current `main`.
5. Validate the GitHub synthetic merge candidate through inherited Pass-217/218/219, Runtime-OS, IDE, Pass-196, and deployment gates.
6. Record terminal validation as a PR comment without moving the validated head.

## Next action

Observe the first Iteration-10 workflow run triggered after this restart-record commit and repair forward only from concrete failures.

## Blockers

No design blocker is known. Validation is pending; the new distributed backend must not be considered admitted until the real-etcd and cumulative gates are green.
