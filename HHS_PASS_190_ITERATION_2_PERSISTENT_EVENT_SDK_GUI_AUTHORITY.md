# HHS PASS 190 ITERATION 2 — PERSISTENT RECEIPT, EVENT, SDK, GUI, AND WORKFLOW AUTHORITY

## 1. Metadata

| Field | Value |
|---|---|
| Contract | `HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216` |
| Iteration | `2` |
| Implementation | `HHS-P190-I2-PRES-WS-SDK-GUI-1.0.0` |
| Baseline | `main @ f268a4d538e609685e5f1d9f19e41511b7a808cd` |
| Classification | `HHS_PASS_190_ITERATION_2_PERSISTENT_EVENT_SDK_GUI_FOUNDATION_VERIFIED` |
| Full Pass 190 completion | Not claimed |

## 2. Purpose

Iteration 2 extends the validated iteration 1 operation nucleus without creating a second semantic engine. The existing `HHSAuthorityContext`, canonical operation registry, implementations, Hash72 receipts, Hash216 identities, capability gates, state-conflict rules, and replay logic remain authoritative.

The new layer adds durable process restart, resumable event transport, generated clients, visible operation control, and workflow bindings around that same authority path.

```text
canonical operation registry
→ iteration 1 semantic implementation
→ singleton admitted transition
→ atomic SQLite receipt/state commit
→ resumable event sequence
→ HTTP/WebSocket/SDK/GUI/workflow projections
```

## 3. Persistent authority store

`SQLiteAuthorityStore` persists atomically:

- complete Hash72 and Hash216 receipts;
- receipt index and predecessor chain;
- canonical runtime state and state root;
- idempotency-key mappings;
- resumable operation and replay events.

Startup restoration verifies every receipt in order. It rejects:

- missing or duplicated receipt indices;
- predecessor discontinuity;
- Hash72 or Hash216 mismatch;
- invalid idempotency references;
- state-root mismatch;
- chain-head or receipt-count disagreement.

The in-memory authority is restored only after the stored chain validates. A failed database commit restores the pre-invocation in-memory state so uncommitted mutations cannot remain authoritative.

## 4. Resumable event authority

Every newly admitted receipt produces one persisted `operation.admitted` event. Replay produces a typed `operation.replayed` event without mutating the receipt chain.

Clients may resume by sequence through:

```text
GET /api/pass190/events?after=<sequence>&limit=<n>
WS  /api/pass190/ws?after=<sequence>
```

The WebSocket channel performs an RFC 6455 upgrade, emits a typed readiness frame, streams persisted events in sequence, and emits bounded heartbeat frames during inactivity.

## 5. Receipt and integrity surfaces

Iteration 2 adds:

```text
GET /api/pass190/integrity
GET /api/pass190/receipts?after=<receipt_index>&limit=<n>
GET /api/pass190/events?after=<sequence>&limit=<n>
GET /api/pass190/ws?after=<sequence>
```

The existing health, registry, invoke, replay, and OpenAPI surfaces remain available through the injected persistent authority context.

## 6. Generated SDKs

The canonical registry generates and validates:

- `sdk/python/hhs_pass190_client.py`;
- `sdk/typescript/hhsPass190Client.ts`.

Both clients expose:

- registry inspection;
- integrity inspection;
- invocation with capability, idempotency, and expected-state headers;
- receipt and event pagination;
- replay;
- operation-specific methods for every currently registered operation;
- WebSocket creation in the TypeScript client.

Generated files are rejected as stale when they differ from registry-derived output.

## 7. GUI and workflow bindings

The runtime application registry now exposes `pass190_operation_fabric` as a singleton, mobile-supported runtime window.

The window provides:

- operation selection from the live canonical registry;
- typed JSON argument entry;
- explicit capability entry;
- admitted result and receipt presentation;
- state root and chain-head inspection;
- live WebSocket receipt events;
- human-readable status rather than a raw-JSON-only surface.

`P190_OPERATION_SURFACE_BINDINGS_V1.json` gives every registered operation one deterministic GUI action identity, workflow-step identity, WebSocket channel, and generated SDK symbol. Its Hash216 identity binds the full surface map to the iteration 1 registry identity.

## 8. DigitalOcean deployment package

The additive deployment package supplies:

- a hardened `hhs-pass190.service` systemd unit;
- persistent database location `/var/lib/hhs/pass190-authority.sqlite3`;
- nginx HTTP and WebSocket routing;
- validation-before-install behavior;
- health and OpenAPI verification.

This package is repository-validated. A live DigitalOcean deployment is not claimed by this iteration.

## 9. Validation

The iteration 2 validation target runs iteration 1 regression tests plus six new tests covering:

- state and receipt restoration after process restart;
- idempotency preservation after restart;
- continued mutation from the restored state;
- receipt-chain and state-root integrity;
- tamper rejection;
- resumable admitted and replay events;
- receipt pagination;
- generated SDK parity;
- live HTTP integrity, events, receipts, invoke, and OpenAPI requests;
- RFC 6455 handshake and live WebSocket event delivery;
- GUI registration and endpoint binding;
- workflow binding generation;
- deployment configuration verification;
- Python bytecode compilation;
- private `eval(...)` and `exec(...)` rejection scan.

## 10. Remaining Pass 190 work

The following remain incomplete:

- repository-wide hydration of every public operation;
- complete Python built-in and standard-library parity;
- native C ABI generation and parity;
- full CST → AST → HIR → VMIR integration;
- migration of every existing API route, GUI action, and workflow to registry resolution;
- complete job, workspace, artifact, provider, and capability registries;
- multi-process distributed mutation arbitration;
- live DigitalOcean installation and production acceptance;
- full Pass 190 completion classification.

Iteration 2 is committed as a validated additive layer. It does not conceal or overstate the remaining Pass 190 surface.
