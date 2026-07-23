# HHS_TYPED_IR_V1 — Pass 075 Contract

`HHS_TYPED_IR_V1` is the canonical, non-executing intermediate representation emitted by the Pass 075 language service.

Every IR preserves:

1. source spans and source-text commitments;
2. symbol identity and ordered-product distinctions;
3. exact type declarations;
4. effect declarations;
5. authority requirements for future effects;
6. required invariant bindings without assuming they are satisfied;
7. source-artifact lineage;
8. deterministic reconstruction recipes.

A validated IR can be committed only when its source is already a committed source artifact and the mutation request carries a valid role contract, task assignment, and capability lease.

The IR does not execute, self-authorize, prove invariant satisfaction, or replace an execution receipt.
