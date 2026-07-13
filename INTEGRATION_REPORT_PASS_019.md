# INTEGRATION REPORT PASS 019 — SRCG Runtime Reachability

## Objective
Expose the SRCG primitive instruction through canonical runtime entry points so it becomes a usable platform capability, not only a kernel/service symbol.

## Integration Work

### Backend
- Added `POST /api/runtime/srcg/selfsolve`.
- Route performs canonical IO ingress before SRCG execution.
- Route calls `selfsolve_ab_gate()` and preserves the nested carrier payload.
- Route emits canonical IO egress after execution.
- Route returns the standard `api_response` runtime contract envelope.

### Frontend Bridge
- Added guarded API dispatch support to `RuntimeKernelBridge`.
- Added `executeSRCGSelfSolve()` for GUI/IDE tools.
- Added contract validation on API response envelopes.

### Verification
- Backend route test confirms API contract, IO receipts, SRCG state schema, and kernel witness trace.
- GUI bridge test confirms SRCG callable surface and contract validation hooks.

## Architectural Effect
SRCG now has a complete reachable path:

```text
GUI / IDE Bridge
→ Canonical API Route
→ IO Gateway ingress
→ SRCG primitive
→ Hash72/u^72 kernel witness trace
→ IO Gateway egress
→ API response runtime contract
```

This keeps SRCG inside the sealed authority chain while making it available to user-facing runtime surfaces.
