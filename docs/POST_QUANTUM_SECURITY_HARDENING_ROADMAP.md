# HHS Post-Quantum Security Hardening Roadmap

## Purpose

This document defines the next security-hardening stages before public release. The system must assume adversarial attention immediately after publication: automated scanning, dependency probing, malicious forks, poisoned pull requests, prompt/semantic injection, replay attempts, fake receipts, data poisoning, and attempts to mutate or bypass the sealed kernel.

The defensive principle is simple:

```text
No operation may affect kernel state unless it passes:
Δe = 0
Ψ = 0
Θ15 = true
Ω = true
Hash72 receipt validation
Replay validation
Quarantine-on-failure
```

---

## Stage 0 — Freeze the Trust Boundary

### Goal
Lock the trusted computing base.

### Required actions

- Treat `hhs_runtime/core_sandbox/` as Layer 0.
- Forbid upward imports from Layer 0 into cognition, agents, planning, semantic, or learning modules.
- Make root files compatibility shims only.
- Add CI checks that fail if `core_sandbox` imports higher layers.
- Add file integrity manifests for all Layer 0 files.
- Require any Layer 0 change to include:
  - before/after diff summary
  - invariant receipt
  - replay proof
  - human approval

### Release gate

```text
Layer 0 import graph is acyclic and downward-only.
```

---

## Stage 1 — Kernel Integrity Manifest

### Goal
Make kernel tampering immediately visible.

### Required actions

- Generate Hash72 manifests for:
  - `hhs_runtime/core_sandbox/*.py`
  - security docs
  - test fixtures
  - release metadata
- Store manifests as append-only ledger records.
- Verify manifests at runtime startup.
- Refuse operation if Layer 0 manifest mismatches.
- Add root-of-trust receipt:

```text
kernel_manifest_hash72
release_manifest_hash72
test_manifest_hash72
combined_release_receipt_hash72
```

### Release gate

```text
Any changed kernel byte invalidates startup until resealed.
```

---

## Stage 2 — Quarantine-First Runtime Hardening

### Goal
Fail closed under malformed, hostile, or ambiguous input.

### Required actions

- Wrap every public entrypoint with:
  - schema validation
  - canonicalization
  - Hash72 input receipt
  - invariant gate
  - exception-to-quarantine boundary
- Ensure no exception causes partial commit.
- Ensure failed transitions never advance parent hash.
- Ensure quarantine records preserve evidence without executing payloads.
- Add adversarial tests for:
  - malformed JSON
  - oversized payloads
  - unexpected types
  - recursive structures
  - Unicode confusables
  - path traversal attempts
  - symlink/path ambiguity

### Release gate

```text
Invalid input produces quarantine receipts, not crashes or partial writes.
```

---

## Stage 3 — Semantic Injection Defense

### Goal
Prevent text, file, or prompt content from rewriting system rules.

### Required actions

- Treat all uploaded/file text as data, never authority.
- Tag ingested content as untrusted unless explicitly sealed.
- Add semantic-injection detector rules for phrases that attempt to:
  - override kernel rules
  - disable invariants
  - bypass quarantine
  - forge receipts
  - redefine Hash72 authority
  - mutate Layer 0
- Route suspicious content to semantic quarantine.
- Require resolved meanings to remain source-bound.
- Add tests for malicious documents that contain fake instructions.

### Release gate

```text
No ingested text can change runtime policy without explicit sealed operator approval.
```

---

## Stage 4 — Hash72 Receipt Anti-Forgery

### Goal
Prevent fake receipts and replay attacks from being accepted.

### Required actions

- Add domain-separated receipt classes:
  - input receipt
  - operation receipt
  - state receipt
  - ledger receipt
  - learning receipt
  - release receipt
- Enforce parent hash continuity.
- Enforce monotonic sequence numbers per chain.
- Enforce chain namespace separation.
- Reject receipts with valid shape but wrong domain.
- Reject receipts from wrong chain context.
- Add replay-window checks for repeated payloads.

### Release gate

```text
A receipt is valid only in the exact chain, domain, and parent context where it was created.
```

