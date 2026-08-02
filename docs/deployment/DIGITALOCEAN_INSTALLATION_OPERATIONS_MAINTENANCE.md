# DigitalOcean Installation, Operations, and Maintenance Runbook

## HHS Pass 189 hydration, calibration, adapter, and driver-provenance services

This document is the operator runbook for installing and maintaining the repository-native Pass 189 services on an Ubuntu DigitalOcean host.

It covers:

- first installation;
- validation and controlled upgrades;
- systemd and nginx operations;
- health checks and log inspection;
- state backup, restore, and rollback;
- security and firewall boundaries;
- port-conflict planning when Pass 190 or Pass 196 shares the host;
- routine maintenance and incident response.

Vercel is not part of this deployment or acceptance authority.

---

## 1. Scope and authority

The Pass 189 deployment consists of four loopback-only Python services behind an existing nginx HTTPS server.

| Layer | systemd unit | Loopback port | Primary state |
|---|---|---:|---|
| Iteration 1 hydration | `hhs-pass189.service` | `8189` | runtime process state |
| Iteration 2 calibration and causal authority | `hhs-pass189-iteration2.service` | `8190` | `/var/lib/hhs-pass189/iteration2.sqlite3` |
| Iteration 3 fail-closed adapter authority | `hhs-pass189-iteration3.service` | `8191` | `/var/lib/hhs-pass189/iteration3.sqlite3` and `/var/lib/hhs-pass189/iteration3/` |
| Iteration 4 provenance and token lifecycle | `hhs-pass189-iteration4.service` | `8192` | `/var/lib/hhs-pass189/iteration4.sqlite3` and `/var/lib/hhs-pass189/iteration4-quarantine/` |

The public TLS boundary is nginx. The Python services must remain bound to `127.0.0.1` unless a later contract explicitly replaces this rule.

The service dependency chain is:

```text
hhs-pass189.service
  → hhs-pass189-iteration2.service
    → hhs-pass189-iteration3.service
      → hhs-pass189-iteration4.service
```

Start in forward order. Stop in reverse order.

### Honest hardware boundary

Iteration 3 executes only the built-in `LOOPBACK` and sandboxed `FILE_SINK` software test adapters. Iteration 4 may classify real hardware packages only as non-executable candidates. The deployed stack does not authorize GPIO, serial, USB, network-device, or actuator dispatch.

---

## 2. Canonical paths

| Purpose | Path |
|---|---|
| Repository checkout | `/opt/holofractal-harmonicode` |
| Pass 189 project | `/opt/holofractal-harmonicode/native_projects/hhs_pass189_hqlh_runtime` |
| Service environment | `/etc/hhs/pass189.env` |
| systemd units | `/etc/systemd/system/hhs-pass189*.service` |
| Durable state root | `/var/lib/hhs-pass189` |
| nginx source include | `native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/nginx-hhs-pass189.conf` |
| Recommended nginx installed include | `/etc/nginx/snippets/hhs-pass189.conf` |
| Installer | `native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh` |
| Verifier | `native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh` |

The systemd units assume the repository is located at `/opt/holofractal-harmonicode`. A different checkout path requires coordinated unit overrides; changing only `REPO_ROOT` during installation does not change the hard-coded `WorkingDirectory` values in the committed units.

---

## 3. Port planning before installation

### 3.1 Dedicated Pass 189 host

The default allocation is:

```text
8189  Pass 189 Iteration 1
8190  Pass 189 Iteration 2
8191  Pass 189 Iteration 3
8192  Pass 189 Iteration 4
```

Use the committed installer and nginx include unchanged.

### 3.2 Co-hosting with Pass 190

The current Pass 190 service also defaults to `127.0.0.1:8190`. It cannot run simultaneously with Pass 189 Iteration 2 on the same address and port.

Before enabling both stacks, choose and document one of these strategies:

1. dedicate separate hosts;
2. reserve `8189–8192` for Pass 189 and relocate Pass 190;
3. relocate the Pass 189 stack with coordinated systemd, nginx, verification, and monitoring overrides.

