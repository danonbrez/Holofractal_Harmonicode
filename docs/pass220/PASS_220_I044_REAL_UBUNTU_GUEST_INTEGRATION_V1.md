# Pass 220 I044 — Real Ubuntu Guest Integration v1

## Purpose

I044 converts the merged I043 guest lifecycle/PTY substrate into an executable
real-Ubuntu integration path.

The architecture is:

```text
production Linux host
  -> digest-pinned Ubuntu 24.04 cloud image
  -> I043 QEMU lifecycle + release-specific QCOW2 overlay
  -> NoCloud seed
  -> Ubuntu guest
  -> strict loopback SSH + real PTY
  -> exact HHS repository SHA inside guest
  -> inherited hhs-application-vm / Pass 190 adapter
  -> Pass 219 cumulative inherited authority
  -> Lane 5 C++ BIOS / AGI optimization control center
  -> signed environmental VM81 canonical admission
```

No I044 component is a new HHS canonical state authority.

## Pinned guest artifact

The guest base image is the Ubuntu 24.04 LTS amd64 released cloud QCOW2 build
from 2026-09-11:

```text
filename:
  ubuntu-24.04-server-cloudimg-amd64.img

source:
  https://cloud-images.ubuntu.com/releases/releases/noble/release-20260911/
  ubuntu-24.04-server-cloudimg-amd64.img

sha256:
  612b2c0cc1bc413a6cb8c38fd611794caf0f2b436c50013d8b3794db12ad7354
```

The repository manifest is:

```text
deployment/ubuntu/guest_runtime/ubuntu-24.04-amd64-image.json
```

The download is never admitted merely because the URL succeeds. The exact
SHA-256 must match before the base artifact is renamed into the immutable image
cache.

## Release-specific guest identity

Each HHS repository target SHA receives a separate guest state root:

```text
/var/lib/hhs/ubuntu-guest/releases/<TARGET_SHA>
```

That state root contains:

- isolated QCOW2 overlay;
- NoCloud seed;
- guest/client SSH identities;
- pinned known_hosts;
- I043 runtime environment;
- preparation receipt;
- runtime status;
- application VM health/status evidence;
- PTY proof;
- final I044 integration receipt.

A prior target's overlay is not silently reused by a later target.

## NoCloud bootstrap

The I044 preparation script creates a NoCloud seed containing:

- an `hhs` operator user;
- no password SSH authentication;
- one release-specific SSH client public key;
- one explicit guest ED25519 host key;
- exact host-key pinning support;
- packages needed by the application VM runtime;
- exact repository checkout of `TARGET_SHA`;
- `/opt/hhs/venv` dependency setup;
- installation of the inherited `hhs-application-vm` service.

The application control plane is intentionally installed with
`HHS_APPLICATION_VM_REQUIRE_GUI=0` for this gate. I044 proves the real guest
runtime and backend control-plane path first. The graphical workstation/desktop
attachment is the subsequent gate.

## Real transport acceptance

The host promotes the guest only after all of these are true:

```text
digest-pinned base image verified
AND NoCloud seed attached read-only
AND QEMU process live
AND SSH reachable only through 127.0.0.1:<port>
AND StrictHostKeyChecking=yes
AND guest cloud-init completed
AND guest repository HEAD == TARGET_SHA
AND hhs-application-vm.service active
AND application VM health ok
AND single_vm81_authority_preserved == true
AND real SSH-backed PTY command exits 0
AND PTY output contains HHS_I044_PTY_OK
```

Only then is:

```text
/var/lib/hhs/ubuntu-guest/current
```

moved to the target state root.

## Authority invariants

I044 must report:

```text
canonical_state_authority = false
new_vm81_authority = false
frontend_attached = false
```

The QEMU host layer, Ubuntu guest, cloud-init metadata, SSH transport, PTY, and
Pass 190 application service are conventional execution/transport/application
surfaces subordinate to Pass 219. Canonical HHS mutations remain downstream of
the Pass 219 -> Lane 5 -> signed environmental VM81 path.

Lane 5 is the Pass 219 C++ BIOS and AGI optimization control center. Its
reasoning/optimization circuits are callable bounded circuits; guest boot,
service startup, PTY availability, or frontend attachment does not imply a
continuous autonomous optimization loop.

## CI and production execution

PR CI validates:

- Python compilation;
- shell syntax;
- image manifest schema;
- I043 regression inheritance;
- seed attachment semantics;
- release-scoped state;
- strict SSH contracts;
- required real-guest acceptance order.

Real production execution is deliberately manual-only through:

```text
.github/workflows/pass220-i044-real-ubuntu-guest.yml
workflow_dispatch -> run_real_guest=true
```

The real job uses the repository's existing pinned DigitalOcean host SSH
credentials and executes the exact dispatched main SHA.

It is not run automatically on merge because it boots a QEMU guest and mutates
host runtime state.

## Current infrastructure blocker

At the start of I044 implementation on 2026-09-23, the connected DigitalOcean
account reported a locked state and the existing `hhs-production-01` droplet
reported `off`.

Therefore the real-host gate is implemented but not claimed executed. No new
Droplet was created and the existing Droplet was not powered on from this cycle.

## Next gate after I044 real-host acceptance

Once the real guest is proven, the next cycle may attach the Native Visual IDE
terminal/status adapter to the guest transport. That adapter must consume the
authenticated guest/PTY boundary, preserve the Pass 219 -> Lane 5 -> signed
VM81 authority hierarchy, and must not reinterpret the existing Pass 190
`/v1/vm/shell` endpoint as a general Linux terminal.
