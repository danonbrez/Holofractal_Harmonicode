# Schema Requirements

## Runtime Event Schema

Runtime events projected to GUI/backend layers must preserve:

- `event_type`
- `timestamp_ns`
- optional sequence/authority/runtime/branch identifiers
- optional hash72 lineage fields
- `payload`

The frontend must not derive runtime truth from projected events. It may cache, visualize, and route only.

## GUI Runtime Metrics Schema

`RuntimeOS.getMetrics()` must expose a stable compatibility surface:

```ts
{
  initialized: boolean,
  destroyed: boolean,
  diagnosticsEnabled: boolean,
  mobileMode: boolean,
  uptimeMs: number,
  connected: boolean,
  replayReady: boolean,
  graphReady: boolean,
  transportReady: boolean,
  totalEvents: number,
  workspaceWindows: number,
  applicationsMounted: number,
  registry: object,
  store: object,
  sockets: object,
  windows: object
}
```

## Window Projection Schema

GUI windows are projection objects only:

```ts
{
  id: string,
  title: string,
  applicationId: string,
  width: number,
  height: number,
  x: number,
  y: number,
  minimized?: boolean,
  maximized?: boolean,
  focused?: boolean,
  mobileFullscreen?: boolean,
  created_at_ns?: number
}
```

## Project State Schema

Root `PROJECT_STATE.json` must remain machine-readable and include:

- project name
- release stage
- current pass
- baseline artifact
- canonical objective
- authority layer mapping
- verified commands
- latest verified results
- known open items
- next pass recommendation

## Pass 004 Runtime Authority Schema

All production runtime execution packets that mutate or advance state must include:

```json
{
  "runtime": {"step": 1, "state_hash72": "<72 chars>", "receipt_hash72": "<72 chars>"},
  "receipt": {"step": 1, "state_hash72": "<72 chars>", "receipt_hash72": "<72 chars>"},
  "authority_audit": {
    "ok": true,
    "delta_e": 0,
    "psi": 0,
    "theta15": true,
    "omega": true,
    "hash72_state_ok": true,
    "hash72_receipt_ok": true,
    "algebraic_closure": true,
    "reasons": []
  }
}
```

Production paths must not consume or emit a mutating runtime packet lacking `authority_audit.ok == true`.

Diagnostic-only paths may inspect lower-level runtime state, but must be labeled diagnostic and must not be exposed as user-facing execution surfaces.


## Pass 010 — Persistence Guard Schema

All runtime-readable, database-like, or user-exportable persistence operations must be wrapped by the canonical IO gateway. Direct file/database writes are not an authority surface.

Required result schemas:

- `HHS_PERSISTENCE_WRITE_JSON_RESULT_V1` for JSON artifact writes.
- `HHS_PERSISTENCE_READ_JSON_RESULT_V1` for JSON artifact reads that may influence runtime behavior.
- `HHS_PERSISTENCE_EXPORT_TEXT_RESULT_V1` for text exports.
- `HHS_PERSISTENCE_PROPAGATION_RESULT_V1` for generic database/file persistence propagation.
- `HHS_PERSISTENCE_GUARD_SELF_TEST_V1` for the persistence containment self-test.

Each persistence result must include a 72-symbol `payload_hash72` and an IO receipt projection (`io_ingress_record`, `io_propagation_record`, or `io_egress_record`).

---

## Pass 011 Addition — Canonical Runtime Contract

All guarded runtime surfaces must converge on `HHS_CANONICAL_RUNTIME_CONTRACT_V1`.

Required contract object families:

- `HHS_EXECUTION_REQUEST_CONTRACT_V1`
- `HHS_RUNTIME_PACKET_CONTRACT_V1`
- `HHS_RECEIPT_CONTRACT_V1`
- `HHS_SERVICE_DESCRIPTOR_CONTRACT_V1`
- `HHS_EVENT_CONTRACT_V1`
- `HHS_VECTOR_CACHE_ENTRY_CONTRACT_V1`
- `HHS_PERSISTENCE_RECORD_CONTRACT_V1`
- `HHS_AUTHORITY_AUDIT_CONTRACT_V1`

Rules:

1. Runtime input must be representable as an execution request or runtime packet.
2. Runtime propagation must carry either IO receipt lineage or validated vector-cache backing receipt lineage.
3. Runtime services must expose canonical service descriptor contracts.
4. Service dispatch must emit an execution request contract and runtime packet contract.
5. Receipts, vectors, persistence records, and events must use native 72-symbol Hash72 fields where Hash72 lineage is required.
6. Legacy schemas may remain temporarily only when adapted into the canonical contract.
7. No GUI/API/plugin/frontend object may become authoritative unless it is wrapped by a canonical contract and committed through the existing authority chain.
