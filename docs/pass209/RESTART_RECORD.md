# Pass 209 Runtime Bootstrap Cache — Restart Record

- Base branch: `main`
- Target: `main`
- Scope: production bootstrap latency, direct status caching, and writable state-root closure
- Canonical application remains: `hhs_backend.visual_server:app`
- Production entrypoint becomes: `hhs_backend.production_visual_server:app`

## Implemented

- Persistent stale-while-revalidate cache for runtime status projections.
- Isolated sequential status probe process so repository scans do not block the serving event loop.
- Immediate warming responses for cold cache misses.
- Browser fetch coordinator that redirects import-time runtime status calls through the cache.
- Direct status-route interception for the known expensive Pass 196-201 status catalog.
- Corrected deployed route names for calibration-registry and Pass 200A/200B/200C status surfaces.
- Event-driven `hhs:browser:ready` synchronization with a 120-second bounded fallback.
- Aggregate `/api/runtime/bootstrap/status` diagnostics.
- External writable state roots for graphics hydration and Pass 196-200C, Pass 204, and Pass 205 persistence.
- External data, runtime-output, and filesystem-ledger roots so production writes do not mutate the Git checkout.
- Dependency-scoped tests for cache persistence, HTML injection, proxy behavior, direct status interception, and production status-catalog identity.

## Production status catalog

```text
/api/runtime/authority/status
/api/runtime/integration/status
/api/runtime/calibration/status
/api/runtime/calibration-registry/status
/api/runtime/distributed-calibration/status
/api/runtime/optimization-authority/status
/api/runtime/optimization-canary/status
/api/runtime/optimization-active/status
/api/public/status
```

## Validation commands

```bash
python -m py_compile \
  hhs_backend/runtime_bootstrap_cache.py \
  hhs_backend/runtime_status_probe.py \
  hhs_backend/cached_visual_server.py \
  hhs_backend/production_visual_server.py
python -m pytest -q \
  tests/test_runtime_bootstrap_gateway.py \
  tests/test_production_visual_server.py
```

## Deployment verification

```bash
sudo systemctl daemon-reload
sudo systemctl restart hhs.service
curl -fsS http://127.0.0.1:8080/api/system/status | python3 -m json.tool
curl -fsS http://127.0.0.1:8080/api/runtime/bootstrap/status | python3 -m json.tool
curl -fsSI http://127.0.0.1:8080/ | grep -i x-hhs-runtime-bootstrap
```

## Remaining independent gate

The assistant provider remains a separate server-side configuration task. The current hierarchy exposes Gemma 4 and the native language provider, but neither becomes selected until its own readiness requirements are satisfied.
