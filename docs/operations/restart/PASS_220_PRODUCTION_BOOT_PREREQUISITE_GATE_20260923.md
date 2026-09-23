# Pass 220 Production Boot Prerequisite Gate — 2026-09-23

## Base

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `3610e36a1b66bdd4a03f92683974ab92518d7270`
- branch: `repair/pass220-production-boot-prerequisite-gate-20260923`
- target: `main`
- production host: `165.227.220.193`

## Observed failure

The public Runtime OS shell can render while live API requests report
`Failed to fetch`, `signal is aborted without reason`, and
`ASSISTANT_OFFLINE`.

A local production reproduction established that the FastAPI application boots
and serves successfully when both hard prerequisites exist:

1. `hhs_runtime/builds/libhhs_runtime.so`;
2. a readable Runtime OS release containing `index.html` and `assets/`.

Removing either prerequisite reproduces an import-time fail-closed boot failure
before uvicorn can bind the production port.

## Repository state before this repair

The guarded updater already:

- builds the native runtime during candidate validation;
- requires `libhhs_runtime.so`;
- stages/verifies a SHA-bound Runtime OS bundle;
- boots the exact production gateway against the staged bundle;
- builds the live native runtime after checkout promotion;
- activates the Runtime OS release before service start.

However, the final systemd service did not itself encode those two
prerequisites. A direct restart or live-state drift could therefore reach the
Python import chain without a local pre-start witness.

## Repair

The canonical production unit now requires:

```text
HHS_DISABLE_C_AUTOBUILD=1
ExecStartPre=/usr/local/lib/hhs-guarded-update/verify-production-prerequisites.sh
```

The pre-start gate executes as the production service user and fails before
uvicorn when any of the following is false:

- production C autobuild is disabled;
- the selected Python runtime exists;
- `libhhs_runtime.so` exists, is non-empty, and is readable;
- the shared library has no unresolved dynamic dependencies;
- the shared library can be loaded through `ctypes.CDLL`;
- both canonical ctypes bridges import with autobuild disabled;
- `HHS_RUNTIME_OS_ASSET_ROOT/index.html` is readable;
- `HHS_RUNTIME_OS_ASSET_ROOT/assets` exists and is traversable;
- `require_runtime_os_build()` succeeds.

The installer and updater both install/self-sync the gate. Candidate boot now
also runs with `HHS_DISABLE_C_AUTOBUILD=1`, so candidate validation cannot
hide a missing native build by compiling during Python import.

The live post-merge command was tightened to `make -B c-abi` before
production-language asset installation, ensuring the native runtime is rebuilt
from the exact promoted source rather than relying on an older generated file.

## Acceptance boundary

A deployment is not accepted until exact-main verification proves:

```text
systemd unit contains HHS_DISABLE_C_AUTOBUILD=1
systemd unit contains the production ExecStartPre gate
pre-start gate succeeds as user hhs
versioned Runtime OS current symlink matches target SHA
one listener exists on 127.0.0.1:8080
/api/system/status succeeds
/api/interface/status succeeds
public HTTPS Runtime OS succeeds
```

The browser frontend remains downstream of these backend/runtime prerequisites.
No degraded C-runtime import is enabled.


## Restartable checkpoint — 2026-09-23 07:11 America/New_York

### Repository identity

- branch head before this checkpoint: `a657f728a3ed25b5c71fc2c9d4df79825564e0f5`
- current `main`: `aed16cd8363bb965fce93e78cd8356053d9e1da9`
- merge base: `3610e36a1b66bdd4a03f92683974ab92518d7270`
- pull request: #559
- divergence at checkpoint: **10 commits ahead / 11 commits behind main**
- merge target: `main`

The branch must be reconciled with current main before merge. No live production
deployment claim is made from the PR validation run.

### Changed files

