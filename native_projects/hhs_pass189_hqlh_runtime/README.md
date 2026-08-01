# HHS Pass 189 HQLH Runtime

This project implements the executable hydration authority specified by the Pass 189 HARMONICODE quantum-logic and unified-physics addition.

It supplies:

- exact C11 decoding and re-encoding for all `51,648,192` first-level contextual addresses;
- a reproducibly derived Lo Shu-ranked 41-coordinate reciprocal lane around every VM81 cell;
- Boolean XNOR, signed XNOR, and nucleus-relative ternary orientation;
- exact-source token and membrane construction with non-destructive `P` / `P+1` witnesses;
- sparse base-41 path hydration without allocating the theoretical full manifold;
- exact tagged `V72 = 8 × 9` topology;
- Hash72 local identity, ordered Hash216 neighborhoods, singleton admission, and replay;
- canonical equation objects with shared VM81, circuit, breadboard, simulation, visual, and worldline projections;
- CLI, HTTP, SSE, WebSocket, standalone visual inspector, and HHS runtime-window integration;
- DigitalOcean Ubuntu `systemd` and nginx deployment assets.

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
5. nine Python unit tests;
6. HTTP, visual document, replay, SSE, WebSocket, registry, and DigitalOcean-authority smoke tests;
7. Python bytecode compilation.

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

## Server and visual inspector

```sh
python3 server/hhs_pass189_server.py --host 127.0.0.1 --port 8189
```

Surfaces:

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

## DigitalOcean deployment

On the authoritative Ubuntu host:

```sh
sudo REPO_ROOT=/opt/holofractal-harmonicode \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh
```

Add `deployment/digitalocean/nginx-hhs-pass189.conf` inside the existing HTTPS server block, validate nginx, and reload it. Then run:

```sh
BASE_URL=https://YOUR_DOMAIN \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

The service binds to loopback at `127.0.0.1:8189`; nginx remains the public TLS authority.

## Calibration boundary

The runtime can construct breadboard, circuit, simulation, and worldline projections from one canonical equation identity, but it does not fabricate physical verification. Hardware output remains blocked until real device bindings, ranges, units, calibration coefficients, measurements, residuals, and safety tests are admitted. Therefore the completion classification is:

```text
HHS_PASS_189_HQLH_HYDRATION_VERIFIED
```

not `HHS_PASS_189_HQLH_UNIFIED_PHYSICS_VERIFIED`.
