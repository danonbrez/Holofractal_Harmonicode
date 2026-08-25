# Pass 219 Iteration 130 — repaired inherited Pass 196 exposure

## Classification

`INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE`

Pass 219 I130 exposes the inherited Pass 196 integrated-environment surface only after repair-forward closure of the historical review findings. The accepted Pass 196 V1 implementation remains immutable provenance; I130 adds a V2 repair surface and binds that repaired surface into the cumulative Pass 219 C ABI/C++ RNA membrane.

## Provenance

- frozen I129 predecessor: `40e6e07d5f4a401541a6255339223e853846e713`
- historical Pass 196 PR: `#128`
- accepted Pass 196 merge: `37687d479f2a9f1d996d225a4ba3556d9db72a86`
- accepted topology-repair PR: `#130`
- accepted topology-repair merge: `959729c9070399fcdf0015702cd8777079e05dcc`
- immutable historical V1 runtime blob: `d2cff008db58a29bf27be20cb3547b9e0018f5e1`

## Historical review census

Historical PR #128 carried ten review findings:

1. `3699626177` — vector persistence could bypass canonical VM81/Hash72 admission.
2. `3699626180` — persisted vector lineage was not restored after restart.
3. `3699626182` — a test-only artifact could satisfy both executable and test evidence and be classified integrated.
4. `3699626186` — browser registry projection stayed stale after later scans.
5. `3699626190` — host-specific checkout path and worker count contaminated canonical manifest identity.
6. `3699626194` — hashing and classification could observe different bytes during a live file mutation.
7. `3699626196` — the DigitalOcean service did not originally provision writable persistent state for the `hhs` user.
8. `3699626198` — generic tool ingress coerced strings such as `"false"` to truthy persistence requests.
9. `3699626201` — a failed later scan could leave prior CLOSED evidence publicly reported as current success.
10. `3699626204` — the generic tool mutation path did not map scan failures consistently with the direct scan route.

The state-directory finding was already repaired on current main through the accepted topology/deployment lineage and remains preserved. I130 repair-forwards the other nine findings.

## Repair-forward V2 boundary

The accepted V1 blob is not rewritten. Production Pass 196 routes now import the additive V2 runtime.

V2 binds these properties:

- persistent vector admission requires a non-empty 72-character VM81-authorized Hash72 receipt;
- the last encrypted vector object and output Hash72 are restored from the persistent Pass 174 vector store before a new append;
- executable evidence must come from a non-test/non-evidence artifact;
- canonical manifest identity excludes host checkout path and worker-count diagnostics;
- each scanned file is read once for both digest and text classification, and a size/mtime stability check fails closed on concurrent mutation;
- failure moves the current public state to `QUARANTINED`; the previous good manifest is historical evidence only;
- `integration.scan` tool ingress uses `StrictBool` rather than Python truthiness coercion;
- direct and tool scan failures share the same governed HTTP mapping;
- Pass 161 browser projection refresh is an explicit validated projection overlay recorded through inherited `P161_REPLAY`; object identity, type, and `VALIDATED_PROJECTION` authority cannot be escalated by the frontend.

Repaired source identities bound by I130:

- V2 runtime: `196b1fbdbbb3610ccb47e7fd638d4c3f2cdc67f6`
- production API wrapper: `39187c3376591c64758019090d9b115c6a43f6ee`
- Pass 196 browser integration: `1503903c844c9e601133853eed9ed597f6fd2274`
- validated projection refresh overlay: `44254e10f90e929a4f8c1a18a75b3ca14a2c05ed`
- I130 repair regression: `d0860d89cd8abe596f49c73b7e544511cdaba5d0`
- I130 repair workflow: `7a19d3e7faab6e7210e156026300e96550b9afcb`

## Native Pass 219 exposure

I130 adds:

- `hhs_runtime/include/hhs_pass219_inherited_pass196_1_30.h`
- `hhs_runtime/include/hhs_pass219_inherited_pass196_1_30.hpp`
- `hhs_runtime/c/hhs_pass219_inherited_pass196_1_30.inc`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i130_pass196.py`
- C, C++, and Python membrane conformance tests.

Public C binder:

`hhs_exact_pass219_bind_pass196_repaired_integrated_environment`

C++ RNA facade:

`hhs::rna::InheritedPass196RepairedIntegratedEnvironment`

The cumulative aggregate registers Pass 196 immediately after repaired Pass 197, preserving reverse-pass inheritance order.

## Authority boundary

I130 does **not** create any new:

- candidate authority;
- canonical mutation authority;
- persistence authority;
- Hash72 clock authority;
- C++ mutation authority;
- VM81 mutation authority;
- vector-source authority;
- browser projection authority.

Singleton VM81 canonical authority remains inherited. Pass 196 encrypted vector persistence remains an inherited evidence/persistence surface admitted only through a valid VM81-authorized Hash72 receipt. The vector store is not source authority and the frontend is not mutation authority.

## Successor preservation

The repaired Pass 197 I129 membrane remains the immediate successor and must continue to validate unchanged. I130 therefore rejects any Pass 196 repair that breaks the frozen Pass 197 successor identity or cumulative exact ABI.

## Freeze gate

I130 is frozen only after both exact-head and synthetic-current-main lanes succeed with:

- historical Pass 196 provenance checks;
- repaired source identity checks;
- strict cumulative C11 ABI compilation;
- C and C++ I130 conformance;
- kernel-derived Python membrane preflight;
- historical Pass 196 lifecycle regression;
- I130 repair regressions;
- frontend projection-refresh regression;
- preserved Pass 197 I129 successor membrane;
- no approximate native authority and no accidental new authority export.

Until those lanes are terminal green, the correct state is `IMPLEMENTED_PENDING_FINAL_SEAL` rather than `FROZEN`.
