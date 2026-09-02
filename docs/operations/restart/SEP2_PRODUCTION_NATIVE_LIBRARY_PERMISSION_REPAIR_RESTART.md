# September 2 Production Native Runtime Permission Repair — Restart Checkpoint

## Scope

Production closure repair for `danonbrez/Holofractal_Harmonicode`, performed through GitHub/native repository tooling only.

## Base and branch

- Merge ancestry required by task: `fe7a80e95df65ae318f5ecf859e22e1c5f34bd09` (PR #352 repair merge).
- Repair base / main snapshot at branch creation: `4b862c1d9975b1e190bf2e88bff92175c2f935ed`.
- Branch: `agent/sep2-production-native-library-permission-repair`.
- Validated feature head before this checkpoint: `d02f1fb76362092baf95e02a2ee346404928bd73`.

## Frozen inherited evidence

1. Pass 202 run `33652186050`:
   - exact lane green;
   - synthetic lane failed only because the post-merge runner could no longer fetch `refs/pull/352/merge`;
   - no synthetic test executed or failed, so this is runner/ref race evidence rather than a product regression.
2. I147 multimodal run `33652331308` is green at `fe7a80e95df65ae318f5ecf859e22e1c5f34bd09`.
3. Original exact-main deployment `33652331363` and authoritative successor deployment `33655103103` both proved that tracked checkout normalization succeeded, including traversal of `/opt`, `/opt/hhs`, `/opt/hhs/app`, `/opt/hhs/app/hhs_backend` and readability of `hhs_backend/__init__.py`.
4. Deployment `33655103103` nevertheless failed recovery because the `hhs` service user could not load generated `hhs_runtime/builds/libhhs_runtime.so`: `Permission denied`. Recovery therefore never reached `HHS_ROLLBACK_BOUNDARY_HEALTHY=1`; promotion and public HTTPS verification were not reached.

## Repair implemented

The production permission normalizer now treats the exact generated native runtime boundary as canonical service runtime state even though it is Git-untracked:

- `hhs_runtime/builds/`
- `hhs_runtime/builds/libhhs_runtime.so`

It repairs group traversal/read permission for that exact boundary, verifies the service user can traverse/read it, preserves the existing `HHS_PRODUCTION_CHECKOUT_PERMISSION_RECEIPT_V2` schema, and continues to avoid recursive mutation of unrelated untracked host state.

Changed files through validated head:

- `deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py`
- `tests/test_hhs_production_native_runtime_permissions_v3.py`
- `.github/workflows/sep2-production-native-library-permission-repair.yml`

## Dependency-scoped validation

Workflow run: `33656442460`

Validated head: `d02f1fb76362092baf95e02a2ee346404928bd73`

Result: **SUCCESS**.

Green steps include:

- Python parse/compile of permission normalizer;
- existing production permission contract tests;
- generated native runtime permission regression tests;
- guarded deployment contract tests;
- inherited Pass 202 deployment identity checks;
- receipt generation and artifact sealing.

Artifact:

- ID: `9856898271`
- Name: `sep2-production-native-library-permission-repair-d02f1fb76362092baf95e02a2ee346404928bd73`
- Digest: `sha256:7c023b805f4e212338f309fb466cac7cc4e0b729f712ab4955523f88791eb52e`

## Restart / next actions

1. Verify current `main` head immediately before integration.
2. If main has advanced, preserve the repair ancestry and reconcile only relevant drift before merge; do not discard the frozen scoped evidence without a dependency-relevant reason.
3. Open the repair PR and merge only with an expected-head guard.
4. Verify resulting current main contains both PR #352 merge ancestry and this repair.
5. Observe the exact-main DigitalOcean deployment for the resulting current main. Required closure evidence:
   - deployment contract green;
   - permission normalizer executes and reports native runtime library readable;
   - recovery mode, if entered, reaches `HHS_ROLLBACK_BOUNDARY_HEALTHY=1` before promotion;
   - promotion receipt outcome is `PROMOTED` for exact current main;
   - `hhs.service` active;
   - `hhs` can traverse `/opt`, `/opt/hhs`, `/opt/hhs/app`, `/opt/hhs/app/hhs_backend` and read `hhs_backend/__init__.py`;
   - `/api/system/status`, `/api/interface/status`, and root Runtime OS workspace pass locally and through public HTTPS.
6. Ignore unrelated historical workflow noise unless it changes this delivery dependency chain.

## Current blocker state

No code-level blocker remains at the validated branch head. Production closure remains pending integration and exact-main deployment verification.
