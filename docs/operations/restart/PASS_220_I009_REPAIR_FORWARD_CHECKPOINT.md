# Pass 220 I009 repair-forward checkpoint

Status: **RESTARTABLE REPAIR CHECKPOINT — NEW CI PENDING**

## Observed failures repaired

1. Pass 220 cumulative run 35319743455 reached the dependency-scoped pytest stage, then failed collection because FastAPI was not installed in that post-calibration environment. The cold raw calibration itself completed before project execution.
2. The cold calibration report renderer used shell backticks inside double-quoted echo strings, causing accidental command substitution while producing Markdown. The measured summary values survived, but the report path emitted shell errors.
3. LiteRT-LM run 35319743295 passed the governed assistant backend, including I009 tests, but its legacy AI-thread interface failed npm resolution because React latest advanced to 19.3 while @react-three/fiber 9.7 requires React <19.3.
4. Full Application IDE run 35319743499 built the canonical Runtime OS successfully, then timed out waiting for the Visual Program component even though Mobile Control is intentionally the default surface. Browser acceptance did not navigate to Visual Program first.
5. main advanced by the verified Lane 5 self-enforcement proof; its two repository-visible proof files have been incorporated into this branch.

## Repairs

- post-calibration setup now installs the exact FastAPI/TestClient dependency set before Pass 220 tests;
- cold calibration report output uses printf/literal shell text and cannot execute Markdown as shell substitutions;
- legacy mobile-console React is pinned to 19.2.0 with @react-three/fiber 9.7.0;
- full-IDE browser acceptance explicitly clicks Visual Program before asserting its lazily mounted registry programmer;
- main's Lane 5 self-enforcement regression and closure checkpoint are present on the branch.

## Restart state

The next task may proceed without waiting for external CI. Inspect only new runs associated with the repaired head and repair forward if an impacted failure remains.
