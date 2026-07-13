# Pass 048 — Authorized Live Mutation Execution + Reversible State Receipts

Pass 048 promotes a conservative allow-list of GUI-requested operations from `RECEIPT_ONLY` into `AUTHORIZED_MUTATION`.

The GUI remains request-only.  A browser event is never runtime truth.  Every authorized mutation must pass through the existing Pass 047 command envelope, zero-bypass interposition, kernel-derived composition/conformance, runtime admissibility enforcement, pre-state identity, transformation identity, post-state identity, reversible receipt, and WebSocket projection feedback.

## Allow-listed live mutations

- `runtime.tick`
- `runtime.pause`
- `runtime.resume`
- `runtime.request_status_snapshot`
- `semantic_cache.refresh_composition_index`
- `expanded_state_decay.sweep`

## Hard invariant

```text
NO UI EVENT
  -> directly becomes runtime truth.

EVERY MUTATION
  -> admissible command identity
  -> kernel-derived authority path
  -> pre-state identity
  -> transformation identity
  -> post-state identity
  -> mutation receipt
  -> projected feedback.
```

## Result

Pass 048 closes the first live mutation loop without granting the GUI execution authority.  The GUI requests; FastAPI enforces; the kernel-derived runtime path decides; the mutation executor emits a reversible receipt; WebSocket feedback drives the projected GUI state.
