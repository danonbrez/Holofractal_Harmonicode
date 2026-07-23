# HHS Native Development Protocol — Pass 074

## Purpose

The HHS repository is a general repository-networking protocol for software development acceleration, alignment enforcement, testing, iteration, bounded self-healing, and collaboration among human, LLM, tool, and CI agents.

The repository, not a conversation window, is the authoritative development state.

## Reciprocal admission constraints

A future change is admissible only when both conditions hold:

1. **Foundation conservation:** no Pass 072 foundation mutation occurs without a justified, minimal, witnessed, reversible alignment patch and independent verification.
2. **Capability-bearing product closure:** no new orphan module is introduced; every new module belongs to a reachable, reusable, Runtime-governed program that adds a verified capability.

```text
ADMIT(change)
=
FOUNDATION_CONSTRAINT(change)
∧
CAPABILITY_CONSTRAINT(change)
```

## Agent-network invariant

```text
AGENT REGISTRATION ≠ AUTHORITY
PROPOSAL ≠ MUTATION
TEST EVIDENCE ≠ ADMISSION
HANDOFF ≠ AUTHORITY TRANSFER
REPAIR PLAN ≠ REPAIR APPLICATION
LLM OUTPUT ≠ CANONICAL REPOSITORY STATE
```

All agents exchange canonical repository objects through the unified Runtime API. Conversation context may assist an agent but may not be required to reconstruct project identity, state, tests, decisions, or continuation.

## Self-healing progression

- Pass 074: alignment decisions, test evidence, handoff capsules, bounded repair planning.
- Pass 075: typed Harmonicode IR and agent-coordinated test acceleration.
- Pass 076+: interpreter-backed reproduction and bounded repair execution with receipts and rollback.

The development graph remains open-ended while the reciprocal constraints remain true.
