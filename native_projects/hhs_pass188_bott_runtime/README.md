# HHS Pass 188 Bott Runtime

Pass 188 implements the Pass 187 Bott-periodic hydration contract as an executable, no-float runtime.

## Surfaces

- C11 ABI and static/shared libraries
- branchless x86_64 assembly entrypoint
- exhaustive native validation over all 1,259,712 projected addresses
- Python runtime, receipts, replay, and CLI
- HTTP transition/hydration/replay API
- WebSocket runtime event stream
- responsive visual runtime inspector

## Build and validate

```sh
make validate
```

Expected native terminal result:

```text
HHS_PASS_188_BOTT_RUNTIME_PASS states=1259712 active=629856 collapse=629856 checksum=11e3bbf0214751c3
```

## CLI

```sh
build/hhs_pass188_cli transition 0
build/hhs_pass188_cli hydrate
python3 python/hhs_pass188.py transition 0
python3 python/hhs_pass188.py hydrate
```

## Visual IDE and API

```sh
python3 server/hhs_pass188_server.py --host 0.0.0.0 --port 8188
```

Open `http://localhost:8188`. The same server exposes:

- `GET /api/pass188/health`
- `GET|POST /api/pass188/transition`
- `GET /api/pass188/hydrate`
- `POST /api/pass188/replay`
- `GET /api/pass188/events`
- `GET /ws`
