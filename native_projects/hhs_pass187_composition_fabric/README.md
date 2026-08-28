# HHS Pass 187 Universal Multimodal Composition Fabric

This project closes the executable implementation gap in:

`HHS-P187-UMOACF-IR-HC-VM81-H72-H216`

It is additive to the historical Pass 187 Bott hydration contract/benchmark and
does not duplicate the later Pass 188 Bott runtime.

## Authority model

Every canonical graph mutation requires a nonzero inherited VM81 Hash72 receipt
supplied by the caller. The runtime stores that inherited receipt and derives a
local event-evidence identity plus Hash216 archive identity.

Local event evidence, caches, UI state, adapters, compiled artifacts, browser
events, and external application output do not authorize mutation.

Canonical graph state rejects floating-point ingress. Host timing and adapter
timeouts are explicitly noncanonical lanes.

## Implemented object fabric

The runtime implements:

- universal immutable object descriptors and versions;
- typed input/output ports;
- all nine relationship semantics:
  `LIVE`, `SNAPSHOT`, `REFERENCE`, `FORK`, `LAYER`, `NEST`,
  `FEEDBACK`, `CONTROL`, `COMPILED`;
- explicit adapter-node conversion only;
- ordered noncommutative Harmonicode serialization and exact round trip;
- CREATE, IMPORT, RECORD, CONNECT, DISCONNECT, INTEGRATE, LAYER, REORDER,
  NEST, UNNEST, FREEZE, SNAPSHOT, REFERENCE, FORK, BRANCH, MERGE, REVERSE,
  REPLAY, REPLACE, INVALIDATE, RECOMPOSE, COMPILE, EXPORT;
- bounded feedback;
- dependency-aware incremental recomposition;
- scoped content-addressed caches;
- target compatibility planning;
- deterministic web-app, project-bundle, and native-CLI compilation;
- files, processes, Unix sockets, and HTTP Ubuntu/Linux adapters;
- CLI, HTTP, SSE event stream, and visual direct-manipulation composition UI;
- checkpoint/cold-restart recovery and replay verification.

## CLI

```sh
PYTHONPATH=. python -m hhs_runtime.pass187.composition \
  --db /tmp/pass187.sqlite3 STATUS
```

## HTTP / visual surface

```sh
PYTHONPATH=. python -m hhs_runtime.pass187.composition_server \
  --db /tmp/pass187.sqlite3 \
  --host 127.0.0.1 \
  --port 8187
```

Open `http://127.0.0.1:8187/`.

API:

```text
GET  /api/pass187/health
GET  /api/pass187/status
GET  /api/pass187/events
POST /api/pass187/preview
POST /api/pass187/execute
```

The UI requires the inherited VM81 Hash72 receipt before it can submit an
admitted graph mutation. Candidate previews are visibly distinct from admission,
execution, projection, receipt, replay, failure, and cancellation events.

## Validation

Focused validation:

```sh
make validate
```

The suite executes all 12 normative Pass 187 end-to-end scenarios, Linux adapter
integration, exact Harmonicode round trip, tamper/replay/restart checks,
authority-bypass negatives, cancellation, a 100-node planner benchmark, and
actual Chromium mouse, keyboard, touch, pen-pointer, and accessibility
interaction acceptance.
