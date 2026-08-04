# Pass 209 Runtime Bootstrap Cache — Restart Record

- Base branch: `main`
- Target: `main`
- Scope: production bootstrap latency and status-fanout correction
- Canonical application remains: `hhs_backend.visual_server:app`
- Production entrypoint becomes: `hhs_backend.cached_visual_server:app`

## Implemented

- Persistent stale-while-revalidate cache for runtime status projections.
- Isolated sequential status probe process so repository scans do not block the serving event loop.
- Immediate warming responses for cold cache misses.
- Browser fetch coordinator that redirects import-time runtime status calls through the cache.
- Event-driven `hhs:browser:ready` synchronization with a 120-second bounded fallback.
- Aggregate `/api/runtime/bootstrap/status` diagnostics.
- Dependency-scoped unit tests for cache persistence, HTML injection, proxy behavior, and source transformation.

## Validation commands

```bash
python -m py_compile \
  hhs_backend/runtime_bootstrap_cache.py \
  hhs_backend/runtime_status_probe.py \
  hhs_backend/cached_visual_server.py
pytest -q tests/test_runtime_bootstrap_gateway.py
```

## Deployment verification remaining

```bash
sudo systemctl daemon-reload
sudo systemctl restart hhs.service
curl -fsS http://127.0.0.1:8080/api/runtime/bootstrap/status | python3 -m json.tool
curl -fsSI http://127.0.0.1:8080/ | grep -i x-hhs-runtime-bootstrap
```

The assistant provider remains an independent server-side configuration gate.
