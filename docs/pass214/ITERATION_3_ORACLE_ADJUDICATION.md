# Pass 214 Iteration 3 — Admitted Oracle Models and Adapter Proofs

Iteration 3 adds the first executable oracle layer above the frozen Iteration 2 compatibility graph. It is deliberately narrower than repository-callable equivalence: the runtime executes only explicitly registered, pure handlers and records their behavior as a **non-promoting oracle model** bound to exact Iteration 2 symbol and implementation roots.

## Implemented authority

Each manifested workload must:

1. reference a symbol pair already present in an Iteration 2 compatibility edge or authority-conflict group;
2. bind both symbol identities and their Iteration 2 implementation roots to explicit handler specifications;
3. carry a Pass 213 admission receipt bound to the workload input root, trusted timestamp anchor root, moving-tensor root, native-dispatch receipt root, and prior admission root;
4. execute only a handler from the fixed pure registry;
5. produce deterministic per-vector, oracle-record, model-adjudication, adapter-proof, compatibility-edge, semantic, and Hash72 receipt roots.

The fixed handlers cover identity, canonical round-trip, positional-to-named conversion, key renaming, field projection, canonical-byte envelopes, and canonical SHA-256 projection. No arbitrary dynamic import, expression evaluation, network access, filesystem mutation, subprocess launch, time source, or randomness is available through the registry.

## Adapter evidence

An adapter proof is emitted only when every admitted vector produces the same canonical output identity after the target adapter. The proof binds source and target symbol roots, model-binding roots, adapter configuration, complete input root, ordered output roots, the Pass 213 admission receipt root, deterministic replay equality, and an explicit prohibition on authority promotion.

Supported adapter classes are `IDENTITY`, `POSITIONAL_TO_NAMED`, `KEY_RENAME`, `FIELD_PROJECTION`, and `CANONICAL_BYTES_ENVELOPE`.

## Honesty boundary

Iteration 3 does not assert that a built-in handler is semantically identical to the repository callable whose symbol it models. Every binding records:

```text
semantic_fidelity_to_repository_callable_claimed = false
repository_callable_executed = false
repository_authority_change_authorized = false
```

A divergent model therefore requires a callable oracle before quarantine; an equivalent model requires callable evidence before fallback designation or adapter integration. No authority is merged, replaced, promoted, or removed.

## Next boundary

The next iteration must introduce safe, exact repository-callable oracle bindings and dependency-scoped execution fixtures. Only callable-backed evidence may adjudicate repository authority conflicts or authorize an adapter for integration.
