# Pass 220 I043 — Ubuntu Guest Runtime + PTY Restart Checkpoint

## Repository identity

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `69e386548cdbbae4a1bd10d510c77ade2410cf6f` (merged Pass 220 I042)
- branch: `pass220/i043-ubuntu-guest-runtime-pty-v1`
- merge target: `main`

## Problem statement

The merged Ubuntu Application VM control plane is an application service intended
to run **inside an already-running Ubuntu environment**. It does not create an
Ubuntu guest, own a hypervisor lifecycle, or provide a general guest PTY.

This cycle adds the missing host-side substrate beneath the existing control plane
without creating any alternate VM81, Hash72, Hash216, Lane 5, Pass 190, or
canonical mutation authority.

Canonical layering for this cycle:

```text
host Linux
  -> Pass 220 guest artifact/lifecycle authority
  -> QEMU/KVM when available, deterministic TCG fallback otherwise
  -> Ubuntu guest
  -> authenticated SSH transport + PTY
  -> existing hhs-application-vm service / Pass 190
  -> Lane 5 / VM81 admission
```

The pre-existing endpoint `/v1/vm/shell` remains an HHS command-lowering
surface. It is not reclassified as a Bash/PTTY transport.

## I043 implementation scope

1. **Guest artifact authority**
   - explicit immutable base-image path and expected SHA-256;
   - fail-closed digest verification before start;
   - deterministic writable QCOW2 overlay creation;
   - persisted runtime manifest/receipt binding base digest, overlay, QEMU
     command, SSH endpoint, and lifecycle state.

2. **VM lifecycle**
   - explicit QEMU backend;
   - KVM-first with TCG fallback encoded by the generated machine argument;
   - loopback-only SSH host forwarding;
   - PID file and QMP UNIX socket identity;
   - start/status/stop/restart semantics;
   - fail closed when the PID file is stale or the image identity diverges.

3. **Guest transport**
   - OpenSSH client transport with explicit identity file and known-hosts file;
   - batch authentication and host-key verification;
   - real PTY allocation through the host PTY subsystem and remote `ssh -tt`;
   - session identity, nonblocking reads, writes, terminal resize, POSIX signals,
     exit status, and bounded close semantics.

4. **CLI and CI**
   - host-side `hhs-guest` CLI for verify/prepare/start/status/stop/restart and
     bounded PTY execution;
   - dependency-scoped unit tests using fake QEMU/QEMU-img/SSH executables;
   - workflow validation without claiming a real nested-KVM boot on GitHub-hosted
     runners.

## Explicit non-goals for I043

- no GUI/frontend adapter yet;
- no replacement for the existing application VM API;
- no direct frontend-to-VM81 path;
- no new capability-token or canonical state authority;
- no production deployment claim;
- no claim that the Ubuntu guest image has already been built or booted on the
  production host.

Frontend attachment is allowed only after guest artifact identity, lifecycle,
authenticated transport, and PTY behavior are demonstrably reachable.

## Acceptance

`I043GuestRuntimeAccepted` requires:

```text
base image digest verified
AND writable overlay prepared
AND generated QEMU transport is loopback-only
AND lifecycle tracks PID + QMP identity
AND stale PID fails closed
AND SSH uses pinned identity + known_hosts
AND PTY supports read/write/resize/signal/close
AND no canonical HHS authority is introduced
AND dependency-scoped tests pass
```

## Next action

Implement the host guest runtime, host CLI, tests, and focused workflow. Run the
focused workflow on the exact branch head, repair only impacted failures, then
open the PR with this checkpoint updated with exact validation evidence.
