# HARMONICODE IDE Interface Rebuild — Ubuntu PTY Checkpoint

Date: 2026-09-28

## Repository identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `interface/harmonicode-ide-rebuild`
- Frozen branch base: `08f504fcb8294296084d1576ef68e9e95c15cffb`
- Content checkpoint before this record: `6baace608d34295b5b80349c1ea875a4ce160f31`
- Merge target: none yet; this is the dedicated interface-development branch.

## Scope invariant

This branch is interface-owned.

- No `hhs_backend/` changes.
- No `hhs_runtime/` changes.
- No canonical API/ABI/opcode semantics changed.
- Existing external Runtime/CLI surfaces are consumed, not bypassed.
- Browser authority is graphics, controls, transport, and presentation only.
- Runtime/guest authority owns execution, state, files, shell semantics, and results.
- No mock/fallback execution is permitted.

## Implemented

1. Mobile-first live Runtime proof page:
   - `hhs_gui/public/interface-proof.html`
   - real service/status discovery;
   - guarded service dispatch;
   - Pass 175 terminal WebSocket;
   - fail-closed contract checks.

2. Ubuntu PTY interface transport:
   - `hhs_gui/interface_gateway/ubuntu_pty_gateway.py`
   - authenticated WebSocket;
   - calls only `bin/hhs-guest` as the guest transport surface;
   - no import of canonical HHS Runtime implementation;
   - bounded command length, output size, dimensions, and timeout;
   - guest SSH identity and known-hosts never leave the server;
   - command executes through `hhs-guest pty-exec -- bash -lc ...`.

3. Production interface deployment:
   - loopback systemd service on `127.0.0.1:8787`;
   - existing promoted I044 guest environment loaded from
     `/var/lib/hhs/ubuntu-guest/current/runtime.env`;
   - same-origin nginx status/WebSocket routes;
   - idempotent authoritative TLS-server discovery;
   - nginx backup, syntax validation, rollback, and reload;
   - one-command installer with generated bearer token.

4. Development routing:
   - Vite routes `/api/interface/ubuntu/pty/*` to loopback port 8787 with
     WebSocket forwarding.

## Source acceptance executed

Connected-repository source checks passed:

- external CLI only: PASS
- bearer authentication: PASS
- no host-shell execution/bypass: PASS
- Bash execution through guest PTY CLI: PASS
- bounded command/output/timeouts: PASS
- loopback gateway service: PASS
- promoted guest environment binding: PASS
- TLS WebSocket route: PASS
- nginx rollback configurator: PASS
- installer closes nginx/service handoff: PASS
- Vite same-origin development route: PASS
- thin browser client / no browser persistence or WASM: PASS
- no mock fallback: PASS
- branch diff restricted to `hhs_gui/`: PASS

The local container could not clone GitHub because DNS/network access is disabled,
so repository-local `py_compile` / `sh -n` execution was not claimed from
that environment. `hhs_gui/interface_gateway/verify.py` contains those executable
checks for any repository checkout.

## Live-host validation boundary

The interface implementation is complete. Actual Ubuntu command execution
requires the already-defined I043/I044 promoted guest and its server-side SSH
credentials to be present on the deployment host. The interface fails closed if
that environment is absent; it does not substitute a local shell or demo result.

## Resume

Continue interface development from this branch without modifying canonical
backend/runtime code. The next UI primitives should consume existing indexed
filesystem/editor/application surfaces through the same thin-client rule.
