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
