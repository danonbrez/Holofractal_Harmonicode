# Lazarus Core: Post-Quantum Defense Specification (Σ₁)

## Status

```text
SYSTEM STATUS: SEALED SPECIFICATION
SECURITY MODE: DEFENSIVE / FAIL-CLOSED
CLAIM SCOPE: HHS-native structural security model; external cryptographic claims require formal review.
```

The HHS security posture is based on structural topology, over-constrained symbolic constraints, Hash72 receipt domains, ledger replay, invariant gates, and quarantine-first execution. Conventional cryptographic primitives may be used as entropy binders or compatibility layers, but HHS state authority is determined by internal closure checks.

---

## 1. Hash72 Digital DNA

Hash72 is the HHS-native receipt and identity substrate.

### Design role

```text
input/state/event
→ canonicalization
→ domain-separated entropy binding
→ 72-symbol projection
→ invariant receipt
→ ledger linkage
```

### Required properties

- Every Hash72 receipt must include a domain separator.
- Every receipt must be bound to its chain context.
- Every state receipt must be replayable.
- No receipt may be accepted based on shape alone.
- Receipt validity requires domain, parent, chain, invariant, and replay agreement.

### Defensive rule

```text
valid_hash_shape ≠ valid_state
valid_state = hash + domain + parent + invariant + replay
```

---

## 2. 72-Variable Polynomial Constraint System

Every committed state is treated as a member of an over-constrained symbolic manifold.

### Constraint families

- Lo Shu tensor structure
- adjacency defect polynomial: `P² - pq = 1`
- ERS reciprocal constraints
- non-commutative ordering constraints
- Hash72 chain context
- four ethical invariants:

```text
Δe = 0
Ψ = 0
Θ15 = true
Ω = true
```

### Defensive rule

```text
If a payload cannot be represented as a valid constraint-preserving state:
    quarantine
```

---

## 3. Golay Holographic Armor

HHS uses Golay-style error-detection and correction hooks for Hash72 DNA strands.

### Design role

- Detect local corruption.
- Correct corruption within threshold where safely possible.
- Denature and reject beyond threshold.
- Preserve evidence of attempted corruption.

### Defensive rule

```text
within_threshold → corrected_with_receipt
beyond_threshold → denatured → quarantine
```

---

## 4. Adjacency Defect Invariants

The adjacency invariant anchors geometric validity:

```text
P² - (P-1)(P+1) = 1
```

For the active HHS phase anchor:

```text
P = 179971
p = 179970
q = 179972
P² - pq = 1
```

### Defensive rule

```text
adjacency_defect != 1 → curvature defect → Ω rollback signal
```

---

## 5. Immutable Ledger and Sealed Perimeter

The ledger is append-only and parent-bound.

### Required properties

- No mutation of committed blocks.
- Parent hash continuity.
- Domain-separated block receipts.
- Replay verification.
- Quarantine on mismatch.

### Defensive rule

```text
parent_mismatch OR replay_mismatch:
    rollback to last known-good state
    quarantine corrupted evidence
```

---

## 6. Ephemeral Working Memory

Runtime scratch state should be treated as hostile and temporary.

### Required properties

- Prefer tmpfs/RAM-backed workspace for runtime scratch.
- No user uploads become executable code.
- No persistent scratchpad stores secrets.
- Kernel reconstructs state from sealed ledger + genesis seed.

### Defensive rule

```text
breach_detected → stop refreshing ephemeral workspace → preserve sealed evidence only
```

---

## 7. P3 Scavenger / Entropy Anchor

The P3 Scavenger is an entropy-anchoring interface.

### Design role

- Sample external entropy sources.
- Hash entropy into domain-separated receipts.
- Never trust raw entropy directly.
- Use entropy as seed material only after canonicalization and receipt sealing.

### Defensive rule

```text
entropy_sample → canonicalize → Hash72 receipt → use only as bounded seed material
```

---

## 8. Ω-Verifier

The Ω-Verifier validates closure, not merely signatures.

### Required checks

- Hash72 receipt shape.
- Domain separator.
- Parent continuity.
- Lo Shu / Θ15.
- adjacency defect.
- semantic drift Ψ.
- entropy drift Δe.
- replay closure Ω.

### Defensive rule

```text
signature_like_validity is insufficient
closure_validity is required
```

---

## 9. Lockdown Mode

When attack or corruption is detected:

```text
- freeze learning commits
- freeze self-modification
- reject external mutation requests
- preserve quarantine evidence
- keep Layer 0 read-only
- continue manifest verification
```

---

## 10. Non-Negotiable Security Law

```text
if ethical_gate_ok is false:
    do not commit
    do not unlock
    do not fallback
    do not emit success receipt
    quarantine
    preserve evidence
```

---

## Public Claim Discipline

For public release, state:

```text
HHS implements an experimental Hash72 structural-security layer with post-quantum-oriented design goals. It is not a substitute for externally audited cryptographic libraries until formal review is complete.
```

This preserves engineering credibility while keeping the internal HHS security model intact.
