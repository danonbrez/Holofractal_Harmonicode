# Pass 219 Fresh Production Runtime State Repair I2 Restart

## Exact state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Recovery branch: `agent/pass219-fresh-production-bootstrap-73652c12-20260908`
- Recovery workflow commit: `a1f754b77fca6f2ee4dd175ab8fc56162a225811`
- Canonical production payload remains unchanged: `73652c122ffff6a8b9bde9de00020610964d704c`
- Production host: `hhs-production-01` / `165.227.220.193`
- Repair workflow run: `34270903498`
- Failed job: `102211945102`

## Completed I1 evidence

The I1 repair run revalidated:

- pinned Ed25519 host trust;
- root SSH authentication;
- exact production HEAD at `73652c122ffff6a8b9bde9de00020610964d704c`;
- clean production worktree;
- exact transferred Runtime OS archive and manifest still present;
- native `libhhs_runtime.so` still present.

The systemd drop-in for runtime certification was installed and loaded:

```ini
[Service]
BindPaths=/var/lib/hhs/runtime-certification:/opt/hhs/app/runtime_certification
```

The previous blocker `PermissionError: /opt/hhs/app/runtime_certification` did not recur.

## New deterministic blocker

Service initialization advanced to the Storybook Reel runtime and then failed at:

`PermissionError: [Errno 13] Permission denied: '/opt/hhs/app/artifacts/storybook_reels'`

The authoritative source `hhs_backend/runtime/hhs_storybook_reel_v1.py` already exposes a production-safe state override:

`HHS_STORYBOOK_REEL_ARTIFACT_ROOT`

Its default only falls back to `repo_root / "artifacts" / "storybook_reels"` when the environment override is absent.

## I2 repair contract

Do not make `/opt/hhs/app` writable and do not modify exact payload `73652c12`.

Extend the root-owned `hhs.service` recovery drop-in with:

```ini
Environment=HHS_STORYBOOK_REEL_ARTIFACT_ROOT=/var/lib/hhs/storybook-reels
Environment=HHS_DATA_ROOT=/var/lib/hhs/data
BindPaths=/var/lib/hhs/runtime-certification:/opt/hhs/app/runtime_certification
```

Create `/var/lib/hhs/storybook-reels` as `hhs:hhs` mode `0750` before restart. `HHS_DATA_ROOT` is set proactively because repository modules use a relative `data` fallback while the production service already defines `/var/lib/hhs/data` as its canonical writable data state.

## Completed vs remaining

Completed and frozen:

- console-authenticated host identity;
- deployment-key enrollment;
- exact payload checkout;
- frontend typecheck/build;
- deterministic Runtime OS seal and transfer;
- Python environment;
- native ABI build;
- checkout-readability normalization;
- runtime certification state-path isolation.

Remaining:

1. apply native Storybook artifact/data-root environment routing;
2. require loopback `/api/system/status` green with a clean exact source tree;
3. resume only the remaining fresh-host bootstrap stages;
4. install/verify guarded follower;
5. configure and verify public browser-trusted HTTPS;
6. write/verify initialization receipt;
7. verify production assistant authority separately;
8. record final deployment closure or the next exact blocker.

## Exact next command semantics

Rerun `deployment/digitalocean/fresh_host_runtime_certification_repair.sh` after extending its systemd drop-in with the two production state environment variables above. Continue the bootstrap only if service health and zero repository drift both pass.
