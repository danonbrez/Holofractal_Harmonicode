# Pass 219 I131 — repaired inherited Pass 195 Kimi K3 content engine

## Status

`REPAIRED_AND_WIRED — FINAL EXACT/SYNTHETIC SEAL PENDING`

## Lineage

- Frozen predecessor I130: `69743440249dd7a05aa2b4096482d248973f239e`
- Historical Pass 195 implementation PR: `#117`
- Accepted Pass 195 merge: `8bcc0921555ecface13113c8a2620415ddb3fdf1`
- Classification: `INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE`
- Merge authorization: **NOT GRANTED**

## Historical review findings repaired

Pass 195 carried twelve unresolved review findings. I131 repair-forwards all twelve while preserving the historical V1 runtime as immutable provenance.

1. `3696077892` — provider JSON is now validated against the strict declared plan schema before normalization, receipt creation, or ingress.
2. `3696077894` — normalized constraint content and reference-image content hashes are bound into proposal/input identity.
3. `3696077896` — Storybook refuses any plan whose HHS result or governed ingress is not admitted.
4. `3696077898` — returned/configured model identity is bound before the final plan Hash72 is computed.
5. `3696077899` — Storybook template defaults are applied before custom style overrides.
6. `3696077901` — paid `/plan` generation requires an operator token plus bounded concurrency and rate admission.
7. `3696077903` — constraints are bounded by count, per-item UTF-8 bytes, and aggregate UTF-8 bytes.
8. `3696077905` — generated handoff title/story lengths are constrained to Storybook-compatible limits.
9. `3696077907` — generated style ranges are aligned with the Storybook controls.
10. `3696077910` — reference images require a separately validated/admitted `IMAGE_ANALYSIS` capability proposal and invocation receipt.
11. `3696077912` — the exact VM81-authorized tick is ingested into the graph before the external provider await; a later global runtime state is never substituted.
12. `3696077914` — status/health Hash72 is recomputed over the final returned object.

## Accepted and repaired source identities

Immutable historical V1:

- `hhs_backend/runtime/hhs_kimi_k3_content_engine_v1.py`
- blob `ea7041c026e63445034c7161268faafe436cd2d1`

Repaired I131 sources:

- V2 runtime `hhs_backend/runtime/hhs_kimi_k3_content_engine_v2.py` — blob `c1cf830a8ede708b62cc052610968f7fc498228d`
- production API `hhs_backend/api/kimi_k3_content_routes.py` — blob `e62f59d5c8617a546908fd9ca2bd43998c62cd2e`
- Storybook client `applications/storybook_reel_studio/kimi-content-engine.js` — blob `9153f922193ddadf2e208986e11dc9d57e12f817`
- I131 repair regression `tests/test_hhs_pass195_i131_repair_v2.py` — blob `866a893e30dfd9565b712df9ff9c979395b25a3f`
- focused repair workflow `.github/workflows/pass195-i131-repair-validation.yml` — blob `f43d6cdb62e8836e075cb4400d9525eaf8f4d491`
- established Pass195 workflow `.github/workflows/pass195-kimi-k3-content-engine.yml` — blob `ca5bf19464aa1c9ef67b37ce5d84f3c24d300a59`

## Repaired execution boundary

### Provider plan and receipt identity

V2 validates the provider's structured plan before any receipt or ingress admission. Constraint text is normalized and bounded before hashing. Each reference image is bound by an exact content-root Hash72; ordered image roots and the constraint root are included in the TEXT_GENERATION proposal identity. When images are present, a separate `IMAGE_ANALYSIS` proposal must validate and pass the capability policy gate before the provider may be called.

The returned model identity is incorporated into the normalized plan before the final plan Hash72. The image-analysis proposal and invocation receipt are also bound into the text-generation receipt chain. External-provider output remains proposal-only and cannot claim VM81 state mutation, canonical rendering, shader execution, or native MP4 execution.

### Paid provider route

