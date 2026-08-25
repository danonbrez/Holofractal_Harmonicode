# Pass 219 I130 / inherited Pass 196 repair membrane — restart record

Status: `IMPLEMENTED — SQUASH-AWARE DOCUMENTATION-INCLUSIVE EXACT/SYNTHETIC RESEAL PENDING`

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass219-iteration130-pass196-repair-membrane`
- Draft PR: `#328`
- Intended target: `main`
- Frozen predecessor I129: `40e6e07d5f4a401541a6255339223e853846e713`
- Main at branch creation / PR base: `634db40aaf57ec087b7353d6d9205d896622adb4`
- Historical Pass 196 implementation PR: `#128`
- Historical Pass 196 reviewed head: `0142d9a6199f8acf9f23e287f471e6d80b9acd2a`
- Accepted Pass 196 implementation merge: `37687d479f2a9f1d996d225a4ba3556d9db72a86`
- PR #128 squash-aware merge base: `1d3c7588a242e3a83304f5083c2ec5a974f19399`
- Historical DigitalOcean topology repair PR: `#130`
- Historical topology repair head: `a2c21e4dab7a0dcb5e3366db2f817b023d413231`
- Accepted topology-repair merge: `959729c9070399fcdf0015702cd8777079e05dcc`
- PR #130 squash-aware merge base: `dd7f6aec3408c807c1cde0d6770aefe610c27e29`
- First complete documentation-inclusive membrane head: `cb29471a906d88d8b08cf516b2d2e009d23172f2`
- Squash-lineage workflow repair commit: `f52c0e6fff06158170547a457d26166c14695ff3`
- Merge authorization: NOT GRANTED

## Classification

`INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE`

Historical PR #128 contains ten review findings. Current main had already repaired the service-state provisioning finding through `StateDirectory=hhs`; I130 repair-forwards the other nine findings while preserving the accepted V1 implementation as immutable provenance.

## Historical review findings and disposition

1. `3699626177` — direct runtime vector persistence could bypass validated VM81/Hash72 admission. **REPAIRED in V2:** persistent vector admission requires a non-empty 72-character VM81-authorized Hash72 receipt.
2. `3699626180` — restart lost persisted predecessor/object lineage. **REPAIRED in V2:** latest persistent Pass174 vector object/output Hash72 is restored before append.
3. `3699626182` — test/evidence paths could satisfy executable-role classification. **REPAIRED in V2:** executable evidence must come from a non-test/non-evidence artifact.
4. `3699626186` — browser registry projection was register-once and stale. **REPAIRED:** validated projection refresh overlay updates the same Pass161 registry read surface through `P161_REPLAY` while rejecting type/authority escalation.
5. `3699626190` — canonical manifest identity contained host-specific repository root and worker count. **REPAIRED in V2:** host diagnostics are excluded from the hashed canonical body.
6. `3699626194` — hashing and classification could read different bytes. **REPAIRED in V2:** a single read supplies both digest and decoded classification text; live changes fail closed.
7. `3699626196` — service state directory ownership/provisioning. **ALREADY REPAIRED AND PRESERVED:** current service uses `StateDirectory=hhs` with `/var/lib/hhs/pass196`.
8. `3699626198` — tool `persist_vector` used Python truthiness coercion. **REPAIRED:** production route uses `StrictBool` and rejects non-boolean tool values.
9. `3699626201` — failed rescan could leave prior closed manifest visible as current OK evidence. **REPAIRED in V2:** current state becomes `QUARANTINED`; last-good evidence is historical only.
10. `3699626204` — tool invocation mapped fewer scan failures than direct `/scan`. **REPAIRED:** both mutation paths use the same governed scan-error mapper.

## Accepted and repaired source identities

Immutable accepted V1 runtime:

- `hhs_backend/runtime/hhs_pass196_integrated_environment_v1.py`
- blob `d2cff008db58a29bf27be20cb3547b9e0018f5e1`

Repaired I130 identities:

- V2 runtime `hhs_backend/runtime/hhs_pass196_integrated_environment_v2.py` — blob `196b1fbdbbb3610ccb47e7fd638d4c3f2cdc67f6`
- production API `hhs_backend/api/pass196_integration_routes.py` — blob `39187c3376591c64758019090d9b115c6a43f6ee`
- browser integration `applications/holofractal_harmonizer/src/pass196-integration.mjs` — blob `1503903c844c9e601133853eed9ed597f6fd2274`
- projection overlay `applications/holofractal_harmonizer/src/pass196-projection-refresh.mjs` — blob `44254e10f90e929a4f8c1a18a75b3ca14a2c05ed`
- repair regression `tests/test_hhs_pass196_i130_repair_v2.py` — blob `d0860d89cd8abe596f49c73b7e544511cdaba5d0`
- repair workflow `.github/workflows/pass196-i130-repair-validation.yml` — blob `7a19d3e7faab6e7210e156026300e96550b9afcb`

## Native I130 membrane

Implemented files:

