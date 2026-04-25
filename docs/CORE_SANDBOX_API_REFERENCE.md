# HHS Core Sandbox API Reference

This document defines the exposed API surface for the sealed Layer 0 sandbox.

Canonical imports must use:

```python
from hhs_runtime.core_sandbox import ...
```

Root-level modules are compatibility shims only.

---

## `hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1`

### Constants

#### `DEFAULT_KERNEL_PATH`
Default external kernel path hint. The standalone core sandbox does not require this path to exist.

#### `GENESIS_RECEIPT_HASH72`
Genesis parent receipt identifier for receipt-chain initialization.

#### `HASH72_ALPHABET`
Canonical 72-symbol alphabet used by the sandbox Hash72 digest encoder.

---

### Functions

#### `canonicalize_for_hash72(obj: Any) -> Any`
Converts Python objects into deterministic JSON-compatible structures.

Handles:
- `Fraction`
- `Path`
- `tuple`
- `list`
- `dict`
- objects exposing `to_dict()`
- dataclass-like objects with `__dict__`

Used before hashing, persistence, and receipt generation.

#### `canonical_json(obj: Any) -> str`
Returns deterministic compact JSON with sorted keys.

#### `security_hash72_v44(payload: Any, *, domain: str = "HHS") -> str`
Produces a deterministic Hash72-native digest string prefixed with `H72N-`.

Inputs:
- `payload`: any canonicalizable object
- `domain`: domain-separation label

Returns:
- Hash72 receipt string

#### `load_authoritative_kernel(kernel_path=DEFAULT_KERNEL_PATH)`
Standalone hook for external kernel loading. In the current core sandbox it returns `None` to prevent import-time dependency on root files or external artifacts.

---

### Classes

#### `Hash72Authority`
Hash authority wrapper.

##### `commit(payload: Any, *, domain: str = "HHS_RUNTIME_COMMITMENT") -> str`
Creates a domain-separated Hash72 commitment.

##### `integrity_bundle(payload: Any, *, symbols: str = "xyzw") -> dict`
Creates a Hash72 integrity bundle for a payload.

---

#### `HashCommitmentReceiptV2`
Frozen dataclass containing a single transition receipt.

Fields:
- `phase`
- `operation`
- `parent_receipt_hash72`
- `input_hash72`
- `pre_state_hash72`
- `operation_hash72`
- `post_state_hash72`
- `witness_hash72`
- `receipt_hash72`
- `integrity_hash72`
- `gate_status`
- `locked`
- `quarantine`
- `reason`

##### `to_dict() -> dict`
Serializes the receipt.

---

#### `HHSState`
Dataclass for runtime state snapshotting.

##### `snapshot() -> dict`
Returns canonical state view with phase, vars, tensors, parent receipt, tip, and metadata.

---

#### `HashCommitmentLayerV2`
Receipt-chain manager.

##### `commit_transition(...) -> HashCommitmentReceiptV2`
Commits a transition with pre-state, post-state, witness, and gate status.

Required keyword arguments:
- `operation`
- `input_payload`
- `pre_state`
- `post_state`
- `witness`
- `gate_status`

Optional:
- `reason`

##### `verify_chain() -> dict`
Verifies parent receipt continuity.

---

#### `KernelGateAdapter`
Sandbox audit gate.

##### `audit_value(value: Any, *, phase: int = 0) -> dict`
Audits a scalar or fraction-compatible value and returns a witness object. Invalid numeric conversion returns a quarantined witness.

---

#### `OperationRegistry`
Registry for named operations.

##### `register(name: str, fn: Callable) -> None`
Registers an operation.

##### `get(name: str) -> Callable`
Retrieves an operation or raises `KeyError`.

##### `names() -> list[str]`
Returns registered operation names.

---

#### `AuditedRunner`
Primary execution interface.

##### `execute(operation: str, *args: Any, input_payload: Any | None = None) -> dict`
Runs an operation through the audit and receipt chain.

Built-in operations:
- `ADD(a,b)`
- `SUB(a,b)`
- `MUL(a,b)`
- `DIV(a,b)`
- `SUM(xs)`
- `SORT(xs)`
- `BINARY_SEARCH(sorted_list, target)`

Returns:
- `ok: True` with `result`, `receipt`, `chain`
- or `ok: False`, `quarantine: True`, `reason`, `receipt`

---

## `hhs_runtime.core_sandbox.hhs_state_layer_v1`

### Constants

#### `STATE_LAYER_VERSION`
State machine version label.

#### `GENESIS_STATE_HASH72`
Genesis state hash label.

---

### Classes

#### `StatePatch`
Dataclass for state patch operations.

Fields:
- `op`: `SET`, `DELETE`, or `MERGE`
- `path`: dotted target path
- `value`
- `metadata`

##### `to_dict() -> dict`
Serializes the patch.

---

#### `StateTransitionRecord`
Dataclass for audited state transition history.

##### `to_dict() -> dict`
Serializes the transition.

---

#### `HHSStateLayerV1`
Deterministic state machine.

##### `snapshot() -> dict`
Returns canonical state snapshot.

##### `get(path: str, default=None) -> Any`
Reads a dotted path without mutation.

##### `exists(path: str) -> bool`
Checks path existence.

##### `apply_patch_to_copy(patch: StatePatch) -> dict`
Applies a patch to a copy of current state without committing.

##### `state_mass(state: dict) -> int`
Computes deterministic state audit carrier mass.

##### `apply_patch(patch: StatePatch) -> dict`
Audits and commits/quarantines a state patch.

##### `set(path: str, value: Any, **metadata) -> dict`
Convenience `SET` patch.

##### `delete(path: str, **metadata) -> dict`
Convenience `DELETE` patch.

##### `merge(path: str, value: dict, **metadata) -> dict`
Convenience `MERGE` patch.

##### `replay_from_history(history=None) -> dict`
Replays transition history and verifies state hash continuity.

##### `save(path: str | Path) -> dict`
Persists state snapshot and history.

##### `load(path: str | Path, *, kernel_path=DEFAULT_KERNEL_PATH) -> HHSStateLayerV1`
Loads a saved state snapshot.

---

## `hhs_runtime.core_sandbox.hhs_physics_model_v1`

### Classes

#### `PhysicalObservation`
Dataclass for raw physical observations.

Fields:
- `sensor_id`
- `value`
- `timestamp`

### Functions

#### `map_observation_to_symbolic(obs: PhysicalObservation) -> dict`
Maps a physical observation to a deterministic symbolic constraint payload.

#### `build_state_patch(symbolic: dict) -> dict`
Builds a state patch from symbolic physical observation data.

---

## `hhs_runtime.core_sandbox.hhs_database_integration_layer_v1`

### Classes

#### `HHSDatabase`
Simple deterministic JSON database interface.

##### `save(data: dict) -> None`
Writes JSON to disk, creating parent directories.

##### `load() -> dict`
Loads JSON or returns `{}` if missing.

---

## Boundary Rule

`core_sandbox` must never import cognition, planning, agents, semantic reconstruction, or self-modification modules. Higher layers may import downward into `core_sandbox`; Layer 0 must not import upward.
