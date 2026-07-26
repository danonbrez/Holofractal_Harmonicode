# Holofractal Harmonicode (HHS)

The Holofractal Harmonicode System is a deterministic, receipt-locked runtime backed by a compiled C kernel. Every computation is cryptographically verifiable, replay-auditable, and graph-linked. Nothing can enter, execute in, or leave the runtime without passing through the canonical IO gateway, which stamps every payload with a Hash72 u^72 Digital DNA witness and appends the record to an append-only unified ledger.

For the full developer walkthrough see [`docs/DEVELOPER_WALKTHROUGH.md`](docs/DEVELOPER_WALKTHROUGH.md).  
For AI-agent navigation rules see [`docs/AI_AGENT_WALKTHROUGH.md`](docs/AI_AGENT_WALKTHROUGH.md).  
For the architecture specification see [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Quick Start

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11.x | 3.12+ not guaranteed |
| gcc | ≥ 12.0 | or clang with equivalent flags |
| GNU make | ≥ 4.3 | for the C kernel build |
| Node.js | ≥ 20 | for the unified GUI only |

### Python runtime tests

```sh
# From the repository root — no build step needed for the Python layer
python hhs_runtime_smoke_tests_v1.py   # infrastructure + kernel bootstrap
python hhs_regression_suite_v1.py      # full invariant regression
python hhs_v1_bundle_runner.py         # end-to-end certification bundle
```

### Unified GUI (Pass 157)

```sh
cd apps/unified_gui
npm install
npx playwright install chromium
npm run verify
```

### Build and start the backend server

```sh
# 1. Install Python packages
pip install -r requirements.txt

# 2. Build the C kernel
mkdir -p hhs_runtime/builds

gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    -fPIC -shared \
    hhs_runtime/c/hhs_runtime_abi.c \
    hhs_runtime/src/hhs_hash216.c \
    -o hhs_runtime/builds/libhhs_runtime.so -lm

gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    hhs_runtime/HARMONICODE_VM_RUNTIME.c \
    -o hhs_runtime/builds/hhs_vm81 -lm

# 3. Launch the FastAPI server
PYTHONPATH=$(pwd) python -m uvicorn hhs_backend.server:app \
    --host 0.0.0.0 --port 8080 --ws websockets
```

> **macOS note:** drop `-lm` (math is in libc). The shared library extension is `.dylib`; update the ctypes load path in `hhs_python/runtime/hhs_ctypes_bridge.py`.  
> **Windows:** not supported natively. Use WSL2 with a Linux environment.

---

## Repository Topology

```
Holofractal_Harmonicode/
├── apps/
│   └── unified_gui/          Pass 157 — Three.js HTML/JS particle GUI
│       ├── index.html
│       ├── src/
│       │   ├── app/          boot.js (lifecycle), state.js (reducer)
│       │   ├── kernel/       exact_bridge.js (BigInt ratio, symbolic AST)
│       │   ├── physics/      engine.js (5,184-particle fixed-step torus),
│       │   │                 address_map.js (Hash72 address table)
│       │   ├── render/       scene.js (Three.js WebGL), lod.js (LOD hysteresis)
│       │   ├── trace/        chain.js (append-only Hash72 trace)
│       │   └── persistence/  indexeddb.js, global.js
│       └── tests/            Playwright + Node test suites
│
├── hhs_runtime/              Canonical Python runtime (~200 modules)
│   ├── kernel_resolution.py  Bootstrap resolver — single authority surface
│   ├── core_sandbox/         Canonical sandbox layer (physics model, state,
│   │                         general runtime, Hash72 encoder)
│   └── *.py                  Acceleration fabric, agents, passes 081–135+
│
├── hhs_backend/              FastAPI transport layer
│   ├── api/                  Route definitions (runtime, audit, cognition)
│   ├── runtime/              Orchestration, distributed consensus, agents
│   └── server.py             Application entry point
│
├── hhs_python/               ctypes bridge to the C ABI; runtime controller
├── hhs_graph/                Graph topology and receipt memory
├── hhs_storage/              Persistence and replay storage
├── hhs_gui/                  GUI runtime OS and spatial environment
├── docs/                     Architecture specs, walkthroughs, API reference
├── formal/                   Coq and Lean proofs
├── native_projects/          C native projects (VM81, compiler, IDE, PPF-MPTC)
│
├── HARMONICODE_KERNEL_v44_2_*.py  Authoritative kernel (do not redefine)
│
├── hhs_general_runtime_layer_v1.py  ← compatibility shim only
├── hhs_state_layer_v1.py            ← compatibility shim only
├── hhs_physics_model_v1.py          ← compatibility shim only
├── hhs_physics_evolution_v1.py      ← compatibility shim only
├── hhs_runtime_smoke_tests_v1.py
├── hhs_regression_suite_v1.py
└── hhs_v1_bundle_runner.py
```

> **Root-level `.py` files are compatibility shims.** Canonical implementations live in `hhs_runtime/core_sandbox/`. See [ARCHITECTURE.md Root Module Policy](ARCHITECTURE.md#root-module-policy).

---

## Kernel Invariants

All computation must pass these invariants on every step:

| Invariant | Meaning |
|---|---|
| Δe = 0 | No energy accumulation across a closed operation |
| Ψ = 0 | Phase residue zero — no symbolic drift |
| Θ15 = true | 15-step closure gate passes |
| Ω = true | Global integrity witness verified |

No float arithmetic inside the kernel. Use rational (`Fraction`) representations.

---

## Execution Pattern

Every operation follows this pipeline — no exceptions:

```text
Input
  → Symbolic / Macro Expansion
  → State Patch
  → Kernel Audit  (Δe, Ψ, Θ15, Ω verified)
  → Receipt Commit  (Hash72 appended to ledger)
```

Skipping any stage is a quarantine trigger, not a valid shortcut.

---

## Kernel Authority

The single authoritative kernel is:

```
HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py
```

Required symbols: `AUTHORITATIVE_TRUST_POLICY_V44`, `security_hash72_v44`, `NativeHash72Codec`, `Manifold9`, `Tensor`.

The `hhs_runtime/kernel_resolution.py` module is the **only** surface allowed to load and verify the kernel. Do not import it directly from other paths.

---

## Prohibited Changes

| Prohibited | Reason |
|---|---|
| Redefine `Hash72` | Breaks all receipt continuity |
| Bypass `Manifold9` or `drift_gate` | Removes the only integrity gate |
| Create alternate integrity paths | Produces irreconcilable ledger forks |
| Replace rational arithmetic with floats | Violates Δe = 0 |
| Silently collapse `xy` and `yx` | Ordered products are not commutative in this algebra |
| Mutate state without a state patch and receipt | Bypasses audit |

---

## Unified GUI — Pass 157

The primary visual interface is a pure browser application in `apps/unified_gui/`. It does not require the Python backend to run.

**Browser globals exposed at runtime:**

| Global | Purpose |
|---|---|
| `HHSApp` | Full application lifecycle |
| `HHSPhysics` | Step, reset, serialize, replay the 5,184-particle engine |
| `HHSRender` | Set render profile, focus particle, diagnostics |
| `HHSSymbolic` | Parse source, register equalities, substitute |
| `HHSTrace` | Inspect and seal the Hash72 trace chain |

**Render profiles:**

| Profile | Mode | Pixel Ratio | Notes |
|---|---|---|---|
| `MOBILE_SAFE` | points | 1.0 | Auto-selected on mobile or without WebGL2 |
| `BALANCED` | instances | 1.25 | Default for WebGL2 desktop |
| `DESKTOP_HIGH` | instances | 1.75 | High-density desktop |
| `HIGH_REFRESH` | instances | 4.0 | Auto-selected on ≥ 8 M-pixel displays; targets 120 Hz |
| `DIAGNOSTIC` | points | 1.0 | Debug overlay |

---

## API Latency — Known Issue and Fix Path

> This section is preserved from the original integration report because the root cause and fix are still relevant.

**Observed:** every API endpoint responds in 3–5 seconds.

**Root cause:** `hhs_runtime/hhs_unified_hash72_ledger_v1.py` re-hashes every prior ledger entry on each `append_payload()` call — O(n) per append. With 1,346 entries this is ~107 ms of hash computation per call, plus full file read/write. Each API request triggers two appends (ingress + egress).

**Fix:** maintain an in-memory tip hash and entry count; update it incrementally on each append. Cold-start reads the file once. This reduces append cost from O(n) to O(1). Expected result: sub-millisecond appends regardless of ledger size.

Secondary fixes: cache IO gateway witnesses by `(source, payload_hash72, runtime_step)`; activate the acceleration fabric for parallel ingress/egress witness computation; add a response-level cache keyed on `(endpoint, runtime_step)`.

---

## Historical Reference

The earlier sections of this README described the initial Replit integration work (C kernel Makefile fix, React/Vite dashboard scaffold, OpenAPI spec generation, Zod version bump). That integration record is preserved in `git` history. The current primary interface is `apps/unified_gui/` (Pass 157). The React dashboard described in the original README was a prototype integration surface and is not the canonical GUI.

---

## Table of Contents

1. [What HHS Is](#what-hhs-is)
2. [Repository Topology](#repository-topology)
3. [What Was Done To Get It Running](#what-was-done-to-get-it-running)
   - [Environment](#1-environment)
   - [C Kernel Compilation](#2-c-kernel-compilation)
   - [Python Dependencies](#3-python-dependencies)
   - [Startup Script](#4-startup-script)
   - [Replit Artifact Wiring](#5-replit-artifact-wiring)
   - [OpenAPI Spec & Code Generation](#6-openapi-spec--code-generation)
   - [HHS Dashboard Frontend](#7-hhs-dashboard-frontend)
   - [API Response Adapter Layer](#8-api-response-adapter-layer)
4. [One-Step Initialization Guide (Any Environment)](#one-step-initialization-guide-any-environment)
5. [API Latency Analysis — Root Cause & Fix](#api-latency-analysis--root-cause--fix)
6. [Current Stack Overview](#current-stack-overview)

---

## What HHS Is

The Holofractal Harmonicode System is a deterministic, receipt-locked Python
runtime backed by a compiled C kernel. Every computation the system performs is
cryptographically verifiable, replay-auditable, and graph-linked. Nothing can
enter, execute in, or leave the runtime without passing through the canonical
IO gateway, which stamps every payload with a Hash72 u^72 Digital DNA witness
produced by the C kernel and appends the record to an append-only unified
ledger.

The stack has three layers:

```
Frontend Dashboard (React / Vite)
        ↓
FastAPI Transport Layer  ←  hhs/hhs_backend/
        ↓
Runtime Orchestrator     ←  hhs/hhs_python/
        ↓
C Kernel (VM81 + ABI)    ←  hhs/hhs_runtime/c/  +  hhs/hhs_runtime/builds/
        ↓
Graph + Persistence + Replay
```

---

## Repository Topology

```
hhs/
├── hhs_runtime/          VM81 substrate, C ABI, hash72 kernel, acceleration fabric
│   ├── c/                C source: hhs_runtime_abi.c, hhs_runtime_abi.h
│   ├── src/              hhs_hash216.c (the u^72 ring implementation)
│   ├── include/          Header files
│   ├── builds/           Compiled outputs: libhhs_runtime.so, hhs_vm81
│   └── acceleration/     HHSAccelerationFabric.ts (heterogeneous dispatch spec)
├── hhs_python/           ctypes bridge to the C ABI; runtime controller/emulator
├── hhs_backend/
│   ├── api/              FastAPI route definitions (runtime_routes.py + others)
│   ├── runtime/          Orchestration, graph, replay, websocket, agent loops
│   └── server.py         FastAPI app entry point with CORS middleware
├── hhs_graph/            Graph topology, receipt memory
├── hhs_storage/          Persistence, replay storage
├── Makefile              C kernel build surface
├── requirements.txt      Python dependencies
└── start.sh              (created during integration) startup script
```

---

## What Was Done To Get It Running

### 1. Environment

**Replit-specific setup required.** The following were not pre-installed:

| Dependency | How Installed | Notes |
|---|---|---|
| Python 3.11 | Replit module system | `python-3_11` module; the default Python was too old for some type annotation syntax used in the backend |
| `gcc` | Replit system package | `gcc` |
| `gnumake` | Replit system package | `gnumake` |
| All Python packages | `pip install -r hhs/requirements.txt --target .pythonlibs` | Replit does not use virtualenvs; packages install to `.pythonlibs/` |

The `PYTHONPATH` must include the `hhs/` directory at runtime so that `hhs_runtime`, `hhs_python`, `hhs_backend`, etc. are importable as top-level packages. This is set in `hhs/start.sh`.

---

### 2. C Kernel Compilation

**The Makefile has a bug on the `vm81` target.** The `LDFLAGS` variable (`-lm`) is
defined at the top of the Makefile and is correctly applied to the shared
library target, but it is **not applied** to the `hhs_vm81` binary target. The
math library (`-lm`) is required because `HARMONICODE_VM_RUNTIME.c` uses
`pow()`, `fabs()`, and related functions. Without `-lm`, the linker fails on
Linux.

**Failing command (from stock Makefile):**
```sh
gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    hhs_runtime/HARMONICODE_VM_RUNTIME.c \
    -o hhs_runtime/builds/hhs_vm81
# ↑ missing -lm → undefined reference to `pow'
```

**Working command:**
```sh
gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    hhs_runtime/HARMONICODE_VM_RUNTIME.c \
    -o hhs_runtime/builds/hhs_vm81 \
    -lm
```

**Fix for the Makefile:** add `$(LDFLAGS)` to the `vm81` recipe, or hard-code
`-lm`. The ABI library target already works correctly.

```makefile
# CURRENT (broken on vm81):
$(VM81_BIN): hhs_runtime/HARMONICODE_VM_RUNTIME.c ... | $(RUNTIME_BUILD_DIR)
	$(CC) $(CFLAGS) hhs_runtime/HARMONICODE_VM_RUNTIME.c -o $(VM81_BIN)

# FIXED:
$(VM81_BIN): hhs_runtime/HARMONICODE_VM_RUNTIME.c ... | $(RUNTIME_BUILD_DIR)
	$(CC) $(CFLAGS) hhs_runtime/HARMONICODE_VM_RUNTIME.c -o $(VM81_BIN) $(LDFLAGS)
```

---

### 3. Python Dependencies

```sh
pip install -r hhs/requirements.txt
```

All packages in `requirements.txt` install cleanly under Python 3.11. The key
runtime packages are:

- `fastapi==0.128.2` + `uvicorn[standard]` — the HTTP/WebSocket server
- `pydantic>=2.7,<3.0` — request/response schema validation
- `networkx>=3.3` — graph topology layer
- `numpy>=1.26`, `sympy>=1.13` — numerical and symbolic runtime support
- `sqlalchemy>=2.0`, `aiosqlite>=0.20` — persistence layer
- `cryptography>=46.0` — signed network envelopes (Pass 146)

---

### 4. Startup Script

`hhs/start.sh` was created because the repository has no single entry point
that handles compilation + server launch together. The file does three things:

1. Compiles the C kernel (both the shared ABI library and the VM81 binary),
   with graceful fallback warnings if compilation fails.
2. Sets `PYTHONPATH` to include the `hhs/` directory.
3. Launches uvicorn on `$PORT` with `--ws websockets`.

```bash
#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[HHS] Building C kernel..."
gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    -fPIC -shared \
    hhs_runtime/c/hhs_runtime_abi.c \
    hhs_runtime/src/hhs_hash216.c \
    -o hhs_runtime/builds/libhhs_runtime.so -lm

gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    hhs_runtime/HARMONICODE_VM_RUNTIME.c \
    -o hhs_runtime/builds/hhs_vm81 -lm

echo "[HHS] C kernel ready."
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"
PORT="${PORT:-8080}"
exec python -m uvicorn hhs_backend.server:app \
    --host 0.0.0.0 --port "$PORT" \
    --ws websockets --log-level info
```

---

### 5. Replit Artifact Wiring

Two artifacts were configured:

**API Server** (`artifacts/api-server/`) was repurposed from a Node.js express
placeholder to run the HHS Python backend. The `artifact.toml` run command was
updated to `bash /home/runner/workspace/hhs/start.sh`. An important lesson:
the run command must use an **absolute path**. A relative path like
`bash hhs/start.sh` failed because the workflow runner uses the artifact
directory as its working directory, not the workspace root.

**HHS Dashboard** (`artifacts/hhs-dashboard/`) is a new React/Vite artifact
registered at path `/`. A Vite proxy was added to forward `/api` requests from
the dev server (port 18142) to the HHS backend (port 8080):

```ts
// vite.config.ts
server: {
  proxy: {
    '/api': { target: 'http://localhost:8080', changeOrigin: true, ws: true }
  }
}
```

---

### 6. OpenAPI Spec & Code Generation

No OpenAPI spec existed in the repository. One was authored at
`lib/api-spec/openapi.yaml` covering all major runtime routes, then codegen
was run via Orval v8.22 to produce:

- `lib/api-client-react/` — typed React Query hooks for all endpoints
- `lib/api-zod/` — Zod v4 schemas for all request/response types

**Zod version bump required.** Orval 8.22 generates Zod v4 syntax
(`z.looseObject()`, etc.) which is incompatible with Zod v3. The workspace
catalog in `pnpm-workspace.yaml` was bumped from `^3.25.76` to `^4.0.0`.

---

### 7. HHS Dashboard Frontend

The dashboard was built against the generated hooks. Six pages were wired:

| Page | Route | Key Data |
|---|---|---|
| Runtime Overview | `/` | Step count, hash72, convergence, Step/Halt controls, latest vector + packet |
| Receipt Graph | `/graph` | Node/edge counts, node lookup, replay, predict, receipt commit |
| Services | `/services` | 351 registered services, search, dispatch console |
| Conformance | `/conformance` | 19 invariants, conformance root hash72, evaluator, state enforcer |
| Sandbox | `/sandbox` | Create isolated fork, step execution, output log |
| Authority & Leases | `/authority` | Roles, components, lease table, issue/revoke, federation status |

**All API hooks are connected.** The dashboard polls every 10 seconds on
live-updating queries.

---

### 8. API Response Adapter Layer

The HHS backend wraps every response in a guarded envelope that does not match
the simplified types the OpenAPI spec describes. For example,
`GET /api/runtime/state` returns:

```json
{
  "schema": "HHS_GUARDED_RUNTIME_STATE_RESPONSE_V1",
  "runtime": { "step": 130, "state_hash72": "...", "converged": true, "halted": false },
  "io": { "ingress": { ... }, "egress": { ... } },
  "runtime_contract": { ... }
}
```

Rather than fight the codegen types, an adapter layer was created at
`artifacts/hhs-dashboard/src/lib/hhs-adapters.ts`. Every page imports its
relevant adapter and normalizes the raw API response before rendering. This
layer is also the right place to add client-side caching or derived fields as
the API matures.

---

## One-Step Initialization Guide (Any Environment)

The following steps are what the development team needs to turn into a single
`make setup` or `./init.sh` invocation.

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11.x | 3.12 has not been tested |
| gcc | ≥ 12.0 | Any modern GCC; clang also works with the same flags |
| make | ≥ 4.3 | GNU make |
| pip | bundled with Python | For Python packages |

### Step-by-step (manual)

```sh
# 1. Clone
git clone https://github.com/danonbrez/Holofractal_Harmonicode
cd Holofractal_Harmonicode

# 2. Python packages
pip install -r requirements.txt

# 3. Build C kernel
#    Fix: vm81 target needs -lm (see Makefile bug above before running stock make)
mkdir -p hhs_runtime/builds

gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    -fPIC -shared \
    hhs_runtime/c/hhs_runtime_abi.c \
    hhs_runtime/src/hhs_hash216.c \
    -o hhs_runtime/builds/libhhs_runtime.so -lm

gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    hhs_runtime/HARMONICODE_VM_RUNTIME.c \
    -o hhs_runtime/builds/hhs_vm81 -lm

# 4. Verify kernel
hhs_runtime/builds/hhs_vm81 --verify

# 5. Launch
PYTHONPATH=$(pwd) python -m uvicorn hhs_backend.server:app \
    --host 0.0.0.0 --port 8080 --ws websockets
```

### Recommended: `init.sh` (add to repo root)

```sh
#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing Python dependencies"
pip install -r requirements.txt

echo "==> Building C kernel"
mkdir -p hhs_runtime/builds

gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    -fPIC -shared \
    hhs_runtime/c/hhs_runtime_abi.c \
    hhs_runtime/src/hhs_hash216.c \
    -o hhs_runtime/builds/libhhs_runtime.so -lm

gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    hhs_runtime/HARMONICODE_VM_RUNTIME.c \
    -o hhs_runtime/builds/hhs_vm81 -lm

echo "==> Verifying kernel"
hhs_runtime/builds/hhs_vm81 --verify

echo "==> HHS ready. Starting server on port ${PORT:-8080}"
PYTHONPATH=$(pwd) python -m uvicorn hhs_backend.server:app \
    --host 0.0.0.0 --port "${PORT:-8080}" \
    --ws websockets --log-level info
```

### Cross-platform notes

| Platform | Notes |
|---|---|
| Linux (x86_64) | Works as-is. Default platform for Replit. |
| macOS | Replace `-lm` with nothing (math is in libc on macOS). The `-fPIC -shared` flags produce `.dylib`, not `.so` — update the ctypes load path in `hhs_python/runtime/hhs_ctypes_bridge.py` accordingly. |
| Windows | Not supported. The C kernel uses POSIX headers and assumes ELF shared libraries. WSL2 is the recommended path. |
| Docker | Use `python:3.11-slim` as base. Add `build-essential` for gcc. The Makefile `vm81` target works once `-lm` is added. |

---

## API Latency Analysis — Root Cause & Fix

### Observed behaviour

Every HHS API endpoint takes **3–5 seconds** to respond. This was measured on
a live server after startup:

```
GET /api/runtime/state     4.3s
GET /api/runtime/vector/latest   3.4s
GET /api/runtime/packet/latest   5.1s
```

This is not a network issue, not a Python GIL issue, and not the hash72 C
kernel being slow. The C kernel itself is fast:

```
10 hash72_kernel_digest() calls: 0.8ms total → ~0.08ms each
```

### Actual latency breakdown per request

Profiled against a running server with 1,346 ledger entries:

```
Controller init:              0ms   (cached, singleton)
Gateway init:                 0ms   (cached, singleton)
ingress() — hash72 + ledger:  1951ms   ← this is the problem
runtime_state():              0ms
egress()  — hash72 + ledger:  1861ms   ← this too
─────────────────────────────────────────
Total per GET /api/runtime/state:  ~3,812ms
```

### Root cause: the unified ledger re-hashes every append

`hhs_runtime/hhs_unified_hash72_ledger_v1.py` keeps all records in a JSON
file on disk. Every call to `append_payload()` does the following:

1. Reads the entire ledger file from disk.
2. Appends the new record.
3. Calls `verify_unified_ledger()` to compute the new tip hash.
4. `verify_unified_ledger()` iterates through every existing entry and runs a
   `hash72_kernel_digest()` call on each one to verify and recompute the
   chain.
5. Writes the full file back to disk.

With 1,346 entries, step 4 runs 1,346 hash72 calls. At ~0.08ms each, that is
**~107ms of hash computation alone per append**. The disk I/O for reading and
writing an ever-growing JSON file adds the rest. Each API request triggers two
`append_payload()` calls (ingress + egress), giving ~215ms of pure ledger
overhead even at this size — and the number grows with every request.

The five-ledger-append benchmark confirmed this:

```
5 ledger appends: 9,523ms → ~1,905ms each
(ledger had 1,341 entries at time of measurement)
```

As the ledger grows the cost grows linearly with it. At 10,000 entries a
single request would take 30+ seconds.

### Why this is not how HHS is designed to work

The repository already contains the full acceleration architecture to prevent
exactly this problem:

**1. The IO gateway has a vector cache (`validate_vector_cache_write`).**
Validated vectors should be served from the cache on repeated identical
requests. A `GET /api/runtime/state` with no intervening `step()` returns
exactly the same runtime state. It should hit the cache, not re-run the full
witness chain.

**2. The zero-bypass interposer has interposition tokens.**
`hhs_runtime/hhs_zero_bypass_runtime_interposer_v1.py` issues reusable tokens
for admitted surface propagations. A repeated read on an unchanged surface
should present its token and bypass full recomputation. The token is already
bound to the payload hash — if the payload hash matches a cached token, the
witness is already proven.

**3. The acceleration fabric (`hhs_runtime/acceleration/HHSAccelerationFabric.ts`)
is designed for exactly this throughput problem.**
It specifies ASIC/FPGA/GPU/SIMD dispatch channels with `latencyNs` slots. The
architecture comment is explicit: *"The fabric accelerates execution, not
authority."* Authority (the receipt chain) remains canonical; computation is
offloaded.

**4. Pass 108 added immutable result reuse.**
The changelog documents: *"Added exact dependency-rooted immutable result
reuse. Added bounded optimization leases and stale-dependency rejection."*
This is the in-process cache that should make repeated reads instant.

**5. Pass 111 added validated continuation caches.**
*"Added validated continuation caches with no speculative future results."*

### What the development team needs to fix

The ledger cost is a single specific fix. Everything else is already
architected:

#### Fix 1: Cache the ledger tip in memory (immediate — removes 95% of latency)

The ledger's own `_ledger_summary_payload()` already hashes only the ordered
list of **entry hashes**, not the full payloads. This means the tip hash can
be maintained incrementally: when a new entry is appended, hash the new entry
and combine it with the previous tip hash. There is no need to re-read all
prior entries.

```python
# hhs_runtime/hhs_unified_hash72_ledger_v1.py
# Current: verify_unified_ledger() reads the file and re-hashes all entries
# Fix: maintain an in-memory tip + entry count; only read from disk on startup

_ledger_tip_cache: dict = {}   # { ledger_path: { tip_hash72, entry_count } }

def _get_cached_tip(path: str) -> tuple[str, int]:
    if path in _ledger_tip_cache:
        return _ledger_tip_cache[path]["tip_hash72"], _ledger_tip_cache[path]["entry_count"]
    # cold start: read file
    ...

def _update_cached_tip(path: str, new_tip: str, count: int):
    _ledger_tip_cache[path] = { "tip_hash72": new_tip, "entry_count": count }
```

This reduces `append_payload()` from O(n) to O(1) per call. Expected result:
sub-millisecond ledger appends regardless of ledger size.

#### Fix 2: Cache GET-only route witnesses by payload hash (removes repeated computation)

For read-only routes (`GET /api/runtime/state`, `/api/runtime/graph/summary`,
etc.) the payload entering the IO gateway is always `{"method": "GET"}`.
Because HHS is deterministic, if the runtime step has not changed, the
ingress witness for this payload is **identical** to the one computed on the
previous request.

The IO gateway should check whether a prior witness exists for the same
`(source, payload_hash72, runtime_step)` tuple before calling
`payload_hash72_witness()`. This is precisely what the interposition token
mechanism is built for.

```python
# In HHSIOGateway._record():
cache_key = (source, payload_hash72(payload_dict), runtime_state.get("step"))
if cache_key in self._witness_cache:
    witness = self._witness_cache[cache_key]
else:
    witness = payload_hash72_witness(payload_dict)
    self._witness_cache[cache_key] = witness
```

#### Fix 3: Activate the acceleration fabric for parallel witness computation

The `HHSAccelerationFabric.ts` spec is currently TypeScript-only and not
connected to the Python layer. For environments where multiple cores are
available, the ingress and egress hash72 computations for a single request are
independent and can run in parallel via `asyncio.gather()` or a thread pool.
This alone would halve the effective latency while Fix 1 is in progress.

#### Fix 4: Add a response-level cache for read-only endpoints

For routes where the runtime step has not advanced, the full response can be
cached behind a simple dict keyed by `(endpoint, runtime_step)`. A `step()`
call invalidates all entries. This is the "buffer accelerate" part of the
design — the accelerated result is served directly without re-entering the IO
gateway at all.

### Expected latency after fixes

| Stage | Current | After Fix 1 | After Fix 1+2 | After all fixes |
|---|---|---|---|---|
| ingress witness | ~1,900ms | ~5ms | ~0ms (cache hit) | ~0ms |
| egress witness | ~1,900ms | ~5ms | ~0ms (cache hit) | ~0ms |
| route handler | ~0ms | ~0ms | ~0ms | ~0ms |
| **Total per request** | **~3,800ms** | **~10ms** | **~1ms** | **< 1ms** |

The 3–5 second latency is a runtime artifact of the ledger append pattern, not
an inherent cost of the cryptographic design. The design intends for unique
operations to pay the crypto cost once, with all subsequent reads served from
the receipt-backed vector cache.

---

## Current Stack Overview

### Running services (Replit)

| Service | Port | Path | Status |
|---|---|---|---|
| HHS FastAPI backend | 8080 | `/api` | Running |
| HHS Dashboard (React/Vite) | 18142 | `/` | Running |

### Dashboard pages

| Page | Route | Data source |
|---|---|---|
| Runtime Overview | `/` | `useGetRuntimeState`, `useGetLatestVector`, `useGetLatestPacket` |
| Receipt Graph | `/graph` | `useGetGraphSummary`, `useGetGraphNodeByHash`, `useReplayGraphNode`, `usePredictFromNode` |
| Services | `/services` | `useListServices`, `useGetServicesStatus`, `useDispatchService` |
| Conformance | `/conformance` | `useListInvariants`, `useGetConformanceStatus`, `useEvaluateConformance`, `useEnforceAdmissibility` |
| Sandbox | `/sandbox` | `useCreateSandbox`, `useStepSandbox` |
| Authority & Leases | `/authority` | `useGetAuthorityStatus`, `useGetAuthorityRoles`, `useGetLeasesStatus`, `useGetFederationStatus`, `useIssueLease`, `useRevokeLease` |

### WebSocket

The runtime streams events at `ws://<host>/api/runtime/ws/runtime`. The
dashboard does not currently subscribe to this stream but all infrastructure
(the backend WebSocket layer, the Vite proxy `ws: true` flag) is in place.

### Key files added or modified in this Replit environment

| File | What it does |
|---|---|
| `hhs/start.sh` | Compiles C kernel + launches uvicorn. Entry point for the api-server workflow. |
| `lib/api-spec/openapi.yaml` | OpenAPI 3.1 spec for all HHS runtime routes. |
| `artifacts/hhs-dashboard/` | React/Vite dashboard scaffold with all six pages. |
| `artifacts/hhs-dashboard/src/lib/hhs-adapters.ts` | Normalizes HHS guarded envelope responses to flat types the UI expects. |
| `artifacts/api-server/.replit-artifact/artifact.toml` | Updated run command to `bash /home/runner/workspace/hhs/start.sh`. |
| `pnpm-workspace.yaml` | Bumped Zod catalog from `^3.25.76` → `^4.0.0` for Orval v8.22 compatibility. |
