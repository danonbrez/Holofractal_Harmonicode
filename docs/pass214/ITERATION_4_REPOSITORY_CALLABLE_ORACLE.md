# Pass 214 Iteration 4 — Repository-Callable Oracle Execution

Iteration 4 crosses the boundary that Iteration 3 deliberately did not cross: selected repository callables are now imported and executed. The execution result is admissible only when the callable remains bound to the same tracked Git commit and tree, exact path, Git blob, top-level symbol, function source, normalized AST, Iteration 2 evidence, Iteration 3 lineage, and Pass 213 admission chain.

## Isolation membrane

Every source and target invocation runs in a fresh `python -I -S` interpreter. The child process receives only the repository root, manifested module and symbol, one canonical vector, and fixed limits. It applies:

- deterministic environment and disabled bytecode writes;
- CPU, address-space, descriptor, process and wall-clock ceilings;
- filesystem-write and mutation denial;
- socket and subprocess denial;
- native-library loading restricted to `hhs_runtime/builds`;
- bounded stdout and stderr capture;
- exact JSON-normalizable output with floating-point output forbidden.

The callable executes twice. A result is not usable unless both runs are canonically identical.

## Exact identity

The record binds:

1. source commit and source tree;
2. repository-relative Python path and exact module mapping;
3. tracked Git blob identity and recomputed Git blob SHA-1;
4. file SHA-256;
5. top-level function source SHA-256;
6. normalized AST Hash216;
7. direct imports;
8. matching Iteration 2 callable records and pair evidence;
9. fixed Iteration 3 implementation and blob lineage;
10. chained Pass 213 admission evidence.

Only undecorated synchronous top-level functions are accepted in this iteration. Dynamic paths, class methods, async functions, generators, and arbitrary expression evaluation remain outside the authority.

## Outcomes

- `CALLABLE_EQUIVALENCE_VERIFIED`
- `CALLABLE_ADAPTER_EQUIVALENCE_VERIFIED`
- `CALLABLE_DIVERGENCE`
- `CALLABLE_INADMISSIBLE`
- `CALLABLE_EXECUTION_ERROR`

An equivalence result confirms behavior only for the exact callable identities and admitted vectors. It does not merge authority. A divergence retains both implementations and the conflict. A pair-scoped adapter is authorized only when every admitted vector is equal after that adapter.

## Selected exact-head workload

The hosted workflow generates a manifest for:

- `hhs_backend/runtime/hhs_agent_algorithm_identity_v1.py:self_test`
- `hhs_backend/runtime/hhs_agent_contribution_provenance_v1.py:self_test`

Both files currently have Git blob `ab698bcb745e0333e79116a71f06c9ebd6cc94c0` and delegate to the same inherited canonical self-test. The workflow builds the native C ABI before execution and preserves the complete Iterations 1–4 artifacts.

The hosted workload uses `PASS213_DEPENDENCY_SCOPED_VALIDATION_FIXTURE`. Its three roots are derived through the inherited Pass 213 Hash216 authority from the exact source commit and tree. This proves the admission and replay mechanism but does **not** claim a live RFC 3161 timestamp anchor, production moving-tensor state, or production native-dispatch receipt. Production promotion remains forbidden until a later iteration supplies `PASS213_LIVE_GOVERNED_SURFACE` evidence.

Pass 214 remains nonterminal. Pass 215 remains unauthorized.
