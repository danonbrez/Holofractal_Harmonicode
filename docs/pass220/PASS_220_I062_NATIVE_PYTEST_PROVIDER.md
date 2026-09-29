# Pass 220 I062 — Native Pytest Provider

I062 replaces external pytest as the authoritative repository validation provider while preserving a pytest-compatible test ingress surface.

The provider is implemented at hhs_runtime/testing/native_pytest_provider_v1.py and does not import or spawn upstream pytest. Existing upstream pytest remains available only as a differential oracle and migration compatibility tool.

Core compatibility includes test discovery, Test* classes, node IDs, sync/async execution, fixture dependency injection and scopes, yield fixtures, built-in tmp_path/tmp_path_factory/monkeypatch/capsys, parametrization, skip/skipif/xfail, raises, approx, setup/teardown hooks, -k/-m selection, collect-only, maxfail, deterministic exit codes, and replayable receipts.

Each run produces three ordered Hash72 identities: configuration, collection/source identity, and deterministic result identity. Their ordered concatenation is the 216-character provider receipt. This receipt is evidence only: the provider receives no VM81 mutation, Hash72 commit, or Hash216 persistence authority.

Unsupported plugin-era behavior fails closed. I062 does not silently delegate unsupported semantics to external pytest.

The Pass 172/173 installer transaction validation command is migrated from python -m pytest to python -m hhs_runtime.testing.native_pytest_provider_v1.

Validation commands:

    python tests/pass220/test_hhs_pass220_i062_native_pytest_provider_v1.py
    python -m hhs_runtime.testing.native_pytest_provider_v1 -q tests/pass220/i062_native_pytest_specimen
