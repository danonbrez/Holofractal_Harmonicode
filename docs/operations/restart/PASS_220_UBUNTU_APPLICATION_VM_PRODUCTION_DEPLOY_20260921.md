# Pass 220 Ubuntu Application VM Production Deployment — Backend-First Restart Record

## Identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main: `72c599586c0035af36f1eb96ca0c93bf8174b85f`
- Branch: `pass220-backend-first-independent-vm-deploy-20260921`
- Merge target: `main`
- Production droplet: `hhs-production-01` / `598826630`
- Production Ubuntu: 24.04 LTS x86_64
- Production IPv4: `165.227.220.193`

## Required delivery order

```text
Ubuntu GUI-capable application VM
-> versioned backend release
-> Bash / hhs-vm
-> inherited Pass 190 operation + capability authority
-> loopback standalone ASGI service
-> nginx TLS /vm-api/ boundary
-> public secure OpenAPI verification
-> deployment receipt
-> only then frontend/FastAPI client wiring
```

The Runtime OS/browser frontend is explicitly outside this acceptance gate. A
rendered frontend cannot qualify the backend as healthy.

## Root integration correction

The first production workflow was downstream of `DigitalOcean Production Exact
Main` and waited for `/opt/hhs/app` plus `hhs.service` to reach the same
commit before installing the application VM. That ordering made the backend
depend on successful frontend/runtime deployment, which contradicted the
backend-first delivery requirement.

The repaired production workflow now triggers directly from `main` and has no
dependency on the Runtime OS deployment workflow or `hhs.service`.

## Independent production release topology

The live application VM release is materialized as an exact Git worktree:

```text
/opt/hhs/app                           source Git repository
/var/lib/hhs/application-vm/
  releases/<commit-sha>/               exact backend source release
  current -> releases/<commit-sha>/    verified release pointer
  pass190-authority.sqlite3            persistent authority state
  last-success.json                    production verification receipt
/etc/hhs/application-vm.env            root-owned runtime/capability environment
/usr/local/bin/hhs-vm                  Bash/CLI entrypoint
127.0.0.1:8720                         standalone ASGI listener
https://165.227.220.193/vm-api/        nginx TLS public boundary
```

The installer accepts both ordinary Git checkouts and linked Git worktrees.

## Runtime and GUI requirements

- target OS must identify as Ubuntu;
- Ubuntu GUI components are required;
- `ubuntu-desktop-minimal` is installed when the GUI components are absent;
- no active desktop login session is required for the backend service;
- the production Python runtime prefers `/opt/hhs/venv/bin/python`;
- FastAPI and uvicorn are verified in the selected runtime before service
  installation.

## Security and authority boundary

- port 8720 is loopback-only;
- public exposure is only nginx TLS under `/vm-api/`;
- health and OpenAPI metadata are public;
- protected VM calls require a signed `HHS-Capability`;
- anonymous protected calls must return HTTP 401;
- capability issuance remains local-only;
- no frontend/static mount exists in the application-VM ASGI process;
- no new VM81 authority is created;
- no new Hash72 mint/clock is created;
- no new Hash216 persistence authority is created;
- no new Pass 190 registry or capability-token format is created.

## Deployment behavior

The production job:

1. validates the backend surfaces independently on the runner;
2. configures pinned SSH host trust;
3. locks application-VM deployment ownership;
4. fetches the requested main commit into the production Git object store;
5. creates/reuses an exact detached worktree under the versioned release root;
6. installs/starts the application-VM service from that release;
7. installs GUI components if required;
8. installs the nginx `/vm-api/` TLS route;
9. proves Bash/CLI and loopback API parity;
10. proves the listener is loopback-only;
11. externally verifies HTTPS health and OpenAPI;
12. proves anonymous denial and authenticated signed-capability access;
13. seals `last-success.json` with the verified target SHA.

A host-side failure before local verification completes attempts rollback to the
previous verified application-VM release without touching the frontend service.

## Frontend rule

Do not wire or debug the browser/FastAPI frontend as the source of authority
until the following backend evidence exists for the deployed commit:

```text
hhs-vm status                           PASS
hhs-vm shell -- hhs status              PASS
127.0.0.1:8720/health                   PASS
/vm-api/openapi.json over HTTPS          PASS
anonymous /v1/vm/status                 HTTP 401
signed /v1/vm/status                    PASS
single_vm81_authority_preserved         true
frontend_attached                       false
last-success.json target_sha             deployed commit
```

## Restart state

Implemented on this branch:

- worktree-compatible installer;
- frontend-independent main-triggered deployment;
- versioned backend release root;
- exact release verification;
- deployment lock;
- host-side rollback to the previous backend release;
- public signed-capability verification;
- production receipt sealing;
- dependency-scoped regression coverage proving no `workflow_run`,
  `DigitalOcean Production Exact Main`, or `hhs.service` dependency.

Next action:

1. run exact-head Pass 220 dependency-scoped CI;
2. merge this branch only after that gate is green;
3. allow the direct main push workflow to deploy the independent backend;
4. inspect the production workflow and host receipt;
5. only after the backend gate is green begin the frontend adapter cycle.
