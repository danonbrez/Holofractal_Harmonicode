# CHANGELOG PASS 019 — SRCG API / GUI Contract Surface

## Added
- Dedicated canonical backend route `POST /api/runtime/srcg/selfsolve`.
- `SRCGSelfSolveRequest` request model for guarded SelfSolve_AB_Gate execution.
- GUI bridge methods `dispatchService()` and `executeSRCGSelfSolve()`.
- RuntimeKernelBridge `apiBaseUrl` configuration.
- `make srcg-api-surface` verification target.

## Changed
- SRCG can now be invoked through the canonical API response envelope instead of only through internal service dispatch.
- SRCG responses now expose IO ingress/egress receipts and API response runtime contracts.

## Preserved
- Kernel SRCG primitive semantics.
- No-flatten quartic carrier rule.
- Hash72/u^72 kernel witness traceability.
- HHS Foundational Standards and Meaning Conservation authority chain.
