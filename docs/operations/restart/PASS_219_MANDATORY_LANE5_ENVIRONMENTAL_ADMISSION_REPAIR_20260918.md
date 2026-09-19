# Pass 219 — Mandatory Lane 5 Environmental Admission Repair

**Date:** 2026-09-18
**Base commit:** `cfb4679e433597081ed2ef76303a4af3956226d6`
**Branch:** `repair/lane5-mandatory-environmental-admission-20260918`
**Merge target:** `main`
**State:** PRE_IMPLEMENTATION_CHECKPOINT

## Defect

The current public canonical entrypoint `hhs_exact_pass219_vm81_environment_admit_signed`
performs the environmental gate and then delegates to the hidden 1.31 signed firewall.
The hidden signed firewall traverses the C++ RNA cell wall, but it directly invokes
the hidden RNA/VM81 commit seam afterward. It does not require
`hhs_exact_pass219_lane5_mediate_candidate`.

Separately, I162 still uses the historical direct `hhs_exact_vm81_admit_uqcel`
transport path for its commit/replay evidence.

This conflicts with the established Lane 5 authority contract:

```text
VM5184 candidate
 -> C++ CoreHolographicRNACellWall
 -> Lane 5 mediation
 -> signed environmental VM81 admission
 -> canonical VM81 transition
 -> Hash72
 -> Hash216
```

## Repair contract

1. Preserve the C++ cell wall and all existing PQC/environmental authority.
2. Derive a Lane 5 mediation request from the exact cell-wall prepared/decision
   evidence plus exact candidate, parent Hash216, BigInt/UQCEL input, and
   capability identities.
3. Require a valid candidate-only Lane 5 mediation receipt before the
   environmental gate may proceed.
4. Reuse the exact same prepared/decision evidence for signing and hidden
   RNA/VM81 commit; do not reroute through a second, disconnected cell-wall
   evaluation.
5. Preserve hidden raw mutators and the sole public canonical mutation entrypoint.
6. Repair I162 so canonical continuation evidence cannot be produced by direct
   `hhs_exact_vm81_admit_uqcel` bypass.
7. Add negative tests proving:
   - malformed/absent Lane 5 evidence cannot reach canonical mutation;
   - Lane 5 cannot mint VM81/Hash72/Hash216 authority;
   - public environmental admission remains the only exported canonical seam;
   - exact replay still closes after the repaired chain.

## Planned validation

- strict cumulative `make c-abi`
- Lane 5 nucleus native contract
- VM81 PQC signature/environmental recovery regressions
- new mandatory Lane 5 environmental admission regression
- I162 / global self-enforcement regression through repaired canonical path
- Lane 5 1.37 state/fingerprint regression
- dynamic-symbol authority audit

## Restart state

No runtime file has been modified yet. Resume from this branch and implement the
mandatory mediation seam before changing proof claims.
