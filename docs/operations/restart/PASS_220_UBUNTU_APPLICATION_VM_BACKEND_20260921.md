# Pass 220 Ubuntu Application VM Backend Control Plane — Restart Record

## Identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main: `820e0ace4bf07919bfc8a6e52692af18a305f2c1`
- Branch: `pass220-ubuntu-vm-control-plane-20260921`
- Merge target: `main`
- PR: #535
- Implementation head before this checkpoint: `5a8f23ef307335eed6ba01c955e07946943188b2`

## Scope

Backend-first integration only:

```text
Ubuntu VM
-> Bash/CLI
-> Pass190 operation/capability authority
-> secure standalone OpenAPI
-> systemd loopback service
-> nginx TLS reverse-proxy boundary
```

The production Runtime OS/FastAPI frontend is intentionally unchanged.

## Implemented

- `hhs_runtime/pass220/application_vm_control_plane.py`
- `hhs_runtime/pass220/application_vm_cli.py`
- `bin/hhs-vm`
- `hhs_backend/application_vm_api_server.py`
- Ubuntu systemd/nginx/install/verify deployment files
- dependency-scoped Pass 220 test
- dependency-scoped GitHub workflow
- the additive Pass 220 CLI supplies the configured Pass 190 capability
  context and preserves structured argv without modifying frozen Pass 190
  source.

## Security/authority boundary

- public backend binds loopback only;
- public exposure is through existing TLS nginx;
- all VM API surfaces except health/OpenAPI/docs require a valid signed
  `HHS-Capability` credential;
- operation-specific scopes remain enforced by Pass 190;
- token issuance exists only in local CLI;
- no new VM81 authority;
- no new Hash72 mint/clock;
- no new Hash216 persistence;
- no new capability-token schema or signature algorithm;
- no frontend/static mount.

## Validation completed in repository construction

- branch is 0 commits behind base at PR creation;
- PR #535 is mergeable;
- deployment scripts are covered by `bash -n` / `sh -n` in the new workflow;
- Python surfaces are covered by `py_compile`;
- API/Bash/receipt/security parity is covered by
  `tests/pass220/test_pass220_ubuntu_application_vm_control_plane.py`.

## Validation remaining

- Pass 220 Ubuntu Application VM Control Plane workflow must execute on the
  current head;
- inherited Pass 190 I136 source identities remain byte-for-byte unchanged;
- if either fails, repair only the affected surface;
- after green validation, merge PR #535 and verify exact main;
- install on the Ubuntu GUI VM and execute
  `deployment/ubuntu/application_vm/verify.sh`;
- verify the public HTTPS `/vm-api/openapi.json` and signed-capability calls.

## Environment

Target deployment:

```text
Ubuntu
Ubuntu desktop / GUI packages present
repository: /opt/holofractal-harmonicode
service user: hhs
state: /var/lib/hhs/application-vm
loopback: 127.0.0.1:8720
public prefix: /vm-api/
TLS termination: nginx
```

## Next action

Read the exact-head Pass 220 and Pass 190 workflow results. Repair forward if
needed. Merge only after dependency-scoped validation is green, then validate
the actual Ubuntu VM backend before beginning frontend wiring.
