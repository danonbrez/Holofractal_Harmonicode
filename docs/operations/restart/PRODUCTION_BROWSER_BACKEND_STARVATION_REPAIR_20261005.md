# Production browser backend-starvation repair — 2026-10-05

## Restart identity

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `96768a5e850c061de2baba0b2fa7e680339808fe`
- branch: `repair/production-browser-backend-starvation-20261005`
- merge target: `main`
- pull request: #718
- triggering Exact-Main run: `37326713517`
- triggering deploy job: `111819630000`

## Proven predecessor state

Exact-Main for `96768a5e850c061de2baba0b2fa7e680339808fe` completed guarded promotion and the pre-browser public verification:

- deployment contract: PASS;
- PROMOTED receipt: PASS;
- Lane 5 host ingress: PASS;
- public HTTPS Runtime OS: PASS;
- public service registry before Chromium: 380 descriptors.

The new live Chromium gate then failed. Artifact `11353246065` recorded:

- `/api/runtime/services` returned HTTP 503;
- the body began `HHS backend unavailable behind Lane 5 ingress`;
- default frontend boot also had bounded aborts/timeouts across product health, workspace session, Pass 174 status, assistant health, and acquisition reads;
- the Runtime OS itself rendered and displayed warming-safe controls.

The plaintext 503 is emitted by `hhs_backend/lane5_ingress_gateway.py` only when its private `:8080` upstream request raises `httpx.HTTPError`. The browser acceptance therefore exposed backend-serving contention rather than a JSON-parser-only defect.

## Repair

1. `hhs_backend/api/litert_lm_assistant_routes.py`
   - adds `GET /api/assistant/deployment-health`;
   - delegates to the already accepted native-only `ProductionAssistantService.deployment_health()`;
   - leaves full `GET /api/assistant/health` diagnostics unchanged.

2. `hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx`
   - ordinary production boot and polling use `/api/assistant/deployment-health`;
   - optional-provider diagnostic fan-out is no longer part of default first paint.

3. `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
   - collapsed Advanced acquisition no longer mounts `OpenSourceAcquisitionPanel`;
   - acquisition status/jobs load only after the user explicitly opens the disclosure.

4. `hhs_gui/scripts/production-live-browser-verify.mjs`
   - probes interface/service-registry reference state through the Playwright context with six bounded attempts and per-attempt evidence;
   - reads response text before JSON parsing, so plaintext 503/warming responses remain inspectable;
   - still requires the actual Chromium page to open Visual Program, render every service descriptor, expose a selectable/runnable service node, and finish with zero browser/page/network/5xx errors.

5. Source/production regressions bind the bounded route, frontend usage, lazy acquisition mount, and retry evidence.

## Changed files

- `hhs_backend/api/litert_lm_assistant_routes.py`
- `hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx`
- `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
- `hhs_gui/scripts/production-live-browser-verify.mjs`
- `hhs_gui/scripts/live-gui-e2e-source-verify.mjs`
- `tests/test_hhs_production_public_app_v1.py`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
- this restart record

## Validation performed

- source changes inspected at branch head;
- prior Source Text Integrity runs passed for the implementation commits already completed;
- PR #718 opened against exact base `96768a5e...`.

## Validation remaining

Dependency-scoped before merge:

1. Source Text Integrity on final branch head;
2. DigitalOcean Production Exact Main PR `validate-deployment-contract`;
3. Validate Full Application IDE;
4. repair-forward only concrete failures from these impacted gates.

After merge:

5. verify authoritative `main` contains the merge;
6. follow only the exact-current-main serialized production run;
7. require PROMOTED + public HTTPS Runtime OS + 380-service registry;
8. require live Chromium frontend capability projection to pass;
9. only then allow the post-verification Hash216 step;
10. if Hash216 produces a generated successor, follow only its serialized Exact-Main run to terminal convergence.

## Acceptance / blockers

Fail closed on any of:

- current main not equal to the promoted production SHA;
- missing PROMOTED receipt;
- Lane 5 ingress failure;
- public Runtime OS or service-registry failure;
- browser Visual Program not rendering all public service descriptors;
- browser page/console/network/HTTP-5xx error after bounded warm-up;
- frontend reintroduction of full optional-provider health into default boot;
- collapsed advanced acquisition performing hidden backend work.

## Next action

Observe the final-head PR gates. Repair only failures attributable to this change. When the impacted gates are green, merge #718, verify main, and follow the serialized Exact-Main/browser/Hash216 chain to terminal closure.