The recommended co-host layout is:

```text
8080       Pass 196 integrated visual environment
8189–8192  Pass 189 Iterations 1–4
8290       Pass 190 API
```

To relocate Pass 190 to `8290`, create a persistent systemd drop-in rather than editing the installed unit directly:

```bash
sudo systemctl edit hhs-pass190.service
```

Use an override equivalent to the currently installed command, but clear and replace `ExecStart` with port `8290`:

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/python3 server/hhs_pass190_iteration7_server.py --host 127.0.0.1 --port 8290 --database /var/lib/hhs/pass190-authority.sqlite3
```

Then update the Pass 190 nginx upstream and deployment verifier, and run:

```bash
sudo systemctl daemon-reload
sudo systemctl restart hhs-pass190.service
sudo ss -ltnp | grep ':8290'
```

Record every port override in the host change log. The Pass 189 installer may reinstall its committed unit files, so Pass 189 port relocation must also use persistent systemd drop-ins.

### 3.3 Preflight port check

Run before installation or restart:

```bash
sudo ss -ltnp | grep -E ':(8080|8189|8190|8191|8192|8290)\b' || true
```

Do not proceed while an unexplained listener occupies a required port.

---

## 4. Host preparation

These commands assume Ubuntu 24.04 or a compatible Ubuntu server installation.

### 4.1 Create or access the host

Use SSH key authentication. Retain an active administrative session while changing firewall or SSH settings.

### 4.2 Install required packages

```bash
sudo apt update
sudo apt install -y \
  git \
  curl \
  ca-certificates \
  build-essential \
  python3 \
  python3-venv \
  python3-pip \
  sqlite3 \
  nginx
```

Confirm the essential tools:

```bash
git --version
python3 --version
cc --version
make --version
nginx -v
sqlite3 --version
```

### 4.3 Configure the firewall

Only SSH and the nginx web boundary should be publicly reachable.

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw status verbose
```

Enable UFW only after confirming the SSH rule:

```bash
sudo ufw enable
```

Do not add public firewall rules for ports `8189–8192`.

### 4.4 Configure DNS and TLS

Point the intended hostname to the Droplet public address. Configure the existing nginx HTTPS server before adding the Pass 189 include. Certificate issuance and renewal remain part of the host-level nginx/TLS administration.

---

## 5. Repository installation

### 5.1 Fresh checkout

```bash
sudo install -d -m 0755 /opt
sudo git clone \
  https://github.com/danonbrez/Holofractal_Harmonicode.git \
  /opt/holofractal-harmonicode
cd /opt/holofractal-harmonicode
sudo git checkout main
```

If the checkout must be writable by a named deployment administrator, set that ownership deliberately. Do not make the repository world-writable.

### 5.2 Existing checkout

```bash
cd /opt/holofractal-harmonicode
git status --short
git fetch origin
git checkout main
git pull --ff-only origin main
```

Stop if `git status --short` reports unexplained local modifications. Do not erase host-local work without reviewing it.

### 5.3 Record the candidate commit

```bash
git rev-parse HEAD
git log -1 --oneline
```

Save the commit SHA in the deployment change record.

---

## 6. Pre-install validation

Run the complete Pass 189 validator before changing systemd state:

```bash
cd /opt/holofractal-harmonicode
make -C native_projects/hhs_pass189_hqlh_runtime validate
```

The validator builds the native authority, performs the exhaustive contextual sweep, checks for prohibited floating-point authority instructions, runs all Pass 189 Python suites, exercises HTTP/SSE/WebSocket/visual surfaces, compiles Python files, and checks deployment shell syntax.

A failed validation is a deployment blocker. Repair the source, dependencies, or host environment; do not weaken invariant checks to force installation.

---

## 7. Install the Pass 189 services

Run the repository installer as root:

```bash
cd /opt/holofractal-harmonicode
sudo REPO_ROOT=/opt/holofractal-harmonicode \
  SERVICE_USER=hhs \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh
```

The installer:

