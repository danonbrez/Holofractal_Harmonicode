# Pass 220 I047 — Unified Lane 5 Production VM

## Purpose

I047 removes the remaining production topology split between the validated HHS
virtual-machine architecture and the legacy host-native application services.

Production is one persistent Ubuntu machine whose HHS computation is admitted
through the inherited Pass 219/220 chain:

```text
public ingress
  -> host nginx transport / static presentation only
  -> loopback QEMU transport
  -> persistent Ubuntu guest
  -> inherited Runtime OS / IDE / application VM surfaces
  -> Pass 220 Lane 5 zero-bypass interposer
  -> Pass 219 C++ RNA VM5184 cell wall
  -> Lane 5 mediation
  -> PQC environmental / instruction firewall
  -> signed environmental VM81 admission
  -> canonical VM81 transition
  -> Hash72 receipt closure
  -> Hash216 lineage / persistence
```

No I047 host component receives canonical HHS authority.

## Singleton production machine

The integration-test release receipts remain SHA-scoped under:

```text
/var/lib/hhs/ubuntu-guest/releases/<TARGET_SHA>
```

Production VM state does not.

When `HHS_GUEST_PERSISTENT_VM=1`, the QEMU overlay, SSH identity, QMP state
and machine-local Ubuntu filesystem live under:

```text
/var/lib/hhs/ubuntu-guest/machine
```

A later merged SHA updates the repository and services inside that same Ubuntu
machine. The guest-local `/var/lib/hhs` databases, Hash216 stores, Lane 5
state, application-VM state and normal Linux filesystem therefore survive the
software release transition.

The SHA-scoped directory is evidence about a release of the singleton machine;
it is not a second VM.

## Existing machinery reused

I047 does not add an alternate IDE, filesystem, VM81 runtime, persistence
engine, instruction engine, or security membrane.

Inside Ubuntu it reuses:

- `hhs-application-vm.service` for the inherited application-VM control plane;
- `hhs_backend.runtime_os_application_server` for the existing Runtime OS
  composition when the sealed release bundle is present;
- `hhs_backend.application_ide_server` only as the bootstrap projection before
  that release is attached;
- the existing native C/C++ runtime and Pass 219/220 Lane 5/RNA/PQC surfaces.

The guest Runtime OS server has no frontend runtime authority and creates no
new VM81 authority.

## Host boundary

The production host is restricted to conventional platform work:

- QEMU lifecycle;
- loopback networking;
- immutable Ubuntu base image cache;
- encrypted/persistent VM disk backing;
- nginx TLS/static presentation;
- deployment validation and exact-SHA promotion;
- non-authoritative operational receipts.

The production `hhs.service` becomes
`HHS Lane 5 BIOS Unified VM Supervisor`. It starts/stops QEMU and verifies
guest health. It does not run Uvicorn or an HHS application server.

QEMU exposes only these loopback forwards:

```text
127.0.0.1:2222  -> guest:22    strict SSH / PTY transport
127.0.0.1:18080 -> guest:8080  Runtime OS / IDE
127.0.0.1:18720 -> guest:8720  application-VM API
```

The historical host listeners on 8080 and 8720 are forbidden after cutover.

## Exact Runtime OS identity

The already-built and verified exact-main Runtime OS release is copied into:

```text
guest:/var/lib/hhs/runtime-os/releases/<TARGET_SHA>
```

and the guest `current` link is advanced to it before public cutover.

Production requires `/api/interface/status` inside the guest to identify the
existing `HHS_VISUAL_RUNTIME_OS_WORKSPACE` projection and retain
`frontend_is_runtime_authority=false`.

## Public cutover

The cutover is ordered:

```text
validate exact candidate
-> fast-forward exact main
-> build/verify inherited native authority
-> activate sealed Runtime OS bundle
-> boot/update persistent exact-SHA Ubuntu guest
-> verify application VM + singleton VM81
-> verify IDE/Runtime OS inside guest
-> verify real guest PTY
-> install host VM-supervisor service
-> verify guest loopback health
-> atomically switch nginx dynamic upstream 8080 -> 18080
-> switch /vm-api 8720 -> 18720
-> disable historical host hhs-application-vm.service
-> seal production topology receipt
-> mark promotion successful
```

The proxy configurator validates guest health before modifying nginx and restores
the prior nginx configuration if `nginx -t` or reload fails.

## Rollback

A failed first I047 migration restores the previous Git SHA and Runtime OS
release, restores the legacy `hhs.service`, re-enables the old host
application-VM service when present, and reverses nginx to the prior host
upstreams.

Once a prior release already contains I047, rollback remains within the unified
VM topology.

## Production receipts

Before public cutover the guest integration receipt proves:

- exact repository SHA;
- running QEMU guest;
- loopback-only transport;
- application VM healthy;
- `single_vm81_authority_preserved=true`;
- guest IDE healthy;
- exact Runtime OS attached;
- real SSH-backed PTY proof;
- no new canonical authority.

After nginx cutover,
`production-topology.receipt.json` additionally proves:

```text
target = guest
frontend_attached = true
host_application_compute_authority = false
canonical_state_authority = false
lane5_vm81_guest_authority_required = true
guest_health_verified = true
```

## Unified merge/deployment gate

`deployment/digitalocean/guarded_auto_update/validate-candidate.sh` now
includes the I047 regression contract. The same validator is executed by the
guarded PR merge path and again against the exact production candidate before
promotion.

The separate Pass 220 application-VM production workflow no longer SSH-deploys
an independent host service. It is now a component/unified-topology validation
workflow only.

## Acceptance

I047 closes when all of the following are true:

1. one persistent Ubuntu guest disk is used across production SHAs;
2. every production SHA is checked out and built inside that same guest;
3. the existing Runtime OS/IDE is served from the guest;
4. the application-VM API is served from the guest;
5. host `hhs.service` is QEMU supervision only and contains no Uvicorn;
6. host ports 8080 and 8720 have no application listeners after cutover;
7. guest loopback ports 18080 and 18720 are live;
8. `single_vm81_authority_preserved=true`;
9. no I047 layer claims VM81/Hash72/Hash216/canonical persistence authority;
10. public HTTPS continues to expose the existing Runtime OS;
11. PR and production candidate gates execute the same I047 topology tests;
12. rollback can restore the pre-I047 topology if first migration fails.
