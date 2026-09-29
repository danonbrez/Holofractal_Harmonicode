# Pass 220 I062 Native Pytest Provider — Restart Record

Status: **RESTARTABLE IMPLEMENTATION — VALIDATION QUEUED**

## Identity

- Base main / verified I061 merge:
  `8db145707a71f60015904577e2a0786e438a4c65`
- Branch: `pass220/i062-native-pytest-provider1`
- Merge target: `main`
- Pull request: `#658`
- Initial implementation:
  `ca94c3a4a2fbc86652cfab931925eff848b3d3ee`
- Compatibility repair:
  `fe9694354bed4e8f2edfb82d61af17de39630c2e`
- Dedicated workflow:
  `Pass 220 I062 Native Pytest Provider`
- Repair-head run: `36588572441`
- Repair-head job: `109475357254`
- Run state at checkpoint write: queued
- PR state at checkpoint write: open, mergeable

## Implemented surfaces

- native pytest compatibility shim, without importing upstream pytest;
- native test discovery for `test_*.py`, `*_test.py`, `Test*` classes,
  function tests and method tests;
- pytest-compatible node IDs and path/node selection;
- sync and async test execution;
- recursive fixture dependency injection;
- function, class, module and session fixture scopes;
- autouse and yield fixtures;
- `request.addfinalizer`;
- `tmp_path`, `tmp_path_factory`, `monkeypatch`, `capsys`;
- `pytest.mark.parametrize`, `pytest.param`, parameter IDs and marks;
- `skip`, `skipif`, `xfail`, `raises`, `approx`, `fail`,
  `importorskip`;
- custom markers and `usefixtures`;
- module/function/class/method setup and teardown;
- `-k`, `-m`, `--collect-only`, `--maxfail`, `-x`;
- pytest-compatible outcome classes:
  PASS, FAIL, ERROR, SKIP, XFAIL, XPASS;
- deterministic config Hash72;
- deterministic collection/source Hash72;
- deterministic result Hash72;
- ordered 216-character replay receipt:
  `config_hash72 || collection_hash72 || result_hash72`;
- installer Pass 172/173 validation migrated from external
  `python -m pytest` to
  `python -m hhs_runtime.testing.native_pytest_provider_v1`.

## Repair applied

Before CI execution, review found configured marks such as
`@pytest.mark.skip(reason=...)` and `xfail(...)` were not attached on the
decorator's second call. Commit
`fe9694354bed4e8f2edfb82d61af17de39630c2e` repairs:

- configured mark decoration;
- single or iterable module-level `pytestmark` normalization;
- zero- or one-argument module/class xUnit hook compatibility.

The provider contract and authority boundary did not change.

## Fail-closed/deferred compatibility

The following are not silently delegated to external pytest:

- indirect parametrization;
- parametrized fixture matrices;
- arbitrary third-party pytest plugin hooks.

Unsupported behavior fails closed and must be implemented natively before it
can become authoritative.

## Authority

- external pytest execution in provider: false;
- upstream pytest role: differential oracle / migration compatibility only;
- VM81 mutation: false;
- Hash72 commit: false;
- Hash216 persistence: false;
- native provider receipt role: replayable test-evidence candidate.

## Files changed

1. `.github/workflows/pass220-i062-native-pytest-provider.yml`
2. `contracts/pass220/PASS_220_I062_NATIVE_PYTEST_PROVIDER_V1.json`
3. `docs/operations/restart/PASS_220_I062_NATIVE_PYTEST_PROVIDER_RESTART_20260929.md`
4. `docs/pass220/PASS_220_I062_NATIVE_PYTEST_PROVIDER.md`
5. `hhs_installer/transaction.py`
6. `hhs_runtime/testing/__init__.py`
7. `hhs_runtime/testing/native_pytest_provider_v1.py`
8. `tests/pass220/i062_native_pytest_specimen/test_native_pytest_specimen.py`
9. `tests/pass220/test_hhs_pass220_i062_native_pytest_provider_v1.py`

## Validation gate

Required workflow steps:

1. standard-library I062 unit suite;
2. native provider CLI against the pytest-compatible specimen;
3. Python syntax compile for provider and installer transaction.

No upstream pytest installation is required by the I062 workflow.

## Next action

Inspect run `36588572441`, job `109475357254`.

If green:
1. freeze green evidence without changing executable provider logic;
2. merge PR #658;
3. verify the provider, installer migration and contract on main;
4. repair-forward only attributable post-merge failures.

If failed:
repair only the attributable I062 provider, compatibility specimen, installer
migration, or provider test surface.

Do not restore external pytest as the authoritative installer validation path
to work around a native-provider defect.
