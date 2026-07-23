# Pass 078.1 — Native ABI Declaration Reconciliation

## Purpose

Reconcile the public `hhs_vm_*` declaration surface with actual frozen native implementation authority before executable IR depends on it.

## Governing rule

`matching name != semantic binding`

`matching signature != authority`

`operational resemblance != semantic equivalence`

## Result

All fifteen unresolved declarations are retained as typed unresolved. Each declaration has an individual `HHS_NATIVE_ABI_DECLARATION_DISPOSITION_V1` record with its declared signature, candidate native primitives, equivalence status, disposition, architectural revision requirement, callability status, rationale, evidence files, and Hash72 disposition root.

No wrapper was created because the public ABI state types and frozen VM81 implementation types are not proven equivalent. Creating such wrappers would constitute a versioned adapter architecture rather than declaration reconciliation.

## Continuation boundary

Pass 079 may bind executable IR only to capabilities whose ABI disposition is callable and whose semantic contract is proven. The fifteen retained declarations are excluded until a versioned architectural revision closes their representation and contract gaps.
