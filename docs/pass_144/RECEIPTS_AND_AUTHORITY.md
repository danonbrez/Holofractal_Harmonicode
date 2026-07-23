# Receipts, Evidence, and Authority

## Evidence layers

- **A1 — Execution evidence:** actual inputs, outputs, diagnostics, receipts, persistence, replay artifacts.
- **A2 — External capability:** behavior demonstrated through a public interface.
- **A3 — Contract conformance:** comparison with an identified governing contract.
- **A4 — Formal proof:** proof checked by an identified formal system or equivalent authority.

No evidence is promoted implicitly across these layers.

## Receipt minimum

A useful receipt binds:

1. schema identity;
2. canonical input root;
3. operation identity;
4. ordered witness path;
5. output root;
6. dependency ancestry;
7. conclusion and authority level;
8. replay or reconstruction data;
9. receipt root.

## Interpretation independence

Evidence remains immutable. Interpretations may be versioned independently. Correcting an interpretation does not rewrite the observed execution.

## Cache and compression

A cache hit or successful decompression does not raise proof authority. Restored objects retain the authority they had before storage.
