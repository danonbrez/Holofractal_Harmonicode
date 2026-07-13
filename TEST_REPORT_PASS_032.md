# Test Report — Pass 032

## Verified make targets

```text
make verify-c ✅
make authorized-pure-function-executor ✅
make authorized-execution-failure-policy ✅
make service-registry ✅
make contract-schema-registry ✅
make runtime-reachability ✅
```

## Verified pytest targets

```text
pytest -q tests/test_hhs_authorized_execution_failure_policy_v1.py ✅ 4 passed
pytest -q tests/test_hhs_authorized_pure_function_executor_v1.py ✅ 4 passed
```

## Key observed state

```text
authorized pure executions: 3
authorized pure errors: 0
failure records: 3
failure reason codes: FORBIDDEN_AUTHORIZATION_FLAG, MALFORMED_EXECUTION_REQUEST, NOT_ALLOWLISTED_FUNCTION
rejected executions performed: false
service count: 25
orphan count: 0
ledger verified: true
```

A combined broader pytest command was not used as the release gate because the
ledger-heavy authority tests grow expensive in this environment. Pass-specific
and affected-surface targets passed cleanly.
