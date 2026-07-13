# Pass 032 Authorized Execution Failure Policy

Schema: `HHS_AUTHORIZED_EXECUTION_FAILURE_POLICY_V1`  
Version: `PASS_032`

Pass 032 hardens the inverse path of controlled authorized execution.  Unsafe or
invalid execution requests now produce explicit witnessed failure records instead
of silent denial or permissive fall-through.

## Summary

- Failure records: `3`
- Reason codes: `FORBIDDEN_AUTHORIZATION_FLAG, MALFORMED_EXECUTION_REQUEST, NOT_ALLOWLISTED_FUNCTION`
- All rejections prevented execution: `True`
- Schema registry valid: `True`
- Classified as failure records: `True`
- Hash72/u^72 witnessed: `True`
- Ledger OK: `True`
- Manifest witness: `(h7K9Pmbj6KTi>H-4!(6AbWu2yir)0+kkcp6s9HXlA!iRGRVF-3ftuX0o?4NNam/-+mQFz8l`

## Failure records

| Reason Code | Stage | Target | Executed | Witness |
|---|---|---|---:|---|
| `NOT_ALLOWLISTED_FUNCTION` | `ALLOWLIST_PREFLIGHT` | `hhs_runtime/hhs_srcg_gate_v1.py::selfsolve_ab_gate` | `False` | `91NDYyPREqfFCZr!Fn…` |
| `FORBIDDEN_AUTHORIZATION_FLAG` | `PRE_EXECUTION_POLICY_PREFLIGHT` | `hhs_runtime/hhs_runtime_contract_v1.py::is_hash72` | `False` | `+r914GTvUV+fhW060i…` |
| `MALFORMED_EXECUTION_REQUEST` | `PRE_EXECUTION_STRUCTURAL_PREFLIGHT` | `<missing>::is_hash72` | `False` | `jXse00Jb3UKVVZuEna…` |

## Rejection invariant

```text
invalid request
→ structural/policy preflight
→ no target import required
→ no target function-body execution
→ execution_request + runtime_packet for failure emission
→ HHS-M001..M007 foundational audit
→ C u^72 Hash72 failure witness
→ unified ledger receipt
```

This keeps the future authorized-execution surface from widening by accident.
