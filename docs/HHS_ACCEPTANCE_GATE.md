# HHS Acceptance Gate

## 1. Definition

The HHS Acceptance Gate is the deterministic enforcement layer that decides whether a repository state may transition into an accepted state.

No commit is valid unless it passes the acceptance gate.

---

## 2. Execution Pipeline

The gate enforces a strict ordered pipeline:

```text
Scan → Dependencies → Manifest → Runtime → Execution → Ledger → Git Binding → ACCEPT
```

Each stage must succeed before the next stage is evaluated.

---

## 3. Stage Definitions

### 3.1 Forbidden Path Scan

Searches all Python files for disallowed environment-bound paths.

Failure condition:

```text
forbidden path detected → reject
```

---

### 3.2 Dependency Audit

Ensures required directories and runtime paths exist.

Failure condition:

```text
missing dependency → reject
```

---

### 3.3 Immutable Manifest Validation

Verifies that protected files match their stored Hash72 digests.

If a mismatch occurs, validation requires:

- an upgrade receipt
- correct Hash72 digest
- valid signature

Failure conditions:

```text
mismatch without receipt → reject
invalid signature → reject
missing manifest → reject
```

---

### 3.4 Runtime Validation

Ensures symbolic language integrity and grammar coherence.

Failure condition:

```text
status != ACCEPTED → reject
```

---

### 3.5 Execution Stage

Runs certification and runtime scripts.

Failure condition:

```text
any script fails → reject
```

---

### 3.6 Artifact Absorption

All runtime JSON artifacts are ingested into the unified ledger.

Failure condition:

```text
ledger ingestion fails → reject
```

---

### 3.7 Unified Ledger Verification

Validates:

- hash chain integrity
- entry consistency
- ledger tip

Failure condition:

```text
ledger mismatch → reject
```

---

### 3.8 Git Binding

Binds repository state to ledger state using Hash72.

Failure condition:

```text
binding fails → reject
```

---

## 4. Acceptance Condition

A state is accepted only when all stages succeed.

Output:

```text
ACCEPTED
```

---

## 5. Failure Behavior

The gate is fail-closed.

Failure produces:

```text
CommitAcceptanceError
```

No partial state is committed.

---

## 6. Determinism

For a given repository state, the acceptance gate must produce identical results across all executions.

---

## 7. CI and Consensus

The gate is executed across multiple nodes in CI.

Acceptance requires unanimous agreement.

---

## 8. System Role

The acceptance gate is the boundary between unverified state and accepted state.

No state transition bypasses this layer.
