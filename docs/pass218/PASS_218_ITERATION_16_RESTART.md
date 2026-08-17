# Pass 218 Iteration 16 Restart Record

## Scope

Iteration 16 extends the frozen Iteration 15 one-time maintenance-consumption boundary into the existing Iteration 10/11 distributed authority substrate. It does not widen canonical authority.

The authoritative ordering in distributed mode is:

```text
I14 release
    -> I15 exact claim construction
    -> I16 owner/fence-guarded distributed CAS
         -> ordered ledger entry
         -> immutable release marker
         -> immutable prepared-action marker
    -> local I15 journal mirror
    -> external I12 operation remains outside the control plane
```

A replacement authority host reconstructs the exact embedded I15 claim from the distributed ledger. Machine loss does not reopen either the consumed release or its prepared I13 action.

## Repository checkpoint

- Frozen I15 parent: `953516e9883a58ab1ad908e4cc518dbd672b9048`
- Branch: `agent/pass218-full-iteration16-distributed-consumption-failover-convergence`
- Initial I16 implementation checkpoint: `2d4e951d7dad9271b151a97a2c45b7e07334e215`
- Main/base at checkpoint: `5cbb85ca33031e1ae2c072491271b66ec967dfde`
- I15 PR remains separate and frozen as PR #223.

The I16 branch was created directly from the frozen I15 head and was verified zero commits behind that parent before implementation began.

## I16 implementation files

- `hhs_runtime/pass218/distributed_consumption_i16.py`
- `hhs_backend/pass218_execution_i16_control.py`
- `hhs_backend/runtime_os_pass218_consumption_i16.py`
- `hhs_backend/runtime_os_application_server.py`
- `scripts/pass218_iteration16_consumption_validation.py`
- `tests/pass218/test_pass218_iteration16_distributed_consumption.py`
- `tests/pass218/test_pass218_iteration16_etcd_cas.py`
- `tests/pass218/test_pass218_iteration16_runtime_control.py`

This restart record is the ninth I16 delta file.

## Implemented invariants

1. The distributed consumption transaction is downstream of a valid I15 claim and the current I10/I11 owner/fence.
2. The transaction atomically advances an ordered ledger head and creates an immutable ledger entry, release marker, and prepared-action marker.
3. The release marker prevents reuse of the same I14 release.
4. The action marker prevents a separately signed release for the same prepared I13 action from creating another attempt.
5. The exact I15 claim and exact distributed ownership record are embedded in the sealed I16 entry.
6. Distributed persistence precedes the local I15 mirror in distributed mode.
7. A lost local mirror is reconstructed from the distributed ledger without minting new authority.
8. A pre-I16 local claim may migrate automatically only while its recorded distributed fence is still current.
9. A local-only claim discovered after the global fence advances is not re-authored under the successor authority; it is classified as stale/ambiguous and the I16 coordinator fails closed.
10. I9-only deployments retain the validated I15 local behavior and do not claim distributed durability.
11. I10/I11-required deployments never silently fall back to local consumption when the distributed ledger is unavailable.
12. I16 performs no canonical target mutation, learning commit, truth promotion, action-authority minting, or maintenance operation.
13. Authoritative I16 modules contain no floating-point literals by contract and dedicated AST test.

## RuntimeOS surfaces

The four I15 API paths remain unchanged and are now backed by the I16 coordinator when the installed lifecycle is distributed:

```text
GET  /api/runtime/pass218/authority/maintenance-consumption/status
POST /api/runtime/pass218/authority/maintenance-consumption/claim
POST /api/runtime/pass218/authority/maintenance-consumption/attest
POST /api/runtime/pass218/authority/maintenance-consumption/reconcile
```

I16 adds:

```text
GET  /api/runtime/pass218/authority/maintenance-consumption/distributed/status
POST /api/runtime/pass218/authority/maintenance-consumption/distributed/synchronize
```

The application server retains `PASS218_I15_CONSUMPTION_CONTROL_PLANE` as a compatibility alias to the installed I16 coordinator and additionally exports `PASS218_I16_CONSUMPTION_CONTROL_PLANE`.

## Dedicated validation coverage

`test_pass218_iteration16_distributed_consumption.py` covers:

- same-fence migration of a pre-I16 I15 claim;
- exact failover reconstruction on a replacement host;
- independent release and action anti-replay markers;
- stale unreplicated local-claim rejection;
- entry tamper rejection;
- no-float authoritative source enforcement.

`test_pass218_iteration16_etcd_cas.py` exercises the production etcd ledger implementation with deterministic etcd transaction semantics and verifies that the ledger head, ordered entry, release marker, and action marker are committed in one owner/fence-guarded transaction. It then advances to a successor ownership record and proves the action marker still blocks a second release.

`test_pass218_iteration16_runtime_control.py` covers:

- distributed persistence surviving failure of the local mirror write;
- subsequent reconstruction of that exact claim;
- stale local-only evidence blocking new distributed claims;
- preservation of the four I15 paths;
- installation of the two I16 convergence paths;
- preservation of local I9/I15 semantics when no distributed lifecycle is configured.

`scripts/pass218_iteration16_consumption_validation.py` is the restartable terminal validator and writes `.i16-evidence`.

## Validation arrangement

An Iteration 16 workflow YAML was prepared but the GitHub connector rejected the workflow-file write before it reached the repository. No partial workflow commit exists. This is the same connector limitation documented for Iteration 15.

Validation therefore uses:

1. the dedicated committed I16 pytest suites and restartable terminal validator;
2. the existing cumulative PR workflows, especially the I10 real-etcd gate and later Pass 218 / RuntimeOS gates, which are triggered by an I16 pull request against `main`;
3. exact-head / synthetic-merge validation where available through those established workflows.

The existing I10 workflow provisions real etcd v3.5.21 and compiles the cumulative `hhs_runtime/pass218/*.py` surface. The production RuntimeOS root workflows import the modified application server and therefore exercise the I16 composition boundary.

## Remaining closure work

- Open the I16 draft PR against `main`.
- Observe the established PR workflows on the I16 head and repair forward any I16-caused failures.
- Run or obtain execution of the dedicated I16 suites plus `scripts/pass218_iteration16_consumption_validation.py` on the exact candidate.
- Record final workflow run IDs, synthetic merge candidate, artifact hashes, and exact validated head.
- Freeze I16 only after those checks are green.

Pass 218 remains **IN DEVELOPMENT**.
