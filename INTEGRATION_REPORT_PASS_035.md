# Integration Report — Pass 035

Pass 034 proved the non-silent propagation and anti-bruteforce scenarios in a security harness. Pass 035 exposes that policy as a runtime preflight binding for API, service, GUI, SRCG, closure, and service-registry surfaces.

## Runtime binding

- canonical full witness chain: admitted
- terminal value only: rejected without execution
- schemaless transformation: rejected without execution
- ledgerless mutation: rejected without execution
- phase-product ECC drift: rejected without execution
- Hash72/u^72 rotation-profile drift: rejected without execution
- harmonic-time/audio drift: rejected without execution
- partial brute-force witness: rejected without execution
- full rule-following brute force: reclassified as valid propagation

## New route

`POST /api/runtime/admissibility/enforce` returns a canonical API contract and an `HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_DECISION_V1` record.
