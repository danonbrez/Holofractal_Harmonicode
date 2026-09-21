# Pass 220 Ubuntu Application VM Production Deployment — Restart Record

## Identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main: `c0f02b1b0f87603a96cdfd40b734f5b858abf59e`
- Branch: `pass220-ubuntu-vm-production-deploy-20260921`
- Merge target: `main`
- Pull request: #537
- Production droplet: `hhs-production-01` / `598826630`
- Production Ubuntu: 24.04 LTS x86_64
- Production IPv4: `165.227.220.193`

## Delivery order

```text
Ubuntu GUI-capable application VM
-> Bash / hhs-vm
-> inherited Pass 190 operation + capability authority
-> loopback standalone ASGI service
-> nginx TLS /vm-api/ boundary
-> public secure OpenAPI verification
-> only then frontend/FastAPI client wiring
```

The frontend is intentionally unchanged in this branch.

## Repairs implemented

1. Installed `/usr/local/bin/hhs-vm` no longer assumes its repository is
   `/usr/local`. It resolves the repository and Python runtime from the
   root-owned application-VM environment file, with repository-local fallback.

2. The systemd service no longer hardcodes `/usr/bin/python3`. The installer
   selects `HHS_APPLICATION_VM_PYTHON_BIN`, preferring the production
   `/opt/hhs/venv/bin/python`, verifies FastAPI/uvicorn there, seals that path
   into the environment file, and materializes it into the unit.

3. Production installation uses the actual exact-main checkout
   `/opt/hhs/app`.

4. Production requires Ubuntu desktop components and installs
   `ubuntu-desktop-minimal` when absent. The backend remains independent of
   an active desktop login session.

5. Port `8720` remains loopback-only. Public exposure is only through the
   existing nginx TLS server under `/vm-api/`.

6. `configure_production_nginx.py` idempotently injects the application-VM
   include into the TLS server block that already owns the Runtime OS
   `127.0.0.1:8080` proxy. It creates a backup and rolls back on `nginx -t`
   failure.

7. Local verification proves Ubuntu/desktop presence, CLI/API operation
   parity, signed-capability enforcement, operation count, loopback binding,
   OpenAPI security metadata, and absence of frontend authority.

8. The post–exact-main production workflow waits for the exact target SHA,
   installs the backend, configures nginx, and externally verifies public HTTPS
   health/OpenAPI, anonymous rejection, and a short-lived signed-capability
   status call.

## Authority preservation

- no new VM81 authority;
- no new Hash72 mint/clock;
- no new Hash216 persistence authority;
- no new Pass 190 operation registry;
- no new capability-token schema or signature algorithm;
- no remote token-issuance endpoint;
- no frontend/static mount;
- no frontend route is authorized to bypass the application-VM boundary.

## Validation

Completed in branch construction:

- branch starts from merged backend main head;
- production checkout/runtime-path mismatch repaired;
- installed CLI root-resolution defect repaired;
- systemd Python-runtime mismatch repaired;
- dependency-scoped tests extended for installed CLI and nginx TLS insertion;
- production deployment workflow is repository-visible and pinned-SSH only.

Remaining gate:

1. exact-head Pass 220 dependency-scoped CI must pass;
2. merge #537;
3. DigitalOcean Production Exact Main must promote the merge SHA;
4. post-exact-main Pass 220 production workflow must succeed;
5. verify public `https://165.227.220.193/vm-api/openapi.json`;
6. verify anonymous protected calls return 401;
7. verify a short-lived signed capability succeeds through public HTTPS;
8. only after those receipts are green begin the FastAPI/frontend adapter pass.

## Next action

Read the exact-head Pass 220 CI result for PR #537. Repair only impacted
surfaces if it fails. If green, merge #537 and verify the exact-main production
and application-VM production workflows before beginning frontend wiring.
