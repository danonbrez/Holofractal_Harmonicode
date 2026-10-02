# Production recovery promotion — 2026-10-02

## Recovery boundary

Production Droplet `603583798` at `159.65.178.254` was restored from
DigitalOcean backup `247312238` (`hhs-production-04 2026-09-27 16:21 UTC`)
after independent clone validation proved that backup boots with healthy SSH,
nginx, systemd-networkd, and HHS service state.

The pre-recovery broken state remains preserved independently as snapshot
`247938260` (`hhs-production-04-pre-rollback-20261001`).

## External recovery proof

A GitHub-hosted runner verified after restore:

- TCP 22 open;
- TCP 80 open;
- TCP 443 open;
- pinned production SSH authority accepted;
- `ssh.service` active;
- `nginx.service` active;
- `hhs.service` active;
- `NetworkManager` inactive;
- `systemd-networkd` active;
- private runtime listener on `127.0.0.1:8080`;
- local HTTPS body available.

Restored repository boundary before forward promotion:

`cf2764c24e85ff4980d599f528218f1328b81627`

## Forward promotion

This repository-visible commit intentionally triggers the existing
DigitalOcean Production Exact Main workflow. The promotion must fast-forward
the recovered healthy host to this exact `main` descendant and install the
merged Lane 5 host-ingress zero-bypass membrane.

Acceptance requires the production workflow to verify:

- exact-main checkout identity;
- guarded updater ownership;
- systemd-owned Lane 5 ingress socket on `127.0.0.1:8715`;
- no public nginx proxy bypass to `:8080` or `:8720`;
- public Runtime OS HTTPS reachability;
- `X-HHS-Lane5-Ingress: mediated` on the public root;
- preserved independent SSH recovery plane.

Do not delete safety snapshot `247938260` until the forward promotion and
public verification complete.
