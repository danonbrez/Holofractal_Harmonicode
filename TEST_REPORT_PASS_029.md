# Test Report — Pass 029

## Commands Run

```bash
make verify-c
make dryrun-live-plugin-executor
python -m pytest tests/test_hhs_dryrun_live_plugin_executor_v1.py tests/test_hhs_readonly_live_plugin_adapter_v1.py tests/test_hhs_controlled_live_plugin_executor_v1.py -q
make service-registry
make runtime-reachability
```

## Results

- `make verify-c` completed successfully.
- `make dryrun-live-plugin-executor` completed successfully.
- targeted pytest completed successfully: **10 passed**.
- `make service-registry` completed successfully.
- `make runtime-reachability` completed successfully.

## Reachability Snapshot

- service count: **22**
- orphan count: **0**
- module count: **712**

## Pass-Specific Assertions

- dry-run self-test succeeds;
- target function bodies are not executed;
- non-allow-listed targets are blocked;
- C u^72 Hash72 kernel witnesses are emitted;
- unified ledger verification remains valid.
