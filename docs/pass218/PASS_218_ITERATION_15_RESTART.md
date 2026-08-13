# Pass 218 Iteration 15 Restart Boundary

Pass 218 remains **IN DEVELOPMENT**. Iteration 15 adds one-time consumption of an I14 maintenance release and downstream attestation/reconciliation. It does not grant canonical authority and does not perform the external I12 maintenance operation itself.

## Repository state

- Frozen parent: `f718408cd06f40ab643c92f3a002865babb58be9` (validated I14 head)
- Branch: `agent/pass218-full-iteration15-one-time-maintenance-release-consumption`
- Merge target: `main`
- Draft PR: `#223`
- Main advanced independently during I15; PR validation therefore uses GitHub's synthetic merge candidate over current `main` rather than assuming the earlier main SHA.

## I15 delta

- `hhs_runtime/pass218/execution_i15.py`
- `hhs_runtime/pass218/consumption_recovery_i15.py`
- `hhs_backend/pass218_execution_i15_control.py`
- `hhs_backend/runtime_os_pass218_consumption_i15.py`
- `hhs_backend/runtime_os_application_server.py`
- `scripts/pass218_iteration15_consumption_validation.py`
- `tests/pass218/test_pass218_iteration15_one_time_consumption.py`
- `tests/pass218/test_pass218_iteration15_runtime_control.py`
- `tests/pass218/test_pass218_iteration15_parallel_reservation.py`
- `tests/pass218/test_pass218_iteration14_runtime_os_status.py` (I14→I15 cumulative integration hook only)
- this restart record

## Authority boundary

I15 consumes an already valid I14 release only after I14 preflight. A durable claim is the external-maintenance start boundary. The same release cannot be claimed twice, and a second release for the same prepared I13 action is rejected. Claimed, failed, aborted, or interrupted attempts do not reopen the release; retry requires a new prepared/approved release.

The secondary per-action index is recoverable from the durable claim receipt. Production startup and each production claim repair missing indexes before admission, closing the claim-written/index-missing crash window.

A successful terminal attestation requires validated action-specific I12 maintenance evidence. Reconciliation binds the claim, terminal attestation, I12 evidence hash, and I13 maintenance-run receipt, and is persisted idempotently under the I14 reconciliation namespace.

I15 does not mint authority, mutate the canonical target, promote truth, commit learning, retain source material, invoke Pass165 source retention, or introduce authoritative floating-point weights.

## Validation surface

The existing I14 PR workflow is intentionally reused as the cumulative executable gate. On the I15 branch its already-executed RuntimeOS status test invokes all dedicated I15 pytest files, including the eight-process single-winner workload. Inherited I1–I14, Pass146, crawler, RuntimeOS, real I12, real I14, application IDE, Pass217 integration, Pass196, and DigitalOcean checks remain independent gates.

Terminal exact-head and synthetic-merge validation identifiers are recorded in the PR #223 terminal checkpoint comment after this documentation commit. No later code or documentation mutation should occur on the frozen I15 branch without reopening validation.
