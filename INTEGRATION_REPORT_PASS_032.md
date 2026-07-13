# Integration Report — Pass 032

## Executive Summary

Pass 032 hardens the controlled authorized execution layer by proving both sides
of the gate:

```text
valid allow-listed pure function → execute through authority chain
invalid/unsafe/non-allow-listed request → failure record, no target execution
```

This prevents the authorized execution layer from expanding by accident.  A
request can no longer fail silently or escape as an unstructured exception; it
must become an auditable failure object.

## New failure-policy path

```text
execution request candidate
→ structural/policy preflight
→ allow-list / forbidden-flag check
→ failure execution_request + runtime_packet
→ HHS-M001..M007 foundational audit
→ C u^72 Hash72 failure witness
→ unified ledger receipt
→ explicit REJECTED_WITHOUT_EXECUTION record
```

## Authorized pure expansion

Authorized pure execution now includes:

```text
hhs_runtime/hhs_srcg_gate_v1.py::check_1001_invariant
hhs_runtime/hhs_system_closure_harness_v1.py::summarize_closure_cycle
hhs_runtime/hhs_runtime_contract_v1.py::is_hash72
```

All still require:

```text
dry-run trace
→ Pass 030 schema validation
→ foundational audit
→ authorized runtime tick
→ pure call
→ Hash72/u^72 result witness
→ ledger receipt
```

## Failure cases validated

- `NOT_ALLOWLISTED_FUNCTION`
- `FORBIDDEN_AUTHORIZATION_FLAG`
- `MALFORMED_EXECUTION_REQUEST`

All three produce schema-valid `FAILURE_RECORD` classifications and preserve
`execution_performed == false`.

## Reachability

- Service count: `25`
- Orphan count: `0`
- New service: `authorized_execution_failure_policy.self_test`
