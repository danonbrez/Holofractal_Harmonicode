# HHS PASS 190 ITERATION 3 — AUTHENTICATED FAIL-CLOSED AUTHORITY AMENDMENT

## Metadata

| Field | Value |
|---|---|
| Contract | `HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216` |
| Iteration | `3`, additive amendment |
| Baseline | `main @ c4757ed8c33604645961cc70275090f1c252fb9c` |
| Native/compiler classification inherited | `HHS_PASS_190_ITERATION_3_NATIVE_ABI_COMPILER_PARITY_FOUNDATION_VERIFIED` |
| Amendment classification | `HHS_PASS_190_ITERATION_3_AUTHENTICATED_FAIL_CLOSED_AUTHORITY_VERIFIED` |
| Full Pass 190 completion | Not claimed |

## Purpose

This amendment preserves the merged Iteration 3 native C ABI and CST → AST → HIR → VMIR compiler. It hardens the same remote operation authority rather than creating a parallel engine.

```text
canonical operation registry
→ exact compiler/native projection
→ singleton HHSAuthorityContext admission
→ Hash72/Hash216 receipt
→ fail-closed SQLite commit
→ verified event topology
→ authenticated HTTP/WebSocket/SDK/GUI projection
```

## Signed capabilities

Protected operations no longer accept client-authored scope strings. They require:

```text
Authorization: HHS-Capability <signed-token>
```

The bounded token preserves principal, sorted scopes, exact integer issue/expiry times, nonce, schema identity, and HMAC-SHA256 signature. The server verifies signature, lifetime, payload shape, and every operation-required scope before passing capabilities to the canonical context. `X-HHS-Capability` is rejected and stripped by nginx.

## Fail-closed persistence

The hardened store validates before restoring authority:

- complete `state`, `state_root`, `receipt_index`, and `last_hash72` metadata;
- sequential receipt indices and predecessors;
- `state_before → state_after` continuity;
- receipt Hash72 and Hash216 identities;
- final receipt state matching persisted state;
- chain head and receipt count;
- idempotency references.

Defaults are allowed only for an empty genesis database. Any partially populated authority database fails closed.

## Event integrity

Every persisted event receives a Hash72 identity over its sequence, type, and canonical payload. Admission events must exactly match the referenced receipt. Replay events must reference an existing receipt and preserve the operation identity. Integrity rejects event gaps, tampering, unsupported event types, duplicate admissions, unknown receipt references, or receipts without admission events.

Iteration 2 databases are migrated additively by deriving event identities and then validating the complete topology.

## Combined server

The Iteration 3 server continues to expose native/compiler surfaces:

```text
GET  /api/pass190/native-abi
POST /api/pass190/compile
POST /api/pass190/compile-execute
```

It also provides complete persistent authority discovery:

```text
GET  /api/pass190/health
GET  /api/pass190/operations
GET  /api/pass190/integrity
GET  /api/pass190/events
GET  /api/pass190/receipts
POST /api/pass190/invoke
POST /api/pass190/replay
WS   /api/pass190/ws
```

Persistence failures return structured HTTP 503 responses after inherited rollback. WebSocket cursors and handshake fields are validated before `101 Switching Protocols`.

## Visual authority

The visual operation fabric:

- uses a dedicated port-8190 Vite HTTP/WebSocket proxy or `VITE_PASS190_BASE_URL`;
- accepts signed tokens only;
- resumes from the last verified event sequence;
- reconnects with bounded exponential backoff;
- suppresses duplicate resumed events;
- displays persistent metadata and event-integrity status.

`RuntimeWindowManager` enforces every registry-declared singleton by restoring and focusing its existing window.

## Deployment

The installer validates and stages the complete native/compiler/hardening project at:

```text
/opt/hhs/pass190-operation-fabric
```

It generates a restricted capability secret when absent, atomically swaps the source tree, installs systemd and nginx assets, verifies health/integrity/native/OpenAPI surfaces, and restores the prior installation if closure fails.

## Validation gate

The combined gate includes:

- native C11 ABI build and executable test;
- Iteration 1, Iteration 2, native/compiler Iteration 3, and hardening regression tests;
- capability forgery, expiry, and scope tests;
- metadata and event tamper rejection;
- Iteration 2 database migration;
- structured persistence-failure tests;
- WebSocket pre-upgrade and coalesced-frame tests;
- registry-derived SDK parity;
- GUI reconnect/proxy/singleton verification;
- deployment source verification;
- no private `eval`/`exec` scan;
- native no-float authority scan.

## Remaining work

Full Pass 190 remains incomplete. Open work includes repository-wide operation hydration, complete Python compatibility, broader native ABI profiles, migration of all routes/actions/workflows, full compiler integration across legacy surfaces, distributed mutation arbitration, complete service registries, and live DigitalOcean production acceptance.
