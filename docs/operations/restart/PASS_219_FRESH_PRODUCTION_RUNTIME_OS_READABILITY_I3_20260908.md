# Pass 219 Fresh Production Runtime OS Readability I3 Restart

## Repository and production state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Recovery branch: `agent/pass219-fresh-production-bootstrap-73652c12-20260908`
- Recovery head entering I3: `94e4ab13108cc607242bd7458b0f77769642021f`
- Canonical production payload remains exactly `73652c122ffff6a8b9bde9de00020610964d704c`
- Production host: `hhs-production-01` / `165.227.220.193`
- I2 workflow run: `34271402869`
- I2 failed job: `102213615271`

## Frozen completed evidence

The I2 run revalidated pinned host trust, root SSH authentication, exact production HEAD, clean production worktree, transferred exact Runtime OS archive/manifest, and native `libhhs_runtime.so` presence.

The two prior service blockers are now absent:

1. `/opt/hhs/app/runtime_certification` is isolated through a service-private bind onto `/var/lib/hhs/runtime-certification`.
2. Storybook Reel runtime state is routed natively through `HHS_STORYBOOK_REEL_ARTIFACT_ROOT=/var/lib/hhs/storybook-reels`; `HHS_DATA_ROOT=/var/lib/hhs/data` is also routed to the existing writable production data root.

Service startup advanced beyond both boundaries and subscribed the runtime event-bus surfaces before the current failure.

## Current deterministic blocker

The service fails while projecting the exact prebuilt Runtime OS:

`PermissionError: [Errno 13] Permission denied: '/var/lib/hhs/runtime-os/releases/73652c122ffff6a8b9bde9de00020610964d704c/index.html'`

`hhs_backend/runtime_os_projection.py` resolves `HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/current`; the symlink resolves to the exact release directory before `RUNTIME_OS_INDEX.is_file()`.

The bundle contents are not missing and the index file is not the source of the mode defect. `runtime-os-bundle.py` creates the staging root with `tempfile.mkdtemp(...)`, which yields a private `0700` stage directory. It later applies `0755` to directories found by `stage.rglob('*')` and `0644` to files, but the stage root itself is not included in that traversal. `os.replace(stage, release)` therefore preserves the root-only stage mode on the final release directory.

This explains why the exact release was successfully sealed and verified as root while `User=hhs` cannot traverse it.

## I3 repair contract

Do not make the Runtime OS release writable by `hhs`, do not alter bundle bytes, and do not change production source SHA.

For the already verified exact release only:

1. require the release directory, manifest, index, and assets to exist;
2. set the exact release directory itself to mode `0755` (root-owned, read/traverse only for non-root);
3. require `hhs` can traverse the release and read `index.html`;
4. rerun the authoritative exact bundle verifier so file count, byte lengths, SHA-256 records, index identity, and archive-bound manifest remain valid;
5. restart `hhs.service` and require loopback `/api/system/status` plus a clean exact source tree.

The recovery bootstrap should also normalize the returned exact release directory to `0755` after `runtime-os-bundle.py stage`, so a fresh retry cannot recreate this packaging-mode fault.

## Root-cause source repair after production closure

The durable source correction belongs in `deployment/digitalocean/guarded_auto_update/runtime-os-bundle.py`: explicitly chmod the stage root to `0755` before `os.replace(stage, release)`. That source change must be validated and delivered through the normal branch/PR/main workflow; it is not substituted into the currently fixed production payload `73652c12` during this recovery.

## Exact next action

Apply the exact-release root traversal repair through the already pinned SSH channel, verify the bundle again, and continue the bootstrap only if service health and zero source drift pass.