1. creates the `hhs` system user when absent;
2. creates `/var/lib/hhs-pass189` and required subdirectories;
3. runs `make validate` again;
4. installs all four systemd units;
5. creates or updates `/etc/hhs/pass189.env`;
6. applies `root:hhs` ownership and mode `0640` to the environment file;
7. enables and starts all four units;
8. checks all four loopback health endpoints.

### Environment-file behavior

The installer preserves unknown `KEY=value` entries but rewrites the known Pass 189 defaults. It also removes comments and custom ordering. Back up `/etc/hhs/pass189.env` before an upgrade when it contains host-specific additions.

The service command lines currently bind the ports explicitly. Changing `HHS189_*_PORT` values alone does not relocate a service; use a systemd drop-in and matching nginx/verification updates.

Inspect the installed file:

```bash
sudo stat /etc/hhs/pass189.env
sudo sed -n '1,200p' /etc/hhs/pass189.env
```

Do not print secrets into shared logs or tickets.

---

## 8. Configure nginx

Install the committed location block as a snippet:

```bash
sudo install -m 0644 \
  /opt/holofractal-harmonicode/native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/nginx-hhs-pass189.conf \
  /etc/nginx/snippets/hhs-pass189.conf
```

Inside the intended HTTPS `server { ... }` block, add:

```nginx
include /etc/nginx/snippets/hhs-pass189.conf;
```

The snippet contains `location` directives and must be included inside a `server` block, not at the top-level `http` configuration.

Validate and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl status nginx --no-pager
```

Include the snippet exactly once per public server block. Duplicate locations will cause `nginx -t` to fail.

### Public routes

| Surface | Route |
|---|---|
| Iteration 1 visual | `/pass189/` |
| Iteration 1 API | `/api/pass189/` |
| Iteration 1 WebSocket | `/ws` |
| Iteration 2 visual | `/pass189/i2/` |
| Iteration 2 API | `/api/pass189/i2/` |
| Iteration 2 WebSocket | `/ws/pass189/i2` |
| Iteration 3 visual | `/pass189/i3/` |
| Iteration 3 API | `/api/pass189/i3/` |
| Iteration 3 WebSocket | `/ws/pass189/i3` |
| Iteration 4 visual | `/pass189/i4/` |
| Iteration 4 API | `/api/pass189/i4/` |
| Iteration 4 WebSocket | `/ws/pass189/i4` |

---

## 9. Installation verification

### 9.1 Local loopback verification

```bash
cd /opt/holofractal-harmonicode
sudo native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

### 9.2 Public TLS verification

Set all four URL variables to the same public origin when nginx provides the path routing:

```bash
cd /opt/holofractal-harmonicode
sudo \
  BASE_URL=https://YOUR_DOMAIN \
  ITERATION2_URL=https://YOUR_DOMAIN \
  ITERATION3_URL=https://YOUR_DOMAIN \
  ITERATION4_URL=https://YOUR_DOMAIN \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

### 9.3 Manual health checks

```bash
curl --fail --silent http://127.0.0.1:8189/api/pass189/health
curl --fail --silent http://127.0.0.1:8190/api/pass189/i2/status
curl --fail --silent http://127.0.0.1:8191/api/pass189/i3/status
curl --fail --silent http://127.0.0.1:8192/api/pass189/i4/status
```

Expected security assertions include:

```text
deployment_authority = DIGITALOCEAN_SELF_HOSTED
vercel_required = false
Iteration 3 actual_physical_dispatch = false
Iteration 4 real_hardware_dispatch_authorized = false
```

### 9.4 Verify listeners

```bash
sudo ss -ltnp | grep -E ':(8189|8190|8191|8192)\b'
```

Each listener must show `127.0.0.1`, not `0.0.0.0` or the Droplet public address.

---

## 10. Routine systemd operations

Define the service list for shell use:

```bash
PASS189_UNITS='hhs-pass189.service hhs-pass189-iteration2.service hhs-pass189-iteration3.service hhs-pass189-iteration4.service'
```

### Status

```bash
sudo systemctl status $PASS189_UNITS --no-pager --full
sudo systemctl is-active $PASS189_UNITS
sudo systemctl is-enabled $PASS189_UNITS
```

### Controlled stop

Stop dependents first:

```bash
sudo systemctl stop \
  hhs-pass189-iteration4.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration2.service \
  hhs-pass189.service
