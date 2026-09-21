# DigitalOcean Runtime OS Production Composition Repair — 2026-09-20

## Restart identity

- Repository: danonbrez/Holofractal_Harmonicode
- Base/main: 59e0d7abfa1e4f9ee60bb0f30a0f8eb225cc6226
- Branch: repair/digitalocean-runtime-os-production-composition
- Merge target: main
- Failed production workflow: DigitalOcean Production Exact Main 35548802545
- Failed deploy job: 106179665780
- Open Stack at the same main head: green
- Scope: deployed Runtime OS composition/liveness only; no VM81, Hash72,
  Hash216, RNA, Lane 5, or canonical mutation authority changes.

## Observed production failure

The exact-main deployment reached the DigitalOcean host, claimed updater
ownership, staged the SHA-bound Runtime OS bundle, built the native runtime,
validated Pass 205, and booted the exact candidate
59e0d7abfa1e4f9ee60bb0f30a0f8eb225cc6226 on port 18080.

The candidate log then showed inherited Pass 174 boot metadata:

- public_interface = HHS_SAFE_OPEN_CLOUD_COMPUTER_IDE
- public_asset_root = applications/holofractal_harmonizer under the candidate
  worktree
- application_ide_is_public_root = true
- authority_ready = false
- ready = false

The candidate successfully answered /api/system/status and /, but validation
did not progress to a completed /health request before the guarded transaction
failed and promotion was withheld. Public HTTPS verification was therefore
skipped.

## Root cause

Two composition contracts were inconsistent.

First, application_ide_server documented /health and /api/health as bounded,
dependency-light liveness, but it only installed those routes if no inherited
route already existed. hhs_backend.server already owns /health and its handler
serializes deep runtime, graph, emulator, websocket, and workflow state.
Because FastAPI resolves the first matching route, the historical heavyweight
handler remained authoritative in the production composition.

Second, runtime_os_application_server_full correctly projected the Runtime OS
after inheriting the application IDE, but it left PASS174_BOOT_STATE carrying
the predecessor Harmonizer public-root metadata. That made candidate diagnostics
report a public-root state different from the final Runtime OS projection.

The production entrypoint also lacked an import-time fail-closed assertion that
the final route graph actually contained the Runtime OS mount and no predecessor
public-root mount.

## Repair

1. hhs_backend/application_ide_server.py
   - removes inherited GET/HEAD handlers at exactly /health and /api/health;
   - installs application_ide_liveness as the sole GET/HEAD owner of both
     production liveness paths;
   - keeps detailed runtime diagnostics on their existing explicit runtime
     status surfaces;
   - projects the final PASS174 public-interface metadata through the liveness
     response instead of hard-coding the predecessor interface identity.

2. hhs_backend/runtime_os_application_server_full.py
   - after project_runtime_os, updates only public-projection metadata in
     PASS174_BOOT_STATE;
   - records HHS_VISUAL_RUNTIME_OS_WORKSPACE, the exact RUNTIME_OS_ROOT,
     application_ide_is_public_root=false,
     runtime_os_is_public_root=true, and
     legacy_harmonizer_is_public_root=false;
   - leaves readiness and runtime authority fields untouched.

3. hhs_backend/production_visual_server.py
   - fails closed at import if the expected Runtime OS mount is missing;
   - fails closed if any predecessor public-root mount remains;
   - requires /api/interface/status and the selected Runtime OS index.

4. deployment/digitalocean/guarded_auto_update/validate-candidate.sh
   - probes bounded /api/health instead of the inherited aggregate /health;
   - verifies /api/interface/status immediately after the root document and
     before slower product/Pass probes.

5. tests/test_runtime_os_production_root.py
   - proves /health and /api/health resolve exactly once to the bounded
     application liveness handler;
   - proves PASS174 public metadata matches the final Runtime OS projection;
   - proves the exact production gateway has no predecessor root authority;
   - proves candidate validation orders bounded liveness/interface checks ahead
     of slower status probes.

## Repository-visible commits

- dfa2e1457f9cbc2c410fe48d77782b5b2066f008 — production liveness route
  precedence repair
- 3b26d333c69036b542e11953423bd0f6e5c7201b — final Runtime OS boot metadata
- 967940a693773c4c6a59e59ff6396722e483d2c9 — production public-root
  fail-closed assertion
- 2b620c3e7b76220bdcaff4d36ba93ce8d8072765 — final interface identity through
  liveness
- 2ef4c0ed6ed26f6e1fbc436517088e9e995d45bd — bounded candidate probe ordering
- 9c17ff50ab7a1210fdefcc3ccb8d1a38043f567d — production composition
  regressions

## Validation required

Before merge:

1. production-root regression tests;
2. guarded updater contract tests;
3. runtime OS deployment/source verification;
4. DigitalOcean pull-request deployment-contract gate;
5. no regression to the inherited API/Pass route set.

After merge to main:

1. DigitalOcean exact-main candidate validation must complete;
2. promotion receipt must identify the exact merged main SHA;
3. hhs.service must run hhs_backend.production_visual_server:app;
4. /api/interface/status must identify HHS_VISUAL_RUNTIME_OS_WORKSPACE and the
   exact versioned release asset root;
5. root HTML must contain HHS Visual Runtime OS Workspace;
6. public HTTPS verification must complete.

