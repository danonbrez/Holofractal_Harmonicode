# KNOWN ISSUES — PASS 011

## Still open
- GUI TypeScript build still requires Node dependencies not bundled in the ZIP.
- Frontend runtime shell/command palette must be adapted to consume canonical service descriptor and packet contracts.
- Event/replay/snapshot modules still need deeper migration from local schemas into the canonical runtime contract.
- Persistence guard self-test output is large because it prints ledger verification data; future pass should add compact CLI output mode.
- Existing C warnings remain non-blocking but should be cleaned before release candidate.

## Not changed in this pass
- Kernel math/invariant semantics.
- Hash72 alphabet/meaning.
- C runtime ABI.
- GUI dependencies or package manager lockfiles.
