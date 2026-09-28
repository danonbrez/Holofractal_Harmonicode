# Standard frontend ingress repair — 2026-09-27

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main: `5671d7174db55be2bae62beeac40b720f4faa498`
- Branch: `agent/standard-frontend-ingress-repair-20260927`
- Merge target: `main`
- Scope: repair external browser/HTTP ingress compatibility without changing the native HHS runtime authority model.

## Trigger

PR #610 was merged to main first, as required. The next repair-forward audit checked the standard frontend compatibility membrane against the inherited Pass 170 public API contract.

The confirmed ingress deviation is explicit in the repository contract:

```text
Production CORS SHALL use an explicit origin allowlist.
allow_origins=["*"] + allow_credentials=True SHALL be prohibited.
```

The canonical backend still configured exactly that prohibited wildcard-plus-credentials combination in `hhs_backend/server.py`.

This is an external transport/configuration defect, not a native VM81/HARMONICODE semantic defect.

## Compatibility rule

The external membrane should behave like an ordinary x86_64 Linux application service:

- same-origin browser clients work without CORS;
- separately hosted standard frontends may be authorized by exact HTTP(S) origins;
- ordinary GET/HEAD/POST/PUT/PATCH/DELETE/OPTIONS browser methods remain available;
- normal JSON, OpenAPI, static assets, and WebSocket projections remain transport mechanisms only;
- frontend code remains request/projection authority only;
- native runtime/VM81/receipt authority is unchanged;
- wildcard cross-origin credential authority is forbidden.

## Implemented

### `hhs_backend/frontend_ingress_policy_v1.py`

New dependency-light compatibility policy:

- parses `HHS_CORS_ALLOWED_ORIGINS` as a comma-separated exact origin list;
- accepts only `http://` and `https://` scheme/host/port origins;
- strips trailing slash and de-duplicates origins;
- rejects wildcard `*`;
- rejects URL paths, query strings, fragments, and non-origin values;
- declares standard browser HTTP methods;
- exposes runtime cache/ETag/content-disposition headers to an authorized cross-origin frontend;
- keeps same-origin transport as the zero-configuration default;
- explicitly records frontend role as request/projection only and backend role as native FastAPI/kernel authority.

### `hhs_backend/server.py`

The canonical FastAPI app now obtains CORS configuration from the ingress policy.

Removed:

```python
allow_origins=["*"]
allow_credentials=True
```

Replaced with exact configured origins while preserving credentials only for explicitly allowed origins.

### `deploy/digitalocean/hhs-pass196.env.example`

Documents how a separately hosted React/Vite/plain-JS/mobile-WebView frontend can be enabled:

```text
HHS_CORS_ALLOWED_ORIGINS=https://console.example.com,http://127.0.0.1:5173
```

Production same-origin Runtime OS operation does not require this variable.

### Test and CI

Added:

- `tests/test_hhs_standard_frontend_ingress_v1.py`
- `.github/workflows/standard-frontend-ingress.yml`

The tests enforce:

- same-origin default;
- exact-origin normalization;
- duplicate removal;
- wildcard rejection;
- malformed-origin rejection;
- standard browser method availability;
- no recurrence of wildcard origin + credential configuration;
- production environment documentation;
- preserved native backend authority.

## Commit chain

- `48864339923f5defe015958b3ef467a1feaab88f` — initial explicit CORS ingress repair
- `e284a0f499c41b6dd71ea4de88e7b3434e76d7d3` — production external-origin configuration documentation
- `0e4e440cd2ff917d443eb426d41b5b77dcc7e4ea` — standard frontend ingress policy module
- `6f57a89da808f6893bff07a2d2d445c60b071f96` — canonical server policy binding
- `3ce5bb5ded9827fcc6d862dccb9bcc640ae45da3` — ingress compatibility regressions
- `57bd9694d71088f4978f35008fe9eb847fe96aa2` — dependency-scoped CI gate

## Dependency-scoped validation

The branch CI runs:

```bash
python -m py_compile \
  hhs_backend/frontend_ingress_policy_v1.py \
  hhs_backend/server.py

python -m pytest -q tests/test_hhs_standard_frontend_ingress_v1.py
```

Existing downstream workflows may run independently. Slow/queued unrelated CI does not block a restartable checkpoint.

## Next repair-forward probes

After this ingress policy lands, probe only concrete failures and repair forward:

1. same-origin HTTP JSON fetch from the production Runtime OS;
2. explicitly allowed cross-origin preflight + credentialed request;
3. OpenAPI retrieval and request-schema compatibility;
4. all four standard WebSocket projections;
5. standard browser/static asset MIME delivery;
6. frontend POST body/content-type handling;
7. bounded file/multimodal upload ingress where exposed;
8. reverse-proxy HTTPS/WebSocket upgrade behavior;
9. typed error responses that never fall through to SPA HTML;
10. legacy frontend adapters that still send a transport shape the canonical backend no longer accepts.

A failure at one of these boundaries is classified as an ingress/adapter deviation and repaired there. It is not grounds to bypass the native backend or substitute browser-side execution.
