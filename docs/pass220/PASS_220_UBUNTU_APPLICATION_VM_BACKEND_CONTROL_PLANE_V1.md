# Pass 220 — Ubuntu Application VM Backend Control Plane v1

## Purpose

This cycle makes the integrated HHS/HARMONICODE application VM independently
operable **before frontend composition**.

The canonical machine relationship is:

```text
VM81 runtime / virtual hardware  [ONLY AUTHORITY]
-> Lane 5 C++ BIOS / AGI optimization control center
-> cumulative pass system OS + callable service registry
-> internal Ubuntu Linux guest
-> Bash / ABI / API / opcode / GUI interface environment
-> VM81 admission for any canonical mutation
-> Hash72 receipt closure
-> Hash216 permanent validation storage
```

This Pass 220 backend is an interface/application surface of that integrated
machine. Ubuntu, Pass 190, OpenAPI, Bash, and the frontend are not authorities.
A host-side deployment or transport harness must not be substituted for the
canonical VM81-backed internal Ubuntu guest.

## Local Bash surface

```bash
sh bin/hhs-vm status
sh bin/hhs-vm doctor
sh bin/hhs-vm capabilities
sh bin/hhs-vm shell -- hhs status
sh bin/hhs-vm invoke python.len '{"value":[1,2,3]}'
sh bin/hhs-vm harmonicode 'Len(value=[1,2,3])'
sh bin/hhs-vm receipts
sh bin/hhs-vm replay <hash72>
```

The Pass 220 `hhs-vm` wrapper supplies the environment-bound Pass 190
capability context and preserves shell/JSON argv boundaries without modifying
the frozen Pass 190 shell source.

Local operator token issuance reuses the inherited Pass 190 HMAC capability
format and issuer:

```bash
sudo -u hhs hhs-vm \
  --env-file /etc/hhs/application-vm.env \
  token issue \
  --principal operator \
  --scope runtime.mutate
```

There is no remote token-issuance endpoint.

## Public OpenAPI

The standalone ASGI entrypoint is:

```text
hhs_backend.application_vm_api_server:app
```

It mounts no Runtime OS frontend and no static application bundle.

Anonymous network surface:

```text
GET /health
GET /openapi.json
GET /docs
```

Signed-capability surface:

```text
GET  /v1/vm/status
GET  /v1/vm/doctor
GET  /v1/vm/capabilities
POST /v1/vm/shell
POST /v1/vm/operations/{operation_id}
POST /v1/vm/harmonicode/eval
GET  /v1/vm/receipts
POST /v1/vm/replay/{receipt_hash72}
```

The OpenAPI document declares `HhsCapabilityToken`. The header form is:

```text
Authorization: HHS-Capability <signed-token>
```

Operation-specific scope authorization remains owned by the inherited Pass 190
registry and verifier.

## Ubuntu service boundary

The service binds only to:

```text
127.0.0.1:8720
```

Public traffic terminates at an existing TLS-enabled nginx server and is
reverse-proxied through `/vm-api/`.

Direct public exposure of port 8720 is not authorized.

The installer verifies Ubuntu and, by default, requires Ubuntu desktop
components. It may install `ubuntu-desktop-minimal` only when the operator
explicitly sets:

```bash
HHS_APPLICATION_VM_INSTALL_GUI=1
```

The backend service does not require an active desktop login session.

## Authority preservation

This integration creates no new:

- VM81 authority;
- Hash72 receipt clock or mint authority;
- Hash216 persistence authority;
- operation registry;
- capability-token schema;
- capability signature algorithm.

It composes inherited Pass 184/190 capability and application surfaces into the
cumulative pass-system operating system and callable service registry. VM81
remains the only authority; Lane 5 remains its BIOS; Hash216 remains permanent
validation storage.

Runtime availability is distinct from cognitive execution: Lane 5 reasoning and
optimization remain callable bounded circuits and are not started continuously
merely because Ubuntu, an API service, or the frontend is running.

## Installation

On an Ubuntu VM with the repository at
`/opt/holofractal-harmonicode`:

```bash
sudo REPO_ROOT=/opt/holofractal-harmonicode \
  HHS_APPLICATION_VM_REQUIRE_GUI=1 \
  bash deployment/ubuntu/application_vm/install.sh
```

To install the required Ubuntu desktop packages when absent:

```bash
sudo REPO_ROOT=/opt/holofractal-harmonicode \
  HHS_APPLICATION_VM_INSTALL_GUI=1 \
  deployment/ubuntu/application_vm/install.sh
```

Then place
`deployment/ubuntu/application_vm/nginx-hhs-application-vm.conf`
inside the existing TLS server block and run:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Verification:

```bash
sudo -u hhs \
  HHS_APPLICATION_VM_ENV_FILE=/etc/hhs/application-vm.env \
  bash deployment/ubuntu/application_vm/verify.sh
```

## Next boundary

Only after this backend gate is running and independently verified should the
production FastAPI/Runtime OS frontend be changed to consume it as an
application client.
