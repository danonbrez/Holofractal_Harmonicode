# Changelog — Pass 032

## Priority

Authorized pure-function expansion plus explicit failure-path enforcement.

## Added

- `hhs_runtime/hhs_authorized_execution_failure_policy_v1.py`
- `tests/test_hhs_authorized_execution_failure_policy_v1.py`
- `AUTHORIZED_EXECUTION_FAILURES_PASS_032.json`
- `AUTHORIZED_EXECUTION_FAILURES_PASS_032.md`
- Guarded service: `authorized_execution_failure_policy.self_test`
- Make target: `make authorized-execution-failure-policy`

## Changed

- Expanded the authorized pure-function allow-list from 2 to 3 deterministic functions.
- Added `hhs_runtime/hhs_runtime_contract_v1.py::is_hash72` as a pure, JSON-stable, side-effect-free target.
- Updated authorized pure execution artifacts to Pass 032 filenames.
- Extended the dry-run allow-list so every authorized pure target still passes the dry-run requirement before actual execution.
- Updated runtime reachability to `PASS_032` with the new service visible and orphan count preserved at zero.

## Boundary preserved

```text
raw plugin execution: blocked
mutation/write/network/process: blocked
non-allow-listed calls: rejected
malformed requests: rejected
rejections: witnessed + ledgered
rejected target function bodies: not executed
```