```

### Controlled start

Start authorities in dependency order:

```bash
sudo systemctl start hhs-pass189.service
sudo systemctl start hhs-pass189-iteration2.service
sudo systemctl start hhs-pass189-iteration3.service
sudo systemctl start hhs-pass189-iteration4.service
```

### Controlled restart

```bash
sudo systemctl stop \
  hhs-pass189-iteration4.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration2.service \
  hhs-pass189.service

sudo systemctl start hhs-pass189.service
sudo systemctl start hhs-pass189-iteration2.service
sudo systemctl start hhs-pass189-iteration3.service
sudo systemctl start hhs-pass189-iteration4.service
```

Run the verifier after every controlled restart.

### Reload changed unit files

```bash
sudo systemctl daemon-reload
sudo systemctl cat hhs-pass189-iteration4.service
```

Unit-file changes require a restart, not merely a daemon reload.

---

## 11. Logs and diagnostics

### Recent logs for all Pass 189 services

```bash
sudo journalctl \
  -u hhs-pass189.service \
  -u hhs-pass189-iteration2.service \
  -u hhs-pass189-iteration3.service \
  -u hhs-pass189-iteration4.service \
  --since '1 hour ago' \
  --no-pager
```

### Follow one service

```bash
sudo journalctl -fu hhs-pass189-iteration4.service
```

### Show the current boot

```bash
sudo journalctl -b -u hhs-pass189.service --no-pager
```

### Failed units

```bash
sudo systemctl --failed
```

### nginx diagnostics

```bash
sudo nginx -t
sudo systemctl status nginx --no-pager
sudo journalctl -u nginx --since '1 hour ago' --no-pager
sudo tail -n 200 /var/log/nginx/error.log
```

Do not post environment files, arm tokens, operator keys, driver package payloads, or private request bodies into public issue trackers.

---

## 12. State inspection and database checks

### Disk use

```bash
sudo du -sh /var/lib/hhs-pass189
sudo du -sh /var/lib/hhs-pass189/* 2>/dev/null | sort -h
sudo df -h /var/lib/hhs-pass189
sudo df -i /var/lib/hhs-pass189
```

Iteration 4 quarantine storage may grow independently of the SQLite database. Investigate growth before deleting any payload.

### Read-only SQLite checks

```bash
sudo -u hhs sqlite3 -readonly /var/lib/hhs-pass189/iteration2.sqlite3 'PRAGMA quick_check;'
sudo -u hhs sqlite3 -readonly /var/lib/hhs-pass189/iteration3.sqlite3 'PRAGMA quick_check;'
sudo -u hhs sqlite3 -readonly /var/lib/hhs-pass189/iteration4.sqlite3 'PRAGMA quick_check;'
```

Expected result:

```text
ok
```

Do not delete SQLite `-wal` or `-shm` files while a service is running. They are part of normal WAL-mode operation.

### Ownership audit

```bash
sudo find /var/lib/hhs-pass189 -maxdepth 2 -printf '%u:%g %m %p\n' | sort
sudo stat /etc/hhs/pass189.env
```

Repair ownership only after understanding why it changed:

```bash
sudo chown -R hhs:hhs /var/lib/hhs-pass189
sudo chown root:hhs /etc/hhs/pass189.env
sudo chmod 0640 /etc/hhs/pass189.env
```

---

## 13. Backup procedure

A coordinated offline backup is the safest complete snapshot because it preserves all SQLite databases, WAL state, adapter files, quarantine payloads, and environment configuration together.

### 13.1 Prepare a root-only backup directory

```bash
sudo install -d -m 0700 /var/backups/hhs-pass189
```

### 13.2 Record the deployed commit

```bash
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
git -C /opt/holofractal-harmonicode rev-parse HEAD | \
  sudo tee "/var/backups/hhs-pass189/${STAMP}.commit" >/dev/null
```

### 13.3 Stop the service chain

```bash
sudo systemctl stop \
  hhs-pass189-iteration4.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration2.service \
  hhs-pass189.service
```

### 13.4 Create the archive

```bash
sudo tar --acls --xattrs \
  -C / \
  -czf "/var/backups/hhs-pass189/${STAMP}.tar.gz" \
  var/lib/hhs-pass189 \
  etc/hhs/pass189.env

sudo sha256sum "/var/backups/hhs-pass189/${STAMP}.tar.gz" | \
  sudo tee "/var/backups/hhs-pass189/${STAMP}.tar.gz.sha256" >/dev/null
```

### 13.5 Restart and verify

```bash
sudo systemctl start hhs-pass189.service
sudo systemctl start hhs-pass189-iteration2.service
sudo systemctl start hhs-pass189-iteration3.service
sudo systemctl start hhs-pass189-iteration4.service

cd /opt/holofractal-harmonicode
sudo native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

### 13.6 Protect off-host backups

Copy backups to encrypted off-host storage. A backup stored only on the same Droplet does not protect against host loss. Restrict access because the archive may include operational credentials and quarantined package material.

---

## 14. Restore procedure

Use a maintenance window. Confirm the archive checksum and recorded commit before modifying state.

### 14.1 Verify the archive

```bash
cd /var/backups/hhs-pass189
sudo sha256sum -c YYYYMMDDTHHMMSSZ.tar.gz.sha256
cat YYYYMMDDTHHMMSSZ.commit
```

### 14.2 Checkout the matching code

```bash
cd /opt/holofractal-harmonicode
sudo git fetch origin
sudo git checkout COMMIT_SHA_FROM_BACKUP
```

Restoring state into a materially different code version may violate schema or receipt assumptions.

### 14.3 Stop services

```bash
sudo systemctl stop \
  hhs-pass189-iteration4.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration2.service \
  hhs-pass189.service
```

### 14.4 Preserve the current state before replacement

```bash
sudo mv /var/lib/hhs-pass189 "/var/lib/hhs-pass189.pre-restore.$(date -u +%Y%m%dT%H%M%SZ)"
```

### 14.5 Extract and repair permissions

```bash
sudo tar --acls --xattrs -C / -xzf /var/backups/hhs-pass189/YYYYMMDDTHHMMSSZ.tar.gz
sudo chown -R hhs:hhs /var/lib/hhs-pass189
sudo chown root:hhs /etc/hhs/pass189.env
sudo chmod 0640 /etc/hhs/pass189.env
```

### 14.6 Reinstall units and verify

```bash
cd /opt/holofractal-harmonicode
sudo REPO_ROOT=/opt/holofractal-harmonicode \
  SERVICE_USER=hhs \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh

sudo nginx -t
sudo systemctl reload nginx
sudo native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

Keep the pre-restore directory until application-level verification is complete.

---

## 15. Controlled upgrade procedure

Never deploy directly from an unvalidated working tree.

### 15.1 Pre-upgrade checks

```bash
cd /opt/holofractal-harmonicode
git status --short
git rev-parse HEAD
sudo systemctl --failed
sudo native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

Resolve unexplained local changes or failed units before upgrading.

### 15.2 Create a backup

Follow the complete backup procedure in Section 13.

### 15.3 Fetch and inspect the target

```bash
cd /opt/holofractal-harmonicode
git fetch origin
git log --oneline --decorate --max-count=20 HEAD..origin/main
git diff --stat HEAD..origin/main
```

### 15.4 Fast-forward to the target

```bash
git checkout main
git pull --ff-only origin main
TARGET_COMMIT=$(git rev-parse HEAD)
printf 'Target commit: %s\n' "$TARGET_COMMIT"
```

### 15.5 Validate before installation

```bash
make -C native_projects/hhs_pass189_hqlh_runtime validate
```

### 15.6 Run the idempotent installer

```bash
sudo REPO_ROOT=/opt/holofractal-harmonicode \
  SERVICE_USER=hhs \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh
```

### 15.7 Refresh nginx assets

```bash
sudo install -m 0644 \
  native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/nginx-hhs-pass189.conf \
  /etc/nginx/snippets/hhs-pass189.conf
sudo nginx -t
sudo systemctl reload nginx
```

### 15.8 Verify local and public surfaces

Run both verification modes from Section 9.

### 15.9 Record closure

Record:

- prior commit;
- target commit;
- backup archive and checksum;
- validation result;
- service status;
- public verification result;
- operator and UTC time;
- any port or unit overrides.

---

## 16. Rollback procedure

Rollback requires the pre-upgrade code SHA and state archive. Code-only rollback over a database migrated by newer code may be unsafe.

1. declare a maintenance window;
2. stop the Pass 189 service chain in reverse order;
3. checkout the commit recorded with the backup;
4. restore the matching state archive;
5. rerun the installer;
6. refresh nginx;
7. verify all local and public surfaces;
8. preserve the failed upgrade state for investigation.

Do not delete evidence or edit receipt rows to make an older runtime accept newer state.

---

## 17. Security maintenance

### Host controls

- use SSH keys;
- restrict administrative accounts;
- apply Ubuntu security updates during a controlled window;
- expose only SSH and nginx through the firewall;
- keep the service ports loopback-only;
- retain root-only or encrypted off-host backups;
- review `systemctl cat` output for unexpected drop-ins;
- review `/etc/nginx` for duplicate or shadowed location blocks.

### Service controls

- run services as the non-login `hhs` user;
- keep `/etc/hhs/pass189.env` at `0640 root:hhs`;
- keep `/var/lib/hhs-pass189` owned by `hhs:hhs`;
- do not weaken the committed systemd hardening flags without a reviewed contract change;
- do not promote software traces into measured-hardware evidence;
- do not manually mark hardware candidates executable.

### Update the operating system

```bash
sudo apt update
apt list --upgradable
```

Apply updates during a maintenance window. When a reboot is required:

```bash
sudo systemctl stop \
  hhs-pass189-iteration4.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration2.service \
  hhs-pass189.service
sudo reboot
```

After reconnecting:

```bash
sudo systemctl status \
  hhs-pass189.service \
  hhs-pass189-iteration2.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration4.service \
  --no-pager

cd /opt/holofractal-harmonicode
sudo native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

---

## 18. Routine maintenance schedule

### Daily

```bash
sudo systemctl --failed
sudo systemctl is-active \
  hhs-pass189.service \
  hhs-pass189-iteration2.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration4.service
sudo df -h /var/lib/hhs-pass189
```

Run local health verification after any alert or restart.

### Weekly

- create and checksum an off-host backup;
- inspect Pass 189 and nginx errors from the preceding week;
- review quarantine growth;
- run SQLite `PRAGMA quick_check` against all persistent databases;
- verify TLS certificate renewal status at the nginx host layer;
- check for unexpected listeners or systemd drop-ins.

### Monthly

- review pending Ubuntu security updates;
- test restore into an isolated staging host or directory;
- verify the deployed commit against authoritative `main`;
- review operator keys, SSH access, firewall rules, and backup access;
- review disk and inode growth trends;
- confirm Pass 189 and Pass 190 port assignments remain conflict-free.

### Before every deployment

- clean repository status;
- backup and checksum;
- validate the target commit;
- record the current and target SHAs;
- verify no required port is occupied;
- confirm nginx configuration validity.

### After every deployment

- verify all systemd units;
- verify all four loopback endpoints;
- verify public HTTPS routes;
- inspect logs for restarts or migration errors;
- record the final deployed commit and evidence.

---

## 19. Troubleshooting matrix

| Symptom | Checks | Corrective action |
|---|---|---|
| Installer reports missing project | `pwd`, `ls /opt/holofractal-harmonicode` | place the repository at the canonical path or create reviewed unit overrides |
| Port already in use | `ss -ltnp` | stop the conflicting process or apply a documented port override |
| Iteration 2 will not start | `systemctl status hhs-pass189.service` | repair and start the required base service first |
| Iteration 3 or 4 will not start | inspect the preceding dependency and journal | restore dependency health, then start forward |
| nginx returns `502 Bad Gateway` | curl the loopback endpoint; inspect service journal | restore backend service before changing nginx |
| nginx configuration fails | `nginx -t`; search duplicate locations | include the Pass 189 snippet once inside the intended server block |
| Permission denied under `/var/lib/hhs-pass189` | `namei -l`, `find`, `stat` | repair ownership to `hhs:hhs`; do not run service processes as root |
| Environment file unreadable | `stat /etc/hhs/pass189.env` | restore `root:hhs` and `0640` |
| SQLite reports locked | inspect active processes and long requests | allow bounded operations to complete; do not delete WAL/SHM files |
| SQLite quick check fails | stop mutation, preserve files, restore known-good backup | do not hand-edit database pages or receipt rows |
| Iteration 4 runs the pre-lifecycle server | `systemctl cat hhs-pass189-iteration4.service` | reinstall the current unit and confirm `hhs_pass189_iteration4_token_server.py` |
| Public route works but WebSocket fails | inspect nginx upgrade headers and proxy path | reinstall the committed nginx snippet and reload after `nginx -t` |
| Validation fails after OS update | inspect compiler/Python version and first failing target | repair dependencies or compatibility; do not bypass validation |

---

## 20. Incident isolation

When a security or integrity event is suspected:

1. preserve logs and current commit information;
2. stop the affected highest iteration first;
3. stop lower layers only when containment requires it;
4. preserve `/var/lib/hhs-pass189`, `/etc/hhs/pass189.env`, and journald evidence;
5. disable or remove the public nginx include if public isolation is required;
6. run `nginx -t` before reloading;
7. create a forensic backup before repair;
8. restore from a verified commit/state pair;
9. rerun full validation and verification before reopening traffic.

Emergency full-stack stop:

```bash
sudo systemctl stop \
  hhs-pass189-iteration4.service \
  hhs-pass189-iteration3.service \
  hhs-pass189-iteration2.service \
  hhs-pass189.service
```

Do not destroy quarantine packages, event ledgers, receipts, or failed databases during containment.

---

## 21. Operator command reference

### Validate

```bash
make -C /opt/holofractal-harmonicode/native_projects/hhs_pass189_hqlh_runtime validate
```

### Install or upgrade units

```bash
sudo REPO_ROOT=/opt/holofractal-harmonicode \
  SERVICE_USER=hhs \
  /opt/holofractal-harmonicode/native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh
```

### Verify locally

```bash
sudo /opt/holofractal-harmonicode/native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh
```

### Show service definitions and overrides

```bash
sudo systemctl cat hhs-pass189.service
sudo systemctl cat hhs-pass189-iteration2.service
sudo systemctl cat hhs-pass189-iteration3.service
sudo systemctl cat hhs-pass189-iteration4.service
```

### Show deployed source identity

```bash
git -C /opt/holofractal-harmonicode rev-parse HEAD
git -C /opt/holofractal-harmonicode status --short
```

### Show listeners

```bash
sudo ss -ltnp | grep -E ':(8189|8190|8191|8192)\b'
```

### Show recent service errors

```bash
sudo journalctl \
  -p warning \
  -u hhs-pass189.service \
  -u hhs-pass189-iteration2.service \
  -u hhs-pass189-iteration3.service \
  -u hhs-pass189-iteration4.service \
  --since '24 hours ago' \
  --no-pager
```

---

## 22. Deployment change-record template

```text
Change ID:
Operator:
UTC start:
UTC finish:
Host:
Public domain:
Prior commit:
Target commit:
Backup archive:
Backup SHA-256:
Port allocation:
Systemd overrides:
Nginx include checksum:
Pre-deploy validation:
Local verification:
Public verification:
Database quick checks:
Observed warnings:
Rollback required:
Final status:
```

Store change records with the operational evidence system used for the DigitalOcean host. Chat history is not a substitute for repository-visible or host-visible deployment state.
