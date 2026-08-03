# Pass 205 Repair-Forward Restart Record

## Identity

- Contract: `HHS-P205-VM5184-G243-DETERMINISTIC-MULTIMODAL-CONTINUATION-GAMING-ML-H72-H216`
- Repair base: `1de3d5e1a62c89a238b7f47b7e7b47cb9644a768`
- Branch: `agent/pass205-production-runtime`
- Pull request: `#152`
- Merge target: `main`
- Policy: preserve the merged Pass 205 V1 compute/storage implementation and repair review gaps through additive governed projections.

## Committed tranches

1. `f5f7f8c5d99720748d2c9acba52b9f82bb1ba5eb` — native library freshness guard.
2. `eeb8bf8c8524ba1470acfa5dd2840480364027ea` — writable `/var/lib/hhs/pass205` deployment boundary.
3. `bb280b6fdfe668c52dfb20f0e3ecfd4ea1900a18` — singleton VM81 admission and reconstructive replay.
4. `905a18e0a99ec262ea90aa765cbf97c9fcbaea3d` — lossless uint64 HTTP transport and canonical retrieval ordering.
5. `10974bf6564b9157e09916974efe2d0382a9d1da` — trusted Pass 205 production workflow expansion.
6. `64a110e24a3d18ccc811083df411cf5e0f750fd3` — removal of the superseded temporary workflow.

## Implemented repair scope

- Reject stale prebuilt Pass 205 libraries when any required C source or header is newer or missing.
- Configure production continuation state under `/var/lib/hhs/pass205/continuation.sqlite3` through a service-owned systemd drop-in.
- Preserve V1 deterministic state, projection, learning, Hash216, and SQLite behavior as the compute/storage substrate.
- Require one successful singleton VM81 runtime authority audit and Hash72 commit before a new continuation can be persisted.
- Store VM81 admission evidence and the native continuation receipt witness atomically with each new governed snapshot.
- Reject LOCKED, QUARANTINED, REJECTED, HALTED, missing-audit, and malformed-receipt authority outcomes.
- Reconstruct replay state, projection, learning features, roots, lineage, and receipt witnesses from ordered stored deltas.
- Encode uint64 state words, learning features, and XOR masks as decimal strings at the HTTP boundary while retaining exact integer internals.
- Sort compatible and rejected vector candidates canonically before retrieval identity construction and persistence.
- Expose `GET /api/runtime/continuation/transport` and bind hosted Pass 205 routes to the governed singleton through deterministic API federation order.

## Changed files

- `hhs_python/runtime/__init__.py`
- `hhs_python/runtime/hhs_pass205_native_freshness_guard.py`
- `hhs_backend/runtime/hhs_pass205_governed_continuation_v2.py`
- `hhs_backend/runtime/hhs_pass205_retrieval_order_v1.py`
- `hhs_backend/api/a0_pass205_transport_bootstrap.py`
- `hhs_backend/api/a_pass205_governed_bootstrap.py`
- `deployment/digitalocean/pass205_state/install.sh`
- `deployment/digitalocean/pass205_state/README.md`
- `bin/post_compile`
- `.github/workflows/pass205-production-runtime.yml`
- four focused repair test modules.

## Validation gate

The trusted Pass 205 production workflow now runs:

- deployment shell syntax checks;
- Python compilation for all repair surfaces;
- canonical and Pass 205 native ABI builds;
- all focused repair tests;
- the inherited exhaustive Pass 205 production suite;
- inherited Pass 205 design and GPU-translation tests;
- hosted production validation and evidence generation;
- hosted public federation binding checks;
- inherited Pass 201–204 regression tests.

## Remaining work

1. Repair only dependency-scoped failures reported by PR #152 checks.
2. Confirm the hosted application exposes the governed singleton and lossless transport route.
3. Update this record with terminal workflow run and evidence artifact identities.
4. Mark PR #152 ready and merge only after the trusted Pass 205 workflow is green.
5. Verify authoritative `main` and DigitalOcean guarded deployment receipts.
6. Physical GPU execution remains a separate validation boundary and is not claimed by this repair.
