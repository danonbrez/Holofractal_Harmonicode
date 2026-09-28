# Pass 220 I046 — Warm Hydrated VM Boot v1

## Purpose

A production VM restart must not reconstruct the HHS machine.

The production boot model is:

```text
persistent VM disk
  -> compiled native runtime / compiled ROM already present
  -> Runtime OS release already built
  -> SQL/vector/cache state already present under durable /var/lib/hhs
  -> exact release manifest verification
  -> reopen/adopt hydrated state
  -> start HHS backend
```

Compilation, package installation, Runtime OS construction, and first-time
hydration belong to deployment/promotion, not `systemctl restart hhs`.

## Warm-boot invariant

```text
Restart
  != rebuild native hardware
  != rebuild Runtime OS
  != create a new vector namespace
  != replace SQL state
  != rehydrate from an empty graph
  != regenerate compiled ROM

Restart
  == verify sealed release identity
  + reopen durable state
  + map compiled runtime
  + resume services
```

If the sealed artifacts required by the deployed SHA are absent or have changed,
production boot fails closed. It does not call a compiler as recovery behavior.

## Durable production bindings

The production service explicitly binds:

```text
HHS_DATA_DIR=/var/lib/hhs/data
HHS_PASS174_STATE_DIR=/var/lib/hhs/pass174
HHS_PASS194_STATE_ROOT=/var/lib/hhs/pass194
HHS_PASS205_DB=/var/lib/hhs/pass205/continuation.sqlite3
HHS_PASS213_SURFACE_STATE_DIR=/var/lib/hhs/pass213/surface
HHS_PASS218_STATE_ROOT=/var/lib/hhs/pass218
HHS_PASS219_LANE5_STATE_ROOT=/var/lib/hhs/pass219/lane5
HHS_RUNTIME_BOOTSTRAP_ROOT=/var/lib/hhs/runtime-bootstrap
HHS_WARM_BOOT_MANIFEST_ROOT=/var/lib/hhs/warm-boot/releases
```

Pass 174 therefore reopens the same encrypted Hash216 vector database instead
of falling back to repository-local `.hhs/pass174`.

Pass 194 reopens the durable hydration/snapshot state instead of falling back to
checkout-local `data/pass194`.

Pass 213 reopens the same governed surface state instead of using a service-user
home-directory default.

Pass 205 remains bound to its existing durable SQLite continuation database.

## Build authority separation

Production service environment:

```text
HHS_DISABLE_C_AUTOBUILD=1
```

The service restart path is guarded by:

```text
deployment/digitalocean/warm_boot_manifest.py verify
```

That verifier performs identity and durable-root checks only.

It does not invoke:

- `make`;
- GCC/Clang/CMake;
- `post_compile`;
- npm/pip/apt;
- hydration generators.

The guarded deployment path retains build authority before promotion. After the
native runtime and Runtime OS candidate have been built and activated, it seals
the warm-boot identity for the candidate SHA.

## SHA-scoped warm manifests

Promotion writes:

```text
/var/lib/hhs/warm-boot/releases/<repository-sha>.json
```

Each manifest binds:

- exact deployed repository SHA;
- exact native runtime path and SHA-256;
- exact Runtime OS release/index identity;
- exact durable production state-root bindings;
- restart policy: autobuild forbidden, empty rehydration forbidden.

Manifests are release-scoped rather than one mutable `current` file. A rollback
to an earlier Git SHA therefore resolves that earlier SHA's own manifest and
does not require reconstructing the VM.

## Systemd behavior

`hhs.service` now executes the warm verifier before Uvicorn:

```text
ExecStartPre=... warm_boot_manifest.py verify ...
ExecStart=... uvicorn hhs_backend.production_visual_server:app ...
```

A missing or mismatched native runtime, Runtime OS release, manifest, or durable
state binding stops boot before the Python application imports.

This intentionally converts accidental cold reconstruction into a visible
deployment integrity failure.

## Authority boundary

The warm-boot manifest is operational evidence only.

```text
canonical_state_authority = false
new_vm81_authority = false
```

It does not mint Hash72/Hash216 state and does not replace VM81 admission.

## Acceptance

I046 is accepted when:

1. production service has C autobuild disabled;
2. Pass 174/194/205/213/218/Lane-5 state roots are durable production paths;
3. promotion creates those durable roots without deleting existing contents;
4. promotion builds first, then seals a SHA-specific warm manifest;
5. restart verifies the manifest before Python application import;
6. restart verifier contains no build/package/hydration commands;
7. native runtime and Runtime OS digests are verified;
8. rollback release manifests coexist;
9. dependency-scoped warm-boot tests and inherited Pass 196 service tests pass.
