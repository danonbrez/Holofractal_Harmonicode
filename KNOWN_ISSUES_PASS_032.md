# Known Issues — Pass 032

## Ledger/test runtime growth

The authority ledger is intentionally richer after Passes 029–032. Repeated
full-suite runs can become slow because each authority path appends and verifies
additional witness records.

Recommended next hardening:

```text
bounded test ledger fixture
→ deterministic ledger compaction mode
→ failure-path integration test profile
```

## Authorized execution scope remains intentionally narrow

Only deterministic pure functions are authorized. Stateful adapters, writes,
network/process actions, and arbitrary plugin function bodies remain blocked.
