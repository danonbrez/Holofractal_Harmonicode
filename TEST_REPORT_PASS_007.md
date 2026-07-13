# TEST REPORT — PASS 007

## Commands executed

```bash
make verify-c
pytest -q
make io-gateway
make service-registry
make backend-routes
```

## Results

- `make verify-c` passed.
- `pytest -q` passed: 42 tests.
- `make io-gateway` passed.
- `make service-registry` passed.
- `make backend-routes` passed.

## Notes

- Existing C runtime warnings remain non-blocking.
- Unified Hash72 ledger verification remains true after IO gateway appends.
- Backend route tests now assert ingress/egress containment metadata.
