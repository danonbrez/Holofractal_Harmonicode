# Pass 175 production terminal repair checkpoint — 2026-10-06

## Authoritative state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative main: `f83fd1a6d1882bbd768d10a0e9e461caf2fa29c6`
- main subject: `Merge PR #726: repair production Pass 175 terminal state`
- checkpoint branch: `checkpoint/pass175-production-terminal-repair-20261006`
- production functional closure: **NOT YET CLAIMED**

## Triggering production failure

Previous authoritative main:

`601059f1bc80693e0f8607fe835a3ff065ded833`

Exact-Main run:

`37448483329`

Deploy job:

`112219050783`

Deployment reached:

- guarded PROMOTED;
- public HTTPS Runtime OS;
- public service registry 380;
- expanded live Chromium frontend acceptance.

The live browser failed specifically at the visible Pass 175 Terminal workflow. Evidence artifact:

- artifact ID: `11406980317`
- browser state after Open terminal: `CLOSED`
- terminal message: `No terminal message yet.`
- timeout at production browser verifier terminal READY wait.

No console error, page error, or HTTP 5xx established the cause before the timeout.

## Root cause

Pass 175 terminal startup uses:

`HHS_PASS175_STATE_DIR`

when configured, otherwise:

`<repository>/.hhs/pass175`.

Production service:

`deploy/digitalocean/hhs-pass196-integrated-environment.service`

runs as user `hhs` with:

- `WorkingDirectory=/opt/hhs/app`
- `ProtectSystem=full`
- `ReadWritePaths=/var/lib/hhs`

but previously had no `HHS_PASS175_STATE_DIR` binding.

Therefore terminal initialization attempted to create mutable encrypted Hash216 terminal state under protected repository path `/opt/hhs/app/.hhs/pass175`.

The WebSocket route accepted the socket and then called `get_terminal_runtime()` before sending READY and outside an error-to-frame boundary. Initialization failure therefore appeared to the frontend as a socket that closed without diagnostic payload.

## PR #726 repair

PR:

`#726 Repair production Pass 175 terminal state`

Final PR head:

`ee67b8218b2b18d6e46dfe09b76ddc0c04f1ea1a`

Merged main:

`f83fd1a6d1882bbd768d10a0e9e461caf2fa29c6`

Changes:

1. Production mutable-state binding:
   - `HHS_PASS175_STATE_DIR=/var/lib/hhs/pass175`.

2. Immutable-checkout validation:
   - runner state creates `pass175`;
   - exports `HHS_PASS175_STATE_DIR`;
   - production mutable-state regression requires the external path.

3. Exact-Main contract:
   - production service must retain `HHS_PASS175_STATE_DIR=/var/lib/hhs/pass175`.

4. Terminal WebSocket bootstrap diagnostics:
   - initialization exceptions after WebSocket acceptance emit:
     `HHS_PASS_175_TERMINAL_WS_BOOT_FAILURE_V1`;
   - payload includes `ok=false`, classification, detail, and `parallel_state_authority=false`;
   - socket closes with code 1011 after diagnostic transmission.

5. Terminal frontend:
   - structured backend rejection is preserved as visible `ERROR`, not overwritten by silent `CLOSED`.

6. Production browser:
   - terminal-open acceptance waits for `READY` or `ERROR`;
   - ERROR immediately captures visible diagnostic and last terminal message;
   - successful path still requires:
     `READY -> ping -> PONG -> HHS_PASS_175_TERMINAL_WS_PONG -> close -> CLOSED`.

7. Focused terminal regression:
   - direct fake-WebSocket test verifies accepted socket, boot-failure payload, classification/detail and close code 1011 without adding an httpx/TestClient dependency.

8. Pass 196 stale acceptance repair:
   - service wiring validation now checks authoritative installed warm-boot verifier:
     `/usr/local/lib/hhs-guarded-update/warm_boot_manifest.py`;
   - adds Pass 175 external-state assertion.

## Frozen validation evidence

Successful before merge:

- Source Text Integrity on repair lineage: SUCCESS.
- Pass 196 Integrated Environment push run `37451917960`: SUCCESS.
- Pass 175 Virtual Instruction Processor PR run `37451968516`: SUCCESS.
- Previous terminal-workflow failure on PR head was isolated to the new test importing TestClient without httpx; test was rewritten to use a direct fake WebSocket.
- I130 PR run failure was outside the modified dependency cone: cumulative exact ABI linkage failed on unresolved inherited OpenSSL/Hash/PQC symbols before any Pass 175 repair code was exercised. No I130 source was changed by PR #726.

## Current post-merge runs

Exact-current-main SHA:

`f83fd1a6d1882bbd768d10a0e9e461caf2fa29c6`

Production:
- DigitalOcean Production Exact Main: `37452413742`
- state at checkpoint: queued

Pass 175:
- Verify Terminal Pass 175 Completion: `37452413808`
- state at checkpoint: queued

Additional current-main validation:
- Pass 196 Integrated Environment: `37452413909`
- Validate HHS Runtime OS Production Root: `37452413914`
- Validate Full Application IDE: `37452413560`
- HHS Source Text Integrity: `37452413904`

Repository runner load at checkpoint:
- 49 active workflows
- 18 in progress
- current production and terminal runs queued due capacity.

## Exact next actions

1. Resolve authoritative `main`.
2. If main remains `f83fd1a6d1882bbd768d10a0e9e461caf2fa29c6`, follow only the current-main runs above.
3. Require terminal completion workflow to pass the direct WebSocket bootstrap regression.
4. Require Exact-Main deployment contract SUCCESS.
5. Require production:
   - exact bundle build/seal;
   - SSH authority;
   - guarded PROMOTED receipt exactly bound to current main;
   - Lane 5 host ingress verified;
   - public HTTPS;
   - public service registry;
   - full expanded live Chromium frontend acceptance.
6. Critical terminal proof:
   - visible Open terminal;
   - production WSS connection;
   - `READY`;
   - visible Ping terminal;
   - `PONG`;
   - message contains `HHS_PASS_175_TERMINAL_WS_PONG`;
   - close returns `CLOSED`.
7. Do not weaken the final browser error sweep. If background `ERR_ABORTED` health requests remain after terminal succeeds, classify them from the new artifact and repair only with evidence.
8. Queue Hash216 only after the full live functional browser gate passes.
9. If Hash216 creates a generated successor, follow its serialized Exact-Main chain to terminal convergence.
10. Do not claim production frontend functional closure until the current exact main passes all expanded user-triggered workflows.
