# Heroku Production Interface and Language Providers Recovery Receipt

```text
status: BLOCKED
repository: danonbrez/Holofractal_Harmonicode
authoritative_base_commit: 1fd2441e2f2bee3b1052a7d0ea081a201b759ec7
implementation_start_commit: 6873ea270e461f209bc066410e0aaaf1a38d0836
latest_implementation_commit: 0a265dae379f79e029af9128f51e451e698a3de7
branch: main
merge_target: main
merge_status: main
worktree_clean: true
worktree_note: repository changes were committed through the GitHub contents API; no private local worktree is authoritative
created_at_utc: 2026-07-29T20:55:00Z
deployment_target: holofractalharmonicode-36c9c955369d.herokuapp.com
deployment_classification: BLOCKED_UNVERIFIED_CURRENT_RELEASE
```

## Task scope

Repair the public HHS deployment so it is a production visual IDE rather than a demonstration surface, prevent blank-screen frontend failure, expose only callable features, and restore the intended language-provider hierarchy:

```text
configured Gemma model through LiteRT-LM when installed and registered
→ provider:hhs.local.text through the same LiteRT-compatible governed thread path
→ explicit provider-unavailable closure
```

The native provider requires the repository-native HHS language layers, native Hash72 authority, and an active offline-ready Pass 166 Word2Vec installation. A generic canned response or repository-search substitute is not an admissible language-model fallback.

## Completed scope

- Replaced the black-screen-prone desktop entrypoint with a boot-independent production shell.
- Added a frontend boot watchdog and visible fatal-error surface; the boot overlay no longer disappears into an unexplained black page.
- Removed the public-root particle simulation and legacy `runtime_application_missing` fallback architecture.
- Restricted visible production controls to callable assistant, governed runtime-read, capability, HARMONICODE analysis, and receipt surfaces.
- Replaced the hard-coded assistant response path with the production provider hierarchy.
- Added dynamic provider identity and provider-constrained capability resolution.
- Implemented `provider:hhs.local.text` as a LiteRT-compatible native HHS provider using the native language/reasoning layers and governed HHS tool loop.
- Preserved Gemma as the preferred provider only when the configured model alias is present in the reachable LiteRT-LM model registry.
- Bound native-provider readiness to active offline-ready Pass 166 Word2Vec state rather than module import success.
- Added production language-asset verification/install tooling.
- Added Heroku `bin/post_compile` closure for native Hash72 build and language-asset verification.
- Added dependency-scoped public production tests and frontend release gates.
- Closed superseded validation PR `#59` without merge; its repository-search fallback is non-authoritative.
- Merged the stateless-resumable delivery policy into `main`.

## Files changed from implementation start to current main

The authoritative compare range is:

```text
6873ea270e461f209bc066410e0aaaf1a38d0836
..
1fd2441e2f2bee3b1052a7d0ea081a201b759ec7
```

Changed production files:

```text
.github/workflows/hhs-runtime-os-deploy.yml
bin/post_compile
hhs_backend/api/litert_lm_assistant_routes.py
hhs_backend/heroku_server.py
hhs_backend/runtime/hhs_assistant_api_tool_gateway_v1.py
hhs_backend/runtime/hhs_capability_resolution_v1.py
hhs_backend/runtime/hhs_litert_lm_assistant_v1.py
hhs_backend/runtime/hhs_litert_lm_hhs_api_assistant_v1.py
hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py
hhs_backend/runtime/hhs_production_assistant_v1.py
hhs_gui/index.html
hhs_gui/main.tsx
hhs_gui/src/ProductionApp.tsx
hhs_gui/src/styles/production.css
hhs_gui/dist/index.html
hhs_gui/dist/assets/index-B2O9DC8C.js
hhs_gui/dist/assets/index-B2O9DC8C.js.map
hhs_gui/dist/assets/index-CljKRO-y.css
tests/test_hhs_production_public_app_v1.py
tools/install_production_language_assets.py
```

Removed obsolete generated demo/runtime-window bundle assets:

```text
hhs_gui/dist/assets/HHSCalculatorGraphProjection-DVo4ynIb.js
hhs_gui/dist/assets/HHSCalculatorGraphProjection-DVo4ynIb.js.map
hhs_gui/dist/assets/HHSCalculatorSurface-18-rA5Xo.js
hhs_gui/dist/assets/HHSCalculatorSurface-18-rA5Xo.js.map
hhs_gui/dist/assets/HHSRuntimeBreadboard-D8BV7_Rt.js
hhs_gui/dist/assets/HHSRuntimeBreadboard-D8BV7_Rt.js.map
hhs_gui/dist/assets/HHSRuntimeTransportOverlay-BMCZwigx.js
hhs_gui/dist/assets/HHSRuntimeTransportOverlay-BMCZwigx.js.map
hhs_gui/dist/assets/index-4HS-IiFC.js
hhs_gui/dist/assets/index-4HS-IiFC.js.map
hhs_gui/dist/assets/index-DYDyI50L.css
```

