# DATAFLOW CONTAINMENT AUDIT — PASS 007

## Non-bypass rule

The release runtime now treats dataflow as sealed by default:

```text
No alternate ingress.
No alternate propagation.
No alternate egress.
```

Authorized data movement must be one of:

1. A Hash72 receipt-chain record emitted through a canonical authority surface.
2. A validated vector-cache record carrying a backing Hash72 state/receipt pair.

## New canonical gateway

`hhs_runtime/hhs_io_gateway_v1.py` is the v1 containment seam for data entering, moving through, or leaving the runtime.

It emits deterministic records with:

- `schema`
- `io_id`
- `direction`: `INGRESS`, `PROPAGATION`, or `EGRESS`
- `source`
- canonical `payload_hash72`
- payload projection
- runtime step
- authority audit
- unified ledger entry count
- unified ledger tip
- unified ledger hash

## Vector-cache rule

Vector records are not allowed to become a shadow authority surface.

`validate_vector_cache_write()` requires:

- non-empty cache key
- vector record
- backing `state_hash72`
- backing `receipt_hash72`
- successful invariant authority audit
- unified Hash72 ledger append

## Backend routes wrapped in Pass 007

Representative runtime/API paths now emit gateway records:

- `GET /api/runtime/state`
- `POST /api/runtime/step`
- `GET /api/runtime/services`
- `POST /api/runtime/services/dispatch`
- `GET /api/runtime/vector/latest`
- `GET /api/runtime/packet/latest`

## Remaining containment targets

The next passes should continue routing every remaining externalized path through the gateway:

- Websocket stream packets.
- Graph summary, hash lookup, replay, and prediction routes.
- Sandbox create/step routes.
- File ingestion and export paths.
- Semantic memory writes.
- Embedding/router writes.
- Runtime event bus emissions that influence downstream state.
- GUI command submissions.
- CLI helpers and diagnostic entry points.

## Release interpretation

Pass 007 does not claim that every repository path is sealed yet. It establishes the canonical gateway and proves representative API, service, and vector paths can be wrapped without changing kernel semantics.
