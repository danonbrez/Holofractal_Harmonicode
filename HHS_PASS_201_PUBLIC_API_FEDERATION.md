# HHS PASS 201 — PUBLIC API FEDERATION FOR ALL REGISTERED SERVICES AND PASS MODULES

Contract identifier: `HHS-P201-PUBLIC-API-FEDERATION-SERVICE-PASS-ROUTER-OPENAPI`

Classification target: `HHS_PASS_201_PUBLIC_API_FEDERATION_VERIFIED`

## 1. Purpose

Pass 201 makes every registered HHS service and every repository pass module discoverable through the public API. Every API router present in `hhs_backend.api` is inspected during server composition and every route not already attached to the public FastAPI application is attached before the public static-file mount.

The public API federation provides:

- one canonical catalog for every registered HTTP and WebSocket route;
- one service catalog derived from registered route tags and prefixes;
- one pass-module catalog derived from repository-visible Python pass modules;
- a pass-module detail endpoint with contract, classification, version, exports, and associated routes when importable;
- the complete generated OpenAPI document;
- a bounded public tool interface for catalog inspection;
- a deterministic registration report identifying imported modules, attached routers, duplicate routes, import failures, and unexposed routers.

## 2. Registration doctrine

A Python module under `hhs_backend.api` that exports one or more `fastapi.APIRouter` objects is a registered API module.

At public server composition:

1. enumerate every Python module in `hhs_backend.api`;
2. import each module once;
3. inspect every module-level `APIRouter` object;
4. compare each router route against the routes already attached to the application;
5. attach each missing route exactly once;
6. retain a deterministic registration report;
7. reject closure when any imported router still has an unexposed route.

Existing explicit router composition remains valid. Automatic federation fills only missing routes and does not replace or reorder already registered authority routes.

## 3. Public route identity

Every cataloged route binds its deterministic identifier, route type, path, methods or WebSocket classification, endpoint name and module, tags, OpenAPI visibility, service identifier, pass identifier when derivable, and direct invocation path.

The route identifier is a deterministic SHA-256 digest of the canonical route identity. It is an index identity, not runtime authority and not a replacement for Hash72 receipts.

## 4. Service catalog

Services are grouped from registered route tags and stable path prefixes. Each record includes its service identity, routes, paths, methods, endpoint modules, pass identities, and public availability.

## 5. Pass-module catalog

Pass modules are discovered from repository-visible Python modules whose names contain a pass identifier such as `pass196`, `pass200a`, or `pass200c`.

A pass module without its own router remains publicly accessible through its pass detail record. A pass module with API routes is additionally accessible through its native routes.

## 6. Public endpoints

Pass 201 registers:

- `GET /api/public/status`
- `GET /api/public/catalog`
- `GET /api/public/routes`
- `GET /api/public/routes/{route_id}`
- `GET /api/public/services`
- `GET /api/public/services/{service_id}`
- `GET /api/public/passes`
- `GET /api/public/passes/{module_name:path}`
- `GET /api/public/openapi`
- `GET /api/public/tools`
- `POST /api/public/tools/invoke`

Native service and pass routes remain callable at their original public paths.

## 7. Public tool boundary

The public tool interface exposes catalog inspection only. It does not create a generic arbitrary Python-call surface. Mutating operations remain governed by native API routes, authorization membranes, VM81 ticks, and receipt contracts.

## 8. Closure requirements

Pass 201 is closed only when every importable API router is inspected, no router route remains unexposed, every application route appears in the catalog, every OpenAPI-visible route appears in OpenAPI, every discovered pass module appears in the pass catalog, all catalog endpoints respond, identifiers are deterministic across restart, and static `/` remains last.

## 9. Claim boundary

Pass 201 proves public discovery and HTTP/WebSocket accessibility for registered API routers and repository-visible pass metadata. It does not make every internal Python function remotely executable; execution surfaces require explicit governed schemas and authority contracts.
