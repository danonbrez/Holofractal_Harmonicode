# Pass 218 Iteration 12 Restart Record

## Identity

- Pass: 218
- Iteration: 12
- Scope: production authority maintenance and rotation
- Branch: `agent/pass218-full-iteration12-production-authority-maintenance`
- Parent / frozen I11 head: `da8ae259e6d688d321fa22a800c729ac5473ee67`
- Merge target: `main`
- Draft PR: `#220`
- Pass 218 status: **IN DEVELOPMENT**

## Preserved authority hierarchy

```text
I9   local process fence
        +
I10  distributed lease/CAS global fence
        +
I11  verified multi-member mTLS quorum
        ↓
     canonical writer
        +
I12  maintenance / rotation membrane
```

I12 is not another source of canonical authority. It constrains how an already-proven I11 deployment may be maintained without creating writer ambiguity or weakening the I10 global fence.

## I12 invariants

1. I10 lease/CAS ownership and checkpoint schemas remain unchanged.
2. I11 quorum identity, majority, leader and linearizable-read requirements remain unchanged.
3. Active client writer credentials are never hot-swapped while retaining the same writer authority.
4. New client credentials must be independently verified before handoff.
5. Canonical ingress must quiesce before the old writer releases.
6. The new writer may become authoritative only through a strictly newer I10 global fence.
7. Old and new writer identities may never be simultaneously authoritative.
8. Etcd member replacement is serial: at most one member is replaced at a time.
9. Pre-change and post-change linearizable quorum proofs are required around rolling member replacement.
10. Consensus-cluster member identity remains operational identity; it is not HHS canonical identity.
11. Snapshot retention is bounded by explicit integer policy.
12. Recovery rehearsal must preserve exact canonical root, VM81 snapshot, consumed I6 receipt and distributed checkpoint identity.
13. Recovery rehearsal may not mint restart authorization or perform canonical mutation.
14. Operational alerts are sealed diagnostic receipts only.
15. Automated recovery has a hard attempt budget. Exhaustion enters `MANUAL_INTERVENTION_REQUIRED`.
16. Any authority-loss recovery requires a strictly newer I10 global fence.
17. I12 cannot mint authority or mutate the canonical target.
18. No source retention, Pass-165 path, learning commit, truth promotion, action authority or authoritative float is admitted.

## Files introduced in the first I12 checkpoint

- `hhs_runtime/pass218/authority_maintenance_i12.py`
- `tests/pass218/test_pass218_iteration12_production_authority_maintenance.py`
- `.github/workflows/pass218-full-iteration12.yml`
- `docs/pass218/PASS_218_ITERATION_12_RESTART.md`

## Validation design

The I12 workflow performs dependency-scoped cumulative validation and a real etcd-v3.5.21 operational sequence:

- compile the cumulative Pass-218 Python surface;
- reject authoritative Python float literals;
- preserve I1-I12 unit/integration suites;
- preserve repository-native crawler and Runtime-OS production-root acceptance;
- provision a real three-member mTLS etcd cluster;
- acquire I10 authority with the old client identity;
- independently verify the new client identity against the same quorum;
- release the old writer before handoff;
- acquire a strictly newer I10 fence with the new identity;
- prove an old-credential contender cannot become a concurrent writer;
- stop/remove/re-add/bootstrap one etcd member under a new etcd member identity while maintaining quorum;
- induce 1/3 reachability and prove fail-closed quorum loss;
- restore 2/3 reachability and prove bounded recovery only through a fresh I10 fence;
- save and validate a real etcd snapshot as the retained operational artifact.

## Current implementation checkpoint

Repository commits written during this iteration before this restart record:

- `dffde652b2c5d9edcbce208f3922f2aa43f28b4c` — I12 authority-maintenance membrane
- `77ecf8d77d6199aafc219a28e123e0d786c0edae` — I12 invariant tests
- `08b99bfbaf8569631e0681c496b87c1b6edc1e63` — I12 real operational CI workflow

Exact-head validation is still required after this record is committed. Do not call I12 frozen or validated until the workflow succeeds against the exact final head and the resulting evidence is inspected.

## Next action

1. Run the I12 pull-request workflow against the exact branch head.
2. Inspect any failing step and repair forward without altering frozen I11 semantics.
3. Record exact run ID, artifact identity and real operational evidence.
4. Re-run impacted validation only.
5. Freeze the validated head and write the terminal PR checkpoint without mutating it.
