# HHS Production Interface Restart Checkpoint — 2026-08-10

## Freeze identity

- Base commit: `bbe3cec241af3d7d6fb26f8f4c6b134f6a4ea486`
- Branch before this checkpoint commit: `agent/retire-legacy-html-production-mutation`
- Pre-checkpoint branch HEAD: `35aed599759e910bccfa11977662b99ffa6c2769`
- Intended merge target: `main`
- Production repository: `danonbrez/Holofractal_Harmonicode`

## Files modified on the current branch before this checkpoint

1. `scripts/complete_hhs_production_https_mobile.sh`
   - Removed the legacy `atomic_install_from_main`/Harmonizer live-checkout frontend mutation path.
   - Converted the script to TLS/Nginx edge management plus Runtime OS identity verification only.
   - Nginx application traffic is proxy-only to `127.0.0.1:8080`; the script does not serve or copy a repository UI tree.
   - Acceptance now requires `HHS_VISUAL_RUNTIME_OS_WORKSPACE`, `legacy_harmonizer_is_public_root=false`, and a versioned `/var/lib/hhs/runtime-os/releases/...` asset root.

2. `.github/workflows/hhs-production-https-mobile-closure.yml`
   - Replaced legacy Harmonizer `/src/*.mjs` acceptance with Runtime OS authority checks.
   - Added fail-closed assertions preventing reintroduction of `atomic_install_from_main`, Harmonizer source deployment, legacy `/src` browser assets, or Nginx-stop certificate renewal.

## Earlier completed and merged implementation relevant to this restart

### PR #200 — single Runtime OS production frontend authority

Merged to `main` as `4017b8d851aaf9b547818a63b7d49fe18e8216e3`.

Completed:
- bound production service to `HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/current`;
- corrected candidate validation to use `HHS_RUNTIME_OS_ASSET_ROOT` rather than the unused `HHS_RUNTIME_OS_ROOT`;
- required candidate `/api/interface/status.asset_root` to equal the exact staged Runtime OS release;
- added single-public-root route authority regression;
- added SSH keepalives to the exact-main DigitalOcean promotion;
- required exact service entrypoint, one port-8080 listener, activated versioned release, and matching local/public interface identity after promotion.

Validated before merge:
- guarded deployment contract: PASS;
- Runtime OS TypeScript build/typecheck/source tests: PASS;
- single public-root route composition: PASS;
- focused production-root pytest: PASS;
- full Chromium application/public-root boot: PASS.

### PR #201 — failed-service recovery and diagnostics

Merged to `main` as `bbe3cec241af3d7d6fb26f8f4c6b134f6a4ea486`.

Completed:
- receipt-gated recovery after `ROLLBACK_HEALTH_FAILED`;
- bounded production health window increased to 600 seconds;
- production failure diagnostics capture systemd service state, effective ExecStart/environment, port 8080 ownership, and journal;
- production service sets `HHS_COGNITION_AUTO_TICK=0` while preserving explicit cognition/runtime APIs and required startup authority behavior;
- rollback/post-merge build command moved away from historical bare `python` wrappers to stable native build plus `/opt/hhs/venv/bin/python` language-asset verification.

Validated before merge:
- guarded deployment contract: PASS;
- Pass 196 integration/runtime-bootstrap regressions: PASS;
- Runtime OS TypeScript build and production-root regression: PASS.

## Production deployment evidence already obtained

The exact-main deployment for `4017b8d851aaf9b547818a63b7d49fe18e8216e3` proved that the Runtime OS bundle was built, transferred, staged, and activated, but the service never became reachable before rollback.

The recovery deployment for `bbe3cec241af3d7d6fb26f8f4c6b134f6a4ea486` produced the decisive host diagnostics:

- `hhs.service` had nine persistent drop-ins under `/etc/systemd/system/hhs.service.d`:
  - `20-final-application-ide.conf`
  - `40-runtime-quiescence.conf`
  - `99-runtime-venv.conf`
  - `zz-runtime-state.conf`
  - `zzzz-pass209-bootstrap.conf`
  - `zzzzz-graphics-state.conf`
  - `zzzzzz-final-runtime.conf`
  - `zzzzzzz-pass-state-roots.conf`
  - `zzzzzzzz-bootstrap-safe.conf`
- Effective rollback service entrypoint was still:
  `/opt/hhs/runtime-venv/bin/python -m uvicorn hhs_backend.cached_visual_server:app --host 127.0.0.1 --port 8080 --workers 1`
  rather than the repository-canonical production entrypoint:
  `/opt/hhs/venv/bin/python -m uvicorn hhs_backend.production_visual_server:app --host 127.0.0.1 --port 8080 --workers 1`.