`POST /api/runtime/content-engine/kimi-k3/plan` fails closed unless `HHS_KIMI_K3_OPERATOR_TOKEN` is configured and the caller supplies the matching Bearer or operator header token. The route also enforces bounded concurrent plans and a bounded sliding-window admission rate.

The VM81-authorized tick is converted to an exact graph packet and ingested immediately before the provider await. The former post-provider `export_multimodal_packet()` path is absent, preventing a later global runtime state from being substituted for the state that authorized the invocation.

### Storybook handoff

The browser requires all three governed conditions before exposing the plan: result `ok`, admitted status, and successful provider-result ingress. The operator token is held only in the password input and sent as authorization for the paid route; no provider API key is sent to the browser.

Template defaults are dispatched first, then admitted custom overrides. Title/story and numeric style ranges are bounded by the same downstream Storybook surface constraints.

## Native I131 membrane

Implemented surfaces:

- `hhs_runtime/include/hhs_pass219_inherited_pass195_1_31.h`
- `hhs_runtime/include/hhs_pass219_inherited_pass195_1_31.hpp`
- `hhs_runtime/c/hhs_pass219_inherited_pass195_1_31.inc`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i131_pass195.py`
- `tests/pass219/test_pass219_inherited_pass195_1_31.c`
- `tests/pass219/test_pass219_inherited_pass195_1_31.cpp`
- `tests/pass219/test_pass219_cumulative_pass195_membrane_i131.py`

Aggregate exact ABI wiring places Pass195 immediately after Pass196 in reverse-pass order.

Public C binder:

`hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine`

C++ RNA facade:

`hhs::rna::InheritedPass195RepairedKimiK3ContentEngine`

The native witness requires the accepted merge, frozen I130 predecessor, immutable V1 blob, exact repaired source blobs, all twelve repair assertions, preserved Pass196 successor, and explicit zero values for every new-authority field.

## Authority boundary

I131 grants no new candidate authority, canonical mutation authority, persistence authority, Hash72 clock authority, C++ mutation authority, VM81 mutation authority, browser authority, or external-provider canonical authority.

Kimi K3 remains a governed external proposal source. Storybook remains a presentation/handoff surface. Singleton VM81 canonical authority remains inherited through the cumulative predecessor chain.

## Dependency-scoped validation

The first expanded Pass195 run exposed one deterministic V2-only defect: V1 reused one mutable string-schema object for multiple properties, so mutating the Storybook story limit also changed the title limit. No provider, receipt, ingress, or authority regression failed. I131 repaired this by replacing the title/story property schemas with independent nodes.

Corrected focused I131 validation:

- workflow: `Pass 195 I131 Repair Validation`
- run: `32962479673`
- job: `98157668867`
- result: **SUCCESS**
- passed immutable V1 provenance, repaired Python compilation, Storybook syntax, historical Pass195 tests, and all I131 repair regressions.

Corrected established Pass195 validation:

- workflow: `Pass 195 Kimi K3 Content Engine`
- run: `32962479406`
- job: `98157668261`
- result: **SUCCESS**
- passed immutable V1 provenance, V1/V2/API/test compilation, Storybook syntax, historical Pass195 tests, and I131 repair regressions.

## Final seal requirement

I131 is not frozen until the dedicated cumulative workflow passes both exact and synthetic lanes on the final documentation-inclusive branch head. The final workflow must prove:

- frozen I130 ancestry and accepted Pass195 merge ancestry;
- immutable V1 provenance and exact repaired-source identities;
- strict Python/JavaScript compilation;
- the historical and I131 repair regressions;
- cumulative C11 exact ABI plus C/C++ I131 conformance;
- kernel-derived Pass195 membrane preflight;
- preserved frozen Pass196/I130 successor membrane;
- no approximate or accidental native-authority expansion;
- exact/synthetic evidence artifact emission.

After both lanes are terminal green, freeze the exact head and record run/job/artifact receipts in PR metadata only. Do not mutate repository files after freeze and do not merge without explicit authorization.
