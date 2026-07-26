# HHS Developer Walkthrough

This document is the authoritative step-by-step guide for developers working on the Holofractal Harmonicode (HHS) system. Read it top-to-bottom on your first session. Return to individual sections whenever you start work on a new area.

---

## Table of Contents

1. [What HHS Is](#1-what-hhs-is)
2. [Repository Map](#2-repository-map)
3. [Environment Setup](#3-environment-setup)
4. [Running the Tests](#4-running-the-tests)
5. [Core Concepts](#5-core-concepts)
6. [Python Runtime Layer](#6-python-runtime-layer)
7. [Unified GUI (apps/unified_gui)](#7-unified-gui-appsunified_gui)
8. [Backend Server](#8-backend-server)
9. [Making Changes Safely](#9-making-changes-safely)
10. [Debugging and Diagnostics](#10-debugging-and-diagnostics)
11. [Prohibited Patterns](#11-prohibited-patterns)

---

## 1. What HHS Is

HHS is a **deterministic, receipt-locked cognitive computing substrate**. Every computation it performs is:

- **Deterministic** — the same input always produces the same output.
- **Receipt-committed** — every state transition is appended as an immutable Hash72 receipt to an append-only ledger.
- **Replay-verifiable** — any sequence of receipts can be independently reconstructed and verified.
- **Audit-gated** — nothing mutates state without passing the kernel invariant gate (Δe = 0, Ψ = 0, Θ15 = true, Ω = true).

It is not a collection of utilities. It is a replay-governed cognitive operating substrate. This distinction affects every design decision.

---

## 2. Repository Map

```
Holofractal_Harmonicode/
│
├── apps/unified_gui/         ← Primary browser GUI (Pass 157, Three.js)
│   ├── index.html
│   ├── src/app/              boot.js (boot lifecycle), state.js (reducer)
│   ├── src/kernel/           exact_bridge.js (exact BigInt arithmetic + symbolic parser)
│   ├── src/physics/          engine.js (particle torus), address_map.js (Hash72 addresses)
│   ├── src/render/           scene.js (Three.js WebGL renderer), lod.js (LOD hysteresis)
│   ├── src/trace/            chain.js (append-only Hash72 event chain)
│   ├── src/persistence/      indexeddb.js (workspace persistence)
│   ├── styles/app.css
│   └── tests/                core.test.mjs, lod.test.mjs, browser/app.spec.mjs
│
├── hhs_runtime/              ← Canonical Python runtime
│   ├── kernel_resolution.py  Bootstrap resolver — load kernel here only
│   ├── core_sandbox/         Canonical sandbox implementations (state, physics, general runtime)
│   └── hhs_*.py              Agents, passes 081–135+, acceleration, linguistic modules
│
├── hhs_backend/              ← FastAPI transport layer (Python)
│   ├── api/                  HTTP route handlers (thin — no business logic)
│   ├── runtime/              Orchestration, distributed consensus, agent loops
│   └── server.py             Application entry point
│
├── hhs_python/               ← ctypes bridge to the C ABI
├── hhs_graph/                ← Graph topology and receipt memory
├── hhs_storage/              ← Durable persistence and replay storage
│
├── HARMONICODE_KERNEL_v44_2_*.py  ← Authoritative kernel (read-only; never redefine)
│
├── hhs_general_runtime_layer_v1.py  ← shim → hhs_runtime/core_sandbox/
├── hhs_state_layer_v1.py            ← shim → hhs_runtime/core_sandbox/
├── hhs_physics_model_v1.py          ← shim → hhs_runtime/core_sandbox/
├── hhs_physics_evolution_v1.py      ← shim → hhs_runtime/core_sandbox/
│
├── hhs_runtime_smoke_tests_v1.py    ← smoke certification suite
├── hhs_regression_suite_v1.py       ← full invariant regression
└── hhs_v1_bundle_runner.py          ← end-to-end certification bundle
```

**Root-level `.py` files** (except the test runners and the kernel) are **compatibility shims only**. They re-export from `hhs_runtime/core_sandbox/`. New code does not go in them.

---

## 3. Environment Setup

### Python (required for all runtime work)

```sh
# Python 3.11 recommended (3.12 not fully tested)
python --version

# Install all dependencies
pip install -r requirements.txt
```

Key packages:
- `fastapi` + `uvicorn[standard]` — HTTP/WebSocket server
- `pydantic` — schema validation
- `networkx` — graph topology
- `numpy`, `sympy` — numerical and symbolic support
- `sqlalchemy`, `aiosqlite` — persistence
- `cryptography` — signed envelopes

### C kernel (required for the backend server and some Python modules)

```sh
mkdir -p hhs_runtime/builds

# Shared library (ctypes ABI)
gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    -fPIC -shared \
    hhs_runtime/c/hhs_runtime_abi.c \
    hhs_runtime/src/hhs_hash216.c \
    -o hhs_runtime/builds/libhhs_runtime.so -lm

# VM81 binary
gcc -O2 -std=c11 -Wall -Wextra \
    -Ihhs_runtime/include -Ihhs_runtime/c \
    hhs_runtime/HARMONICODE_VM_RUNTIME.c \
    -o hhs_runtime/builds/hhs_vm81 -lm
```

> **macOS:** omit `-lm`; the math library is in libc. The shared library will be `.dylib` — update the ctypes load path in `hhs_python/runtime/hhs_ctypes_bridge.py`.

### Node.js (required for the unified GUI only)

```sh
node --version   # must be ≥ 20

cd apps/unified_gui
npm install
npx playwright install chromium   # for browser tests
```

---

## 4. Running the Tests

### Python test suite (from the repository root)

```sh
python hhs_runtime_smoke_tests_v1.py
```
Validates: runtime bootstrap, authoritative kernel loading, receipt/replay continuity, runtime gate integrity, persistence availability. Expects 7 tests to pass. One known pre-existing failure (`no_mnt_data_dependency` in `tools/pass148/package_release.py`) is a stale reference in an unrelated tool and does not block development.

```sh
python hhs_regression_suite_v1.py
```
Validates: valid operations lock, invalid operations quarantine, receipt-chain replay, receipt tampering quarantine, control flow gates, `.hhsprog` execution, `.hhsrun` replay. Expects 10 tests to pass with `all_ok: true`.

```sh
python hhs_v1_bundle_runner.py
```
Runs the full certification sequence: smoke tests → regression suite → demo `.hhsprog` execution → `.hhsrun` replay verification → optional database check → final certification report. Output: `data/runtime/hhs_v1_bundle_certification_report.json`.

### GUI tests (from apps/unified_gui)

```sh
cd apps/unified_gui
npm run verify               # Node.js unit tests (address map, LOD, engine, trace, exact bridge)
```

For browser end-to-end tests:
```sh
npx playwright test
```

### If a test fails

1. Check whether it is a **path/setup issue** (wrong working directory, missing build, import error). Fix the path adapter, not the invariant.
2. Check whether it is a **kernel invariant failure** (Δe ≠ 0, Ψ ≠ 0, etc.). This is a quarantine signal — do not suppress it.
3. Do not weaken invariant checks to make tests pass. Fix the underlying cause.

---

## 5. Core Concepts

### Hash72

A 72-character deterministic identity string produced by the authoritative kernel. Every piece of state, every receipt, every particle address, every event in the trace chain has a Hash72. It is not a checksum — it is a cryptographic witness produced by the kernel's `security_hash72_v44` function.

```python
# Python
from hhs_runtime.kernel_resolution import resolve_authoritative_kernel
kernel = resolve_authoritative_kernel()
h = kernel.security_hash72_v44("my payload")

# JavaScript (browser)
import { hash72String } from "./src/physics/address_map.js";
const h = hash72String("my payload");
```

### Receipt Chain

Every state transition appends an immutable receipt to the ledger:

```
receipt(n)
  → parent: receipt(n-1)
  → payload hash72
  → state hash72
  → audit result
```

A receipt is never modified. A chain replay must produce identical hashes at every step. Any mismatch is a quarantine trigger.

### State Patch

State mutations are expressed as patches, not direct assignments:

```python
from hhs_runtime.core_sandbox.hhs_state_layer_v1 import StatePatch

patch = StatePatch(op="SET", path="sensors.temperature", value={"reading": 36.6})
# The state layer hashes the patch, applies it, emits a receipt
```

### Drift Gate

`Manifold9` and `drift_gate` are the kernel's primary invariant enforcement surfaces. If a computation would violate Δe = 0 or Ψ = 0, the drift gate quarantines it and prevents state advancement. You cannot bypass these; failure is the correct response.

### Execution Pattern

```text
Input
  → Symbolic/Macro Expansion   (exact typed AST, no floats)
  → State Patch                (declared, not silent)
  → Kernel Audit               (Δe, Ψ, Θ15, Ω gates)
  → Receipt Commit             (Hash72 appended to ledger)
```

---

## 6. Python Runtime Layer

### Canonical locations

| What you want | Canonical location |
|---|---|
| Kernel loading | `hhs_runtime/kernel_resolution.py` → `resolve_authoritative_kernel()` |
| General runtime | `hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py` → `AuditedRunner` |
| State layer | `hhs_runtime/core_sandbox/hhs_state_layer_v1.py` → `HHSStateLayerV1` |
| Physics model | `hhs_runtime/core_sandbox/hhs_physics_model_v1.py` |
| Receipt replay | `hhs_receipt_replay_verifier_v1.py` → `HHSReceiptReplayVerifierV1` |
| Control flow gates | `hhs_control_flow_gates_v1.py` → `HHSControlFlowGatesV1` |
| Program format | `hhs_program_format_and_cli_v1.py` |

### AuditedRunner

`AuditedRunner` is the canonical way to execute any operation in the Python runtime. It loads the kernel, verifies invariants, commits a receipt, and returns the result:

```python
from hhs_general_runtime_layer_v1 import AuditedRunner   # root shim

runner = AuditedRunner()
result = runner.run("ADD", {"a": 1, "b": 2})
# result contains: locked=True, receipt_hash72=..., state_hash72=...
```

### Writing a new runtime module

1. Place the canonical implementation in `hhs_runtime/your_module_v1.py`.
2. Add a root-level shim if other modules import from the root:
   ```python
   # your_module_v1.py (root)
   """Compatibility shim. Canonical: hhs_runtime.your_module_v1"""
   from hhs_runtime.your_module_v1 import *
   ```
3. Add tests to `hhs_regression_suite_v1.py` before expanding the module's surface.
4. Every state transition must produce a receipt. Use `AuditedRunner` or the state layer's `apply_patch()`.

---

## 7. Unified GUI (apps/unified_gui)

### Architecture

The GUI is a pure browser application with no build step required — open `index.html` in a web server or use `npx serve .` from `apps/unified_gui/`.

```
boot.js          Application entry point; detects capabilities; starts physics + render
state.js         Redux-style immutable state reducer with Hash72 state hashing
engine.js        5,184-particle fixed-step physics (torus + reciprocal + Lo Shu + closure)
address_map.js   72×72 Hash72 address table, sector/VM81 decomposition
scene.js         Three.js WebGL renderer; profiles: MOBILE_SAFE, BALANCED, DESKTOP_HIGH,
                 HIGH_REFRESH, DIAGNOSTIC
lod.js           Camera-relative LOD hysteresis (LOD0–LOD3)
exact_bridge.js  BigInt exact ratio arithmetic; symbolic AST parser; equality registry
chain.js         Append-only Hash72 trace chain with full replay verification
indexeddb.js     Versioned workspace persistence with quarantine on invalid bundles
```

### Key design rules

- The render layer (float) and the exact layer (BigInt/rational) are separate state channels. A GPU buffer value cannot mutate exact state.
- `updateBuffers()` only runs when `markDirty()` has been called (dirty flag set by the physics clock after each step).
- The physics clock calls `stepSilent()` at 60 Hz; `serialize()` (which runs Hash72) is called only every 15 steps.
- `requestAnimationFrame` fires at the display's native refresh rate (up to 120 Hz on capable monitors).
- The `HIGH_REFRESH` profile auto-selects on WebGL2 desktops with ≥ 8,000,000 physical screen pixels.

### Adding a new workspace panel

1. Add an `<article data-panel="My Panel" hidden>` block to `index.html`.
2. Add a `<button type="button" data-workspace="My Panel">` to the nav.
3. Wire event handlers in `boot.js → _bindControls()`.
4. Add a new `ACTIONS.MY_PANEL_ACTION` constant to `state.js`.
5. Add a case to `reduceApplicationState()` in `state.js`.
6. Add a test to `tests/core.test.mjs`.

### Running only the GUI (no Python backend)

```sh
cd apps/unified_gui
# Use any static file server, e.g.:
npx serve .
# Open http://localhost:3000/index.html
```

---

## 8. Backend Server

### Entry point

```sh
PYTHONPATH=$(pwd) python -m uvicorn hhs_backend.server:app \
    --host 0.0.0.0 --port 8080 --ws websockets --log-level info
```

### Route layer contract

API routes (`hhs_backend/api/`) are **transport only**. They must not contain business logic. All logic routes through the runtime orchestrator (`hhs_backend/runtime/runtime_orchestrator.py`).

```python
# Correct
@router.get("/runtime/state")
async def get_state():
    return await orchestrator.get_state()

# Prohibited — never do this in a route handler
@router.get("/runtime/state")
async def get_state():
    vm.step()           # direct mutation — bypasses audit
    return vm.state
```

### WebSocket

The runtime streams events at `ws://<host>/api/runtime/ws/runtime`. The WebSocket handler is in `hhs_backend/websocket/`. It is streaming transport only — no execution logic belongs there.

---

## 9. Making Changes Safely

### Decision tree before touching any file

1. **Is this a root-level `.py` file?** → It is a shim. Edit the canonical module in `hhs_runtime/` instead.
2. **Does this touch the kernel or Hash72?** → Read `ARCHITECTURE.md` and `AGENTS.md` Prohibited Changes first.
3. **Does this mutate state?** → Add a `StatePatch`, route it through `AuditedRunner` or the state layer, emit a receipt.
4. **Does this change the GUI render loop?** → Keep the dirty flag contract. Do not call `updateBuffers()` unconditionally in `renderFrame`.
5. **Does this add a new module?** → Add tests before expanding the surface. Place canonical code in `hhs_runtime/`, add a shim at root if needed.

### Commit checklist

```sh
python hhs_runtime_smoke_tests_v1.py    # must pass
python hhs_regression_suite_v1.py      # must show all_ok: true
python hhs_v1_bundle_runner.py         # must emit a certified report
```

For GUI changes:
```sh
cd apps/unified_gui && npm run verify   # must pass
```

---

## 10. Debugging and Diagnostics

### Python

```python
from hhs_runtime.kernel_resolution import runtime_bootstrap_report
print(runtime_bootstrap_report())
# Shows: kernel path, resolved symbols, topology status
```

```python
from hhs_general_runtime_layer_v1 import AuditedRunner
runner = AuditedRunner()
# runner.run() returns full audit result including receipt and invariant status
```

### GUI — browser console

The browser exposes the full runtime at the console level. Open DevTools and use:

```js
// Physics diagnostics
HHSApp.refreshDiagnostics()

// Current render state
HHSRender.captureDiagnostics()
// Returns: profile, mode, effective_pixels, effective_pixel_ratio, color_depth_bits, frame, webgl2

// Particle engine
HHSPhysics.serialize()
// Returns: step_count, state_hash72, projection_sample

// Trace chain
HHSTrace.getHead()
HHSTrace.getEvents(0, 10)   // first 10 events
HHSTrace.seal()             // seal and get bundle hash

// Exact calculation
HHSSymbolic.parse("u^72==1; P^2(MOD)(pq)")
```

### Replay verification

```js
// Replay the physics engine from the current receipt
HHSApp.physics.replay(HHSPhysics.serialize())
// Returns: { match: true/false, classification: "PASS157_REPLAY_MATCH"|"REPLAY_MISMATCH" }
```

---

## 11. Prohibited Patterns

| Pattern | Why it is prohibited |
|---|---|
| `from HARMONICODE_KERNEL_v44_2_*.py import *` (direct import, path varies) | Use `kernel_resolution.resolve_authoritative_kernel()` |
| Redefining `Hash72` or `security_hash72_v44` | Breaks all receipt continuity across the entire ledger |
| Calling `drift_gate` with a pre-computed pass result | The gate must evaluate the actual computation |
| Bypassing `Manifold9` | Removes integrity enforcement |
| Float arithmetic inside the kernel or state layer | Violates Δe = 0; use `Fraction` or BigInt |
| `xy == yx` (collapsing ordered products) | These are distinct elements in the Harmonicode algebra |
| Mutating state without a patch + receipt | The audit trail is broken; replay will fail |
| Execution logic in API route handlers | Routes are transport; logic belongs in the orchestrator |
| Execution logic in WebSocket handlers | Same rule |
| Weakening invariant checks to fix a test | The test is telling you something real; fix the root cause |

---

*This document reflects the codebase as of Pass 157. When the codebase is reorganized under `hhs_runtime/`, update `AGENTS.md` and this file in the same commit.*
