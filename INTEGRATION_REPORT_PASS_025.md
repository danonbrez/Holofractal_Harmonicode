# Integration Report — Pass 025

## Priority

Guarded plugin invocation execution.

## Rationale

Pass 024 produced safe invocation plans. Pass 025 makes those plans reachable through the validated runtime graph without authorizing direct plugin execution. This is the safe midpoint between static planning and live semantic adapters.

## Runtime Path

```text
capability plan validation
→ canonical execution request
→ canonical runtime packet
→ HHS-M001..M007 foundational audit
→ authorized runtime tick
→ C u^72 Hash72 Digital DNA witness
→ unified Hash72 ledger append
→ explicit plan-only adapter result
```

## Non-Bypass Enforcement

The executor refuses `direct_execution_authorized=true`. A live plugin function must first receive a dedicated semantic adapter and closure-harness coverage.
