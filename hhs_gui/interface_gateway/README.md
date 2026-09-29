# HHS Interface Ubuntu PTY Gateway

Frontend-integration transport for the dedicated interface branch.

## Boundary

The gateway is transport only. It does not import HHS runtime implementation
modules and does not implement shell semantics. Every guest operation is invoked
through the existing external `bin/hhs-guest` CLI.

Browser flow:

```text
browser controls
  -> wss /api/interface/ubuntu/pty/ws
  -> loopback interface gateway :8787
  -> bin/hhs-guest pty-exec
  -> authenticated SSH + PTY
  -> Ubuntu guest
```

The SSH identity, known-hosts file, guest image identity, and guest Runtime
configuration remain server-side.

## Security

The gateway:

- is intended to bind only to `127.0.0.1:8787`;
- is disabled unless `HHS_INTERFACE_PTY_ENABLED=1`;
- refuses WebSocket use unless `HHS_INTERFACE_PTY_TOKEN` is configured;
- authenticates before status or execution;
- bounds command length, output size, PTY dimensions, and timeout;
- passes commands as arguments to `bin/hhs-guest`; it does not execute the
  command with a host shell;
- returns only the structured `hhs-guest` result;
- owns no VM81, Hash72, Hash216, Lane 5, filesystem, or persistence authority.

## Installation

From the repository root on the Ubuntu host:

```bash
sudo sh hhs_gui/interface_gateway/install.sh
```

The installer creates and starts the loopback systemd service, discovers the
single existing TLS server block that owns the HHS runtime proxy, injects the
interface snippet idempotently, runs `nginx -t`, rolls back the nginx edit on
validation failure, and reloads nginx only after validation succeeds.

The installer prints the newly generated interface bearer token once. Store it
securely. The proof client accepts it into an in-memory password field and clears
the field after authentication; it is not written to browser storage.

## Required inherited guest configuration

`bin/hhs-guest` continues to require the I043/I044 environment, including the
digest-pinned guest image and strict SSH identity/known-hosts configuration.
The gateway does not weaken or replace those requirements.

## Development

Vite routes `/api/interface/ubuntu/pty/*` to loopback port 8787. Start the
gateway separately with the same environment:

```bash
python -m uvicorn hhs_gui.interface_gateway.ubuntu_pty_gateway:app \
  --host 127.0.0.1 --port 8787
```

No mock fallback is provided. If the gateway, guest, SSH/PTTY transport, or
required credentials are unavailable, the client reports failure.
