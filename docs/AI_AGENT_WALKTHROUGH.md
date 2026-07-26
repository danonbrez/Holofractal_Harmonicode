# HHS AI Agent Walkthrough

This document is the navigation contract for AI agents (coding assistants, Copilot, Codex, Claude, GPT, and similar) operating inside the Holofractal Harmonicode repository. Read `AGENTS.md` first, then read this document in full before making any changes.

---

## Table of Contents

1. [What Kind of System This Is](#1-what-kind-of-system-this-is)
2. [Codebase Orientation in 5 Minutes](#2-codebase-orientation-in-5-minutes)
3. [The Kernel Contract](#3-the-kernel-contract)
4. [Invariants That Must Never Be Violated](#4-invariants-that-must-never-be-violated)
5. [Prohibited Changes — Hard Stops](#5-prohibited-changes--hard-stops)
6. [How to Navigate the Repository](#6-how-to-navigate-the-repository)
7. [How to Make a Safe Change](#7-how-to-make-a-safe-change)
8. [Test Commands and What They Verify](#8-test-commands-and-what-they-verify)
9. [The GUI Layer Rules](#9-the-gui-layer-rules)
10. [Common Failure Patterns to Avoid](#10-common-failure-patterns-to-avoid)
11. [Worked Examples](#11-worked-examples)

---

## 1. What Kind of System This Is

HHS is a **deterministic, receipt-locked cognitive operating substrate**. It is not a web app with a backend. It is not a collection of utilities. Every computation is:

- produced by a single authoritative kernel (Hash72 `security_hash72_v44`),
- witnessed by an immutable receipt appended to a ledger,
- verifiable by replaying the receipt chain from genesis,
- gated by four kernel invariants before any state advancement.

The consequence for AI agents: **there is no shortcut path**. You cannot write code that skips receipts, replaces the kernel, uses floats instead of rationals, or adds a "fast path" that bypasses `drift_gate`. Any such change will fail the regression suite and must be reverted.

---

## 2. Codebase Orientation in 5 Minutes

### Files you will most often read or edit

| File | What it is |
|---|---|
| `apps/unified_gui/src/physics/engine.js` | 5,184-particle physics engine; `stepSilent()`, `serialize()`, `replay()` |
| `apps/unified_gui/src/physics/address_map.js` | Hash72 address table; `PARTICLE_COUNT = 5184`; `hash72String()` |
| `apps/unified_gui/src/render/scene.js` | Three.js renderer; render profiles; dirty flag; `updateBuffers()` |
| `apps/unified_gui/src/app/boot.js` | Application lifecycle; `detectCapabilities()`; physics clock |
| `apps/unified_gui/src/app/state.js` | Immutable state reducer; `ACTIONS`; `canonicalStateHash()` |
| `apps/unified_gui/src/kernel/exact_bridge.js` | BigInt exact ratio arithmetic; symbolic AST parser |
| `apps/unified_gui/src/trace/chain.js` | Append-only Hash72 event chain |
| `hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py` | Canonical `AuditedRunner` |
| `hhs_runtime/core_sandbox/hhs_state_layer_v1.py` | Canonical state machine |
| `hhs_runtime/kernel_resolution.py` | The only authorized kernel loader |
| `hhs_runtime_smoke_tests_v1.py` | Smoke test suite |
| `hhs_regression_suite_v1.py` | Full regression suite |
| `hhs_v1_bundle_runner.py` | End-to-end certification bundle |

### Files you must not touch

| File | Reason |
|---|---|
| `HARMONICODE_KERNEL_v44_2_*.py` | Authoritative kernel — read-only |
| Root-level `hhs_general_runtime_layer_v1.py`, `hhs_state_layer_v1.py`, `hhs_physics_model_v1.py`, `hhs_physics_evolution_v1.py` | Shims — canonical code is in `hhs_runtime/core_sandbox/` |
| `.github/agents/` | Agent configuration — not your concern |

### Files you should understand but rarely need to edit

- `ARCHITECTURE.md` — authoritative layer topology
- `AGENTS.md` — codex navigation contract and prohibited changes
- `hhs_runtime/kernel_resolution.py` — bootstrap resolver (only edit to fix path resolution bugs)

---

## 3. The Kernel Contract

The single authoritative kernel is:

```
HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py
```

**Required kernel symbols:**

```python
AUTHORITATIVE_TRUST_POLICY_V44   # trust policy declaration
security_hash72_v44              # the canonical Hash72 function
NativeHash72Codec                # low-level codec
Manifold9                        # primary integrity surface
Tensor                           # tensor type
```

**The only authorized way to load the kernel:**

```python
from hhs_runtime.kernel_resolution import resolve_authoritative_kernel
kernel = resolve_authoritative_kernel()
```

Never construct an import path to the kernel file manually. Never copy the kernel function into a different module. Never monkeypatch it.

---

## 4. Invariants That Must Never Be Violated

Every state transition must pass all four:

| Invariant | Contract |
|---|---|
| **Δe = 0** | No energy accumulation across a closed operation. A computation that produces a net surplus or deficit fails this gate. |
| **Ψ = 0** | Phase residue zero — no symbolic drift between input and output representations. |
| **Θ15 = true** | The 15-step closure gate must confirm that the operation closes within 15 steps. |
| **Ω = true** | The global integrity witness must verify — the receipt chain is intact. |

If your code causes any of these to fail in the regression suite, the change is wrong. Do not suppress the failure — find the root cause.

### Arithmetic rule

No float arithmetic inside the kernel, state transitions, or the physics authority layer.  
Use `Fraction` (Python) or `BigInt` with exact rational representations (JavaScript).

The particle physics engine (`engine.js`) uses `Float64` arrays for 3D projection coordinates only — this is the render float layer, which is explicitly separated from the exact authority layer. Positions in `engine.js` are projections, not authority values.

---

## 5. Prohibited Changes — Hard Stops

If you are about to make one of these changes, **stop immediately** and explain to the user why it cannot be done:

| Prohibited action | Why |
|---|---|
| Redefine `Hash72` or `security_hash72_v44` in any module | All existing receipts in the ledger would be irreconcilable. Replay would fail universally. |
| Bypass `Manifold9` or `drift_gate` | These are the only enforcement surfaces for Δe = 0 and Ψ = 0. Bypassing them means invariants are no longer enforced — silently. |
| Create an alternate integrity or truth path | Two divergent receipt chains cannot be merged. The ledger becomes permanently forked. |
| Replace rational arithmetic with floats in the kernel or state layer | Float rounding violates Δe = 0. Even `float(Fraction(1, 3))` introduces irrecoverable error. |
| Silently collapse ordered products (`xy` ≠ `yx`) | These are distinct non-commutative elements. Collapsing them silently corrupts the symbolic algebra. |
| Mutate state without a `StatePatch` and receipt | The audit trail is broken. The system cannot replay what it cannot reconstruct. |
| Add execution logic to an API route handler | Routes are transport. The orchestrator owns execution. |
| Add execution logic to a WebSocket handler | Same rule. |
| Weaken or remove an invariant check to fix a test | The test failure is a signal. Fix the code, not the test. |

---

## 6. How to Navigate the Repository

### Finding the canonical implementation of something

1. If you see a root-level `.py` file like `hhs_general_runtime_layer_v1.py`, open it. It will say `from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import *`. The canonical code is in `hhs_runtime/core_sandbox/`.
2. If you see an import from `hhs_runtime.hhs_<something>_v1`, the canonical module is `hhs_runtime/hhs_<something>_v1.py`.
3. For JavaScript modules, every import is a relative path — follow it directly.
4. Use `grep -r "class HHSStateLayerV1" hhs_runtime/` to find where a symbol is defined.

### Understanding a pass

The codebase is organized by "passes" (development milestones). Pass 157 is the current GUI pass. Passes < 145 are historical. When a file name contains `pass145` or `pass157`, it belongs to that pass's surface area. You generally only need to work in Pass 157 or the root-level test infrastructure.

### Finding which test covers your change

- Python kernel/runtime changes → `hhs_regression_suite_v1.py` (check the test names at the top)
- GUI physics changes → `apps/unified_gui/tests/core.test.mjs`
- LOD changes → `apps/unified_gui/tests/lod.test.mjs`
- Browser end-to-end → `apps/unified_gui/tests/browser/app.spec.mjs`

---

## 7. How to Make a Safe Change

### Step 1 — Understand before touching

Before changing any file:
1. Read the file header/docstring to understand its role.
2. Identify which test covers it.
3. Confirm the change does not touch the kernel, Hash72, Manifold9, or drift_gate.

### Step 2 — Plan the minimal change

Changes must be minimal. The architecture is intentionally conservative. Prefer:
- Modifying an existing module over creating a new abstraction.
- Preserving existing module interfaces.
- Thin adapters over new layers.

### Step 3 — For Python changes

Every state mutation must follow this pattern:

```python
from hhs_general_runtime_layer_v1 import AuditedRunner

runner = AuditedRunner()
result = runner.run("MY_OPERATION", {"key": "value"})
# result.locked == True  ← invariants passed
# result.receipt_hash72  ← new receipt appended to ledger
```

If you need a state transition, use `StatePatch`:

```python
from hhs_runtime.core_sandbox.hhs_state_layer_v1 import HHSStateLayerV1, StatePatch

layer = HHSStateLayerV1()
patch = StatePatch(op="SET", path="my.key", value={"data": 42})
record = layer.apply_patch(patch)
# record.locked == True
# record.receipt_hash72 is set
```

### Step 4 — For JavaScript (GUI) changes

State mutations go through typed actions:

```js
import { ACTIONS } from "./state.js";

// Add your action constant:
export const ACTIONS = Object.freeze({
  ...existing,
  MY_NEW_ACTION: "MY_NEW_ACTION",
});

// Add a case in reduceApplicationState():
case ACTIONS.MY_NEW_ACTION:
  next = { ...state, my_field: action.payload.value };
  break;

// Dispatch from boot.js:
this._dispatch({ type: ACTIONS.MY_NEW_ACTION, payload: { value: 42 } });
```

Never mutate the state object directly. The state reducer is the only mutation authority.

### Step 5 — Run the tests

```sh
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
```

For GUI changes:
```sh
cd apps/unified_gui && npm run verify
```

All tests must pass before committing.

---

## 8. Test Commands and What They Verify

### `python hhs_runtime_smoke_tests_v1.py`

| Test name | What it checks |
|---|---|
| `kernel_authority` | Kernel loads; all 5 required symbols present |
| `runtime_gate_integrity` | Drift gate enforcement function available |
| `database_bridge_available` | SQLite persistence accessible |
| `regression_suite_importable` | Regression suite can be imported |
| `no_mnt_data_dependency` | No stale `/mnt/` path references in key modules |
| `runtime_package_topology` | `hhs_runtime` and `hhs_backend` importable |

Expected: 7 pass. One known pre-existing failure on `no_mnt_data_dependency` in a tool file — does not block development.

### `python hhs_regression_suite_v1.py`

10 tests covering: valid operation lock, invalid operation quarantine, receipt chain replay, receipt tampering quarantine, parent-link tampering quarantine, IF gate, LOOP gate (terminating), LOOP stutter quarantine, `.hhsprog` execution, `.hhsrun` replay verification.

Expected: `all_ok: true`, 10 passed, 0 failed.

### `python hhs_v1_bundle_runner.py`

Full certification bundle. Runs all suites and emits `data/runtime/hhs_v1_bundle_certification_report.json` with a `PASS` or `FAIL` status.

### `cd apps/unified_gui && npm run verify`

Node.js unit tests:
- `tests/core.test.mjs` — address map (5,184 particles, uniqueness, sector coverage), physics engine (determinism, step/replay), trace chain (append-only, verify, seal), exact bridge (BigInt ratio arithmetic), state reducer (all actions, hash progression)
- `tests/lod.test.mjs` — LOD threshold validation, hysteresis transitions, camera distance calculation

---

## 9. The GUI Layer Rules

### Two separate state authorities

| Authority | What it contains | What can change it |
|---|---|---|
| **Exact** | BigInt ratios, symbolic AST, Hash72 addresses, VM81 cells, Lo Shu values, trace events, typed actions | Only typed `_dispatch()` calls |
| **Render projection** | Float32 positions, velocities, colors, GPU buffers, camera state | Only `updateBuffers()` after `markDirty()` |

A float in a GPU buffer cannot mutate the exact layer. If you write code that reads a canvas pixel and writes it to the state, you are violating this boundary.

### The render loop contract

```js
// renderFrame runs at the display refresh rate (up to 120 Hz)
renderFrame = () => {
  this.controls?.update();           // camera update — always
  if (this._dirty) {                 // buffer copy — only when physics stepped
    this.updateBuffers();
    this._dirty = false;
  }
  this.renderer.render(this.scene, this.camera);   // always render
  this.frame += 1;
  this.animationFrame = requestAnimationFrame(this.renderFrame);
};
```

Do not call `updateBuffers()` unconditionally in `renderFrame`. The dirty flag exists to prevent a 5,184-particle buffer copy every frame when physics is paused.

### Physics clock contract

```js
// Physics clock runs at 60 Hz (setInterval at 1000/60)
this.physicsTimer = window.setInterval(() => {
  if (document.hidden || !this.physics.running) return;
  this.physics.stepSilent(1);    // integrate — no serialize
  this.render?.markDirty();      // signal render to copy buffers
  if (this.physics.stepCount % 15 === 0) {
    const receipt = this.physics.serialize();  // Hash72 — only every 15 steps
    this.lastPhysicsReceipt = receipt;
    this._dispatch({ ... });
  }
}, 1000 / 60);
```

Do not call `serialize()` on every tick. `serialize()` runs `hash72String` over the projection sample — at 60 Hz this is expensive.

### Render profiles

| Profile | pixelRatio | Auto-selected when |
|---|---|---|
| `MOBILE_SAFE` | 1.0 | No WebGL2 or mobile device |
| `BALANCED` | 1.25 | WebGL2 desktop, < 8M pixels |
| `DESKTOP_HIGH` | 1.75 | Manual selection |
| `HIGH_REFRESH` | 4.0 | WebGL2 desktop, screen has ≥ 8M physical pixels |
| `DIAGNOSTIC` | 1.0 | Manual selection |

---

## 10. Common Failure Patterns to Avoid

### Pattern: "I'll use a float here, it's just for display"

Wrong. The exact bridge and state layer must stay rational. The render projection is the only place floats are permitted, and it is clearly separated from the exact layer in `scene.js`.

### Pattern: "I'll create a new Hash72 function that's faster"

Wrong. `hash72String` in `address_map.js` and `security_hash72_v44` in the kernel are the only authorized Hash72 implementations. A new implementation would produce different outputs for the same inputs, breaking receipt chain verification.

### Pattern: "The test is wrong, I'll change the assertion"

Almost certainly wrong. Invariant assertions in the test suite are the specification. If the test says a receipt chain replay must match, and your code produces a mismatch, your code is wrong.

### Pattern: "I'll add this shortcut path for performance"

Read the existing performance optimizations first (`stepSilent()`, dirty flag, cached `_addressRootHash72`, hoisted `_reuseColor`/`_reuseMatrixObject`). New "shortcuts" must not skip receipts, bypass drift_gate, or violate the execution pattern. If a performance improvement is needed, profile it, then implement it as a thin adapter that preserves all audit semantics.

### Pattern: "I'll move this into a helper file to keep things clean"

Before creating a new file: check whether an existing module already does it. The codebase has ~200 `hhs_runtime/` modules. Search first. Prefer modifying an existing module over creating a new abstraction.

### Pattern: "This import works from the root, so I'll use the root shim"

The shims exist for backward compatibility. New code should import from the canonical location (`hhs_runtime.core_sandbox.*`) not from the root shim.

---

## 11. Worked Examples

### Example A: Fix a physics bug without breaking receipts

**Problem:** particles drift off the torus after many steps.

**Correct approach:**
1. Identify the force computation in `engine.js → _computeForces()`.
2. Understand which weight constant is involved (`torusWeight`, `reciprocalWeight`, etc.).
3. Change the constant or the force formula.
4. Run: `cd apps/unified_gui && npm run verify` — the determinism test in `core.test.mjs` will catch if the step output changes unexpectedly.
5. The receipt chain is in JavaScript and is reset on each browser session; no Python receipt chain is affected.

**Wrong approach:** Changing the physics to use floats for the force calculation "because it's just projection." The `Float64Array` positions are projection only; the force model must remain numerically stable.

### Example B: Add a new render diagnostic field

**Problem:** need to expose the current LOD level in diagnostics.

**Correct approach:**
1. Track the LOD level in `HHSRenderProjection` as `this._currentLod`.
2. Update it in `updateBuffers()` or a new `updateLod()` method.
3. Add `current_lod: this._currentLod` to the return value of `diagnostics()`.
4. No state action needed — diagnostics are read-only observations.

**Wrong approach:** Adding the LOD level to the Redux state via a new action on every frame. That would dispatch 60 state mutations per second, recomputing `canonicalStateHash()` (a full Hash72) on every render tick.

### Example C: Add a new Python runtime module

**Problem:** need a new bounded queue for ordered receipts.

**Correct approach:**
1. Create `hhs_runtime/hhs_bounded_receipt_queue_v1.py`.
2. The module must load the kernel via `kernel_resolution.resolve_authoritative_kernel()` if it calls Hash72.
3. State transitions must use `AuditedRunner` or `StatePatch`.
4. Add at least two regression tests to `hhs_regression_suite_v1.py`: one that passes and one that correctly quarantines an invalid operation.
5. Run `python hhs_regression_suite_v1.py` — all 10 original tests must still pass, plus your new ones.
6. If you need a root-level shim: `echo 'from hhs_runtime.hhs_bounded_receipt_queue_v1 import *' > hhs_bounded_receipt_queue_v1.py`.

**Wrong approach:** Creating the module in the repository root or in `hhs_backend/api/`. Root is for shims. API is transport.

### Example D: Debug a receipt chain mismatch

**Problem:** `hhs_regression_suite_v1.py` reports `REPLAY_MISMATCH`.

**Diagnosis steps:**
1. Check whether any recent change modified `canonical_json()` in `hhs_general_runtime_layer_v1.py` or `canonicalize_for_hash72()`. Any change to how objects are serialized before hashing will break existing receipt chains.
2. Check whether any float value is entering a path that previously used `Fraction`. Float `repr` is platform-dependent; `Fraction` serializes as `{"__fraction__": [n, d]}`.
3. Check whether the order of keys in a dict changed. `canonical_json()` sorts keys, so ordering in the source dict does not matter — but if you replaced a `sorted()` with an unsorted dict somewhere in the serialization chain, that is the bug.
4. Revert the change that introduced the mismatch. Do not patch the replay verifier to accept the new hash.

---

*This document reflects the codebase as of Pass 157. Update it whenever a new pass changes the canonical module locations, test suite, or invariant set.*
