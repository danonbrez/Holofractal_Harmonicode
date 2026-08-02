# Pass 190 Iteration 7 Restart Record

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ 1d3c7588a242e3a83304f5083c2ec5a974f19399`
- Working branch: `agent/pass190-iteration7-durable-workers`
- Merge target: `main`
- Contract: `HHS-P190-I7-DWE-DSCR-WL-VM81-H72-H216`

## Intended scope

Close the bounded Pass 190 gap between the Iteration 6 durable job registry and actual governed execution by implementing:

- worker registration, heartbeat, capability matching, enable/disable, and one-job ownership;
- exact dependency and schedule admission;
- deterministic priority claims;
- Hash72 execution claim tokens;
- pure-operation-only internal execution;
- one outer receipt-bound target evaluation;
- cancellation, bounded retry, and stale-worker recovery;
- API, SDK, compiler, binding, GUI, worker-service, and deployment surfaces.

## Changed source groups

- `python/hhs_pass190_iteration7_registry.py`
- `python/hhs_pass190_iteration7.py`
- `python/hhs_pass190_iteration7_compiler.py`
- `python/test_hhs_pass190_iteration7.py`
- `server/hhs_pass190_iteration7_server.py`
- `worker/hhs_pass190_iteration7_worker.py`
- generated Python and TypeScript SDKs
- generated governed binding V3
- Pass 190 GUI execution status
- API and worker systemd services
- installation and deployment verification
- cumulative Makefile validation
- Iteration 7 source and GUI verifiers
- formal contract, evidence, restart record, and CI

## Preserved inherited authority

- canonical ten-operation C ABI and generated native artifacts;
- all Iteration 1–6 operations and resource records;
- persistent Hash72/Hash216 receipts and replay;
- signed capability authentication;
- singleton VM81 admission;
- SQLite lease, fencing, and atomic kernel witnesses;
- event resume and WebSocket transport;
- workspace, artifact, provider, capability-definition, and legacy job lifecycles;
- inherited GUI verification strings and surfaces.

## Validation command

```bash
cd native_projects/hhs_pass190_operation_fabric
make validate
```

Expected cumulative gate:

- strict C11 shared library and test executable;
- 64 inherited Python tests;
- 13 Iteration 7 tests;
- 77 Python tests total;
- Python compilation;
- SDK generation parity;
- governed binding V3 parity;
- inherited native generator parity;
- GUI verification through Iteration 7;
- deployment verification for both services;
- private eval/exec rejection;
- native no-float authority verification.

## Current status

- Implementation source committed to the working branch.
- Generated SDK and binding sources committed.
- GUI and dual-service deployment sources committed.
- Contract and evidence committed.
- GitHub PR and Actions validation remain before merge.

## Honest boundary

Not claimed:

- external provider execution;
- arbitrary subprocess or shell execution;
- worker execution of mutating targets;
- multi-host consensus;
- full native parity;
- complete Python compatibility;
- live DigitalOcean installation or production acceptance;
- final Pass 190 completion.

## Next action

1. Add the dedicated Iteration 7 GitHub Actions workflow.
2. Compare branch against current `main` and reconcile only additive conflicts.
3. Open a ready PR.
4. Run the full inherited and Iteration 7 workflows.
5. Repair only validated failures.
6. Merge after all Pass 190 workflows pass.
7. Verify authoritative `main` and update branch alignment.
