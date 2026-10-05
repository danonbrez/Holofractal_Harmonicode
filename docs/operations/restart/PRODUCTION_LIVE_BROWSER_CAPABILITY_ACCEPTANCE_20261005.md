# Production Live Browser Capability Acceptance Restart Record — 2026-10-05

## Restart identity

- repository: `danonbrez/Holofractal_Harmonicode`
- base authoritative main: `a908e987335983451371a1d61df8438a5b9bbe54`
- repair branch: `repair/production-live-browser-capability-20261005`
- merge target: `main`
- prior frozen checkpoint: `checkpoint/serialized-delivery-20261005-0929`
- prior checkpoint commit: `b85a65b6d38e9212a8e79b7ea032b30c07ecefea`

## Resumed delivery state

Authoritative main was re-resolved before continuing and remained:

`a908e987335983451371a1d61df8438a5b9bbe54`

The final Exact-Main run for that SHA was already successful:

- run: `37311090084`
- deploy job: `111766510668`
- public Runtime OS/service-registry verification: PASS
- public service count: `380`

The post-promotion Hash216 step was inspected directly in deploy-job logs. Because
the current SHA is itself the generated dependency-index successor, the workflow
correctly emitted:

`HHS_EXACT_MAIN_HASH216_INDEX_TERMINAL_GENERATED_SUCCESSOR=a908e987335983451371a1d61df8438a5b9bbe54`

No additional Hash216 run was required. Production delivery convergence is
therefore closed at the branch base.

## Current repair objective

Close the remaining frontend acceptance gap with real-browser evidence that every
descriptor returned by the public production runtime registry is actually exposed
through the Runtime OS Visual Program interface.

The frontend mechanism already exists:

- `RegistryVisualProgrammer` fetches `GET /api/runtime/services`;
- every normalized service descriptor becomes a selectable registry definition;
- service-node execution routes through `POST /api/runtime/services/dispatch`;
- the frontend remains a consumer/projection rather than canonical authority.

The missing evidence was a live exact-main browser gate over the deployed public
surface.

## Implemented changes

### `hhs_gui/scripts/production-live-browser-verify.mjs`

New Playwright acceptance runner that:

1. opens the live public Runtime OS;
2. requires the canonical Runtime OS and product workspace;
3. fetches live `/api/interface/status` and `/api/runtime/services` through the
   browser origin;
4. requires the public asset root to contain the exact promoted SHA;
5. requires browser-observed service count to equal the pre-browser public probe;
6. requires unique names for every public service descriptor;
7. navigates to `Visual Program`;
8. waits for the live registry to report the full backend-service count;
9. compares every service name from the public API with rendered selectable
   registry entries;
10. requires zero missing services;
11. selects a deterministic registered service and proves it exposes a runnable
    frontend node;
12. fails on browser console errors, page errors, request failures, or HTTP 5xx;
13. writes JSON evidence and a full-page screenshot.

Success markers:

- `HHS_DIGITALOCEAN_PUBLIC_FRONTEND_CAPABILITY_SURFACE_VERIFIED=<count>`
- `HHS_DIGITALOCEAN_PUBLIC_FRONTEND_SELECTABLE_SERVICE_VERIFIED=<service>`

### `.github/workflows/digitalocean-production-main.yml`

Exact-Main now:

- syntax-checks the live browser verifier during PR deployment-contract validation;
- syntax-checks it again before sealing the frontend bundle;
- after public HTTPS/service-registry verification, installs bounded Playwright
  Chromium and runs the live production browser acceptance;
- uploads JSON + PNG browser evidence;
- queues Hash216 only after the browser capability gate succeeds.

This preserves the existing serialized `hhs-production-main-delivery` queue and
the shared host mutation lock.

### `tests/test_hhs_guarded_auto_update_contract_v1.py`

Added a dependency-scoped contract regression requiring:

- live-browser gate tokens;
- public-service probe before browser acceptance;
- browser acceptance before Hash216 queue;
- browser verification of Runtime OS identity, service-registry fetch, Visual
  Program, complete service-name coverage, guarded-dispatch identity, and
  non-authoritative frontend semantics.

## Branch commits before this restart record

- `a3ac8eba2f22c94c6d85c9735c2f91fca9070a20` — add live production frontend capability browser acceptance
- `15b40b139616ce3a5ba748ae62aef1b0b2894c67` — gate exact-main on live frontend capability projection
- `1fd216f2cbeb1a596615ea8b25ca21d1307eccdc` — validate live browser acceptance source on pull requests
- `bc97c265dd47b6b0b9fc0f2c867db77fc73bf8cc` — bind exact-main to live frontend registry coverage

Branch is four commits ahead of base and zero behind before this restart-record
commit.

## Validation done

- authoritative main re-resolved: PASS, unchanged at `a908e987...`;
- prior Exact-Main/public registry evidence rechecked: PASS;
- terminal generated-successor Hash216 behavior verified from job log: PASS;
- branch compare against base: four commits ahead, zero behind;
- changed code is dependency-scoped to Exact-Main frontend acceptance.

## Validation remaining

1. open PR to `main`;
2. require Exact-Main deployment-contract PR validation to pass, including
   `node --check` for the browser runner and the new contract regression;
3. merge after dependency-scoped validation;
4. follow only the new main Exact-Main run;
5. require live Chromium acceptance to report all public service descriptors
   rendered/selectable with no browser/runtime errors;
6. require uploaded browser JSON/PNG evidence;
7. follow the serialized Hash216 successor only if one is generated;
8. require final current-main Exact-Main closure.

## Blockers

Fail closed on:

- browser runner syntax failure;
- public asset-root SHA mismatch;
- browser registry count mismatch;
- duplicate/unnamed public service descriptors;
- any public service descriptor missing from Visual Program;
- frontend registry unavailable;
- browser console/page/network/HTTP-5xx errors;
- newer main without matching Exact-Main promotion;
- missing PROMOTED/public HTTPS/service-registry evidence.

## Next action

Open and validate the repair PR. Do not rerun predecessor deployments.