```text
.github/workflows/digitalocean-production-main.yml
deploy/digitalocean/hhs-pass196-integrated-environment.service
deployment/digitalocean/guarded_auto_update/hhs-guarded-update.env.example
deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh
deployment/digitalocean/guarded_auto_update/install.sh
deployment/digitalocean/guarded_auto_update/validate-candidate.sh
deployment/digitalocean/guarded_auto_update/verify-production-prerequisites.sh
docs/operations/restart/PASS_220_PRODUCTION_BOOT_PREREQUISITE_GATE_20260923.md
tests/test_hhs_guarded_auto_update_contract_v1.py
tests/test_runtime_os_production_root.py
```

### Implemented state

- canonical `hhs.service` now declares
  `Environment=HHS_DISABLE_C_AUTOBUILD=1`;
- canonical `hhs.service` now executes
  `/usr/local/lib/hhs-guarded-update/verify-production-prerequisites.sh`
  through `ExecStartPre`;
- the pre-start gate verifies the native runtime, dynamic dependencies, ctypes
  load, canonical bridge imports, Runtime OS `index.html`, Runtime OS
  `assets/`, and `require_runtime_os_build()`;
- guarded updater installation and self-sync install the pre-start verifier;
- candidate production boot runs with C autobuild disabled;
- live post-merge native build is forced with `make -B c-abi`;
- exact-main production verification is wired to re-run the prerequisite gate
  as the `hhs` service user;
- degraded C-runtime import remains disabled.

### Validation frozen at this checkpoint

Exact branch head `a657f728a3ed25b5c71fc2c9d4df79825564e0f5`:

- **Validate HHS Runtime OS Production Root**
  - run: `35843957738`
  - job: `107125470483`
  - conclusion: **SUCCESS**
  - native runtime build: success
  - TypeScript Runtime OS build: success
  - production projection compilation: success
  - public-root authority gate: success
  - dependency-scoped production-root regressions: success

- **DigitalOcean Production Exact Main**
  - run: `35843957779`
  - deployment-contract job: `107125470193` — **SUCCESS**
  - `deploy-exact-main` job: `107126343461` — **SKIPPED**
  - reason: pull-request validation does not deploy production

Other branch workflows include broad inherited successes. Two cumulative Pass
219 membrane workflows reported failures on the same head; they are not treated
as proof of a defect in this dependency-scoped production-boot repair without
an impacted-surface trace.

### Live production status

Not yet proven by this branch.

The public screenshot still showed a rendered Runtime OS shell with API failures
(`Failed to fetch`, aborted signals, assistant offline). This is consistent
with a stale/unhealthy live backend even when the browser bundle itself renders.

Required live proof after merge:

```text
git -C /opt/hhs/app rev-parse HEAD == merged main SHA
hhs.service active
ExecStartPre prerequisite gate succeeds as user hhs
/opt/hhs/app/hhs_runtime/builds/libhhs_runtime.so exists and loads
/var/lib/hhs/runtime-os/current/index.html readable
/var/lib/hhs/runtime-os/current/assets traversable
exact Runtime OS current release matches deployed SHA
exactly one listener on 127.0.0.1:8080
http://127.0.0.1:8080/api/system/status succeeds
http://127.0.0.1:8080/api/interface/status succeeds
public HTTPS system/interface/root checks succeed
```

### Remaining validation / next action

1. Reconcile branch with current main `aed16cd8363bb965fce93e78cd8356053d9e1da9`.
2. Re-run only the impacted deployment-contract and Runtime OS production-root
   gates on the reconciled exact head.
3. If green, merge PR #559.
4. Let the resulting main push execute the real `deploy-exact-main` job.
5. Verify host-side service state, prerequisite gate output, exact release
   identity, localhost port 8080, and public HTTPS.
6. Only after those receipts are green return to frontend/FastAPI adapter work.

### Blockers

- branch is currently 11 commits behind main and must be reconciled;
- live production evidence is intentionally absent until a merged-main
  deployment runs;
- no browser-side workaround or degraded runtime mode is authorized.

### Restart command surface

Resume from PR #559 / branch
`repair/pass220-production-boot-prerequisite-gate-20260923`. First compare the
branch with current main and reconcile the 11-main-commit drift. Preserve every
boot-prerequisite invariant above, rerun only the two dependency-scoped gates,
then merge and verify the real exact-main production deployment.
