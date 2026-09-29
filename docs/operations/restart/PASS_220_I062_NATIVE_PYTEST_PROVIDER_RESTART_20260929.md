# Pass 220 I062 Native Pytest Provider — Restart Record

Status: RESTARTABLE IMPLEMENTATION — VALIDATION PENDING

Base main: 8db145707a71f60015904577e2a0786e438a4c65
Branch: pass220/i062-native-pytest-provider1
Merge target: main

I061 prerequisite is satisfied by merged PR #655 at the exact I062 base.

Implemented surfaces:
- native pytest-compatible shim;
- native collector and node IDs;
- function/class test execution;
- sync and async execution;
- recursive fixture dependency resolution;
- function/class/module/session fixture scopes;
- yield-fixture teardown and request.addfinalizer;
- tmp_path, tmp_path_factory, monkeypatch, capsys;
- parametrization and pytest.param IDs/marks;
- skip, skipif, xfail, raises, approx and fail;
- setup/teardown hooks;
- -k/-m/path/node selection, collect-only, maxfail and -x;
- deterministic config/collection/result Hash72 receipts;
- ordered 216-character replay receipt;
- installer validation migration away from external pytest.

Fail-closed/deferred:
- indirect parametrization;
- parametrized fixture matrices;
- arbitrary third-party pytest plugin hooks.

Authority:
- external pytest is not executed by the I062 provider;
- upstream pytest remains a differential oracle only;
- VM81 mutation remains false;
- Hash72 commit remains false;
- Hash216 persistence remains false.

Validation remaining:
1. standard-library I062 unit suite;
2. native provider CLI against the compatibility specimen;
3. structural assertion that installer validation no longer invokes python -m pytest;
4. PR CI and repair-forward if attributable failures occur.