Operational policy/evidence files also added or updated:

```text
docs/operations/STATELESS_RESUMABLE_AGENTIC_DELIVERY_POLICY.md
docs/operations/recovery_receipts/VM81_RUNTIME_BENCHMARK_2026-07-29_BLOCKED.md
native_projects/hhs_pass159_harmonicode_toolchain/evidence/P159_AUTHORITATIVE_MAIN_CLOSURE.json
native_projects/hhs_pass159_harmonicode_toolchain/evidence/P159_COMPLETION_RECEIPT.json
```

## Commands and operations already executed

Repository-visible operations:

```text
GitHub compare 6873ea270e461f209bc066410e0aaaf1a38d0836..1fd2441e2f2bee3b1052a7d0ea081a201b759ec7
GitHub commit inspection for 0a265dae379f79e029af9128f51e451e698a3de7
GitHub commit inspection for d147eaeec4143dd68d6ee35eb69d40e9a97bfdeb
GitHub combined-status lookup for 0a265dae379f79e029af9128f51e451e698a3de7
GitHub combined-status lookup for 1fd2441e2f2bee3b1052a7d0ea081a201b759ec7
GitHub recent-PR inspection
GitHub workflow-run lookup for d448b6676edb9c18644443c1a80582ad51105e9f
GitHub workflow-run lookup for f1ed32801e3dabb80011dbad97bcb9139d70f838
GitHub PR #59 closure as superseded/non-authoritative
```

Bounded live-deployment probe:

```bash
timeout 20s curl -sS -D /tmp/hhs_headers.txt \
  -o /tmp/hhs_health.json -w '%{http_code}\n' \
  https://holofractalharmonicode-36c9c955369d.herokuapp.com/healthz
```

Captured result:

```text
exit_status: 6
http_status: 000
stderr: curl: (6) Could not resolve host: holofractalharmonicode-36c9c955369d.herokuapp.com
fallback: do not poll; validate from a networked runner or Heroku CLI and commit the result
```

## Validation results

```text
PASS: source implementation is committed on authoritative main
PASS: current main is 44 commits ahead of implementation_start_commit and 0 behind
PASS: obsolete demo bundle assets are removed from the production bundle
PASS: production frontend bundle exists on main
PASS: public assistant no longer uses the original hard-coded template response path
PASS: provider-constrained capability resolution is implemented
PASS: native HHS LiteRT-compatible provider is implemented
PASS: production language-asset installer and Heroku post-compile hook are committed
PASS: superseded PR #59 is closed without merge
PASS: historical full release gate run 30485142254 completed successfully
FAIL_SUPERSEDED: validation run 30486000818 failed on the old repository-search fallback design
NOT_CERTIFIED: run 30485142254 predates the native-provider and production installation changes
NOT_RUN_CURRENT: no complete native/backend/frontend gate has been observed for current main after commit 0a265dae379f79e029af9128f51e451e698a3de7
FAIL_EXTERNAL_STATUS: GitHub combined status reports Vercel failure for 0a265dae379f79e029af9128f51e451e698a3de7 and 1fd2441e2f2bee3b1052a7d0ea081a201b759ec7
BLOCKED: current Heroku release and live endpoint cannot be verified from this execution environment because DNS resolution failed
```

## Installation and environment state

### Native Hash72

Heroku build closure is registered in `bin/post_compile`:

```bash
make c-abi
test -s hhs_runtime/builds/libhhs_runtime.so
```

Actual execution in the current Heroku slug is not yet confirmed.

### Gemma through LiteRT-LM

Readiness requires all of the following:

```text
litert-lm executable or external LiteRT-LM service available
HHS_LITERT_LM_BASE_URL reachable
HHS_LITERT_LM_MODEL registered by GET <base_url>/models
configured model alias present in the returned model registry
```

Default configured alias in the production installer is `gemma4-12b`. Current Heroku registry state is unknown.

### Native HHS language provider

Readiness requires:

```text
native HHS language layers import and self-check
native Hash72 runtime authority available
Pass 166 Word2Vec active_model_id present
Pass 166 Word2Vec offline_ready == true
```

Current Heroku Word2Vec state is unknown.

### Required authoritative Word2Vec configuration

No source may be invented. Installation requires a pinned manifest supplied through exactly one of:

```text
HHS_WORD2VEC_MANIFEST
HHS_WORD2VEC_MANIFEST_JSON
```

