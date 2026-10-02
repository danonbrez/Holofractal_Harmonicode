# Lane 5 host ingress membrane restart checkpoint — 2026-10-02

## Objective

Repair the production environmental-ingress divergence exposed by the
2026-10-01 outage investigation.

The repository already required Lane 5 mediation and signed environmental VM81
admission for applicable environmental/canonical paths, but production network
ingress still entered nginx/private application sockets before Lane 5. The
existing native `lane5_zero_bypass_interposer` field was a route witness, not a
Linux socket/firewall/network interposer.

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- branch: `repair/lane5-host-ingress-membrane-20261002`
- pull request: `#679`
- merge target: `main`
- production deployment from pull request: disabled/skipped

Use the current branch head from GitHub as the restart SHA; later validation
repairs may advance it.

## Production preservation state

- DigitalOcean Droplet: `hhs-production-04`
- Droplet ID: `603583798`
- public IPv4: `159.65.178.254`
- production disk restored after rollback experiments to safety snapshot:
  `247938260` (`hhs-production-04-pre-rollback-20261001`)
- account status was verified active with no outstanding account balance.
- no PR #679 source has been deployed to the inaccessible production host.

Whole-disk rollback probes on the original production Droplet/IP reproduced the
same no-listener condition for the Sep 27, Sep 26, and earliest Sep 25
`hhs-production-04` backups. Further blind application/checkpoint rollback is
therefore not the active recovery strategy.

The user directly observed the HTML simulation and backend-generated messages
working during the active session immediately before the crash. The outage is
therefore treated as an operational state transition, with provider/host/network
inspection remaining separate from this repository repair.

## Implemented host-ingress membrane

Public application traffic becomes:

```text
80/443
-> nginx
-> systemd-owned 127.0.0.1:8715 socket
-> hhs_backend.lane5_ingress_gateway
-> exact ordered-byte/provenance Lane 5 1.48 mediation
-> private 127.0.0.1:8080 or 127.0.0.1:8720
-> inherited signed environmental VM81 admission where mutating
```

SSH/22 is not part of this dependency chain.

### Gateway

`hhs_backend/lane5_ingress_gateway.py`:

- length-frames actual transport/method/path/query/header/payload bytes;
- binds them through the existing arbitrary-byte Lane 5 1.48 native bridge;
- admits only candidate-only receipts with no VM81/Hash216 authority;
- requires the inherited signed environmental VM81 admission boundary;
- mediates HTTP requests and WebSocket handshakes/client frames;
- preserves the original Host header and forwards a Lane 5 handshake witness;
- fails closed on mediation failure;
- returns a mediated 503 when the private backend is unavailable rather than
  treating backend disappearance as permission to bypass Lane 5;
- startup health executes a real native Lane 5 mediation self-test.

Native 1.48 phase slots are restricted to `{0,18,36,54}`; the deterministic
network route maps the workload digest to that quarter-cycle geometry.

### Socket ownership

`deploy/digitalocean/hhs-lane5-ingress.socket` owns
`127.0.0.1:8715` independently of `hhs.service`.

`deploy/digitalocean/hhs-lane5-ingress.service` consumes inherited FD 3 with
Uvicorn and has no `Requires=hhs.service` or backend ordering dependency.

This ensures an application/backend process failure does not release the ingress
socket.

### Nginx and deployment

- generic Runtime OS proxy moves from `:8080` to `:8715`;
- `/vm-api/` moves from direct `:8720` to `:8715`;
- first-paint root/assets keep cache policy but no longer use direct nginx
  filesystem serving;
- HTTPS closure script discovers/targets `:8715`;
- guarded installer proves local Lane 5 native health before nginx migration;
- migration rolls nginx back on validation/reload failure;
- post-migration `nginx -T` must contain no direct public `:8080`/`:8720`
  proxy and must contain `:8715`;
- Exact-Main verifies socket/service/listener/nginx ownership and requires the
  public `X-HHS-Lane5-Ingress: mediated` response witness.

## Validation

Dedicated workflow:

`.github/workflows/pass220-lane5-host-ingress-membrane.yml`

It:

1. compiles Python/shell deployment surfaces;
2. builds the real C ABI;
3. executes `Lane5IngressMediator().health()` against the native runtime;
4. runs the new host-ingress regressions;
5. reruns I045, Application-VM, and guarded-updater contracts.

The expanded escaped-newline regression rejects the actual historical
patch-corruption shape (literal backslash-n followed by workflow indentation)
without rejecting legitimate shell escapes such as `printf '%s\n'`.

## Remaining validation/next action

1. inspect the newest PR #679 dependency-scoped workflow runs;
2. repair-forward attributable failures only;
3. require the dedicated native ingress gate, I045, Application-VM, HTTPS
   closure, and Exact-Main PR deployment-contract validation to pass;
4. mark PR ready only after those gates are green;
5. do not deploy to the inaccessible production Droplet merely to validate the
   source repair;
6. continue provider/host/network recovery independently, then apply the merged
   ingress membrane only after management access is restored.
