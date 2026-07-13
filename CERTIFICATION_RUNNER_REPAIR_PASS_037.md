# Certification Runner Repair Pass 037

The legacy runner `hhs_v1_bundle_runner.py` imported `HHSSmokeTestSuiteV1`, but the smoke module exposes `run_smoke_suite()`.

Pass 037 updates the legacy runner to call `run_smoke_suite()` and normalize the returned summary into the legacy report shape.

The database persistence phase is also treated as optional when the database bridge cannot be imported, matching the runner's documented sequence.

## Result

```text
hhs_v1_bundle_runner.py
-> CERTIFIED_LOCKED

hhs_v1_bundle_runner-2.py
-> CERTIFIED_LOCKED
```
