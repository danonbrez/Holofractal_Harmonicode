# NEXT PASS 019 — SRCG Global Constraint Propagation Fabric

## Goal
Extend SRCG from a primitive A/B gate into a multi-gate GCP engine that parses symbolic instruction sets and fires over every equality relation under the same authority chain.

## Priority tasks
1. Add an SRCG instruction parser that identifies equality relations without semantic flattening.
2. Represent each equality as a gate branch with A/B witnesses.
3. Execute branches as a fabric transaction with all-or-nothing rollback.
4. Attach one Hash72/u^72 witness per branch plus a fabric-level witness.
5. Add service/API surface for submitting SRCG programs.
6. Add tests for multi-branch rollback and last-known-closure preservation.
