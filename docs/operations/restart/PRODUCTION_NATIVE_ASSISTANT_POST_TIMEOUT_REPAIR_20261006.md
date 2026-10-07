# Production native assistant POST timeout — restartable repair (2026-10-06)

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base `main`: `ad4671f6077a8b049b3a09910fa27126bbda585d`
- Branch: `repair/production-native-first-lazy-provider-health-20261006`
- Merge target: `main`
- Triggering Exact-Main workflow run: `37551015343` (deploy job `112566306471`)
- Triggering browser acceptance artifact: `11453236259`

## Frozen evidence and current limits

The triggering Exact-Main run successfully promoted the exact source SHA and Runtime OS
bundle, verified guarded ownership, permissions, Lane 5 ingress through
`127.0.0.1:8715`, zero bypass, public HTTPS interface, and 380 service
descriptors. Deployment acceptance remained **FAILED**, because the live Chromium
run timed out at the first `POST /api/assistant/chat` response wait in
`hhs_gui/scripts/production-live-browser-verify.mjs`.

The browser evidence recorded a failed `POST /api/assistant/chat` request with
`net::ERR_ABORTED` and no HTTP 5xx. The production React client itself aborts
assistant requests after 120 seconds, ahead of the 180-second Playwright response
wait. This proves missing timely chatbot completion; it does **not** by itself
prove which server operation blocked.

Source inspection identified one unnecessary blocking dependency on the primary
production path: `ProductionAssistantService.send_message()` probes the optional
Pass 153 fallback provider's health *before* admitting even a ready native provider.
The earlier deployment-health repair already deferred optional provider fan-out
during page boot, but not during chat turns.

## Repair and exact authority preservation

1. `hhs_backend/runtime/hhs_production_assistant_v1.py`: for native-first
   deployment, defer optional Pass 153 health until the primary native model is
   offline or its turn fails. Do not alter other model-routing modes.
2. `tests/pass220/test_hhs_pass220_unified_chatbot_lane5_model_fabric.py`:
   add success-path and failover-path regressions using counting native/Pass 153
   providers and one witnessed thread.
3. This restart record preserves the investigative chain.

Native calls still pass through `HHSAPIAssistantService`, its provider proposal
and policy gate, exact Native Lean alignment, Hash72 receipts, result ingress,
and the existing VM81 / Hash216 admission boundaries. Fallback availability is
retained, not assumed. No HTTP errors, invalid receipts, failed transitions, or
missing provider admission can be converted to successful acceptance.

## Validation and closure plan

- Executed: inspected exact-main branch and workflow jobs/logs; inspected
  Playwright evidence, frontend abort timeout, assistant provider routing, and
  current tests; created this dependency-scoped repair branch.
- Pending: PR source and native-fabric tests; dependency-scoped production-root
  checks; merge only on suitable gates; verify authoritative main SHA.
- After merge: follow serialized Exact-Main deployment. Require PROMOTED
  receipt bound to main, host ingress zero bypass, public registry 380/380,
  visible Visual Program dispatch, Build, vector hydration, **both** assistant
  chat turns in Chromium, and an artifact with no unexpected browser errors.
- If the first assistant POST still hangs: inspect the live per-request backend
  trace and guarded service journal, then repair the precise blocking step.
  Do not lower the Chromium gate, waive browser errors, or lengthen timeout
  as a substitute for responsiveness.
- Existing separate failing Pass220 I003-I010 runner on base SHA reports
  13 failing tests (including stale UI expectations and Pass 148 installation);
  evaluate them against the unchanged base rather than attributing them
  automatically to this scoped repair.
- CI state, deployment result, and blockers must be appended by the next
  execution pass if work is interrupted. Only changed source/test/docs files
  belong in the repair history. No inherited ZIP artifact is rewritten.

## Next action

Open the PR, check dependency-scoped gates, repair regressions if any, then
merge/verify exact main and rerun the existing serialized delivery chain.
