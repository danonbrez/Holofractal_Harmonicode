# Production 502 Boot + Rollback Recovery Repair — 2026-09-21

## Restart identity

- Repository: danonbrez/Holofractal_Harmonicode
- Base main: baaa1799f8772631e1b8904cbc8b0621dd8d5323
- Branch: repair/production-artifact-root-and-rollback-import
- Merge target: main
- Failing exact-main deployment: run 35590348164 / job 106303141736
- Live symptom: nginx 502 Bad Gateway at 165.227.220.193
- Scope: production boot artifact-path boundary and guarded rollback recovery import path.

## Exact failure

The exact-main deploy job reached production and then hhs.service entered a
restart loop. The traceback is deterministic:

- production entrypoint: hhs_backend.production_visual_server:app
- import chain reaches hhs_runtime_api_server_v1.py
- module import executes ARTIFACT_ROOT.mkdir(...)
- ARTIFACT_ROOT was relative: demo_reports/runtime_api
- service WorkingDirectory is /opt/hhs/app
- service runs as user/group hhs under ProtectSystem=full
- /opt/hhs/app is not a writable runtime-state boundary
- result: PermissionError: [Errno 13] Permission denied: 'demo_reports'

Because the backend listener on 127.0.0.1:8080 repeatedly exited, nginx returned
502 Bad Gateway publicly.

The guarded updater then attempted rollback/recovery and exposed a second
deterministic defect:

- normalize-service-permissions.py is installed under
  /usr/local/lib/hhs-guarded-update;
- recovery derived source_root from Path(__file__).resolve().parents[3], which
  resolves to /usr when installed;
- import of hhs_runtime.hhs_unified_hash72_ledger_recovery_v1 therefore failed;
- result: ModuleNotFoundError: No module named 'hhs_runtime'.

This prevented the rollback path from restoring the service after the boot
failure.

## Repair

### Runtime API artifact root

hhs_runtime_api_server_v1.py now selects artifact storage in this order:

1. HHS_RUNTIME_API_ARTIFACT_ROOT when explicitly configured;
2. HHS_RUNTIME_OUTPUT_DIR/runtime_api when the production runtime-output
   boundary is configured;
3. historical demo_reports/runtime_api only as the local/development fallback.

Production already supplies:

HHS_RUNTIME_OUTPUT_DIR=/var/lib/hhs/data/runtime

and the guarded permission normalizer makes that boundary writable to the hhs
service identity. No repository source directory is made writable.

### Rollback recovery import root

normalize-service-permissions.py now binds source_root to the explicit
validated repository argument:

source_root = root.resolve()

and inserts that path into sys.path before importing the unified Hash72 ledger
recovery implementation. It no longer derives a repository path from the
installed helper's own /usr/local/lib location.

The helper continues to bind HHS_REPO_ROOT to the validated live checkout.

## Tests

New:

- tests/test_hhs_production_runtime_artifact_root_v1.py
  - production runtime-output path wins over read-only current working directory;
  - explicit HHS_RUNTIME_API_ARTIFACT_ROOT still overrides.

Extended:

- tests/test_hhs_digitalocean_ledger_recovery_boundary_v1.py
  - recovery import root must be root.resolve();
  - installed-helper parents[3] derivation is forbidden.

Production-root CI now executes both regressions.

## Pass 202 successor integrity

The guarded normalizer blob changed, so the current successor identity is
resealed from:

35ef0b50e92721bddf01aa9273edb58bbc12fdb3

to:

6934f540060f36ca78b6e4dc2b2461d8327f54b9

Only CURRENT_SUCCESSOR_BLOBS / current-successor workflow expectations advance.
Frozen historical Pass 202 identities remain unchanged.

## Repository-visible commits

- e28bb9c2d5d0d385749da55e031c35cdc51257b7 — production runtime API artifact root
- 735945be6c4a47eda90d4e6b1e1b9f7e8d1f8eba — guarded rollback recovery import root
- fb43ef0248872f4b816f0f07711661060afa7c13 — rollback import-root regression
- b29f568dba2317ea8ab3b15d8529d88a6fa1068d — production artifact-root regressions
- ed473be62b12a2c59ab9daa050055d8ee7597e90 — Pass202 workflow successor reseal
- 866c202394646a28fdcbe9b95feaa19675b4ec39 — Pass202 Python successor reseal
- baea25fa1360a64e90e474520ae865f92e8c7cec — production-root gate coverage
- b1a61eaafb391efed9df5285995de2808e5cb6c1 — exact-main deployment trigger coverage

## Acceptance

Before merge require one exact PR head with:

1. Pass 202 exact and synthetic jobs green;
2. Runtime OS Production Root green including the new boot/recovery regressions;
3. DigitalOcean Production Exact Main PR contract green;
4. Full Application IDE green if triggered.

After merge require exact-main:

1. guarded recovery handles the pre-existing failed state without
   ModuleNotFoundError;
2. hhs.service starts and remains active on 127.0.0.1:8080;
3. no import writes are attempted under /opt/hhs/app/demo_reports;
4. guarded updater emits PROMOTED for the merged SHA;
5. nginx no longer returns 502;
6. public HTTPS Runtime OS verification passes.

## Next action

Open the repair PR, run the exact-head dependency-scoped gates, merge when
green, and immediately require exact-main production recovery plus public HTTPS
verification.
