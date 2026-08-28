# HHS Pass 188 Versioned Content-License Lineage Runtime

This project closes the implementation gap in
`HHS-P188-VNFTCLL-LOSP-VM81-H72-H216`.

The implementation is additive to the already-verified Pass 188 Bott runtime. It
does not replace or modify `native_projects/hhs_pass188_bott_runtime`.

## Authority model

Every mutation requires an explicit nonzero 72-glyph inherited VM81-authority
witness. The runtime then appends one deterministic local Hash72 event under a
single SQLite `BEGIN IMMEDIATE` transaction. It does not create a second VM81
mutation path or Hash72 clock.

Wallet state, browser-local state, marketplace metadata, and blockchain/NFT
anchors are evidence only. They never authorize canonical mutation or egress.

Canonical arithmetic is integer/exact. Royalty terms are stored as normalized
numerator/denominator pairs. Floating-point canonical ingress is rejected.

## Implemented contract surfaces

- immutable content versions
- immutable license versions and exact deltas
- `LEGACY_BOUND`, `CURRENT_TERMS`, `OPT_IN_UPGRADE`,
  `COMPATIBILITY_FLOOR`, `REVOCABLE_CAPABILITY`, `FORKED_LICENSE`, and
  `SUNSET` policy support
- exact project/content/license bindings
- explicit binding upgrades with downstream Pass 187 graph impact closure
- controller transfer with stale-root rejection
- bounded delegation
- prospective revocation limited to rights declared revocable at admission
- expiry without historical receipt deletion
- typed obligations and exact royalty aggregation
- nested-license egress compatibility checks
- deterministic Hash72 event chain and ordered Hash216 evidence
- materialized-state integrity verification
- checkpoint, cold restart, and recovery
- offline external-anchor operation
- CLI and dependency-free HTTP API

## CLI

```sh
PYTHONPATH=. python -m hhs_runtime.pass188.license_lineage \
  --db /tmp/pass188.sqlite3 verify
```

The CLI exposes the contract operation names as hyphenated commands, including
`content-create`, `license-update`, `binding-upgrade`,
`ownership-transfer`, `revoke`, `impact`, `replay`, `verify`, and
`export-evidence`.

## HTTP

```sh
PYTHONPATH=. python -m hhs_runtime.pass188.license_server \
  --db /tmp/pass188.sqlite3 --host 127.0.0.1 --port 8187
```

Endpoints:

```text
GET  /api/pass188/license/health
GET  /api/pass188/license/verify
POST /api/pass188/license/execute
```

POST body:

```json
{
  "operation": "license-decision",
  "args": {
    "...": "..."
  }
}
```

## Validation

```sh
make validate
```

The focused suite executes all 16 normative Pass 188 license/legacy/transfer/
revocation acceptance scenarios, HTTP and CLI dispatch, no-float/zero-authority
negative tests, tamper checks, and cold-restart recovery.
