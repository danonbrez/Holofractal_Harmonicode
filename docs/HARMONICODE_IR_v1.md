# HARMONICODE_IR_v1

## 0. Purpose

HARMONICODE IR (Intermediate Representation) is the canonical execution form of all programs, calculator expressions, AI patches, and DAW operations.

The IR is:

- deterministic
- non-commutative aware
- constraint-first
- state-transition explicit
- kernel-auditable
- receipt-emitting

Every source must lower into IR before execution.

---

## 1. Core model

IR is a sequence of **Constraint Blocks** and **State Transitions**.

```json
{
  "kind": "IRProgram",
  "blocks": [
    {
      "kind": "ConstraintBlock",
      "constraints": [],
      "projection_layer": "eigenstate | normalized | mixed"
    },
    {
      "kind": "StateTransition",
      "effect": "PURE | AUDITED | EXTERNAL",
      "patch": {},
      "receipt": null
    }
  ]
}
```

---

## 2. Expression nodes

### 2.1 Ordered product

```json
{
  "kind": "OrderedProduct",
  "left": "x",
  "right": "y"
}
```

### 2.2 Fused product

```json
{
  "kind": "FusedProduct",
  "symbol": "xy"
}
```

### 2.3 Power

```json
{
  "kind": "Power",
  "base": "x",
  "exponent": 2
}
```

### 2.4 Chain equality

```json
{
  "kind": "ChainEq",
  "terms": ["P^2-pq","n^4","xy"]
}
```

### 2.5 Distinct chain

```json
{
  "kind": "DistinctChain",
  "terms": ["x","y","xy","yx"]
}
```

---

## 3. Constraint graph

All constraints are compiled into a graph:

```json
{
  "nodes": [...],
  "edges": [
    {"type":"eq","from":"xy","to":"-1/yx"},
    {"type":"neq","from":"xy","to":"yx"}
  ]
}
```

The solver operates on the full graph, not individual equations.

---

## 4. State transitions

### 4.1 Pure

Symbolic rewrite only.

```json
{
  "kind": "StateTransition",
  "effect": "PURE",
  "operation": "rewrite",
  "input": "xy=-1/yx",
  "output": "yx=-xy"
}
```

### 4.2 Audited

Requires kernel.

```json
{
  "kind": "StateTransition",
  "effect": "AUDITED",
  "patch": {
    "op": "SET",
    "path": "phase.anchor",
    "value": 36
  }
}
```

### 4.3 External

```json
{
  "kind": "StateTransition",
  "effect": "EXTERNAL",
  "operation": "audio.sample",
  "payload": {}
}
```

---

## 5. Receipt model

Every audited or external transition emits:

```json
{
  "receipt_hash72": "...",
  "parent_receipt_hash72": "...",
  "status": "LOCKED | QUARANTINED",
  "phase_locked": true,
  "temporal_ok": true
}
```

Replay must verify:

```text
recompute(receipt_core) == receipt_hash72
```

---

## 6. Projection layers

Each constraint block may specify layer:

```text
eigenstate
normalized
projection
```

Example:

```json
{
  "kind":"ConstraintBlock",
  "projection_layer":"normalized",
  "constraints":["a^2:b^2:c^2=1:2:3"]
}
```

---

## 7. Calculator IR

Calculator expressions lower directly into IR.

Example:

```text
Sqrt(xy)
```

becomes:

```json
{
  "kind":"FunctionCall",
  "name":"Sqrt",
  "args":[{"kind":"FusedProduct","symbol":"xy"}]
}
```

---

## 8. Execution contract

Execution order:

```text
IR -> Constraint Graph -> Solve -> StateTransition -> Kernel Audit -> Receipt -> Replay
```

Failure at any step aborts execution.

---

## 9. Determinism

IR must be:

```text
order-preserving
hash-stable
replayable
non-ambiguous
```

---

## 10. Compatibility

IR must be transpilable into:

```text
Python
C
Assembly
```

without losing:

```text
constraint structure
ordered products
receipt flow
```

---

## 11. Key rule

```text
No execution without IR
No IR without constraint graph
No constraint graph without global reconciliation
```

---

## 12. Summary

HARMONICODE IR is the bridge between:

```text
symbolic algebra
programming language
calculator
AI assistant
DAW engine
kernel execution
```

It enforces that all of them operate under the same audited, replayable, non-commutative constraint system.
