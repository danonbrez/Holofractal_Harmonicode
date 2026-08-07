# Pass 214 Iteration 2 — Callable Conformance and Compatibility Graph

Iteration 2 consumes the exact Iteration 1 repository census and creates one callable-conformance record for every discovered symbol. It does not import candidate modules or claim that static similarity proves runtime behavior.

## Implemented surfaces

- Python AST interface and normalized implementation binding.
- Balanced lexical declaration/body binding for JavaScript, TypeScript, C, C++, Rust, Go, shell, PowerShell, and SQL-discovered symbols.
- Direct-call dependency and behavioral-risk inventories.
- Active-callable, active-authority, duplicate-reference, non-active, and unresolved ownership classes.
- Exact normalized implementation equivalence groups.
- Divergent canonical, VM81, persistence, recovery, cache, learning, media, compiler/API, and accelerator authority candidates.
- Deterministic compatibility edges for static equivalence, interface compatibility, adapter requirements, unresolved interface divergence, and conflicting authority.
- Hash216 roots, Hash72 receipt, replay validation, tamper rejection, and retained artifacts.

## Safety and honesty boundary

`SEMANTICALLY_EQUIVALENT_STATIC_NORMAL_FORM` means that two symbols have identical Iteration 2 normalized implementation forms. It does not assert identical runtime effects, timing, external state, or observational behavior.

No authority-conflict candidate is automatically merged. Runtime-verified edge count remains zero until a later iteration supplies admissible oracle workloads and executes them through the inherited Pass 213 gates.

## Outputs

1. `callable_conformance_records.json`
2. `semantic_equivalence_groups.json`
3. `authority_conflicts.json`
4. `compatibility_edges.json`
5. `compatibility_graph.json`
6. `iteration2_summary.json`

## Next boundary

Iteration 3 resolves selected authority conflicts with dependency-scoped oracle workloads and implements only the adapters that preserve canonical identity, Pass 213 admission, and replay equality.