- `hhs_runtime/include/hhs_pass219_inherited_pass196_1_30.h`
- `hhs_runtime/include/hhs_pass219_inherited_pass196_1_30.hpp`
- `hhs_runtime/c/hhs_pass219_inherited_pass196_1_30.inc`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i130_pass196.py`
- `tests/pass219/test_pass219_inherited_pass196_1_30.c`
- `tests/pass219/test_pass219_inherited_pass196_1_30.cpp`
- `tests/pass219/test_pass219_cumulative_pass196_membrane_i130.py`
- `docs/pass196/PASS_219_I130_INHERITED_EXPOSURE.md`
- `.github/workflows/pass219-cumulative-pass196-repair-membrane-i130.yml`

Aggregate wiring:

- `hhs_runtime/include/hhs_runtime_exact_abi.h` includes Pass196 immediately after Pass197.
- `hhs_runtime/c/hhs_runtime_exact_abi.c` includes the I130 implementation in the same reverse-pass order.

Public C binder: `hhs_exact_pass219_bind_pass196_repaired_integrated_environment`

C++ RNA facade: `hhs::rna::InheritedPass196RepairedIntegratedEnvironment`

## Authority boundary

I130 creates no new candidate authority, canonical mutation authority, persistence authority, Hash72 clock authority, C++ mutation authority, VM81 mutation authority, vector-source authority, or browser projection authority.

Singleton VM81 canonical authority remains inherited. Encrypted Pass196 vector persistence remains inherited evidence/persistence admitted only behind a valid VM81-authorized Hash72 receipt. The vector store is not source authority and the frontend is not mutation authority.

## Hosted validation history

### Focused repair gate

Initial focused run `32874918615`, job `97890436626`, failed only in the new browser-projection test harness: `.map(structuredClone)` caused Node 22 to pass the array index as the structuredClone options argument. Repair-forward commit `08cd5519a2082772b1f2050030f535321c795126` changed only that harness invocation.

Corrected focused repair validation:

- workflow: `Pass 196 I130 Repair Validation`
- run: `32900368913`
- job: `97972541699`
- result: **SUCCESS**
- all provenance, Python compilation, browser projection, authority source gates, historical Pass196 lifecycle, I130 repair regressions, and route-composition steps passed.

### First complete I130 membrane seal

Workflow run `32900896132` on head `cb29471a906d88d8b08cf516b2d2e009d23172f2` executed both lanes and failed at the first lineage step before implementation/ABI tests:

- exact job `97974255081` — FAILURE at `Prove frozen I129 and accepted Pass 196 lineage`
- synthetic job `97974255261` — same failure

Executed defect: the workflow incorrectly required the reviewed heads of squash-merged PR #128 and PR #130 to be literal ancestors of their accepted squash commits.

Repository-proven squash identities:

- `merge-base(0142d9a6199f8acf9f23e287f471e6d80b9acd2a, 37687d479f2a9f1d996d225a4ba3556d9db72a86) = 1d3c7588a242e3a83304f5083c2ec5a974f19399`
- `merge-base(a2c21e4dab7a0dcb5e3366db2f817b023d413231, 959729c9070399fcdf0015702cd8777079e05dcc) = dd7f6aec3408c807c1cde0d6770aefe610c27e29`

Commit `f52c0e6fff06158170547a457d26166c14695ff3` replaces only those invalid ancestor assertions with exact squash-aware merge-base assertions. Accepted-merge ancestry, runtime/membrane identities, and authority semantics are unchanged.

## Final reseal requirement

The next exact branch head created by this restart-record update is the documentation-inclusive final reseal candidate. The dedicated workflow `Pass 219 Cumulative Pass 196 Repair Membrane I130` must pass both exact and synthetic lanes on that exact head.

Required lanes prove:

- frozen I129 ancestry;
- accepted Pass196 implementation and topology ancestry;
- squash-aware reviewed-head identity through the two exact merge bases above;
- immutable V1 provenance and exact repaired source identities;
- preserved service-state topology;
- Python/JavaScript compilation;
- no approximate native authority or accidental authority exports;
- strict cumulative C11 exact ABI build;
- C and C++ I130 conformance;
- kernel-derived Pass196 membrane preflight;
- historical Pass196 lifecycle and I130 repair regressions;
- browser projection-refresh regression;
- preserved repaired Pass197 I129 successor membrane;
- exact/synthetic evidence artifact emission.

Freeze requires both lanes terminal SUCCESS on this exact documentation-inclusive head. After a successful final seal, do not mutate repository files; record the final run/job evidence in PR #328 metadata only.

## Environment state

No local/private worktree is required for recovery. Repository-visible Git objects and GitHub Actions are the authoritative execution environment.

## Next action

1. identify the exact head created by this restart-record update;
2. wait for the dedicated I130 exact/synthetic reseal on that head;
3. if a lane fails, inspect the executed failing step/log and repair only that defect;
4. when both lanes are terminal green, update PR #328 metadata to `PASS_219_I130 = FROZEN` and `Pass 196 = REPAIRED_AND_WIRED` without changing repository files;
5. keep PR #328 draft/open/unmerged because merge authorization has not been granted;
6. next reverse-pass census target after I130 freeze is Pass195.

## Blockers

No implementation blocker is known. Final freeze is gated only on the documentation-inclusive exact/synthetic reseal and any evidence-backed failure it may reveal.
