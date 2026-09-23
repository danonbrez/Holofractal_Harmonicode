# Pass 220 I043 — Ubuntu Guest Runtime + PTY v1

## Purpose

Pass 220's existing Ubuntu Application VM control plane is preserved as the HHS
application/runtime authority **inside** an Ubuntu environment. I043 adds the
missing host-side guest substrate beneath it.

The authority order is:

```text
Host Linux
  -> I043 guest artifact + QEMU lifecycle
  -> Ubuntu guest
  -> authenticated SSH + PTY transport
  -> existing hhs-application-vm / Pass 190 control plane
  -> Lane 5 candidate/control kernel
  -> VM81 canonical admission
```

I043 does not create a second VM81, Hash72 clock, Hash216 persistence path,
Lane 5 kernel, operation registry, or HHS capability format.

## Guest artifact authority

The base Ubuntu image is an external runtime artifact identified by:

- an explicit filesystem path;
- an explicit expected SHA-256;
- an explicit source format (`qcow2` or `raw`).

The runtime refuses to prepare or start a guest if the image digest differs.
The base is never modified by I043. A writable QCOW2 overlay is created beneath
the I043 state root and becomes the only guest disk mutated by QEMU.

The runtime receipt records the base digest, overlay path, PID-file path, QMP
socket, loopback SSH endpoint, and transition. It is explicitly a host-runtime
receipt, **not** a Hash72/Hash216 canonical state commit.

## Hypervisor lifecycle

The explicit backend is QEMU x86_64.

Generated machine policy:

```text
q35,accel=kvm:tcg
```

KVM is therefore preferred when available and TCG is the deterministic fallback
when KVM acceleration cannot be used. No second HHS execution authority is
introduced by either accelerator.

Lifecycle identity is bound to:

- `qemu.pid`;
- a QMP UNIX socket;
- the digest-verified base image;
- the deterministic overlay path.

A stale PID file is a fail-closed state. It is not silently discarded during
start because doing so could mask an unknown guest/runtime owner.

The guest SSH forward is always:

```text
127.0.0.1:<configured-port> -> guest:22
```

Public `0.0.0.0` SSH forwarding is outside this contract.

## Authenticated guest transport

OpenSSH is the v1 transport. It requires both:

- an explicit identity/private-key file;
- an explicit known-hosts file.

The generated SSH invocation enforces:

```text
BatchMode=yes
IdentitiesOnly=yes
StrictHostKeyChecking=yes
UserKnownHostsFile=<explicit-path>
```

No password fallback and no implicit host-key acceptance are authorized.

## PTY semantics

A guest terminal session is a real local PTY connected to an authenticated
`ssh -tt` process. The I043 PTY object defines:

- unique session identity;
- nonblocking reads;
- writes;
- terminal row/column resize through `TIOCSWINSZ`;
- POSIX signal delivery to the SSH process group;
- exit-status observation;
- bounded close with SIGHUP followed by SIGKILL only after timeout.

This is distinct from the inherited `/v1/vm/shell` endpoint. That endpoint
continues to lower HHS shell commands through Pass 190; it is not a general
Ubuntu Bash/PTTY.

## Host CLI

The host-facing launcher is:

```bash
sh bin/hhs-guest verify
sh bin/hhs-guest prepare
sh bin/hhs-guest start
sh bin/hhs-guest status
sh bin/hhs-guest stop
sh bin/hhs-guest restart
sh bin/hhs-guest pty-exec -- bash -lc 'pwd && hhs-vm status'
```

Configuration is supplied through environment variables:

```text
HHS_GUEST_BASE_IMAGE
HHS_GUEST_BASE_SHA256
HHS_GUEST_STATE_ROOT
HHS_GUEST_BASE_FORMAT
HHS_GUEST_NAME
HHS_GUEST_MEMORY_MIB
HHS_GUEST_CPUS
HHS_GUEST_SSH_PORT
HHS_GUEST_SSH_USER
HHS_GUEST_SSH_IDENTITY
HHS_GUEST_SSH_KNOWN_HOSTS
HHS_GUEST_QEMU_BIN
HHS_GUEST_QEMU_IMG_BIN
HHS_GUEST_SSH_BIN
HHS_GUEST_PYTHON_BIN
```

The digest variables are mandatory. SSH identity/known-hosts become mandatory
when transport is requested.

## Frontend boundary

I043 intentionally does not attach the Visual IDE or Runtime OS to this
transport yet.

Frontend work must not begin by treating the existing Pass 190 shell endpoint as
a terminal substitute. A subsequent adapter may attach only after an actual
digest-verified guest is booted and the authenticated PTY path is reachable.

## Acceptance

I043 acceptance is dependency-scoped and requires:

1. digest mismatch rejects before guest start;
2. overlay preparation never mutates the base;
3. QEMU command carries PID/QMP identity and loopback-only SSH forwarding;
4. lifecycle start/stop is explicit and stale PID state fails closed;
5. SSH transport pins identity and host key;
6. PTY read/write/resize/signal/close semantics execute against a real PTY;
7. tests demonstrate that the new layer carries no HHS canonical-state authority;
8. focused CI passes on the exact branch head.

A GitHub-hosted runner unit test does not establish that a production Ubuntu
guest image has booted. Real boot, SSH reachability, installation of the existing
application control plane inside the guest, and GUI attachment remain separate
integration gates.
