# HHS Acceptance Gate

## Purpose

Reject any state that violates system invariants.

## Pipeline

1. Forbidden path scan
2. Dependency audit
3. Manifest validation
4. Runtime validation
5. Execution tests
6. Artifact absorption
7. Ledger verification
8. Git binding

## Failure Conditions

- Missing dependencies
- Manifest mismatch
- Execution failure
- Ledger inconsistency

## Output

ACCEPTED or CommitAcceptanceError
