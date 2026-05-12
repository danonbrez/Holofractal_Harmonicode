# HHS Runtime Integration Matrix
#
# Repository:
# danonbrez/Holofractal_Harmonicode
#
# Purpose:
# Define the canonical execution routing topology for the
# HHS Runtime OS during the hybrid migration phase.
#
# This document exists to:
#
# - normalize runtime entrypoints
# - eliminate duplicate authority paths
# - stabilize bootstrap behavior
# - preserve replay continuity
# - prevent namespace drift
# - unify Runtime OS orchestration
#
# Invariants:
# Δe = 0
# Ψ = 0
# Θ15 = true
# Ω = true

---

# 1. CURRENT EXECUTION STATE

The repository currently contains:

| Runtime Layer | Status |
|---|---|
| root compatibility runtime | ACTIVE |
| canonical package runtime | ACTIVE |
| backend orchestration | ACTIVE |
| replay infrastructure | ACTIVE |
| graph persistence | ACTIVE |
| websocket runtime | ACTIVE |
| Runtime OS GUI workspace | ACTIVE |
| package migration | IN PROGRESS |

Therefore runtime entrypoints must now be explicitly normalized.

---

# 2. PRIMARY EXECUTION PRINCIPLE

The Runtime OS MUST behave as:

```text
ONE deterministic execution substrate
```

All runtime surfaces must converge toward:

```text
canonical authority routing
```

rather than independent bootstrap logic.

---

# 3. ENTRYPOINT INTEGRATION MATRIX

## Runtime Bootstrap

| Entrypoint | Canonical Authority |
|---|---|
| `hhs_runtime/kernel_resolution.py` | runtime root + kernel authority |
| `hhs_runtime/__init__.py` | canonical runtime namespace |
| `pytest.ini` | pytest topology normalization |

### Rules

- no cwd-relative runtime discovery
- no `/mnt/data` assumptions
- no duplicate kernel resolution logic

---

## Certification Layer

| Entrypoint | Canonical Authority |
|---|---|
| `hhs_v1_bundle_runner-2.py` | global certification orchestrator |
| `hhs_runtime_smoke_tests_v1.py` | topology-aware smoke validation |
| `hhs_regression_suite_v1.py` | regression/replay continuity validation |

### Rules

- smoke suite owns topology validation
- bundle runner owns LOCKED-state certification
- regression suite owns replay continuity validation
- no duplicated certification logic

---

## Runtime Layer

| Entrypoint | Canonical Authority |
|---|---|
| `hhs_general_runtime_layer_v1.py` | compatibility shim |
| `hhs_runtime/core_sandbox/...` | canonical runtime implementation |
| runtime controllers | canonical execution authority |

### Rules

- root runtime files forward only
- canonical runtime lives under package hierarchy
- runtime mutations must remain receipt-linked

---

## Persistence Layer

| Entrypoint | Canonical Authority |
|---|---|
| `hhs_database_integration_layer_v1.py` | persistence adapter |
| canonical storage layer | authoritative persistence |
| replay persistence | replay continuity authority |

### Rules

- persistence derives from repo-root authority
- no local implicit DB topology
- replay continuity preserved across persistence

---

## Replay Layer

| Entrypoint | Canonical Authority |
|---|---|
| `hhs_receipt_replay_verifier_v1.py` | replay verification |
| receipt chain | deterministic continuity authority |

### Rules

- replay must remain deterministic
- no state mutation outside receipt chain
- receipt continuity globally preserved

---

## Backend Runtime

| Entrypoint | Canonical Authority |
|---|---|
| `hhs_backend/server.py` | Runtime OS bootstrap |
| websocket runtime | live runtime synchronization |
| runtime event bus | execution event authority |

### Rules

- backend runtime uses canonical bootstrap only
- websocket runtime derives from canonical runtime state
- runtime events remain replay-consistent

---

## Graph Runtime

| Entrypoint | Canonical Authority |
|---|---|
| `hhs_graph/` | graph-native runtime memory |
| replay graph | execution continuity |
| branch/rejoin graph | adaptive runtime topology |

### Rules

- graph memory remains receipt-linked
- graph state must remain replayable
- graph ingestion uses canonical runtime authority

---

## GUI Runtime OS

| Entrypoint | Canonical Authority |
|---|---|
| `gui/hhs-mobile-runtime-console/` | Runtime OS shell |
| runtime visualizer | live runtime state projection |
| graph visualizer | graph-native workspace topology |

### Rules

- GUI performs no local runtime authority
- GUI acts as projection surface only
- runtime execution remains backend-authoritative

---

# 4. IMPORT NORMALIZATION RULES

## ALLOWED

```python
from hhs_runtime.kernel_resolution import ...
from hhs_runtime.core_sandbox...
from hhs_backend...
from hhs_graph...
```

## DISALLOWED

```python
cwd-relative imports
/mnt/data runtime paths
duplicate runtime implementations
direct bootstrap duplication
```

---

# 5. RUNTIME EXECUTION FLOW

Canonical Runtime OS flow:

```text
repo root
    ↓
kernel resolution
    ↓
runtime namespace
    ↓
runtime controller
    ↓
receipt commit
    ↓
replay verification
    ↓
persistence
    ↓
graph ingestion
    ↓
websocket synchronization
    ↓
GUI Runtime OS projection
```

No subsystem should independently redefine:

- runtime authority
- persistence authority
- replay authority
- kernel authority

---

# 6. COMPATIBILITY SHIM POLICY

Root-level files remain temporarily active during migration.

They MUST:

```text
forward execution only
```

They MUST NOT:

- duplicate runtime logic
- redefine runtime authority
- bypass replay continuity
- mutate runtime state independently

---

# 7. CURRENT PRIMARY INTEGRATION RISKS

| Risk | Description |
|---|---|
| mixed namespace imports | root vs package authority |
| duplicate bootstrap logic | inconsistent runtime state |
| stale runtime assumptions | `/mnt/data`, cwd-relative paths |
| replay divergence | non-canonical mutation surfaces |
| persistence drift | multiple DB roots |
| GUI-local execution | non-authoritative runtime execution |

---

# 8. CURRENT CONSOLIDATION TARGETS

## Immediate

- normalize imports
- unify bootstrap routing
- eliminate duplicate kernel resolution
- stabilize bundle orchestration
- stabilize persistence authority

## Near-Term

- backend runtime consolidation
- websocket event normalization
- graph/runtime synchronization
- GUI Runtime OS shell stabilization

## Long-Term

- graph-native Runtime OS
- multimodal execution substrate
- harmonic reconstruction codec
- deterministic simulation engine
- adaptive replayable agents
- Runtime OS applications

---

# 9. FINAL RUNTIME OBJECTIVE

The repository is converging toward:

```text
deterministic graph-native Runtime OS
```

where:

- every execution is replayable
- every mutation is receipt-linked
- every subsystem shares one runtime authority
- every application is a runtime projection
- every modality routes through the same substrate

including:

- calculators
- breadboards
- schematic IDEs
- quantum emulators
- physics simulations
- games
- adaptive agents
- multimodal Runtime OS workspaces

all operating over:

```text
ONE canonical deterministic execution manifold
```