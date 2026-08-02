# Pass 189 DigitalOcean Deployment

This directory contains the repository-native DigitalOcean deployment assets for Pass 189 Iterations 1–4.

The complete installation, operations, backup, restore, rollback, security, troubleshooting, and maintenance runbook is:

[`docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md`](../../../../docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md)

## Service map

| Unit | Address | State |
|---|---|---|
| `hhs-pass189.service` | `127.0.0.1:8189` | runtime process state |
| `hhs-pass189-iteration2.service` | `127.0.0.1:8190` | `/var/lib/hhs-pass189/iteration2.sqlite3` |
| `hhs-pass189-iteration3.service` | `127.0.0.1:8191` | `/var/lib/hhs-pass189/iteration3.sqlite3`, `/var/lib/hhs-pass189/iteration3/` |
| `hhs-pass189-iteration4.service` | `127.0.0.1:8192` | `/var/lib/hhs-pass189/iteration4.sqlite3`, `/var/lib/hhs-pass189/iteration4-quarantine/` |

Start in the listed order. Stop in reverse order.

## Files

| File | Purpose |
|---|---|
| `install.sh` | validate, install units, update the environment file, enable services, and check loopback health |
| `verify.sh` | verify APIs, visual surfaces, DigitalOcean authority, and hardware-dispatch denial |
| `nginx-hhs-pass189.conf` | location blocks for Iterations 1–4, APIs, SSE, and WebSockets |
| `hhs-pass189.service` | Iteration 1 hydration service |
| `hhs-pass189-iteration2.service` | Iteration 2 calibration and causal authority |
| `hhs-pass189-iteration3.service` | Iteration 3 fail-closed software adapter authority |
| `hhs-pass189-iteration4.service` | Iteration 4 provenance and promotion-token lifecycle authority |

## Install

The committed units require the checkout at:

```text
/opt/holofractal-harmonicode
```

Validate and install:

```bash
cd /opt/holofractal-harmonicode
make -C native_projects/hhs_pass189_hqlh_runtime validate

sudo REPO_ROOT=/opt/holofractal-harmonicode \
  SERVICE_USER=hhs \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh
```

Install the nginx snippet inside the existing HTTPS server block:

```bash
sudo install -m 0644 \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/nginx-hhs-pass189.conf \
  /etc/nginx/snippets/hhs-pass189.conf
sudo nginx -t
sudo systemctl reload nginx
```

The site configuration must contain:

```nginx
include /etc/nginx/snippets/hhs-pass189.conf;
```

## Verify

Local:

```bash
sudo native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

Public HTTPS:

```bash
sudo \
  BASE_URL=https://YOUR_DOMAIN \
  ITERATION2_URL=https://YOUR_DOMAIN \
  ITERATION3_URL=https://YOUR_DOMAIN \
  ITERATION4_URL=https://YOUR_DOMAIN \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

## Common operations

Status:

```bash
sudo systemctl status \
  hhs-pass189.service \
  hhs-pass189-iteration2.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration4.service \
  --no-pager --full
```

Logs:

```bash
sudo journalctl \
  -u hhs-pass189.service \
  -u hhs-pass189-iteration2.service \
  -u hhs-pass189-iteration3.service \
  -u hhs-pass189-iteration4.service \
  --since '1 hour ago' \
  --no-pager
```

Listeners:

```bash
sudo ss -ltnp | grep -E ':(8189|8190|8191|8192)\b'
```

All four services must remain loopback-only.

## Co-host warning

Pass 190 currently also defaults to `127.0.0.1:8190`. Do not enable Pass 189 Iteration 2 and the default Pass 190 service on the same host without a documented systemd, nginx, verifier, and monitoring port override.

Pass 196 currently uses `127.0.0.1:8080` and does not collide with the default Pass 189 ports.

## Authority boundary

Vercel is excluded from this deployment authority. Iteration 3 executes only `LOOPBACK` and `FILE_SINK` software test adapters. Iteration 4 hardware packages remain non-executable candidates; real hardware dispatch is not authorized.