The manifest must bind the source URI, exact byte length, SHA-256, license identity, file format, vector dimensions, vocabulary count, and package/model identity. The deployment must also set:

```text
HHS_WORD2VEC_ACCEPT_LICENSE=1
```

When production availability is mandatory, set:

```text
HHS_PRODUCTION_REQUIRE_ASSISTANT=1
```

This causes build/install closure to fail instead of deploying an assistant with neither provider ready.

## Remaining scope

- Run the complete release gate against current `main` after `0a265dae379f79e029af9128f51e451e698a3de7`.
- Confirm Pass 166 acquisition uses resumable transfer, durable partial files, checksum verification, bounded timeouts, captured logs, and idempotent restart behavior for the selected manifest source.
- Configure and verify the authoritative Word2Vec manifest and license acceptance in Heroku, or configure a reachable LiteRT-LM Gemma registry.
- Confirm `bin/post_compile` executes successfully in the Heroku build.
- Confirm at least one production assistant provider reports ready.
- Deploy the current authoritative `main` release.
- Verify `/healthz`, `/api/assistant/health`, `/api/assistant/tools`, `/api/product/capabilities`, `/api/assistant/chat`, `/api/runtime/read/state`, and the public root in a real browser.
- Verify two materially different user queries receive materially different provider-grounded responses and receipts.
- Verify no suggestion is auto-submitted and no canned response is emitted.
- Verify the production UI mounts on mobile and desktop without a blank screen.
- Record Heroku release number, commit SHA, dyno state, HTTP results, browser console results, assistant provider selected, Word2Vec model identity, and receipt hashes in a completion receipt committed to main.

## Blockers

```text
1. No networked execution surface is currently available to verify the public Heroku endpoint.
2. Current Heroku config vars and release SHA are not visible through the connected GitHub interface.
3. No authoritative Word2Vec manifest/model identity was supplied in this task context.
4. No post-0a265 complete release-gate run has been observed.
5. Vercel status is failing; Heroku is the intended target but its current release remains unverified.
```

## Last command

```text
last_command: timeout 20s curl -sS -D /tmp/hhs_headers.txt -o /tmp/hhs_health.json -w '%{http_code}\n' https://holofractalharmonicode-36c9c955369d.herokuapp.com/healthz
last_exit_status: 6
captured_output: HTTP 000; DNS resolution failure
fallback_taken: stop polling and commit a blocked recovery receipt
```

## Exact resumable validation action

Run from a networked Linux environment with Git, Python 3, GCC, Make, Node.js 22, npm, and Heroku CLI. Every potentially blocking command is bounded and logs stdout/stderr.