## Next action

Open the repair PR, run dependency-scoped CI, repair forward only impacted
composition/deployment failures, then merge when green and verify exact-main
promotion plus public HTTPS.


## PR checkpoint

- PR: #526
- current head: 2ca36e949c850775b8e6c6c9cf7f2ad7dad7f758
- base: main 59e0d7abfa1e4f9ee60bb0f30a0f8eb225cc6226
- branch divergence at checkpoint: 0 behind main
- PR state: draft pending dependency-scoped validation

Additional repair commit:

- 2ca36e949c850775b8e6c6c9cf7f2ad7dad7f758 — preserves the production
  gateway's frozen source-selection token while retaining the new import-time
  Runtime OS projection assertion.

Queued exact-head checks:

- DigitalOcean Production Exact Main PR contract:
  run 35558731171
- Validate HHS Runtime OS Production Root:
  run 35558731082

A separate branch-push Pass205 workflow reports an immediate workflow-level
failure without a job on this repair branch. It is not used as evidence for
this composition repair unless dependency-scoped validation demonstrates that
the changed production files caused it.

Per the forward-progress rule, the implementation is repository-visible and
restartable while the two relevant deployment gates wait for runners.


## Validation-timeout repair

The failed exact-main transaction began candidate validation at approximately
00:51:32 UTC and terminated at approximately 00:56:57 UTC. The current updater
default is 3600 seconds, but install.sh previously preserved an existing
HHS_VALIDATE_TIMEOUT_SECONDS value when /etc/hhs/guarded-update.env already
existed. Therefore a historical shorter host override could continue governing
new exact-main promotions indefinitely.

Repair-forward commit:

- c9d8846b4cd3deab4fb12bf49193bc39cac9eda9 — on promotion, normalize
  HHS_VALIDATE_TIMEOUT_SECONDS to at least 3600 seconds while preserving any
  larger operator-configured bound.
- ed6932138ca2a71f19c2cc27ed8d69dccd386f62 — contract regression for the
  timeout normalization.

This does not weaken validation or convert timeout into success. It only ensures
the current bounded validator receives its intended production budget rather
than an inherited shorter deployment-era value.


## Final implementation checkpoint before CI

Implementation head before this restart-record commit:

- 153ad50fb18bf97dd24f9633304bda5c357373cd
- base main: 59e0d7abfa1e4f9ee60bb0f30a0f8eb225cc6226
- PR: #526
- branch: repair/digitalocean-runtime-os-production-composition
- merge target: main

Additional repository-visible commits after the initial PR checkpoint:

- c9d8846b4cd3deab4fb12bf49193bc39cac9eda9 — normalize stale production
  HHS_VALIDATE_TIMEOUT_SECONDS to a minimum of 3600 seconds during promotion;
- ed6932138ca2a71f19c2cc27ed8d69dccd386f62 — add guarded-updater timeout
  normalization regression;
- 153ad50fb18bf97dd24f9633304bda5c357373cd — align the frozen Pass176
  degraded-mode liveness source contract with sole-owner bounded liveness.

Relevant exact-head validation launched for 153ad50f:

- Validate HHS Runtime OS Production Root: run 35558862710 — queued;
- DigitalOcean Production Exact Main PR contract: run 35558862714 — queued;
- Validate Full Application IDE: run 35558862585 — queued.

Validation still required:

1. the three dependency-scoped runs above must complete successfully;
2. PR #526 must then be marked ready and merged to main;
3. the resulting exact-main DigitalOcean workflow must promote the merged SHA;
4. candidate /api/health must return bounded liveness before timeout;
5. /api/interface/status and / must prove the versioned Runtime OS root;
6. systemd production entrypoint must remain
   hhs_backend.production_visual_server:app;
7. public HTTPS Runtime OS verification must run and pass.

No merge or production promotion has been claimed at this checkpoint.

## Exact-head CI repair after 646d4df

At head 646d4df7d381b662f9f934db42e1e41b46b66ca5:

- DigitalOcean Production Exact Main PR contract 35558948261: SUCCESS.
- Validate Full Application IDE 35558948175: SUCCESS.
- Validate HHS Runtime OS Production Root 35558948258: FAILURE only in the
  dependency-scoped pytest step; all build, source, compile, public-root, and
  route-ordering steps before it passed.

The two failing regressions exposed test/import-order details rather than a
canonical runtime-authority failure:

1. runtime_os_visual_server could be imported after the full Runtime OS
   application had already been composed. Because all HHS projections share
   the same inherited FastAPI object, the reduced visual module could then
   replace the higher-order application public-root mount. Repair
   f6efd048a89e701b2d9fffe6b4c79101b8259275 makes the reduced projection adopt
   the already-installed application mount name when present before calling
   project_runtime_os, preventing import-order downgrade of public-root
   authority.

2. The guarded-validator source regression searched for a quoted path beginning
   immediately at /api/health, while the actual shell line correctly contains
   the absolute candidate URL before that path. Repair
   39065f0c9c93c3d11bbf141d87e894e44c3cfdd4 checks the stable path/output
   fragment and preserves the same ordering assertions.

Next validation target is the exact branch head after this checkpoint. Do not
merge until Runtime OS Production Root, DigitalOcean PR contract, and Full
Application IDE all pass on the same head.
