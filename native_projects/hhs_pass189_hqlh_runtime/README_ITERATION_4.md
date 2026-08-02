# Pass 189 Iteration 4

Iteration 4 adds authenticated driver manifests, payload-bound quarantine, conformance evidence, dual promotion, revocation, and rollback.

```bash
PYTHONPATH=python python3 -m unittest -v python/test_hhs_pass189_iteration4.py
PYTHONPATH=python python3 tools/hhs_pass189_iteration4_surface_smoke.py
```

Run locally:

```bash
HHS189_I4_DB=/tmp/pass189-i4.sqlite3 \
HHS189_I4_QUARANTINE=/tmp/pass189-i4-quarantine \
python3 server/hhs_pass189_iteration4_server.py --host 127.0.0.1 --port 8192
```

Open `/pass189/i4/`.

Real hardware packages can only become non-executable candidates. Iteration 4 never loads a physical driver.
