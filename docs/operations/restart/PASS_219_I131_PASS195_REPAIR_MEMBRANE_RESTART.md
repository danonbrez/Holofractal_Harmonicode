# Pass 219 I131 / inherited Pass 195 repair membrane — restart record

Status: `CENSUS_COMPLETE_ENOUGH_TO_IMPLEMENT — REPAIR_AND_MEMBRANE_PENDING`

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass219-iteration131-pass195-repair-membrane`
- Intended target: `main`
- Frozen predecessor I130: `69743440249dd7a05aa2b4096482d248973f239e`
- Frozen predecessor PR: `#328`
- Historical Pass 195 implementation PR: `#117`
- Accepted Pass 195 merge: `8bcc0921555ecface13113c8a2620415ddb3fdf1`
- Merge authorization: NOT GRANTED

## Classification

`INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE`

Pass 195 is not merely missing a Pass219 membrane. Historical PR #117 carries twelve unresolved review findings, and the current frozen I130 head still reproduces multiple findings in live Pass195 sources. No later Pass195/Kimi K3 repair commit was found by commit census.

## Historical review findings to repair

1. `3696077892` — validate provider JSON against the declared plan schema before normalization/admission.
2. `3696077894` — bind reference-image content and normalized constraints into proposal/input receipt identity.
3. `3696077896` — Storybook client must reject a plan when governed ingress failed.
4. `3696077898` — bind configured/returned model identity into the hashed plan.
5. `3696077899` — apply template before custom style overrides.
6. `3696077901` — require authorization and bounded throttling/concurrency for paid generation.
7. `3696077903` — bound constraint count, per-item size, and aggregate UTF-8 bytes.
8. `3696077905` — constrain handoff title/story text to downstream Storybook limits.
9. `3696077907` — align generated style ranges with Storybook control ranges.
10. `3696077910` — require separately admitted IMAGE_ANALYSIS capability when reference images are sent.
11. `3696077912` — bind the authorized runtime tick to its graph state before provider await; do not ingest a later global state.
12. `3696077914` — recompute status/health integrity hash over the final returned health object.

## Current evidence

Current frozen-head `hhs_backend/api/kimi_k3_content_routes.py` still has unbounded `constraints`, no explicit paid-route auth/throttle, and exports/ingests runtime state only after the external provider await.

Current frozen-head `applications/storybook_reel_studio/kimi-content-engine.js` still applies style overrides before template dispatch and accepts any returned `plan` without checking the governed `ok`/ingress decision.

Current frozen-head `hhs_backend/runtime/hhs_kimi_k3_content_engine_v1.py` remains the historical V1 implementation and still carries several review-visible schema/provenance/integrity defects. V1 must remain immutable provenance; repairs should be additive in V2 where practical.

## Planned implementation

- preserve accepted V1 source identity;
- add `hhs_backend/runtime/hhs_kimi_k3_content_engine_v2.py` with validated provider-plan schema, final-health hashing, full input binding, model binding, multimodal capability admission, and downstream-safe handoff normalization;
- route production Pass195 API through V2;
- add strict constraint budgets, explicit operator authorization boundary, bounded concurrency/rate guard, and immediate authorized-tick graph ingestion;
- repair Storybook client ingress decision handling and template/override order;
- add dedicated Pass195 I131 repair regressions;
- add C ABI / C++ RNA inherited Pass195 membrane `1.31` and cumulative Python membrane;
- wire Pass195 into the cumulative exact ABI immediately after Pass196 in reverse-pass order;
- add exact/synthetic dedicated I131 workflow and evidence artifact;
- preserve Pass196/I130 successor membrane and singleton VM81 authority;
- create/update draft PR only after repository-visible validation reaches a bounded ready state.

## Validation plan

Dependency-scoped validation only:

1. Python bytecode compilation for changed runtime/API/membrane/tests.
2. Node syntax plus focused Storybook Kimi handoff regression.
3. Pass195 historical conformance plus new I131 repair tests.
4. no approximate/native-authority escalation scans on new C/C++ membrane.
5. cumulative C11 exact ABI build and Pass195 C/C++ conformance.
6. kernel-derived Pass195 membrane preflight.
7. preserved Pass196/I130 successor membrane.
8. exact and synthetic workflow lanes on the final documentation-inclusive head.

## Environment state

No local/private worktree is required for recovery. Repository-visible Git objects and GitHub Actions are the authoritative execution environment.

## Next action

Implement the twelve bounded repair-forward findings, then add and validate the Pass195 I131 membrane without modifying frozen I130 evidence.

## Blockers

No external blocker is currently known. Production Moonshot provider verification remains separately fail-closed when no protected API key is configured; it is not required to validate deterministic repair semantics or membrane authority boundaries.