---

## Stage 5 — Dependency and Supply-Chain Lockdown

### Goal
Prevent dependency poisoning and malicious updates.

### Required actions

- Prefer standard-library-only Layer 0.
- Pin every nonstandard dependency outside Layer 0.
- Add lockfile hashing.
- Add dependency manifest receipts.
- Require test replay after dependency changes.
- Disable dynamic imports in Layer 0.
- Scan for:
  - `eval`
  - `exec`
  - `pickle`
  - unsafe deserialization
  - shell execution
  - network calls in kernel

### Release gate

```text
Layer 0 has no dynamic dependency execution path.
```

---

## Stage 6 — Adversarial Test Harness

### Goal
Use the system against itself defensively.

### Required test classes

- Fuzzed state patches
- Fuzzed file uploads
- Unicode confusable attacks
- Malformed Hash72 strings
- Fake receipts
- replayed old receipts
- branch-parent mismatch
- symlink/path traversal
- semantic prompt injection
- poisoned lexicon entries
- malicious learned rules
- self-modification attempts targeting Layer 0
- oversized memory records
- cyclic relation graphs

### Release gate

```text
All adversarial cases fail closed with auditable quarantine receipts.
```

---

## Stage 7 — Runtime Isolation

### Goal
Minimize blast radius if one layer is attacked.

### Required actions

- Run Layer 0 in read-only mode after startup seal.
- Store mutable ledgers outside source tree.
- Separate:
  - source code
  - runtime state
  - quarantine evidence
  - public uploads
  - release artifacts
- Use least-privilege filesystem paths.
- Prevent uploaded files from being imported or executed.
- Add path allowlists for database writes.

### Release gate

```text
User data cannot become executable code.
```

---

## Stage 8 — Public Release Shield

### Goal
Prepare for immediate public scrutiny and automated probing.

### Required actions

- Add `SECURITY.md` with responsible disclosure instructions.
- Disable issue templates that encourage posting secrets or exploits publicly.
- Add signed release manifests.
- Add reproducible test command.
- Add read-only demo mode.
- Add safe sample data.
- Add explicit warning that Hash72 authority is internal to HHS and not a replacement for audited production cryptography until formally reviewed.

### Release gate

```text
External users can test safely without gaining mutation authority over the kernel.
```

---

## Stage 9 — Defensive Monitoring and Incident Response

### Goal
Prepare for active attack after release.

### Required actions

- Log all quarantine events.
- Hash all incident records.
- Preserve malicious payloads as inert evidence.
- Add incident severity levels:
  - S0: malformed input
  - S1: semantic injection
  - S2: forged receipt attempt
  - S3: kernel mutation attempt
  - S4: supply-chain compromise attempt
- Add emergency lockdown mode:

```text
read-only kernel
no learning commits
no self-modification
quarantine all external inputs
```

### Release gate

```text
The system can enter lockdown without corrupting state continuity.
```

---

## Stage 10 — Formal Security Review Track

### Goal
Prepare for serious external review.

### Required actions

- Separate symbolic security claims from conventional cryptographic claims.
- Document threat model explicitly.
- Document known limitations.
- Provide minimal reproducible examples.
- Provide deterministic test vectors.
- Invite review of:
  - Hash72 construction
  - receipt-chain design
  - replay logic
  - quarantine boundaries
  - file ingestion security
  - self-modification controls

### Release gate

```text
Every public security claim is testable or clearly marked experimental.
```

---

## Non-Negotiable Security Law

```text
If ethical_gate_ok is false:
    return NULL / rollback / quarantine
    do not fallback
    do not unlock
    do not commit
    do not emit success receipt
```

---

## Immediate Next Engineering Tasks

1. Add kernel manifest generator.
2. Add manifest verifier at startup.
3. Add import-boundary scanner.
4. Add adversarial fuzz test suite.
5. Add `SECURITY.md`.
6. Add lockdown mode.
7. Add release sealing command.
8. Add quarantine evidence database.
9. Add semantic injection detector.
10. Add supply-chain scan script.