- Effective environment retained host override values including `HHS_RUNTIME_STATUS_PROBE=0`.
- The newest promotion failed before canonical service start because the configured production language-asset verification returned:
  `RuntimeError: production assistant installation is incomplete: configure a reachable LiteRT-LM Gemma model or install an authoritative Pass 166 Word2Vec manifest`.
- Rollback then restarted the historical overridden `cached_visual_server` service and remained unable to satisfy port-8080 health during the recorded interval.

## Diagnosis frozen at checkpoint

Two independent production authority problems are established:

1. Frontend asset authority was split between the versioned Runtime OS release system and legacy frontend mutation/deployment paths. PR #200 fixed the Runtime OS asset-root split; the current branch removes the remaining HTTPS/mobile Harmonizer mutation path.
2. Host systemd drop-ins still override the repository-controlled `hhs.service`, selecting an older Python environment/backend entrypoint and environment values. Therefore repository service deployment is not yet the effective host service authority.

A separate promotion blocker is also established: production structural deployment currently hard-requires assistant language assets even when the frontend/server deployment itself is otherwise valid.

## Commands / operations already executed

Repository/GitHub operations:
- inspected `hhs_backend/visual_server.py`, `production_visual_server.py`, `runtime_os_visual_server.py`, `runtime_os_projection.py`, `runtime_os_application_server.py`, DigitalOcean service/workflow/update scripts, and production language-asset installer;
- created and merged PR #200;
- created and merged PR #201;
- created branch `agent/retire-legacy-html-production-mutation` from `bbe3cec241af3d7d6fb26f8f4c6b134f6a4ea486`;
- updated the two current-branch files listed above;
- opened a draft PR for retiring the legacy HTML production mutation path.

CI/workflow commands already exercised in completed validation runs included:
- `bash -n` on guarded deployment shell assets;
- `python3 -m py_compile` on deployment/runtime projection modules;
- guarded deployment contract test execution;
- `npm install --no-audit --no-fund`;
- Runtime OS `npm run typecheck`;
- Runtime OS source tests and `npm run build`;
- dependency-scoped `pytest` production-root and Pass 196 regressions;
- full browser/Chromium public-root boot validation;
- exact-main Runtime OS bundle create/stage/verify/transfer operations;
- DigitalOcean guarded promotion/recovery transactions with systemd and HTTP health probes.

## Validation status at freeze

Completed successfully:
- PR #200 deployment contract and Runtime OS/public-root/browser gates;
- PR #201 deployment contract, Pass 196 integration, and Runtime OS production-root gates;
- exact Runtime OS bundle generation/staging/identity checks before host promotion.

Failed production validations/blockers:
- exact-main production health failed after Runtime OS activation;
- recovery promotion failed at production assistant language-asset verification;
- rollback health failed;
- effective host `hhs.service` remains overridden by persistent systemd drop-ins.

Not run for the current `agent/retire-legacy-html-production-mutation` branch after its latest edits:
- its PR workflow validation has not been used as a merge authority in this checkpoint;
- no production deployment from this branch has been attempted;
- no new broad repository validation is authorized by this checkpoint.

## Failed tool operation

- A GitHub code-search attempt using the literal query `--require-assistant` failed with HTTP 422 query parsing. It was not retried after the stop instruction.

## Committed versus uncommitted state

- All repository changes made through the GitHub connector are committed directly to their branches.
- There is no known uncommitted local workspace state associated with this task.
- Current branch changes before this checkpoint are committed at `021d9eba0225a15bc548c14f952e73a1f9ba709a` and `35aed599759e910bccfa11977662b99ffa6c2769`.
- This restart document is the only additional change authorized after the stop instruction.

## Exact next implementation action

Do not resume broad frontend work.

Next implementation action is narrowly scoped to production service authority:

1. Extend the guarded installer to inventory and archive `/etc/systemd/system/hhs.service.d/*.conf` before promotion.
2. Retire/mask only drop-ins that override repository-authoritative `ExecStart`, Python environment, frontend/backend entrypoint, or Runtime OS authority; preserve state-root/resource settings only if they do not conflict with the canonical unit.
3. Run `systemctl daemon-reload` and prove effective `ExecStart` is exactly `/opt/hhs/venv/bin/python -m uvicorn hhs_backend.production_visual_server:app --host 127.0.0.1 --port 8080 --workers 1` before starting promotion health checks.
4. Decouple structural server/Runtime OS promotion from `--require-assistant`: language-model/Word2Vec readiness should remain reported and separately enforceable, but absence of optional assistant hydration must not roll back an otherwise valid frontend/server deployment unless an explicit deployment contract requires assistant readiness.
5. Add dependency-scoped tests for drop-in archival/effective-unit authority and optional-vs-required assistant readiness; then perform one guarded exact-main recovery attempt.

No implementation beyond this point was performed in this checkpoint.
