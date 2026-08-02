# HHS Pass 189 HQLH Runtime

This project implements the executable hydration, calibration, causal-batch, fail-closed adapter, and driver-provenance authorities specified by Pass 189.

It supplies:

- exact C11 decoding and re-encoding for all `51,648,192` first-level contextual addresses;
- a reproducibly derived Lo Shu-ranked 41-coordinate reciprocal lane around every VM81 cell;
- Boolean XNOR, signed XNOR, and nucleus-relative ternary orientation;
- exact-source token and membrane construction with non-destructive `P` / `P+1` witnesses;
- sparse base-41 path hydration without allocating the theoretical full manifold;
- exact tagged `V72 = 8 × 9` topology;
- Hash72 local identity, ordered Hash216 neighborhoods, singleton admission, and replay;
- canonical equation objects with shared VM81, circuit, breadboard, simulation, visual, and worldline projections;
- persistent exact calibration evidence and atomic receipt-locked causal batches;
- fail-closed `LOOPBACK` and sandboxed `FILE_SINK` software adapters;
- authenticated driver-package quarantine, conformance evidence, dual promotion, token validation, expiry, revocation, and rollback;
- CLI, HTTP, SSE, WebSocket, standalone visual inspectors, and HHS runtime-window integration;
- DigitalOcean Ubuntu `systemd` and nginx deployment assets for Iterations 1–4.

Vercel is not part of the runtime or deployment authority.

## Validation

```sh
make validate
```

Expected authoritative native result:

```text
HHS_PASS_189_HQLH_NATIVE_PASS contexts=51648192 reciprocal=51648192 drift=0 checksum=e02ef2dc8070e3f3
```

The validation target performs:

1. strict C11 static/shared library and CLI build;
2. exhaustive round-trip validation of all 51,648,192 contextual addresses;
3. reciprocal Lo Shu lane validation for every address;
4. no-floating-arithmetic disassembly scan;
5. inherited and Iterations 2–4 Python authority tests;
6. token-lifecycle migration and persistent-expiry tests;
7. HTTP, visual document, replay, SSE, WebSocket, registry, and DigitalOcean-authority smoke tests;
8. Python bytecode and deployment shell-syntax checks.

## CLI

```sh
build/hhs_pass189_cli decode 51648191
build/hhs_pass189_cli local 40 8
build/hhs_pass189_cli xnor 1 0
build/hhs_pass189_cli validate

PYTHONPATH=python python3 python/hhs_pass189.py membranes 'List(01,xy)==(yx=01)+(zw*wz)'
PYTHONPATH=python python3 python/hhs_pass189.py hydrate 1259711 --path 8,-8,0 --source 'x==x'
PYTHONPATH=python python3 python/hhs_pass189.py equation 'V==I*R'
```

## Runtime surfaces

### Iteration 1 hydration

```sh
python3 server/hhs_pass189_server.py --host 127.0.0.1 --port 8189
```

```text
GET  /pass189/
GET  /api/pass189/health
GET  /api/pass189/registry
GET  /api/pass189/decode?extended=0
GET  /api/pass189/events
GET  /ws
POST /api/pass189/membranes
POST /api/pass189/hydrate
POST /api/pass189/replay
POST /api/pass189/equation
```

### Persistent iterations

```text
Iteration 2 calibration and causal authority    127.0.0.1:8190
Iteration 3 fail-closed adapters                127.0.0.1:8191
Iteration 4 driver provenance and lifecycle     127.0.0.1:8192
```

The corresponding visual routes are `/pass189/i2/`, `/pass189/i3/`, and `/pass189/i4/`.

## DigitalOcean deployment

The canonical operator documentation is:

- [DigitalOcean installation, operations, and maintenance runbook](../../docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md)
- [Deployment-directory quick reference](deployment/digitalocean/README.md)

On the authoritative Ubuntu host:

```sh
cd /opt/holofractal-harmonicode
make -C native_projects/hhs_pass189_hqlh_runtime validate

sudo REPO_ROOT=/opt/holofractal-harmonicode \
  SERVICE_USER=hhs \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh
```

Install `deployment/digitalocean/nginx-hhs-pass189.conf` as an include inside the existing HTTPS server block, run `nginx -t`, reload nginx, and verify all four services.

Local verification:

```sh
sudo native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

Public verification through one nginx origin:

```sh
sudo \
  BASE_URL=https://YOUR_DOMAIN \
  ITERATION2_URL=https://YOUR_DOMAIN \
  ITERATION3_URL=https://YOUR_DOMAIN \
  ITERATION4_URL=https://YOUR_DOMAIN \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

The four services bind to loopback at ports `8189–8192`; nginx remains the public TLS authority.

### Co-host port warning

Pass 190 also defaults to `127.0.0.1:8190`. A host running both stacks must use a documented systemd/nginx/verifier port override or separate hosts. Pass 196 uses `127.0.0.1:8080` and does not conflict with the default Pass 189 range.

## Calibration and hardware boundary

The runtime can construct breadboard, circuit, simulation, and worldline projections from one canonical equation identity, retain measured-calibration candidates, and govern non-executable driver packages. It does not fabricate physical verification.

Iteration 3 executes only software test adapters. Iteration 4 real-hardware packages remain `HARDWARE_CANDIDATE_NONEXECUTABLE` with:

```text
executable = false
real_hardware_dispatch_authorized = false
```

The current classification remains:

```text
HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS
```

not `HHS_PASS_189_HQLH_UNIFIED_PHYSICS_VERIFIED`.