```bash
set -euo pipefail

REPO='https://github.com/danonbrez/Holofractal_Harmonicode.git'
COMMIT='1fd2441e2f2bee3b1052a7d0ea081a201b759ec7'
APP='holofractalharmonicode-36c9c955369d'
WORKDIR='Holofractal_Harmonicode_production_resume'

rm -rf "$WORKDIR"
timeout 180s git clone --filter=blob:none "$REPO" "$WORKDIR" \
  >clone.stdout 2>clone.stderr
cd "$WORKDIR"
git checkout --detach "$COMMIT"
mkdir -p logs evidence

# Record environment identity.
{
  git rev-parse HEAD
  python3 --version
  gcc --version | head -n 1
  node --version
  npm --version
  heroku --version
} > evidence/environment.txt 2>&1

# Native authority.
timeout 300s make c-abi \
  >logs/c-abi.stdout 2>logs/c-abi.stderr
test -s hhs_runtime/builds/libhhs_runtime.so
sha256sum hhs_runtime/builds/libhhs_runtime.so \
  >evidence/native_runtime.sha256

# Production language assets. The Word2Vec manifest must already be configured
# in the environment or Gemma must be reachable through LiteRT-LM.
timeout 1800s python3 tools/install_production_language_assets.py \
  --install-if-configured --require-assistant \
  >logs/language-assets.stdout 2>logs/language-assets.stderr
cp .hhs/production_language_assets_status.json \
  evidence/production_language_assets_status.json

# Dependency-scoped backend validation.
timeout 900s python3 -m pytest -q \
  tests/test_hhs_production_public_app_v1.py \
  tests/test_hhs_litert_lm_assistant_v1.py \
  >logs/backend-tests.stdout 2>logs/backend-tests.stderr

# Frontend validation and build.
cd hhs_gui
timeout 600s npm install --no-audit --no-fund \
  >../logs/npm-install.stdout 2>../logs/npm-install.stderr
timeout 600s npm run test:e2e:source \
  >../logs/frontend-source-e2e.stdout 2>../logs/frontend-source-e2e.stderr
timeout 600s npm run test:workspace:source \
  >../logs/frontend-workspace.stdout 2>../logs/frontend-workspace.stderr
timeout 600s npm run build \
  >../logs/frontend-build.stdout 2>../logs/frontend-build.stderr
cd ..

test -s hhs_gui/dist/index.html
grep -q 'HHS Runtime OS' hhs_gui/dist/index.html
grep -q 'frontend_boot_timeout' hhs_gui/dist/index.html
! grep -R 'runtime_application_missing' hhs_gui/dist

# Deploy exact commit/repository state through the connected Heroku application.
timeout 300s heroku git:remote --app "$APP" \
  >logs/heroku-remote.stdout 2>logs/heroku-remote.stderr
timeout 1800s git push heroku HEAD:main \
  >logs/heroku-deploy.stdout 2>logs/heroku-deploy.stderr
timeout 120s heroku ps:scale web=1 --app "$APP" \
  >logs/heroku-scale.stdout 2>logs/heroku-scale.stderr
timeout 180s heroku ps:wait --app "$APP" \
  >logs/heroku-wait.stdout 2>logs/heroku-wait.stderr
heroku releases --app "$APP" >evidence/heroku-releases.txt 2>&1
heroku ps --app "$APP" >evidence/heroku-ps.txt 2>&1

# Bounded live API checks.
for path in \
  /healthz \
  /api/assistant/health \
  /api/assistant/tools \
  /api/product/capabilities \
  /api/runtime/read/state; do
  safe_name="$(printf '%s' "$path" | tr '/' '_' | sed 's/^_//')"
  timeout 30s curl --fail-with-body --show-error --silent \
    "https://${APP}.herokuapp.com${path}" \
    >"evidence/${safe_name}.json" \
    2>"logs/${safe_name}.stderr"
done

# Two distinct assistant turns must not collapse to one template.
timeout 60s curl --fail-with-body --show-error --silent \
  -H 'Content-Type: application/json' \
  -d '{"project_id":"project:production-verify","title":"Production verification","content":"List the active kernel invariants."}' \
  "https://${APP}.herokuapp.com/api/assistant/chat" \
  >evidence/assistant_turn_1.json 2>logs/assistant_turn_1.stderr

timeout 60s curl --fail-with-body --show-error --silent \
  -H 'Content-Type: application/json' \
  -d '{"project_id":"project:production-verify","title":"Production verification","content":"Explain the installed Word2Vec provider state."}' \
  "https://${APP}.herokuapp.com/api/assistant/chat" \
  >evidence/assistant_turn_2.json 2>logs/assistant_turn_2.stderr

python3 - <<'PY'
import json
from pathlib import Path
one = json.loads(Path('evidence/assistant_turn_1.json').read_text())
two = json.loads(Path('evidence/assistant_turn_2.json').read_text())
a = str((one.get('assistant_message') or {}).get('content') or '')
b = str((two.get('assistant_message') or {}).get('content') or '')
assert a.strip(), one
assert b.strip(), two
assert a != b, 'assistant responses collapsed to the same template'
assert 'must be attached before inference can execute' not in a.lower()
assert 'must be attached before inference can execute' not in b.lower()
assert one.get('runtime_mutation_admitted') is not True
assert two.get('runtime_mutation_admitted') is not True
PY

# Preserve reproducible evidence identities.
find evidence logs -type f -print0 | sort -z | xargs -0 sha256sum \
  >evidence/SHA256SUMS
```

## Defined fallback

If the language-asset step fails:

```text
- Do not deploy.
- Preserve logs/language-assets.stderr and the generated status JSON if present.
- Identify whether the missing condition is Gemma registry reachability, LiteRT-LM installation, Word2Vec manifest, license acceptance, digest mismatch, Pass 166 activation, or native provider self-check.
- Correct only that dependency and rerun from the language-asset step.
```

If Heroku deploy or boot fails:

```text
- Capture `heroku releases`, `heroku ps`, and `heroku logs -n 500` with bounded CLI timeouts.
- Record the release number, commit SHA, dyno transition, and first traceback/error code.
- Roll back to the last known working release only when the current release cannot be repaired in place.
- Commit a new FAILURE or BLOCKED receipt before stopping.
```

## Required closure after resumption

```text
IMPLEMENT OR REPAIR ONLY THE IDENTIFIED DEPENDENCY
→ RUN THE COMPLETE CURRENT RELEASE GATE
→ COMMIT ANY REPAIR
→ VERIFY MAIN
→ DEPLOY EXACT MAIN COMMIT
→ VERIFY HTTP + BROWSER + ASSISTANT + RECEIPTS
→ COMMIT SUCCESS OR FAILURE RECEIPT
→ RETURN USER-FACING COMPLETION RESPONSE
```
