# KNOWN ISSUES PASS 012

## Remaining Contract Migration Targets

- Some graph lookup/replay and prediction routes still return legacy payloads and should be wrapped in a later pass.
- Sandbox create/step routes still need full canonical ingress/egress envelopes.
- Frontend TypeScript contract types are not yet generated from the Python canonical contract.
- Node dependencies are not vendored, so GUI build verification remains environment-dependent.

## Kernel Semantics
No kernel or algebraic invariant semantics were changed.
